import unittest
import os
import sqlite3
from datetime import datetime, timedelta
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from planogram_optimizer import PlanogramOptimizer

class TestPlanogramOptimizer(unittest.TestCase):
    """Test cases for planogram optimizer functionality."""
    
    def setUp(self):
        """Create test database with sample data."""
        self.test_db = 'test_cvd.db'
        self.api_key = os.getenv('ANTHROPIC_API_KEY', 'test_key')
        self.optimizer = PlanogramOptimizer(self.api_key, self.test_db)
        
        # Create test database schema
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Create minimal schema for testing
        cursor.executescript("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                category TEXT,
                price REAL
            );
            
            CREATE TABLE sales (
                id INTEGER PRIMARY KEY,
                device_id INTEGER,
                product_id INTEGER,
                sale_units INTEGER,
                sale_cash REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE cabinet_configurations (
                id INTEGER PRIMARY KEY,
                device_id INTEGER,
                cabinet_index INTEGER,
                cabinet_type TEXT,
                modelName TEXT,
                rows INTEGER,
                columns INTEGER
            );
            
            CREATE TABLE planograms (
                id INTEGER PRIMARY KEY,
                planogram_key TEXT UNIQUE
            );
            
            CREATE TABLE planogram_slots (
                id INTEGER PRIMARY KEY,
                planogram_id INTEGER,
                slot_position TEXT,
                product_id INTEGER,
                quantity INTEGER,
                capacity INTEGER,
                price REAL
            );
        """)
        
        # Insert test data
        self._insert_test_data(cursor)
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def _insert_test_data(self, cursor):
        """Insert sample test data."""
        # Products
        products = [
            (1, 'Coke', 'Beverages', 1.50),
            (2, 'Pepsi', 'Beverages', 1.50),
            (3, 'Snickers', 'Candy', 1.00),
            (4, 'Chips', 'Snacks', 2.00)
        ]
        cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?)', products)
        
        # Cabinet configuration
        cursor.execute("""
            INSERT INTO cabinet_configurations 
            (device_id, cabinet_index, cabinet_type, modelName, rows, columns)
            VALUES (1, 0, 'Cooler', 'Test Model', 5, 8)
        """)
        
        # Planogram
        cursor.execute("INSERT INTO planograms (planogram_key) VALUES ('1_0')")
        
        # Planogram slots
        slots = [
            (1, 1, 'A1', 1, 10, 20, 1.50),  # Coke in A1
            (2, 1, 'A2', 2, 15, 20, 1.50),  # Pepsi in A2
            (3, 1, 'B1', 3, 8, 15, 1.00),   # Snickers in B1
            (4, 1, 'B2', None, 0, 20, 0)    # Empty slot B2
        ]
        cursor.executemany("""
            INSERT INTO planogram_slots 
            (id, planogram_id, slot_position, product_id, quantity, capacity, price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, slots)
        
        # Sales data
        sales_data = []
        base_date = datetime.now() - timedelta(days=30)
        for day in range(30):
            date = base_date + timedelta(days=day)
            # Coke sells well
            sales_data.append((1, 1, 5, 7.50, date))
            # Pepsi sells poorly
            sales_data.append((1, 2, 1, 1.50, date))
            # Snickers moderate
            sales_data.append((1, 3, 3, 3.00, date))
        
        cursor.executemany("""
            INSERT INTO sales (device_id, product_id, sale_units, sale_cash, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, sales_data)
    
    def test_get_sales_data(self):
        """Test fetching sales data."""
        sales_data = self.optimizer.get_sales_data(1, 30)
        
        self.assertIsInstance(sales_data, list)
        self.assertTrue(len(sales_data) > 0)
        
        # Check Coke has highest sales
        coke_sales = next(s for s in sales_data if s['product_id'] == 1)
        self.assertEqual(coke_sales['total_units'], 150)  # 5 units * 30 days
    
    def test_get_current_planogram(self):
        """Test fetching current planogram."""
        planogram_data = self.optimizer.get_current_planogram(1, 0)
        
        self.assertIsNotNone(planogram_data)
        self.assertIn('cabinet', planogram_data)
        self.assertIn('slots', planogram_data)
        
        # Check cabinet details
        cabinet = planogram_data['cabinet']
        self.assertEqual(cabinet['device_id'], 1)
        self.assertEqual(cabinet['rows'], 5)
        self.assertEqual(cabinet['columns'], 8)
        
        # Check slots
        slots = planogram_data['slots']
        self.assertEqual(len(slots), 4)  # We created 4 slots
        
        # Check A1 has Coke
        a1_slot = next(s for s in slots if s['slot_position'] == 'A1')
        self.assertEqual(a1_slot['product_id'], 1)
        self.assertEqual(a1_slot['product_name'], 'Coke')
    
    def test_calculate_performance_metrics(self):
        """Test performance metrics calculation."""
        sales_data = self.optimizer.get_sales_data(1, 30)
        planogram_data = self.optimizer.get_current_planogram(1, 0)
        
        metrics = self.optimizer.calculate_performance_metrics(sales_data, planogram_data)
        
        self.assertIn('product_velocity', metrics)
        self.assertIn('slot_performance', metrics)
        self.assertIn('stockout_risk', metrics)
        
        # Verify Coke has higher velocity than Pepsi
        coke_velocity = metrics['product_velocity'][1]['daily_units']
        pepsi_velocity = metrics['product_velocity'][2]['daily_units']
        self.assertGreater(coke_velocity, pepsi_velocity)
        
        # Check slot performance
        self.assertIn('A1', metrics['slot_performance'])
        a1_perf = metrics['slot_performance']['A1']
        self.assertEqual(a1_perf['product_id'], 1)
        self.assertAlmostEqual(a1_perf['daily_units'], 5.0)
    
    def test_parse_ai_response(self):
        """Test parsing of AI response."""
        sample_response = """Based on the analysis, here are my recommendations:
        
        [
            {
                "slot": "A1",
                "current_product": "Pepsi",
                "recommendation": {
                    "product": "Red Bull",
                    "reason": "3x higher velocity in similar locations",
                    "expected_improvement": "+$4.50/day"
                },
                "confidence": 0.85
            },
            {
                "slot": "B2", 
                "current_product": null,
                "recommendation": {
                    "product": "Monster Energy",
                    "reason": "High demand, currently not stocked",
                    "expected_improvement": "+$6.00/day"
                },
                "confidence": 0.92
            }
        ]
        """
        
        recommendations = self.optimizer.parse_ai_response(sample_response)
        
        self.assertEqual(len(recommendations), 2)
        self.assertEqual(recommendations[0]['slot'], 'A1')
        self.assertAlmostEqual(recommendations[0]['confidence'], 0.85)
        self.assertEqual(recommendations[1]['slot'], 'B2')
        self.assertAlmostEqual(recommendations[1]['confidence'], 0.92)
    
    def test_generate_recommendations_no_planogram(self):
        """Test recommendations when no planogram exists."""
        result = self.optimizer.generate_recommendations(999, 0)  # Non-existent device
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'No planogram found for this device/cabinet')
    
    def test_build_optimization_prompt(self):
        """Test prompt building."""
        sales_data = [
            {'product_id': 1, 'product_name': 'Coke', 'total_units': 150, 'total_revenue': 225.0}
        ]
        cabinet_config = {
            'cabinet_type': 'Cooler',
            'rows': 5,
            'columns': 8,
            'modelName': 'Test Model'
        }
        metrics = {
            'product_velocity': {1: {'daily_units': 5.0, 'daily_revenue': 7.50}}
        }
        
        prompt = self.optimizer.build_optimization_prompt(metrics, cabinet_config, sales_data)
        
        self.assertIn('Cooler', prompt)
        self.assertIn('5x8', prompt)
        self.assertIn('Test Model', prompt)
        self.assertIn('product_velocity', prompt)

if __name__ == '__main__':
    unittest.main()