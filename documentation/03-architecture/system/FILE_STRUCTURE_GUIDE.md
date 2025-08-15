---
type: reference
category: system
title: CVD File Structure and Location Guide
status: active
last_updated: 2025-08-12
tags: [file-structure, navigation, development]
cross_references:
  - /documentation/05-development/SETUP_GUIDE.md
  - /documentation/04-implementation/README.md
---

# CVD File Location Guide

This guide provides a quick reference for locating files in the CVD (Vision Device Configuration) application codebase. Use this document to quickly find where specific types of files are stored.

## Quick Reference

### Core Application Files
- **Backend API**: `app.py` (root)
- **Frontend API Client**: `api.js` (root)
- **Main Entry Point**: `index.html` (root)
- **Database**: `cvd.db` (root)
- **Python Dependencies**: `requirements.txt` (root)

### By File Type

#### Python Files (.py)
**Root Directory (Core Components):**
- `app.py` - Flask backend server
- `auth.py` - Authentication module
- `dex_parser.py` - DEX file parser
- `grid_pattern_analyzer.py` - Grid pattern detection
- `knowledge_base.py` - AI assistant knowledge base
- `planogram_optimizer.py` - Planogram optimization
- `service_order_service.py` - Service order management
- `migration_add_addresses.py` - Address migration script

**Testing Files:** `/tests/`
- `test_*.py` - All test files

**Utility Scripts:** `/tools/python/`
- `check_chat_api.py` - API validation
- `export_device_products.py` - Data export
- `reset_admin_password.py` - Password reset
- `update_existing_grid_patterns.py` - Grid updates
- `validate_optimizer.py` - Optimizer validation

#### HTML Files
**Application Pages:** `/pages/`
- `PCP.html` - Device listing (coolers)
- `INVD.html` - Device configuration wizard
- `NSPT.html` - Planogram management
- `database-viewer.html` - Database viewer
- `company-settings.html` - Company settings
- `route-schedule.html` - Route scheduling
- `asset-sales.html` - Asset sales reports
- `product-sales.html` - Product sales reports
- `dex-parser.html` - DEX parser interface
- `service-orders.html` - Service orders
- `login.html` - Authentication
- `profile.html` - User profile
- `user-management.html` - User management
- `home-dashboard.html` - Dashboard

**Driver PWA:** `/pages/driver-app/`
- `index.html` - Driver app main page
- `order-detail.html` - Order details view
- Various support files for iOS/Android fixes

**Test HTML:** `/tests/`
- `debug-*.html` - Debug utilities
- `test-*.html` - Test pages

#### JavaScript Files
**Root Directory:**
- `api.js` - Frontend API client
- `auth-check.js` - Auth checking utility
- `service-worker.js` - PWA service worker

**Driver App:** `/pages/driver-app/`
- `app.js` - Main driver app logic
- `db.js` - Database handling
- `sync-manager.js` - Data synchronization
- Various platform-specific fixes

#### Documentation Files
**New Documentation Structure:** `/documentation/`
- `01-project-core/` - Core project information
- `02-requirements/` - Business requirements and user guides
- `03-architecture/` - System architecture and patterns
- `04-implementation/` - Implementation details
- `05-development/` - Development guides and tools
- `06-design/` - UI/UX design system
- `07-cvd-framework/` - CVD-specific features
- `08-project-management/` - Project management resources
- `09-reference/` - Quick references and examples

**Legacy Documentation:** `/docs/` (being migrated)
- `debug-reports/` - Bug fix documentation
- `examples/` - Code examples and DEX file samples
- `plans/` - Implementation plans
- `prompts/` - AI prompt engineering
- `reports/` - Analysis reports
- `system-structure/` - Architecture docs

**Root Documentation:**
- `CLAUDE.md` - Claude Code instructions

### By Feature

#### Authentication System
- Backend: `auth.py`
- Frontend: `auth-check.js`, `/pages/login.html`
- Tests: `/tests/test_auth_flow.py`
- Migrations: `/migrations/001_authentication.sql`

#### DEX Parser
- Backend: `dex_parser.py`, `grid_pattern_analyzer.py`
- Frontend: `/pages/dex-parser.html`
- Examples: `/documentation/09-reference/examples/dex/`

#### Service Orders
- Backend: `service_order_service.py`
- Frontend: `/pages/service-orders.html`
- Driver App: `/pages/driver-app/order-detail.*`
- Migrations: `/migrations/*service_orders*.sql`

#### Planograms
- Backend: `planogram_optimizer.py`
- Frontend: `/pages/NSPT.html`
- Tests: `/tests/test_planogram_optimizer.py`

#### Route Management
- Frontend: `/pages/route-schedule.html`
- Tests: `/tests/test-route-api.py`

#### Sales Reports
- Asset Sales: `/pages/asset-sales.html`
- Product Sales: `/pages/product-sales.html`

#### Driver PWA
- Main App: `/pages/driver-app/`
- Service Worker: `service-worker.js`
- Manifest: `manifest.json`
- Icons: `/icons/`

### Supporting Files

#### Configuration
- Nginx: `/config/nginx-pwa.conf`
- PWA Manifest: `manifest.json`

#### Database
- Main DB: `cvd.db`
- Backups: `/backups/`
- Migrations: `/migrations/`

#### Logs
- All logs: `/logs/`
  - `flask.log` - Backend logs
  - `server.log` - Server logs
  - `frontend_test.log` - Frontend tests
  - `http_server.log` - HTTP server

#### Assets
- Logo: `/images/365-logo.png`
- PWA Icons: `/icons/`
- Additional Icons: `/images/icons/`

#### Development Tools
- Icon Generation: `/tools/icon-generator/`
- Python Utilities: `/tools/python/`
- HTML Tools: `/tools/html/`

#### Testing
- Python Tests: `/tests/test_*.py`
- HTML Tests: `/tests/*.html`
- DEX Samples: `/documentation/09-reference/examples/dex/`

## Directory Structure

```
365/
├── Root (Core Application)
│   ├── *.py (Core Python modules)
│   ├── *.js (Core JavaScript)
│   ├── index.html (Main entry)
│   └── cvd.db (Database)
├── /backups/ (Database & code backups)
├── /config/ (Configuration files)
├── /documentation/ (New structured documentation)
│   ├── /01-project-core/
│   ├── /02-requirements/
│   ├── /03-architecture/
│   ├── /04-implementation/
│   ├── /05-development/
│   ├── /06-design/
│   ├── /07-cvd-framework/
│   ├── /08-project-management/
│   └── /09-reference/
├── /docs/ (Legacy documentation - being migrated)
│   ├── /debug-reports/
│   ├── /examples/
│   ├── /plans/
│   ├── /prompts/
│   ├── /reports/
│   └── /system-structure/
├── /icons/ (PWA icons)
├── /images/ (Application images)
├── /logs/ (Application logs)
├── /migrations/ (Database migrations)
├── /pages/ (Application pages)
│   └── /driver-app/ (PWA driver app)
├── /tests/ (Test files)
├── /tools/ (Development utilities)
│   ├── /icon-generator/
│   └── /python/
└── /venv/ (Python virtual environment)
```

## Common Tasks

### Finding a Feature
1. Check `/pages/` for the HTML interface
2. Look in root for the Python backend module
3. Check `/documentation/07-cvd-framework/` for feature documentation

### Adding New Features
1. HTML pages go in `/pages/`
2. Backend modules go in root directory
3. Tests go in `/tests/`
4. Documentation goes in `/documentation/`

### Debugging Issues
1. Check `/logs/` for error logs
2. Review `/docs/debug-reports/` for similar issues
3. Use test files in `/tests/` for isolated testing

### Database Work
1. Current database: `cvd.db` (root)
2. Backups in `/backups/`
3. Migrations in `/migrations/`
4. Schema docs in `/documentation/03-architecture/system/DATABASE_SCHEMA.md`

This guide reflects the current file organization as of the latest restructuring. Always check the actual directory structure if files appear to be missing.
