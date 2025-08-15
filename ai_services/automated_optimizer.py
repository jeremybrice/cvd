"""
Automated Optimization Suggestions with Multi-Objective Optimization
Provides AI-driven recommendations considering multiple business objectives
"""

import json
import sqlite3
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import anthropic

class MultiObjectiveOptimizer:
    """AI-powered multi-objective planogram optimization"""
    
    def __init__(self, api_key: str, db_path: str = 'cvd.db'):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.db_path = db_path
        self.objectives = {
            'revenue': {'weight': 0.4, 'direction': 'maximize'},
            'turnover': {'weight': 0.2, 'direction': 'maximize'},
            'variety': {'weight': 0.2, 'direction': 'maximize'},
            'freshness': {'weight': 0.1, 'direction': 'maximize'},
            'accessibility': {'weight': 0.1, 'direction': 'maximize'}
        }
        
    def generate_optimizations(self, device_id: int, cabinet_index: int,
                              objectives: Dict = None) -> Dict:
        """
        Generate multi-objective optimization suggestions
        """
        
        # Override default objectives if provided
        if objectives:
            self.objectives = objectives
        
        # Get current state
        current_state = self._analyze_current_state(device_id, cabinet_index)
        
        # Get constraints
        constraints = self._get_constraints(device_id, cabinet_index)
        
        # Generate optimization strategies
        strategies = self._generate_strategies(current_state, constraints)
        
        # Get AI recommendations
        recommendations = self._get_ai_recommendations(
            current_state, constraints, strategies
        )
        
        # Implement A/B test suggestions
        ab_tests = self._suggest_ab_tests(recommendations)
        
        return {
            'current_performance': current_state['performance'],
            'optimization_objectives': self.objectives,
            'recommendations': recommendations,
            'ab_test_suggestions': ab_tests,
            'implementation_plan': self._create_implementation_plan(recommendations)
        }
    
    def _analyze_current_state(self, device_id: int, cabinet_index: int) -> Dict:
        """Analyze current planogram state across all objectives"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        planogram_key = f"{device_id}_{cabinet_index}"
        
        # Revenue analysis
        revenue_query = """
        SELECT 
            AVG(s.sale_cash) as avg_daily_revenue,
            SUM(s.sale_cash) / COUNT(DISTINCT DATE(s.created_at)) as revenue_per_day
        FROM sales s
        WHERE s.device_id = ?
        AND s.created_at > datetime('now', '-30 days')
        """
        cursor.execute(revenue_query, (device_id,))
        revenue_data = cursor.fetchone()
        
        # Turnover analysis
        turnover_query = """
        SELECT 
            ps.slot_position,
            p.name,
            ps.quantity,
            ps.capacity,
            AVG(s.sale_units) as daily_sales,
            ps.capacity / NULLIF(AVG(s.sale_units), 0) as days_to_empty
        FROM planogram_slots ps
        JOIN products p ON ps.product_id = p.id
        LEFT JOIN sales s ON s.product_id = p.id AND s.device_id = ?
        WHERE ps.planogram_id = (SELECT id FROM planograms WHERE planogram_key = ?)
        AND s.created_at > datetime('now', '-7 days')
        GROUP BY ps.slot_position
        """
        cursor.execute(turnover_query, (device_id, planogram_key))
        turnover_data = cursor.fetchall()
        
        # Variety analysis
        variety_query = """
        SELECT 
            COUNT(DISTINCT p.category) as category_count,
            COUNT(DISTINCT ps.product_id) as unique_products,
            COUNT(*) as total_slots,
            COUNT(CASE WHEN ps.product_id = 1 THEN 1 END) as empty_slots
        FROM planogram_slots ps
        LEFT JOIN products p ON ps.product_id = p.id
        WHERE ps.planogram_id = (SELECT id FROM planograms WHERE planogram_key = ?)
        """
        cursor.execute(variety_query, (planogram_key,))
        variety_data = cursor.fetchone()
        
        conn.close()
        
        # Calculate objective scores
        performance = {
            'revenue': {
                'current': revenue_data[0] or 0,
                'score': self._normalize_score(revenue_data[0] or 0, 0, 200),
                'details': f"${revenue_data[0] or 0:.2f}/day"
            },
            'turnover': {
                'current': len([t for t in turnover_data if t[5] and t[5] < 7]),
                'score': self._calculate_turnover_score(turnover_data),
                'details': f"{len([t for t in turnover_data if t[5] and t[5] < 7])} fast movers"
            },
            'variety': {
                'current': variety_data[1],
                'score': self._normalize_score(variety_data[1], 0, 50),
                'details': f"{variety_data[1]} unique products, {variety_data[0]} categories"
            },
            'freshness': {
                'current': 0,  # Would need expiry tracking
                'score': 0.7,  # Default
                'details': "Freshness tracking not implemented"
            },
            'accessibility': {
                'current': 0,
                'score': self._calculate_accessibility_score(turnover_data),
                'details': "Based on product placement"
            }
        }
        
        return {
            'performance': performance,
            'turnover_details': turnover_data,
            'variety_details': variety_data,
            'empty_slots': variety_data[3]
        }
    
    def _get_constraints(self, device_id: int, cabinet_index: int) -> Dict:
        """Get physical and business constraints"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get cabinet configuration
        cabinet_query = """
        SELECT 
            cc.rows,
            cc.columns,
            ct.name as cabinet_type
        FROM cabinet_configurations cc
        JOIN cabinet_types ct ON cc.cabinet_type_id = ct.id
        WHERE cc.device_id = ? AND cc.cabinet_index = ?
        """
        cursor.execute(cabinet_query, (device_id, cabinet_index))
        cabinet = cursor.fetchone()
        
        conn.close()
        
        if not cabinet:
            return {}
        
        # Define constraints based on cabinet type
        constraints = {
            'physical': {
                'total_slots': cabinet[0] * cabinet[1],
                'rows': cabinet[0],
                'columns': cabinet[1],
                'temperature_zone': self._map_temperature(cabinet[2]),
                'weight_limits': {
                    'top_rows': 2.0,  # kg
                    'middle_rows': 5.0,
                    'bottom_rows': 10.0
                }
            },
            'business': {
                'min_variety': 10,  # Minimum unique products
                'max_price_variance': 5.00,  # Max price difference in column
                'required_categories': ['Beverage', 'Snack'],
                'vendor_slots': {},  # Vendor-specific slot requirements
                'promotional_slots': []  # Required promotional positions
            },
            'operational': {
                'min_turnover_days': 3,  # Don't want products sitting too long
                'max_turnover_days': 14,  # Don't want constant restocking
                'service_frequency': 7,  # Days between service
                'min_par_level': 0.3  # Minimum 30% stock
            }
        }
        
        return constraints
    
    def _generate_strategies(self, current_state: Dict, constraints: Dict) -> List[Dict]:
        """Generate optimization strategies based on objectives"""
        strategies = []
        
        # Strategy 1: Fill empty slots with high-performers
        if current_state['empty_slots'] > 0:
            strategies.append({
                'name': 'Fill Empty Slots',
                'priority': 'high',
                'type': 'quick_win',
                'description': f"Fill {current_state['empty_slots']} empty slots with proven products",
                'expected_impact': {
                    'revenue': current_state['empty_slots'] * 5.0,  # $5 per slot estimate
                    'variety': current_state['empty_slots']
                }
            })
        
        # Strategy 2: Optimize slow movers
        slow_movers = [
            t for t in current_state['turnover_details'] 
            if t[5] and t[5] > 14
        ]
        if slow_movers:
            strategies.append({
                'name': 'Replace Slow Movers',
                'priority': 'medium',
                'type': 'performance',
                'description': f"Replace {len(slow_movers)} slow-moving products",
                'products': [{'slot': s[0], 'product': s[1]} for s in slow_movers[:5]]
            })
        
        # Strategy 3: Improve category balance
        if current_state['variety_details'][0] < 4:
            strategies.append({
                'name': 'Increase Category Variety',
                'priority': 'medium',
                'type': 'variety',
                'description': "Add products from underrepresented categories"
            })
        
        # Strategy 4: Optimize placement for accessibility
        strategies.append({
            'name': 'Optimize Product Placement',
            'priority': 'low',
            'type': 'accessibility',
            'description': "Move high-velocity items to more accessible positions"
        })
        
        return strategies
    
    def _get_ai_recommendations(self, state: Dict, constraints: Dict, 
                               strategies: List[Dict]) -> List[Dict]:
        """Get AI-powered optimization recommendations"""
        
        prompt = f"""<optimization_context>
Current Performance:
{json.dumps(state['performance'], indent=2)}

Objectives (weighted):
{json.dumps(self.objectives, indent=2)}

Constraints:
Physical: {constraints['physical']['total_slots']} slots ({constraints['physical']['rows']}x{constraints['physical']['columns']})
Temperature: {constraints['physical']['temperature_zone']}
Business: Min variety={constraints['business']['min_variety']}, Required categories={constraints['business']['required_categories']}
Operational: Service every {constraints['operational']['service_frequency']} days

Strategies Identified:
{json.dumps(strategies, indent=2)}

Empty Slots: {state['empty_slots']}
</optimization_context>

Generate specific optimization recommendations that:
1. Balance all objectives according to their weights
2. Respect all constraints
3. Are implementable immediately
4. Include specific products and slot positions

For each recommendation provide:
- Specific action (add/remove/move product)
- Exact slot position(s)
- Product selection with reasoning
- Expected impact on each objective
- Implementation difficulty (easy/medium/hard)
- Confidence score (0-1)

Focus on actionable, high-impact changes.
Return as JSON array of recommendations, maximum 10 items.

Format:
[{{
    "action": "add|remove|move",
    "product": {{"name": str, "category": str, "price": float}},
    "slot": str or {{"from": str, "to": str}} for moves,
    "reasoning": str,
    "impact": {{
        "revenue": float ($ per day),
        "turnover": float (days improvement),
        "variety": int (product count change),
        "accessibility": float (-1 to 1)
    }},
    "difficulty": "easy|medium|hard",
    "confidence": float (0-1),
    "priority": int (1-10)
}}]"""
        
        try:
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0.5,
                system="You are a merchandising optimization expert with deep knowledge of vending machine operations.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Extract JSON array
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
                
                # Sort by priority
                recommendations.sort(key=lambda x: x.get('priority', 5))
                
                return recommendations[:10]
            
        except Exception as e:
            print(f"AI recommendation error: {e}")
        
        # Fallback to rule-based recommendations
        return self._generate_rule_based_recommendations(state, strategies)
    
    def _generate_rule_based_recommendations(self, state: Dict, 
                                            strategies: List[Dict]) -> List[Dict]:
        """Generate rule-based recommendations as fallback"""
        recommendations = []
        
        # Fill empty slots first
        if state['empty_slots'] > 0:
            recommendations.append({
                'action': 'add',
                'product': {'name': 'Coca-Cola', 'category': 'Beverage', 'price': 2.50},
                'slot': 'A1',  # Would need actual empty slot detection
                'reasoning': 'Fill empty slot with high-velocity beverage',
                'impact': {
                    'revenue': 8.0,
                    'turnover': 5.0,
                    'variety': 1,
                    'accessibility': 0.8
                },
                'difficulty': 'easy',
                'confidence': 0.7,
                'priority': 1
            })
        
        return recommendations
    
    def _suggest_ab_tests(self, recommendations: List[Dict]) -> List[Dict]:
        """Suggest A/B tests for validating recommendations"""
        ab_tests = []
        
        # Group similar recommendations for testing
        high_confidence = [r for r in recommendations if r['confidence'] > 0.8]
        medium_confidence = [r for r in recommendations if 0.5 <= r['confidence'] <= 0.8]
        
        if high_confidence:
            ab_tests.append({
                'name': 'High-Confidence Changes',
                'description': 'Test top recommendations with high confidence',
                'variant_a': 'Current planogram',
                'variant_b': 'Implement top 3 high-confidence changes',
                'changes': high_confidence[:3],
                'duration_days': 14,
                'success_metrics': ['revenue', 'units_sold'],
                'minimum_sample_size': 100  # transactions
            })
        
        if medium_confidence:
            ab_tests.append({
                'name': 'Experimental Changes',
                'description': 'Test medium-confidence optimizations',
                'variant_a': 'Current planogram',
                'variant_b': 'Implement medium-confidence changes',
                'changes': medium_confidence[:2],
                'duration_days': 21,
                'success_metrics': ['revenue', 'customer_satisfaction'],
                'minimum_sample_size': 150
            })
        
        # Suggest time-based testing
        ab_tests.append({
            'name': 'Time-of-Day Optimization',
            'description': 'Test different configurations for different times',
            'variant_a': 'Standard all-day planogram',
            'variant_b': 'Morning-optimized (6am-12pm) vs afternoon (12pm-6pm)',
            'changes': [],  # Would be populated with time-specific products
            'duration_days': 30,
            'success_metrics': ['revenue_by_hour', 'product_velocity'],
            'minimum_sample_size': 200
        })
        
        return ab_tests
    
    def _create_implementation_plan(self, recommendations: List[Dict]) -> Dict:
        """Create step-by-step implementation plan"""
        
        # Group by difficulty
        easy = [r for r in recommendations if r.get('difficulty') == 'easy']
        medium = [r for r in recommendations if r.get('difficulty') == 'medium']
        hard = [r for r in recommendations if r.get('difficulty') == 'hard']
        
        plan = {
            'immediate_actions': {
                'description': 'Can be implemented today',
                'items': easy,
                'estimated_time': '30 minutes',
                'expected_impact': sum(r['impact']['revenue'] for r in easy)
            },
            'short_term_actions': {
                'description': 'Implement within next service visit',
                'items': medium,
                'estimated_time': '1-2 hours',
                'expected_impact': sum(r['impact']['revenue'] for r in medium)
            },
            'long_term_actions': {
                'description': 'Requires planning and coordination',
                'items': hard,
                'estimated_time': '1-2 weeks',
                'expected_impact': sum(r['impact']['revenue'] for r in hard)
            },
            'total_expected_impact': {
                'revenue': sum(r['impact']['revenue'] for r in recommendations),
                'implementation_cost': len(recommendations) * 15,  # Rough estimate
                'roi_days': 30  # Estimated payback period
            }
        }
        
        return plan
    
    def _normalize_score(self, value: float, min_val: float, max_val: float) -> float:
        """Normalize value to 0-1 range"""
        if max_val == min_val:
            return 0.5
        return max(0, min(1, (value - min_val) / (max_val - min_val)))
    
    def _calculate_turnover_score(self, turnover_data: List) -> float:
        """Calculate turnover score from data"""
        if not turnover_data:
            return 0
        
        # Good turnover is 3-7 days
        optimal_turnover = [t for t in turnover_data if t[5] and 3 <= t[5] <= 7]
        return len(optimal_turnover) / len(turnover_data) if turnover_data else 0
    
    def _calculate_accessibility_score(self, turnover_data: List) -> float:
        """Calculate accessibility score based on placement"""
        if not turnover_data:
            return 0
        
        score = 0
        for item in turnover_data:
            slot = item[0]
            if slot and len(slot) > 0:
                row = slot[0]
                # Eye-level rows (B, C) get higher scores
                if row in ['B', 'C']:
                    score += 1
                elif row in ['A', 'D']:
                    score += 0.7
                else:
                    score += 0.4
        
        return score / len(turnover_data) if turnover_data else 0
    
    def _map_temperature(self, cabinet_type: str) -> str:
        """Map cabinet type to temperature zone"""
        zones = {
            'Cooler': 'Refrigerated (35-45°F)',
            'Freezer': 'Frozen (0-10°F)',
            'Ambient': 'Room temperature',
            'Ambient+': 'Room temperature'
        }
        return zones.get(cabinet_type, 'Unknown')