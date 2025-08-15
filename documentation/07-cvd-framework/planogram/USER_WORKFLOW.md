# Planogram User Workflow Guide


## Metadata
- **ID**: 07_CVD_FRAMEWORK_PLANOGRAM_USER_WORKFLOW
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #cvd-specific #data-exchange #data-layer #database #debugging #device-management #dex-parser #domain #integration #logistics #machine-learning #metrics #operations #optimization #performance #planogram #product-placement #quality-assurance #reporting #route-management #service-orders #testing #troubleshooting #vending #vending-machine
- **Intent**: The planogram system enables fleet managers to optimize product placement through an intuitive drag-and-drop interface, backed by AI-powered recommendations and real-time performance analytics
- **Audience**: system administrators, managers, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/07-cvd-framework/planogram/
- **Category**: Planogram
- **Search Keywords**: #planogram, **save, access, analysis, application, assignment, balance, batch, cabinet, capacity, catalog, category, configuration, continuous, current

This guide provides step-by-step instructions for creating and managing planograms in the CVD system, covering both basic configuration and advanced AI optimization workflows.

## Overview

The planogram system enables fleet managers to optimize product placement through an intuitive drag-and-drop interface, backed by AI-powered recommendations and real-time performance analytics.

### Prerequisites
- Administrative or Manager role access
- Device configured with cabinet specifications
- Product catalog populated with available inventory

## Basic Planogram Creation

### Step 1: Access Planogram Interface

1. Navigate to the main CVD dashboard
2. Click **Planogram** in the navigation menu (or use hash route `#planogram`)
3. The system loads the planogram configuration interface (`NSPT.html`)

### Step 2: Select Device and Cabinet

```javascript
// Device Selection Process
1. Choose target device from device dropdown
   - Displays: Asset ID, Location, Device Type
   - Filters: Active devices only

2. Select cabinet for configuration
   - Options: Cabinet 0, Cabinet 1, Cabinet 2 (based on device config)
   - Shows: Cabinet type, dimensions, current fill status
```

### Step 3: Configure Cabinet Layout

1. **Cabinet Type Selection**
   - Choose from configured cabinet types
   - System displays grid dimensions (rows × columns)
   - Preview shows slot layout visualization

2. **Grid Initialization**
   - System generates slot positions (A1, A2, B1, B2, etc.)
   - Empty slots display with placeholder styling
   - Existing products load if planogram exists

### Step 4: Product Assignment

#### Using Drag-and-Drop Interface

1. **Product Catalog Panel**
   ```
   - Organized by categories: Beverages, Snacks, Fresh Food
   - Each product shows: Name, Price, Category, Image
   - Drag handles enabled on all product items
   ```

2. **Slot Assignment Process**
   ```
   1. Click and drag product from catalog
   2. Hover over target slot (highlights in blue)
   3. Drop product onto slot
   4. System validates placement and updates slot
   5. Visual confirmation with product image and name
   ```

3. **Slot Configuration**
   - **Capacity**: Maximum items per slot (default: 20)
   - **Par Level**: Restocking threshold (default: 15)
   - **Current Quantity**: Current inventory level
   - **Price Override**: Slot-specific pricing (optional)

### Step 5: Bulk Configuration

#### Using Category Assignment
1. Select multiple empty slots (Ctrl+Click or Shift+Click)
2. Choose "Assign by Category" from context menu
3. System distributes category products across selected slots
4. Maintains product variety and balance

#### Using Template Application
1. Select "Load Template" from toolbar
2. Choose from saved planogram templates
3. Apply template to current cabinet configuration
4. Customize individual slots as needed

## Advanced AI Optimization Workflow

### Step 1: Performance Analysis

1. **Access AI Optimization Panel**
   - Click "AI Optimize" button in planogram toolbar
   - System loads current performance data
   - Displays optimization options

2. **Sales Data Integration**
   ```
   - Analyzes last 30 days of sales data
   - Calculates product velocity and revenue per slot
   - Identifies empty slots and underperforming positions
   ```

### Step 2: Generate AI Recommendations

1. **Optimization Request**
   ```javascript
   // System sends optimization request
   {
     "device_id": 123,
     "cabinet_index": 0,
     "optimization_type": "full",
     "analysis_period": 30
   }
   ```

2. **AI Analysis Process**
   - Claude AI analyzes sales patterns and current layout
   - Prioritizes empty slots for immediate revenue impact
   - Considers position premiums (eye-level vs. lower slots)
   - Generates confidence-scored recommendations

### Step 3: Review and Apply Recommendations

1. **Recommendation Display**
   ```
   Each recommendation shows:
   - Target slot position (e.g., "A4")
   - Current product (if any)
   - Recommended product
   - Expected revenue improvement
   - Confidence score (0.0-1.0)
   - Reasoning explanation
   ```

2. **Selective Implementation**
   - Review recommendations by confidence score
   - Click "Apply" on individual recommendations
   - System implements changes with visual feedback
   - Option to "Apply All High Confidence" (>0.8)

3. **Batch Application**
   ```javascript
   // Apply multiple recommendations
   - Select recommendations using checkboxes
   - Click "Apply Selected" button
   - System processes changes sequentially
   - Progress indicator shows completion status
   ```

## Advanced Configuration Workflows

### Empty Slot Management

1. **Empty Slot Detection**
   - System highlights empty slots in red
   - Shows total revenue opportunity
   - Prioritizes in AI recommendations

2. **Quick Fill Options**
   - Right-click empty slot → "Quick Fill"
   - Choose from top-performing products
   - System suggests based on position and category balance

### Performance Monitoring

1. **Slot Performance Metrics**
   ```
   Per-slot tracking:
   - Daily units sold
   - Revenue per day
   - Days until stockout
   - Performance vs. cabinet average
   ```

2. **Optimization History**
   - Track changes over time
   - Compare before/after performance
   - Identify successful optimization patterns

### Category Balance Management

1. **Category Distribution Analysis**
   - Visual representation of category balance
   - Identifies gaps in product variety
   - Suggests category additions for customer satisfaction

2. **Seasonal Optimization**
   - Adjust product mix for seasonal preferences
   - Track seasonal performance patterns
   - Schedule automatic optimization reviews

## Error Handling and Troubleshooting

### Common Issues and Solutions

1. **Drag-and-Drop Failures**
   ```
   Issue: Product won't drop onto slot
   Solutions:
   - Verify slot isn't locked or restricted
   - Check product compatibility rules
   - Refresh browser and retry
   - Use right-click context menu as alternative
   ```

2. **AI Optimization Unavailable**
   ```
   Issue: "AI optimization unavailable" message
   Cause: ANTHROPIC_API_KEY not configured
   Solution: Contact system administrator for API key setup
   Fallback: Use manual optimization based on sales reports
   ```

3. **Save Failures**
   ```
   Issue: Changes not saving to database
   Solutions:
   - Check network connectivity
   - Verify user permissions (Manager/Admin required)
   - Look for validation errors in slot configuration
   - Try saving individual slots instead of bulk update
   ```

### Validation Rules

1. **Slot Configuration Validation**
   - Par level cannot exceed capacity
   - Current quantity cannot exceed capacity
   - Price must be positive value
   - Product must exist in catalog

2. **Grid Layout Validation**
   - All slots must have valid position coordinates
   - No duplicate position assignments
   - Cabinet dimensions must match device configuration

## Best Practices

### Optimization Strategy

1. **Start with Empty Slots**
   - Fill empty slots before optimizing existing assignments
   - Empty slots represent immediate revenue opportunity
   - Use AI recommendations for optimal product selection

2. **Premium Position Management**
   - Place high-velocity products in Row A (eye level)
   - Reserve premium spots for highest-margin items
   - Consider visual appeal and brand recognition

3. **Category Balance**
   - Maintain diverse product mix for customer satisfaction
   - Ensure popular categories have multiple options
   - Balance price points across visible positions

### Maintenance Workflow

1. **Regular Review Schedule**
   - Weekly performance analysis
   - Monthly optimization review
   - Seasonal planogram updates

2. **Performance Tracking**
   - Monitor slot performance metrics
   - Track AI recommendation success rates
   - Document successful optimization patterns

3. **Continuous Improvement**
   - Test new product placements
   - A/B test different configurations
   - Share successful patterns across fleet

## Integration with Service Orders

### Automatic Restocking Integration

1. **Par Level Monitoring**
   - System tracks inventory levels per slot
   - Generates restocking alerts when below par level
   - Creates service orders for efficient restocking

2. **Pick List Generation**
   - Service orders include planogram-based pick lists
   - Optimized for efficient restocking workflow
   - Accounts for capacity and par level requirements

### Inventory Planning

1. **Capacity Planning**
   - Plan inventory purchases based on slot capacities
   - Optimize service visit frequency
   - Minimize stockout risk while controlling inventory costs

The planogram user workflow transforms complex product placement decisions into an intuitive, data-driven process that maximizes both operational efficiency and revenue performance across the entire vending machine fleet.