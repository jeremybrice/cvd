# Authentication API Endpoints


## Metadata
- **ID**: 05_DEVELOPMENT_API_ENDPOINTS_AUTH
- **Type**: API Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #authentication #coding #data-layer #database #debugging #development #device-management #driver-app #integration #machine-learning #mobile #optimization #pwa #security #troubleshooting #vending-machine #workflows
- **Intent**: The authentication endpoints handle user login, logout, session management, and profile updates
- **Audience**: developers, system administrators, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/05-development/api/endpoints/
- **Category**: Endpoints
- **Search Keywords**: ###, ####, (401), (429), **body:**, **parameters:**, 401, account, anomaly, api, attempt, audit, authentication, automated, body:

## Overview

The authentication endpoints handle user login, logout, session management, and profile updates. All authentication uses session-based authentication with server-side session storage and automatic session cleanup.

## Security Features

- Brute force protection with IP blocking
- Account lockout after 5 failed attempts (15-minute lockout)
- Geographic anomaly detection
- Comprehensive audit logging
- CSRF protection
- Secure session configuration

---

## POST /api/auth/login

Authenticate user credentials and create a new session.

### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Parameters:**
- `username` (string, required) - Username or email address
- `password` (string, required) - User password

### Response

#### Success (200)
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  },
  "session_id": "abc123def456..."
}
```

#### Validation Error (400)
```json
{
  "error": "Username and password required"
}
```

#### Invalid Credentials (401)
```json
{
  "error": "Invalid credentials"
}
```

#### Account Locked (401)
```json
{
  "error": "Account temporarily locked"
}
```

#### Rate Limited (429)
```json
{
  "error": "Too many failed attempts. Please try again later."
}
```

### Security Behavior

1. **Brute Force Protection**: After multiple failed attempts from the same IP, requests are temporarily blocked
2. **Account Lockout**: After 5 failed login attempts, the account is locked for 15 minutes
3. **Failed Attempt Tracking**: Each failed login increments a counter that resets on successful login
4. **Geographic Anomaly Detection**: Unusual login locations trigger security alerts
5. **Audit Logging**: All login attempts (successful and failed) are logged with IP address and user agent

### Notes

- Username field accepts both username and email address
- Sessions expire after 8 hours of inactivity
- Session ID is stored in Flask session cookie
- User must be active (`is_active = 1`) to login

---

## POST /api/auth/logout

Terminate the current user session.

### Authentication Required
This endpoint requires a valid session.

### Request

**Headers:**
```
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Body:** Empty JSON object `{}`

### Response

#### Success (200)
```json
{
  "message": "Logged out successfully"
}
```

#### Authentication Required (401)
```json
{
  "error": "Authentication required"
}
```

### Behavior

1. Removes session from server-side database
2. Clears Flask session cookie
3. Logs logout event to audit trail

---

## GET /api/auth/current-user

Get information about the currently authenticated user.

### Authentication Required
This endpoint requires a valid session.

### Request

**Headers:**
```
Cookie: session=<session_cookie>
```

### Response

#### Success (200)
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "created_at": "2024-01-01T10:00:00Z",
    "last_login": "2024-01-02T09:30:00Z"
  }
}
```

#### Authentication Required (401)
```json
{
  "error": "Authentication required"
}
```

#### Invalid Session (401)
```json
{
  "error": "Invalid or expired session"
}
```

### Notes

- Returns user information from both session data and database
- Includes account creation date and last login timestamp
- Used by frontend to verify session validity and display user info

---

## POST /api/auth/change-password

Change the current user's password.

### Authentication Required
This endpoint requires a valid session.

### Request

**Headers:**
```
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Body:**
```json
{
  "currentPassword": "oldpassword123",
  "newPassword": "newpassword456"
}
```

**Parameters:**
- `currentPassword` (string, required) - Current password for verification
- `newPassword` (string, required) - New password (minimum 8 characters)

### Response

#### Success (200)
```json
{
  "message": "Password changed successfully"
}
```

#### Validation Error (400)
```json
{
  "error": "Current and new password required"
}
```

```json
{
  "error": "Password must be at least 8 characters"
}
```

#### Invalid Current Password (401)
```json
{
  "error": "Current password incorrect"
}
```

#### Authentication Required (401)
```json
{
  "error": "Authentication required"
}
```

### Security Behavior

1. **Current Password Verification**: Requires current password to authorize change
2. **Password Strength**: Minimum 8 character requirement
3. **Secure Hashing**: Uses Werkzeug's secure password hashing
4. **Audit Logging**: Password changes are logged to audit trail
5. **Session Preservation**: User remains logged in after password change

---

## PUT /api/auth/update-profile

Update the current user's profile information.

### Authentication Required
This endpoint requires a valid session.

### Request

**Headers:**
```
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Body:**
```json
{
  "email": "newemail@example.com"
}
```

**Parameters:**
- `email` (string, required) - New email address

### Response

#### Success (200)
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "newemail@example.com",
    "role": "admin"
  }
}
```

#### Validation Error (400)
```json
{
  "error": "Email is required"
}
```

```json
{
  "error": "Invalid email format"
}
```

```json
{
  "error": "Email already in use"
}
```

#### Authentication Required (401)
```json
{
  "error": "Authentication required"
}
```

### Validation Rules

1. **Email Format**: Must be valid email format (regex validation)
2. **Email Uniqueness**: Email must not be used by another user
3. **Required Field**: Email is required (cannot be empty)

### Notes

- Currently only supports email updates
- Email must be unique across all users
- Updates are logged to audit trail
- Returns updated user object

---

## GET /api/auth/activity

Get the current user's recent authentication activity.

### Authentication Required
This endpoint requires a valid session.

### Request

**Headers:**
```
Cookie: session=<session_cookie>
```

### Response

#### Success (200)
```json
{
  "activities": [
    {
      "action": "LOGIN",
      "ip_address": "192.168.1.100",
      "created_at": "2024-01-02T09:30:00Z",
      "details": "Successful login"
    },
    {
      "action": "LOGOUT",
      "ip_address": "192.168.1.100",
      "created_at": "2024-01-01T17:00:00Z",
      "details": "User logged out"
    }
  ]
}
```

#### Authentication Required (401)
```json
{
  "error": "Authentication required"
}
```

### Notes

- Returns last 10 authentication events for the current user
- Includes login successes, failures, and logouts
- Shows IP address and timestamp for each event
- Used for user security awareness and account monitoring

---

## Session Management

### Session Configuration

- **Expiration**: 8 hours from creation
- **Storage**: Server-side database storage with session ID in cookie
- **Security**: Secure, HTTP-only, SameSite cookies
- **Cleanup**: Automated cleanup of expired sessions

### Session Validation

All protected endpoints automatically validate sessions:

1. Check for session ID in Flask session
2. Verify session exists in database and hasn't expired
3. Confirm associated user is active and not deleted
4. Populate `g.user` object with user information

### Device Detection

Sessions track device type based on User-Agent:
- `mobile` - Mobile devices
- `tablet` - Tablet devices  
- `desktop` - Desktop browsers
- `bot` - Automated tools
- `unknown` - Unidentified agents

---

## Error Handling

### Common Error Responses

All authentication endpoints may return these common errors:

#### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

#### 401 Invalid Session
```json
{
  "error": "Invalid or expired session"
}
```

#### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

### Security Error Responses

#### Rate Limiting
```json
{
  "error": "Too many failed attempts. Please try again later."
}
```

#### Account Security
```json
{
  "error": "Account temporarily locked"
}
```

```json
{
  "error": "Account has been deactivated"
}
```

---

## Integration Examples

### Frontend Login Flow

```javascript
// Login request
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'password123'
  })
});

const data = await response.json();

if (response.ok) {
  // Session cookie is automatically set
  console.log('Logged in as:', data.user.username);
  // Redirect to dashboard
} else {
  console.error('Login failed:', data.error);
}
```

### Session Validation

```javascript
// Check current user
const response = await fetch('/api/auth/current-user');

if (response.ok) {
  const data = await response.json();
  console.log('Current user:', data.user);
} else {
  // Redirect to login
  window.location.href = '/login.html';
}
```

### Logout

```javascript
// Logout request
const response = await fetch('/api/auth/logout', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: '{}'
});

if (response.ok) {
  // Redirect to login page
  window.location.href = '/login.html';
}
```