# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

CVD (Vision Device Configuration) is a full-stack web application for managing vending machine devices, planograms, routes, and sales analytics. Built with a Flask/SQLite backend and modular iframe-based frontend with no build dependencies.

## How to Run the Application

### Initial Setup

```bash
# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### AI Chat Bot Configuration

The application includes an AI-powered chat assistant that requires additional setup:

1. **Set Anthropic API Key**:
   ```bash
   export ANTHROPIC_API_KEY="your-actual-api-key-here"
   ```
  
   - Get your API key from https://console.anthropic.com/
   - The chat bot will fall back to rule-based responses if the API key is not set or invalid

2. **Required Python Package**:
   - The `anthropic` package is included in requirements.txt
   - If missing, install with: `pip install anthropic==0.57.1`

### Running the Application

```bash
# Terminal 1: Start Flask API server (required for data operations)
source venv/bin/activate
export ANTHROPIC_API_KEY="your-actual-api-key-here"  # Set API key for chat bot

# verify key 
echo $ANTHROPIC_API_KEY

# launch server
python app.py
# Server runs on http://localhost:5000/api

# Terminal 2: Start local HTTP server for frontend (required for proper CORS handling)
cd /home/jbrice/Projects/365
python -m http.server 8000
# OR
python3 -m http.server 8000

# Access at: http://localhost:8000/
```

**Frontend**: Pure HTML/CSS/JavaScript with no compilation or dependencies
**Backend**: Flask with SQLite database
**AI Assistant**: Anthropic Claude API (optional, falls back to rule-based responses)

## Architecture & Key Relationships

### Core Module Structure
- **`index.html`** - Main navigation shell and iframe router (root directory)
- **`pages/PCP.html`** - Device listing and management (tabular interface)
- **`pages/INVD.html`** - Device configuration wizard (5-step multi-cabinet setup)
- **`pages/NSPT.html`** - Planogram management tool (drag-and-drop interface)
- **`pages/database-viewer.html`** - Database viewer and CSV export utility
- **`pages/company-settings.html`** - Company settings management interface
- **`pages/route-planning.html`** - Route planning and device scheduling interface
- **`pages/route-schedule.html`** - Route scheduling interface with 50/50 layout (device list left, interactive map right) featuring Leaflet.js integration, two-way device selection sync, and real-time address geocoding
- **`pages/asset-sales.html`** - Asset-based sales reporting and analytics
- **`pages/product-sales.html`** - Product-based sales reporting and analytics
- **`pages/dex-parser.html`** - DEX parser frontend interface
- **`app.py`** - Flask backend API server
- **`dex_parser.py`** - Standalone DEX parsing engine
- **`api.js`** - Frontend API client module (imported by all pages)

### DEX Parser Engine with Grid Pattern Analysis
- **`dex_parser.py`** - Standalone DEX (Data Exchange) file parser
  - Comprehensive record type support (40+ processors)  
  - PA record consolidation with error validation
  - **Grid pattern analysis** - Automatic detection of vending machine selection layouts
  - Multi-manufacturer compatibility (Vendo, AMS, Crane)
  - No external dependencies - pure Python implementation
- **`grid_pattern_analyzer.py`** - Grid pattern detection engine
  - **5 Pattern Types**: Alphanumeric (A1-A9), Numeric Tens (10,12,14), Sequential Blocks (1-10), Zero-padded (01-09), Custom Numeric (101-201)
  - **Confidence Scoring**: 0.0-1.0 confidence ratings for pattern detection accuracy
  - **Row/Column Assignment**: Automatic assignment of grid coordinates to selection numbers
  - **Error Handling**: Graceful handling of irregular patterns and missing selections

### Communication Pattern
```javascript
// Cross-iframe communication via postMessage API
window.parent.postMessage({
    type: 'NAVIGATE|DEVICE_ADDED|REQUEST_DEVICES|REFRESH_DATA',
    payload: { /* data */ }
}, window.location.origin);
```

### Data Storage Architecture
**Backend**: Flask REST API (`app.py`) with SQLite database (`cvd.db`):

#### Core Tables
- **`devices`** - Device metadata with soft delete support
  - Fields: asset, cooler, location_id (FK), model, device_type_id (FK), route_id, deleted_at, deleted_by
  - Supports soft deletion with deleted_at timestamp
- **`cabinet_configurations`** - Cabinet details with camelCase properties
  - Fields: device_id (FK), cabinet_type, modelName, isParent, cabinet_index, rows, columns
- **`products`** - Product catalog with integer primary keys
  - Migrated from hard-coded JavaScript, 12 system products
  - Fields: name, category, price, image, is_system
- **`planograms`** and **`planogram_slots`** - Planogram layouts and slot assignments
  - planogram_slots has foreign key to products table
  - Fields: slot_position, product_id (FK), quantity, capacity, par_level, price

#### Location & Route Management
- **`locations`** - Device location definitions
  - Fields: name, created_at, updated_at
- **`routes`** - Delivery/service route definitions  
  - Fields: name, route_number, created_at, updated_at
- **`device_routes`** - Many-to-many relationship between devices and routes
  - Primary key: (device_id, route_id)

#### Type Definitions
- **`device_types`** - Device type definitions
  - Fields: name, description, allows_additional_cabinets
- **`cabinet_types`** - Cabinet type definitions
  - Fields: name, description, rows, cols, icon
  - Types: Cooler, Freezer, Ambient, Ambient+

#### Analytics & DEX Data
- **`sales`** - Sales transaction data
  - Fields: device_id (FK), product_id (FK), sale_units, sale_cash, created_at
- **`dex_reads`** - DEX file upload tracking
  - Fields: filename, machine_info, total_records, created_at
- **`dex_pa_records`** - Consolidated PA (Product Audit) records with grid analysis
  - Fields: dex_read_id (FK), selection_number, price_cents, units_sold, revenue_cents, **row**, **column**
  - **Grid Fields**: `row` and `column` VARCHAR(10) fields populated by automatic pattern analysis
  - **Pattern Support**: Alphanumeric (A1, B2), Numeric (10, 12), Sequential (1-9), and Custom patterns

**API Convention**: Backend serves camelCase properties for frontend compatibility
**Frontend**: Pages import `api.js` using absolute paths (`<script src="/api.js"></script>`) to ensure proper loading from `/pages/` subfolder

### Planogram Data Flow (Critical)
**NO CACHING** - All planogram data flows directly between database and frontend:
```
Database (planogram_slots) ←→ API ←→ Frontend (state.planogram)
```
- **Load**: Always fetches fresh from database when selecting cabinet
- **Save**: Always saves directly to database
- **No in-memory cache** - Removed `state.planograms` to ensure data consistency

## Navigation & Routing

Hash-based routing managed by index.html:
- `#coolers` → `pages/PCP.html` (device listing)
- `#new-device` → `pages/INVD.html` (device configuration)
- `#planogram` → `pages/NSPT.html` (planogram management) 
- `#database` → `pages/database-viewer.html` (database viewer)
- `#company-settings` → `pages/company-settings.html` (company settings)
- `#route-planning` → `pages/route-planning.html` (route management)
- `#asset-sales` → `pages/asset-sales.html` (asset sales reports)
- `#product-sales` → `pages/product-sales.html` (product sales reports)

**Important**: All page routes in `pageRoutes` object use `pages/` prefix to match current file organization

## Key Technical Patterns

### Multi-Cabinet Device Support
- **Parent Cabinet**: Primary cabinet defining device model
- **Additional Cabinets**: Up to 2 additional cabinets for PicoVision devices
- **Layout Types**: 5×8 (standard), 6×9 (Ambient+)
- **Individual Planograms**: Each cabinet has separate planogram data

### Backend API Integration
- Frontend uses `CVDApi` class from `api.js` for all server communication
- API client includes retry logic, offline queueing, and error handling
- Backend API serves camelCase properties (`modelName`, `isParent`) for frontend compatibility
- Database stores snake_case but converts on API response

### Product Management System
- **Products migrated from hard-coded JavaScript** to database with integer primary keys
- **Drag-and-drop functionality** in NSPT.html uses type-safe product ID handling (parseInt for string-to-integer conversion)
- **API endpoints**: `/api/products`, `/api/products/categories` with optional category filtering
- **Foreign key relationships**: planogram_slots.product_id references products.id

### Cross-Frame State Management
- index.html acts as central message hub
- Each iframe can request device data from parent
- Real-time updates broadcast to all frames
- Secure origin validation for all postMessage calls

## Development Guidelines

### File Structure
- Main navigation: `index.html` (root directory)
- Application pages: `/pages/` subfolder
- Documentation: `/docs/` subfolder
- Each HTML file is self-contained (embedded CSS/JS)
- Assets: `images/365-logo.png` (40px height in navigation)
- API module: `api.js` (root directory, imported with absolute paths)
- Python dependencies: `requirements.txt` (Flask, Flask-CORS, Gunicorn)
- Deployment config: `render.yaml` (Render.com deployment)

### Styling Standards
- **Primary Color**: `#006dfe`
- **System Fonts**: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Desktop Optimized**: Minimum 1200px width
- Consistent component styling across modules
- **Save Button Fix**: Special CSS to ensure proper hover/click behavior

### Data Validation
- Required fields validated before save operations
- Multi-cabinet configuration validation
- Form progression with section-by-section enabling
- Input sanitization for database storage

### Browser Requirements
- ES6+ support required
- FileReader API (photo uploads)
- CSS Grid and Flexbox support
- Fetch API for backend communication

## Development Commands

### Starting the Application
```bash
# Terminal 1: Start Flask API server (required)
python app.py

# Terminal 2: Start frontend HTTP server  
python -m http.server 8000

# Access: http://localhost:8000/
```

### Database Operations
```bash
# View all tables
python -c "import sqlite3; db=sqlite3.connect('cvd.db'); print([row[0] for row in db.execute('SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name')])"

# Check products count
python -c "import sqlite3; db=sqlite3.connect('cvd.db'); print('Products:', db.execute('SELECT COUNT(*) FROM products').fetchone()[0])"

# View planogram slots for a specific planogram
python -c "import sqlite3; db=sqlite3.connect('cvd.db'); print(db.execute('SELECT * FROM planogram_slots WHERE planogram_id=1').fetchall())"

# Check device soft delete status
python -c "import sqlite3; db=sqlite3.connect('cvd.db'); print('Deleted devices:', db.execute('SELECT COUNT(*) FROM devices WHERE deleted_at IS NOT NULL').fetchone()[0])"

# Reset database (if needed)
rm cvd.db && python app.py
```

### DEX Parser Testing with Grid Analysis
```bash
# Test standalone parser with grid analysis
python -c "from dex_parser import DEXParser; print('Import successful')"

# Test with sample file including grid pattern detection
python -c "
from dex_parser import DEXParser
with open('examples/AMS Sensit III.txt', 'r') as f:
    content = f.read()
parser = DEXParser()
result = parser.parse_file(content, 'test.txt')
print(f'Success: {result[\"success\"]}, PA Records: {len(result[\"pa_records\"])}')
if 'grid_analysis' in result:
    grid = result['grid_analysis']
    print(f'Grid Pattern: {grid[\"pattern_type\"]}, Confidence: {grid[\"confidence\"]:.2f}')
    print(f'Grid Dimensions: {grid[\"grid_dimensions\"]}')
"

# Test grid pattern analyzer standalone
python -c "
from grid_pattern_analyzer import GridPatternAnalyzer
analyzer = GridPatternAnalyzer()
# Test different pattern types
patterns = [
    ['A1', 'A2', 'B1', 'B2'],  # Alphanumeric
    ['10', '12', '14', '20', '22'],  # Numeric tens
    ['1', '2', '3', '4', '5']  # Sequential
]
for i, pattern in enumerate(patterns):
    result = analyzer.analyze_selections(pattern)
    print(f'Pattern {i+1}: {result[\"pattern_type\"]} (confidence: {result[\"confidence\"]:.2f})')
"

# Update existing records with grid patterns (batch processing)
python update_existing_grid_patterns.py
```

### Product Database Migration
- Products are auto-migrated on first backend startup from hard-coded data in app.py
- Migration creates 12 system products with integer IDs 1-12
- Automatically converts planogram_slots.product_id from TEXT to INTEGER with foreign key constraint

## Debug and Troubleshooting

### Common Data Structure Issues
- Use `cabinet.modelName` not `cabinet.cabinetType` 
- API imports must use absolute paths: `<script src="/api.js"></script>`
- Navigation routes in index.html must include `pages/` prefix
- Backend serves camelCase properties; frontend expects camelCase

### Product ID Type Safety
- **Critical**: Product IDs from HTML data attributes are strings, database uses integers
- **Always use parseInt()** when extracting product IDs: `parseInt(element.dataset.productId)`
- **Drag-drop handlers** must convert string IDs to integers for database lookups
- **Save operations** expect integer product IDs in planogram data structure

### Planogram Loading Issues
- **No caching**: If planogram data doesn't load, check database directly
- **Console logs**: Look for `📥 Loading planogram from database` messages
- **API response**: Verify `/api/planograms/<key>` returns slot data
- **Type consistency**: Ensure productId is integer in all operations

### File Organization Rules
- New HTML pages go in `/pages/` subfolder
- Update `pageRoutes` in index.html when adding pages
- Use absolute API imports to avoid path resolution issues
- Clear browser cache when debugging import issues

### Map Integration (Route Schedule)
- **Technology**: Leaflet.js v1.9.4 with OpenStreetMap tiles
- **Address Data**: Real Michigan addresses from Asset Address.txt for devices 111, 222, 333, 444, 555, 666, 888, 999, 5436, 7875
- **Geocoding**: Nominatim (OpenStreetMap) service with 100ms delay to prevent rate limiting
- **Two-way Selection**: Device selection in left panel automatically updates map markers; clicking map markers selects devices
- **Visual Indicators**: Selected devices show larger radius (10px vs 8px) and blue border (#006dfe)
- **Status Colors**: Critical (#dc3545), Warning (#ffc107), Normal (#28a745) based on Days Remaining Inventory
- **Performance**: Address coordinates cached in `addressCoordinates` object to avoid repeated geocoding
- **Error Handling**: Graceful fallback for missing addresses or geocoding failures
- **Layout**: Map fits within 50/50 grid layout with proper height constraints and internal scrolling

## API Endpoints Reference

### Device Management
- `GET /api/devices` - List all devices with cabinet configurations
- `POST /api/devices` - Create new device
- `PUT /api/devices/<id>` - Update device
- `DELETE /api/devices/<id>` - Delete device (soft delete)
- `POST /api/devices/bulk-delete` - Delete multiple devices

### Planogram Management
- `GET /api/planograms/<key>` - Get planogram with all slot data
- `POST /api/planograms` - Save/update planogram
- `GET /api/planograms/export` - Export all planograms

### Product Management
- `GET /api/products` - List all products (optional ?category=filter)
- `GET /api/products/<id>` - Get single product
- `GET /api/products/categories` - Get all product categories

### Sales Analytics
- `GET /api/sales` - List sales data (supports pagination: ?page=1&per_page=20)
- `GET /api/sales/summary` - Sales summary statistics
- `GET /api/sales/asset-report` - Asset-based sales report (supports date range)
- `GET /api/sales/product-report` - Product-based sales report (supports date range)
- `POST /api/sales/generate-demo-data` - Generate demo sales data

### Location Management
- `GET /api/locations` - List all locations
- `POST /api/locations` - Create new location
- `PUT /api/locations/<id>` - Update location
- `DELETE /api/locations/<id>` - Delete location

### Route Management
- `GET /api/routes` - List all routes
- `POST /api/routes` - Create new route
- `PUT /api/routes/<id>` - Update route
- `DELETE /api/routes/<id>` - Delete route

### Type Definitions
- `GET /api/device-types` - List device types
- `POST /api/device-types` - Create device type
- `GET /api/cabinet-types` - List cabinet types
- `POST /api/cabinet-types` - Create cabinet type

### DEX File Processing & Grid Analysis
- `POST /api/dex/parse` - Parse DEX file and automatically detect grid patterns
- `GET /api/dex/reads` - List all DEX file reads
- `GET /api/dex/reads/<id>` - Get specific DEX file read details
- `GET /api/dex/pa-records/<id>` - Get PA records with grid metadata for DEX file
- `GET /api/dex/grid-layout/<id>` - Get structured grid layout data for visualization
- `GET /api/dex/grid-info/<id>` - Get grid pattern detection metadata and confidence scores
- `GET /api/dex/records/<id>` - Get all parsed DEX records for a specific read

### Admin Functions
- `GET /api/admin/devices/deleted` - List soft-deleted devices
- `POST /api/admin/devices/<id>/recover` - Recover soft-deleted device
- `GET /api/admin/planograms/<key>/cleared-slots` - Get cleared slot history
- `POST /api/query` - Execute direct SQL query (admin only)

### Utility
- `GET /api/health` - Health check
- `POST /api/migrate` - Migrate localStorage data to database

## Documentation

- **`docs/style_guide.md`** - UI/UX design system and component library
- **`route-planning-analysis.md`** - Analysis of route planning page implementation

When making changes, update relevant documentation to maintain accuracy.