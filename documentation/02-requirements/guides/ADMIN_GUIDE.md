# Administrator User Guide


## Metadata
- **ID**: 02_REQUIREMENTS_GUIDES_ADMIN_GUIDE
- **Type**: Requirements
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #data-exchange #data-layer #database #debugging #device-management #dex-parser #integration #logistics #machine-learning #metrics #operations #optimization #performance #planogram #product-placement #quality-assurance #reporting #requirements #route-management #security #service-orders #specifications #testing #troubleshooting #user-stories #vending-machine
- **Intent**: As a CVD system administrator, you have complete system access and responsibility for maintaining the enterprise vending machine fleet management platform
- **Audience**: system administrators, managers, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/02-requirements/guides/
- **Category**: Guides
- **Search Keywords**: #asset-sales, #company-settings, #coolers, #database, #dex-parser, #home, #new-device, #planogram, #product-sales, #profile, #route-schedule, #service-orders, #user-management, (recommended), access

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [User Management](#user-management)
4. [System Configuration](#system-configuration)
5. [Device Fleet Management](#device-fleet-management)
6. [Security & Monitoring](#security--monitoring)
7. [Reports & Analytics](#reports--analytics)
8. [Database Management](#database-management)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## Overview

As a CVD system administrator, you have complete system access and responsibility for maintaining the enterprise vending machine fleet management platform. Your role encompasses user management, system configuration, security monitoring, and ensuring optimal system performance.

### Admin Capabilities
- Complete system administration and oversight
- Full user lifecycle management (create, edit, delete, restore)
- System configuration and company settings
- Security policy enforcement and monitoring
- Database access and maintenance
- Audit log review and compliance reporting
- Device fleet oversight and recovery operations

### Key Responsibilities
- Maintain user accounts and role assignments
- Monitor system security and performance
- Configure system-wide settings
- Oversee data integrity and backups
- Troubleshoot system issues
- Ensure regulatory compliance

## Getting Started

### Initial Login
1. Navigate to the CVD system URL
2. Use your administrator credentials to log in
3. You'll be directed to the home dashboard with full system access

### Dashboard Overview
The admin dashboard provides:
- System health indicators
- User activity metrics  
- Device status overview
- Recent audit log entries
- Quick access to admin functions

### Navigation Structure
Admins have access to all system pages:
- **Home Dashboard** (`#home`) - System overview and KPIs
- **Device Management** (`#coolers`) - Fleet management (PCP.html)
- **Device Configuration** (`#new-device`) - Add/edit devices (INVD.html)
- **Planogram Management** (`#planogram`) - Product placement (NSPT.html)
- **Service Orders** (`#service-orders`) - Order management
- **Route Planning** (`#route-schedule`) - Route optimization
- **Analytics** (`#asset-sales`, `#product-sales`) - Performance reports
- **System Tools** (`#database`) - Database viewer
- **DEX Parser** (`#dex-parser`) - Data import tools
- **Company Settings** (`#company-settings`) - System configuration
- **User Management** (`#user-management`) - Account administration
- **Profile Management** (`#profile`) - Account settings

## User Management

### Accessing User Management
1. Click on the main navigation menu
2. Select "User Management" or navigate to `#user-management`
3. The user management interface will load in the main content area

### User Management Interface

#### Overview Section
- **User Count Badge** - Displays total active users
- **Filter Controls** - Filter users by role, status, or activity
- **Search Functionality** - Find users by name, email, or username
- **Bulk Actions** - Perform operations on multiple users

#### User List View
The user table displays:
- User avatar and basic information
- Username and email address
- Assigned role (Admin, Manager, Driver, Viewer)
- Status (Active, Inactive, Pending)
- Last login date/time
- Action buttons for each user

### Creating New Users

#### Step-by-Step User Creation
1. **Access Creation Form**
   - Click the "Add New User" button in the toolbar
   - A modal dialog will appear with the user creation form

2. **Required Information**
   - **Username**: Unique identifier (3-50 characters, alphanumeric)
   - **Email Address**: Valid email for notifications and password resets
   - **Full Name**: Display name for the interface
   - **Role**: Select from Admin, Manager, Driver, or Viewer
   - **Password**: Initial password (user will be prompted to change on first login)

3. **Optional Settings**
   - **Send Welcome Email**: Automatically notify user of account creation
   - **Require Password Change**: Force password reset on first login
   - **Account Status**: Set initial status (Active by default)

4. **Validation and Creation**
   - System validates all required fields
   - Checks for duplicate usernames and emails
   - Creates user account and sends confirmation
   - User appears in the user list immediately

#### Role Assignment Guidelines
- **Admin**: Only assign to trusted IT personnel
- **Manager**: For operational supervisors and fleet managers
- **Driver**: For field service personnel
- **Viewer**: For stakeholders needing read-only access

### Editing User Details

#### User Profile Management
1. **Access User Profile**
   - Click the "Edit" button next to any user in the list
   - The user edit modal will display current information

2. **Editable Fields**
   - Full name and display preferences
   - Email address (with verification if changed)
   - Role assignment (with immediate effect)
   - Account status (Active/Inactive)
   - Password reset (generate new temporary password)

3. **Role Change Procedures**
   - **Role Elevation**: Requires confirmation dialog
   - **Role Demotion**: System checks for active assignments
   - **Immediate Effect**: Role changes apply instantly
   - **Session Impact**: User may need to re-login for new permissions

4. **Account Status Changes**
   - **Deactivation**: Preserves data but blocks access
   - **Reactivation**: Restores full access
   - **Pending Status**: For new accounts awaiting activation

### User Deactivation and Deletion

#### Soft Delete Process
The CVD system uses soft deletion to maintain data integrity:

1. **Deactivation (Recommended)**
   - Click "Deactivate" next to the user
   - User loses system access immediately
   - Data and history are preserved
   - Can be reactivated at any time

2. **Soft Deletion**
   - Available only for users with no active assignments
   - User marked as deleted but data retained
   - Requires confirmation dialog
   - Can be restored from trash view

3. **Permanent Deletion**
   - **Warning**: Only available after soft deletion
   - Completely removes user data
   - Cannot be undone
   - Requires administrator password confirmation

#### Pre-Deletion Checks
Before deactivating users, the system validates:
- No active service orders assigned (Drivers)
- No pending route assignments
- No incomplete data entry tasks
- System notifies of any blocking conditions

### Password Management

#### Password Reset Procedures
1. **Admin-Initiated Reset**
   - Select user from the list
   - Click "Reset Password" 
   - Choose temporary password or auto-generate
   - Option to send reset email to user

2. **Password Policies**
   - Minimum 8 characters
   - Must contain uppercase, lowercase, number
   - Special character required
   - Cannot reuse last 5 passwords
   - 90-day expiration (configurable)

3. **Account Lockout Management**
   - Auto-lockout after 5 failed attempts
   - 30-minute lockout duration
   - Admin can manually unlock accounts
   - Audit trail for all lockout events

### Bulk User Operations

#### Mass User Management
1. **Bulk Selection**
   - Use checkboxes to select multiple users
   - "Select All" option for page-wide selection
   - Filter-based selection available

2. **Available Bulk Actions**
   - Password reset for multiple users
   - Role changes (with confirmation)
   - Account status updates
   - Export user lists
   - Send system notifications

3. **Bulk Import/Export**
   - **Export**: CSV format with all user data
   - **Import**: CSV template for bulk user creation
   - **Validation**: Pre-import data validation
   - **Rollback**: Undo capability for bulk operations

## System Configuration

### Company Settings Management

#### Accessing Company Settings
1. Navigate to `#company-settings`
2. The settings page provides multiple configuration sections
3. Changes require admin privileges and confirmation

#### Core Configuration Sections

##### Company Information
- **Company Name**: Displayed throughout the system
- **Contact Information**: Default contact details
- **Business Hours**: Operating schedule settings
- **Time Zone**: System-wide time zone configuration
- **Address**: Primary business location

##### System Preferences
- **Session Timeout**: Default user session length (1-12 hours)
- **Password Policies**: Complexity and expiration rules
- **Email Notifications**: System-wide email settings
- **Audit Logging**: Retention and detail level settings
- **Backup Schedule**: Automated backup frequency

##### Security Settings
- **Login Attempts**: Failed login threshold (3-10 attempts)
- **Lockout Duration**: Account lockout time (15-120 minutes)
- **Multi-Factor Authentication**: Enable/disable MFA requirements
- **API Access**: External integration permissions
- **Data Encryption**: Encryption policy settings

#### Making Configuration Changes
1. **Edit Mode Activation**
   - Click "Edit Settings" to unlock form fields
   - Yellow highlight indicates editable sections
   - Warning displayed about system-wide impact

2. **Validation and Confirmation**
   - Real-time validation of entered values
   - Confirmation dialog for sensitive changes
   - Option to schedule changes for maintenance window

3. **Change Application**
   - Some changes apply immediately
   - Others require system restart (clearly indicated)
   - Users notified of relevant changes via system messages

### System Health Monitoring

#### Health Dashboard Access
1. Navigate to the admin dashboard (`#home`)
2. Dedicated "System Health" panel shows key metrics
3. Color-coded indicators for quick status assessment

#### Key Health Metrics
- **Database Performance**: Query times and connection status
- **Service Availability**: API endpoint response times
- **Storage Usage**: Database and file system capacity
- **User Activity**: Current sessions and activity levels
- **Error Rates**: Application and system error frequencies

#### Performance Thresholds
- **Green**: All systems operating normally
- **Yellow**: Performance degradation detected
- **Red**: Critical issues requiring immediate attention

### Notification Configuration

#### System Notification Settings
1. **Admin Alerts**
   - Security events and failed login attempts
   - System errors and performance issues
   - Data integrity warnings
   - Backup completion status

2. **User Notifications**
   - Account creation and modification
   - Password expiration warnings
   - Service order assignments
   - System maintenance notifications

3. **Email Templates**
   - Customizable email templates for user communications
   - Support for company branding
   - Multiple language support (if configured)

## Device Fleet Management

### Device Overview and Management

#### Accessing Device Management
1. Navigate to `#coolers` for the main device list (PCP.html)
2. Device list shows all fleet devices with status indicators
3. Filter and search capabilities for large fleets

#### Device List Features
- **Status Indicators**: Online, offline, maintenance required
- **Location Information**: Address and route assignment
- **Device Details**: Model, configuration, last contact
- **Performance Metrics**: Sales data and uptime statistics
- **Action Buttons**: Edit, configure, service, delete options

### Device Configuration Management

#### Accessing Device Configuration
1. Click "Edit" on any device from the device list
2. Or navigate to `#new-device` (INVD.html) for new device setup
3. Configuration interface loads with device details

#### Device Information Management
1. **Basic Device Details**
   - Device ID and name assignment
   - Location address with geocoding
   - Device type and model selection
   - Installation and service dates

2. **Cabinet Configuration**
   - Support for multi-cabinet devices (up to 3 cabinets)
   - Individual cabinet naming and specifications
   - Product capacity settings per cabinet
   - Temperature and operational parameters

3. **Network and Communication**
   - Network connection settings
   - DEX communication parameters
   - Remote monitoring configuration
   - Telemetry data collection settings

#### Advanced Configuration Options
- **Service Parameters**: Maintenance schedules and thresholds
- **Pricing Configuration**: Product pricing by location
- **Planogram Assignment**: Link to specific planogram layouts
- **Route Assignment**: Assign device to service routes

### Device Recovery and Troubleshooting

#### Soft Delete Recovery
As an admin, you can recover accidentally deleted devices:

1. **Access Deleted Devices**
   - Use the "Show Deleted" filter in device management
   - Deleted devices appear with special indicators
   - Deletion date and reason displayed

2. **Recovery Process**
   - Click "Restore" button next to deleted device
   - Confirm restoration in dialog box
   - Device restored with all historical data
   - Previous configuration settings maintained

3. **Permanent Deletion**
   - Only available for admin users
   - Requires password confirmation
   - Cannot be undone after confirmation
   - All associated data permanently removed

#### Device Communication Issues
1. **Offline Device Detection**
   - System automatically detects offline devices
   - Email alerts sent to administrators
   - Dashboard indicators show offline status

2. **Troubleshooting Tools**
   - Communication test functions
   - Historical connection logs
   - Network diagnostic utilities
   - Remote restart capabilities (if supported)

3. **Service Escalation**
   - Automatic service order generation for persistent issues
   - Integration with maintenance scheduling
   - Priority assignment based on device importance

## Security & Monitoring

### Activity Monitoring

#### Accessing Activity Monitoring
1. Navigate to `/pages/admin/activity-monitor.html`
2. Comprehensive activity dashboard loads
3. Real-time activity feed and historical analysis

#### Activity Tracking Features
- **User Actions**: Login, logout, and system interactions
- **Data Changes**: Create, update, delete operations
- **Security Events**: Failed logins, permission escalations
- **System Events**: Configuration changes, maintenance activities

#### Activity Analysis Tools
1. **Real-Time Feed**
   - Live activity stream
   - Color-coded event types
   - User and timestamp information
   - Action details and outcomes

2. **Historical Analysis**
   - Date range filtering
   - User-specific activity reports
   - Action type categorization
   - Export capabilities for compliance

3. **Alert Configuration**
   - Threshold-based alerting
   - Email notifications for critical events
   - Custom alert rules
   - Integration with external monitoring systems

### Audit Log Management

#### Audit Log Access
1. **Direct Database Access**
   - Navigate to `#database` for database viewer
   - Select `audit_log` table for detailed records
   - Advanced querying capabilities available

2. **Filtered Audit Views**
   - Pre-configured filters for common audit needs
   - Security-focused event filtering
   - Compliance reporting templates
   - Automated report generation

#### Audit Log Analysis
1. **Security Event Review**
   - Failed login attempts and patterns
   - Unauthorized access attempts
   - Permission escalation events
   - System configuration changes

2. **User Activity Patterns**
   - User login frequency and timing
   - Feature usage statistics
   - Data access patterns
   - Unusual activity detection

3. **Compliance Reporting**
   - Automated compliance report generation
   - Data retention policy enforcement
   - Regulatory requirement fulfillment
   - External auditor data preparation

### Security Policy Enforcement

#### User Session Management
1. **Session Monitoring**
   - Active session dashboard
   - Session duration tracking
   - Concurrent session limits
   - Remote session termination

2. **Session Policies**
   - Maximum session duration (configurable)
   - Idle timeout settings
   - Multi-device login policies
   - Session renewal requirements

#### Data Access Controls
1. **Permission Verification**
   - Real-time permission checking
   - Role-based access enforcement
   - Resource-level access control
   - Audit trail for access attempts

2. **Data Classification**
   - Sensitive data identification
   - Access level requirements
   - Encryption requirements
   - Export restrictions

## Reports & Analytics

### Administrative Reporting

#### System Performance Reports
1. **User Activity Analysis**
   - Login patterns and frequency
   - Feature utilization statistics
   - Performance bottleneck identification
   - User productivity metrics

2. **System Health Reports**
   - Database performance trends
   - API response time analysis
   - Error rate monitoring
   - Capacity utilization reports

#### Security Reporting
1. **Access Control Reports**
   - Failed login attempt summaries
   - Permission escalation logs
   - Unauthorized access attempts
   - Security policy compliance

2. **Data Integrity Reports**
   - Database consistency checks
   - Data validation error summaries
   - Backup verification reports
   - Data retention compliance

### Report Generation and Scheduling

#### Manual Report Generation
1. **Report Selection**
   - Choose from pre-configured report templates
   - Customize date ranges and parameters
   - Select output format (PDF, CSV, Excel)
   - Apply filters and grouping options

2. **Custom Report Creation**
   - Database query builder interface
   - Visual report designer
   - Chart and graph generation
   - Template saving for reuse

#### Automated Report Scheduling
1. **Schedule Configuration**
   - Daily, weekly, monthly schedules
   - Custom frequency options
   - Recipient email lists
   - Delivery format preferences

2. **Report Distribution**
   - Automatic email delivery
   - Secure download links
   - Access permission controls
   - Delivery confirmation tracking

## Database Management

### Database Viewer Access

#### Accessing Database Tools
1. Navigate to `#database` for database viewer interface
2. Direct access to all system tables
3. Advanced querying capabilities with safety controls

#### Database Viewer Features
- **Table Browsing**: View all database tables and structures
- **Query Builder**: Visual query construction interface
- **Data Export**: Export functionality for backup and analysis
- **Schema Visualization**: Database structure diagrams
- **Performance Monitoring**: Query performance analysis

### Data Management Operations

#### Data Integrity Maintenance
1. **Consistency Checks**
   - Automated database consistency validation
   - Foreign key constraint verification
   - Data type validation
   - Duplicate record detection

2. **Data Cleanup Operations**
   - Orphaned record removal
   - Temporary data cleanup
   - Audit log rotation
   - Performance optimization

#### Backup and Recovery
1. **Backup Management**
   - Manual backup initiation
   - Backup verification procedures
   - Restore point creation
   - Backup storage management

2. **Recovery Procedures**
   - Point-in-time recovery options
   - Selective data restoration
   - Recovery testing procedures
   - Emergency recovery protocols

### Query and Analysis Tools

#### Advanced Querying
1. **SQL Interface**
   - Direct SQL query execution
   - Query result visualization
   - Query performance analysis
   - Query history and favorites

2. **Report Queries**
   - Pre-built analytical queries
   - Business intelligence queries
   - Performance monitoring queries
   - Custom query development

## Troubleshooting

### Common Administrative Issues

#### User Access Issues
1. **Login Problems**
   - **Symptoms**: Users cannot log in despite correct credentials
   - **Diagnosis**: Check account status, password expiration, lockout status
   - **Resolution**: Reset password, unlock account, verify role permissions
   - **Prevention**: Regular password policy communication, proactive account monitoring

2. **Permission Errors**
   - **Symptoms**: Users receive "Access Denied" errors
   - **Diagnosis**: Review user role assignments, check feature permissions
   - **Resolution**: Adjust user roles, verify system configuration
   - **Prevention**: Regular permission audits, clear role documentation

3. **Session Issues**
   - **Symptoms**: Frequent session timeouts, login loops
   - **Diagnosis**: Check session configuration, browser compatibility
   - **Resolution**: Adjust session timeout settings, clear browser cache
   - **Prevention**: User education, browser compatibility testing

#### System Performance Issues

1. **Slow Response Times**
   - **Symptoms**: Pages loading slowly, API timeouts
   - **Diagnosis**: Check database performance, network connectivity
   - **Resolution**: Database optimization, server resource scaling
   - **Prevention**: Regular performance monitoring, capacity planning

2. **Database Issues**
   - **Symptoms**: Data inconsistencies, query failures
   - **Diagnosis**: Database integrity checks, log analysis
   - **Resolution**: Data repair procedures, index rebuilding
   - **Prevention**: Regular maintenance, backup verification

### System Recovery Procedures

#### Emergency Access Recovery
1. **Admin Account Lockout**
   - Use emergency admin reset script
   - Direct database access required
   - Follow security protocols for emergency access
   - Document all emergency access activities

2. **System Configuration Reset**
   - Backup current configuration before changes
   - Use configuration restore procedures
   - Verify system functionality after restoration
   - Communicate changes to affected users

#### Data Recovery Procedures
1. **Accidental Data Deletion**
   - Identify scope and timeline of deletion
   - Use soft delete recovery where available
   - Restore from backup if necessary
   - Verify data integrity after recovery

2. **System Corruption Issues**
   - Stop system services to prevent further damage
   - Assess corruption scope and impact
   - Use backup restoration procedures
   - Implement additional monitoring post-recovery

### Escalation Procedures

#### When to Escalate
- Security breaches or suspected unauthorized access
- Data corruption or loss beyond recovery capabilities  
- System-wide performance degradation
- Multiple user reports of critical functionality failures

#### Escalation Process
1. **Document the Issue**
   - Detailed problem description
   - Timeline of events
   - Steps taken to resolve
   - Impact assessment

2. **Gather Supporting Data**
   - System logs and error messages
   - Screenshots of error conditions
   - User reports and testimonies
   - Performance metrics

3. **Contact Support**
   - Use designated support channels
   - Provide all documented information
   - Maintain communication throughout resolution
   - Document resolution for future reference

## Best Practices

### User Management Best Practices

#### Account Lifecycle Management
1. **User Onboarding**
   - Create accounts with minimum required permissions
   - Implement mandatory password change on first login
   - Provide role-appropriate training materials
   - Schedule follow-up check-ins for new users

2. **Regular Account Reviews**
   - Quarterly access reviews for all users
   - Annual role appropriateness assessments
   - Immediate review for role changes
   - Documentation of all review activities

3. **Account Offboarding**
   - Immediate deactivation upon employee departure
   - Transfer of critical responsibilities before deactivation
   - Secure deletion of personal data per policy
   - Documentation of offboarding completion

#### Security Best Practices
1. **Password Management**
   - Enforce strong password policies consistently
   - Regular password expiration reminders
   - Monitor for common passwords and patterns
   - Provide password manager recommendations

2. **Access Control**
   - Principle of least privilege implementation
   - Regular permission audits and adjustments
   - Temporary access grants with expiration
   - Documentation of all access decisions

### System Maintenance Best Practices

#### Regular Maintenance Tasks
1. **Daily Tasks**
   - Review system health dashboard
   - Check overnight audit logs for issues
   - Verify backup completion status
   - Monitor user activity for anomalies

2. **Weekly Tasks**
   - Database performance optimization
   - User account status review
   - Security event analysis
   - System performance trend analysis

3. **Monthly Tasks**
   - Comprehensive security audit
   - User access right reviews
   - System configuration backup
   - Performance capacity planning

#### Change Management
1. **Configuration Changes**
   - Test all changes in development environment first
   - Document change rationale and procedures
   - Schedule changes during maintenance windows
   - Implement rollback procedures for all changes

2. **User Communication**
   - Advance notice for all system changes
   - Clear impact communication to users
   - Provide updated documentation post-changes
   - Follow up on user adaptation to changes

### Documentation and Compliance

#### Documentation Standards
1. **Administrative Procedures**
   - Maintain current procedures for all admin tasks
   - Version control for all documentation
   - Regular review and update schedules
   - User feedback integration into documentation

2. **Incident Documentation**
   - Detailed incident reports for all issues
   - Timeline documentation with evidence
   - Resolution procedures and outcomes
   - Lessons learned and prevention measures

#### Compliance Maintenance
1. **Regulatory Requirements**
   - Maintain awareness of applicable regulations
   - Regular compliance audits and assessments
   - Documentation of compliance measures
   - Staff training on compliance requirements

2. **Internal Policies**
   - Regular policy review and updates
   - Staff acknowledgment and training
   - Policy violation tracking and response
   - Continuous improvement based on feedback

---

*This guide represents comprehensive administrative procedures for the CVD system. For specific technical issues or advanced configuration requirements, consult the system documentation or contact technical support.*