"""
Planogram optimization engine using Claude API for intelligent product placement.
"""
import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import anthropic

class PlanogramOptimizer:
    """Standalone planogram optimization using sales data and AI recommendations."""
    
    def __init__(self, api_key: str, db_path: str = 'cvd.db'):
        """Initialize with Anthropic API key and database path."""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.db_path = db_path
    
    def _generate_all_slot_positions(self, rows: int, cols: int) -> List[str]:
        """Generate all possible slot positions for a cabinet."""
        positions = []
        for row in range(rows):
            row_letter = chr(65 + row)  # A, B, C, D...
            for col in range(1, cols + 1):
                positions.append(f"{row_letter}{col}")
        return positions
        
    def get_sales_data(self, device_id: int, days: int = 30) -> List[Dict]:
        """Fetch sales data for a device over specified time period."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
        SELECT 
            s.product_id,
            p.name as product_name,
            p.category,
            p.price,
            SUM(s.sale_units) as total_units,
            SUM(s.sale_cash) as total_revenue,
            COUNT(DISTINCT DATE(s.created_at)) as days_sold
        FROM sales s
        JOIN products p ON s.product_id = p.id
        WHERE s.device_id = ?
        AND s.created_at > datetime('now', '-' || ? || ' days')
        GROUP BY s.product_id
        """
        
        cursor.execute(query, (device_id, days))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_current_planogram(self, device_id: int, cabinet_index: int = 0) -> Dict:
        """Fetch current planogram configuration."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get cabinet configuration
        cabinet_query = """
        SELECT 
        cc.*,
        ct.name as cabinet_type
        FROM cabinet_configurations cc
        JOIN cabinet_types ct ON cc.cabinet_type_id = ct.id
        WHERE cc.device_id = ? AND cc.cabinet_index = ?
        """
        cursor.execute(cabinet_query, (device_id, cabinet_index))
        cabinet_row = cursor.fetchone()
        cabinet = dict(cabinet_row) if cabinet_row else None
        
        if not cabinet:
            conn.close()
            return None
            
        # Get planogram slots
        planogram_key = f"{device_id}_{cabinet_index}"
        slots_query = """
        SELECT 
            ps.*,
            p.name as product_name,
            p.category,
            p.price as product_price
        FROM planogram_slots ps
        LEFT JOIN products p ON ps.product_id = p.id
        WHERE ps.planogram_id = (
            SELECT id FROM planograms WHERE planogram_key = ?
        )
        """
        cursor.execute(slots_query, (planogram_key,))
        slots = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Generate all possible slot positions for the cabinet
        all_positions = self._generate_all_slot_positions(cabinet['rows'], cabinet['columns'])
        
        # Find which positions are filled
        filled_positions = {slot['slot_position'] for slot in slots}
        empty_positions = set(all_positions) - filled_positions
        
        # Add empty slot records for missing positions
        for position in empty_positions:
            slots.append({
                'slot_position': position,
                'product_id': 1,  # EMPTY_SLOT_ID
                'product_name': 'Empty',
                'category': None,
                'product_price': 0,
                'quantity': 0,
                'capacity': 20,  # Default capacity
                'price': 0,
                'is_empty': True
            })
        
        # Also mark slots with product_id = 1 as empty
        for slot in slots:
            if slot.get('product_id') == 1:
                slot['is_empty'] = True
                slot['product_name'] = 'Empty'
        
        return {
            'cabinet': cabinet,
            'slots': slots
        }
    
    def calculate_performance_metrics(self, sales_data: List[Dict], 
                                    planogram_data: Dict) -> Dict:
        """Calculate performance metrics for current planogram."""
        metrics = {
            'slot_performance': {},
            'product_velocity': {},
            'revenue_by_position': {},
            'stockout_risk': {},
            'category_distribution': {},
            'empty_slots': [],  # Track empty slots
            'top_performers': [],  # Top selling products
            'category_gaps': []  # Missing categories
        }
        
        # Calculate velocity (units per day) for each product
        for sale in sales_data:
            product_id = sale['product_id']
            days_sold = sale['days_sold'] or 1
            velocity = sale['total_units'] / days_sold
            metrics['product_velocity'][product_id] = {
                'daily_units': velocity,
                'daily_revenue': sale['total_revenue'] / days_sold,
                'total_units': sale['total_units'],
                'total_revenue': sale['total_revenue']
            }
        
        # Analyze slot performance
        for slot in planogram_data['slots']:
            position = slot['slot_position']
            product_id = slot.get('product_id')
            
            # Check if slot is empty
            if not product_id or product_id == 1 or slot.get('is_empty'):
                metrics['empty_slots'].append({
                    'position': position,
                    'row': position[0],  # A, B, C, D
                    'column': int(position[1:]) if len(position) > 1 else 0
                })
            elif product_id in metrics['product_velocity']:
                perf = metrics['product_velocity'][product_id]
                metrics['slot_performance'][position] = {
                    'product_id': product_id,
                    'daily_units': perf['daily_units'],
                    'daily_revenue': perf['daily_revenue'],
                    'capacity': slot.get('capacity', 20),
                    'days_until_empty': slot.get('quantity', 0) / perf['daily_units'] if perf['daily_units'] > 0 else 999
                }
                
                # Stockout risk assessment
                if metrics['slot_performance'][position]['days_until_empty'] < 3:
                    metrics['stockout_risk'][position] = 'high'
                elif metrics['slot_performance'][position]['days_until_empty'] < 7:
                    metrics['stockout_risk'][position] = 'medium'
        
        # Get top performers from sales data
        if sales_data:
            sorted_products = sorted(
                sales_data, 
                key=lambda x: x.get('total_revenue', 0), 
                reverse=True
            )[:10]
            metrics['top_performers'] = sorted_products
        
        # Analyze category gaps
        current_categories = {
            slot.get('category') 
            for slot in planogram_data['slots'] 
            if slot.get('category') and not slot.get('is_empty')
        }
        
        all_categories = {
            item.get('category') 
            for item in sales_data 
            if item.get('category')
        }
        
        metrics['category_gaps'] = list(all_categories - current_categories)
        
        return metrics
    
    def build_optimization_prompt(self, performance_metrics: Dict, 
                                cabinet_config: Dict, sales_data: List[Dict]) -> str:
        """Build comprehensive prompt for Claude with all context."""
        empty_slots = performance_metrics.get('empty_slots', [])
        top_performers = performance_metrics.get('top_performers', [])
        
        prompt = f"""You are analyzing a vending machine planogram for optimization.

Cabinet Configuration:
- Type: {cabinet_config['cabinet_type']}
- Size: {cabinet_config['rows']}x{cabinet_config['columns']} 
- Model: {cabinet_config['model_name']}

CRITICAL: This planogram has {len(empty_slots)} EMPTY SLOTS that need products:
Empty Slots: {', '.join([slot['position'] for slot in empty_slots])}

Current Performance Metrics:
{json.dumps(performance_metrics, indent=2)}

Top Selling Products (Last 30 days):
{json.dumps(top_performers[:15], indent=2)}

Full Product Sales Data:
{json.dumps(sales_data[:30], indent=2)}

IMPORTANT INSTRUCTIONS:
1. FIRST PRIORITY: You MUST suggest products for ALL {len(empty_slots)} empty slots
2. Empty slots generate $0 revenue - filling them is the highest impact optimization
3. Row A slots are premium eye-level positions - assign high-velocity, high-margin products
4. After filling empty slots, then suggest replacements for underperforming products

For EACH recommendation, provide:
{{
    "slot": "position (e.g., A4)",
    "current_product": null or "product name",
    "current_performance": "e.g., $0/day for empty slots",
    "recommendation": {{
        "product": "Specific product name from sales data",
        "reason": "Why this product suits this position",
        "expected_improvement": "e.g., +$5.50/day"
    }},
    "confidence": 0.0-1.0
}}

You MUST provide at least {len(empty_slots)} recommendations for the empty slots.
Format your response as a JSON array."""
        
        return prompt
    
    def get_claude_recommendations(self, prompt: str) -> str:
        """Get AI recommendations from Claude."""
        try:
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0.7,
                system="You are a vending machine optimization expert. Provide specific, actionable recommendations based on sales data analysis.",
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
    
    def parse_ai_response(self, ai_response: str) -> List[Dict]:
        """Parse and validate Claude's response."""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
                
                # Validate and enhance recommendations
                validated = []
                for rec in recommendations:
                    # Ensure required fields exist
                    if 'slot' in rec and 'recommendation' in rec:
                        # Handle both empty and filled slot recommendations
                        if 'current_product' not in rec:
                            rec['current_product'] = None
                        if 'current_performance' not in rec:
                            rec['current_performance'] = '$0/day' if rec['current_product'] is None else 'Unknown'
                        if 'confidence' not in rec:
                            rec['confidence'] = 0.85  # Default confidence for empty slots
                        
                        # Ensure recommendation has required subfields
                        if isinstance(rec['recommendation'], dict):
                            if 'product' in rec['recommendation']:
                                validated.append(rec)
                
                # Sort recommendations: empty slots first, then by confidence
                validated.sort(key=lambda x: (
                    0 if x['current_product'] is None else 1,  # Empty slots first
                    -x['confidence']  # Then by confidence (highest first)
                ))
                
                return validated
            else:
                print(f"No JSON array found in AI response")
                return []
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            print(f"AI Response preview: {ai_response[:500]}...")
            return []
    
    def generate_recommendations(self, device_id: int, cabinet_index: int = 0,
                               optimization_type: str = 'full') -> Dict:
        """Main entry point for generating optimization recommendations."""
        try:
            # Fetch data
            sales_data = self.get_sales_data(device_id)
            planogram_data = self.get_current_planogram(device_id, cabinet_index)
            
            if not planogram_data:
                return {
                    'success': False,
                    'error': 'No planogram found for this device/cabinet'
                }
            
            # Calculate metrics
            metrics = self.calculate_performance_metrics(sales_data, planogram_data)
            
            # Build and send prompt
            prompt = self.build_optimization_prompt(
                metrics, 
                planogram_data['cabinet'],
                sales_data
            )
            
            # Get AI recommendations
            ai_response = self.get_claude_recommendations(prompt)
            recommendations = self.parse_ai_response(ai_response)
            
            return {
                'success': True,
                'device_id': device_id,
                'cabinet_index': cabinet_index,
                'recommendations': recommendations,
                'performance_metrics': metrics,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }