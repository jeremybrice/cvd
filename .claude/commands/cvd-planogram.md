---
name: cvd-planogram
description: Create, optimize, or analyze vending machine planograms using AI-powered recommendations and sales data analysis
---

# CVD Planogram Management Command

You are executing planogram operations for the CVD vending machine fleet.

## Command Variations

### Create New Planogram
When asked to "create planogram for [device/cabinet]":
1. Analyze device type and cabinet configuration
2. Review location demographics
3. Select appropriate product mix
4. Apply merchandising best practices
5. Set initial par levels

### Optimize Existing Planogram
When asked to "optimize planogram for [device]":
1. Analyze last 30 days of sales data
2. Identify underperforming slots
3. Calculate slot efficiency ratios
4. Generate AI recommendations
5. Project revenue impact

### Fill Empty Slots
When asked to "fill empty slots in [device]":
1. Identify all empty positions
2. Analyze adjacent product performance
3. Review category balance
4. Recommend high-velocity products
5. Calculate expected revenue gain

## Implementation Patterns

### Slot Performance Analysis
```python
# Calculate slot metrics
for slot in planogram.slots:
    metrics = {
        'daily_velocity': sales_units / days_active,
        'revenue_per_day': sales_revenue / days_active,
        'stockout_frequency': stockout_count / service_visits,
        'days_until_empty': current_quantity / daily_velocity,
        'efficiency_ratio': actual_revenue / potential_revenue
    }
```

### AI Optimization Request
```python
# Prepare context for AI optimizer
context = {
    'current_planogram': planogram_data,
    'sales_history': last_30_days_sales,
    'location_type': device.location.type,
    'cabinet_zones': ['A-row (eye-level)', 'B-row', 'C-row'],
    'constraints': {
        'temperature': cabinet.temperature_zone,
        'slot_dimensions': cabinet.slot_config
    }
}
recommendations = planogram_optimizer.optimize(context)
```

### Merchandising Rules
1. **Zone Strategy**:
   - A-row: Premium placement, highest margin items
   - B-row: High velocity, popular items
   - C-row: Value items, bulk products

2. **Category Distribution**:
   - No more than 30% single category
   - Complementary products adjacent
   - Avoid flavor cannibalization

3. **Visual Balance**:
   - Alternate package colors
   - Group similar sizes
   - Create visual flow

## Files to Reference
- `/home/jbrice/Projects/365/planogram_optimizer.py`
- `/home/jbrice/Projects/365/pages/NSPT.html`
- `/home/jbrice/Projects/365/api.js` (planogram endpoints)

## Success Metrics
- Revenue increase > 15%
- Zero empty slots
- Stockout rate < 5%
- Category balance maintained