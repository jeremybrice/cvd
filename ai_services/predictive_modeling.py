"""
Predictive Performance Modeling for Planogram Changes
Uses AI to predict sales impact of proposed planogram modifications
"""

import json
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import anthropic

class PredictiveModeler:
    """AI-powered predictive modeling for planogram performance"""
    
    def __init__(self, api_key: str, db_path: str = 'cvd.db'):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.db_path = db_path
        
    def predict_change_impact(self, device_id: int, cabinet_index: int, 
                             proposed_changes: List[Dict]) -> Dict:
        """
        Predict sales impact of proposed planogram changes
        Returns confidence-scored predictions
        """
        
        # Get baseline performance
        baseline = self._get_baseline_performance(device_id, cabinet_index)
        
        # Get historical patterns
        patterns = self._analyze_historical_patterns(device_id)
        
        # Structure data for AI prediction
        prediction_context = self._build_prediction_context(
            baseline, patterns, proposed_changes
        )
        
        # Get AI predictions
        predictions = self._get_ai_predictions(prediction_context)
        
        # Calculate confidence scores
        predictions_with_confidence = self._add_confidence_scores(
            predictions, patterns
        )
        
        return predictions_with_confidence
    
    def _get_baseline_performance(self, device_id: int, cabinet_index: int) -> Dict:
        """Get current planogram performance baseline"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get last 30 days performance
        query = """
        SELECT 
            AVG(sale_cash) as avg_daily_revenue,
            AVG(sale_units) as avg_daily_units,
            COUNT(DISTINCT product_id) as product_variety,
            MAX(sale_cash) as best_day_revenue,
            MIN(sale_cash) as worst_day_revenue,
            COUNT(DISTINCT DATE(created_at)) as active_days
        FROM sales
        WHERE device_id = ?
        AND created_at > datetime('now', '-30 days')
        """
        cursor.execute(query, (device_id,))
        result = cursor.fetchone()
        
        # Get product-level performance
        product_query = """
        SELECT 
            p.id,
            p.name,
            p.category,
            ps.slot_position,
            SUM(s.sale_units) as units_sold,
            SUM(s.sale_cash) as revenue,
            COUNT(DISTINCT DATE(s.created_at)) as days_sold
        FROM planogram_slots ps
        JOIN products p ON ps.product_id = p.id
        LEFT JOIN sales s ON s.product_id = p.id AND s.device_id = ?
        WHERE ps.planogram_id = (
            SELECT id FROM planograms 
            WHERE planogram_key = ?
        )
        AND s.created_at > datetime('now', '-30 days')
        GROUP BY p.id, ps.slot_position
        """
        
        planogram_key = f"{device_id}_{cabinet_index}"
        cursor.execute(product_query, (device_id, planogram_key))
        products = cursor.fetchall()
        
        conn.close()
        
        return {
            'avg_daily_revenue': result[0] or 0,
            'avg_daily_units': result[1] or 0,
            'product_variety': result[2] or 0,
            'revenue_variance': (result[3] or 0) - (result[4] or 0),
            'active_days': result[5] or 0,
            'product_performance': [
                {
                    'id': p[0],
                    'name': p[1],
                    'category': p[2],
                    'slot': p[3],
                    'units_sold': p[4] or 0,
                    'revenue': p[5] or 0,
                    'velocity': (p[4] or 0) / (p[6] or 1)
                }
                for p in products
            ]
        }
    
    def _analyze_historical_patterns(self, device_id: int) -> Dict:
        """Analyze historical patterns for prediction accuracy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get seasonal patterns
        seasonal_query = """
        SELECT 
            strftime('%m', created_at) as month,
            AVG(sale_cash) as avg_revenue,
            AVG(sale_units) as avg_units
        FROM sales
        WHERE device_id = ?
        GROUP BY month
        ORDER BY month
        """
        cursor.execute(seasonal_query, (device_id,))
        seasonal = cursor.fetchall()
        
        # Get day-of-week patterns
        dow_query = """
        SELECT 
            strftime('%w', created_at) as day_of_week,
            AVG(sale_cash) as avg_revenue,
            AVG(sale_units) as avg_units
        FROM sales
        WHERE device_id = ?
        GROUP BY day_of_week
        ORDER BY day_of_week
        """
        cursor.execute(dow_query, (device_id,))
        day_patterns = cursor.fetchall()
        
        # Get product interaction patterns
        interaction_query = """
        WITH daily_sales AS (
            SELECT 
                DATE(created_at) as sale_date,
                product_id,
                SUM(sale_units) as units
            FROM sales
            WHERE device_id = ?
            GROUP BY sale_date, product_id
        )
        SELECT 
            a.product_id as product1,
            b.product_id as product2,
            COUNT(*) as co_occurrence,
            AVG(a.units + b.units) as avg_combined_units
        FROM daily_sales a
        JOIN daily_sales b ON a.sale_date = b.sale_date 
            AND a.product_id < b.product_id
        GROUP BY a.product_id, b.product_id
        HAVING co_occurrence > 5
        ORDER BY co_occurrence DESC
        LIMIT 20
        """
        cursor.execute(interaction_query, (device_id,))
        interactions = cursor.fetchall()
        
        conn.close()
        
        return {
            'seasonal_patterns': {
                str(s[0]): {'revenue': s[1], 'units': s[2]}
                for s in seasonal
            },
            'day_of_week_patterns': {
                str(d[0]): {'revenue': d[1], 'units': d[2]}
                for d in day_patterns
            },
            'product_interactions': [
                {
                    'product1': i[0],
                    'product2': i[1],
                    'strength': i[2],
                    'combined_units': i[3]
                }
                for i in interactions
            ]
        }
    
    def _build_prediction_context(self, baseline: Dict, patterns: Dict, 
                                 changes: List[Dict]) -> Dict:
        """Build context for AI prediction"""
        
        # Summarize changes
        change_summary = {
            'additions': [],
            'removals': [],
            'moves': []
        }
        
        for change in changes:
            if change['action'] == 'add':
                change_summary['additions'].append({
                    'product': change['product']['name'],
                    'slot': change['slot'],
                    'category': change['product'].get('category'),
                    'price': change['product'].get('price')
                })
            elif change['action'] == 'remove':
                change_summary['removals'].append({
                    'product': change['product']['name'],
                    'slot': change['slot']
                })
            elif change['action'] == 'move':
                change_summary['moves'].append({
                    'product': change['product']['name'],
                    'from_slot': change['from_slot'],
                    'to_slot': change['to_slot']
                })
        
        return {
            'baseline_performance': {
                'daily_revenue': baseline['avg_daily_revenue'],
                'daily_units': baseline['avg_daily_units'],
                'top_products': sorted(
                    baseline['product_performance'],
                    key=lambda x: x['revenue'],
                    reverse=True
                )[:5]
            },
            'historical_patterns': {
                'current_month_multiplier': patterns['seasonal_patterns'].get(
                    str(datetime.now().month), {}
                ).get('revenue', 1.0),
                'strong_interactions': patterns['product_interactions'][:5]
            },
            'proposed_changes': change_summary,
            'change_count': len(changes)
        }
    
    def _get_ai_predictions(self, context: Dict) -> Dict:
        """Get AI predictions for planogram changes"""
        
        prompt = f"""<prediction_context>
Baseline Performance:
- Daily Revenue: ${context['baseline_performance']['daily_revenue']:.2f}
- Daily Units: {context['baseline_performance']['daily_units']:.1f}

Top Current Products:
{json.dumps(context['baseline_performance']['top_products'], indent=2)}

Historical Patterns:
- Current Season Multiplier: {context['historical_patterns']['current_month_multiplier']:.2f}
- Product Synergies: {len(context['historical_patterns']['strong_interactions'])} identified

Proposed Changes:
{json.dumps(context['proposed_changes'], indent=2)}
</prediction_context>

Predict the impact of these planogram changes on:
1. Daily revenue (% change and dollar amount)
2. Unit sales (% change)
3. Customer satisfaction (score 1-10)
4. Operational efficiency (score 1-10)

Consider:
- Product placement effects (eye-level, accessibility)
- Category clustering benefits
- Cross-selling opportunities
- Seasonal appropriateness
- Inventory turnover improvements

Provide specific predictions with reasoning.
Format as JSON with these fields:
{{
    "revenue_impact": {{
        "percent_change": float,
        "dollar_change": float,
        "confidence": float (0-1),
        "reasoning": string
    }},
    "unit_impact": {{
        "percent_change": float,
        "unit_change": float,
        "confidence": float (0-1),
        "reasoning": string
    }},
    "customer_satisfaction": {{
        "current_score": float,
        "predicted_score": float,
        "factors": [string]
    }},
    "operational_efficiency": {{
        "current_score": float,
        "predicted_score": float,
        "improvements": [string]
    }},
    "risk_factors": [string],
    "opportunities": [string],
    "recommendation": string
}}"""
        
        try:
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1500,
                temperature=0.4,
                system="You are a retail analytics expert specializing in vending machine optimization.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse JSON response
            response_text = message.content[0].text
            predictions = json.loads(response_text)
            
            return predictions
            
        except Exception as e:
            # Fallback to rule-based predictions
            return self._fallback_predictions(context)
    
    def _fallback_predictions(self, context: Dict) -> Dict:
        """Rule-based fallback predictions"""
        
        change_count = context['change_count']
        additions = len(context['proposed_changes']['additions'])
        removals = len(context['proposed_changes']['removals'])
        
        # Simple heuristic predictions
        revenue_impact = 0
        if additions > removals:
            revenue_impact = additions * 2.5  # Each new product adds ~2.5%
        elif removals > additions:
            revenue_impact = -removals * 1.5  # Each removal costs ~1.5%
        
        return {
            'revenue_impact': {
                'percent_change': revenue_impact,
                'dollar_change': context['baseline_performance']['daily_revenue'] * (revenue_impact / 100),
                'confidence': 0.6,
                'reasoning': 'Based on product count changes'
            },
            'unit_impact': {
                'percent_change': revenue_impact * 0.8,
                'unit_change': context['baseline_performance']['daily_units'] * (revenue_impact * 0.8 / 100),
                'confidence': 0.5,
                'reasoning': 'Estimated from revenue impact'
            },
            'customer_satisfaction': {
                'current_score': 7.0,
                'predicted_score': 7.0 + (additions - removals) * 0.2,
                'factors': ['Product variety', 'Availability']
            },
            'operational_efficiency': {
                'current_score': 6.5,
                'predicted_score': 6.5,
                'improvements': []
            },
            'risk_factors': ['Prediction based on simple heuristics'],
            'opportunities': ['Test changes with A/B testing'],
            'recommendation': 'Monitor performance closely after changes'
        }
    
    def _add_confidence_scores(self, predictions: Dict, patterns: Dict) -> Dict:
        """Add confidence scores based on data quality and patterns"""
        
        # Calculate data quality score
        data_quality = 1.0
        
        # Reduce confidence if limited historical data
        if len(patterns['seasonal_patterns']) < 6:
            data_quality *= 0.8
        
        # Reduce confidence if few product interactions
        if len(patterns['product_interactions']) < 5:
            data_quality *= 0.9
        
        # Adjust predictions with confidence
        if 'revenue_impact' in predictions:
            predictions['revenue_impact']['confidence'] *= data_quality
        if 'unit_impact' in predictions:
            predictions['unit_impact']['confidence'] *= data_quality
        
        # Add overall confidence
        predictions['overall_confidence'] = data_quality
        
        # Add confidence explanation
        predictions['confidence_factors'] = {
            'historical_data': 'Good' if data_quality > 0.8 else 'Limited',
            'pattern_strength': 'Strong' if len(patterns['product_interactions']) > 10 else 'Moderate',
            'model_certainty': predictions.get('revenue_impact', {}).get('confidence', 0.5)
        }
        
        return predictions

class ScenarioSimulator:
    """Simulate different planogram scenarios"""
    
    def __init__(self, modeler: PredictiveModeler):
        self.modeler = modeler
        
    def simulate_scenarios(self, device_id: int, cabinet_index: int) -> List[Dict]:
        """Generate and evaluate multiple optimization scenarios"""
        
        scenarios = []
        
        # Scenario 1: Maximize revenue
        revenue_scenario = self._generate_revenue_scenario(device_id, cabinet_index)
        revenue_prediction = self.modeler.predict_change_impact(
            device_id, cabinet_index, revenue_scenario['changes']
        )
        scenarios.append({
            'name': 'Revenue Maximization',
            'description': 'Optimize for maximum daily revenue',
            'changes': revenue_scenario['changes'],
            'predictions': revenue_prediction
        })
        
        # Scenario 2: Improve variety
        variety_scenario = self._generate_variety_scenario(device_id, cabinet_index)
        variety_prediction = self.modeler.predict_change_impact(
            device_id, cabinet_index, variety_scenario['changes']
        )
        scenarios.append({
            'name': 'Product Variety',
            'description': 'Increase product selection',
            'changes': variety_scenario['changes'],
            'predictions': variety_prediction
        })
        
        # Scenario 3: Seasonal optimization
        seasonal_scenario = self._generate_seasonal_scenario(device_id, cabinet_index)
        seasonal_prediction = self.modeler.predict_change_impact(
            device_id, cabinet_index, seasonal_scenario['changes']
        )
        scenarios.append({
            'name': 'Seasonal Adjustment',
            'description': 'Optimize for current season',
            'changes': seasonal_scenario['changes'],
            'predictions': seasonal_prediction
        })
        
        return scenarios
    
    def _generate_revenue_scenario(self, device_id: int, cabinet_index: int) -> Dict:
        """Generate changes to maximize revenue"""
        # Implementation would analyze top performers and suggest replacements
        return {
            'changes': [
                {
                    'action': 'add',
                    'slot': 'B3',
                    'product': {'name': 'Premium Water', 'category': 'Beverage', 'price': 3.50}
                }
            ]
        }
    
    def _generate_variety_scenario(self, device_id: int, cabinet_index: int) -> Dict:
        """Generate changes to improve variety"""
        return {
            'changes': [
                {
                    'action': 'add',
                    'slot': 'C2',
                    'product': {'name': 'Protein Bar', 'category': 'Snack', 'price': 2.50}
                }
            ]
        }
    
    def _generate_seasonal_scenario(self, device_id: int, cabinet_index: int) -> Dict:
        """Generate seasonal optimization changes"""
        current_month = datetime.now().month
        
        # Summer items (months 6-8)
        if 6 <= current_month <= 8:
            return {
                'changes': [
                    {
                        'action': 'add',
                        'slot': 'A2',
                        'product': {'name': 'Sports Drink', 'category': 'Beverage', 'price': 2.75}
                    }
                ]
            }
        
        # Winter items (months 12, 1-2)
        elif current_month in [12, 1, 2]:
            return {
                'changes': [
                    {
                        'action': 'add',
                        'slot': 'B1',
                        'product': {'name': 'Hot Chocolate', 'category': 'Beverage', 'price': 2.00}
                    }
                ]
            }
        
        return {'changes': []}