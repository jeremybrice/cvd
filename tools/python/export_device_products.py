import sqlite3
import csv

def export_device_products():
    # Connect to database
    db = sqlite3.connect('cvd.db')
    cursor = db.cursor()
    
    # Complex query to get all device, cabinet, planogram, and product data
    query = """
    SELECT 
        d.asset,
        d.cooler as device_name,
        dt.name as device_type,
        d.model,
        ct.name as cabinet_type,
        cc.model_name as cabinet_model,
        cc.cabinet_index,
        p.planogram_key,
        ps.slot_position,
        CASE 
            WHEN ps.product_id IS NULL THEN 'EMPTY SLOT'
            ELSE pr.name
        END as product_name,
        CASE 
            WHEN ps.product_id IS NULL THEN NULL
            ELSE ps.price
        END as price,
        ps.capacity
    FROM devices d
    LEFT JOIN device_types dt ON d.device_type_id = dt.id
    LEFT JOIN cabinet_configurations cc ON d.id = cc.device_id
    LEFT JOIN cabinet_types ct ON cc.cabinet_type_id = ct.id
    LEFT JOIN planograms p ON p.cabinet_id = cc.id
    LEFT JOIN planogram_slots ps ON p.id = ps.planogram_id
    LEFT JOIN products pr ON ps.product_id = pr.id
    WHERE d.deleted_at IS NULL
    ORDER BY d.asset, cc.cabinet_index, ps.slot_position
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Get column names
    column_names = [description[0] for description in cursor.description]
    
    # Write to CSV
    with open('device_products.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(column_names)
        writer.writerows(rows)
    
    db.close()
    print(f"Exported {len(rows)} rows to device_products.csv")
    return len(rows)

if __name__ == "__main__":
    export_device_products()