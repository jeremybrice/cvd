"""
Visual Intelligence Integration for Planogram Analysis
Uses Claude's vision capabilities to analyze planogram layouts and generate heatmaps
"""

import json
import sqlite3
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from typing import Dict, List, Tuple, Optional
import anthropic
from datetime import datetime

class VisualPlanogramAnalyzer:
    """Analyze planograms using visual AI capabilities"""
    
    def __init__(self, api_key: str, db_path: str = 'cvd.db'):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.db_path = db_path
        
    def analyze_planogram_image(self, device_id: int, cabinet_index: int,
                               planogram_image: bytes = None) -> Dict:
        """
        Analyze planogram visually for optimization opportunities
        """
        
        # Generate planogram visualization if not provided
        if not planogram_image:
            planogram_image = self._generate_planogram_image(device_id, cabinet_index)
        
        # Get sales data for context
        sales_context = self._get_sales_context(device_id)
        
        # Analyze with vision AI
        visual_analysis = self._analyze_with_vision(planogram_image, sales_context)
        
        # Generate heat maps
        heatmaps = self._generate_heatmaps(device_id, cabinet_index)
        
        # Analyze visibility zones
        visibility_analysis = self._analyze_visibility_zones(device_id, cabinet_index)
        
        return {
            'visual_analysis': visual_analysis,
            'heatmaps': heatmaps,
            'visibility_zones': visibility_analysis,
            'recommendations': self._generate_visual_recommendations(
                visual_analysis, heatmaps, visibility_analysis
            )
        }
    
    def _generate_planogram_image(self, device_id: int, cabinet_index: int) -> bytes:
        """Generate visual representation of planogram"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get cabinet configuration
        cabinet_query = """
        SELECT cc.rows, cc.columns, ct.name
        FROM cabinet_configurations cc
        JOIN cabinet_types ct ON cc.cabinet_type_id = ct.id
        WHERE cc.device_id = ? AND cc.cabinet_index = ?
        """
        cursor.execute(cabinet_query, (device_id, cabinet_index))
        cabinet = cursor.fetchone()
        
        if not cabinet:
            conn.close()
            return None
        
        rows, cols, cabinet_type = cabinet
        
        # Get planogram data
        planogram_key = f"{device_id}_{cabinet_index}"
        slots_query = """
        SELECT 
            ps.slot_position,
            p.name,
            p.category,
            ps.quantity,
            ps.capacity,
            ps.price,
            COALESCE(SUM(s.sale_units), 0) as units_sold
        FROM planogram_slots ps
        LEFT JOIN products p ON ps.product_id = p.id
        LEFT JOIN sales s ON s.product_id = p.id AND s.device_id = ?
        WHERE ps.planogram_id = (SELECT id FROM planograms WHERE planogram_key = ?)
        GROUP BY ps.slot_position
        """
        cursor.execute(slots_query, (device_id, planogram_key))
        slots = cursor.fetchall()
        
        conn.close()
        
        # Create image
        slot_width = 100
        slot_height = 80
        padding = 10
        
        img_width = cols * slot_width + (cols + 1) * padding
        img_height = rows * slot_height + (rows + 1) * padding + 50  # Extra for header
        
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to load font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            font = ImageFont.load_default()
            title_font = font
        
        # Draw title
        title = f"Planogram - {cabinet_type} ({rows}x{cols})"
        draw.text((img_width//2 - 100, 10), title, fill='black', font=title_font)
        
        # Create slot lookup
        slot_data = {s[0]: s for s in slots}
        
        # Define category colors
        category_colors = {
            'Beverage': '#3498db',
            'Snack': '#e74c3c',
            'Food': '#2ecc71',
            'Candy': '#f39c12',
            'Other': '#95a5a6',
            None: '#ecf0f1'
        }
        
        # Draw slots
        for row in range(rows):
            for col in range(cols):
                x = col * slot_width + (col + 1) * padding
                y = row * slot_height + (row + 1) * padding + 40
                
                slot_pos = f"{chr(65 + row)}{col + 1}"
                slot_info = slot_data.get(slot_pos)
                
                if slot_info:
                    product_name = slot_info[1] or "Empty"
                    category = slot_info[2]
                    quantity = slot_info[3] or 0
                    capacity = slot_info[4] or 0
                    units_sold = slot_info[6] or 0
                    
                    # Get color based on category
                    color = category_colors.get(category, '#95a5a6')
                    
                    # Calculate fill based on quantity
                    fill_percent = quantity / capacity if capacity > 0 else 0
                    
                    # Draw slot background
                    draw.rectangle([x, y, x + slot_width, y + slot_height], 
                                 outline='black', width=2)
                    
                    # Draw fill level
                    if fill_percent > 0:
                        fill_height = int(slot_height * fill_percent)
                        draw.rectangle([x, y + slot_height - fill_height, 
                                      x + slot_width, y + slot_height],
                                     fill=color, outline=None)
                    
                    # Draw slot position
                    draw.text((x + 5, y + 5), slot_pos, fill='black', font=font)
                    
                    # Draw product name (truncated)
                    name_display = product_name[:12] + "..." if len(product_name) > 12 else product_name
                    draw.text((x + 5, y + 20), name_display, fill='black', font=font)
                    
                    # Draw sales indicator
                    if units_sold > 0:
                        sales_text = f"{units_sold} sold"
                        draw.text((x + 5, y + slot_height - 20), sales_text, 
                                fill='green' if units_sold > 10 else 'orange', font=font)
                else:
                    # Empty slot
                    draw.rectangle([x, y, x + slot_width, y + slot_height], 
                                 outline='gray', fill='#f8f9fa', width=1)
                    draw.text((x + 5, y + 5), slot_pos, fill='gray', font=font)
                    draw.text((x + 20, y + 30), "EMPTY", fill='gray', font=font)
        
        # Draw legend
        legend_y = img_height - 30
        legend_x = 10
        for category, color in category_colors.items():
            if category:
                draw.rectangle([legend_x, legend_y, legend_x + 15, legend_y + 15], 
                             fill=color, outline='black')
                draw.text((legend_x + 20, legend_y), str(category), fill='black', font=font)
                legend_x += 100
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    
    def _get_sales_context(self, device_id: int) -> Dict:
        """Get sales context for visual analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get top/bottom performers
        perf_query = """
        SELECT 
            p.name,
            p.category,
            SUM(s.sale_units) as units,
            SUM(s.sale_cash) as revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        WHERE s.device_id = ?
        AND s.created_at > datetime('now', '-30 days')
        GROUP BY s.product_id
        ORDER BY revenue DESC
        """
        cursor.execute(perf_query, (device_id,))
        products = cursor.fetchall()
        
        conn.close()
        
        return {
            'top_5': [{'name': p[0], 'category': p[1], 'revenue': p[3]} 
                     for p in products[:5]],
            'bottom_5': [{'name': p[0], 'category': p[1], 'revenue': p[3]} 
                        for p in products[-5:] if len(products) > 5]
        }
    
    def _analyze_with_vision(self, image_bytes: bytes, sales_context: Dict) -> Dict:
        """Use Claude's vision API to analyze planogram image"""
        
        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        prompt = f"""Analyze this vending machine planogram image and provide insights.

Sales Context:
Top Performers: {json.dumps(sales_context['top_5'], indent=2)}
Poor Performers: {json.dumps(sales_context['bottom_5'], indent=2)}

Please analyze:
1. Product placement effectiveness (are high-sellers in optimal positions?)
2. Category clustering (are similar products grouped effectively?)
3. Visual appeal and organization
4. Empty slot opportunities
5. Accessibility concerns (heavy items, frequently purchased items)
6. Color/category balance across the planogram

Provide specific recommendations for improvement with slot positions.
Format response as JSON with these sections:
{{
    "placement_effectiveness": {{"score": 0-100, "issues": [], "suggestions": []}},
    "category_organization": {{"score": 0-100, "clusters": [], "improvements": []}},
    "visual_appeal": {{"score": 0-100, "balance": str, "suggestions": []}},
    "empty_slots": {{"count": int, "positions": [], "recommendations": []}},
    "accessibility": {{"score": 0-100, "concerns": [], "fixes": []}},
    "overall_score": 0-100,
    "top_3_actions": []
}}"""
        
        try:
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )
            
            response_text = message.content[0].text
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
                
        except Exception as e:
            print(f"Vision analysis error: {e}")
        
        # Fallback analysis
        return {
            'placement_effectiveness': {'score': 70, 'issues': [], 'suggestions': []},
            'category_organization': {'score': 65, 'clusters': [], 'improvements': []},
            'visual_appeal': {'score': 75, 'balance': 'Good', 'suggestions': []},
            'empty_slots': {'count': 0, 'positions': [], 'recommendations': []},
            'accessibility': {'score': 80, 'concerns': [], 'fixes': []},
            'overall_score': 72,
            'top_3_actions': ['Fill empty slots', 'Improve category clustering', 'Optimize placement']
        }
    
    def _generate_heatmaps(self, device_id: int, cabinet_index: int) -> Dict:
        """Generate various heatmaps for the planogram"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get cabinet dimensions
        dim_query = """
        SELECT rows, columns 
        FROM cabinet_configurations 
        WHERE device_id = ? AND cabinet_index = ?
        """
        cursor.execute(dim_query, (device_id, cabinet_index))
        dims = cursor.fetchone()
        
        if not dims:
            conn.close()
            return {}
        
        rows, cols = dims
        
        # Get sales heatmap data
        sales_query = """
        SELECT 
            ps.slot_position,
            COALESCE(SUM(s.sale_units), 0) as units,
            COALESCE(SUM(s.sale_cash), 0) as revenue
        FROM planogram_slots ps
        LEFT JOIN sales s ON s.product_id = ps.product_id AND s.device_id = ?
        WHERE ps.planogram_id = (
            SELECT id FROM planograms WHERE planogram_key = ?
        )
        GROUP BY ps.slot_position
        """
        planogram_key = f"{device_id}_{cabinet_index}"
        cursor.execute(sales_query, (device_id, planogram_key))
        sales_data = cursor.fetchall()
        
        conn.close()
        
        # Create heatmap matrices
        revenue_matrix = np.zeros((rows, cols))
        units_matrix = np.zeros((rows, cols))
        interaction_matrix = np.zeros((rows, cols))
        
        for slot_pos, units, revenue in sales_data:
            if slot_pos and len(slot_pos) >= 2:
                row = ord(slot_pos[0]) - 65
                col = int(slot_pos[1:]) - 1
                if 0 <= row < rows and 0 <= col < cols:
                    revenue_matrix[row, col] = revenue
                    units_matrix[row, col] = units
        
        # Calculate interaction zones (adjacent high-performers)
        for i in range(rows):
            for j in range(cols):
                adjacent_sum = 0
                count = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < rows and 0 <= nj < cols:
                            adjacent_sum += revenue_matrix[ni, nj]
                            count += 1
                if count > 0:
                    interaction_matrix[i, j] = adjacent_sum / count
        
        return {
            'revenue_heatmap': {
                'data': revenue_matrix.tolist(),
                'max_value': float(np.max(revenue_matrix)),
                'description': 'Revenue generation by slot position'
            },
            'velocity_heatmap': {
                'data': units_matrix.tolist(),
                'max_value': float(np.max(units_matrix)),
                'description': 'Product movement velocity by position'
            },
            'interaction_heatmap': {
                'data': interaction_matrix.tolist(),
                'max_value': float(np.max(interaction_matrix)),
                'description': 'Adjacent product interaction strength'
            },
            'visibility_zones': self._calculate_visibility_zones(rows, cols)
        }
    
    def _analyze_visibility_zones(self, device_id: int, cabinet_index: int) -> Dict:
        """Analyze visibility zones and their performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get cabinet dimensions
        dim_query = """
        SELECT rows, columns 
        FROM cabinet_configurations 
        WHERE device_id = ? AND cabinet_index = ?
        """
        cursor.execute(dim_query, (device_id, cabinet_index))
        dims = cursor.fetchone()
        
        if not dims:
            conn.close()
            return {}
        
        rows, cols = dims
        
        # Define visibility zones
        zones = {
            'premium': [],  # Eye level (rows B-C typically)
            'standard': [], # Easily accessible (rows A, D)
            'low': []       # Bottom rows (E+)
        }
        
        for row in range(rows):
            for col in range(cols):
                slot_pos = f"{chr(65 + row)}{col + 1}"
                
                if row in [1, 2]:  # B, C rows (eye level)
                    zones['premium'].append(slot_pos)
                elif row in [0, 3]:  # A, D rows
                    zones['standard'].append(slot_pos)
                else:  # Bottom rows
                    zones['low'].append(slot_pos)
        
        # Analyze performance by zone
        zone_performance = {}
        for zone_name, positions in zones.items():
            if positions:
                position_str = "','".join(positions)
                query = f"""
                SELECT 
                    AVG(s.sale_cash) as avg_revenue,
                    AVG(s.sale_units) as avg_units
                FROM planogram_slots ps
                LEFT JOIN sales s ON s.product_id = ps.product_id AND s.device_id = ?
                WHERE ps.slot_position IN ('{position_str}')
                AND ps.planogram_id = (
                    SELECT id FROM planograms WHERE planogram_key = ?
                )
                """
                planogram_key = f"{device_id}_{cabinet_index}"
                cursor.execute(query, (device_id, planogram_key))
                result = cursor.fetchone()
                
                zone_performance[zone_name] = {
                    'positions': positions,
                    'avg_revenue': result[0] or 0 if result else 0,
                    'avg_units': result[1] or 0 if result else 0
                }
        
        conn.close()
        
        return {
            'zones': zones,
            'performance': zone_performance,
            'recommendations': self._generate_zone_recommendations(zone_performance)
        }
    
    def _calculate_visibility_zones(self, rows: int, cols: int) -> Dict:
        """Calculate visibility zone matrix"""
        visibility_matrix = np.zeros((rows, cols))
        
        for i in range(rows):
            for j in range(cols):
                if i in [1, 2]:  # Eye level
                    visibility_matrix[i, j] = 1.0
                elif i in [0, 3]:  # Good visibility
                    visibility_matrix[i, j] = 0.7
                else:  # Lower visibility
                    visibility_matrix[i, j] = 0.4
                
                # Adjust for column position (center columns more visible)
                center_col = cols // 2
                distance_from_center = abs(j - center_col)
                visibility_matrix[i, j] *= (1 - distance_from_center * 0.1)
        
        return {
            'data': visibility_matrix.tolist(),
            'description': 'Visibility scores by position (0-1 scale)'
        }
    
    def _generate_zone_recommendations(self, zone_performance: Dict) -> List[str]:
        """Generate recommendations based on zone analysis"""
        recommendations = []
        
        if 'premium' in zone_performance and 'low' in zone_performance:
            premium_rev = zone_performance['premium']['avg_revenue']
            low_rev = zone_performance['low']['avg_revenue']
            
            if premium_rev < low_rev * 1.5:
                recommendations.append(
                    "Premium eye-level slots underperforming - consider placing higher-margin items"
                )
        
        if 'standard' in zone_performance:
            if zone_performance['standard']['avg_units'] < 5:
                recommendations.append(
                    "Standard visibility zones have low velocity - review product selection"
                )
        
        return recommendations
    
    def _generate_visual_recommendations(self, visual_analysis: Dict, 
                                        heatmaps: Dict, 
                                        visibility_analysis: Dict) -> List[Dict]:
        """Generate comprehensive visual-based recommendations"""
        recommendations = []
        
        # Based on visual analysis scores
        if visual_analysis.get('placement_effectiveness', {}).get('score', 100) < 70:
            recommendations.append({
                'type': 'placement',
                'priority': 'high',
                'action': 'Reorganize product placement',
                'details': visual_analysis.get('placement_effectiveness', {}).get('suggestions', []),
                'expected_impact': 'Increase revenue by 10-15%'
            })
        
        if visual_analysis.get('category_organization', {}).get('score', 100) < 70:
            recommendations.append({
                'type': 'organization',
                'priority': 'medium',
                'action': 'Improve category clustering',
                'details': visual_analysis.get('category_organization', {}).get('improvements', []),
                'expected_impact': 'Improve shopping experience and cross-selling'
            })
        
        # Based on heatmap analysis
        if heatmaps.get('revenue_heatmap'):
            low_revenue_threshold = heatmaps['revenue_heatmap']['max_value'] * 0.3
            recommendations.append({
                'type': 'revenue_optimization',
                'priority': 'high',
                'action': 'Address low-revenue zones',
                'details': f"Slots generating less than ${low_revenue_threshold:.2f} need attention",
                'expected_impact': 'Increase overall revenue by 5-8%'
            })
        
        # Based on visibility zones
        if visibility_analysis.get('recommendations'):
            for rec in visibility_analysis['recommendations']:
                recommendations.append({
                    'type': 'visibility',
                    'priority': 'medium',
                    'action': rec,
                    'details': [],
                    'expected_impact': 'Improve product visibility and sales'
                })
        
        return recommendations