---
name: cvd-route-optimize
description: Optimize driver routes for efficient service order completion, including stop sequencing, time windows, and vehicle capacity constraints
---

# CVD Route Optimization Command

Optimize vending machine service routes for maximum efficiency.

## Command Variations

### Optimize Daily Routes
When asked to "optimize routes for [date]":
1. Load all service orders for date
2. Cluster devices by geographic proximity
3. Assign to available drivers
4. Sequence stops optimally
5. Calculate time and distance

### Rebalance Driver Workload
When asked to "rebalance driver workload":
1. Analyze current assignments
2. Calculate service time per driver
3. Redistribute for equality
4. Maintain route coherence
5. Minimize total distance

### Emergency Rerouting
When asked to "reroute for [emergency/breakdown]":
1. Identify affected orders
2. Find available drivers nearby
3. Recalculate optimal paths
4. Update driver apps
5. Send notifications

## Optimization Algorithm

### TSP with Constraints
```python
def optimize_route(orders, constraints):
    # Time window constraints
    time_windows = [(order.earliest, order.latest) for order in orders]
    
    # Vehicle capacity
    vehicle_capacity = constraints['vehicle_capacity']
    
    # Service time per stop
    service_times = [estimate_service_time(order) for order in orders]
    
    # Distance matrix
    distances = calculate_distance_matrix(orders)
    
    # Apply optimization
    route = traveling_salesman_with_windows(
        distances, time_windows, service_times, vehicle_capacity
    )
    return route
```

### Clustering Strategy
```python
# Geographic clustering
clusters = {
    'downtown': {'lat': 40.7128, 'lon': -74.0060, 'radius': 5},
    'suburbs_north': {'lat': 40.8500, 'lon': -74.0060, 'radius': 10},
    'suburbs_south': {'lat': 40.6500, 'lon': -74.0060, 'radius': 10}
}

# Assign devices to clusters
for device in devices:
    nearest_cluster = find_nearest_cluster(device.location, clusters)
    device.cluster = nearest_cluster
```

## Integration Points

### Driver PWA Updates
```javascript
// Push optimized route to driver
const route = {
    driver_id: driver.id,
    stops: optimized_stops,
    total_distance: calculated_distance,
    estimated_time: total_time,
    turn_by_turn: navigation_instructions
};

// Send via push notification
await sendPushNotification(driver.device_token, {
    type: 'ROUTE_UPDATE',
    data: route
});
```

### Real-time Tracking
```python
# Update route progress
def update_route_progress(driver_id, current_location):
    route = get_active_route(driver_id)
    next_stop = route.get_next_stop()
    
    # Recalculate if off-route
    if distance_from_route(current_location, route) > threshold:
        new_route = recalculate_route(current_location, remaining_stops)
        notify_driver(driver_id, new_route)
```

## Constraints Management

### Time Windows
- Business hours restrictions
- Customer preferences
- Traffic patterns
- Break requirements

### Vehicle Constraints
- Capacity limits (weight/volume)
- Refrigeration requirements
- Equipment needs
- Fuel/battery range

### Driver Constraints
- Shift duration
- Overtime limits
- Skill requirements
- Territory familiarity

## Files to Reference
- `/home/jbrice/Projects/365/pages/route-schedule.html`
- `/home/jbrice/Projects/365/pages/driver-app/`
- Database tables: routes, service_orders, locations

## Success Metrics
- Route efficiency > 85%
- On-time delivery > 95%
- Miles per stop < 3.5
- Driver utilization > 80%