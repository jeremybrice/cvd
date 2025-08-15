# User Roles and Permissions


## Metadata
- **ID**: 02_REQUIREMENTS_USER_ROLES
- **Type**: Requirements
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #data-exchange #data-layer #database #debugging #device-management #dex-parser #driver-app #integration #logistics #machine-learning #metrics #mobile #operations #optimization #performance #planogram #product-placement #pwa #reporting #requirements #route-management #security #service-orders #specifications #troubleshooting #user-stories #vending-machine
- **Intent**: The CVD system implements a four-tier role-based access control (RBAC) system that governs user permissions across the enterprise vending machine fleet management platform
- **Audience**: system administrators, managers, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/02-requirements/
- **Category**: 02 Requirements
- **Search Keywords**: access, analytics, cabinet, characteristics, configuration, core, data, device, dex, driver, focus, full, key, management, mobile-centric

## Overview

The CVD system implements a four-tier role-based access control (RBAC) system that governs user permissions across the enterprise vending machine fleet management platform. Each role is designed to align with specific job functions and operational responsibilities.

## Role Hierarchy

```
Admin
├── System configuration and management
├── Full user lifecycle management
└── Complete system access

Manager
├── Operational management
├── Reporting and analytics
└── Device and planogram management

Driver
├── Mobile service operations
├── Service order execution
└── Field data collection

Viewer
├── Read-only reporting access
├── Basic device information
└── Analytics viewing
```

## User Role Definitions

### Admin Role

**Purpose**: Complete system administration and oversight
**Target Users**: System administrators, IT staff, executive management

**Core Responsibilities**:
- System configuration and maintenance
- User account lifecycle management
- Security policy enforcement
- Data integrity oversight
- System monitoring and troubleshooting

**Key Characteristics**:
- Unrestricted system access
- Can manage all user accounts
- Access to sensitive system configurations
- Database query capabilities
- Audit trail oversight

### Manager Role

**Purpose**: Operational management and strategic oversight
**Target Users**: Operations managers, fleet supervisors, regional managers

**Core Responsibilities**:
- Fleet operations management
- Performance monitoring and optimization
- Service order coordination
- Route planning and optimization
- Strategic reporting and analysis

**Key Characteristics**:
- Full operational access
- Cannot manage user accounts
- Can configure devices and planograms
- Access to all reports and analytics
- Service order management

### Driver Role

**Purpose**: Field service execution and data collection
**Target Users**: Service technicians, route drivers, field personnel

**Core Responsibilities**:
- Service order execution
- Inventory restocking
- Equipment maintenance
- Photo documentation
- Real-time data collection

**Key Characteristics**:
- Mobile-first interface access
- Limited to assigned service orders
- Cannot modify system configurations
- Can update service execution data
- Offline capability support

### Viewer Role

**Purpose**: Read-only access for reporting and monitoring
**Target Users**: Stakeholders, analysts, external partners, auditors

**Core Responsibilities**:
- Report generation and viewing
- Performance monitoring
- Data analysis
- Compliance reporting

**Key Characteristics**:
- Read-only access only
- Cannot modify any system data
- Access to reports and dashboards
- No operational capabilities
- Limited system navigation

## Comprehensive Permissions Matrix

| Resource | Admin | Manager | Driver | Viewer |
|----------|--------|---------|--------|--------|
| **Authentication & Session Management** | | | | |
| Login/Logout | ✓ | ✓ | ✓ | ✓ |
| Change Own Password | ✓ | ✓ | ✓ | ✓ |
| View Own Profile | ✓ | ✓ | ✓ | ✓ |
| Update Own Profile | ✓ | ✓ | ✓ | ✓ |
| **User Management** | | | | |
| View All Users | ✓ | ✗ | ✗ | ✗ |
| Create Users | ✓ | ✗ | ✗ | ✗ |
| Edit User Details | ✓ | ✗ | ✗ | ✗ |
| Delete/Deactivate Users | ✓ | ✗ | ✗ | ✗ |
| Reset User Passwords | ✓ | ✗ | ✗ | ✗ |
| Assign User Roles | ✓ | ✗ | ✗ | ✗ |
| **Device Management** | | | | |
| View Devices | ✓ | ✓ | ✓ | ✓ |
| Create Devices | ✓ | ✓ | ✗ | ✗ |
| Edit Device Details | ✓ | ✓ | ✗ | ✗ |
| Delete Devices (Soft) | ✓ | ✗ | ✗ | ✗ |
| Restore Deleted Devices | ✓ | ✗ | ✗ | ✗ |
| Configure Cabinets | ✓ | ✓ | ✗ | ✗ |
| View Device History | ✓ | ✓ | ✓ | ✓ |
| **Planogram Management** | | | | |
| View Planograms | ✓ | ✓ | ✓ | ✓ |
| Create Planograms | ✓ | ✓ | ✗ | ✗ |
| Edit Planograms | ✓ | ✓ | ✗ | ✗ |
| Delete Planograms | ✓ | ✗ | ✗ | ✗ |
| AI Optimization | ✓ | ✓ | ✗ | ✗ |
| Product Assignment | ✓ | ✓ | ✗ | ✗ |
| Update Inventory Levels | ✓ | ✓ | ✓* | ✗ |
| **Service Order Management** | | | | |
| View Service Orders | ✓ | ✓ | ✓* | ✓ |
| Create Service Orders | ✓ | ✓ | ✗ | ✗ |
| Edit Service Orders | ✓ | ✓ | ✗ | ✗ |
| Execute Service Orders | ✓ | ✓ | ✓* | ✗ |
| Cancel Service Orders | ✓ | ✓ | ✗ | ✗ |
| Generate Pick Lists | ✓ | ✓ | ✓* | ✗ |
| Upload Service Photos | ✓ | ✓ | ✓ | ✗ |
| **Route Management** | | | | |
| View Routes | ✓ | ✓ | ✓* | ✓ |
| Create Routes | ✓ | ✓ | ✗ | ✗ |
| Edit Routes | ✓ | ✓ | ✗ | ✗ |
| Delete Routes | ✓ | ✗ | ✗ | ✗ |
| Assign Devices to Routes | ✓ | ✓ | ✗ | ✗ |
| Assign Drivers to Routes | ✓ | ✓ | ✗ | ✗ |
| **Analytics & Reporting** | | | | |
| View Dashboard | ✓ | ✓ | ✗ | ✓ |
| Asset Sales Reports | ✓ | ✓ | ✗ | ✓ |
| Product Sales Reports | ✓ | ✓ | ✗ | ✓ |
| Performance Analytics | ✓ | ✓ | ✗ | ✓ |
| Export Reports | ✓ | ✓ | ✗ | ✓ |
| Create Custom Reports | ✓ | ✓ | ✗ | ✗ |
| **System Configuration** | | | | |
| Database Viewer | ✓ | ✗ | ✗ | ✗ |
| System Settings | ✓ | ✗ | ✗ | ✗ |
| Company Settings | ✓ | ✓ | ✗ | ✗ |
| DEX Parser Configuration | ✓ | ✓ | ✗ | ✗ |
| Activity Monitoring | ✓ | ✗ | ✗ | ✗ |
| Audit Log Access | ✓ | ✗ | ✗ | ✗ |
| **Data Management** | | | | |
| DEX File Upload | ✓ | ✓ | ✗ | ✗ |
| Data Import/Export | ✓ | ✓ | ✗ | ✗ |
| Database Queries | ✓ | ✗ | ✗ | ✗ |
| Data Purging | ✓ | ✗ | ✗ | ✗ |

*Driver access is limited to assigned routes and service orders only

## Role-Based Feature Access Mapping

### Admin Feature Access

**Full System Access**: All features and functionalities
- User Management Dashboard
- System Configuration Panel
- Database Viewer and Query Interface
- Activity Monitoring and Security Alerts
- Complete Audit Trail Access
- System Health Monitoring
- Backup and Recovery Tools

### Manager Feature Access

**Operational Management Focus**: Business operations and fleet management
- Fleet Dashboard with KPIs
- Device and Planogram Management
- Service Order Creation and Management
- Route Planning and Optimization
- Comprehensive Reports and Analytics
- Company Settings Configuration
- DEX File Processing and Analysis

**Restricted Access**:
- No user account management
- No database query access
- No system-level configurations
- No audit log access beyond operational events

### Driver Feature Access

**Mobile-Centric Operations**: Field service execution
- Driver PWA (Progressive Web App)
- Assigned Service Orders View
- Order Execution Interface
- Photo Upload Capability
- Offline Data Synchronization
- Basic Device Information View
- Route Navigation Assistance

**Restricted Access**:
- Cannot create or modify service orders
- Cannot access other drivers' assignments
- Cannot modify device or planogram configurations
- No access to system reports or analytics
- Cannot view administrative functions

### Viewer Feature Access

**Read-Only Reporting**: Information access only
- Business Intelligence Dashboard
- Asset and Product Performance Reports
- Fleet Overview and Status
- Historical Trend Analysis
- Export Capabilities for Reports
- Basic Device Status Information

**Restricted Access**:
- No modification capabilities
- No operational functions
- No configuration access
- No service order interaction
- No mobile app access

## Security Constraints and Business Rules

### Authentication Requirements
- All roles require secure authentication
- Session timeout after 8 hours of inactivity
- Password complexity requirements enforced
- Multi-device session management

### Role Assignment Rules
- Only Admins can assign or modify user roles
- Users cannot elevate their own permissions
- Role changes require immediate session refresh
- Audit logging for all role modifications

### Data Access Constraints
- Drivers can only access assigned routes and orders
- Soft-deleted resources invisible to non-Admin users
- Historical data access varies by role
- Geographic restrictions may apply based on business rules

### Operational Constraints
- Users with pending service orders cannot be deactivated
- Drivers must complete in-progress orders before reassignment
- Manager role required for device creation and major configuration changes
- Admin approval required for bulk data operations

## Permission Inheritance and Delegation

### Hierarchical Permissions
- Higher roles do not automatically inherit lower role permissions
- Each role is specifically designed for its function
- Permissions are explicitly granted, not inherited

### Temporary Permissions
- No temporary permission elevation supported
- Role changes require Admin intervention
- Emergency access procedures require system administrator involvement

### Delegation Rules
- Admins cannot delegate user management to other roles
- Managers cannot delegate device creation permissions
- Service order execution cannot be delegated between drivers

## Audit and Compliance

### Role-Based Audit Requirements
- All permission checks are logged
- Unauthorized access attempts trigger alerts
- Role changes create permanent audit entries
- User activity tracking varies by role level

### Compliance Considerations
- Role definitions support regulatory compliance
- Separation of duties enforced through role restrictions
- Data access logging meets audit requirements
- User certification tracking per role requirements

## Implementation Notes

### Technical Implementation
- Role permissions stored in `auth.py` `get_user_permissions()` method
- Database-level role validation in user sessions
- API endpoint protection through decorators
- Frontend route protection based on user role

### Security Implementation
- Role validation on every authenticated request
- Session-based role caching for performance
- Privilege escalation detection and alerting
- Comprehensive audit logging for security events