"""
Knowledge Base for CVD Vending Machine Management System
Provides comprehensive guidance about pages, tools, and features for the AI chatbot.
"""

PAGE_KNOWLEDGE = {
    "coolers": {
        "name": "Device Management (PCP)",
        "file": "pages/PCP.html",
        "purpose": "View, manage, and organize all vending machine devices in your fleet",
        "key_features": [
            "Tabular device listing with sortable columns",
            "Device status monitoring and health indicators",
            "Bulk device management and operations",
            "Quick device search and filtering",
            "Device deletion and recovery options",
            "Export device data to CSV"
        ],
        "common_tasks": [
            "View all devices: Navigate to #coolers to see complete device list",
            "Search devices: Use search bar to find specific devices by name or location",
            "Sort devices: Click column headers to sort by asset, location, route, etc.",
            "Delete devices: Select devices and use bulk delete option",
            "Export data: Use export button to download device list as CSV",
            "View device details: Click on any device row to see full configuration"
        ],
        "navigation": "Click 'Coolers' in main menu or use #coolers URL hash"
    },
    
    "new-device": {
        "name": "Device Configuration Wizard (INVD)",
        "file": "pages/INVD.html", 
        "purpose": "Configure new vending machine devices with multi-cabinet support",
        "key_features": [
            "5-step device configuration wizard",
            "Multi-cabinet device support (up to 3 cabinets)",
            "Cabinet type selection (Cooler, Freezer, Ambient, Ambient+)",
            "Layout configuration (5×8 standard, 6×9 Ambient+)",
            "Location and route assignment",
            "Device photo upload capability",
            "Configuration validation and preview"
        ],
        "common_tasks": [
            "Add new device: Complete all 5 wizard steps in sequence",
            "Configure cabinets: Select cabinet types and layouts for each unit",
            "Set device info: Enter asset number, model, and location details",
            "Assign routes: Choose appropriate delivery/service route",
            "Upload photos: Add device photos for visual identification",
            "Save configuration: Complete wizard to create new device"
        ],
        "navigation": "Click 'Add New Device' in main menu or use #new-device URL hash",
        "wizard_steps": [
            "Step 1: Device Information (asset, model, location)",
            "Step 2: Cabinet Configuration (type, layout, quantity)",
            "Step 3: Route Assignment (delivery/service scheduling)",
            "Step 4: Photo Upload (device identification)",
            "Step 5: Review and Save (final validation)"
        ]
    },
    
    "planogram": {
        "name": "Planogram Management (NSPT)",
        "file": "pages/NSPT.html",
        "purpose": "Design and manage product layouts for vending machine cabinets",
        "key_features": [
            "Drag-and-drop planogram builder",
            "Product catalog with categories",
            "Individual cabinet planogram support",
            "Slot-level product assignment",
            "Quantity, capacity, and par level management",
            "Pricing configuration per slot",
            "Visual planogram preview",
            "Auto-save functionality"
        ],
        "common_tasks": [
            "Select device: Choose device and cabinet to work with",
            "Design layout: Drag products from catalog to planogram slots",
            "Set quantities: Configure capacity, par levels, and current stock",
            "Adjust pricing: Set individual slot prices if needed",
            "Clear slots: Remove products from slots as needed",
            "Save planogram: Changes auto-save to database",
            "Copy layouts: Duplicate successful planograms to other devices"
        ],
        "navigation": "Click 'Planogram' in main menu or use #planogram URL hash",
        "product_categories": [
            "Beverages (cold drinks, sodas, water)",
            "Snacks (chips, crackers, candy)",
            "Food (sandwiches, salads, prepared meals)",
            "Healthy Options (fruits, nuts, protein bars)"
        ]
    },
    
    "database": {
        "name": "Database Viewer",
        "file": "pages/database-viewer.html",
        "purpose": "View and export system data for analysis and reporting",
        "key_features": [
            "Direct database table viewing",
            "CSV export functionality",
            "Data filtering and search",
            "Table relationship visualization",
            "Query result display",
            "Data validation checking"
        ],
        "common_tasks": [
            "View data: Select tables to examine system data",
            "Export CSV: Download table data for external analysis",
            "Filter records: Use search to find specific data",
            "Validate data: Check for inconsistencies or errors",
            "Analyze relationships: Understand data connections"
        ],
        "navigation": "Click 'Database' in main menu or use #database URL hash"
    },
    
    "company-settings": {
        "name": "Company Settings",
        "file": "pages/company-settings.html",
        "purpose": "Configure company-wide settings and preferences",
        "key_features": [
            "Company information management",
            "System configuration options",
            "User preferences and defaults",
            "Operational parameters",
            "Integration settings"
        ],
        "common_tasks": [
            "Update company info: Modify business details and contact information",
            "Configure defaults: Set system-wide default values",
            "Adjust preferences: Customize user experience settings",
            "Manage integrations: Configure external system connections"
        ],
        "navigation": "Click 'Settings' in main menu or use #company-settings URL hash"
    },
    
    "route-planning": {
        "name": "Route Planning",
        "file": "pages/route-planning.html",
        "purpose": "Plan and organize delivery/service routes for efficient operations",
        "key_features": [
            "Route creation and management",
            "Device assignment to routes",
            "Route optimization tools",
            "Scheduling capabilities",
            "Performance tracking"
        ],
        "common_tasks": [
            "Create routes: Define new delivery/service routes",
            "Assign devices: Add devices to specific routes",
            "Optimize paths: Arrange stops for maximum efficiency",
            "Schedule visits: Plan regular service intervals",
            "Monitor performance: Track route effectiveness"
        ],
        "navigation": "Click 'Routes' in main menu or use #route-planning URL hash"
    },
    
    "route-schedule": {
        "name": "Route Scheduling",
        "file": "pages/route-schedule.html",
        "purpose": "Interactive route scheduling with map visualization",
        "key_features": [
            "50/50 split layout (device list + interactive map)",
            "Real-time address geocoding",
            "Two-way device selection (list ↔ map)",
            "Visual status indicators on map",
            "Leaflet.js map integration",
            "Route optimization with real addresses"
        ],
        "common_tasks": [
            "View route map: See device locations on interactive map",
            "Select devices: Click devices in list or map markers",
            "Plan route: Visualize optimal stop sequence",
            "Check status: Monitor device health via color coding",
            "Optimize schedule: Arrange visits by geography"
        ],
        "navigation": "Access through route planning or direct URL",
        "map_features": [
            "Color-coded status (Critical: red, Warning: yellow, Normal: green)",
            "Two-way selection sync between list and map",
            "Real Michigan addresses with geocoding",
            "Zoom and pan controls for detailed planning"
        ]
    },
    
    "asset-sales": {
        "name": "Asset Sales Reporting",
        "file": "pages/asset-sales.html",
        "purpose": "Analyze sales performance by individual vending machine assets",
        "key_features": [
            "Asset-based sales analytics",
            "Performance comparison charts",
            "Revenue tracking by device",
            "Time-based analysis",
            "Export capabilities"
        ],
        "common_tasks": [
            "View asset performance: See revenue by individual device",
            "Compare devices: Analyze relative performance",
            "Track trends: Monitor sales over time",
            "Export reports: Download data for further analysis",
            "Identify top performers: Find most profitable devices"
        ],
        "navigation": "Click 'Asset Sales' in main menu or use #asset-sales URL hash"
    },
    
    "product-sales": {
        "name": "Product Sales Reporting", 
        "file": "pages/product-sales.html",
        "purpose": "Analyze sales performance by product category and individual items",
        "key_features": [
            "Product-based sales analytics",
            "Category performance analysis",
            "Revenue tracking by product",
            "Inventory velocity insights",
            "Profit margin analysis"
        ],
        "common_tasks": [
            "View product performance: See sales by individual products",
            "Analyze categories: Compare product category performance",
            "Track inventory velocity: Monitor how quickly products sell",
            "Optimize pricing: Adjust prices based on performance data",
            "Plan restocking: Use sales data to guide inventory decisions"
        ],
        "navigation": "Click 'Product Sales' in main menu or use #product-sales URL hash"
    },

    "index": {
        "name": "Main Navigation Shell (index.html)",
        "file": "index.html",
        "purpose": "The main navigation shell and iframe router that provides the primary interface for the CVD application with comprehensive navigation, authentication, and user management features",
        "key_features": [
            "Top navigation bar with dropdown menus organized by function",
            "User authentication and session management with automatic timeout",
            "Iframe-based content loading for modular architecture",
            "Breadcrumb navigation that updates based on current route",
            "AI chat widget for context-aware assistance",
            "Command palette with keyboard shortcuts (Cmd/Ctrl + K)",
            "Cross-frame messaging system for component communication",
            "Role-based access control with visual feedback",
            "PWA support with manifest and service worker integration",
            "Toast notifications for user feedback and system messages"
        ],
        "navigation_structure": [
            "Routes dropdown: Route Schedule, Service Orders",
            "Devices dropdown: Device List, Planograms", 
            "Analytics dropdown: Device Performance, Product Performance, Device Issues, Revenue Analysis",
            "Settings dropdown: Customer Settings, Company Settings, Users (admin only)",
            "Help dropdown: Customer Support, Knowledge Base, Database Viewer, DEX Parser"
        ],
        "keyboard_shortcuts": [
            "Cmd/Ctrl + K: Open command palette",
            "Alt + 1-5: Open navigation dropdown menus",
            "Alt + H: Go to home dashboard",
            "Alt + D: Device list",
            "Alt + P: Planograms",
            "Ctrl + R: Refresh current page",
            "?: Show keyboard shortcuts help",
            "Escape: Close command palette"
        ],
        "hash_routes": [
            "#home → home-dashboard.html (Business overview with map)",
            "#coolers → PCP.html (Device management listing)",
            "#new-device → INVD.html (Device configuration wizard)",
            "#planogram → NSPT.html (Planogram management)",
            "#service-orders → service-orders.html (Service order management)",
            "#route-schedule → route-schedule.html (Interactive route scheduling)",
            "#asset-sales → asset-sales.html (Device performance analytics)",
            "#product-sales → product-sales.html (Product performance analytics)",
            "#database → database-viewer.html (Admin only - Direct database access)",
            "#dex-parser → dex-parser.html (DEX file processing)",
            "#company-settings → company-settings.html (System configuration)",
            "#user-management → user-management.html (Admin only - User administration)",
            "#profile → profile.html (User profile management)"
        ],
        "cross_frame_communication": [
            "NAVIGATE: Navigate to different pages within the application",
            "REFRESH_DATA: Trigger data refresh in parent or child frames",
            "AUTH_ERROR: Handle authentication failures and redirect to login",
            "GLOBAL_ACTION: Execute system-wide actions affecting multiple components",
            "SHOW_TOAST: Display notification messages to users",
            "UPDATE_TITLE: Update page title and breadcrumb navigation",
            "KEYBOARD_EVENT: Handle keyboard shortcuts across frame boundaries"
        ],
        "role_access_control": [
            "Admin: Full access to all pages including database viewer and user management",
            "Manager: Access to operational pages excluding database viewer and user management",
            "Driver: Limited access to operational pages focused on service tasks",
            "Viewer: Read-only access to reports and analytics pages"
        ],
        "command_palette_features": [
            "Fuzzy search for commands with intelligent matching",
            "Grouped commands by category (Navigation, Actions, User, Help)",
            "Keyboard navigation with arrow keys and Enter selection",
            "Visual keyboard shortcuts displayed for each command",
            "Accessible via Cmd/Ctrl + K from any page",
            "Context-aware command suggestions based on current page"
        ],
        "ai_chat_widget": [
            "Floating chat button in bottom-right corner",
            "Context-aware assistance based on current page location",
            "Uses Claude API when available with fallback to rule-based responses",
            "Persistent across page navigation maintaining conversation context",
            "Knowledge base integration for CVD-specific guidance"
        ],
        "accessibility_features": [
            "Skip navigation link for screen readers",
            "ARIA labels and roles for semantic structure",
            "Keyboard navigation support for all interactive elements",
            "Focus management during page transitions",
            "Touch-friendly targets with minimum 44px size",
            "High contrast color schemes for visibility"
        ],
        "pwa_support": [
            "Manifest link for progressive web app installation",
            "Theme color and icon configuration",
            "Service worker registration for offline functionality",
            "App shell architecture for fast loading",
            "Background sync capabilities for offline actions"
        ],
        "technical_details": [
            "Iframe-based architecture for content isolation and modularity",
            "Session-based authentication with configurable timeout periods",
            "Breadcrumb navigation updates automatically based on current route hash",
            "Loading overlay during page transitions for smooth user experience",
            "Toast notification system for user feedback and error handling",
            "Origin validation for secure cross-frame messaging",
            "Responsive design supporting desktop and mobile devices"
        ],
        "common_tasks": [
            "Navigate pages: Use dropdown menus or keyboard shortcuts to access features",
            "Use command palette: Press Cmd/Ctrl + K to quickly search for commands",
            "Access help: Use AI chat widget or Help dropdown for assistance",
            "Manage user session: Use profile dropdown for account management and logout",
            "Switch between pages: Navigate using hash routes or main navigation",
            "Get contextual help: AI chat widget provides page-specific assistance",
            "Use keyboard shortcuts: Alt + number keys for quick menu access"
        ],
        "navigation": "Main entry point - accessed at application root URL"
    }
}

NAVIGATION_GUIDE = {
    "main_menu": {
        "location": "Top navigation bar in index.html",
        "items": [
            "Coolers - View all devices",
            "Add New Device - Configure new devices", 
            "Planogram - Design product layouts",
            "Database - View system data",
            "Settings - Company configuration",
            "Routes - Plan delivery routes",
            "Asset Sales - Device performance",
            "Product Sales - Product analytics"
        ]
    },
    "url_navigation": {
        "description": "Direct navigation using URL hash fragments",
        "examples": [
            "#coolers - Device management",
            "#new-device - Device configuration",
            "#planogram - Planogram management",
            "#database - Database viewer",
            "#company-settings - Settings",
            "#route-planning - Route planning",
            "#asset-sales - Asset reports",
            "#product-sales - Product reports"
        ]
    },
    "cross_page_communication": {
        "description": "Pages communicate via postMessage API",
        "common_actions": [
            "Device selection triggers planogram loading",
            "New device creation updates device list",
            "Settings changes affect all modules",
            "Route updates refresh device assignments"
        ]
    }
}

COMMON_WORKFLOWS = {
    "adding_new_device": {
        "description": "Complete process to add a new vending machine",
        "steps": [
            "Navigate to #new-device (Add New Device)",
            "Step 1: Enter device information (asset, model, location)",
            "Step 2: Configure cabinets (type, layout, quantity)",
            "Step 3: Assign to route for servicing",
            "Step 4: Upload device photos for identification",
            "Step 5: Review configuration and save",
            "Device appears in Coolers list immediately"
        ],
        "tips": [
            "Asset numbers must be unique",
            "Cabinet types determine available layouts",
            "Routes help organize service scheduling",
            "Photos help technicians identify devices"
        ]
    },
    
    "creating_planogram": {
        "description": "Design product layout for a vending machine cabinet",
        "steps": [
            "Navigate to #planogram (Planogram Management)",
            "Select device and cabinet from dropdown",
            "Drag products from catalog to planogram slots",
            "Set quantity, capacity, and par levels for each slot",
            "Adjust pricing if needed",
            "Changes auto-save to database",
            "Planogram is immediately available for restocking"
        ],
        "tips": [
            "Products are organized by category",
            "Par levels determine restock triggers",
            "Capacity sets maximum slot inventory",
            "Popular items should be in accessible slots"
        ]
    },
    
    "route_optimization": {
        "description": "Optimize delivery routes for efficiency",
        "steps": [
            "Navigate to #route-planning (Route Planning)",
            "Create or select existing route",
            "Assign devices to route based on geography",
            "Use #route-schedule for map visualization",
            "View devices on interactive map",
            "Optimize stop sequence for efficiency",
            "Save route configuration"
        ],
        "tips": [
            "Group nearby devices on same route",
            "Consider device status when planning visits",
            "Use map view to identify optimal sequences",
            "Critical devices (red) need immediate attention"
        ]
    },
    
    "sales_analysis": {
        "description": "Analyze business performance using sales reports",
        "steps": [
            "Navigate to #asset-sales for device performance",
            "Navigate to #product-sales for product analytics",
            "Review performance charts and metrics",
            "Filter by date range for specific periods",
            "Export data for detailed analysis",
            "Use insights to optimize operations"
        ],
        "tips": [
            "Asset reports show which devices are most profitable",
            "Product reports reveal best-selling items",
            "Use date filters to identify trends",
            "Export data for external analysis tools"
        ]
    },
    
    "using_main_navigation": {
        "description": "Master the main navigation system and keyboard shortcuts",
        "steps": [
            "Use dropdown menus from top navigation bar",
            "Access command palette with Cmd/Ctrl + K",
            "Use keyboard shortcuts (Alt + 1-5 for menus)",
            "Navigate directly with hash routes (#page-name)",
            "Use AI chat widget for contextual help",
            "Manage user session through profile dropdown"
        ],
        "tips": [
            "Command palette provides fastest navigation",
            "Keyboard shortcuts work from any page",
            "AI chat widget is context-aware",
            "Hash routes can be bookmarked",
            "Session timeout provides security",
            "Role-based access controls what you can see"
        ]
    }
}

TROUBLESHOOTING_GUIDE = {
    "device_not_appearing": {
        "issue": "New device doesn't appear in device list",
        "solutions": [
            "Ensure all wizard steps were completed",
            "Check that asset number is unique",
            "Refresh the page or navigate to #coolers",
            "Verify device was saved successfully"
        ]
    },
    
    "planogram_not_loading": {
        "issue": "Planogram doesn't load for selected device",
        "solutions": [
            "Ensure device has cabinet configuration",
            "Check that device was saved properly",
            "Verify cabinet type is supported",
            "Try refreshing the planogram page"
        ]
    },
    
    "product_drag_drop_issues": {
        "issue": "Can't drag products to planogram slots",
        "solutions": [
            "Ensure planogram is loaded first",
            "Check that slot is not already occupied",
            "Try refreshing the page",
            "Verify product catalog is loaded"
        ]
    },
    
    "route_map_not_loading": {
        "issue": "Route map doesn't display devices",
        "solutions": [
            "Check internet connection (map requires external tiles)",
            "Ensure devices have valid addresses",
            "Wait for geocoding to complete",
            "Try refreshing the route schedule page"
        ]
    },
    
    "export_not_working": {
        "issue": "CSV export doesn't download",
        "solutions": [
            "Check browser popup blocker settings",
            "Ensure sufficient data exists to export",
            "Try a different browser",
            "Verify file download permissions"
        ]
    },
    
    "command_palette_not_opening": {
        "issue": "Command palette doesn't open with Cmd/Ctrl + K",
        "solutions": [
            "Ensure you're on the main application (not login page)",
            "Try clicking in the main content area first",
            "Check if browser shortcuts are conflicting",
            "Refresh the page if keyboard events are not working",
            "Use mouse to access navigation menus as alternative"
        ]
    },
    
    "keyboard_shortcuts_not_working": {
        "issue": "Keyboard shortcuts (Alt + numbers) don't work",
        "solutions": [
            "Ensure focus is on the main application window",
            "Check if browser or OS shortcuts are conflicting",
            "Try clicking in the content area to focus the page",
            "Refresh the page to reset keyboard event handlers",
            "Use mouse navigation as alternative"
        ]
    },
    
    "iframe_content_not_loading": {
        "issue": "Page content doesn't load in the iframe",
        "solutions": [
            "Check browser console for JavaScript errors",
            "Ensure you have proper authentication session",
            "Try refreshing the entire page",
            "Clear browser cache and reload",
            "Check network connectivity for API calls"
        ]
    },
    
    "navigation_menu_not_showing": {
        "issue": "Dropdown menus don't appear when clicked",
        "solutions": [
            "Check if CSS is loading properly",
            "Clear browser cache and refresh",
            "Try a different browser to isolate the issue",
            "Check browser console for JavaScript errors",
            "Ensure popup blockers aren't interfering"
        ]
    },
    
    "chat_widget_not_responding": {
        "issue": "AI chat widget doesn't respond or appear",
        "solutions": [
            "Check if Anthropic API key is configured",
            "Verify internet connectivity for API calls",
            "Look for JavaScript errors in browser console",
            "Try refreshing the page to reinitialize widget",
            "Chat falls back to rule-based responses if API unavailable"
        ]
    }
}

FEATURE_REFERENCE = {
    "search_functionality": {
        "location": "Device management (PCP) page",
        "usage": "Type in search bar to filter devices by name, location, or asset number",
        "tips": "Search is case-insensitive and matches partial text"
    },
    
    "bulk_operations": {
        "location": "Device management (PCP) page",
        "usage": "Select multiple devices and perform bulk delete or export operations",
        "tips": "Use Ctrl+Click or Shift+Click for multiple selection"
    },
    
    "auto_save": {
        "location": "Planogram management (NSPT) page",
        "usage": "Changes are automatically saved to database",
        "tips": "No manual save required - changes persist immediately"
    },
    
    "drag_and_drop": {
        "location": "Planogram management (NSPT) page",
        "usage": "Drag products from catalog to planogram slots",
        "tips": "Drop on empty slots to assign products"
    },
    
    "photo_upload": {
        "location": "Device configuration wizard (INVD) page",
        "usage": "Upload device photos for identification",
        "tips": "Supports standard image formats (JPG, PNG, etc.)"
    },
    
    "interactive_map": {
        "location": "Route scheduling page",
        "usage": "View device locations on map with status indicators",
        "tips": "Click markers to select devices, colors indicate status"
    },
    
    "export_functionality": {
        "location": "Multiple pages (Database, Device management, Sales reports)",
        "usage": "Download data as CSV files for external analysis",
        "tips": "Exported files can be opened in Excel or other spreadsheet programs"
    },
    
    "command_palette": {
        "location": "Main navigation shell (index.html)",
        "usage": "Press Cmd/Ctrl + K to open fuzzy search for commands",
        "tips": "Fastest way to navigate - supports keyboard navigation with arrow keys"
    },
    
    "keyboard_shortcuts": {
        "location": "Main navigation shell (index.html)",
        "usage": "Alt + 1-5 for dropdown menus, Alt + H/D/P for common pages",
        "tips": "Works from any page within the application - see ? for full list"
    },
    
    "cross_frame_messaging": {
        "location": "Main navigation shell and all iframe pages",
        "usage": "Pages communicate via postMessage for navigation and data updates",
        "tips": "Enables seamless integration between main shell and loaded pages"
    },
    
    "breadcrumb_navigation": {
        "location": "Main navigation shell (index.html)",
        "usage": "Shows current location and allows quick navigation to parent sections",
        "tips": "Updates automatically based on current page route"
    },
    
    "ai_chat_assistant": {
        "location": "Floating widget in bottom-right corner",
        "usage": "Click chat button for context-aware help and guidance",
        "tips": "Maintains conversation context across page navigation"
    },
    
    "role_based_access": {
        "location": "Main navigation shell (index.html)",
        "usage": "Menu items and pages are filtered based on user role",
        "tips": "Admin sees all options, other roles have limited access"
    },
    
    "toast_notifications": {
        "location": "Main navigation shell (index.html)", 
        "usage": "System messages appear as temporary notifications",
        "tips": "Provide feedback for user actions and system events"
    }
}

def get_page_knowledge(page_hash):
    """Get knowledge for a specific page based on URL hash"""
    return PAGE_KNOWLEDGE.get(page_hash.replace('#', ''), {})

def get_navigation_help():
    """Get navigation guidance"""
    return NAVIGATION_GUIDE

def get_workflow_help(workflow_name=None):
    """Get workflow guidance"""
    if workflow_name:
        return COMMON_WORKFLOWS.get(workflow_name, {})
    return COMMON_WORKFLOWS

def get_troubleshooting_help(issue=None):
    """Get troubleshooting guidance"""
    if issue:
        return TROUBLESHOOTING_GUIDE.get(issue, {})
    return TROUBLESHOOTING_GUIDE

def get_feature_help(feature=None):
    """Get feature reference"""
    if feature:
        return FEATURE_REFERENCE.get(feature, {})
    return FEATURE_REFERENCE

def search_knowledge(query):
    """Search knowledge base for relevant information"""
    query = query.lower()
    results = []
    
    # Define searchable keywords for the index page
    index_keywords = [
        'navigation', 'main page', 'index', 'keyboard shortcuts', 'command palette',
        'shell', 'navbar', 'menu', 'dropdown', 'auth', 'authentication', 'login',
        'iframe', 'routing', 'breadcrumb', 'chat widget', 'shortcuts', 'accessibility',
        'pwa', 'progressive web app', 'cross frame', 'messaging', 'role based',
        'session management', 'hash routes', 'toast notifications'
    ]
    
    # Search page knowledge
    for page_id, page_info in PAGE_KNOWLEDGE.items():
        match_found = False
        
        # Standard search in name, purpose, and features
        if (query in page_info.get('name', '').lower() or 
            query in page_info.get('purpose', '').lower() or
            any(query in feature.lower() for feature in page_info.get('key_features', []))):
            match_found = True
        
        # Special keyword matching for index page
        if page_id == 'index' and any(keyword in query for keyword in index_keywords):
            match_found = True
        
        # Search in additional structured fields for index page
        if page_id == 'index':
            searchable_fields = ['navigation_structure', 'keyboard_shortcuts', 'hash_routes', 
                               'cross_frame_communication', 'role_access_control', 'command_palette_features',
                               'ai_chat_widget', 'accessibility_features', 'pwa_support', 'technical_details']
            for field in searchable_fields:
                field_content = page_info.get(field, [])
                if isinstance(field_content, list):
                    if any(query in item.lower() for item in field_content):
                        match_found = True
                        break
        
        if match_found:
            results.append({
                'type': 'page',
                'id': page_id,
                'title': page_info.get('name', ''),
                'description': page_info.get('purpose', ''),
                'navigation': page_info.get('navigation', '')
            })
    
    # Search workflows
    for workflow_id, workflow_info in COMMON_WORKFLOWS.items():
        if (query in workflow_info.get('description', '').lower() or
            any(query in step.lower() for step in workflow_info.get('steps', []))):
            results.append({
                'type': 'workflow',
                'id': workflow_id,
                'title': workflow_info.get('description', ''),
                'steps': workflow_info.get('steps', [])
            })
    
    # Search troubleshooting
    for issue_id, issue_info in TROUBLESHOOTING_GUIDE.items():
        if (query in issue_info.get('issue', '').lower() or
            any(query in solution.lower() for solution in issue_info.get('solutions', []))):
            results.append({
                'type': 'troubleshooting',
                'id': issue_id,
                'title': issue_info.get('issue', ''),
                'solutions': issue_info.get('solutions', [])
            })
    
    return results