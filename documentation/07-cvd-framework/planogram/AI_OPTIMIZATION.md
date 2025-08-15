# Planogram AI Optimization


## Metadata
- **ID**: 07_CVD_FRAMEWORK_PLANOGRAM_AI_OPTIMIZATION
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #cvd-specific #data-exchange #data-layer #database #debugging #device-management #dex-parser #domain #integration #logistics #machine-learning #metrics #optimization #performance #planogram #product-placement #reporting #route-management #troubleshooting #vending #vending-machine
- **Intent**: Documentation for Planogram AI Optimization
- **Audience**: managers, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/07-cvd-framework/planogram/
- **Category**: Planogram
- **Search Keywords**: ###, ####, analysis, balance, cabinet, calculation, category, confidence, data, detection, device, dex, empty, optimization, performance

The CVD planogram system integrates advanced AI optimization capabilities through the `planogram_optimizer.py` service, providing data-driven product placement recommendations that maximize revenue and operational efficiency.

## System Overview

### AI Integration Architecture
The planogram optimizer leverages Claude API for intelligent analysis of sales data, current planogram configurations, and performance metrics to generate actionable placement recommendations.

```python
# Core Architecture
planogram_optimizer.py (AI Service)
    ↓
Anthropic Claude API (Analysis Engine)
    ↓
Sales Data + Current Planogram → Optimization Recommendations
    ↓
Frontend Implementation (NSPT.html)
```

### Key Capabilities
- **Empty Slot Prioritization**: Identifies and fills revenue-generating opportunities
- **Performance Analysis**: Evaluates current slot performance against sales data
- **Product Velocity Optimization**: Places high-performing products in premium positions
- **Category Balance**: Ensures diverse product mix for customer satisfaction
- **Revenue Projection**: Estimates impact of recommended changes

## Technical Implementation

### PlanogramOptimizer Class Structure

```python
class PlanogramOptimizer:
    """Standalone planogram optimization using sales data and AI recommendations."""
    
    def __init__(self, api_key: str, db_path: str = 'cvd.db'):
        """Initialize with Anthropic API key and database path."""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.db_path = db_path
```

#### Core Methods

**Sales Data Analysis**
```python
def get_sales_data(self, device_id: int, days: int = 30) -> List[Dict]:
    """Fetch sales data for a device over specified time period."""
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
    WHERE s.device_id = ? AND s.created_at > datetime('now', '-' || ? || ' days')
    GROUP BY s.product_id
    """
```

**Planogram Configuration Retrieval**
```python
def get_current_planogram(self, device_id: int, cabinet_index: int = 0) -> Dict:
    """Fetch current planogram configuration with empty slot detection."""
    # Generates all possible slot positions for cabinet
    all_positions = self._generate_all_slot_positions(rows, columns)
    
    # Identifies empty slots (product_id = 1 or missing)
    empty_positions = set(all_positions) - filled_positions
    
    # Adds empty slot records for optimization analysis
    for position in empty_positions:
        slots.append({
            'slot_position': position,
            'product_id': 1,  # EMPTY_SLOT_ID
            'product_name': 'Empty',
            'is_empty': True
        })
```

### Performance Metrics Calculation

```python
def calculate_performance_metrics(self, sales_data: List[Dict], 
                                planogram_data: Dict) -> Dict:
    """Calculate comprehensive performance metrics for optimization."""
    metrics = {
        'slot_performance': {},      # Revenue per slot position
        'product_velocity': {},      # Daily sales velocity
        'revenue_by_position': {},   # Position-based performance
        'stockout_risk': {},         # Inventory risk assessment
        'empty_slots': [],           # Revenue opportunity slots
        'top_performers': [],        # High-performing products
        'category_gaps': []          # Missing product categories
    }
```

#### Velocity Calculation
```python
# Calculate daily sales velocity for each product
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
```

#### Empty Slot Detection
```python
# Identify empty slots for prioritized optimization
for slot in planogram_data['slots']:
    position = slot['slot_position']
    product_id = slot.get('product_id')
    
    if not product_id or product_id == 1 or slot.get('is_empty'):
        metrics['empty_slots'].append({
            'position': position,
            'row': position[0],       # A, B, C, D
            'column': int(position[1:])  # 1, 2, 3, 4
        })
```

## AI Prompt Engineering

### Optimization Prompt Structure

```python
def build_optimization_prompt(self, performance_metrics: Dict, 
                            cabinet_config: Dict, sales_data: List[Dict]) -> str:
    """Build comprehensive prompt for Claude with all context."""
    
    prompt = f"""You are analyzing a vending machine planogram for optimization.

Cabinet Configuration:
- Type: {cabinet_config['cabinet_type']}
- Size: {cabinet_config['rows']}x{cabinet_config['columns']} 
- Model: {cabinet_config['model_name']}

CRITICAL: This planogram has {len(empty_slots)} EMPTY SLOTS that need products:
Empty Slots: {', '.join([slot['position'] for slot in empty_slots])}

Current Performance Metrics:
{json.dumps(performance_metrics, indent=2)}

IMPORTANT INSTRUCTIONS:
1. FIRST PRIORITY: You MUST suggest products for ALL empty slots
2. Empty slots generate $0 revenue - filling them is highest impact
3. Row A slots are premium eye-level positions - assign high-velocity products
4. After filling empty slots, suggest replacements for underperforming products
"""
```

### Response Format Specification

```python
# Expected AI Response Structure
{
    "slot": "A4",
    "current_product": null,  # Empty slot
    "current_performance": "$0/day",
    "recommendation": {
        "product": "Coca-Cola",
        "reason": "High velocity product for premium eye-level position",
        "expected_improvement": "+$5.50/day"
    },
    "confidence": 0.95
}
```

## AI Response Processing

### Response Parsing and Validation

```python
def parse_ai_response(self, ai_response: str) -> List[Dict]:
    """Parse and validate Claude's response."""
    try:
        # Extract JSON from AI response
        json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
        if json_match:
            recommendations = json.loads(json_match.group())
            
            # Validate required fields
            validated = []
            for rec in recommendations:
                if 'slot' in rec and 'recommendation' in rec:
                    # Ensure complete recommendation structure
                    if isinstance(rec['recommendation'], dict):
                        if 'product' in rec['recommendation']:
                            validated.append(rec)
            
            # Sort: empty slots first, then by confidence
            validated.sort(key=lambda x: (
                0 if x['current_product'] is None else 1,
                -x['confidence']
            ))
            
            return validated
```

### Claude API Integration

```python
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
```

## Frontend Integration

### AI Optimization Panel

The planogram interface (`NSPT.html`) integrates AI optimization through dedicated UI components:

```javascript
// AI Optimization Integration
class AIOptimizationPanel {
    constructor(planogramManager) {
        this.planogramManager = planogramManager;
        this.recommendations = [];
    }
    
    async runOptimization(deviceId, cabinetIndex) {
        try {
            this.showLoadingState();
            
            const response = await fetch('/api/planogram/optimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    device_id: deviceId,
                    cabinet_index: cabinetIndex,
                    optimization_type: 'full'
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.recommendations = result.recommendations;
                this.displayRecommendations();
            } else {
                this.showError(result.error);
            }
            
        } catch (error) {
            this.showError('Failed to run AI optimization');
        }
    }
    
    displayRecommendations() {
        const panel = document.getElementById('ai-recommendations');
        panel.innerHTML = '';
        
        this.recommendations.forEach(rec => {
            const card = this.createRecommendationCard(rec);
            panel.appendChild(card);
        });
    }
}
```

### Recommendation Implementation

```javascript
// Apply AI Recommendation
async applyRecommendation(recommendation) {
    const { slot, recommendation: rec } = recommendation;
    
    try {
        // Find product in catalog
        const product = this.findProductByName(rec.product);
        if (!product) {
            throw new Error(`Product "${rec.product}" not found in catalog`);
        }
        
        // Update slot configuration
        await this.planogramManager.updateSlot(slot, {
            productId: product.id,
            productName: product.name,
            price: product.price
        });
        
        // Visual feedback
        this.highlightSlotUpdate(slot);
        this.showSuccessMessage(`Applied: ${rec.product} → ${slot}`);
        
    } catch (error) {
        this.showError(`Failed to apply recommendation: ${error.message}`);
    }
}
```

## Optimization Strategies

### Empty Slot Prioritization

The AI system prioritizes empty slots as the highest revenue opportunity:

```python
# Empty slots generate $0 revenue - highest impact optimization
empty_slots = performance_metrics.get('empty_slots', [])

prompt += f"""
CRITICAL: This planogram has {len(empty_slots)} EMPTY SLOTS that need products:
Empty Slots: {', '.join([slot['position'] for slot in empty_slots])}

FIRST PRIORITY: You MUST suggest products for ALL {len(empty_slots)} empty slots
"""
```

### Position-Based Optimization

Premium positions (Row A - eye level) receive high-velocity product assignments:

```python
# Row A slots are premium positions
if slot_position.startswith('A'):
    priority = 'high_velocity'
    reasoning = 'Premium eye-level position for maximum visibility'
```

### Performance-Based Replacement

Underperforming slots receive replacement recommendations:

```python
# Identify underperforming slots
for position, performance in slot_performance.items():
    if performance['daily_revenue'] < threshold:
        underperforming_slots.append({
            'position': position,
            'current_revenue': performance['daily_revenue'],
            'improvement_opportunity': True
        })
```

## API Endpoints

### Optimization Service Endpoint

```python
@app.route('/api/planogram/optimize', methods=['POST'])
def optimize_planogram():
    """Generate AI optimization recommendations."""
    data = request.json
    device_id = data.get('device_id')
    cabinet_index = data.get('cabinet_index', 0)
    
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return {'error': 'AI optimization unavailable - API key not configured'}, 400
    
    try:
        optimizer = PlanogramOptimizer(api_key)
        result = optimizer.generate_recommendations(device_id, cabinet_index)
        return result
        
    except Exception as e:
        return {'error': str(e)}, 500
```

## Error Handling and Fallbacks

### Graceful Degradation

```python
# Fallback for API unavailability
if not api_key:
    return {
        'success': False,
        'error': 'AI optimization requires ANTHROPIC_API_KEY environment variable'
    }

# Rule-based fallback for empty slots
if ai_optimization_fails:
    return basic_empty_slot_recommendations(performance_metrics)
```

### Confidence Thresholds

```python
# Only return high-confidence recommendations
if recommendation['confidence'] < 0.7:
    logger.warning(f"Low confidence recommendation ignored: {recommendation}")
    continue
```

The AI optimization system transforms planogram management from manual configuration to intelligent, data-driven optimization that continuously improves revenue performance across the entire vending machine fleet.