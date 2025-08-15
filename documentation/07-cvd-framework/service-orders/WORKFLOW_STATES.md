# Service Order Workflow States


## Metadata
- **ID**: 07_CVD_FRAMEWORK_SERVICE_ORDERS_WORKFLOW_STATES
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #cvd-specific #data-layer #database #debugging #device-management #domain #driver-app #integration #logistics #machine-learning #metrics #mobile #operations #optimization #performance #planogram #product-placement #pwa #reporting #route-management #service-orders #troubleshooting #vending #vending-machine
- **Intent**: The CVD Service Orders system implements a comprehensive state management system that tracks the lifecycle of service orders from creation to completion
- **Audience**: system administrators, managers, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/07-cvd-framework/service-orders/
- **Category**: Service Orders
- **Search Keywords**: cabinet, characteristics, conditions, definition, driver, entry, granularity, order, pick list, planogram, purpose, route, scope, service, service order

## State Management Overview

The CVD Service Orders system implements a comprehensive state management system that tracks the lifecycle of service orders from creation to completion. The multi-tiered state system provides granular visibility into service progress while maintaining operational efficiency and data integrity.

## State Hierarchy Architecture

### Three-Tier State System

#### Tier 1: Service Order Level
- **Scope**: Overall service order status
- **Granularity**: Aggregate status across all assigned cabinets
- **Purpose**: High-level tracking and route management

#### Tier 2: Cabinet Level  
- **Scope**: Individual cabinet service status
- **Granularity**: Per-cabinet progress tracking
- **Purpose**: Operational execution and driver workflow

#### Tier 3: Item Level
- **Scope**: Individual product delivery status
- **Granularity**: Per-product fulfillment tracking
- **Purpose**: Inventory management and completion verification

## Service Order States

### Primary States

#### 1. PENDING
```sql
-- Database representation
status = 'pending'
created_at = CURRENT_TIMESTAMP
completed_at = NULL
```

**Definition**: Service order has been created and assigned but no cabinet service has begun

**Characteristics**:
- All assigned cabinets are in 'pending' state
- Driver has not yet started any service activity
- Pick list is finalized and available
- Route assignment is confirmed

**Entry Conditions**:
- Service order successfully created via `ServiceOrderService.create_service_order()`
- Route and driver assignment completed
- Pick list calculated and validated

**Valid Transitions**:
- `PENDING → IN_PROGRESS`: First cabinet service begins
- `PENDING → CANCELLED`: Order cancelled before service begins

#### 2. IN_PROGRESS
```sql
-- Database representation  
status = 'in_progress'
created_at = [original timestamp]
completed_at = NULL
```

**Definition**: At least one assigned cabinet has been serviced, but order is not yet complete

**Characteristics**:
- One or more cabinets have 'completed' status
- One or more cabinets remain in 'pending' state
- Driver is actively working on the service order
- Partial pick list fulfillment has occurred

**Entry Conditions**:
- Transition from `PENDING` when first cabinet service is completed
- Service visit created for at least one cabinet

**Valid Transitions**:
- `IN_PROGRESS → COMPLETED`: All cabinets serviced and documented
- `IN_PROGRESS → CANCELLED`: Order cancelled during partial completion

#### 3. COMPLETED
```sql
-- Database representation
status = 'completed'
created_at = [original timestamp]  
completed_at = CURRENT_TIMESTAMP
```

**Definition**: All assigned cabinets have been successfully serviced and documented

**Characteristics**:
- All cabinets have 'completed' status
- Service visits created for all cabinets
- Photo documentation completed (if required)
- Planogram quantities updated
- Pick list fully fulfilled

**Entry Conditions**:
- All cabinet service tasks completed via `execute_service_order_cabinet()`
- Service visits documented with required photos
- Inventory updates applied successfully

**Valid Transitions**:
- **Terminal State**: No further transitions allowed

#### 4. CANCELLED
```sql
-- Database representation
status = 'cancelled'
created_at = [original timestamp]
completed_at = CURRENT_TIMESTAMP
```

**Definition**: Service order has been cancelled and will not be completed

**Characteristics**:
- Service order terminated before full completion
- Any completed cabinet services remain documented
- Partial inventory updates preserved
- Cancellation reason and timestamp recorded

**Entry Conditions**:
- Manual cancellation by authorized user
- System cancellation due to business rule violation
- Route cancellation or driver reassignment

**Valid Transitions**:
- **Terminal State**: No further transitions allowed

## Cabinet Service States

### Cabinet-Level State Management

#### 1. PENDING
```sql
-- Database representation in service_order_cabinets
status = 'pending'
estimated_minutes = 10  -- Default cabinet service time
```

**Definition**: Cabinet assigned to service order but not yet serviced

**Characteristics**:
- Cabinet included in service order cabinet selection
- Product requirements calculated and included in pick list
- Driver has not yet begun service for this cabinet
- Service visit record does not exist

**Entry Conditions**:
- Cabinet selected during service order creation
- Cabinet configuration validation completed
- Product requirements successfully calculated

**Valid Transitions**:
- `PENDING → IN_PROGRESS`: Driver begins cabinet service
- `PENDING → COMPLETED`: Cabinet service completed (direct transition for quick services)

#### 2. IN_PROGRESS  
```sql
-- Database representation
status = 'in_progress'
estimated_minutes = 10
```

**Definition**: Driver has begun servicing this cabinet but has not yet completed

**Characteristics**:
- Service visit record created but not finalized
- Driver mobile app shows cabinet as active
- Photo capture may be in progress
- Product delivery partially completed

**Entry Conditions**:
- Driver initiates cabinet service in mobile app
- Service visit record creation begins

**Valid Transitions**:
- `IN_PROGRESS → COMPLETED`: Service visit finalized with documentation
- `IN_PROGRESS → PENDING`: Service reverted (rare, for error recovery)

#### 3. COMPLETED
```sql
-- Database representation
status = 'completed'
estimated_minutes = [actual service time]
```

**Definition**: Cabinet has been fully serviced and documented

**Characteristics**:
- Service visit record completed with all required information
- Photo documentation uploaded and validated
- Product deliveries recorded and quantities updated
- Service completion timestamp recorded

**Entry Conditions**:
- `ServiceOrderService.execute_service_order_cabinet()` successfully executed
- All required photos captured and uploaded
- Product delivery quantities validated and recorded

**Valid Transitions**:
- **Terminal State**: No further transitions allowed

## State Transition Implementation

### Automatic State Transitions

#### Service Order State Update Logic
```python
def update_service_order_status(service_order_id):
    """Automatically update service order status based on cabinet completion"""
    
    cursor = get_db().cursor()
    
    # Get cabinet completion statistics
    cursor.execute('''
        SELECT 
            COUNT(*) as total_cabinets,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_cabinets,
            SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_cabinets
        FROM service_order_cabinets 
        WHERE service_order_id = ?
    ''', (service_order_id,))
    
    stats = cursor.fetchone()
    
    # Determine new service order status
    if stats['completed_cabinets'] == stats['total_cabinets']:
        # All cabinets completed
        new_status = 'completed'
        completed_at = 'CURRENT_TIMESTAMP'
    elif stats['completed_cabinets'] > 0 or stats['in_progress_cabinets'] > 0:
        # Some activity has occurred
        new_status = 'in_progress'
        completed_at = 'NULL'
    else:
        # No activity yet
        new_status = 'pending'
        completed_at = 'NULL'
    
    # Update service order status
    cursor.execute(f'''
        UPDATE service_orders 
        SET status = ?, completed_at = {completed_at}
        WHERE id = ?
    ''', (new_status, service_order_id))
    
    get_db().commit()
    
    return {
        'service_order_id': service_order_id,
        'new_status': new_status,
        'cabinet_stats': dict(stats)
    }
```

#### Cabinet State Transition Triggers
```python
def execute_cabinet_service_transition(cabinet_id, new_status, context=None):
    """Execute cabinet service state transition with validation"""
    
    cursor = get_db().cursor()
    
    # Get current cabinet state
    cursor.execute('''
        SELECT soc.*, so.status as order_status
        FROM service_order_cabinets soc
        JOIN service_orders so ON soc.service_order_id = so.id
        WHERE soc.id = ?
    ''', (cabinet_id,))
    
    cabinet = cursor.fetchone()
    if not cabinet:
        raise ValueError(f"Cabinet {cabinet_id} not found")
    
    # Validate state transition
    valid_transition = validate_cabinet_state_transition(
        current_status=cabinet['status'],
        new_status=new_status,
        order_status=cabinet['order_status']
    )
    
    if not valid_transition['valid']:
        raise ValueError(f"Invalid state transition: {valid_transition['reason']}")
    
    # Execute state transition
    cursor.execute('''
        UPDATE service_order_cabinets 
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (new_status, cabinet_id))
    
    # Log state transition
    log_cabinet_state_transition(cabinet_id, cabinet['status'], new_status, context)
    
    # Trigger service order status update
    update_service_order_status(cabinet['service_order_id'])
    
    get_db().commit()
```

### Manual State Transitions

#### Administrative State Management
```python
@app.route('/api/service-orders/<int:order_id>/status', methods=['PUT'])
@require_auth
@require_role(['admin', 'manager'])
def update_service_order_status_manual(order_id):
    """Manually update service order status with authorization check"""
    
    data = request.get_json()
    new_status = data.get('status')
    reason = data.get('reason', 'Manual status update')
    
    # Validate requested status
    valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status: {new_status}'}), 400
    
    try:
        # Get current service order
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM service_orders WHERE id = ?', (order_id,))
        order = cursor.fetchone()
        
        if not order:
            return jsonify({'error': 'Service order not found'}), 404
        
        # Validate state transition rules
        transition_validation = validate_manual_state_transition(
            current_status=order['status'],
            new_status=new_status,
            user_role=get_current_user_role()
        )
        
        if not transition_validation['allowed']:
            return jsonify({
                'error': 'State transition not allowed',
                'reason': transition_validation['reason']
            }), 403
        
        # Execute manual state change
        cursor.execute('''
            UPDATE service_orders 
            SET status = ?, completed_at = CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE completed_at END
            WHERE id = ?
        ''', (new_status, new_status, order_id))
        
        # Log administrative action
        log_administrative_action(
            action='service_order_status_change',
            entity_id=order_id,
            old_value=order['status'],
            new_value=new_status,
            reason=reason,
            user_id=get_current_user_id()
        )
        
        get_db().commit()
        
        return jsonify({
            'success': True,
            'service_order_id': order_id,
            'old_status': order['status'],
            'new_status': new_status
        })
        
    except Exception as e:
        get_db().rollback()
        return jsonify({'error': str(e)}), 500
```

## State Validation Rules

### Business Rule Enforcement

#### State Transition Validation Matrix
```python
def validate_cabinet_state_transition(current_status, new_status, order_status):
    """Validate cabinet state transitions based on business rules"""
    
    # Define valid transition matrix
    valid_transitions = {
        'pending': ['in_progress', 'completed'],
        'in_progress': ['completed', 'pending'],  # 'pending' for error recovery
        'completed': []  # Terminal state
    }
    
    # Check if transition is allowed
    if new_status not in valid_transitions.get(current_status, []):
        return {
            'valid': False,
            'reason': f'Direct transition from {current_status} to {new_status} not allowed'
        }
    
    # Business rule: Cannot complete cabinet if service order is cancelled
    if new_status == 'completed' and order_status == 'cancelled':
        return {
            'valid': False,
            'reason': 'Cannot complete cabinet service for cancelled order'
        }
    
    # Business rule: Cannot revert to pending after completion without admin privileges
    if current_status == 'completed' and new_status == 'pending':
        if not has_admin_privileges():
            return {
                'valid': False,
                'reason': 'Reverting completed cabinet requires administrator privileges'
            }
    
    return {
        'valid': True,
        'reason': 'Valid state transition'
    }


def validate_service_order_state_consistency():
    """Validate service order state consistency across all orders"""
    
    cursor = get_db().cursor()
    
    # Find service orders with inconsistent states
    cursor.execute('''
        SELECT 
            so.id,
            so.status as order_status,
            COUNT(soc.id) as total_cabinets,
            SUM(CASE WHEN soc.status = 'completed' THEN 1 ELSE 0 END) as completed_cabinets,
            CASE 
                WHEN COUNT(soc.id) = SUM(CASE WHEN soc.status = 'completed' THEN 1 ELSE 0 END) 
                THEN 'completed'
                WHEN SUM(CASE WHEN soc.status = 'completed' THEN 1 ELSE 0 END) > 0 
                THEN 'in_progress'
                ELSE 'pending'
            END as expected_status
        FROM service_orders so
        LEFT JOIN service_order_cabinets soc ON so.id = soc.service_order_id
        WHERE so.status NOT IN ('cancelled')
        GROUP BY so.id, so.status
        HAVING so.status != expected_status
    ''')
    
    inconsistent_orders = cursor.fetchall()
    
    return [dict(order) for order in inconsistent_orders]
```

## State Monitoring and Reporting

### Real-Time State Tracking

#### Service Order Dashboard Queries
```python
def get_service_order_status_summary(date_range=None):
    """Get real-time service order status summary for dashboard"""
    
    cursor = get_db().cursor()
    
    date_filter = ""
    params = []
    
    if date_range:
        date_filter = "WHERE created_at BETWEEN ? AND ?"
        params = [date_range['start'], date_range['end']]
    
    # Get order status distribution
    cursor.execute(f'''
        SELECT 
            status,
            COUNT(*) as count,
            AVG(total_units) as avg_units,
            AVG(estimated_duration_minutes) as avg_duration_minutes
        FROM service_orders 
        {date_filter}
        GROUP BY status
        ORDER BY 
            CASE status
                WHEN 'pending' THEN 1
                WHEN 'in_progress' THEN 2  
                WHEN 'completed' THEN 3
                WHEN 'cancelled' THEN 4
            END
    ''', params)
    
    status_distribution = [dict(row) for row in cursor.fetchall()]
    
    # Get cabinet status distribution
    cursor.execute(f'''
        SELECT 
            soc.status,
            COUNT(*) as count,
            AVG(soc.estimated_minutes) as avg_service_time
        FROM service_order_cabinets soc
        JOIN service_orders so ON soc.service_order_id = so.id
        {date_filter.replace('created_at', 'so.created_at') if date_filter else ''}
        GROUP BY soc.status
    ''', params)
    
    cabinet_distribution = [dict(row) for row in cursor.fetchall()]
    
    return {
        'order_status_distribution': status_distribution,
        'cabinet_status_distribution': cabinet_distribution,
        'total_orders': sum(item['count'] for item in status_distribution),
        'total_cabinets': sum(item['count'] for item in cabinet_distribution)
    }
```

#### State Transition History
```sql
-- State transition audit log
CREATE TABLE service_order_state_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_order_id INTEGER NOT NULL,
    cabinet_id INTEGER,  -- NULL for order-level state changes
    old_status TEXT NOT NULL,
    new_status TEXT NOT NULL,
    transition_reason TEXT,
    user_id INTEGER,
    transition_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_order_id) REFERENCES service_orders(id),
    FOREIGN KEY (cabinet_id) REFERENCES service_order_cabinets(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Performance Metrics by State

#### State Duration Analysis
```python
def analyze_state_durations(time_period='last_30_days'):
    """Analyze how long orders spend in each state"""
    
    cursor = get_db().cursor()
    
    cursor.execute('''
        SELECT 
            so.id,
            so.status,
            so.created_at,
            so.completed_at,
            MIN(sv.created_at) as first_service_start,
            MAX(sv.created_at) as last_service_completion,
            COUNT(DISTINCT soc.id) as total_cabinets,
            COUNT(DISTINCT sv.id) as completed_cabinets
        FROM service_orders so
        LEFT JOIN service_order_cabinets soc ON so.id = soc.service_order_id
        LEFT JOIN service_visits sv ON soc.id = sv.service_order_cabinet_id
        WHERE so.created_at >= date('now', '-30 days')
        GROUP BY so.id
    ''')
    
    orders = cursor.fetchall()
    
    state_durations = {
        'pending_to_in_progress': [],
        'in_progress_to_completed': [],
        'total_completion_time': []
    }
    
    for order in orders:
        # Time spent in pending state
        if order['first_service_start']:
            pending_duration = (
                datetime.fromisoformat(order['first_service_start']) - 
                datetime.fromisoformat(order['created_at'])
            ).total_seconds() / 3600  # Convert to hours
            
            state_durations['pending_to_in_progress'].append(pending_duration)
        
        # Time spent in in_progress state  
        if order['completed_at'] and order['first_service_start']:
            in_progress_duration = (
                datetime.fromisoformat(order['completed_at']) -
                datetime.fromisoformat(order['first_service_start'])
            ).total_seconds() / 3600
            
            state_durations['in_progress_to_completed'].append(in_progress_duration)
        
        # Total completion time
        if order['completed_at']:
            total_duration = (
                datetime.fromisoformat(order['completed_at']) -
                datetime.fromisoformat(order['created_at'])
            ).total_seconds() / 3600
            
            state_durations['total_completion_time'].append(total_duration)
    
    # Calculate statistics
    duration_stats = {}
    for state_name, durations in state_durations.items():
        if durations:
            duration_stats[state_name] = {
                'avg_hours': statistics.mean(durations),
                'median_hours': statistics.median(durations),
                'min_hours': min(durations),
                'max_hours': max(durations),
                'count': len(durations)
            }
    
    return duration_stats
```

## Error Handling and Recovery

### State Inconsistency Recovery

#### Automatic State Repair
```python
def repair_inconsistent_service_order_states():
    """Automatically repair service orders with inconsistent states"""
    
    inconsistent_orders = validate_service_order_state_consistency()
    
    repair_results = []
    
    for order in inconsistent_orders:
        try:
            # Repair the inconsistent state
            cursor = get_db().cursor()
            
            cursor.execute('''
                UPDATE service_orders 
                SET status = ?, completed_at = CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE NULL END
                WHERE id = ?
            ''', (order['expected_status'], order['expected_status'], order['id']))
            
            # Log the repair action
            log_administrative_action(
                action='automatic_state_repair',
                entity_id=order['id'], 
                old_value=order['order_status'],
                new_value=order['expected_status'],
                reason='Automatic consistency repair',
                user_id=None  # System action
            )
            
            get_db().commit()
            
            repair_results.append({
                'service_order_id': order['id'],
                'repaired': True,
                'old_status': order['order_status'],
                'new_status': order['expected_status']
            })
            
        except Exception as e:
            get_db().rollback()
            repair_results.append({
                'service_order_id': order['id'],
                'repaired': False,
                'error': str(e)
            })
    
    return repair_results
```

This comprehensive state management system ensures reliable service order tracking while providing the flexibility and visibility needed for efficient vending machine fleet operations.