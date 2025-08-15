"""
LLM Integration Pipeline for AI Planogram System
Production-ready prompt templates and integration patterns
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Optional, Tuple, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from datetime import datetime, timedelta
import anthropic
from anthropic import AsyncAnthropic
import tiktoken
import sqlite3
from functools import lru_cache

# =============================================================================
# MODEL CONFIGURATION & TOKEN MANAGEMENT
# =============================================================================

class ModelType(Enum):
    """Model selection based on use case requirements"""
    REALTIME = "claude-3-haiku-20240307"      # Fast, <500ms responses
    ANALYSIS = "claude-3-sonnet-20240229"      # Balanced performance
    COMPLEX = "claude-3-opus-20240229"         # Deep analysis
    VISION = "claude-3-opus-20240229"          # Image analysis

class TokenLimits:
    """Token management configuration"""
    REALTIME = 500       # Quick responses for drag-and-drop
    ANALYSIS = 2000      # Standard analysis
    COMPLEX = 4000       # Comprehensive recommendations
    BATCH = 8000         # Batch processing
    
    # Input context limits (leaving room for response)
    MAX_CONTEXT = {
        ModelType.REALTIME: 2000,
        ModelType.ANALYSIS: 6000,
        ModelType.COMPLEX: 12000,
        ModelType.VISION: 15000
    }

@dataclass
class UsageMetrics:
    """Track token usage and costs"""
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float
    cache_hit: bool = False
    
    @classmethod
    def calculate_cost(cls, model: ModelType, input_tokens: int, output_tokens: int) -> float:
        """Calculate API cost in USD"""
        # Pricing per 1M tokens (as of 2024)
        PRICING = {
            ModelType.REALTIME: {"input": 0.25, "output": 1.25},
            ModelType.ANALYSIS: {"input": 3.00, "output": 15.00},
            ModelType.COMPLEX: {"input": 15.00, "output": 75.00},
            ModelType.VISION: {"input": 15.00, "output": 75.00}
        }
        
        rates = PRICING.get(model, PRICING[ModelType.ANALYSIS])
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]
        return round(input_cost + output_cost, 6)

# =============================================================================
# PROMPT ENGINEERING TEMPLATES
# =============================================================================

class PromptTemplates:
    """Production-ready prompt templates for each AI feature"""
    
    @staticmethod
    def realtime_placement_analysis() -> str:
        """Template for real-time drag-and-drop feedback"""
        return """<role>
You are a vending machine merchandising expert providing instant feedback on product placement.
</role>

<context>
A user is dragging product "{product_name}" (ID: {product_id}) to position {target_position} in a {cabinet_type} vending machine.
</context>

<current_state>
{current_planogram_xml}
</current_state>

<sales_metrics>
Product velocity: {product_velocity} units/day
Product revenue: ${product_revenue}/day
Position {target_position} historical performance: ${position_revenue}/day
</sales_metrics>

<constraints>
Temperature zone: {temperature_zone}
Weight limit: {weight_limit}kg
Adjacent products: {adjacent_products}
</constraints>

<task>
Provide instant scoring (0-100) and brief feedback for this placement.
Consider: visibility, accessibility, cross-sell potential, zone compatibility.
</task>

<output_format>
{{
    "score": integer_0_to_100,
    "feedback": "max_15_words",
    "concerns": ["list_of_issues"] or null,
    "better_position": "position_code" or null
}}
</output_format>"""

    @staticmethod
    def revenue_prediction() -> str:
        """Template for revenue impact prediction"""
        return """<role>
You are a predictive analytics expert specializing in vending machine revenue optimization.
</role>

<analysis_request>
Predict the revenue impact of changing a planogram configuration.
</analysis_request>

<current_configuration>
<planogram>
{current_planogram_xml}
</planogram>
<performance>
Daily revenue: ${current_daily_revenue}
Weekly trend: {weekly_trend}%
Top sellers: {top_products_json}
Stockout frequency: {stockout_rate}%
</performance>
</current_configuration>

<proposed_changes>
{changes_xml}
</proposed_changes>

<historical_patterns>
Similar changes in the past resulted in:
{historical_outcomes_json}
</historical_patterns>

<location_context>
Venue type: {venue_type}
Traffic patterns: {traffic_json}
Demographics: {demographics_json}
Competition: {competition_level}
</location_context>

<task>
Predict the revenue impact with confidence intervals and identify key risk factors.
</task>

<output_format>
{{
    "baseline_daily_revenue": float,
    "predicted_daily_revenue": float,
    "lift_percentage": float,
    "confidence_interval": {{
        "lower_bound": float,
        "upper_bound": float,
        "confidence_level": 0.95
    }},
    "break_even_days": integer,
    "key_drivers": [
        {{
            "factor": "string",
            "impact": "positive|negative",
            "magnitude": "high|medium|low"
        }}
    ],
    "risks": [
        {{
            "risk": "string",
            "probability": "high|medium|low",
            "mitigation": "string"
        }}
    ],
    "recommendation": "implement|test|reconsider",
    "reasoning": "string_max_100_words"
}}
</output_format>"""

    @staticmethod
    def heat_zone_optimization() -> str:
        """Template for visual zone optimization"""
        return """<role>
You are a visual merchandising specialist optimizing product placement based on visibility zones.
</role>

<zone_definitions>
Zone A (Eye Level): Rows at 130-170cm height - Premium visibility, 50% higher engagement
Zone B (Reach): Rows at 80-130cm - Good accessibility, standard engagement  
Zone C (Bend): Rows at 40-80cm - Requires bending, 20% lower engagement
Zone D (Squat): Rows below 40cm - Difficult access, 40% lower engagement
</zone_definitions>

<current_layout>
{planogram_with_zones_xml}
</current_layout>

<product_characteristics>
{products_json_with_attributes}
</product_characteristics>

<performance_data>
Zone A revenue: ${zone_a_revenue}/day ({zone_a_velocity} units/day)
Zone B revenue: ${zone_b_revenue}/day ({zone_b_velocity} units/day)
Zone C revenue: ${zone_c_revenue}/day ({zone_c_velocity} units/day)
Zone D revenue: ${zone_d_revenue}/day ({zone_d_velocity} units/day)
</performance_data>

<task>
Optimize product placement across visibility zones to maximize revenue while considering:
1. High-margin products in premium zones
2. Impulse items at eye level
3. Heavy items in lower zones for safety
4. Category clustering for convenience
</task>

<output_format>
{{
    "zone_assignments": {{
        "A": ["product_ids_for_premium_zone"],
        "B": ["product_ids_for_reach_zone"],
        "C": ["product_ids_for_bend_zone"],
        "D": ["product_ids_for_squat_zone"]
    }},
    "expected_impact": {{
        "current_daily_revenue": float,
        "optimized_daily_revenue": float,
        "improvement_percentage": float
    }},
    "key_moves": [
        {{
            "product": "name",
            "from_zone": "letter",
            "to_zone": "letter",
            "reason": "string",
            "expected_lift": "percentage"
        }}
    ],
    "visualization_data": {{
        "heat_map": [[row_values]],
        "zone_scores": {{"A": float, "B": float, "C": float, "D": float}}
    }}
}}
</output_format>"""

    @staticmethod
    def affinity_clustering() -> str:
        """Template for product affinity analysis"""
        return """<role>
You are a data scientist specializing in market basket analysis for vending machines.
</role>

<transaction_data>
{recent_transactions_json}
</transaction_data>

<current_layout>
{current_adjacencies_xml}
</current_layout>

<product_catalog>
{products_with_categories_json}
</product_catalog>

<task>
Identify product affinities and recommend optimal clustering to increase basket size.
Calculate lift scores for product pairs and suggest adjacency improvements.
</task>

<analysis_approach>
1. Identify frequently co-purchased items
2. Calculate lift scores (observed/expected co-occurrence)
3. Find complementary category clusters
4. Recommend high-affinity adjacencies
5. Predict basket size impact
</analysis_approach>

<output_format>
{{
    "affinity_matrix": {{
        "product_id_1": {{
            "product_id_2": {{
                "co_purchase_frequency": float,
                "lift_score": float,
                "confidence": float
            }}
        }}
    }},
    "recommended_clusters": [
        {{
            "cluster_name": "string",
            "products": ["product_names"],
            "positions": ["recommended_positions"],
            "expected_basket_lift": "percentage",
            "rationale": "string"
        }}
    ],
    "adjacency_changes": [
        {{
            "product_1": "name",
            "product_2": "name", 
            "action": "place_adjacent|separate",
            "lift_score": float,
            "revenue_impact": "dollars_per_day"
        }}
    ],
    "expected_results": {{
        "current_avg_basket": float,
        "predicted_avg_basket": float,
        "basket_size_increase": "percentage",
        "daily_revenue_impact": float
    }}
}}
</output_format>"""

    @staticmethod
    def demand_forecasting() -> str:
        """Template for ML-based demand prediction"""
        return """<role>
You are a demand forecasting expert using advanced time series analysis for inventory optimization.
</role>

<historical_data>
<sales_history>{ninety_day_sales_json}</sales_history>
<stockout_events>{stockout_history_json}</stockout_events>
<service_visits>{service_schedule_json}</service_visits>
</historical_data>

<external_factors>
<weather>
Current: {current_weather}
Forecast: {weather_forecast_json}
Historical correlation: {weather_impact_json}
</weather>
<events>
Upcoming: {upcoming_events_json}
Historical impact: {event_impact_json}
</events>
<seasonality>
Day of week patterns: {dow_patterns_json}
Monthly trends: {monthly_trends_json}
Holiday effects: {holiday_impacts_json}
</seasonality>
</external_factors>

<constraints>
<shelf_life>{product_shelf_life_json}</shelf_life>
<storage_capacity>{slot_capacities_json}</storage_capacity>
<service_frequency>{service_interval_days}</service_frequency>
</constraints>

<task>
Forecast demand for the next service cycle and recommend optimal inventory levels.
Identify high-risk stockout products and suggest par level adjustments.
</task>

<output_format>
{{
    "demand_forecast": {{
        "product_id": {{
            "next_7_days": float,
            "next_cycle": float,
            "confidence_interval": [lower, upper],
            "trend": "increasing|stable|decreasing",
            "seasonality_factor": float
        }}
    }},
    "stockout_risk": [
        {{
            "product": "name",
            "risk_level": "high|medium|low",
            "days_until_stockout": float,
            "probability": float,
            "revenue_at_risk": float
        }}
    ],
    "par_level_recommendations": {{
        "product_id": {{
            "current_par": integer,
            "recommended_par": integer,
            "change_reason": "string",
            "expected_impact": {{
                "stockout_reduction": "percentage",
                "spoilage_reduction": "percentage",
                "revenue_capture": float
            }}
        }}
    }},
    "optimal_service_timing": {{
        "next_service": "datetime",
        "urgency": "high|normal|low",
        "critical_products": ["product_names"]
    }}
}}
</output_format>"""

    @staticmethod
    def location_personalization() -> str:
        """Template for venue-specific optimization"""
        return """<role>
You are a location intelligence expert personalizing vending machine assortments for specific venues.
</role>

<venue_profile>
Type: {venue_type}
Subtype: {venue_subtype}
Size: {venue_size}
Operating hours: {operating_hours}
Demographics: {demographics_json}
</venue_profile>

<performance_baseline>
{current_performance_json}
</performance_baseline>

<venue_insights>
<traffic_patterns>{hourly_traffic_json}</traffic_patterns>
<purchase_patterns>{time_of_day_sales_json}</purchase_patterns>
<category_preferences>{category_performance_json}</category_preferences>
<price_sensitivity>{price_point_analysis_json}</price_sensitivity>
</venue_insights>

<competitive_landscape>
Nearby vending: {competitor_machines_json}
Retail options: {nearby_retail_json}
Differentiation opportunity: {differentiation_score}
</competitive_landscape>

<task>
Create a personalized planogram optimized for this specific venue.
Balance local preferences with profitability and operational constraints.
</task>

<output_format>
{{
    "venue_strategy": {{
        "key_insights": ["insight_strings"],
        "target_customer": "description",
        "value_proposition": "string"
    }},
    "personalized_assortment": {{
        "core_products": [
            {{
                "product": "name",
                "rationale": "why_essential",
                "expected_velocity": float
            }}
        ],
        "local_favorites": [
            {{
                "product": "name",
                "local_index": float,
                "vs_network_avg": "percentage"
            }}
        ],
        "experimental": [
            {{
                "product": "name",
                "hypothesis": "string",
                "success_metric": "string"
            }}
        ]
    }},
    "time_based_optimization": {{
        "morning": ["product_names"],
        "afternoon": ["product_names"],
        "evening": ["product_names"]
    }},
    "pricing_strategy": {{
        "premium_products": ["names_with_rationale"],
        "value_products": ["names_with_rationale"],
        "optimal_price_points": {{"product": price}}
    }},
    "expected_performance": {{
        "daily_revenue": float,
        "vs_network_average": "percentage",
        "vs_current": "percentage",
        "roi_days": integer
    }}
}}
</output_format>"""

# =============================================================================
# DATA STRUCTURING FOR LLM CONSUMPTION
# =============================================================================

class DataStructurer:
    """Convert raw data into LLM-optimized formats"""
    
    @staticmethod
    def planogram_to_xml(planogram_data: Dict) -> str:
        """Convert planogram to structured XML for better LLM comprehension"""
        xml_parts = ['<planogram>']
        
        # Cabinet metadata
        xml_parts.append(f'  <cabinet type="{planogram_data.get("cabinet_type", "unknown")}">')
        xml_parts.append(f'    <dimensions rows="{planogram_data.get("rows", 0)}" columns="{planogram_data.get("columns", 0)}"/>')
        xml_parts.append(f'    <temperature>{planogram_data.get("temperature", "ambient")}</temperature>')
        xml_parts.append('  </cabinet>')
        
        # Slot data organized by row
        xml_parts.append('  <slots>')
        slots_by_row = {}
        for slot in planogram_data.get('slots', []):
            row = slot['position'][0]
            if row not in slots_by_row:
                slots_by_row[row] = []
            slots_by_row[row].append(slot)
        
        for row in sorted(slots_by_row.keys()):
            xml_parts.append(f'    <row letter="{row}" zone="{DataStructurer._get_zone(row)}">')
            for slot in sorted(slots_by_row[row], key=lambda x: int(x['position'][1:])):
                xml_parts.append(f'      <slot position="{slot["position"]}" '
                               f'product="{slot.get("product_name", "Empty")}" '
                               f'quantity="{slot.get("quantity", 0)}" '
                               f'capacity="{slot.get("capacity", 20)}" '
                               f'revenue="${slot.get("daily_revenue", 0):.2f}"/>')
            xml_parts.append('    </row>')
        xml_parts.append('  </slots>')
        xml_parts.append('</planogram>')
        
        return '\n'.join(xml_parts)
    
    @staticmethod
    def _get_zone(row_letter: str) -> str:
        """Map row letter to visibility zone"""
        zones = {'A': 'A', 'B': 'A', 'C': 'B', 'D': 'B', 
                'E': 'C', 'F': 'C', 'G': 'D', 'H': 'D'}
        return zones.get(row_letter, 'B')
    
    @staticmethod
    def transactions_to_json(transactions: List[Dict], limit: int = 100) -> str:
        """Structure transaction data for affinity analysis"""
        # Group by transaction/timestamp
        grouped = {}
        for trans in transactions[:limit]:
            key = f"{trans['device_id']}_{trans['timestamp']}"
            if key not in grouped:
                grouped[key] = {
                    'transaction_id': key,
                    'timestamp': trans['timestamp'],
                    'products': [],
                    'total': 0
                }
            grouped[key]['products'].append({
                'id': trans['product_id'],
                'name': trans['product_name'],
                'price': trans['price'],
                'category': trans['category']
            })
            grouped[key]['total'] += trans['price']
        
        return json.dumps(list(grouped.values()), indent=2)
    
    @staticmethod
    def performance_metrics_to_json(metrics: Dict, emphasize: List[str] = None) -> str:
        """Structure performance metrics with emphasis on key indicators"""
        structured = {
            'summary': {
                'daily_revenue': metrics.get('daily_revenue', 0),
                'daily_units': metrics.get('daily_units', 0),
                'avg_transaction': metrics.get('avg_transaction', 0),
                'stockout_rate': metrics.get('stockout_rate', 0)
            },
            'trends': {
                'revenue_trend': metrics.get('revenue_trend', 'stable'),
                'velocity_trend': metrics.get('velocity_trend', 'stable')
            }
        }
        
        # Add emphasized metrics
        if emphasize:
            structured['key_metrics'] = {
                key: metrics.get(key) for key in emphasize if key in metrics
            }
        
        # Add detailed breakdowns
        if 'by_product' in metrics:
            structured['product_performance'] = sorted(
                metrics['by_product'].items(),
                key=lambda x: x[1].get('revenue', 0),
                reverse=True
            )[:10]  # Top 10 only to save tokens
        
        return json.dumps(structured, indent=2)

# =============================================================================
# STREAMING RESPONSE HANDLER
# =============================================================================

class StreamingHandler:
    """Handle streaming responses from Claude API"""
    
    def __init__(self, client: AsyncAnthropic):
        self.client = client
        
    async def stream_analysis(
        self,
        prompt: str,
        model: ModelType = ModelType.ANALYSIS,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_prompt: str = None
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks as they arrive"""
        
        try:
            async with self.client.messages.stream(
                model=model.value,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "You are an expert in vending machine optimization.",
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                async for chunk in stream.text_stream:
                    yield chunk
                    
        except Exception as e:
            yield f"Error in streaming: {str(e)}"
    
    async def stream_with_parsing(
        self,
        prompt: str,
        model: ModelType = ModelType.ANALYSIS,
        parse_json: bool = True
    ) -> AsyncGenerator[Dict, None]:
        """Stream and parse structured responses"""
        
        buffer = ""
        in_json = False
        json_buffer = ""
        
        async for chunk in self.stream_analysis(prompt, model):
            buffer += chunk
            
            # Detect JSON boundaries
            if '{' in chunk and not in_json:
                in_json = True
                json_buffer = buffer[buffer.rfind('{'):]
            elif in_json:
                json_buffer += chunk
                
                # Try to parse complete JSON objects
                try:
                    # Check for complete JSON
                    if json_buffer.count('{') == json_buffer.count('}'):
                        parsed = json.loads(json_buffer)
                        yield {'type': 'data', 'content': parsed}
                        in_json = False
                        json_buffer = ""
                except json.JSONDecodeError:
                    # Not complete yet, continue buffering
                    pass
            else:
                # Non-JSON text
                yield {'type': 'text', 'content': chunk}

# =============================================================================
# BATCH PROCESSING PATTERNS
# =============================================================================

class BatchProcessor:
    """Efficient batch processing for multiple planograms"""
    
    def __init__(self, client: anthropic.Anthropic, db_path: str):
        self.client = client
        self.db_path = db_path
        self.batch_size = 10  # Process 10 planograms at a time
        
    async def batch_optimize(
        self,
        device_ids: List[int],
        optimization_type: str = 'revenue'
    ) -> List[Dict]:
        """Process multiple planograms in batches"""
        
        results = []
        
        # Process in batches to manage token limits
        for i in range(0, len(device_ids), self.batch_size):
            batch = device_ids[i:i + self.batch_size]
            
            # Prepare batch context
            batch_context = self._prepare_batch_context(batch)
            
            # Create consolidated prompt
            prompt = self._create_batch_prompt(batch_context, optimization_type)
            
            # Get recommendations for batch
            batch_results = await self._process_batch(prompt)
            results.extend(batch_results)
            
            # Rate limiting
            await asyncio.sleep(1)
        
        return results
    
    def _prepare_batch_context(self, device_ids: List[int]) -> Dict:
        """Prepare context for batch processing"""
        context = {
            'devices': {},
            'common_patterns': {},
            'venue_types': {}
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for device_id in device_ids:
            # Get device data
            device_data = self._get_device_context(cursor, device_id)
            context['devices'][device_id] = device_data
            
            # Track patterns
            venue_type = device_data.get('venue_type')
            if venue_type not in context['venue_types']:
                context['venue_types'][venue_type] = []
            context['venue_types'][venue_type].append(device_id)
        
        conn.close()
        return context
    
    def _create_batch_prompt(self, context: Dict, optimization_type: str) -> str:
        """Create efficient batch processing prompt"""
        return f"""<batch_optimization>
<optimization_type>{optimization_type}</optimization_type>
<device_count>{len(context['devices'])}</device_count>

<devices>
{json.dumps(context['devices'], indent=2)}
</devices>

<venue_patterns>
{json.dumps(context['venue_types'], indent=2)}
</venue_patterns>

<task>
Provide optimization recommendations for each device.
Group similar recommendations for venues of the same type.
Focus on {optimization_type} optimization.
</task>

<output_format>
{{
    "recommendations": {{
        "device_id": {{
            "priority_changes": [...],
            "expected_impact": float,
            "implementation_effort": "low|medium|high"
        }}
    }},
    "patterns": {{
        "venue_type": {{
            "common_improvements": [...],
            "avg_expected_lift": float
        }}
    }}
}}
</output_format>
</batch_optimization>"""
    
    async def _process_batch(self, prompt: str) -> List[Dict]:
        """Process batch and parse results"""
        # Implementation would call Claude API and parse response
        pass
    
    def _get_device_context(self, cursor, device_id: int) -> Dict:
        """Get device context for batch processing"""
        # Implementation would fetch device data from database
        pass

# =============================================================================
# SEMANTIC CACHING
# =============================================================================

class SemanticCache:
    """Cache LLM responses based on semantic similarity"""
    
    def __init__(self, cache_dir: str = "/tmp/llm_cache", ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        os.makedirs(cache_dir, exist_ok=True)
        
    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt"""
        # Use first 1000 chars + model for key
        content = f"{prompt[:1000]}_{model}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str) -> Optional[Dict]:
        """Retrieve cached response if available"""
        cache_key = self._get_cache_key(prompt, model)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            # Check TTL
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if datetime.now() - file_time < self.ttl:
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        return None
    
    def set(self, prompt: str, model: str, response: Dict):
        """Cache response"""
        cache_key = self._get_cache_key(prompt, model)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        with open(cache_file, 'w') as f:
            json.dump({
                'prompt': prompt[:500],  # Store truncated prompt for debugging
                'model': model,
                'response': response,
                'timestamp': datetime.now().isoformat()
            }, f)
    
    def clear_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if now - file_time > self.ttl:
                os.remove(filepath)

# =============================================================================
# COST MONITORING & MANAGEMENT
# =============================================================================

class CostMonitor:
    """Monitor and control API costs"""
    
    def __init__(self, db_path: str, daily_limit_usd: float = 50.0):
        self.db_path = db_path
        self.daily_limit = daily_limit_usd
        self._init_db()
    
    def _init_db(self):
        """Initialize cost tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                model TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                cost_usd REAL,
                latency_ms REAL,
                cache_hit BOOLEAN,
                feature TEXT,
                device_id INTEGER
            )
        """)
        conn.commit()
        conn.close()
    
    def track_usage(self, metrics: UsageMetrics, feature: str, device_id: int = None):
        """Track API usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO api_usage 
            (model, input_tokens, output_tokens, cost_usd, latency_ms, cache_hit, feature, device_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metrics.model, metrics.input_tokens, metrics.output_tokens,
            metrics.cost_usd, metrics.latency_ms, metrics.cache_hit,
            feature, device_id
        ))
        conn.commit()
        conn.close()
    
    def get_daily_usage(self) -> Dict:
        """Get today's usage statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                SUM(cost_usd) as total_cost,
                SUM(input_tokens) as total_input,
                SUM(output_tokens) as total_output,
                COUNT(*) as request_count,
                AVG(latency_ms) as avg_latency,
                SUM(cache_hit) as cache_hits
            FROM api_usage
            WHERE DATE(timestamp) = DATE('now')
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_cost': result[0] or 0,
            'total_input_tokens': result[1] or 0,
            'total_output_tokens': result[2] or 0,
            'request_count': result[3] or 0,
            'avg_latency_ms': result[4] or 0,
            'cache_hit_rate': (result[5] or 0) / max(result[3] or 1, 1)
        }
    
    def check_budget(self) -> bool:
        """Check if within daily budget"""
        usage = self.get_daily_usage()
        return usage['total_cost'] < self.daily_limit
    
    def get_feature_costs(self) -> Dict:
        """Get costs broken down by feature"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                feature,
                COUNT(*) as requests,
                SUM(cost_usd) as total_cost,
                AVG(cost_usd) as avg_cost,
                AVG(latency_ms) as avg_latency
            FROM api_usage
            WHERE DATE(timestamp) >= DATE('now', '-7 days')
            GROUP BY feature
            ORDER BY total_cost DESC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return {
            row[0]: {
                'requests': row[1],
                'total_cost': row[2],
                'avg_cost': row[3],
                'avg_latency': row[4]
            }
            for row in results
        }

# =============================================================================
# ERROR HANDLING & FALLBACKS
# =============================================================================

class ErrorHandler:
    """Robust error handling with fallback strategies"""
    
    def __init__(self, fallback_to_rules: bool = True):
        self.fallback_to_rules = fallback_to_rules
        self.retry_delays = [1, 2, 4, 8, 16]  # Exponential backoff
        
    async def safe_api_call(
        self,
        api_func,
        *args,
        fallback_func=None,
        **kwargs
    ) -> Dict:
        """Execute API call with error handling"""
        
        last_error = None
        
        for attempt, delay in enumerate(self.retry_delays):
            try:
                # Check if we should proceed
                if hasattr(self, 'cost_monitor'):
                    if not self.cost_monitor.check_budget():
                        raise Exception("Daily budget exceeded")
                
                # Make API call
                result = await api_func(*args, **kwargs)
                return result
                
            except anthropic.RateLimitError as e:
                last_error = e
                await asyncio.sleep(delay)
                continue
                
            except anthropic.APIError as e:
                last_error = e
                if attempt < len(self.retry_delays) - 1:
                    await asyncio.sleep(delay)
                    continue
                break
                
            except Exception as e:
                last_error = e
                break
        
        # All retries failed, use fallback
        if fallback_func and self.fallback_to_rules:
            return await fallback_func(*args, **kwargs)
        else:
            return {
                'success': False,
                'error': str(last_error),
                'fallback_used': False
            }
    
    @staticmethod
    async def rule_based_fallback(planogram_data: Dict, optimization_type: str) -> Dict:
        """Rule-based optimization when AI is unavailable"""
        recommendations = []
        
        # Simple rules for fallback
        if optimization_type == 'revenue':
            # Put high-price items at eye level
            for slot in planogram_data['slots']:
                if slot['position'][0] in ['A', 'B'] and slot.get('is_empty'):
                    recommendations.append({
                        'slot': slot['position'],
                        'recommendation': {
                            'product': 'High-margin product',
                            'reason': 'Eye-level placement for premium items',
                            'expected_improvement': '+$3-5/day'
                        },
                        'confidence': 0.6
                    })
        
        return {
            'success': True,
            'recommendations': recommendations,
            'fallback_used': True,
            'message': 'Using rule-based optimization (AI unavailable)'
        }

# =============================================================================
# MAIN INTEGRATION PIPELINE
# =============================================================================

class LLMIntegrationPipeline:
    """Main pipeline orchestrating all LLM operations"""
    
    def __init__(
        self,
        api_key: str,
        db_path: str = 'cvd.db',
        cache_enabled: bool = True,
        cost_monitoring: bool = True
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.async_client = AsyncAnthropic(api_key=api_key)
        self.db_path = db_path
        
        # Initialize components
        self.templates = PromptTemplates()
        self.structurer = DataStructurer()
        self.streaming = StreamingHandler(self.async_client)
        self.batch = BatchProcessor(self.client, db_path)
        self.error_handler = ErrorHandler()
        
        # Optional components
        if cache_enabled:
            self.cache = SemanticCache()
        else:
            self.cache = None
            
        if cost_monitoring:
            self.cost_monitor = CostMonitor(db_path)
            self.error_handler.cost_monitor = self.cost_monitor
        else:
            self.cost_monitor = None
    
    def select_model(self, feature: str) -> ModelType:
        """Select appropriate model based on feature requirements"""
        model_map = {
            'realtime': ModelType.REALTIME,
            'drag_drop': ModelType.REALTIME,
            'quick_score': ModelType.REALTIME,
            'analysis': ModelType.ANALYSIS,
            'prediction': ModelType.ANALYSIS,
            'optimization': ModelType.COMPLEX,
            'batch': ModelType.ANALYSIS,
            'vision': ModelType.VISION
        }
        return model_map.get(feature, ModelType.ANALYSIS)
    
    def optimize_tokens(self, prompt: str, model: ModelType) -> str:
        """Optimize prompt to fit within token limits"""
        max_context = TokenLimits.MAX_CONTEXT[model]
        
        # Simple token estimation (4 chars ≈ 1 token)
        estimated_tokens = len(prompt) // 4
        
        if estimated_tokens > max_context:
            # Truncate less important sections
            # This is a simplified version - production would use tiktoken
            truncation_point = max_context * 4
            prompt = prompt[:truncation_point] + "\n[Content truncated for token limit]"
        
        return prompt
    
    async def process_request(
        self,
        feature: str,
        data: Dict,
        stream: bool = False
    ) -> Dict:
        """Main entry point for processing LLM requests"""
        
        start_time = time.time()
        
        # Select model and prepare prompt
        model = self.select_model(feature)
        prompt = self._prepare_prompt(feature, data)
        prompt = self.optimize_tokens(prompt, model)
        
        # Check cache
        if self.cache:
            cached = self.cache.get(prompt, model.value)
            if cached:
                return {
                    'success': True,
                    'result': cached['response'],
                    'cached': True,
                    'latency_ms': 0
                }
        
        # Process request
        if stream:
            result = await self._process_streaming(prompt, model)
        else:
            result = await self._process_standard(prompt, model)
        
        # Track metrics
        latency_ms = (time.time() - start_time) * 1000
        
        if self.cost_monitor and result.get('success'):
            metrics = UsageMetrics(
                model=model.value,
                input_tokens=result.get('input_tokens', 0),
                output_tokens=result.get('output_tokens', 0),
                latency_ms=latency_ms,
                cost_usd=UsageMetrics.calculate_cost(
                    model, 
                    result.get('input_tokens', 0),
                    result.get('output_tokens', 0)
                )
            )
            self.cost_monitor.track_usage(metrics, feature, data.get('device_id'))
        
        # Cache successful responses
        if self.cache and result.get('success'):
            self.cache.set(prompt, model.value, result)
        
        result['latency_ms'] = latency_ms
        return result
    
    def _prepare_prompt(self, feature: str, data: Dict) -> str:
        """Prepare prompt based on feature and data"""
        # Map features to template methods
        template_map = {
            'realtime': self.templates.realtime_placement_analysis,
            'prediction': self.templates.revenue_prediction,
            'heat_zone': self.templates.heat_zone_optimization,
            'affinity': self.templates.affinity_clustering,
            'demand': self.templates.demand_forecasting,
            'personalization': self.templates.location_personalization
        }
        
        template_func = template_map.get(feature)
        if not template_func:
            raise ValueError(f"Unknown feature: {feature}")
        
        # Get template and format with data
        template = template_func()
        
        # Structure data appropriately
        if 'planogram' in data:
            data['current_planogram_xml'] = self.structurer.planogram_to_xml(data['planogram'])
        if 'transactions' in data:
            data['recent_transactions_json'] = self.structurer.transactions_to_json(data['transactions'])
        if 'metrics' in data:
            data['performance_metrics_json'] = self.structurer.performance_metrics_to_json(data['metrics'])
        
        # Format template with data
        return template.format(**data)
    
    async def _process_standard(self, prompt: str, model: ModelType) -> Dict:
        """Process standard (non-streaming) request"""
        try:
            response = await self.error_handler.safe_api_call(
                self._make_api_call,
                prompt,
                model,
                fallback_func=self.error_handler.rule_based_fallback
            )
            return response
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _process_streaming(self, prompt: str, model: ModelType) -> AsyncGenerator:
        """Process streaming request"""
        async for chunk in self.streaming.stream_with_parsing(prompt, model):
            yield chunk
    
    async def _make_api_call(self, prompt: str, model: ModelType) -> Dict:
        """Make actual API call to Claude"""
        response = await self.async_client.messages.create(
            model=model.value,
            max_tokens=TokenLimits.ANALYSIS,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            'success': True,
            'result': response.content[0].text,
            'input_tokens': response.usage.input_tokens,
            'output_tokens': response.usage.output_tokens
        }

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def example_usage():
    """Example of using the LLM Integration Pipeline"""
    
    # Initialize pipeline
    pipeline = LLMIntegrationPipeline(
        api_key=os.getenv('ANTHROPIC_API_KEY'),
        db_path='cvd.db',
        cache_enabled=True,
        cost_monitoring=True
    )
    
    # Example 1: Real-time placement scoring
    placement_data = {
        'product_name': 'Coca-Cola',
        'product_id': 3,
        'target_position': 'A4',
        'cabinet_type': 'USI Alpine 5000',
        'planogram': {
            'cabinet_type': 'refrigerated',
            'rows': 7,
            'columns': 10,
            'slots': [
                {'position': 'A3', 'product_name': 'Pepsi', 'daily_revenue': 8.50},
                {'position': 'A5', 'product_name': 'Sprite', 'daily_revenue': 6.25}
            ]
        },
        'product_velocity': 12.5,
        'product_revenue': 25.00,
        'position_revenue': 22.00,
        'temperature_zone': 'refrigerated',
        'weight_limit': 5,
        'adjacent_products': 'Pepsi, Sprite'
    }
    
    result = await pipeline.process_request('realtime', placement_data)
    print(f"Placement Score: {result}")
    
    # Example 2: Revenue prediction with streaming
    prediction_data = {
        'current_planogram_xml': '<planogram>...</planogram>',
        'current_daily_revenue': 285.50,
        'weekly_trend': 5.2,
        'top_products_json': '[...]',
        'stockout_rate': 12.5,
        'changes_xml': '<changes>...</changes>',
        'historical_outcomes_json': '[...]',
        'venue_type': 'office_building',
        'traffic_json': '{...}',
        'demographics_json': '{...}',
        'competition_level': 'medium'
    }
    
    async for chunk in pipeline.process_request('prediction', prediction_data, stream=True):
        print(f"Stream chunk: {chunk}")
    
    # Example 3: Batch optimization
    device_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    batch_results = await pipeline.batch.batch_optimize(device_ids, 'revenue')
    print(f"Batch results: {batch_results}")
    
    # Example 4: Check costs
    if pipeline.cost_monitor:
        daily_usage = pipeline.cost_monitor.get_daily_usage()
        print(f"Today's API usage: ${daily_usage['total_cost']:.2f}")
        
        feature_costs = pipeline.cost_monitor.get_feature_costs()
        print(f"Costs by feature: {feature_costs}")

if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())