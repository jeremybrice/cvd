"""
Real-time Planogram Assistant API Integration
Flask endpoints for real-time AI assistance
"""

from flask import jsonify, request
from functools import wraps
import asyncio
import json
from typing import Dict, Optional
from ai_services.realtime_pipeline import RealtimePlanogramPipeline, StreamingAssistant
import anthropic

def setup_realtime_routes(app, db_path='cvd.db'):
    """Setup real-time AI assistant routes"""
    
    pipeline = RealtimePlanogramPipeline(db_path)
    
    @app.route('/api/planograms/realtime-analysis', methods=['POST'])
    def analyze_placement():
        """Analyze product placement in real-time"""
        try:
            data = request.json
            device_id = data.get('device_id')
            cabinet_index = data.get('cabinet_index', 0)
            user_action = data.get('action')
            target_product = data.get('product')
            target_slot = data.get('slot')
            
            # Structure data for LLM
            context = pipeline.structure_for_llm(
                device_id, 
                cabinet_index,
                user_action,
                target_product
            )
            
            # Add specific placement context
            context['placement'] = {
                'slot': target_slot,
                'product': target_product
            }
            
            # Get AI analysis (use cached model for speed)
            analysis = get_placement_analysis(context)
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'context': context
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/planograms/validate-constraints', methods=['POST'])
    def validate_constraints():
        """Validate planogram changes against business rules"""
        try:
            data = request.json
            device_id = data.get('device_id')
            cabinet_index = data.get('cabinet_index', 0)
            changes = data.get('changes', [])
            
            # Get current state
            context = pipeline.structure_for_llm(device_id, cabinet_index)
            
            # Validate each change
            validations = []
            for change in changes:
                validation = validate_single_change(context, change)
                validations.append(validation)
            
            return jsonify({
                'success': True,
                'validations': validations,
                'overall_valid': all(v['valid'] for v in validations)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/planograms/pattern-suggestions', methods=['POST'])
    def get_pattern_suggestions():
        """Get suggestions based on successful patterns"""
        try:
            data = request.json
            device_id = data.get('device_id')
            cabinet_index = data.get('cabinet_index', 0)
            
            # Get device context
            context = pipeline.structure_for_llm(device_id, cabinet_index)
            
            # Find similar successful devices
            similar_devices = find_similar_devices(device_id)
            
            # Get pattern-based suggestions
            suggestions = analyze_patterns(context, similar_devices)
            
            return jsonify({
                'success': True,
                'suggestions': suggestions,
                'based_on_devices': len(similar_devices)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/planograms/stream-analysis', methods=['POST'])
    def stream_analysis():
        """Stream analysis using Server-Sent Events"""
        def generate():
            data = request.json
            context = pipeline.structure_for_llm(
                data.get('device_id'),
                data.get('cabinet_index', 0)
            )
            
            # Stream analysis results
            for chunk in stream_ai_analysis(context):
                yield f"data: {json.dumps(chunk)}\n\n"
        
        return app.response_class(
            generate(),
            mimetype='text/event-stream'
        )

def get_placement_analysis(context: Dict) -> Dict:
    """Get AI analysis for product placement"""
    import os
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        return {
            'score': 75,
            'reasoning': 'AI service unavailable - using default rules',
            'suggestions': []
        }
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Build focused prompt
    prompt = f"""Analyze this product placement:
Device: {context['device_context']['name']}
Cabinet: {context['cabinet_context']['type']} {context['cabinet_context']['layout']}
Product: {context['placement']['product']['name']}
Slot: {context['placement']['slot']}
Current Performance: ${context['performance_summary']['daily_revenue']}/day

Score the placement (0-100) and provide brief reasoning.
Consider: visibility, accessibility, category grouping, sales velocity.

Return JSON: {{"score": int, "reasoning": str, "improvement": str}}"""
    
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",  # Fast model
            max_tokens=200,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = json.loads(message.content[0].text)
        return result
    except:
        return {
            'score': 75,
            'reasoning': 'Analysis unavailable',
            'improvement': 'Check AI configuration'
        }

def validate_single_change(context: Dict, change: Dict) -> Dict:
    """Validate a single planogram change"""
    
    # Business rules validation
    validations = []
    
    # Rule 1: Premium slots for high-velocity items
    if change['slot'][0] in ['A', 'B', 'C']:  # Eye-level rows
        if change.get('product', {}).get('velocity', 0) < 5:
            validations.append({
                'rule': 'Premium slot placement',
                'valid': False,
                'message': 'Low-velocity item in premium slot'
            })
    
    # Rule 2: Temperature zone compatibility
    if context['cabinet_context']['temperature'] == 'Cold (35-45°F)':
        if change.get('product', {}).get('requires_ambient', False):
            validations.append({
                'rule': 'Temperature compatibility',
                'valid': False,
                'message': 'Product requires ambient temperature'
            })
    
    # Rule 3: Weight limits for upper shelves
    if change['slot'][0] in ['A', 'B']:
        if change.get('product', {}).get('weight', 0) > 2:  # 2 lbs limit
            validations.append({
                'rule': 'Weight distribution',
                'valid': False,
                'message': 'Product too heavy for upper shelf'
            })
    
    return {
        'change': change,
        'valid': len(validations) == 0 or all(v['valid'] for v in validations),
        'validations': validations
    }

def find_similar_devices(device_id: int, limit: int = 5) -> list:
    """Find similar devices based on location type and performance"""
    import sqlite3
    
    conn = sqlite3.connect('cvd.db')
    cursor = conn.cursor()
    
    # Get device characteristics
    query = """
    SELECT location_id, device_type_id
    FROM devices
    WHERE id = ?
    """
    cursor.execute(query, (device_id,))
    device_info = cursor.fetchone()
    
    if not device_info:
        conn.close()
        return []
    
    # Find similar devices
    similar_query = """
    SELECT d.id, d.cooler, AVG(s.sale_cash) as avg_sales
    FROM devices d
    LEFT JOIN sales s ON d.id = s.device_id
    WHERE d.location_id = ? 
    AND d.device_type_id = ?
    AND d.id != ?
    AND d.deleted_at IS NULL
    GROUP BY d.id
    ORDER BY avg_sales DESC
    LIMIT ?
    """
    cursor.execute(similar_query, (
        device_info[0], 
        device_info[1], 
        device_id,
        limit
    ))
    
    similar = cursor.fetchall()
    conn.close()
    
    return [{'id': s[0], 'name': s[1], 'avg_sales': s[2]} for s in similar]

def analyze_patterns(context: Dict, similar_devices: list) -> list:
    """Analyze patterns from similar successful devices"""
    
    suggestions = []
    
    # Get planogram patterns from similar devices
    for device in similar_devices:
        pattern = get_device_pattern(device['id'])
        if pattern:
            suggestions.append({
                'source': device['name'],
                'pattern': pattern,
                'expected_impact': f"+${pattern.get('revenue_lift', 0):.2f}/day"
            })
    
    return suggestions[:3]  # Top 3 suggestions

def get_device_pattern(device_id: int) -> Dict:
    """Extract successful patterns from a device"""
    import sqlite3
    
    conn = sqlite3.connect('cvd.db')
    cursor = conn.cursor()
    
    # Get top performing product positions
    query = """
    SELECT 
        ps.slot_position,
        p.name,
        p.category,
        AVG(s.sale_cash) as avg_revenue
    FROM planogram_slots ps
    JOIN products p ON ps.product_id = p.id
    LEFT JOIN sales s ON s.product_id = p.id AND s.device_id = ?
    WHERE ps.planogram_id IN (
        SELECT id FROM planograms WHERE planogram_key LIKE ? || '%'
    )
    GROUP BY ps.slot_position, ps.product_id
    ORDER BY avg_revenue DESC
    LIMIT 5
    """
    cursor.execute(query, (device_id, str(device_id)))
    
    patterns = cursor.fetchall()
    conn.close()
    
    if patterns:
        return {
            'top_positions': [
                {'slot': p[0], 'product': p[1], 'category': p[2]}
                for p in patterns
            ],
            'revenue_lift': sum(p[3] or 0 for p in patterns) / len(patterns)
        }
    return None

def stream_ai_analysis(context: Dict):
    """Generator for streaming AI analysis"""
    import time
    
    # Simulate streaming response
    stages = [
        {'stage': 'analyzing_layout', 'progress': 25, 'message': 'Analyzing current layout...'},
        {'stage': 'checking_performance', 'progress': 50, 'message': 'Checking sales performance...'},
        {'stage': 'finding_patterns', 'progress': 75, 'message': 'Finding optimization patterns...'},
        {'stage': 'generating_suggestions', 'progress': 100, 'message': 'Generating suggestions...'}
    ]
    
    for stage in stages:
        time.sleep(0.5)  # Simulate processing
        yield stage