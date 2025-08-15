#!/usr/bin/env python3
"""
Test script for cabinet-centric service orders
"""

import sqlite3
import json

def test_database_structure():
    """Test that all new tables were created correctly"""
    db = sqlite3.connect('cvd.db')
    cursor = db.cursor()
    
    print("Testing database structure...")
    
    # Check new tables exist
    tables = ['service_order_cabinets', 'service_order_cabinet_items', 'service_visit_items']
    for table in tables:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        result = cursor.fetchone()
        if result:
            print(f"✓ Table {table} exists")
        else:
            print(f"✗ Table {table} missing!")
    
    # Check service_visits has new column
    cursor.execute("PRAGMA table_info(service_visits)")
    columns = {col[1] for col in cursor.fetchall()}
    if 'service_order_cabinet_id' in columns:
        print("✓ service_visits.service_order_cabinet_id column exists")
    else:
        print("✗ service_visits.service_order_cabinet_id column missing!")
    
    # Check old table is gone
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='service_order_items'")
    if cursor.fetchone():
        print("✗ Old service_order_items table still exists!")
    else:
        print("✓ Old service_order_items table removed")
    
    db.close()

def test_create_service_order():
    """Test creating a service order through the API"""
    print("\nTesting service order creation...")
    
    # This would normally be done through the API
    # For now, just show the expected structure
    test_data = {
        "routeId": 1,
        "cabinetSelections": [
            {"deviceId": 111, "cabinetIndex": 0},
            {"deviceId": 111, "cabinetIndex": 1},
            {"deviceId": 222, "cabinetIndex": 0}
        ],
        "createdBy": "test-user"
    }
    
    print("Test payload structure:")
    print(json.dumps(test_data, indent=2))
    
    # Check cabinet configurations exist
    db = sqlite3.connect('cvd.db')
    cursor = db.cursor()
    
    for selection in test_data['cabinetSelections']:
        cursor.execute('''
            SELECT cc.id, d.asset, ct.name 
            FROM cabinet_configurations cc
            JOIN devices d ON cc.device_id = d.id
            JOIN cabinet_types ct ON cc.cabinet_type_id = ct.id
            WHERE cc.device_id = ? AND cc.cabinet_index = ?
        ''', (selection['deviceId'], selection['cabinetIndex']))
        
        result = cursor.fetchone()
        if result:
            print(f"✓ Found cabinet config: Device {selection['deviceId']}, Cabinet {selection['cabinetIndex']} -> ID {result[0]}")
        else:
            print(f"✗ Missing cabinet config: Device {selection['deviceId']}, Cabinet {selection['cabinetIndex']}")
    
    db.close()

def test_slot_metrics():
    """Test that slot metrics are being used"""
    print("\nTesting slot metrics integration...")
    
    db = sqlite3.connect('cvd.db')
    cursor = db.cursor()
    
    # Check if slot_metrics table has data
    cursor.execute("SELECT COUNT(*) FROM slot_metrics")
    count = cursor.fetchone()[0]
    print(f"Slot metrics count: {count}")
    
    # Sample query to show how cabinet metrics would be aggregated
    cursor.execute('''
        SELECT 
            cc.device_id,
            cc.cabinet_index,
            COUNT(sm.id) as metric_count,
            SUM(sm.units_to_par) as total_units_to_par
        FROM cabinet_configurations cc
        JOIN planograms p ON p.cabinet_id = cc.id
        JOIN planogram_slots ps ON ps.planogram_id = p.id
        LEFT JOIN slot_metrics sm ON sm.planogram_slot_id = ps.id
        WHERE cc.device_id IN (111, 222)
        GROUP BY cc.device_id, cc.cabinet_index
        LIMIT 5
    ''')
    
    results = cursor.fetchall()
    print("\nCabinet-level metrics aggregation:")
    for row in results:
        print(f"  Device {row[0]}, Cabinet {row[1]}: {row[2]} metrics, {row[3] or 0} units to par")
    
    db.close()

if __name__ == '__main__':
    print("Cabinet-Centric Service Orders Test\n" + "="*40)
    test_database_structure()
    test_create_service_order()
    test_slot_metrics()
    print("\nTest complete!")