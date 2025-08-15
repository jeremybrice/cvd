-- Migration: Cabinet-Centric Service Orders
-- Date: 2025-07-24
-- Description: Convert from device-centric to cabinet-centric service order system

-- Step 1: Delete all demo data
DELETE FROM service_order_items;
DELETE FROM service_orders;
DELETE FROM service_visits;

-- Step 2: Drop the old service_order_items table
DROP TABLE IF EXISTS service_order_items;

-- Step 3: Create new service_order_cabinets table
CREATE TABLE service_order_cabinets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_order_id INTEGER NOT NULL,
    cabinet_configuration_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_order_id) REFERENCES service_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (cabinet_configuration_id) REFERENCES cabinet_configurations(id)
);

-- Step 4: Create service_order_cabinet_items table
CREATE TABLE service_order_cabinet_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_order_cabinet_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity_needed INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_order_cabinet_id) REFERENCES service_order_cabinets(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Step 5: Add cabinet reference to service_visits
ALTER TABLE service_visits ADD COLUMN service_order_cabinet_id INTEGER REFERENCES service_order_cabinets(id);

-- Step 6: Create service_visit_items table (as specified in the spec)
CREATE TABLE service_visit_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_visit_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity_filled INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_visit_id) REFERENCES service_visits(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Step 7: Create indexes for performance
CREATE INDEX idx_service_order_cabinets_order_id ON service_order_cabinets(service_order_id);
CREATE INDEX idx_service_order_cabinets_cabinet_id ON service_order_cabinets(cabinet_configuration_id);
CREATE INDEX idx_service_order_cabinet_items_cabinet_id ON service_order_cabinet_items(service_order_cabinet_id);
CREATE INDEX idx_service_order_cabinet_items_product_id ON service_order_cabinet_items(product_id);
CREATE INDEX idx_service_visits_cabinet_id ON service_visits(service_order_cabinet_id);
CREATE INDEX idx_service_visit_items_visit_id ON service_visit_items(service_visit_id);
CREATE INDEX idx_service_visit_items_product_id ON service_visit_items(product_id);

-- Step 8: Update service_orders table to ensure proper fields
-- Add any missing fields if needed
-- (The table already exists with proper structure based on previous analysis)