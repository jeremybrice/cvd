# AI Assistant Guide for CVD System


## Metadata
- **ID**: 01_PROJECT_CORE_AI_ASSISTANT_GUIDE
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #core-concepts #data-exchange #data-layer #database #debugging #deployment #device-management #devops #dex-parser #driver-app #getting-started #integration #logistics #machine-learning #metrics #mobile #operations #optimization #performance #planogram #product-placement #project-overview #pwa #quality-assurance #reporting #route-management #security #service-orders #testing #troubleshooting #vending-machine
- **Intent**: Documentation for AI Assistant Guide for CVD System
- **Audience**: system administrators, managers, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/01-project-core/
- **Category**: 01 Project Core
- **Search Keywords**: ###, (being, (listing),, (migrating, **complete, **cross-reference, **documentation**:, **key, **technical, **testing, .html`, 40+, `/api/auth/, `/api/devices/, `/api/dex/

This guide provides comprehensive instructions for AI assistants (particularly Claude Code) when working with the CVD (Vision Device Configuration) application. It preserves all technical patterns and guidance while referencing the new documentation structure.

## Application Overview

CVD (Vision Device Configuration) is an enterprise vending machine fleet management system with:
- Flask/SQLite backend with role-based authentication
- Modular iframe-based frontend (no build dependencies)
- Progressive Web App for mobile driver operations
- AI-powered planogram optimization and chat assistant
- Real-time analytics and service order management

## Quick Start Reference

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

**Documentation Reference**: See `/documentation/01-project-core/QUICK_START.md` for detailed setup instructions.

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

**New Documentation Structure**: See `/documentation/00-index/MASTER_INDEX.md` for complete directory organization.

Key locations:
- Frontend pages: `/pages/`
- Driver PWA: `/pages/driver-app/`
- Documentation: `/documentation/` (new structured system)
- Legacy docs: `/docs/` (being migrated)
- Tests: `/tests/`
- Tools: `/tools/`

**Cross-Reference Guide**: `/documentation/00-index/MIGRATION_MAP.md` maps old paths to new locations.
**System Architecture**: `/documentation/03-architecture/system/` contains migrated system documentation including file structure guides, data flow analysis, and technical specifications.

## Feature Guide

### 1. Authentication & Users
- **4 User Roles**: Admin, Manager, Driver, Viewer
- **Session-based auth** with secure password hashing
- **Pages**: `login.html`, `user-management.html`, `profile.html`
- **Key APIs**: `/api/auth/*`, `/api/users/*`
- **Documentation**: `/documentation/04-implementation/backend/authentication.md`

### 2. Device Management
- **Multi-cabinet support** (up to 3 cabinets per device)
- **Soft delete** with recovery options
- **Pages**: `PCP.html` (listing), `INVD.html` (configuration)
- **Key APIs**: `/api/devices/*`
- **Documentation**: `/documentation/07-cvd-framework/device-management.md`

### 3. Planogram Management
- **Drag-and-drop interface** with product catalog
- **AI optimization** for product placement
- **No caching** - direct database operations
- **Page**: `NSPT.html`
- **Key APIs**: `/api/planograms/*`, `/api/products/*`
- **Documentation**: `/documentation/07-cvd-framework/planogram/README.md`

### 4. Service Orders
- **Cabinet-centric** order generation
- **Pick lists** based on par levels
- **Photo upload** for service verification
- **Page**: `service-orders.html`
- **Key APIs**: `/api/service-orders/*`
- **Documentation**: `/documentation/07-cvd-framework/service-orders/README.md`

### 5. Driver PWA
- **Mobile-first** progressive web app
- **Offline support** with IndexedDB
- **Push notifications** for new orders
- **Location tracking** for route optimization
- **Path**: `/pages/driver-app/`
- **Documentation**: `/documentation/04-implementation/frontend/pwa-architecture.md`

### 6. Analytics & Reports
- **Asset sales**: Device-level performance
- **Product sales**: Product performance across fleet
- **Home dashboard**: Business overview with map
- **Pages**: `asset-sales.html`, `product-sales.html`, `home-dashboard.html`
- **Documentation**: `/documentation/07-cvd-framework/analytics/README.md`

### 7. DEX Parser
- **40+ record types** supported
- **Grid pattern detection** (5 pattern types)
- **Multi-manufacturer** compatibility
- **Page**: `dex-parser.html`
- **Key APIs**: `/api/dex/*`
- **Documentation**: `/documentation/07-cvd-framework/dex-parser/README.md`

### 8. Route Management
- **Interactive map** with Leaflet.js
- **Two-way selection** sync
- **Address geocoding** with caching
- **Page**: `route-schedule.html`
- **Documentation**: `/documentation/04-implementation/components/route-management.md`

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

**Navigation Documentation**: `/documentation/04-implementation/frontend/navigation-system.md`

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

**Complete Schema**: `/documentation/03-architecture/system/DATABASE_SCHEMA.md`
**Database Reference**: `/documentation/09-reference/database/`

## API Reference

**Complete API Documentation**: `/documentation/05-development/api/README.md`

Key endpoint categories:

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

**Endpoint Details**: Individual endpoint documentation in `/documentation/05-development/api/endpoints/`

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

**Technical Patterns**: `/documentation/03-architecture/patterns/README.md`

## Development Guidelines

### Adding Features
1. Create page in `/pages/`
2. Add route to `index.html` pageRoutes
3. Import api.js with absolute path: `<script src="/api.js">`
4. Use CVDApi class for backend communication
5. Follow existing styling patterns

**Development Guide**: `/documentation/05-development/README.md`

### Common Issues
- **Product IDs**: Always parseInt() from HTML attributes
- **Cabinet naming**: Use `modelName` not `cabinetType`
- **API paths**: Use absolute paths for imports
- **Auth errors**: Check session expiry

**Troubleshooting**: `/documentation/09-reference/troubleshooting/common-issues.md`

### Testing
- Python tests: `/tests/test_*.py`
- DEX samples: `/documentation/09-reference/examples/dex/` (migrated from `/docs/examples/dex files/`)
- HTML tests: `/tests/*.html`

**Testing Guide**: `/documentation/05-development/testing/README.md`

## AI Features

### Chat Assistant
- Knowledge base in `knowledge_base.py`
- Falls back to rule-based if no API key
- Context-aware help for current page

### Planogram Optimizer
- Analyzes sales data
- Suggests optimal product placement
- Uses Claude API for recommendations

**AI Integration**: `/documentation/04-implementation/backend/ai-services.md`

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

**PWA Documentation**: `/documentation/04-implementation/frontend/pwa-features.md`

## Security Notes

- Role-based access control enforced
- Session timeout after inactivity
- Password complexity requirements
- Audit logging for sensitive operations
- CORS configured for API security

**Security Guide**: `/documentation/03-architecture/security/README.md`

## New Documentation System Navigation

The CVD system now uses a structured documentation system. Key navigation points for AI assistants:

### Primary Documentation Categories
1. **Project Core** (`/documentation/01-project-core/`): System understanding, quick start
2. **Requirements** (`/documentation/02-requirements/`): User stories, analysis, scope
3. **Architecture** (`/documentation/03-architecture/`): System design, patterns, decisions
4. **Implementation** (`/documentation/04-implementation/`): Backend, frontend, components
5. **Development** (`/documentation/05-development/`): API, testing, tools, deployment
6. **Design** (`/documentation/06-design/`): UI patterns, components, user flows
7. **CVD Framework** (`/documentation/07-cvd-framework/`): Feature-specific documentation
8. **Project Management** (`/documentation/08-project-management/`): Planning and coordination
9. **Reference** (`/documentation/09-reference/`): Cheat sheets, examples, database info

### AI Assistant Navigation Tools
- **Master Index**: `/documentation/00-index/MASTER_INDEX.md` - Complete document inventory
- **AI Navigation**: `/documentation/00-index/AI_NAVIGATION_GUIDE.md` - AI-specific guidance
- **Cross References**: `/documentation/00-index/CROSS_REFERENCES.md` - Topic relationships
- **Migration Map**: `/documentation/00-index/MIGRATION_MAP.md` - Old to new path mappings

### Legacy Documentation
Legacy documentation in `/docs/` has been systematically migrated to the new structure. System documentation, examples, and database reports have been migrated. Check migration status in `/documentation/00-index/MIGRATION_INVENTORY.md`.

## AI Assistant Instructions

When working with the CVD system:

1. **Always check documentation structure first**: Use `/documentation/00-index/` for navigation
2. **Reference current paths**: Use absolute paths and check migration mappings
3. **Follow established patterns**: Maintain consistency with existing code patterns
4. **Document new features**: Follow templates in `/documentation/00-index/templates/`
5. **Update cross-references**: Maintain documentation relationships

**Important**: This AI Assistant Guide will be updated as the documentation migration progresses. Always check for the latest version and cross-reference with the master index.

For detailed information on specific features, refer to the structured documentation in `/documentation/` rather than legacy `/docs/` paths when available.