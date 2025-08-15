from flask import g
import sqlite3

def get_db():
    """Get database connection from Flask g object"""
    if 'db' not in g:
        g.db = sqlite3.connect('cvd.db')
        g.db.row_factory = sqlite3.Row
    return g.db

class ServiceOrderService:
    """Service for creating and managing cabinet-centric service orders"""
    
    @staticmethod
    def create_service_order(route_id, cabinet_selections, created_by=None):
        """
        Create a service order from cabinet selections
        cabinet_selections: list of {deviceId, cabinetIndex}
        """
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Get the driver assigned to this route
            route_info = cursor.execute('''
                SELECT driver_id FROM routes WHERE id = ?
            ''', (route_id,)).fetchone()
            
            driver_id = route_info['driver_id'] if route_info else None
            
            # Calculate pick list from cabinet selections
            pick_list = ServiceOrderService.calculate_pick_list(cabinet_selections)
            
            # Calculate total units and estimated time
            total_units = sum(item['quantity'] for item in pick_list)
            estimated_minutes = len(cabinet_selections) * 10  # 10 minutes per cabinet
            
            # Create service order
            cursor.execute('''
                INSERT INTO service_orders 
                (route_id, driver_id, created_by, status, total_units, estimated_duration_minutes)
                VALUES (?, ?, ?, 'pending', ?, ?)
            ''', (route_id, driver_id, created_by, total_units, estimated_minutes))
            
            order_id = cursor.lastrowid
            
            # Create service order cabinet entries
            for selection in cabinet_selections:
                device_id = selection['deviceId']
                cabinet_index = selection['cabinetIndex']
                
                # Get cabinet configuration ID
                cabinet_config = cursor.execute('''
                    SELECT id FROM cabinet_configurations
                    WHERE device_id = ? AND cabinet_index = ?
                ''', (device_id, cabinet_index)).fetchone()
                
                if not cabinet_config:
                    raise ValueError(f"Cabinet configuration not found for device {device_id}, cabinet {cabinet_index}")
                
                # Create service order cabinet entry
                cursor.execute('''
                    INSERT INTO service_order_cabinets
                    (service_order_id, cabinet_configuration_id)
                    VALUES (?, ?)
                ''', (order_id, cabinet_config['id']))
                
                service_order_cabinet_id = cursor.lastrowid
                
                # Get products needed for this cabinet
                products_needed = cursor.execute('''
                    SELECT 
                        ps.product_id,
                        SUM(ps.par_level - ps.quantity) as quantity_needed
                    FROM planogram_slots ps
                    JOIN planograms p ON ps.planogram_id = p.id
                    WHERE p.cabinet_id = ?
                    AND ps.product_id != 1
                    AND ps.par_level > ps.quantity
                    GROUP BY ps.product_id
                ''', (cabinet_config['id'],)).fetchall()
                
                # Create service order cabinet items
                for product in products_needed:
                    cursor.execute('''
                        INSERT INTO service_order_cabinet_items
                        (service_order_cabinet_id, product_id, quantity_needed)
                        VALUES (?, ?, ?)
                    ''', (service_order_cabinet_id, product['product_id'], product['quantity_needed']))
            
            db.commit()
            
            return {
                'orderId': order_id,
                'totalUnits': total_units,
                'estimatedMinutes': estimated_minutes,
                'pickList': pick_list
            }
            
        except Exception as e:
            db.rollback()
            raise e
    
    @staticmethod
    def calculate_pick_list(cabinet_selections):
        """Calculate aggregated pick list across all selected cabinets"""
        db = get_db()
        cursor = db.cursor()
        
        # Build query to aggregate products needed
        product_totals = {}
        
        for selection in cabinet_selections:
            device_id = selection['deviceId']
            cabinet_index = selection['cabinetIndex']
            
            # Get cabinet configuration ID
            cabinet_config = cursor.execute('''
                SELECT id FROM cabinet_configurations
                WHERE device_id = ? AND cabinet_index = ?
            ''', (device_id, cabinet_index)).fetchone()
            
            if not cabinet_config:
                continue
            
            products = cursor.execute('''
                SELECT 
                    ps.product_id,
                    ps.product_name,
                    pr.category,
                    SUM(ps.par_level - ps.quantity) as quantity_needed
                FROM planogram_slots ps
                JOIN planograms p ON ps.planogram_id = p.id
                LEFT JOIN products pr ON ps.product_id = pr.id
                WHERE p.cabinet_id = ?
                AND ps.product_id != 1
                AND ps.par_level > ps.quantity
                GROUP BY ps.product_id, ps.product_name
            ''', (cabinet_config['id'],)).fetchall()
            
            for product in products:
                key = product['product_id']
                if key in product_totals:
                    product_totals[key]['quantity'] += product['quantity_needed']
                else:
                    product_totals[key] = {
                        'productId': product['product_id'],
                        'productName': product['product_name'],
                        'category': product['category'],
                        'quantity': product['quantity_needed']
                    }
        
        # Convert to list and sort by category, then name
        pick_list = list(product_totals.values())
        pick_list.sort(key=lambda x: (x['category'] or '', x['productName']))
        
        return pick_list
    
    @staticmethod
    def get_service_order_preview(cabinet_selections):
        """Generate a preview of what a service order would contain"""
        db = get_db()
        cursor = db.cursor()
        
        preview_data = {
            'cabinets': [],
            'deviceSummary': {},
            'pickList': ServiceOrderService.calculate_pick_list(cabinet_selections),
            'totalUnits': 0,
            'estimatedMinutes': len(cabinet_selections) * 10
        }
        
        # Group by device for summary
        device_cabinets = {}
        
        for selection in cabinet_selections:
            device_id = selection['deviceId']
            cabinet_index = selection['cabinetIndex']
            
            if device_id not in device_cabinets:
                device_cabinets[device_id] = []
            device_cabinets[device_id].append(cabinet_index)
            
            # Get cabinet and device details
            cabinet_details = cursor.execute('''
                SELECT 
                    cc.id as cabinet_config_id,
                    cc.cabinet_index,
                    ct.name as cabinet_type,
                    d.asset,
                    d.cooler,
                    l.name as location
                FROM cabinet_configurations cc
                JOIN cabinet_types ct ON cc.cabinet_type_id = ct.id
                JOIN devices d ON cc.device_id = d.id
                LEFT JOIN locations l ON d.location_id = l.id
                WHERE cc.device_id = ? AND cc.cabinet_index = ?
            ''', (device_id, cabinet_index)).fetchone()
            
            if cabinet_details:
                # Get products needed for this cabinet
                products_needed = cursor.execute('''
                    SELECT 
                        ps.product_id,
                        ps.product_name,
                        pr.category,
                        SUM(ps.par_level - ps.quantity) as quantity_needed
                    FROM planogram_slots ps
                    JOIN planograms p ON ps.planogram_id = p.id
                    LEFT JOIN products pr ON ps.product_id = pr.id
                    WHERE p.cabinet_id = ?
                    AND ps.product_id != 1
                    AND ps.par_level > ps.quantity
                    GROUP BY ps.product_id, ps.product_name
                ''', (cabinet_details['cabinet_config_id'],)).fetchall()
                
                cabinet_info = {
                    'deviceId': device_id,
                    'asset': cabinet_details['asset'],
                    'cooler': cabinet_details['cooler'],
                    'location': cabinet_details['location'],
                    'cabinetIndex': cabinet_index,
                    'cabinetType': cabinet_details['cabinet_type'],
                    'products': [dict(p) for p in products_needed],
                    'totalUnits': sum(p['quantity_needed'] for p in products_needed)
                }
                
                preview_data['cabinets'].append(cabinet_info)
                preview_data['totalUnits'] += cabinet_info['totalUnits']
        
        # Build device summary
        for device_id, cabinet_indices in device_cabinets.items():
            device_info = cursor.execute('''
                SELECT asset, cooler, l.name as location
                FROM devices d
                LEFT JOIN locations l ON d.location_id = l.id
                WHERE d.id = ?
            ''', (device_id,)).fetchone()
            
            if device_info:
                preview_data['deviceSummary'][str(device_id)] = {
                    'asset': device_info['asset'],
                    'cooler': device_info['cooler'],
                    'location': device_info['location'],
                    'cabinetCount': len(cabinet_indices),
                    'cabinetIndices': sorted(cabinet_indices)
                }
        
        return preview_data
    
    @staticmethod
    def execute_service_order_cabinet(service_order_cabinet_id, delivered_items):
        """
        Execute a single cabinet from a service order
        delivered_items: list of {productId, quantityFilled}
        """
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Get service order cabinet details
            cabinet_info = cursor.execute('''
                SELECT soc.*, so.id as order_id, cc.device_id, cc.cabinet_index
                FROM service_order_cabinets soc
                JOIN service_orders so ON soc.service_order_id = so.id
                JOIN cabinet_configurations cc ON soc.cabinet_configuration_id = cc.id
                WHERE soc.id = ?
            ''', (service_order_cabinet_id,)).fetchone()
            
            if not cabinet_info:
                raise ValueError("Service order cabinet not found")
            
            # Create service visit for this cabinet
            cursor.execute('''
                INSERT INTO service_visits
                (service_order_cabinet_id, service_type, user_id, notes)
                VALUES (?, 'routine', ?, 'Service order execution')
            ''', (service_order_cabinet_id, 1))  # TODO: Get actual user ID
            
            service_visit_id = cursor.lastrowid
            
            # Record delivered items
            total_units = 0
            for item in delivered_items:
                cursor.execute('''
                    INSERT INTO service_visit_items
                    (service_visit_id, product_id, quantity_filled)
                    VALUES (?, ?, ?)
                ''', (service_visit_id, item['productId'], item['quantityFilled']))
                
                total_units += item['quantityFilled']
                
                # Update planogram quantities
                cursor.execute('''
                    UPDATE planogram_slots
                    SET quantity = quantity + ?
                    WHERE planogram_id IN (
                        SELECT id FROM planograms WHERE cabinet_id = ?
                    ) AND product_id = ?
                ''', (item['quantityFilled'], cabinet_info['cabinet_configuration_id'], item['productId']))
            
            # Update service visit with total units and duration
            cursor.execute('''
                UPDATE service_visits
                SET duration_minutes = 10
                WHERE id = ?
            ''', (service_visit_id,))
            
            # Check if all cabinets in the order are executed
            cursor.execute('''
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN sv.id IS NOT NULL THEN 1 ELSE 0 END) as executed
                FROM service_order_cabinets soc
                LEFT JOIN service_visits sv ON sv.service_order_cabinet_id = soc.id
                WHERE soc.service_order_id = ?
            ''', (cabinet_info['order_id'],)).fetchone()
            
            # If all cabinets executed, update order status
            if cursor.lastrowid and cursor.fetchone()['total'] == cursor.fetchone()['executed']:
                cursor.execute('''
                    UPDATE service_orders
                    SET status = 'completed'
                    WHERE id = ?
                ''', (cabinet_info['order_id'],))
            elif cursor.execute('''SELECT status FROM service_orders WHERE id = ?''', 
                              (cabinet_info['order_id'],)).fetchone()['status'] == 'pending':
                # Update to in_progress if it was pending
                cursor.execute('''
                    UPDATE service_orders
                    SET status = 'in_progress'
                    WHERE id = ?
                ''', (cabinet_info['order_id'],))
            
            db.commit()
            
            return {
                'success': True,
                'serviceVisitId': service_visit_id,
                'totalUnits': total_units
            }
            
        except Exception as e:
            db.rollback()
            raise e