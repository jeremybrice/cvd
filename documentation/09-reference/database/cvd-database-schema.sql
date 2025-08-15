-- CVD (Vision Device Configuration) Database Schema
-- SQLite database structure for vending machine device management
-- Generated from app.py

-- Drop tables if they exist (for clean recreation)
-- Note: Order matters due to foreign key constraints
DROP TABLE IF EXISTS dex_pa_records;
DROP TABLE IF EXISTS dex_records;
DROP TABLE IF EXISTS dex_reads;
DROP TABLE IF EXISTS slot_metrics;
DROP TABLE IF EXISTS service_order_items;
DROP TABLE IF EXISTS service_orders;
DROP TABLE IF EXISTS device_routes;
DROP TABLE IF EXISTS device_metrics;
DROP TABLE IF EXISTS service_visits;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS planogram_slots;
DROP TABLE IF EXISTS planograms;
DROP TABLE IF EXISTS cabinet_configurations;
DROP TABLE IF EXISTS devices;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS cabinet_types;
DROP TABLE IF EXISTS device_types;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS route_planning_config;

-- Create locations table
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create routes table
CREATE TABLE IF NOT EXISTS routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    route_number TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create device_types table
CREATE TABLE IF NOT EXISTS device_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    allows_additional_cabinets BOOLEAN NOT NULL
);

-- Create cabinet_types table
CREATE TABLE IF NOT EXISTS cabinet_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    rows INTEGER NOT NULL,
    cols INTEGER NOT NULL,
    icon TEXT NOT NULL
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    image TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create devices table
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset TEXT UNIQUE NOT NULL,
    cooler TEXT NOT NULL,
    location_id INTEGER,
    model TEXT NOT NULL,
    device_type_id INTEGER NOT NULL,
    route_id INTEGER,
    deleted_at TIMESTAMP,
    deleted_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL,
    FOREIGN KEY (device_type_id) REFERENCES device_types(id),
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE SET NULL
);

-- Create cabinet_configurations table
CREATE TABLE IF NOT EXISTS cabinet_configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    cabinet_type_id INTEGER NOT NULL,
    model_name TEXT,
    is_parent BOOLEAN DEFAULT 0,
    cabinet_index INTEGER NOT NULL,
    rows INTEGER NOT NULL,
    columns INTEGER NOT NULL,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    FOREIGN KEY (cabinet_type_id) REFERENCES cabinet_types(id)
);

-- Create planograms table
CREATE TABLE IF NOT EXISTS planograms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cabinet_id INTEGER NOT NULL,
    planogram_key TEXT UNIQUE NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cabinet_id) REFERENCES cabinet_configurations(id) ON DELETE CASCADE
);

-- Create planogram_slots table
CREATE TABLE IF NOT EXISTS planogram_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planogram_id INTEGER NOT NULL,
    slot_position TEXT NOT NULL,
    product_id INTEGER,
    product_name TEXT,
    quantity INTEGER DEFAULT 0,
    capacity INTEGER DEFAULT 0,
    par_level INTEGER DEFAULT 0,
    price DECIMAL(10,2),
    cleared_at TIMESTAMP,
    cleared_by TEXT,
    previous_product_id INTEGER,
    FOREIGN KEY (planogram_id) REFERENCES planograms(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
    FOREIGN KEY (previous_product_id) REFERENCES products(id) ON DELETE SET NULL,
    UNIQUE(planogram_id, slot_position)
);

-- Create sales table
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    sale_units INTEGER NOT NULL,
    sale_cash DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Create service_visits table for tracking device service history
CREATE TABLE IF NOT EXISTS service_visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    route_id INTEGER,
    service_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    units_restocked INTEGER DEFAULT 0,
    service_type TEXT CHECK(service_type IN ('routine', 'emergency', 'maintenance')),
    technician_id INTEGER,
    duration_minutes INTEGER,
    notes TEXT,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE SET NULL
);

-- Create device_metrics table for caching calculated metrics
CREATE TABLE IF NOT EXISTS device_metrics (
    device_id INTEGER PRIMARY KEY,
    sold_out_count INTEGER DEFAULT 0,
    days_remaining_inventory REAL,
    data_collection_rate REAL DEFAULT 100.0,
    product_level_percent REAL,
    units_to_par INTEGER DEFAULT 0,
    last_calculated TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

-- Create route_planning_config table for configuration settings
CREATE TABLE IF NOT EXISTS route_planning_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    critical_dri_threshold INTEGER DEFAULT 1,
    warning_dri_threshold INTEGER DEFAULT 3,
    ok_dri_threshold INTEGER DEFAULT 7,
    auto_select_critical BOOLEAN DEFAULT TRUE,
    metrics_cache_ttl_minutes INTEGER DEFAULT 15
);

-- Create service_orders table
CREATE TABLE IF NOT EXISTS service_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    total_units INTEGER,
    estimated_duration_minutes INTEGER,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE SET NULL
);

-- Create service_order_items table
CREATE TABLE IF NOT EXISTS service_order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_order_id INTEGER NOT NULL,
    device_id INTEGER NOT NULL,
    cabinet_index INTEGER,
    product_id INTEGER,
    quantity_needed INTEGER,
    FOREIGN KEY (service_order_id) REFERENCES service_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);

-- Create slot_metrics table for individual slot-level metrics
CREATE TABLE IF NOT EXISTS slot_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planogram_slot_id INTEGER NOT NULL UNIQUE,
    
    -- Calculated metrics
    is_sold_out INTEGER DEFAULT 0,
    days_remaining_inventory INTEGER,
    product_level_percent INTEGER,
    units_to_par INTEGER,
    
    -- Sales velocity data
    sales_28_day INTEGER DEFAULT 0,
    sales_all_time INTEGER DEFAULT 0,
    days_with_sales INTEGER DEFAULT 0,
    daily_velocity REAL DEFAULT 0.0,
    
    -- Metadata
    last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    calculation_version INTEGER DEFAULT 1,
    
    FOREIGN KEY (planogram_slot_id) REFERENCES planogram_slots(id) ON DELETE CASCADE
);

-- Create device_routes table for many-to-many relationship
CREATE TABLE IF NOT EXISTS device_routes (
    device_id INTEGER NOT NULL,
    route_id INTEGER NOT NULL,
    PRIMARY KEY (device_id, route_id),
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
);

-- Create DEX-related tables
CREATE TABLE IF NOT EXISTS dex_reads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    machine_serial VARCHAR(50),
    manufacturer VARCHAR(10),
    dex_version VARCHAR(20),
    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    raw_content TEXT NOT NULL,
    total_records INTEGER,
    parsed_successfully BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    error_line INTEGER,
    error_field INTEGER
);

CREATE TABLE IF NOT EXISTS dex_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dex_read_id INTEGER NOT NULL,
    record_type VARCHAR(10) NOT NULL,
    record_subtype VARCHAR(10),
    line_number INTEGER NOT NULL,
    raw_record TEXT NOT NULL,
    parsed_data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dex_read_id) REFERENCES dex_reads(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dex_pa_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dex_read_id INTEGER NOT NULL,
    record_subtype VARCHAR(10) NOT NULL,
    selection_number VARCHAR(10),
    price_cents INTEGER,
    capacity INTEGER,
    units_sold INTEGER,
    revenue_cents INTEGER,
    test_vends INTEGER,
    free_vends INTEGER,
    cash_sales INTEGER,
    cash_sales_cents INTEGER,
    cashless_sales INTEGER,
    cashless_sales_cents INTEGER,
    discount_sales INTEGER,
    discount_sales_cents INTEGER,
    line_number INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dex_read_id) REFERENCES dex_reads(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_devices_asset ON devices(asset);
CREATE INDEX IF NOT EXISTS idx_cabinets_device ON cabinet_configurations(device_id);
CREATE INDEX IF NOT EXISTS idx_planograms_key ON planograms(planogram_key);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_slots_product ON planogram_slots(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_device ON sales(device_id);
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_created ON sales(created_at);
CREATE INDEX IF NOT EXISTS idx_device_routes_route ON device_routes(route_id);

-- New indexes for route planning functionality
CREATE INDEX IF NOT EXISTS idx_service_visits_device ON service_visits(device_id);
CREATE INDEX IF NOT EXISTS idx_service_visits_date ON service_visits(service_date);
CREATE INDEX IF NOT EXISTS idx_device_metrics_calculated ON device_metrics(last_calculated);
CREATE INDEX IF NOT EXISTS idx_sales_device_date ON sales(device_id, created_at);
CREATE INDEX IF NOT EXISTS idx_devices_deleted ON devices(deleted_at);
CREATE INDEX IF NOT EXISTS idx_service_orders_route ON service_orders(route_id);
CREATE INDEX IF NOT EXISTS idx_service_order_items_order ON service_order_items(service_order_id);

-- Indexes for slot_metrics table
CREATE INDEX IF NOT EXISTS idx_slot_metrics_planogram_slot ON slot_metrics(planogram_slot_id);
CREATE INDEX IF NOT EXISTS idx_slot_metrics_last_calc ON slot_metrics(last_calculated);

-- Indexes for DEX tables
CREATE INDEX IF NOT EXISTS idx_dex_reads_machine_serial ON dex_reads(machine_serial);
CREATE INDEX IF NOT EXISTS idx_dex_reads_timestamp ON dex_reads(upload_timestamp);
CREATE INDEX IF NOT EXISTS idx_dex_records_read_id ON dex_records(dex_read_id);
CREATE INDEX IF NOT EXISTS idx_dex_records_type ON dex_records(record_type);
CREATE INDEX IF NOT EXISTS idx_dex_pa_records_read_id ON dex_pa_records(dex_read_id);
CREATE INDEX IF NOT EXISTS idx_dex_pa_records_selection ON dex_pa_records(selection_number);

-- Insert default data for device_types
INSERT OR IGNORE INTO device_types (id, name, description, allows_additional_cabinets) VALUES 
(1, 'PicoVision', 'Multi-cabinet vending machine', 1),
(2, 'Single Cabinet', 'Single cabinet vending machine', 0);

-- Insert default data for cabinet_types  
INSERT OR IGNORE INTO cabinet_types (id, name, description, rows, cols, icon) VALUES
(1, 'Cooler', 'Refrigerated cabinet for cold beverages', 5, 8, '❄️'),
(2, 'Freezer', 'Frozen product cabinet', 5, 8, '🧊'),
(3, 'Ambient', 'Room temperature snacks and beverages', 6, 9, '🍪'),
(4, 'Ambient+', 'Extended ambient cabinet', 6, 9, '🍿');

-- Insert default route planning config
INSERT OR IGNORE INTO route_planning_config (id, critical_dri_threshold, warning_dri_threshold, ok_dri_threshold, auto_select_critical, metrics_cache_ttl_minutes)
VALUES (1, 1, 3, 7, TRUE, 15);

-- Comments about key design decisions:
-- 1. Devices support soft deletion via deleted_at timestamp
-- 2. Cabinet configurations use camelCase properties for frontend compatibility
-- 3. Planogram slots have foreign key relationships to products table
-- 4. DEX PA records include row/column fields for grid pattern analysis
-- 5. All timestamps use CURRENT_TIMESTAMP default
-- 6. Foreign keys include appropriate CASCADE/SET NULL behaviors
-- 7. Unique constraints prevent duplicate data where needed
-- 8. Indexes optimize common query patterns for performance