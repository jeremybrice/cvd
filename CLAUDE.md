# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the CVD application.

## Application Overview

CVD (Vision Device Configuration) is an enterprise vending machine fleet management system with:
- Flask/SQLite backend with role-based authentication
- Modular iframe-based frontend (no build dependencies)
- Progressive Web App for mobile driver operations
- AI-powered planogram optimization and chat assistant
- Real-time analytics and service order management

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure AI (optional)
export ANTHROPIC_API_KEY="your-key-here"

# Run Application
# Terminal 1: Backend
python app.py

# Terminal 2: Frontend
python -m http.server 8000

# Access: http://localhost:8000/
# Default login: admin/admin
```

## Architecture Overview

### Core Components
- `app.py` - Flask backend with authentication & REST API
- `index.html` - Main navigation shell (iframe router)
- `api.js` - Frontend API client with retry logic
- `auth.py` - Authentication module with role-based access
- `service_order_service.py` - Service order management
- `dex_parser.py` + `grid_pattern_analyzer.py` - DEX file processing
- `planogram_optimizer.py` - AI-powered optimization
- `knowledge_base.py` - Chat assistant knowledge

### File Organization
See `/documentation/03-architecture/system/FILE_STRUCTURE_GUIDE.md` for complete directory structure.

Key locations:
- Frontend pages: `/pages/`
- Driver PWA: `/pages/driver-app/`
- **Documentation (NEW)**: `/documentation/` - Comprehensive structured documentation system
- Legacy docs: `/docs/` (migrated to `/documentation/`)
- Tests: `/tests/`
- Tools: `/tools/`

### 📚 Documentation System Guide

The CVD project now has a comprehensive documentation system at `/documentation/`:

**Quick Navigation**:
- **Master Index**: `/documentation/00-index/MASTER_INDEX.md` - Complete catalog of all documentation
- **AI Navigation**: `/documentation/00-index/AI_NAVIGATION_GUIDE.md` - AI-optimized query patterns
- **Search System**: `/documentation/00-index/scripts/search.py` - Full-text search across 124+ documents
- **Quick Reference**: `/documentation/09-reference/QUICK_REFERENCE.md` - Commands and common tasks

**10 Main Categories**:
1. **00-index**: Navigation, standards, templates, search system
2. **01-project-core**: Setup guides, project overview, AI assistant guide
3. **02-requirements**: User stories, business rules, feature requirements
4. **03-architecture**: System design, database schema, technology decisions
5. **04-implementation**: Component docs, authentication, frontend/backend
6. **05-development**: API docs, testing, deployment, coding standards
7. **06-design**: UI components, design system, user flows
8. **07-cvd-framework**: Planogram, DEX parser, service orders, analytics
9. **08-project-management**: Planning, tracking, project documentation
10. **09-reference**: Glossary, database queries, cheat sheets, examples

**Finding Information**:
```bash
# Search documentation
python /documentation/00-index/scripts/search.py --search "planogram"

# Use AI query patterns (see AI_QUERY_PATTERNS.md):
- "How do I..." → User guides
- "Error..." → Troubleshooting  
- "API..." → API documentation
- "What is..." → Glossary/Reference
```

## Feature Guide

### 1. Authentication & Users
- **4 User Roles**: Admin, Manager, Driver, Viewer
- **Session-based auth** with secure password hashing
- **Pages**: `login.html`, `user-management.html`, `profile.html`
- **Key APIs**: `/api/auth/*`, `/api/users/*`

### 2. Device Management
- **Multi-cabinet support** (up to 3 cabinets per device)
- **Soft delete** with recovery options
- **Pages**: `PCP.html` (listing), `INVD.html` (configuration)
- **Key APIs**: `/api/devices/*`

### 3. Planogram Management
- **Drag-and-drop interface** with product catalog
- **AI optimization** for product placement
- **No caching** - direct database operations
- **Page**: `NSPT.html`
- **Key APIs**: `/api/planograms/*`, `/api/products/*`

### 4. Service Orders
- **Cabinet-centric** order generation
- **Pick lists** based on par levels
- **Photo upload** for service verification
- **Page**: `service-orders.html`
- **Key APIs**: `/api/service-orders/*`

### 5. Driver PWA
- **Mobile-first** progressive web app
- **Offline support** with IndexedDB
- **Push notifications** for new orders
- **Location tracking** for route optimization
- **Path**: `/pages/driver-app/`

### 6. Analytics & Reports
- **Asset sales**: Device-level performance
- **Product sales**: Product performance across fleet
- **Home dashboard**: Business overview with map
- **Pages**: `asset-sales.html`, `product-sales.html`, `home-dashboard.html`

### 7. DEX Parser
- **40+ record types** supported
- **Grid pattern detection** (5 pattern types)
- **Multi-manufacturer** compatibility
- **Page**: `dex-parser.html`
- **Key APIs**: `/api/dex/*`

### 8. Route Management
- **Interactive map** with Leaflet.js
- **Two-way selection** sync
- **Address geocoding** with caching
- **Page**: `route-schedule.html`

## Navigation Routes

```javascript
// Hash-based routing in index.html
#home → home-dashboard.html
#coolers → PCP.html
#new-device → INVD.html
#planogram → NSPT.html
#service-orders → service-orders.html
#route-schedule → route-schedule.html
#asset-sales → asset-sales.html
#product-sales → product-sales.html
#database → database-viewer.html
#dex-parser → dex-parser.html
#company-settings → company-settings.html
#user-management → user-management.html
#profile → profile.html
```

## Database Schema

### Core Tables
- `devices` - Device registry with soft delete
- `cabinet_configurations` - Cabinet details
- `products` - Product catalog (12 system products)
- `planograms` & `planogram_slots` - Planogram data

### Authentication
- `users` - User accounts with roles
- `sessions` - Active sessions
- `audit_log` - Activity tracking

### Service Orders
- `service_orders` - Order headers
- `service_order_cabinets` - Cabinet-level tasks
- `service_order_cabinet_items` - Product requirements
- `service_visits` - Completed visits

### Analytics
- `sales` - Transaction data
- `device_metrics` - Performance tracking
- `dex_reads` & `dex_pa_records` - DEX data with grid info

### Configuration
- `locations`, `routes`, `device_types`, `cabinet_types`

## API Reference

Complete endpoints in original CLAUDE.md. Key additions:

### Authentication
- `POST /api/auth/login`
- `GET /api/auth/current-user`
- `POST /api/auth/logout`

### Service Orders
- `GET/POST /api/service-orders`
- `GET /api/service-orders/{id}/pick-list`
- `POST /api/service-orders/execute`

### Analytics
- `POST /api/metrics/calculate`
- `GET /api/metrics/weekly`
- `GET /api/metrics/top-performers`

## Key Technical Patterns

### Authentication Flow
```javascript
// Frontend auth check (auth-check.js)
await AuthCheck.verify();
// Redirects to login if unauthorized
```

### Cross-Frame Communication
```javascript
window.parent.postMessage({
    type: 'NAVIGATE|REFRESH_DATA|etc',
    payload: { /* data */ }
}, window.location.origin);
```

### API Client Usage
```javascript
const api = new CVDApi();
const devices = await api.getDevices();
```

### Planogram Data Flow
```
Database ←→ API ←→ Frontend (no caching)
```

## Development Guidelines

### Adding Features
1. Create page in `/pages/`
2. Add route to `index.html` pageRoutes
3. Import api.js with absolute path: `<script src="/api.js">`
4. Use CVDApi class for backend communication
5. Follow existing styling patterns

### Common Issues
- **Product IDs**: Always parseInt() from HTML attributes
- **Cabinet naming**: Use `modelName` not `cabinetType`
- **API paths**: Use absolute paths for imports
- **Auth errors**: Check session expiry

### Testing
- Python tests: `/tests/test_*.py`
- DEX samples: `/documentation/09-reference/examples/dex/`
- HTML tests: `/tests/*.html`
- **Testing Guide**: `/documentation/05-development/testing/GUIDE.md`
- **Test Examples**: `/documentation/05-development/testing/examples/`

## AI Features

### Chat Assistant
- Knowledge base in `knowledge_base.py`
- Falls back to rule-based if no API key
- Context-aware help for current page

### Planogram Optimizer
- Analyzes sales data
- Suggests optimal product placement
- Uses Claude API for recommendations

## PWA Features

### Driver App
- Install prompt on mobile
- Offline order viewing
- Background sync
- Push notifications
- Location tracking

### Service Worker
- Caches static assets
- Offline fallback pages
- Background sync queue

## Security Notes

- Role-based access control enforced
- Session timeout after inactivity
- Password complexity requirements
- Audit logging for sensitive operations
- CORS configured for API security

## 📖 Comprehensive Documentation System

The CVD project has a fully structured documentation system at `/documentation/` with:

### Key Entry Points for Agents

**Navigation & Discovery**:
- `/documentation/00-index/MASTER_INDEX.md` - Complete documentation catalog
- `/documentation/00-index/AI_QUERY_PATTERNS.md` - Query pattern mappings for AI agents
- `/documentation/00-index/CONTEXT_BRIDGES.md` - Document relationships and connections
- `/documentation/00-index/CROSS_REFERENCES.md` - Cross-reference system

**Search & Find**:
```bash
# Full-text search
python /home/jbrice/Projects/365/documentation/00-index/scripts/search.py --search "your query"

# Category-specific search
python /home/jbrice/Projects/365/documentation/00-index/scripts/search.py --search "API" --categories "Development"
```

**Standards & Templates**:
- `/documentation/00-index/DOCUMENTATION_STANDARDS.md` - Documentation guidelines
- `/documentation/00-index/METADATA_SCHEMA.md` - Metadata requirements
- `/documentation/00-index/templates/` - Document templates for new content

### For Creating New Documentation

When creating new documentation:
1. **Choose the right category** (00-index through 09-reference)
2. **Use appropriate template** from `/documentation/00-index/templates/`
3. **Add metadata header** following METADATA_SCHEMA.md
4. **Update cross-references** if linking to other docs
5. **Rebuild search index**: `python /documentation/00-index/scripts/search.py --build`

### For Finding Information

**By Role**:
- **Developers**: Start at `/documentation/05-development/`
- **Admins**: See `/documentation/02-requirements/guides/ADMIN_GUIDE.md`
- **Managers**: See `/documentation/02-requirements/guides/MANAGER_GUIDE.md`
- **Drivers**: See `/documentation/02-requirements/guides/DRIVER_APP_GUIDE.md`

**By Feature**:
- **Planogram**: `/documentation/07-cvd-framework/planogram/`
- **Service Orders**: `/documentation/07-cvd-framework/service-orders/`
- **DEX Parser**: `/documentation/07-cvd-framework/dex-parser/`
- **Analytics**: `/documentation/07-cvd-framework/analytics/`

**Quick References**:
- **Commands**: `/documentation/09-reference/cheat-sheets/DEVELOPER_COMMANDS.md`
- **Database Queries**: `/documentation/09-reference/cheat-sheets/DATABASE_QUERIES.md`
- **Emergency Procedures**: `/documentation/09-reference/cheat-sheets/EMERGENCY_PROCEDURES.md`
- **Glossary**: `/documentation/09-reference/GLOSSARY.md`

### Documentation Quality & Maintenance

- **Current Quality Score**: 89/100 (Grade: B+)
- **Search Index**: 124 documents, 4,588 searchable terms
- **Coverage**: 147+ documentation files
- **Automated Tools**: Link checking, format validation, metrics collection

For detailed information on any aspect of the CVD system, use the search system or navigate through the structured categories in `/documentation/`.
## Important Notes (Updated 2025-08-13)

### Database Architecture Decision
- **SQLite is the permanent database solution** - No PostgreSQL migration planned
- All PostgreSQL migration artifacts have been removed (2025-08-13)
- Django framework evaluation discontinued - Flask remains the web framework
- Backup of removed items stored at: `/backup_postgres_removal_20250813/`

### Removed Infrastructure
The following were removed on 2025-08-13:
- `/migration/` directory - PostgreSQL migration scripts (38 files)
- `/django_venv/` - Django virtual environment 
- `.env.postgresql` configuration files
- PostgreSQL-related documentation

### Current Architecture
- **Database**: SQLite (permanent solution)
- **Web Framework**: Flask
- **Frontend**: Modular iframe-based architecture (no build dependencies)
- **Mobile**: Progressive Web App for drivers
