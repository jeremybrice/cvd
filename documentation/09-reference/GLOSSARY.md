# CVD System Glossary


## Metadata
- **ID**: 09_REFERENCE_GLOSSARY
- **Type**: Reference
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #data-exchange #data-layer #database #debugging #deployment #device-management #devops #dex-parser #documentation #driver-app #integration #logistics #machine-learning #metrics #mobile #operations #optimization #performance #planogram #product-placement #pwa #quality-assurance #reference #reporting #route-management #security #service-orders #testing #troubleshooting #vending-machine
- **Intent**: This glossary provides comprehensive definitions for all terminology used in the CVD (Vision Device Configuration) system
- **Audience**: system administrators, managers, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/09-reference/
- **Category**: 09 Reference
- **Search Keywords**: (data, (pwa), .db, .html, .js, .md, .py, /api/auth/current-user, /api/auth/login, /api/auth/logout, /api/devices, /api/devices/{id}, /api/metrics/calculate, /api/metrics/weekly, /api/planograms

## Purpose
This glossary provides comprehensive definitions for all terminology used in the CVD (Vision Device Configuration) system. Terms are organized alphabetically with context and cross-references to support both human users and AI agents.

## Usage
- **Bold terms** indicate primary entries
- *Italic terms* indicate cross-references to other entries
- Terms marked with `[CVD]` are system-specific
- Terms marked with `[VENDING]` are industry-specific
- Terms marked with `[TECH]` are technical/development terms

---

## A

**Activity Tracker** `[CVD]` `[TECH]`
System component that monitors user actions, request patterns, and system performance metrics for security and analytics purposes. See also: *Security Monitor*, *Audit Logging*.

**Admin Role** `[CVD]`
Highest privilege user role with access to all system functions including user management, system configuration, and administrative controls. See also: *Role-Based Access Control*, *User Roles*.

**API (Application Programming Interface)** `[TECH]`
RESTful interface providing programmatic access to CVD system functionality. Implemented using Flask with JSON request/response format.

**API Client** `[CVD]` `[TECH]`
Frontend JavaScript class (CVDApi) that handles all communication with the backend API, including authentication, error handling, and retry logic.

**Asset Sales** `[CVD]` `[VENDING]`
Analytics feature tracking financial performance and transaction data for individual vending machines. Provides device-level revenue analysis.

**Audit Logging** `[CVD]` `[TECH]`
Comprehensive logging system that records all user actions, system events, and security-related activities for compliance and security monitoring.

**Authentication** `[TECH]`
Process of verifying user identity using username/password credentials with session-based management and secure password hashing.

**Authorization** `[TECH]`
Process of determining user permissions and access rights based on assigned roles. Implemented through *Role-Based Access Control*.

## B

**Backend** `[TECH]`
Server-side component built with Flask framework, handling API requests, database operations, and business logic. Runs on Python with SQLite database.

**Bulk Operations** `[CVD]`
System capability to perform mass updates or modifications across multiple devices, products, or planograms simultaneously.

## C

**Cabinet** `[VENDING]`
Individual refrigerated unit within a vending machine. CVD supports multi-cabinet devices (up to 3 cabinets per device). Each cabinet has specific temperature settings and product configurations.

**Cabinet Configuration** `[CVD]` `[VENDING]`
Database table and UI screens for defining cabinet specifications including dimensions, temperature zones, door types, and slot arrangements.

**Cabinet Type** `[CVD]` `[VENDING]`
Classification system for different cabinet models (e.g., Glass Front, Solid Door, Multi-Temperature). Used for configuration templates and compatibility checking.

**Cache** `[TECH]`
Temporary storage mechanism used for address geocoding, map tiles, and other performance optimizations. No planogram caching implemented by design.

**Chat Assistant** `[CVD]` `[AI]`
AI-powered help system using knowledge base and Claude API to provide context-aware assistance for current page operations.

**Company Settings** `[CVD]`
System configuration page for organization-wide settings including branding, default values, and operational parameters.

**CORS (Cross-Origin Resource Sharing)** `[TECH]`
Security feature configured to allow frontend-backend communication across different ports (8000 for frontend, 5000 for backend).

**CVD (Vision Device Configuration)** `[CVD]`
The complete enterprise vending machine fleet management system. Acronym for the system name.

**CVDApi** `[CVD]` `[TECH]`
JavaScript class providing centralized API communication with built-in error handling, authentication, and retry logic. Used by all frontend pages.

## D

**Database Schema** `[TECH]`
SQLite database structure defining tables, relationships, and constraints. Includes core entities: devices, products, planograms, users, and service orders.

**Data Retention** `[CVD]` `[TECH]`
Automated system for managing historical data lifecycle, including archival and cleanup of old records based on configurable policies.

**DEX (Data Exchange)** `[VENDING]` `[TECH]`
Industry-standard protocol for vending machine data communication. CVD supports 40+ DEX record types for comprehensive machine data processing.

**DEX Parser** `[CVD]` `[TECH]`
System component that processes DEX files, extracting transaction data, machine status, and operational metrics. Includes grid pattern detection.

**Device** `[CVD]` `[VENDING]`
Complete vending machine unit that may contain multiple cabinets. Core entity in CVD system with unique identification and configuration management.

**Device Management** `[CVD]`
System functionality for configuring, monitoring, and maintaining vending machine inventory including locations, routes, and operational status.

**Device Metrics** `[CVD]` `[ANALYTICS]`
Performance tracking data for individual devices including sales volumes, uptime, temperature monitoring, and service history.

**Device Type** `[CVD]` `[VENDING]`
Classification system for different vending machine models and manufacturers. Used for configuration templates and compatibility.

**Driver App** `[CVD]` `[PWA]`
Progressive Web App designed for mobile field operations. Provides offline capability, route management, and service order execution for drivers.

**Driver Role** `[CVD]`
User role specifically for field service personnel with access to mobile app, service orders, and route information but limited administrative functions.

## E

**Emergency Procedures** `[CVD]` `[OPERATIONS]`
Defined protocols for system outages, security incidents, and critical failures. Documented in runbooks and cheat sheets.

**Error Handling** `[TECH]`
Comprehensive error management including user-friendly messages, logging, and graceful degradation for system reliability.

## F

**Flask** `[TECH]`
Python web framework used for CVD backend implementation. Provides routing, request handling, and extension ecosystem.

**Frontend** `[TECH]`
Client-side interface built with vanilla HTML, CSS, and JavaScript using iframe-based architecture for modularity and maintenance.

## G

**Geocoding** `[CVD]` `[TECH]`
Process of converting addresses to geographic coordinates for mapping functionality. Results are cached for performance optimization.

**Grid Pattern** `[CVD]` `[VENDING]`
Physical arrangement of product slots within a cabinet. CVD detects 5 different grid pattern types for optimal planogram configuration.

**Grid Pattern Analyzer** `[CVD]` `[TECH]`
System component that analyzes DEX data to automatically detect and classify cabinet slot arrangements for accurate planogram mapping.

## H

**Hash Navigation** `[TECH]`
URL routing mechanism using fragment identifiers (hash) for single-page application navigation between iframe content.

**HTTP Server** `[TECH]`
Simple Python HTTP server used for frontend development and deployment. Serves static files on port 8000.

## I

**Iframe Architecture** `[CVD]` `[TECH]`
Design pattern using embedded frames for modular page loading. Eliminates build dependencies while maintaining component separation.

**IndexedDB** `[PWA]` `[TECH]`
Browser-based storage system used by Driver App for offline functionality and data synchronization.

**INVD** `[CVD]`
Page code for device configuration interface. Handles device creation and cabinet configuration.

## J

**JSON (JavaScript Object Notation)** `[TECH]`
Data format used for all API communication between frontend and backend components.

## K

**Knowledge Base** `[CVD]` `[AI]`
Structured information repository used by chat assistant to provide context-specific help and documentation.

## L

**Location** `[CVD]` `[VENDING]`
Physical site where devices are installed. Includes address, contact information, and operational details for route planning.

**Login** `[CVD]` `[AUTH]`
Authentication process requiring username and password. Default system credentials are admin/admin.

## M

**Manager Role** `[CVD]`
Mid-level user role with access to operational features including planograms, service orders, and analytics but limited administrative functions.

**Mapping** `[CVD]` `[GIS]`
Geographic visualization using Leaflet.js for route planning, device locations, and service territory management.

**Migration** `[TECH]`
Database schema update scripts for adding new features or modifying existing structures while preserving data integrity.

**Model Name** `[CVD]` `[VENDING]`
Specific cabinet model identifier used in configuration. Note: Use modelName not cabinetType for consistency.

## N

**Navigation** `[CVD]` `[UX]`
System routing and menu structure using hash-based URLs and iframe content loading for seamless user experience.

**NSPT** `[CVD]`
Page code for planogram management interface. Handles product placement and AI optimization features.

## O

**Offline Support** `[PWA]`
Driver App capability to function without internet connectivity using cached data and background synchronization.

**Optimization** `[CVD]` `[AI]`
AI-powered feature for suggesting optimal product placement in planograms based on sales data and machine learning algorithms.

## P

**Par Level** `[CVD]` `[VENDING]`
Target inventory quantity for each product slot. Used for automatic restock calculations and service order generation.

**PCP** `[CVD]`
Page code for device listing and management interface. Primary view for device inventory and status monitoring.

**Pick List** `[CVD]` `[OPERATIONS]`
Generated report showing products and quantities needed for specific service orders, organized by cabinet and location.

**Planogram** `[CVD]` `[VENDING]`
Visual representation of product placement within vending machine cabinets. Defines which products go in which slots with quantities.

**Planogram Optimizer** `[CVD]` `[AI]`
AI component that analyzes sales data to recommend optimal product placement strategies for improved performance.

**Planogram Slot** `[CVD]` `[VENDING]`
Individual product position within a planogram. Contains product assignment, quantity, and par level information.

**Product** `[CVD]` `[VENDING]`
Individual items sold through vending machines. CVD includes 12 system-defined products with standardized pricing and categories.

**Product Sales** `[CVD]` `[ANALYTICS]`
Analytics feature tracking performance of individual products across the entire fleet for inventory and purchasing decisions.

**Progressive Web App (PWA)** `[TECH]`
Web application technology enabling native app-like features including offline support, push notifications, and device integration.

**Push Notifications** `[PWA]`
Mobile alert system for Driver App to notify field personnel of new service orders and system updates.

## Q

**Quality Assurance** `[TECH]`
Testing and validation processes ensuring system reliability, security, and performance standards.

## R

**RBAC (Role-Based Access Control)** `[TECH]` `[SECURITY]`
Security model controlling user permissions based on assigned roles (Admin, Manager, Driver, Viewer).

**REST API** `[TECH]`
Representational State Transfer architecture used for backend API endpoints with standard HTTP methods and JSON responses.

**Route** `[CVD]` `[OPERATIONS]`
Defined path for service personnel covering multiple device locations. Used for scheduling and optimization of field operations.

**Route Management** `[CVD]`
System functionality for planning, tracking, and optimizing service routes using interactive mapping and address geocoding.

## S

**Sales Data** `[CVD]` `[ANALYTICS]`
Transaction records from vending machines including timestamps, products, quantities, and revenue for performance analysis.

**Security Monitor** `[CVD]` `[SECURITY]`
System component tracking privilege escalation attempts, unauthorized access, and suspicious activity patterns.

**Service Order** `[CVD]` `[OPERATIONS]`
Work order generated for device maintenance, restocking, or repairs. Contains cabinet-specific tasks and product requirements.

**Service Visit** `[CVD]` `[OPERATIONS]`
Completed service order record including photos, notes, and verification of work performed by field personnel.

**Session Management** `[TECH]` `[SECURITY]`
User authentication system maintaining secure login state with automatic timeout and session validation.

**Slot** `[CVD]` `[VENDING]`
Individual product position within a vending machine cabinet. Physical location where products are stored and dispensed.

**Soft Delete** `[CVD]` `[TECH]`
Data management strategy marking records as deleted without physical removal, enabling recovery and audit trail maintenance.

**SQLite** `[TECH]`
Embedded database engine used for CVD data storage. File-based database requiring no separate server installation.

## T

**Temperature Monitoring** `[CVD]` `[VENDING]`
System capability to track and alert on cabinet temperature variations for product quality and compliance.

**Testing** `[TECH]`
Comprehensive test suite including unit tests, integration tests, and frontend validation for system reliability.

**Two-Way Selection Sync** `[CVD]` `[UX]`
UI pattern where selections in lists automatically update corresponding map markers and vice versa for improved usability.

## U

**User Management** `[CVD]` `[ADMIN]`
Administrative functionality for creating, modifying, and managing user accounts with role assignments and permissions.

**User Roles** `[CVD]` `[SECURITY]`
Four-tier access control system: Admin (full access), Manager (operational), Driver (field), Viewer (read-only).

## V

**Vending Machine** `[VENDING]`
Automated retail device dispensing products. Primary asset managed by CVD system with comprehensive configuration and monitoring.

**Viewer Role** `[CVD]`
Read-only user role with access to reports and analytics but no modification capabilities.

## W

**Web Push** `[PWA]`
Notification system enabling server-to-browser messaging for Driver App alerts and system notifications.

**Werkzeug** `[TECH]`
Python WSGI utility library used by Flask for security functions including password hashing and request handling.

## Configuration Terms

**ANTHROPIC_API_KEY** `[CONFIG]`
Environment variable for AI assistant functionality. Optional - system falls back to rule-based help if not configured.

**CORS Origins** `[CONFIG]`
Allowed frontend domains for API access: localhost:8000, 127.0.0.1:8000, and production domains.

**DATABASE** `[CONFIG]`
SQLite database filename (cvd.db) containing all system data.

**SECRET_KEY** `[CONFIG]`
Flask session encryption key. Auto-generated if not provided via SESSION_SECRET environment variable.

**SESSION_COOKIE_SECURE** `[CONFIG]`
HTTPS-only cookie setting enabled in production environments for enhanced security.

## Database Tables

**audit_log** `[DB]`
Records all user actions and system events for security monitoring and compliance tracking.

**cabinet_configurations** `[DB]`
Stores cabinet specifications including dimensions, types, and slot arrangements.

**cabinet_types** `[DB]`
Reference table for cabinet model definitions and specifications.

**device_metrics** `[DB]`
Performance and operational data for individual devices including uptime and transaction volumes.

**device_types** `[DB]`
Reference table for vending machine model classifications and specifications.

**devices** `[DB]`
Core device registry with location, status, and configuration information.

**dex_pa_records** `[DB]`
DEX transaction data with grid pattern analysis results.

**dex_reads** `[DB]`
Raw DEX file processing records with metadata and parsing results.

**locations** `[DB]`
Site information including addresses, contacts, and operational details.

**planogram_slots** `[DB]`
Individual slot configurations within planograms including product assignments and quantities.

**planograms** `[DB]`
Product placement configurations for device cabinets with AI optimization support.

**products** `[DB]`
Product catalog with 12 system-defined items including pricing and category information.

**routes** `[DB]`
Service route definitions for field operations and scheduling.

**sales** `[DB]`
Transaction records from vending machines for analytics and reporting.

**service_order_cabinet_items** `[DB]`
Product requirements for individual cabinet service tasks.

**service_order_cabinets** `[DB]`
Cabinet-specific tasks within service orders including status and completion tracking.

**service_orders** `[DB]`
Work order headers with scheduling, assignment, and completion information.

**service_visits** `[DB]`
Completed service records with photos, notes, and verification data.

**sessions** `[DB]`
Active user session tracking for authentication and security monitoring.

**users** `[DB]`
User account information with roles, credentials, and profile data.

## API Endpoints

**Authentication Endpoints**
- `POST /api/auth/login` - User authentication
- `GET /api/auth/current-user` - Session validation
- `POST /api/auth/logout` - Session termination

**Device Management Endpoints**
- `GET /api/devices` - Device listing
- `POST /api/devices` - Device creation
- `PUT /api/devices/{id}` - Device updates
- `DELETE /api/devices/{id}` - Device deletion (soft delete)

**Planogram Management Endpoints**
- `GET /api/planograms` - Planogram listing
- `POST /api/planograms` - Planogram creation
- `PUT /api/planograms/{id}` - Planogram updates
- `POST /api/planograms/optimize` - AI optimization

**Service Order Endpoints**
- `GET /api/service-orders` - Order listing
- `POST /api/service-orders` - Order creation
- `GET /api/service-orders/{id}/pick-list` - Pick list generation
- `POST /api/service-orders/execute` - Order completion

**Analytics Endpoints**
- `POST /api/metrics/calculate` - Metric calculation
- `GET /api/metrics/weekly` - Weekly performance data
- `GET /api/metrics/top-performers` - Top performing devices

## File Extensions and Types

**.html** `[FRONTEND]`
Static web pages for user interface components and forms.

**.js** `[FRONTEND]`
JavaScript files for client-side logic and API communication.

**.py** `[BACKEND]`
Python source files for server logic and business rules.

**.db** `[DATABASE]`
SQLite database file containing all system data.

**.md** `[DOCS]`
Markdown documentation files for system reference and guides.

## Status Values

**Device Status**
- Active: Operational and in service
- Inactive: Temporarily out of service
- Maintenance: Under repair or servicing

**Service Order Status**
- Pending: Created but not assigned
- Assigned: Assigned to driver
- In Progress: Being executed
- Completed: Successfully finished
- Cancelled: Cancelled or aborted

**User Status**
- Active: Normal operational status
- Inactive: Temporarily disabled
- Locked: Security locked due to violations

## Common Abbreviations

**API** - Application Programming Interface
**CORS** - Cross-Origin Resource Sharing
**CSS** - Cascading Style Sheets
**CVD** - Vision Device Configuration
**DB** - Database
**DEX** - Data Exchange
**HTML** - HyperText Markup Language
**HTTP** - HyperText Transfer Protocol
**HTTPS** - HTTP Secure
**JS** - JavaScript
**JSON** - JavaScript Object Notation
**PWA** - Progressive Web App
**RBAC** - Role-Based Access Control
**REST** - Representational State Transfer
**SQL** - Structured Query Language
**UI** - User Interface
**URL** - Uniform Resource Locator
**UX** - User Experience

## Cross-References

For additional information, see:
- **System Architecture**: `/documentation/03-architecture/system/OVERVIEW.md`
- **Database Schema**: `/documentation/03-architecture/system/DATABASE_SCHEMA.md`
- **API Documentation**: `/documentation/05-development/api/OVERVIEW.md`
- **User Guides**: `/documentation/02-requirements/guides/`
- **Development Setup**: `/documentation/05-development/SETUP_GUIDE.md`

---

*This glossary is maintained as part of the CVD documentation suite. For updates or additions, see the documentation standards guide.*