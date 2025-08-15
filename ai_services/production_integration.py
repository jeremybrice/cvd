"""
Production-Ready LLM Integration for Flask Application
Complete integration with endpoints, streaming, and monitoring
"""

import os
import json
import asyncio
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from typing import Dict, List, Optional, Generator
import time
from datetime import datetime
import sqlite3
import logging

# Import our LLM pipeline components
from llm_integration_pipeline import (
    LLMIntegrationPipeline,
    ModelType,
    TokenLimits,
    UsageMetrics,
    DataStructurer,
    SemanticCache,
    CostMonitor,
    ErrorHandler
)
from advanced_prompts import (
    AdvancedPromptTemplates,
    ChainOfThoughtPrompts,
    ReasoningPattern,
    PromptComposer
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# FLASK APPLICATION SETUP
# =============================================================================

def create_app():
    """Create and configure Flask application with LLM endpoints"""
    app = Flask(__name__)
    CORS(app)
    
    # Initialize LLM pipeline
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.warning("No Anthropic API key found, using fallback mode")
        pipeline = None
    else:
        pipeline = LLMIntegrationPipeline(
            api_key=api_key,
            db_path='cvd.db',
            cache_enabled=True,
            cost_monitoring=True
        )
    
    # =============================================================================
    # REAL-TIME ENDPOINTS
    # =============================================================================
    
    @app.route('/api/planogram/realtime-score', methods=['POST'])
    async def realtime_placement_score():
        """Get instant placement score during drag-and-drop"""
        if not pipeline:
            return jsonify({'error': 'AI service unavailable'}), 503
        
        try:
            data = request.json
            
            # Prepare context for real-time scoring
            context = {
                'product_name': data.get('product_name'),
                'product_id': data.get('product_id'),
                'target_position': data.get('target_position'),
                'cabinet_type': data.get('cabinet_type'),
                'planogram': data.get('current_planogram'),
                'product_velocity': data.get('product_velocity', 0),
                'product_revenue': data.get('product_revenue', 0),
                'position_revenue': data.get('position_revenue', 0),
                'temperature_zone': data.get('temperature_zone', 'ambient'),
                'weight_limit': data.get('weight_limit', 10),
                'adjacent_products': data.get('adjacent_products', '')
            }
            
            # Use Haiku for speed
            result = await pipeline.process_request(
                feature='realtime',
                data=context,
                stream=False
            )
            
            if result.get('success'):
                # Parse the response
                response_data = json.loads(result['result'])
                response_data['latency_ms'] = result['latency_ms']
                response_data['cached'] = result.get('cached', False)
                return jsonify(response_data)
            else:
                return jsonify({'error': result.get('error')}), 500
                
        except Exception as e:
            logger.error(f"Realtime scoring error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/planogram/predict-revenue', methods=['POST'])
    async def predict_revenue_impact():
        """Predict revenue impact of planogram changes"""
        if not pipeline:
            return jsonify({'error': 'AI service unavailable'}), 503
        
        try:
            data = request.json
            
            # Prepare data for revenue prediction
            context = {
                'current_planogram': data.get('current_planogram'),
                'proposed_planogram': data.get('proposed_planogram'),
                'current_daily_revenue': data.get('current_revenue', 0),
                'weekly_trend': data.get('weekly_trend', 0),
                'top_products_json': json.dumps(data.get('top_products', [])),
                'stockout_rate': data.get('stockout_rate', 0),
                'changes_xml': DataStructurer.planogram_to_xml(data.get('changes', {})),
                'historical_outcomes_json': json.dumps(data.get('historical', [])),
                'venue_type': data.get('venue_type', 'unknown'),
                'traffic_json': json.dumps(data.get('traffic', {})),
                'demographics_json': json.dumps(data.get('demographics', {})),
                'competition_level': data.get('competition', 'medium')
            }
            
            # Use Sonnet for balanced performance
            result = await pipeline.process_request(
                feature='prediction',
                data=context,
                stream=False
            )
            
            if result.get('success'):
                response_data = json.loads(result['result'])
                return jsonify({
                    'success': True,
                    'prediction': response_data,
                    'latency_ms': result['latency_ms']
                })
            else:
                return jsonify({'error': result.get('error')}), 500
                
        except Exception as e:
            logger.error(f"Revenue prediction error: {e}")
            return jsonify({'error': str(e)}), 500
    
    # =============================================================================
    # STREAMING ENDPOINTS
    # =============================================================================
    
    @app.route('/api/planogram/stream-optimization', methods=['POST'])
    def stream_optimization():
        """Stream optimization results as they're generated"""
        if not pipeline:
            return jsonify({'error': 'AI service unavailable'}), 503
        
        def generate():
            """Generator for streaming response"""
            try:
                data = request.json
                
                # Prepare context
                context = {
                    'device_id': data.get('device_id'),
                    'cabinet_index': data.get('cabinet_index', 0),
                    'optimization_type': data.get('type', 'revenue'),
                    'planogram': data.get('planogram'),
                    'sales_data': data.get('sales_data'),
                    'constraints': data.get('constraints', {})
                }
                
                # Stream results
                async def async_stream():
                    async for chunk in pipeline.process_request(
                        feature='optimization',
                        data=context,
                        stream=True
                    ):
                        yield f"data: {json.dumps(chunk)}\n\n"
                
                # Run async generator in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                for item in loop.run_until_complete(async_stream()):
                    yield item
                    
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    
    # =============================================================================
    # BATCH PROCESSING ENDPOINTS
    # =============================================================================
    
    @app.route('/api/planogram/batch-optimize', methods=['POST'])
    async def batch_optimize():
        """Optimize multiple planograms in batch"""
        if not pipeline:
            return jsonify({'error': 'AI service unavailable'}), 503
        
        try:
            data = request.json
            device_ids = data.get('device_ids', [])
            optimization_type = data.get('optimization_type', 'revenue')
            
            # Process batch
            results = await pipeline.batch.batch_optimize(
                device_ids=device_ids,
                optimization_type=optimization_type
            )
            
            return jsonify({
                'success': True,
                'results': results,
                'devices_processed': len(results)
            })
            
        except Exception as e:
            logger.error(f"Batch optimization error: {e}")
            return jsonify({'error': str(e)}), 500
    
    # =============================================================================
    # ADVANCED ANALYSIS ENDPOINTS
    # =============================================================================
    
    @app.route('/api/planogram/heat-zone-analysis', methods=['POST'])
    async def heat_zone_analysis():
        """Analyze and optimize based on visibility zones"""
        if not pipeline:
            return jsonify({'error': 'AI service unavailable'}), 503
        
        try:
            data = request.json
            
            # Use advanced heat zone template
            template = AdvancedPromptTemplates.heat_zone_optimization()
            
            context = {
                'planogram_with_zones_xml': DataStructurer.planogram_to_xml(
                    data.get('planogram')
                ),
                'products_json_with_attributes': json.dumps(
                    data.get('products', [])
                ),
                'zone_a_revenue': data.get('zone_revenues', {}).get('A', 0),
                'zone_b_revenue': data.get('zone_revenues', {}).get('B', 0),
                'zone_c_revenue': data.get('zone_revenues', {}).get('C', 0),
                'zone_d_revenue': data.get('zone_revenues', {}).get('D', 0),
                'zone_a_velocity': data.get('zone_velocities', {}).get('A', 0),
                'zone_b_velocity': data.get('zone_velocities', {}).get('B', 0),
                'zone_c_velocity': data.get('zone_velocities', {}).get('C', 0),
                'zone_d_velocity': data.get('zone_velocities', {}).get('D', 0)
            }
            
            # Format template with data
            prompt = template.format(**context)
            
            # Process with Opus for complex analysis
            result = await pipeline._process_standard(
                prompt=prompt,
                model=ModelType.COMPLEX
            )
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'analysis': json.loads(result['result']),
                    'latency_ms': result['latency_ms']
                })
            else:
                return jsonify({'error': result.get('error')}), 500
                
        except Exception as e:
            logger.error(f"Heat zone analysis error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/planogram/affinity-analysis', methods=['POST'])
    async def affinity_analysis():
        """Analyze product affinities and clustering"""
        if not pipeline:
            return jsonify({'error': 'AI service unavailable'}), 503
        
        try:
            data = request.json
            
            context = {
                'transactions': data.get('transactions', []),
                'current_planogram': data.get('planogram'),
                'products': data.get('products', [])
            }
            
            result = await pipeline.process_request(
                feature='affinity',
                data=context,
                stream=False
            )
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'affinities': json.loads(result['result']),
                    'latency_ms': result['latency_ms']
                })
            else:
                return jsonify({'error': result.get('error')}), 500
                
        except Exception as e:
            logger.error(f"Affinity analysis error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/planogram/demand-forecast', methods=['POST'])
    async def demand_forecast():
        """Forecast demand and optimize inventory"""
        if not pipeline:
            return jsonify({'error': 'AI service unavailable'}), 503
        
        try:
            data = request.json
            
            # Use demand forecasting template
            template = AdvancedPromptTemplates.demand_forecasting()
            
            context = {
                'ninety_day_sales_json': json.dumps(data.get('sales_history', [])),
                'stockout_history_json': json.dumps(data.get('stockouts', [])),
                'service_schedule_json': json.dumps(data.get('service_visits', [])),
                'current_weather': data.get('current_weather', 'unknown'),
                'weather_forecast_json': json.dumps(data.get('weather_forecast', [])),
                'weather_impact_json': json.dumps(data.get('weather_correlations', {})),
                'upcoming_events_json': json.dumps(data.get('events', [])),
                'event_impact_json': json.dumps(data.get('event_impacts', {})),
                'dow_patterns_json': json.dumps(data.get('day_patterns', {})),
                'monthly_trends_json': json.dumps(data.get('monthly_trends', {})),
                'holiday_impacts_json': json.dumps(data.get('holiday_effects', {})),
                'product_shelf_life_json': json.dumps(data.get('shelf_life', {})),
                'slot_capacities_json': json.dumps(data.get('capacities', {})),
                'service_interval_days': data.get('service_interval', 7)
            }
            
            prompt = template.format(**context)
            
            result = await pipeline._process_standard(
                prompt=prompt,
                model=ModelType.COMPLEX
            )
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'forecast': json.loads(result['result']),
                    'latency_ms': result['latency_ms']
                })
            else:
                return jsonify({'error': result.get('error')}), 500
                
        except Exception as e:
            logger.error(f"Demand forecast error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/planogram/location-personalize', methods=['POST'])
    async def location_personalization():
        """Personalize planogram for specific location"""
        if not pipeline:
            return jsonify({'error': 'AI service unavailable'}), 503
        
        try:
            data = request.json
            
            context = {
                'venue_type': data.get('venue_type'),
                'venue_subtype': data.get('venue_subtype', ''),
                'venue_size': data.get('venue_size', 'medium'),
                'operating_hours': data.get('hours', '9-5'),
                'demographics_json': json.dumps(data.get('demographics', {})),
                'current_performance_json': json.dumps(data.get('performance', {})),
                'hourly_traffic_json': json.dumps(data.get('traffic', {})),
                'time_of_day_sales_json': json.dumps(data.get('sales_by_time', {})),
                'category_performance_json': json.dumps(data.get('category_data', {})),
                'price_point_analysis_json': json.dumps(data.get('price_analysis', {})),
                'competitor_machines_json': json.dumps(data.get('competitors', [])),
                'nearby_retail_json': json.dumps(data.get('retail', [])),
                'differentiation_score': data.get('differentiation', 0.5)
            }
            
            result = await pipeline.process_request(
                feature='personalization',
                data=context,
                stream=False
            )
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'personalization': json.loads(result['result']),
                    'latency_ms': result['latency_ms']
                })
            else:
                return jsonify({'error': result.get('error')}), 500
                
        except Exception as e:
            logger.error(f"Location personalization error: {e}")
            return jsonify({'error': str(e)}), 500
    
    # =============================================================================
    # MONITORING & ANALYTICS ENDPOINTS
    # =============================================================================
    
    @app.route('/api/planogram/ai-usage', methods=['GET'])
    def get_ai_usage():
        """Get AI usage statistics and costs"""
        if not pipeline or not pipeline.cost_monitor:
            return jsonify({'error': 'Cost monitoring not available'}), 503
        
        try:
            # Get usage stats
            daily_usage = pipeline.cost_monitor.get_daily_usage()
            feature_costs = pipeline.cost_monitor.get_feature_costs()
            
            return jsonify({
                'daily': daily_usage,
                'by_feature': feature_costs,
                'budget_remaining': pipeline.cost_monitor.daily_limit - daily_usage['total_cost']
            })
            
        except Exception as e:
            logger.error(f"Usage stats error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/planogram/cache-stats', methods=['GET'])
    def get_cache_stats():
        """Get cache performance statistics"""
        if not pipeline or not pipeline.cache:
            return jsonify({'error': 'Cache not available'}), 503
        
        try:
            cache_dir = pipeline.cache.cache_dir
            cache_files = os.listdir(cache_dir)
            total_size = sum(
                os.path.getsize(os.path.join(cache_dir, f))
                for f in cache_files
            ) / 1024 / 1024  # MB
            
            return jsonify({
                'entries': len(cache_files),
                'size_mb': round(total_size, 2),
                'ttl_hours': pipeline.cache.ttl.total_seconds() / 3600
            })
            
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/planogram/clear-cache', methods=['POST'])
    def clear_cache():
        """Clear expired cache entries"""
        if not pipeline or not pipeline.cache:
            return jsonify({'error': 'Cache not available'}), 503
        
        try:
            pipeline.cache.clear_expired()
            return jsonify({'success': True, 'message': 'Expired cache cleared'})
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return jsonify({'error': str(e)}), 500
    
    # =============================================================================
    # TESTING & VALIDATION ENDPOINTS
    # =============================================================================
    
    @app.route('/api/planogram/test-prompt', methods=['POST'])
    async def test_prompt():
        """Test a custom prompt template"""
        if not pipeline:
            return jsonify({'error': 'AI service unavailable'}), 503
        
        try:
            data = request.json
            prompt = data.get('prompt', '')
            model = data.get('model', 'analysis')
            variables = data.get('variables', {})
            
            # Format prompt with variables
            formatted_prompt = prompt.format(**variables)
            
            # Select model
            model_type = pipeline.select_model(model)
            
            # Process
            result = await pipeline._process_standard(
                prompt=formatted_prompt,
                model=model_type
            )
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'response': result['result'],
                    'tokens': {
                        'input': result.get('input_tokens', 0),
                        'output': result.get('output_tokens', 0)
                    },
                    'latency_ms': result['latency_ms']
                })
            else:
                return jsonify({'error': result.get('error')}), 500
                
        except Exception as e:
            logger.error(f"Prompt test error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/planogram/validate-data', methods=['POST'])
    def validate_planogram_data():
        """Validate planogram data structure for AI processing"""
        try:
            data = request.json
            
            issues = []
            warnings = []
            
            # Check required fields
            required = ['planogram', 'device_id']
            for field in required:
                if field not in data:
                    issues.append(f"Missing required field: {field}")
            
            # Check planogram structure
            if 'planogram' in data:
                planogram = data['planogram']
                if 'slots' not in planogram:
                    issues.append("Planogram missing 'slots' array")
                elif not isinstance(planogram['slots'], list):
                    issues.append("Planogram 'slots' must be an array")
                else:
                    # Check slot structure
                    for i, slot in enumerate(planogram['slots']):
                        if 'position' not in slot:
                            warnings.append(f"Slot {i} missing position")
                        if 'product_id' not in slot and 'product_name' not in slot:
                            warnings.append(f"Slot {i} missing product information")
            
            # Check sales data if provided
            if 'sales_data' in data:
                if not isinstance(data['sales_data'], list):
                    issues.append("Sales data must be an array")
            
            return jsonify({
                'valid': len(issues) == 0,
                'issues': issues,
                'warnings': warnings,
                'ready_for_ai': len(issues) == 0
            })
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return jsonify({'error': str(e)}), 500
    
    # =============================================================================
    # WEBSOCKET SUPPORT (using Flask-SocketIO)
    # =============================================================================
    
    # Note: For production WebSocket support, add Flask-SocketIO
    # from flask_socketio import SocketIO, emit
    # socketio = SocketIO(app, cors_allowed_origins="*")
    
    # @socketio.on('optimize_planogram')
    # def handle_optimization(data):
    #     """WebSocket handler for real-time optimization"""
    #     async def process():
    #         async for chunk in pipeline.process_request('optimization', data, stream=True):
    #             emit('optimization_update', chunk)
    #     asyncio.run(process())
    
    return app

# =============================================================================
# INTEGRATION HELPERS
# =============================================================================

class PlanogramAIService:
    """Service class for integrating AI into existing planogram operations"""
    
    def __init__(self, db_path: str = 'cvd.db'):
        self.db_path = db_path
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if api_key:
            self.pipeline = LLMIntegrationPipeline(
                api_key=api_key,
                db_path=db_path,
                cache_enabled=True,
                cost_monitoring=True
            )
        else:
            self.pipeline = None
            logger.warning("AI service running in fallback mode")
    
    def enhance_planogram_with_ai(self, planogram_id: str) -> Dict:
        """Enhance existing planogram with AI recommendations"""
        if not self.pipeline:
            return self._fallback_enhancement(planogram_id)
        
        try:
            # Fetch planogram data
            planogram_data = self._fetch_planogram(planogram_id)
            sales_data = self._fetch_sales_data(planogram_data['device_id'])
            
            # Get AI recommendations
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.pipeline.process_request(
                    feature='optimization',
                    data={
                        'planogram': planogram_data,
                        'sales_data': sales_data,
                        'device_id': planogram_data['device_id']
                    }
                )
            )
            
            if result.get('success'):
                recommendations = json.loads(result['result'])
                return {
                    'success': True,
                    'original': planogram_data,
                    'recommendations': recommendations,
                    'confidence': self._calculate_confidence(recommendations)
                }
            else:
                return self._fallback_enhancement(planogram_id)
                
        except Exception as e:
            logger.error(f"AI enhancement error: {e}")
            return self._fallback_enhancement(planogram_id)
    
    def _fetch_planogram(self, planogram_id: str) -> Dict:
        """Fetch planogram from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, d.name as device_name
            FROM planograms p
            JOIN devices d ON p.device_id = d.id
            WHERE p.planogram_key = ?
        """, (planogram_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(zip([col[0] for col in cursor.description], result))
        return {}
    
    def _fetch_sales_data(self, device_id: int) -> List[Dict]:
        """Fetch recent sales data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.*, p.name as product_name, p.category
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.device_id = ?
            AND s.created_at >= datetime('now', '-30 days')
            ORDER BY s.created_at DESC
        """, (device_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            dict(zip([col[0] for col in cursor.description], row))
            for row in results
        ]
    
    def _fallback_enhancement(self, planogram_id: str) -> Dict:
        """Rule-based fallback when AI is unavailable"""
        return {
            'success': False,
            'fallback': True,
            'message': 'Using rule-based optimization',
            'recommendations': [
                {
                    'type': 'general',
                    'suggestion': 'Place high-margin items at eye level',
                    'confidence': 0.6
                },
                {
                    'type': 'general',
                    'suggestion': 'Group similar categories together',
                    'confidence': 0.7
                }
            ]
        }
    
    def _calculate_confidence(self, recommendations: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not recommendations:
            return 0.0
        
        confidences = [
            r.get('confidence', 0.5)
            for r in recommendations
            if isinstance(r, dict)
        ]
        
        return sum(confidences) / len(confidences) if confidences else 0.5

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    app = create_app()
    
    # Run with async support
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    app.run(debug=True, port=5001)