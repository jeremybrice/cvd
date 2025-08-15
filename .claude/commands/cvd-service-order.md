---
name: cvd-service-order
description: Generate or optimize service orders for vending machines, including pick lists, route planning, and cabinet-specific requirements
---

# CVD Service Order Command

You are executing a service order workflow for the CVD vending machine fleet management system.

## Command Variations

### Generate Service Order
When asked to "generate service order for [device/route]":
1. Query device configurations and current inventory levels
2. Calculate required products based on par levels
3. Generate pick list organized by cabinet
4. Create service order with proper priority
5. Assign to appropriate driver based on route

### Optimize Pick List
When asked to "optimize pick list for [order]":
1. Analyze current pick list items
2. Group products by warehouse location
3. Optimize picking sequence
4. Calculate estimated service time
5. Identify potential stockout risks

### Execute Service Visit
When asked to "execute service visit for [order]":
1. Mark order as in-progress
2. Track actual vs planned quantities
3. Handle photo uploads for verification
4. Update inventory levels
5. Complete order and generate next service date

## Implementation Steps

1. **Check Current Orders**
```python
# Query existing service orders
SELECT * FROM service_orders 
WHERE status IN ('pending', 'in_progress')
ORDER BY priority DESC, scheduled_date ASC
```

2. **Calculate Requirements**
```python
# For each cabinet in device
for cabinet in device.cabinets:
    for slot in cabinet.slots:
        current = slot.current_quantity
        par = slot.par_level
        needed = par - current
        if needed > 0:
            add_to_pick_list(slot.product, needed)
```

3. **Generate Pick List**
- Group by product category
- Sort by warehouse location
- Calculate total volume/weight
- Estimate service time

4. **Assign to Driver**
- Check driver availability
- Match route assignments
- Consider vehicle capacity
- Send push notification

## Context Files to Load
- `/home/jbrice/Projects/365/service_order_service.py`
- `/home/jbrice/Projects/365/pages/service-orders.html`
- Database schema for service_orders tables

## Success Metrics
- Pick list accuracy > 95%
- Service time within estimate
- Zero stockouts post-service
- Driver satisfaction score > 4.5