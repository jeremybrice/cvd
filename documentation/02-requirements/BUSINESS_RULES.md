# Business Rules


## Metadata
- **ID**: 02_REQUIREMENTS_BUSINESS_RULES
- **Type**: Requirements
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #data-exchange #data-layer #database #debugging #device-management #dex-parser #integration #logistics #machine-learning #metrics #operations #optimization #performance #planogram #product-placement #reporting #requirements #route-management #security #service-orders #specifications #troubleshooting #user-stories #vending-machine
- **Intent**: Requirements for Business Rules
- **Audience**: system administrators, managers, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/02-requirements/
- **Category**: 02 Requirements
- **Search Keywords**: (40+, additional, adjustments, alpha-numeric, assignment, audit, automated, base, business, cabinet, calculation, calculations, cancellation, cascade, cascading

## Core Business Logic Documentation

This document outlines the fundamental business rules, constraints, and operational logic that govern the CVD system's behavior. These rules ensure data integrity, operational consistency, and regulatory compliance across all system operations.

## Service Order Workflow Rules

### Service Order States and Transitions

**Valid State Transitions:**
```
pending → in_progress → completed
pending → cancelled
in_progress → cancelled (with restrictions)
```

**State Transition Rules:**

1. **Pending to In-Progress**:
   - Triggered when first cabinet service begins
   - Must be initiated by assigned driver or authorized manager
   - Started timestamp is recorded
   - Order remains "in_progress" until ALL cabinets are serviced

2. **In-Progress to Completed**:
   - Automatic transition when final cabinet is marked as serviced
   - Completed timestamp is recorded
   - All cabinet services must have recorded delivery quantities
   - System validates all required data is present

3. **Cancellation Rules**:
   - Pending orders: Can be cancelled by managers or admins
   - In-progress orders: Require admin authorization and special handling
   - Completed orders: Cannot be cancelled, only marked with notes

### Cabinet Service Execution Rules

1. **Cabinet Selection Validation**:
   - Only cabinets with products below par level can be selected
   - Empty slots (product_id = 1) are excluded from service requirements
   - Cabinet must exist and be associated with active (non-deleted) device

2. **Pick List Generation Logic**:
   - Par Level - Current Quantity = Required Quantity (if positive)
   - Products aggregated across all selected cabinets
   - Sorted by category, then alphabetically for picking efficiency
   - Zero or negative requirements excluded from pick list

3. **Service Execution Constraints**:
   - Driver can only service cabinets assigned to their route
   - Actual delivery quantities cannot exceed par level for any slot
   - Negative delivery quantities not permitted
   - Service completion updates planogram quantities in real-time

### Time Estimation Rules

- **Base Time Calculation**: 10 minutes per cabinet (regardless of size)
- **Additional Factors**: Complex cabinet configurations may require adjustment
- **Total Service Time**: Sum of all cabinet service times plus travel time estimates

## Planogram Slot Rules and Validation

### Slot Configuration Rules

1. **Slot Position Validation**:
   - Position must be within cabinet grid dimensions (1-based indexing)
   - Format: "R{row}C{column}" (e.g., "R1C1", "R3C5")
   - Positions must be unique within each planogram
   - Invalid positions rejected with clear error messages

2. **Product Assignment Rules**:
   - Product ID must exist in products table
   - Product ID = 1 reserved for empty slots
   - Only one product per slot position
   - Product changes tracked in audit log

3. **Quantity and Capacity Validation**:
   - Current quantity: 0 ≤ quantity ≤ capacity
   - Capacity: Must be > 0 for non-empty slots
   - Par level: 0 ≤ par_level ≤ capacity
   - Par level recommended as 80-90% of capacity for optimal operations

### Inventory Management Rules

1. **Par Level Calculations**:
   - Default par level: 85% of slot capacity
   - Minimum par level: 1 unit (cannot be zero for active products)
   - Maximum par level: 100% of slot capacity
   - Par levels can be adjusted based on sales velocity data

2. **Restocking Thresholds**:
   - Service Required: Current quantity < par level
   - Critical Level: Current quantity < 25% of par level
   - Empty Slot: Current quantity = 0 and product_id != 1
   - Units to Par: par_level - current_quantity (when positive)

3. **Inventory Update Rules**:
   - Updates must be within capacity constraints
   - Negative quantities not permitted
   - Quantity changes logged with timestamp and user
   - Real-time updates to prevent concurrent modification conflicts

## Soft Delete Policies and Recovery

### Soft Delete Implementation

1. **Device Soft Delete**:
   - Sets deleted_at timestamp and deleted_by user ID
   - Device remains in database but excluded from operational queries
   - All related data (cabinets, planograms) remains intact
   - Only admin users can view and recover soft-deleted devices

2. **Cascade Protection Rules**:
   - Associated cabinet configurations preserved
   - Planogram data maintained for historical reference
   - Service order references preserved for audit trail
   - Sales data relationships maintained

### Recovery Procedures

1. **Device Recovery**:
   - Clears deleted_at and deleted_by fields
   - Device becomes immediately available in system
   - All historical data remains intact
   - Recovery action logged in audit trail

2. **Recovery Validation**:
   - Asset ID uniqueness re-validated upon recovery
   - Location and route assignments verified for conflicts
   - Cabinet configurations validated for current device types

### Data Retention Rules

- Soft-deleted devices retained indefinitely for audit purposes
- Admin users can permanently delete after 1-year retention minimum
- Recovery available for 90 days without special approval
- Extended recovery requires business justification documentation

## Cabinet Configuration Rules

### Multi-Cabinet Support

1. **Cabinet Limits**:
   - Maximum 3 cabinets per device
   - Cabinet indices must be unique per device (0, 1, 2)
   - Each cabinet can have different types and dimensions
   - Parent cabinet designation for primary cabinet identification

2. **Cabinet Type Constraints**:
   - Cabinet type must exist in cabinet_types table
   - Dimensions (rows × columns) must match cabinet type specifications
   - Cabinet type changes require planogram regeneration
   - Historical cabinet configurations preserved in audit log

3. **Device Type Compatibility**:
   - Device type determines if additional cabinets allowed
   - Single-cabinet devices cannot have additional cabinets added
   - Multi-cabinet devices validate cabinet type compatibility
   - Device type changes require cabinet configuration validation

### Planogram Integration Rules

1. **Cabinet-Planogram Relationship**:
   - Each cabinet has exactly one planogram
   - Planogram key format: "{device_id}_{cabinet_index}"
   - Planogram dimensions must match cabinet configuration
   - Cabinet deletion cascades to planogram removal

2. **Slot Generation Rules**:
   - Slots generated based on cabinet rows × columns
   - All slots initially empty (product_id = 1)
   - Slot positions calculated as grid coordinates
   - Total slots cannot exceed system limits (maximum 400 per cabinet)

## Par Level Calculations and Thresholds

### Calculation Methodology

1. **Base Par Level Determination**:
   - New products: 85% of slot capacity
   - Existing products: Historical sales velocity consideration
   - Minimum viable par level: 1 unit for active products
   - Maximum par level: 100% of slot capacity

2. **Velocity-Based Adjustments**:
   - High velocity products (>1 unit/day): 90-95% of capacity
   - Medium velocity products (0.3-1 unit/day): 80-85% of capacity
   - Low velocity products (<0.3 unit/day): 70-80% of capacity
   - Static products (no recent sales): 50% of capacity

### Threshold Classifications

1. **Service Priority Levels**:
   - **Critical**: Current quantity ≤ 25% of par level
   - **High**: Current quantity ≤ 50% of par level
   - **Medium**: Current quantity ≤ 75% of par level
   - **Low**: Current quantity > 75% of par level

2. **Automated Triggers**:
   - Service orders automatically suggest critical and high priority items
   - Route planning systems prioritize devices with critical inventory levels
   - Analytics dashboards highlight devices requiring immediate attention
   - Alert notifications for sustained critical inventory conditions

### Dynamic Par Level Management

1. **Seasonal Adjustments**:
   - Par levels adjusted based on historical seasonal patterns
   - Holiday periods may increase par levels by 10-20%
   - Off-season adjustments may decrease par levels by 10-15%
   - Weather-dependent products have dynamic par level algorithms

2. **Performance-Based Optimization**:
   - Monthly par level review based on actual sales performance
   - Overstock situations (consistently high inventory) trigger par level reduction
   - Stockout frequency triggers par level increase recommendations
   - AI optimization suggestions for par level adjustments

## DEX File Processing Rules

### File Validation Rules

1. **File Format Requirements**:
   - Must be valid DEX format with proper structure
   - File size limits: Maximum 50MB per file
   - Character encoding: ASCII or UTF-8 supported
   - File extension: .dex or .txt accepted

2. **Content Validation**:
   - Must contain valid DXS (header) and DXE (trailer) records
   - Machine serial number must be present and valid
   - Transaction records must have valid format and data types
   - Checksums validated where present

### Record Processing Rules

1. **Supported Record Types** (40+ types):
   - **DXS**: Header record with machine and operator information
   - **ST**: Configuration and setup information
   - **PA**: Product activity and sales data
   - **CA**: Cash audit information
   - **VA**: Vend audit records
   - **DA**: Date/time audit records
   - **TA**: Transaction audit information

2. **Data Extraction Rules**:
   - PA records: Extract sales units, revenue, and pricing information
   - Selection numbers mapped to planogram positions when possible
   - Invalid or corrupted records logged but don't stop processing
   - Duplicate records detected and handled appropriately

### Grid Pattern Detection

1. **Pattern Recognition** (5 supported patterns):
   - **Sequential**: 1, 2, 3, 4... (linear progression)
   - **Row-Column**: 11, 12, 13, 21, 22, 23... (grid-based)
   - **Alpha-Numeric**: A1, A2, A3, B1, B2, B3... (mixed format)
   - **Custom**: Manufacturer-specific patterns
   - **Hybrid**: Combination of multiple pattern types

2. **Mapping Rules**:
   - Detected patterns mapped to cabinet grid positions
   - Invalid selections logged but processing continues
   - Manual override capability for complex patterns
   - Pattern detection confidence scoring for validation

## User Account Lifecycle Rules

### Account Creation Rules

1. **Username Requirements**:
   - Must be unique across all users
   - 3-50 characters, alphanumeric only
   - Cannot be changed after creation
   - Cannot reuse usernames from deleted accounts

2. **Role Assignment Rules**:
   - New users default to 'viewer' role unless specified
   - Only admin users can assign roles
   - Role changes take effect immediately
   - Role assignment changes logged in audit trail

### Account Deactivation Constraints

1. **Service Order Dependencies**:
   - Users with pending service orders cannot be deactivated
   - Users with in-progress service orders require special handling
   - Completed service orders do not block deactivation
   - Service order reassignment required before deactivation

2. **Route Assignment Constraints**:
   - Drivers assigned to routes require route reassignment first
   - Active route assignments prevent user deactivation
   - Historical route assignments preserved for audit purposes
   - Route reassignment notifications sent to affected parties

### Password and Security Rules

1. **Password Requirements**:
   - Minimum 8 characters length
   - Must contain uppercase, lowercase, and numeric characters
   - Special characters recommended but not required
   - Password history prevents reuse of last 5 passwords

2. **Session Management Rules**:
   - Session timeout: 8 hours of inactivity
   - Concurrent sessions allowed across devices
   - Session invalidation upon role changes
   - Forced logout for security violations

## Data Integrity and Validation Rules

### Foreign Key Constraints

1. **Cascading Delete Rules**:
   - Device deletion: CASCADE to cabinet_configurations and planograms
   - Cabinet deletion: CASCADE to planogram_slots
   - Route deletion: SET NULL on device route assignments
   - User deletion: SET NULL on service order assignments

2. **Referential Integrity**:
   - All foreign keys must reference existing records
   - Orphaned records prevented by database constraints
   - Circular references detected and prevented
   - Data consistency validated at transaction level

### Audit Trail Requirements

1. **Required Audit Events**:
   - All user account lifecycle events
   - Device creation, modification, and deletion
   - Service order state transitions
   - Planogram configuration changes
   - Role and permission modifications

2. **Audit Data Retention**:
   - Audit logs retained for minimum 7 years
   - Security events retained permanently
   - Performance audit data retained for 2 years
   - User activity logs retained for 1 year

### Data Validation Standards

1. **Input Validation Rules**:
   - All user inputs sanitized and validated
   - Numeric fields validated for range and type
   - String fields validated for length and format
   - Date fields validated for reasonable ranges

2. **Business Logic Validation**:
   - Cross-field validation for related data
   - Business rule enforcement at database level
   - Transaction-level consistency checks
   - Real-time validation feedback to users