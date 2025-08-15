---
type: technical-specification
category: system
title: Vending Machine Metrics Calculation System
status: active
last_updated: 2025-08-12
tags: [metrics, inventory, calculations, database, api]
cross_references:
  - /documentation/03-architecture/system/DATABASE_SCHEMA.md
  - /documentation/07-cvd-framework/analytics/OVERVIEW.md
  - /documentation/05-development/api/endpoints/README.md
---

# Vending Machine Metrics Calculation System - Technical Specification

## Overview

This document defines the complete implementation of real-time metrics calculation for vending machine inventory management, including Sold Out Count (SO), Days Remaining Inventory (DRI), Product Level (PL), and Units to Par (UTP).

## Database Schema

### New Table: slot_metrics

```sql
CREATE TABLE slot_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planogram_slot_id INTEGER NOT NULL,
    planogram_id INTEGER NOT NULL,
    device_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,

    -- Calculated metrics
    is_sold_out INTEGER DEFAULT 0,          -- 0 or 1
    days_remaining_inventory INTEGER,       -- Whole days
    product_level_percent INTEGER,          -- 0-100
    units_to_par INTEGER,                   -- Units needed

    -- Sales velocity data
    sales_28_day INTEGER DEFAULT 0,         -- Units sold in last 28 days
    sales_all_time INTEGER DEFAULT 0,       -- Total units sold ever
    days_with_sales INTEGER DEFAULT 0,      -- Days with recorded sales
    daily_velocity REAL DEFAULT 0.0,        -- Calculated daily rate

    -- Metadata
    last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    calculation_version INTEGER DEFAULT 1,

    FOREIGN KEY (planogram_slot_id) REFERENCES planogram_slots(id),
    FOREIGN KEY (planogram_id) REFERENCES planograms(id),
    FOREIGN KEY (device_id) REFERENCES devices(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE INDEX idx_slot_metrics_device ON slot_metrics(device_id);
CREATE INDEX idx_slot_metrics_planogram ON slot_metrics(planogram_id);
CREATE INDEX idx_slot_metrics_last_calc ON slot_metrics(last_calculated);
```

## Metric Calculations

### 1. Sold Out Count (SO)

**Definition**: Binary indicator if a slot is completely empty

**Slot Level Calculation:**
```sql
is_sold_out = CASE WHEN quantity = 0 THEN 1 ELSE 0 END
```

**Cabinet Level Aggregation:**
```
cabinet_so = sum(all slot.is_sold_out where slot.planogram_id = cabinet.planogram_id)
```

**Device Level Aggregation:**
```
device_so = sum(all cabinet_so for device)
```

### 2. Days Remaining Inventory (DRI)

**Definition**: Estimated days until slot depletes based on sales velocity

**Slot Level Calculation:**
```sql
-- Step 1: Calculate 28-day sales for this product at this device
sales_28_day = SELECT SUM(sale_units)
                FROM sales
                WHERE device_id = ?
                AND product_id = ?
                AND created_at >= date('now', '-28 days')

-- Step 2: Calculate daily velocity
if sales_28_day > 0:
    daily_velocity = sales_28_day / 28.0
else:
    -- Fallback to historical average
    total_sales = SELECT SUM(sale_units)
                  FROM sales
                  WHERE device_id = ? AND product_id = ?

    days_active = SELECT julianday('now') - julianday(MIN(created_at))
                  FROM sales
                  WHERE device_id = ? AND product_id = ?

    if days_active > 0 and total_sales > 0:
        daily_velocity = total_sales / days_active
    else:
        daily_velocity = 0.1  -- Default minimum velocity

-- Step 3: Calculate DRI
current_quantity = SELECT quantity FROM planogram_slots WHERE id = ?

if daily_velocity > 0:
    dri = int(current_quantity / daily_velocity)
else:
    dri = 999  -- Infinity

-- Cap at reasonable maximum
dri = min(dri, 999)
```

**Cabinet Level Aggregation:**
```javascript
// Take minimum DRI (worst case) across all slots
cabinet_dri = Math.min(...all_slot_dri_values)
```

**Device Level Aggregation:**
```javascript
// Take minimum DRI across all cabinets
device_dri = Math.min(...all_cabinet_dri_values)
```

### 3. Product Level Percent (PL)

**Definition**: Percentage of capacity currently filled

**Slot Level Calculation:**
```sql
product_level_percent = ROUND((quantity * 100.0) / NULLIF(capacity, 0))
```

**Cabinet Level Aggregation:**
```javascript
total_quantity = sum(all slot.quantity)
total_capacity = sum(all slot.capacity)
cabinet_pl = Math.round((total_quantity / total_capacity) * 100)
```

**Device Level Aggregation:**
```javascript
total_quantity = sum(all cabinet quantities)
total_capacity = sum(all cabinet capacities)
device_pl = Math.round((total_quantity / total_capacity) * 100)
```

### 4. Units to Par (UTP)

**Definition**: Number of units needed to reach full capacity

**Slot Level Calculation:**
```sql
units_to_par = capacity - quantity
```

**Cabinet Level Aggregation:**
```javascript
cabinet_utp = sum(all slot.units_to_par)
```

**Device Level Aggregation:**
```javascript
device_utp = sum(all cabinet_utp)
```

## Backend Implementation

### Calculation Service

```python
# app.py additions

@app.route('/api/metrics/calculate', methods=['POST'])
def calculate_all_metrics():
    """Manually trigger metrics calculation for all devices"""
    db = get_db()
    cursor = db.cursor()

    try:
        # Get all active planogram slots
        slots = cursor.execute('''
            SELECT 
                ps.id as slot_id,
                ps.planogram_id,
                ps.product_id,
                ps.quantity,
                ps.capacity,
                p.device_id,
                p.cabinet_configuration_id
            FROM planogram_slots ps
            JOIN planograms p ON ps.planogram_id = p.id
            JOIN devices d ON p.device_id = d.id
            WHERE d.deleted_at IS NULL
        ''').fetchall()

        processed = 0
        for slot in slots:
            calculate_slot_metrics(
                slot['slot_id'],
                slot['planogram_id'],
                slot['device_id'],
                slot['product_id'],
                slot['quantity'],
                slot['capacity']
            )
            processed += 1

        db.commit()
        return jsonify({
            'success': True,
            'processed': processed,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

def calculate_slot_metrics(slot_id, planogram_id, device_id, product_id, quantity, capacity):
    """Calculate metrics for a single slot"""
    db = get_db()
    cursor = db.cursor()

    # Calculate SO
    is_sold_out = 1 if quantity == 0 else 0

    # Calculate PL
    product_level_percent = round((quantity * 100.0) / capacity) if capacity > 0 else 0

    # Calculate UTP
    units_to_par = capacity - quantity

    # Calculate DRI
    # Get 28-day sales
    sales_28 = cursor.execute('''
        SELECT COALESCE(SUM(sale_units), 0) as total
        FROM sales
        WHERE device_id = ? 
        AND product_id = ?
        AND datetime(created_at) >= datetime('now', '-28 days')
    ''', (device_id, product_id)).fetchone()['total']

    if sales_28 > 0:
        daily_velocity = sales_28 / 28.0
    else:
        # Get historical average
        historical = cursor.execute('''
            SELECT 
                COALESCE(SUM(sale_units), 0) as total_sales,
                julianday('now') - julianday(MIN(created_at)) as days_active
            FROM sales
            WHERE device_id = ? AND product_id = ?
        ''', (device_id, product_id)).fetchone()

        if historical['total_sales'] > 0 and historical['days_active'] > 0:
            daily_velocity = historical['total_sales'] / historical['days_active']
        else:
            daily_velocity = 0.1  # Default minimum

    # Calculate DRI
    if daily_velocity > 0:
        dri = int(quantity / daily_velocity)
    else:
        dri = 999

    dri = min(dri, 999)  # Cap at 999

    # Upsert metrics
    cursor.execute('''
        INSERT OR REPLACE INTO slot_metrics (
            planogram_slot_id, planogram_id, device_id, product_id,
            is_sold_out, days_remaining_inventory, product_level_percent, units_to_par,
            sales_28_day, daily_velocity, last_calculated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (
        slot_id, planogram_id, device_id, product_id,
        is_sold_out, dri, product_level_percent, units_to_par,
        sales_28, daily_velocity
    ))
```

### Updated Device API Endpoint

```python
@app.route('/api/routes/<int:route_id>/devices', methods=['GET'])
def get_route_devices(route_id):
    # ... existing code ...

    # After getting devices, attach slot metrics
    for device in devices:
        # Get all slot metrics for this device
        slot_metrics = cursor.execute('''
            SELECT 
                sm.*,
                ps.slot_position,
                p.cabinet_configuration_id
            FROM slot_metrics sm
            JOIN planogram_slots ps ON sm.planogram_slot_id = ps.id
            JOIN planograms p ON sm.planogram_id = p.id
            WHERE sm.device_id = ?
            ORDER BY p.cabinet_configuration_id, ps.slot_position
        ''', (device['id'],)).fetchall()

        # Aggregate metrics by cabinet
        cabinet_metrics = {}
        for slot in slot_metrics:
            cab_id = slot['cabinet_configuration_id']
            if cab_id not in cabinet_metrics:
                cabinet_metrics[cab_id] = {
                    'slots': [],
                    'so_count': 0,
                    'min_dri': 999,
                    'total_quantity': 0,
                    'total_capacity': 0,
                    'total_utp': 0
                }

            cabinet_metrics[cab_id]['slots'].append(dict(slot))
            cabinet_metrics[cab_id]['so_count'] += slot['is_sold_out']
            cabinet_metrics[cab_id]['min_dri'] = min(
                cabinet_metrics[cab_id]['min_dri'],
                slot['days_remaining_inventory']
            )
            # Add quantity/capacity from planogram_slots for PL calculation

        # Attach to device
        device['slot_metrics'] = slot_metrics
        device['cabinet_metrics'] = cabinet_metrics
```

## Frontend Aggregation

```javascript
// In route-planner.html

function aggregateDeviceMetrics(device) {
    if (!device.slot_metrics || device.slot_metrics.length === 0) {
        return {
            soldOutCount: 0,
            daysRemainingInventory: 999,
            productLevelPercent: 100,
            unitsToPar: 0
        };
    }

    let totalSO = 0;
    let minDRI = 999;
    let totalQuantity = 0;
    let totalCapacity = 0;
    let totalUTP = 0;

    device.slot_metrics.forEach(slot => {
        totalSO += slot.is_sold_out;
        minDRI = Math.min(minDRI, slot.days_remaining_inventory);
        totalUTP += slot.units_to_par;
        // Need quantity/capacity from original slot data
    });

    // For PL, need to get quantities from planogram_slots
    const pl = Math.round((totalQuantity / totalCapacity) * 100);

    return {
        soldOutCount: totalSO,
        daysRemainingInventory: minDRI,
        productLevelPercent: pl,
        unitsToPar: totalUTP
    };
}
```

## Database Viewer Integration

```javascript
// Add to database-viewer.html

function addMetricsTab() {
    const tabHtml = `
        <div class="tab-content" id="metrics-content" style="display: none;">
            <h2>Metrics Calculation</h2>
            <div class="metrics-info">
                <p>Calculate inventory metrics for all devices based on 28-day sales history.</p>
                <p>Last calculation: <span id="last-calc-time">Never</span></p>
            </div>
            <button class="btn btn-primary" onclick="calculateMetrics()">
                Calculate All Metrics
            </button>
            <div id="calc-status" style="margin-top: 20px;"></div>
        </div>
    `;
}

async function calculateMetrics() {
    const statusEl = document.getElementById('calc-status');
    const btn = event.target;

    btn.disabled = true;
    btn.textContent = 'Calculating...';
    statusEl.innerHTML = '<p>Processing...</p>';

    try {
        const response = await fetch('/api/metrics/calculate', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            statusEl.innerHTML = `
                <p style="color: green;">
                    ✓ Successfully calculated metrics for ${result.processed} slots
                </p>
            `;
            document.getElementById('last-calc-time').textContent =
                new Date(result.timestamp).toLocaleString();
        } else {
            statusEl.innerHTML = `<p style="color: red;">Error: ${result.error}</p>`;
        }
    } catch (error) {
        statusEl.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    } finally {
        btn.disabled = false;
        btn.textContent = 'Calculate All Metrics';
    }
}
```

## Edge Cases & Handling

1. **New Products**: No sales history → Use minimum velocity (0.1 units/day)
2. **Seasonal Items**: Use 28-day window to adapt to seasonal changes
3. **Empty Slots**: DRI = 0, but don't affect cabinet minimum
4. **Capacity = 0**: Treat as maintenance slot, exclude from calculations
5. **No Planogram**: Skip device in calculations
6. **Deleted Devices**: Exclude from calculations

## Performance Considerations

1. **Batch Processing**: Calculate all slots in one pass
2. **Indexing**: Index on device_id and last_calculated for quick lookups
3. **Caching**: Store results, only recalculate on demand
4. **Incremental Updates**: Future enhancement - only recalculate changed devices

## Testing Checklist

- Calculate metrics with no sales history
- Calculate metrics with partial (< 28 days) history
- Verify DRI calculation with various velocities
- Test aggregation from slot → cabinet → device
- Verify edge cases (empty slots, zero capacity)
- Performance test with 1000+ devices
- Verify manual trigger from database viewer

## API Endpoints Summary

- `POST /api/metrics/calculate` - Trigger full metrics calculation
- `GET /api/routes/<id>/devices` - Get devices with attached metrics
- `GET /api/metrics/weekly` - Weekly metrics summary (future enhancement)
- `GET /api/metrics/top-performers` - Top performing devices (future enhancement)

This system provides comprehensive inventory metrics calculation with proper database design, efficient algorithms, and robust error handling.
