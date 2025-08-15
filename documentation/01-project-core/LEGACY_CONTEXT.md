# CVD Context Management Guide

This document helps Claude Code efficiently navigate and understand the CVD codebase.

## Module Context Maps

### Service Order Module
**Primary Files:**
- Backend: `/home/jbrice/Projects/365/service_order_service.py`
- Frontend: `/home/jbrice/Projects/365/pages/service-orders.html`
- API Client: `/home/jbrice/Projects/365/api.js` (lines 500-700)
- Database: `service_orders`, `service_order_cabinets`, `service_order_cabinet_items`

**Key Concepts:**
- Cabinet-centric order generation
- Pick list calculation based on par levels
- Photo verification for completed visits
- Driver assignment and route integration

**Dependencies:**
- Requires: Device configurations, Product catalog, Route assignments
- Impacts: Inventory levels, Sales metrics, Driver schedules

### Planogram Module
**Primary Files:**
- Optimizer: `/home/jbrice/Projects/365/planogram_optimizer.py`
- Frontend: `/home/jbrice/Projects/365/pages/NSPT.html`
- Drag-Drop: `/home/jbrice/Projects/365/pages/NSPT.html` (lines 200-500)
- Database: `planograms`, `planogram_slots`

**Key Concepts:**
- No caching - direct database operations
- AI optimization via Claude API
- Slot-level performance tracking
- Visual merchandising zones (A/B/C rows)

**Critical Functions:**
```python
# Planogram optimization entry point
optimize_planogram(device_id, sales_data, constraints)

# Slot performance calculation
calculate_slot_metrics(slot_id, date_range)

# Product recommendation
recommend_products_for_empty_slots(cabinet_config, location_type)
```

### DEX Parser Module
**Primary Files:**
- Parser: `/home/jbrice/Projects/365/dex_parser.py`
- Grid Analyzer: `/home/jbrice/Projects/365/grid_pattern_analyzer.py`
- Frontend: `/home/jbrice/Projects/365/pages/dex-parser.html`
- Examples: `/home/jbrice/Projects/365/docs/examples/dex files/`

**Supported Records:**
- Transaction: DXS, ST, SE, DXE
- Product: PA1, PA2 (grid mapping)
- Sales: VA1, VA2, VA3
- Cash: CA1-CA15
- Events: EA1-EA7

**Grid Patterns:**
1. Spiral (most common)
2. Column-based
3. Serpentine
4. Horizontal
5. Custom

### Driver PWA Module
**Primary Files:**
- Main App: `/home/jbrice/Projects/365/pages/driver-app/index.html`
- Service Worker: `/home/jbrice/Projects/365/pages/driver-app/service-worker.js`
- Offline Storage: `/home/jbrice/Projects/365/pages/driver-app/offline-storage.js`
- Manifest: `/home/jbrice/Projects/365/pages/driver-app/manifest.json`

**Key Features:**
- IndexedDB for offline data
- Background sync for uploads
- Push notifications
- GPS tracking
- Photo capture

**Data Flow:**
```
Server → Service Worker → IndexedDB → UI
       ← Background Sync ← User Actions ←
```

## Context Loading Strategies

### For New Features
1. Load CLAUDE.md for project overview
2. Load relevant module context from this file
3. Load specific implementation files
4. Check database schema if data-related

### For Bug Fixes
1. Load error context from debug-reports/
2. Load affected module files
3. Check recent git commits in area
4. Review related test files

### For Optimizations
1. Load current implementation
2. Review performance metrics
3. Check similar patterns in codebase
4. Load relevant agent expertise

## Quick Reference Paths

### Core Backend
- Main App: `/home/jbrice/Projects/365/app.py`
- Auth: `/home/jbrice/Projects/365/auth.py`
- Database: `/home/jbrice/Projects/365/database.db`

### Frontend Entry Points
- Navigation: `/home/jbrice/Projects/365/index.html`
- API Client: `/home/jbrice/Projects/365/api.js`
- Auth Check: `/home/jbrice/Projects/365/auth-check.js`

### Key Pages
- Devices: `/home/jbrice/Projects/365/pages/PCP.html`
- Config: `/home/jbrice/Projects/365/pages/INVD.html`
- Planogram: `/home/jbrice/Projects/365/pages/NSPT.html`
- Analytics: `/home/jbrice/Projects/365/pages/asset-sales.html`

### Testing
- Python: `/home/jbrice/Projects/365/tests/test_*.py`
- HTML: `/home/jbrice/Projects/365/tests/*.html`

## Memory Management Tips

### Large Context Operations
When working with multiple modules:
1. Start with module-specific context
2. Load only relevant sections of large files
3. Summarize findings before switching context
4. Use agents specialized for the domain

### Context Switching Protocol
1. Save current state/findings
2. Clear unnecessary context
3. Load new module context
4. Reference saved state as needed

### Efficient File Reading
```python
# Read specific sections
Read file_path limit=100 offset=500  # Read lines 500-600

# Read multiple related files in batch
Read service_order_service.py
Read pages/service-orders.html
Read api.js limit=200 offset=500
```