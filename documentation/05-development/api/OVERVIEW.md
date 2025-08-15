# CVD API Overview


## Metadata
- **ID**: 05_DEVELOPMENT_API_OVERVIEW
- **Type**: API Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #coding #data-exchange #data-layer #database #debugging #development #device-management #dex-parser #driver-app #integration #logistics #machine-learning #metrics #mobile #operations #optimization #performance #planogram #product-placement #pwa #quality-assurance #reporting #route-management #security #service-orders #testing #troubleshooting #vending-machine #workflows
- **Intent**: ## Introduction
- **Audience**: developers, system administrators, managers, end users, architects
- **Related**: auth.md, devices.md, service-orders.md
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/05-development/api/
- **Category**: Api
- **Search Keywords**: ###, ####, /api/health, 200, 201, 400, 401, 403, 404, 500, admin, all, api, authentication, authorization

## Introduction

The CVD (Vision Device Configuration) system provides a comprehensive REST API for managing vending machine fleet operations. The API follows RESTful principles and provides endpoints for authentication, device management, service orders, planogram configuration, and analytics.

## Base URL and Structure

```
Base URL: http://localhost:5000/api
```

All API endpoints use the `/api` prefix and follow consistent RESTful patterns:

- **GET** - Retrieve resources
- **POST** - Create new resources
- **PUT** - Update existing resources
- **DELETE** - Remove resources (often soft delete)

## Authentication

### Session-Based Authentication

The CVD API uses session-based authentication with the following flow:

1. **Login**: `POST /api/auth/login` with credentials
2. **Session Validation**: Automatic session validation on protected endpoints
3. **Logout**: `POST /api/auth/logout` to terminate session

### Session Management

- Sessions expire after 8 hours of inactivity
- Session IDs are stored in Flask sessions and server-side database
- Expired sessions are automatically cleaned up
- Device type detection (mobile/desktop/tablet) for session tracking

### Authorization Levels

The system implements role-based access control with four user roles:

1. **Admin** - Full system access including user management
2. **Manager** - Device and planogram management, reports
3. **Driver** - Service order execution, limited device access
4. **Viewer** - Read-only access to most resources

## Request/Response Format

### Content Type

All requests and responses use JSON format:

```
Content-Type: application/json
```

### Request Format

```json
{
  "field1": "value1",
  "field2": "value2"
}
```

### Response Format

#### Success Response

```json
{
  "data": { /* resource data */ },
  "message": "Success message (optional)"
}
```

#### Error Response

```json
{
  "error": "Error description",
  "code": "ERROR_CODE (optional)",
  "details": { /* additional error details (optional) */ }
}
```

### HTTP Status Codes

The API uses standard HTTP status codes:

- **200** - Success
- **201** - Created
- **400** - Bad Request (validation errors)
- **401** - Unauthorized (authentication required)
- **403** - Forbidden (insufficient permissions)
- **404** - Not Found
- **500** - Internal Server Error

## Common Response Patterns

### Pagination

For list endpoints that return multiple items:

```json
{
  "data": [/* array of items */],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 150,
    "pages": 3
  }
}
```

### Filtering and Search

Many endpoints support query parameters for filtering:

```
GET /api/devices?search=term&status=active&route_id=1
```

### Soft Delete Pattern

Resources that support soft delete return deleted items with metadata:

```json
{
  "id": 1,
  "name": "Resource Name",
  "is_deleted": true,
  "deleted_at": "2024-01-01T12:00:00Z",
  "deleted_by": 1
}
```

## Error Handling Patterns

### Validation Errors

Field validation errors return detailed information:

```json
{
  "error": "Validation failed",
  "details": {
    "field_name": ["Field is required", "Field must be unique"]
  }
}
```

### Authentication Errors

```json
{
  "error": "Authentication required"
}
```

```json
{
  "error": "Invalid or expired session"
}
```

### Authorization Errors

```json
{
  "error": "Insufficient permissions"
}
```

### Resource Not Found

```json
{
  "error": "Resource not found",
  "resource_type": "device",
  "resource_id": 123
}
```

## Rate Limiting and Security

### Security Headers

All API responses include security headers:

- CORS enabled for frontend domain
- CSRF protection for state-changing operations
- Secure session cookie configuration

### Input Validation

- All inputs are validated and sanitized
- SQL injection protection through parameterized queries
- XSS prevention through output encoding

### Audit Logging

Critical operations are logged to the audit trail:

- User authentication events
- Resource modifications
- Permission violations
- Administrative actions

### Activity Monitoring

The system tracks user activity for security and analytics:

- Session creation and termination
- API endpoint access patterns
- Failed authentication attempts
- Suspicious activity detection

## API Categories

### Authentication (`/api/auth/*`)
- User login/logout
- Session management
- Profile updates
- Password changes

### Device Management (`/api/devices/*`)
- Device CRUD operations
- Cabinet configurations
- Device metrics and service history
- Bulk operations

### Service Orders (`/api/service-orders/*`)
- Order lifecycle management
- Pick list generation
- Cabinet-centric execution
- Photo uploads and documentation

### Planogram Management (`/api/planograms/*`)
- Planogram configuration
- AI-powered optimization
- Real-time scoring
- Revenue prediction

### Analytics and Reports (`/api/sales/*`, `/api/metrics/*`)
- Sales data and reporting
- Performance metrics
- Timeline analytics
- Achievement tracking

### User Management (`/api/users/*`)
- User CRUD operations (admin only)
- Role assignment
- Activity tracking
- Soft delete functionality

### Location and Route Management
- Location management (`/api/locations/*`)
- Route configuration (`/api/routes/*`)
- Geocoding services (`/api/geocode`)

### DEX Parser (`/api/dex/*`)
- DEX file processing
- Grid pattern analysis
- Multi-manufacturer support
- Historical data retrieval

### Knowledge Base (`/api/knowledge-base/*`)
- Article management
- Search functionality
- Category organization
- Usage statistics

### AI Services (`/api/chat`, `/api/planograms/ai-*`)
- Interactive chat assistance
- Planogram optimization suggestions
- Real-time scoring
- Predictive analytics

## Integration Patterns

### Frontend Integration

The API is designed to work with the iframe-based frontend architecture:

- Cross-frame communication support
- Progressive Web App compatibility
- Offline-first patterns for mobile driver app

### Database Integration

- SQLite primary database with potential PostgreSQL migration support
- Row-level security for multi-tenant data isolation
- Optimized queries with proper indexing
- Connection pooling and transaction management

### External Service Integration

- Anthropic Claude API for AI features (optional)
- Push notification services for driver app
- Geocoding services for location management
- Email services for notifications

## Performance Considerations

### Caching Strategy

- Database query optimization
- Session caching
- Static asset caching
- API response caching for read-heavy endpoints

### Database Optimization

- Proper indexing on frequently queried columns
- Pagination for large result sets
- Bulk operations for efficiency
- Connection reuse and pooling

### Mobile Optimization

- Lightweight responses for mobile driver app
- Offline data synchronization
- Background sync capabilities
- Efficient binary data handling for photos

## API Versioning

Currently, the API is unversioned but follows these stability principles:

- Additive changes (new fields, endpoints) are backwards compatible
- Breaking changes would require version negotiation
- Deprecation notices for removed functionality
- Migration guides for major changes

## Development and Testing

### Local Development

```bash
# Start the Flask development server
python app.py

# API available at http://localhost:5000/api
```

### Testing Endpoints

Health check endpoint for service monitoring:

```
GET /api/health
```

### Documentation Standards

- All endpoints documented with request/response examples
- Error scenarios covered
- Authentication requirements specified
- Role-based access restrictions noted

## API Reference Structure

The complete API reference is organized into the following sections:

1. **[Authentication Endpoints](endpoints/auth.md)** - Login, logout, session management
2. **[Device Management Endpoints](endpoints/devices.md)** - Device CRUD and configuration
3. **[Service Order Endpoints](endpoints/service-orders.md)** - Order lifecycle and execution
4. **[Additional Endpoints](endpoints/)** - Full endpoint catalog by category

For detailed endpoint documentation, refer to the specific endpoint documentation files in the `endpoints/` directory.