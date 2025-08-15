"""
Real-time Data Pipeline for Planogram AI Assistant
Structures and optimizes data for LLM consumption
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib

class RealtimePlanogramPipeline:
    """Optimized data pipeline for real-time AI assistance"""
    
    def __init__(self, db_path: str = 'cvd.db'):
        self.db_path = db_path
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes
        
    def structure_for_llm(self, device_id: int, cabinet_index: int, 
                         user_action: str = None, target_product: Dict = None) -> Dict:
        """
        Structure all relevant data for LLM analysis
        Optimizes token usage while maintaining context
        """
        
        # Get device and cabinet info
        device_info = self._get_device_info(device_id)
        cabinet_info = self._get_cabinet_info(device_id, cabinet_index)
        
        # Get current planogram state
        planogram_state = self._get_planogram_state(device_id, cabinet_index)
        
        # Get performance metrics (last 30 days)
        performance = self._get_performance_metrics(device_id, days=30)
        
        # Structure for optimal token usage
        context = {
            "device_context": {
                "id": device_id,
                "name": device_info.get('cooler'),
                "asset": device_info.get('asset'),
                "location": self._simplify_location(device_info.get('location')),
                "type": device_info.get('device_type')
            },
            "cabinet_context": {
                "type": cabinet_info.get('type'),
                "layout": f"{cabinet_info.get('rows')}x{cabinet_info.get('columns')}",
                "temperature": self._map_temperature_zone(cabinet_info.get('type')),
                "total_slots": cabinet_info.get('rows', 0) * cabinet_info.get('columns', 0)
            },
            "planogram_summary": {
                "filled_slots": planogram_state['filled_count'],
                "empty_slots": planogram_state['empty_count'],
                "unique_products": planogram_state['unique_products'],
                "categories": planogram_state['categories'],
                "avg_price": planogram_state['avg_price']
            },
            "performance_summary": {
                "daily_revenue": round(performance['avg_daily_revenue'], 2),
                "top_sellers": performance['top_5_products'],
                "slow_movers": performance['bottom_5_products'],
                "stockout_risk": performance['stockout_count']
            }
        }
        
        # Add user action context if provided
        if user_action:
            context["current_action"] = {
                "action": user_action,
                "product": target_product.get('name') if target_product else None,
                "category": target_product.get('category') if target_product else None,
                "price": target_product.get('price') if target_product else None
            }
        
        return context
    
    def _get_device_info(self, device_id: int) -> Dict:
        """Get device information with caching"""
        cache_key = f"device_{device_id}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
        SELECT d.*, l.name as location, dt.name as device_type
        FROM devices d
        LEFT JOIN locations l ON d.location_id = l.id
        LEFT JOIN device_types dt ON d.device_type_id = dt.id
        WHERE d.id = ?
        """
        cursor.execute(query, (device_id,))
        result = cursor.fetchone()
        conn.close()
        
        data = dict(result) if result else {}
        self._set_cache(cache_key, data)
        return data
    
    def _get_cabinet_info(self, device_id: int, cabinet_index: int) -> Dict:
        """Get cabinet configuration"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
        SELECT cc.*, ct.name as type
        FROM cabinet_configurations cc
        JOIN cabinet_types ct ON cc.cabinet_type_id = ct.id
        WHERE cc.device_id = ? AND cc.cabinet_index = ?
        """
        cursor.execute(query, (device_id, cabinet_index))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else {}
    
    def _get_planogram_state(self, device_id: int, cabinet_index: int) -> Dict:
        """Get current planogram state summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        planogram_key = f"{device_id}_{cabinet_index}"
        
        # Get slot statistics
        query = """
        SELECT 
            COUNT(*) as total_slots,
            COUNT(CASE WHEN ps.product_id != 1 THEN 1 END) as filled_slots,
            COUNT(DISTINCT CASE WHEN ps.product_id != 1 THEN ps.product_id END) as unique_products,
            COUNT(DISTINCT p.category) as category_count,
            AVG(CASE WHEN ps.product_id != 1 THEN ps.price END) as avg_price
        FROM planogram_slots ps
        LEFT JOIN products p ON ps.product_id = p.id
        WHERE ps.planogram_id = (
            SELECT id FROM planograms WHERE planogram_key = ?
        )
        """
        cursor.execute(query, (planogram_key,))
        result = cursor.fetchone()
        
        # Get category list
        cat_query = """
        SELECT DISTINCT p.category
        FROM planogram_slots ps
        JOIN products p ON ps.product_id = p.id
        WHERE ps.planogram_id = (
            SELECT id FROM planograms WHERE planogram_key = ?
        ) AND ps.product_id != 1
        """
        cursor.execute(cat_query, (planogram_key,))
        categories = [row[0] for row in cursor.fetchall() if row[0]]
        
        conn.close()
        
        if result:
            return {
                'total_slots': result[0] or 0,
                'filled_count': result[1] or 0,
                'empty_count': (result[0] or 0) - (result[1] or 0),
                'unique_products': result[2] or 0,
                'categories': categories,
                'avg_price': round(result[4] or 0, 2)
            }
        return {
            'total_slots': 0,
            'filled_count': 0,
            'empty_count': 0,
            'unique_products': 0,
            'categories': [],
            'avg_price': 0
        }
    
    def _get_performance_metrics(self, device_id: int, days: int = 30) -> Dict:
        """Get performance metrics optimized for token usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get revenue summary
        rev_query = """
        SELECT 
            AVG(sale_cash) as avg_daily_revenue,
            SUM(sale_cash) as total_revenue,
            COUNT(DISTINCT DATE(created_at)) as days_with_sales
        FROM sales
        WHERE device_id = ? 
        AND created_at > datetime('now', '-' || ? || ' days')
        """
        cursor.execute(rev_query, (device_id, days))
        rev_result = cursor.fetchone()
        
        # Get top/bottom products (limit to save tokens)
        product_query = """
        SELECT 
            p.name,
            SUM(s.sale_units) as units,
            SUM(s.sale_cash) as revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        WHERE s.device_id = ?
        AND s.created_at > datetime('now', '-' || ? || ' days')
        GROUP BY s.product_id
        ORDER BY revenue DESC
        """
        cursor.execute(product_query, (device_id, days))
        products = cursor.fetchall()
        
        conn.close()
        
        # Format for token efficiency
        top_5 = [f"{p[0]}:${p[2]:.0f}" for p in products[:5]] if products else []
        bottom_5 = [f"{p[0]}:${p[2]:.0f}" for p in products[-5:]] if len(products) > 5 else []
        
        return {
            'avg_daily_revenue': rev_result[0] or 0 if rev_result else 0,
            'total_revenue': rev_result[1] or 0 if rev_result else 0,
            'top_5_products': top_5,
            'bottom_5_products': bottom_5,
            'stockout_count': 0  # Would need inventory tracking
        }
    
    def _simplify_location(self, location: str) -> str:
        """Simplify location string to save tokens"""
        if not location:
            return "Unknown"
        # Extract key parts of location
        parts = location.split(',')
        if len(parts) > 1:
            return f"{parts[0].strip()}, {parts[-1].strip()}"
        return location[:50]  # Truncate long locations
    
    def _map_temperature_zone(self, cabinet_type: str) -> str:
        """Map cabinet type to temperature zone"""
        zones = {
            'Cooler': 'Cold (35-45°F)',
            'Freezer': 'Frozen (0-10°F)',
            'Ambient': 'Room temp',
            'Ambient+': 'Room temp'
        }
        return zones.get(cabinet_type, 'Unknown')
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid"""
        if key not in self.cache:
            return False
        return (datetime.now() - self.cache[key]['timestamp']).seconds < self.cache_ttl
    
    def _set_cache(self, key: str, data: Any):
        """Set cache entry with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }

class StreamingAssistant:
    """Handle streaming responses for real-time feedback"""
    
    def __init__(self, anthropic_client):
        self.client = anthropic_client
        
    async def stream_placement_analysis(self, context: Dict, callback):
        """Stream AI analysis as user drags products"""
        
        # Optimize prompt for fast response
        prompt = self._build_fast_analysis_prompt(context)
        
        # Use streaming for immediate feedback
        stream = await self.client.messages.create(
            model="claude-3-haiku-20240307",  # Faster model for real-time
            max_tokens=500,
            temperature=0.3,  # Lower temperature for consistency
            stream=True,
            messages=[{"role": "user", "content": prompt}]
        )
        
        buffer = ""
        async for chunk in stream:
            if chunk.type == "content_block_delta":
                buffer += chunk.delta.text
                # Parse and send incremental updates
                if self._is_complete_json_object(buffer):
                    try:
                        result = json.loads(buffer)
                        await callback(result)
                        buffer = ""
                    except json.JSONDecodeError:
                        continue
    
    def _build_fast_analysis_prompt(self, context: Dict) -> str:
        """Build optimized prompt for fast analysis"""
        return f"""Quick placement analysis:
Product: {context.get('product_name')}
Slot: {context.get('target_slot')}
Adjacent: {context.get('adjacent_products')}

Rate placement (0-100) and suggest if poor. Brief JSON response."""
    
    def _is_complete_json_object(self, text: str) -> bool:
        """Check if text contains complete JSON object"""
        return text.count('{') == text.count('}') and text.strip().endswith('}')