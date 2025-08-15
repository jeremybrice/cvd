---
type: architecture
category: system
title: CVD Application Architecture Overview
status: active
last_updated: 2025-08-12
tags: [architecture, flask, nginx, deployment]
cross_references:
  - /documentation/03-architecture/patterns/API_PATTERNS.md
  - /documentation/05-development/deployment/GUIDE.md
  - /documentation/03-architecture/SECURITY.md
---

# CVD Application Architecture

## Overview

The CVD (Vision Device Configuration) application uses a multi-server architecture with Flask backend, static frontend, and nginx reverse proxy for production deployment.

## Architecture Components

### 1. Frontend (Static Files)
- **Technology**: Pure HTML/CSS/JavaScript (no build process)
- **Location**: `/home/jbrice/Projects/365/`
- **Key Files**:
  - `index.html` - Main navigation shell and iframe router
  - `pages/*.html` - Individual application pages
  - `api.js` - Centralized API client module
- **Server**: Python HTTP server (`python -m http.server 8000`)
- **Port**: 8000
- **Limitations**: Can only serve static files, cannot handle API requests

### 2. Backend API (Flask)
- **Technology**: Flask with SQLite database
- **Location**: `/home/jbrice/Projects/365/app.py`
- **Database**: `cvd.db` (SQLite)
- **Port**: 5000
- **Features**:
  - RESTful API endpoints
  - Session-based authentication
  - CORS support for cross-origin requests
  - Role-based access control (RBAC)

### 3. Reverse Proxy (Nginx)
- **Purpose**: Routes requests between frontend and backend
- **Domain**: https://jeremybrice.duckdns.org
- **Configuration**:
  - Routes `/api/*` requests to Flask backend (port 5000)
  - Serves static files for all other requests
  - Handles SSL termination
  - Manages CORS headers

## Access Patterns

### Production Access (Recommended)
```
User Browser → https://jeremybrice.duckdns.org → Nginx → 
  ├── /api/* → Flask (localhost:5000)
  └── /* → Static files
```

### Local Development Options

#### Option 1: Direct Flask Access
```
User Browser → http://localhost:5000 → Flask (serves both API and static files)
```

#### Option 2: Split Server Access (Problematic)
```
User Browser → http://localhost:8000 → Python HTTP Server (static only)
                        ↓
                  API calls fail (501 errors)
```

## Authentication Architecture

### Session Management
- **Type**: Server-side sessions with secure cookies
- **Storage**: SQLite database (`sessions` table)
- **Cookie Name**: `session`
- **Expiration**: 8 hours
- **Security**: 
  - HttpOnly cookies
  - Secure flag in production
  - CORS credentials required

### User Roles
1. **Admin**: Full system access
2. **Manager**: Device and route management
3. **Driver**: View-only with route assignments
4. **Viewer**: Read-only access

### Authentication Flow
1. User submits credentials to `/api/auth/login`
2. Backend validates credentials against `users` table
3. Creates session in `sessions` table
4. Returns session cookie to browser
5. Subsequent requests include session cookie
6. Backend validates session on each request

## Database Schema

### Key Tables
- `users` - User accounts and authentication
- `sessions` - Active user sessions
- `audit_log` - Security audit trail
- `devices` - Vending machine devices
- `cabinet_configurations` - Device cabinet details
- `products` - Product catalog
- `planograms` - Device layout configurations
- `locations` - Device locations
- `routes` - Service routes
- `sales` - Sales transaction data

## API Structure

### Base URL
- Production: `https://jeremybrice.duckdns.org/api`
- Local Flask: `http://localhost:5000/api`

### Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/current-user` - Get current user info

### Protected Endpoints
All other endpoints require authentication via session cookie.

## Known Issues

### Local Development Limitations
When accessing via `http://localhost:8000`:
- API calls fail with 501 "Unsupported method" errors
- Python HTTP server cannot proxy to Flask backend
- Authentication doesn't work properly

### Cookie Domain Mismatches
- Cookies set for `localhost` won't work with `127.0.0.1`
- Must use consistent domain throughout session

## Deployment Commands

### Start Flask Backend
```bash
source venv/bin/activate
export ANTHROPIC_API_KEY="your-key-here"  # For AI chat bot
python app.py
```

### Start Static File Server (Optional for local dev)
```bash
python -m http.server 8000
```

### Access Points
- Production: https://jeremybrice.duckdns.org
- Local Flask: http://localhost:5000
- Local Static (limited): http://localhost:8000

## Security Considerations

### CORS Configuration
```python
CORS(app, origins=[
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://jeremybrice.duckdns.org'
], supports_credentials=True)
```

### Session Security
- Random 32-character session IDs
- Server-side session storage
- IP address validation
- User agent tracking
- Automatic expiration

### Audit Logging
All authentication events and sensitive operations are logged to `audit_log` table for compliance and security monitoring.
