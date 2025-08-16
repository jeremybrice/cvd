#!/usr/bin/env python3
"""
CVD Backend API Server
Provides RESTful API endpoints for device and planogram management
with SQLite database storage.
"""

from flask import Flask, jsonify, request, g, session, send_from_directory, abort
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import sqlite3
from datetime import datetime, timedelta
import json
import os
import secrets
from contextlib import closing
from werkzeug.security import generate_password_hash, check_password_hash
from dex_parser import DEXParser
from planogram_optimizer import PlanogramOptimizer
from auth import AuthManager, log_audit_event
import requests
import time
from activity_tracker import ActivityTracker
from security_monitor import SecurityMonitor
from activity_trends_api import init_trends_module

app = Flask(__name__)

# Configure proxy support for Railway
if os.environ.get('RAILWAY_ENVIRONMENT'):
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', secrets.token_hex(32))
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RAILWAY_ENVIRONMENT')  # HTTPS in production/Railway
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

# CORS configuration with Railway domain support
railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
cors_origins = [
    'http://localhost:8000', 
    'http://127.0.0.1:8000',
    'https://jeremybrice.duckdns.org'
]
if railway_domain:
    cors_origins.append(f'https://{railway_domain}')

CORS(app, origins=cors_origins, 
     allow_headers=['Content-Type'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     supports_credentials=True)

# Try multiple database locations for Railway compatibility
DATABASE = os.environ.get('DATABASE_PATH', 'cvd.db')
if not os.path.exists(DATABASE):
    # Try Railway persistent volume path
    if os.path.exists('/app/data/cvd.db'):
        DATABASE = '/app/data/cvd.db'
        print(f"📍 Using Railway persistent volume database: {DATABASE}")
    elif os.path.exists('./cvd.db'):
        DATABASE = './cvd.db'
        print(f"📍 Using local database: {DATABASE}")
    else:
        print(f"⚠️  Database not found at any location, will use: {DATABASE}")
app.config['DATABASE'] = DATABASE
app.config['get_db'] = lambda: get_db()

# Initialize authentication manager
auth_manager = AuthManager(app, DATABASE)

# Initialize activity tracker and security monitor
activity_tracker = None  # Will be initialized after database setup
security_monitor = None  # Will be initialized after database setup

def get_db():
    """Get database connection for current request context"""
    db = getattr(g, '_database', None)
    if db is None:
        # Ensure we use the correct database path
        db_path = app.config['DATABASE']
        if not os.path.exists(db_path):
            app.logger.error(f"Database not found at {db_path}")
            app.logger.error(f"Current working directory: {os.getcwd()}")
            app.logger.error(f"Directory contents: {os.listdir('.')}")
            raise FileNotFoundError(f"Database not found: {db_path}")
        db = g._database = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close database connection at end of request"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Activity tracking and security monitoring middleware
@app.before_request
def before_request():
    """Run before each request for activity tracking and security monitoring"""
    # Set up user context for auth
    if 'session_id' in session:
        user = auth_manager.validate_session(session['session_id'])
        if user:
            g.user = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
            
            # Security monitoring for authenticated requests
            if security_monitor and request.method in ['POST', 'PUT', 'DELETE']:
                # Check for privilege escalation attempts
                is_unauth, should_alert, alert_details = security_monitor.check_privilege_escalation(
                    user['id'], user['role'], request.path, request.method
                )
                if should_alert:
                    security_monitor.create_security_alert(alert_details)
                if is_unauth:
                    return jsonify({'error': 'Unauthorized access'}), 403
    
    # Track activity if tracker is initialized
    if activity_tracker:
        activity_tracker.track_activity()

@app.after_request
def after_request(response):
    """Run after each request for response time tracking"""
    if activity_tracker:
        activity_tracker.track_response_time(response)
    return response

def init_db():
    """Initialize database with schema"""
    with closing(sqlite3.connect(DATABASE)) as db:
        db.execute('PRAGMA foreign_keys = ON')
        
        # Create devices table
        db.execute('''
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
            )
        ''')
        
        # Create cabinet_configurations table
        db.execute('''
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
            )
        ''')
        
        # Create planograms table
        db.execute('''
            CREATE TABLE IF NOT EXISTS planograms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cabinet_id INTEGER NOT NULL,
                planogram_key TEXT UNIQUE NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cabinet_id) REFERENCES cabinet_configurations(id) ON DELETE CASCADE
            )
        ''')
        
        # Create products table
        db.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                image TEXT,
                is_system BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create device_types table
        db.execute('''
            CREATE TABLE IF NOT EXISTS device_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                allows_additional_cabinets BOOLEAN NOT NULL
            )
        ''')
        
        # Create cabinet_types table
        db.execute('''
            CREATE TABLE IF NOT EXISTS cabinet_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                rows INTEGER NOT NULL,
                cols INTEGER NOT NULL,
                icon TEXT NOT NULL
            )
        ''')
        
        # Create planogram_slots table
        db.execute('''
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
            )
        ''')
        
        # Create sales table
        db.execute('''
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
            )
        ''')
        
        # Create locations table
        db.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                latitude REAL,
                longitude REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create routes table
        db.execute('''
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                route_number TEXT,
                assigned_driver_id INTEGER UNIQUE,
                assigned_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assigned_driver_id) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')
        
        # Create service_visits table for tracking device service history
        db.execute('''
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
                service_order_cabinet_id INTEGER,
                FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
                FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE SET NULL,
                FOREIGN KEY (service_order_cabinet_id) REFERENCES service_order_cabinets(id)
            )
        ''')
        
        # Create device_metrics table for caching calculated metrics
        db.execute('''
            CREATE TABLE IF NOT EXISTS device_metrics (
                device_id INTEGER PRIMARY KEY,
                sold_out_count INTEGER DEFAULT 0,
                days_remaining_inventory REAL,
                data_collection_rate REAL DEFAULT 100.0,
                product_level_percent REAL,
                units_to_par INTEGER DEFAULT 0,
                last_calculated TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
            )
        ''')
        
        # Create route_planning_config table for configuration settings
        db.execute('''
            CREATE TABLE IF NOT EXISTS route_planning_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                critical_dri_threshold INTEGER DEFAULT 1,
                warning_dri_threshold INTEGER DEFAULT 3,
                ok_dri_threshold INTEGER DEFAULT 7,
                auto_select_critical BOOLEAN DEFAULT TRUE,
                metrics_cache_ttl_minutes INTEGER DEFAULT 15
            )
        ''')
        
        # Create service_orders table
        db.execute('''
            CREATE TABLE IF NOT EXISTS service_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled')),
                total_units INTEGER,
                estimated_duration_minutes INTEGER,
                driver_id INTEGER,
                sync_version INTEGER DEFAULT 1,
                last_modified TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE SET NULL,
                FOREIGN KEY (driver_id) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')
        
        # Create service_order_cabinets table
        db.execute('''
            CREATE TABLE IF NOT EXISTS service_order_cabinets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_order_id INTEGER NOT NULL,
                cabinet_configuration_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                executed_at TIMESTAMP,
                executed_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_modified TIMESTAMP,
                FOREIGN KEY (service_order_id) REFERENCES service_orders(id) ON DELETE CASCADE,
                FOREIGN KEY (cabinet_configuration_id) REFERENCES cabinet_configurations(id),
                FOREIGN KEY (executed_by) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')
        
        # Create service_order_cabinet_items table
        db.execute('''
            CREATE TABLE IF NOT EXISTS service_order_cabinet_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_order_cabinet_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity_needed INTEGER NOT NULL,
                quantity_filled INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_order_cabinet_id) REFERENCES service_order_cabinets(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
            )
        ''')
        
        # Create service_visit_items table
        db.execute('''
            CREATE TABLE IF NOT EXISTS service_visit_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_visit_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity_filled INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_visit_id) REFERENCES service_visits(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        # Create slot_metrics table for individual slot-level metrics
        db.execute('''
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
            )
        ''')
        
        # Create device_routes table for many-to-many relationship
        db.execute('''
            CREATE TABLE IF NOT EXISTS device_routes (
                device_id INTEGER NOT NULL,
                route_id INTEGER NOT NULL,
                PRIMARY KEY (device_id, route_id),
                FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
                FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
            )
        ''')
        
        # Create DEX-related tables
        db.execute('''
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
            )
        ''')
        
        db.execute('''
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
            )
        ''')
        
        db.execute('''
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
            )
        ''')
        
        # Create indexes for better performance
        db.execute('CREATE INDEX IF NOT EXISTS idx_devices_asset ON devices(asset)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_cabinets_device ON cabinet_configurations(device_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_planograms_key ON planograms(planogram_key)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_slots_product ON planogram_slots(product_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_sales_device ON sales(device_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_sales_created ON sales(created_at)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_device_routes_route ON device_routes(route_id)')
        
        # New indexes for route planning functionality
        db.execute('CREATE INDEX IF NOT EXISTS idx_service_visits_device ON service_visits(device_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_service_visits_date ON service_visits(service_date)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_device_metrics_calculated ON device_metrics(last_calculated)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_sales_device_date ON sales(device_id, created_at)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_devices_deleted ON devices(deleted_at)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_service_orders_route ON service_orders(route_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_service_order_cabinets_order_id ON service_order_cabinets(service_order_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_service_order_cabinets_cabinet_id ON service_order_cabinets(cabinet_configuration_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_service_order_cabinet_items_cabinet_id ON service_order_cabinet_items(service_order_cabinet_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_service_order_cabinet_items_product_id ON service_order_cabinet_items(product_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_service_visit_items_visit_id ON service_visit_items(service_visit_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_service_visit_items_product_id ON service_visit_items(product_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_service_visits_cabinet_id ON service_visits(service_order_cabinet_id)')
        
        # Indexes for slot_metrics table
        db.execute('CREATE INDEX IF NOT EXISTS idx_slot_metrics_planogram_slot ON slot_metrics(planogram_slot_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_slot_metrics_last_calc ON slot_metrics(last_calculated)')
        
        # Indexes for DEX tables
        db.execute('CREATE INDEX IF NOT EXISTS idx_dex_reads_machine_serial ON dex_reads(machine_serial)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_dex_reads_timestamp ON dex_reads(upload_timestamp)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_dex_records_read_id ON dex_records(dex_read_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_dex_records_type ON dex_records(record_type)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_dex_pa_records_read_id ON dex_pa_records(dex_read_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_dex_pa_records_selection ON dex_pa_records(selection_number)')
        
        # Handle migration: Check if product_id column is TEXT and migrate to INTEGER
        cursor = db.cursor()
        
        # Check current column type for product_id
        table_info = cursor.execute("PRAGMA table_info(planogram_slots)").fetchall()
        product_id_col = next((col for col in table_info if col[1] == 'product_id'), None)
        
        if product_id_col and product_id_col[2] == 'TEXT':
            print("Migrating planogram_slots.product_id from TEXT to INTEGER...")
            
            # Add temporary column
            db.execute('ALTER TABLE planogram_slots ADD COLUMN product_id_new INTEGER')
            
            # Note: Actual data migration will happen after products are inserted
            print("Added temporary product_id_new column")
        
        # Create authentication tables
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'driver', 'viewer')),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        ''')
        
        db.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        db.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id INTEGER,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        db.execute('''
            CREATE TABLE IF NOT EXISTS driver_routes (
                user_id INTEGER NOT NULL,
                route_id INTEGER NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, route_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for authentication tables
        db.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        
        db.commit()

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    return dict(zip(row.keys(), row))

def geocode_address(address):
    """Geocode an address using Nominatim API with proper headers"""
    if not address:
        return None, None
        
    try:
        # Respect Nominatim rate limit (1 request per second)
        time.sleep(1)
        
        headers = {
            'User-Agent': '365 Retail Markets CVD Application'
        }
        
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={
                'q': address,
                'format': 'json',
                'limit': 1
            },
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
                
    except Exception as e:
        print(f"Geocoding error for {address}: {e}")
        
    return None, None

def calculate_grid_metadata(pa_records):
    """Calculate grid metadata from PA records"""
    if not pa_records:
        return {
            'pattern_type': 'unknown',
            'confidence': 0.0,
            'grid_dimensions': {'rows': 0, 'columns': 0},
            'coverage': {'total': 0, 'with_grid': 0, 'percentage': 0}
        }
    
    # Count records with grid data
    total_records = len(pa_records)
    with_grid = sum(1 for record in pa_records if record['row'] is not None and record['column'] is not None)
    
    # Get unique rows and columns
    rows = set()
    columns = set()
    for record in pa_records:
        if record['row'] is not None:
            rows.add(record['row'])
        if record['column'] is not None:
            columns.add(record['column'])
    
    return {
        'pattern_type': 'mixed',  # Could be determined by re-analyzing
        'confidence': (with_grid / total_records) if total_records > 0 else 0.0,
        'grid_dimensions': {'rows': len(rows), 'columns': len(columns)},
        'coverage': {
            'total': total_records,
            'with_grid': with_grid,
            'percentage': (with_grid / total_records * 100) if total_records > 0 else 0
        }
    }

def build_grid_structure(pa_records):
    """Build structured grid layout from PA records"""
    grid = {}
    rows = set()
    columns = set()
    
    # Build grid structure
    for record in pa_records:
        row = record['row']
        col = record['column']
        
        if row is not None and col is not None:
            rows.add(row)
            columns.add(col)
            
            if row not in grid:
                grid[row] = {}
            
            grid[row][col] = {
                'selection_number': record['selection_number'],
                'units_sold': record['units_sold'],
                'revenue_cents': record['revenue_cents'],
                'price_cents': record['price_cents'],
                'capacity': record['capacity']
            }
    
    # Sort rows and columns appropriately
    try:
        # Try numeric sort first
        sorted_rows = sorted(rows, key=lambda x: int(x) if str(x).isdigit() else float('inf'))
        sorted_columns = sorted(columns, key=lambda x: int(x) if str(x).isdigit() else float('inf'))
    except:
        # Fall back to string sort
        sorted_rows = sorted(rows)
        sorted_columns = sorted(columns)
    
    return {
        'grid': grid,
        'dimensions': {
            'rows': len(rows),
            'columns': len(columns),
            'row_labels': sorted_rows,
            'column_labels': sorted_columns
        },
        'metadata': {
            'total_cells': len(rows) * len(columns),
            'filled_cells': sum(len(row_data) for row_data in grid.values()),
            'empty_cells': (len(rows) * len(columns)) - sum(len(row_data) for row_data in grid.values())
        }
    }

def migrate_database_schema():
    """Handle database schema migrations for existing installations"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check and migrate devices table columns
        table_info = cursor.execute("PRAGMA table_info(devices)").fetchall()
        columns = {col[1] for col in table_info}
        
        if 'location' in columns and 'location_id' not in columns:
            # First ensure locations table exists and migrate data
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='locations'")
            if cursor.fetchone()[0] == 0:
                # Create locations table first
                cursor.execute('''
                    CREATE TABLE locations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Migrate location data
                locations = cursor.execute("SELECT DISTINCT location FROM devices WHERE location IS NOT NULL").fetchall()
                for loc in locations:
                    cursor.execute("INSERT INTO locations (name) VALUES (?)", (loc[0],))
            
            # Add location_id column and migrate data
            cursor.execute("ALTER TABLE devices ADD COLUMN location_id INTEGER")
            cursor.execute('''
                UPDATE devices 
                SET location_id = (SELECT id FROM locations WHERE locations.name = devices.location)
            ''')
        
        if 'device_type' in columns and 'device_type_id' not in columns:
            cursor.execute("ALTER TABLE devices ADD COLUMN device_type_id INTEGER")
            # Default to PicoVision (id=1) for existing devices
            cursor.execute("UPDATE devices SET device_type_id = 1 WHERE device_type_id IS NULL")
        
        if 'route_id' not in columns:
            cursor.execute("ALTER TABLE devices ADD COLUMN route_id INTEGER")
        
        if 'deleted_at' not in columns:
            cursor.execute("ALTER TABLE devices ADD COLUMN deleted_at TIMESTAMP")
        
        if 'deleted_by' not in columns:
            cursor.execute("ALTER TABLE devices ADD COLUMN deleted_by TEXT")
        
        # Check cabinet_configurations table
        table_info = cursor.execute("PRAGMA table_info(cabinet_configurations)").fetchall()
        columns = {col[1] for col in table_info}
        
        if 'cabinet_type' in columns and 'cabinet_type_id' not in columns:
            cursor.execute("ALTER TABLE cabinet_configurations ADD COLUMN cabinet_type_id INTEGER")
            # Default to Cooler (id=1) for existing cabinets
            cursor.execute("UPDATE cabinet_configurations SET cabinet_type_id = 1 WHERE cabinet_type_id IS NULL")
        
        # Check planogram_slots table
        table_info = cursor.execute("PRAGMA table_info(planogram_slots)").fetchall()
        columns = {col[1] for col in table_info}
        
        if 'cleared_at' not in columns:
            cursor.execute("ALTER TABLE planogram_slots ADD COLUMN cleared_at TIMESTAMP")
        
        if 'cleared_by' not in columns:
            cursor.execute("ALTER TABLE planogram_slots ADD COLUMN cleared_by TEXT")
        
        if 'previous_product_id' not in columns:
            cursor.execute("ALTER TABLE planogram_slots ADD COLUMN previous_product_id INTEGER")
        
        # Initialize route planning config if not exists
        cursor.execute("SELECT COUNT(*) FROM route_planning_config")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO route_planning_config 
                (critical_dri_threshold, warning_dri_threshold, ok_dri_threshold, 
                 auto_select_critical, metrics_cache_ttl_minutes)
                VALUES (1, 3, 7, TRUE, 15)
            ''')
        
        db.commit()
        print("Database schema migration completed successfully")
        
    except Exception as e:
        print(f"Error during schema migration: {e}")
        db.rollback()

def migrate_products():
    """Migrate products from hard-coded data to database"""
    # Product data extracted from NSPT.html
    products_data = [
        {'id': 'deja-blue', 'name': 'Deja Blue Water', 'category': 'water', 'price': 2.00, 'image': 'https://jeremy.parlevelvms.com/img/uploaded/9459-deja-blue.png'},
        {'id': 'gatorade-fruit-punch', 'name': 'Gatorade Fruit Punch', 'category': 'sports', 'price': 3.00, 'image': 'https://jeremy.parlevelvms.com/img/uploaded/6619-gatorade_fruitpunch_20oz.png'},
        {'id': 'glacier-cherry', 'name': 'Powerade Glacier Cherry', 'category': 'sports', 'price': 3.00, 'image': 'https://jeremy.parlevelvms.com/img/uploaded/53dff1db7f66a_6_glaciercherry.png'},
        {'id': 'v8', 'name': 'V8 Original', 'category': 'juice', 'price': 3.50, 'image': 'https://jeremy.parlevelvms.com/img/uploaded/56042342f30e9_6_v8.png'},
        {'id': 'vitamin-water', 'name': 'Vitamin Water', 'category': 'water', 'price': 2.50, 'image': 'https://jeremy.parlevelvms.com/img/uploaded/558ae001be2d9_6_Untitled-4.png'},
        {'id': 'country-time', 'name': 'Country Time Lemonade', 'category': 'juice', 'price': 2.50, 'image': 'https://jeremy.parlevelvms.com/img/uploaded/8960-COUNTRY_TIME_YELLOW_LEMONADE_20.png'},
        {'id': 'monster-original', 'name': 'Monster Energy Original', 'category': 'energy', 'price': 3.50, 'image': 'https://jeremy.parlevelvms.com/img/uploaded/5732-8450-monster-can.png'},
        {'id': 'monster-blue', 'name': 'Monster Energy Blue', 'category': 'energy', 'price': 3.50, 'image': 'https://jeremy.parlevelvms.com/img/uploaded/104-monster-blue-1.png'},
        {'id': 'nos', 'name': 'NOS Energy', 'category': 'energy', 'price': 3.50, 'image': 'https://jeremy.parlevelvms.com/img/uploaded/12123_16oz_nos.jpg'},
        {'id': 'monster-zero', 'name': 'Monster Zero Ultra', 'category': 'energy', 'price': 3.50, 'image': 'https://jeremy.parlevelvms.com/img/uploaded/7074-monster%20zero%20ultra.png'},
        {'id': 'pepsi', 'name': 'Pepsi', 'category': 'soda', 'price': 2.50, 'image': 'https://jeremy.parlevelvms.com/img/uploaded/2306-pepsi_bottle_20oz.png'},
        {'id': 'coca-cola', 'name': 'Coca-Cola', 'category': 'soda', 'price': 2.50, 'image': 'https://jeremy.parlevelvms.com/img/uploaded/7937-7848-cokebottle.png'}
    ]
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if products already exist
    existing_count = cursor.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    if existing_count > 0:
        print(f"Products table already has {existing_count} entries, skipping migration")
        return
    
    # Insert products and create mapping
    string_to_int_mapping = {}
    
    for product in products_data:
        cursor.execute('''
            INSERT INTO products (name, category, price, image)
            VALUES (?, ?, ?, ?)
        ''', (product['name'], product['category'], product['price'], product['image']))
        
        new_id = cursor.lastrowid
        string_to_int_mapping[product['id']] = new_id
        print(f"Migrated product: {product['id']} -> {new_id} ({product['name']})")
    
    # Update existing planogram_slots data
    # Check if we have the temporary column
    table_info = cursor.execute("PRAGMA table_info(planogram_slots)").fetchall()
    has_temp_col = any(col[1] == 'product_id_new' for col in table_info)
    
    if has_temp_col:
        # Update the new column with integer IDs based on product names
        for old_id, new_id in string_to_int_mapping.items():
            # Find the product name for this old_id
            product_name = next(p['name'] for p in products_data if p['id'] == old_id)
            
            cursor.execute('''
                UPDATE planogram_slots 
                SET product_id_new = ? 
                WHERE product_name = ?
            ''', (new_id, product_name))
        
        # Also handle direct string ID matches (if any exist)
        cursor.execute('''
            UPDATE planogram_slots 
            SET product_id_new = ? 
            WHERE product_id = ?
        ''', [(new_id, old_id) for old_id, new_id in string_to_int_mapping.items()])
        
        # Drop old column and rename new one
        cursor.execute('ALTER TABLE planogram_slots DROP COLUMN product_id')
        cursor.execute('ALTER TABLE planogram_slots RENAME COLUMN product_id_new TO product_id')
        
        print("Updated planogram_slots to use integer product IDs")
    
    db.commit()
    print(f"Successfully migrated {len(products_data)} products to database")

def migrate_device_types():
    """Migrate device types from hard-coded data to database"""
    device_types_data = [
        {
            'name': 'PicoVision',
            'description': 'Full-featured device with cashless reader',
            'allows_additional_cabinets': True
        },
        {
            'name': 'PicoVision Express',
            'description': 'QR code only device',
            'allows_additional_cabinets': False
        }
    ]
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if device types already exist
    existing_count = cursor.execute('SELECT COUNT(*) FROM device_types').fetchone()[0]
    if existing_count > 0:
        print(f"Device types table already has {existing_count} entries, skipping migration")
        return
    
    # Insert device types
    for device_type in device_types_data:
        cursor.execute('''
            INSERT INTO device_types (name, description, allows_additional_cabinets)
            VALUES (?, ?, ?)
        ''', (device_type['name'], device_type['description'], device_type['allows_additional_cabinets']))
        print(f"Migrated device type: {device_type['name']}")
    
    db.commit()
    print(f"Successfully migrated {len(device_types_data)} device types to database")

def migrate_cabinet_types():
    """Migrate cabinet types from hard-coded data to database"""
    cabinet_types_data = [
        {
            'name': 'Cooler',
            'description': 'Refrigerated storage',
            'rows': 5,
            'cols': 8,
            'icon': 'C'
        },
        {
            'name': 'Freezer',
            'description': 'Frozen storage',
            'rows': 5,
            'cols': 8,
            'icon': 'F'
        },
        {
            'name': 'Ambient',
            'description': 'Room temperature storage',
            'rows': 5,
            'cols': 8,
            'icon': 'A'
        },
        {
            'name': 'Ambient+',
            'description': 'Extended room temperature storage',
            'rows': 6,
            'cols': 9,
            'icon': 'A+'
        }
    ]
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if cabinet types already exist
    existing_count = cursor.execute('SELECT COUNT(*) FROM cabinet_types').fetchone()[0]
    if existing_count > 0:
        print(f"Cabinet types table already has {existing_count} entries, skipping migration")
        return
    
    # Insert cabinet types
    for cabinet_type in cabinet_types_data:
        cursor.execute('''
            INSERT INTO cabinet_types (name, description, rows, cols, icon)
            VALUES (?, ?, ?, ?, ?)
        ''', (cabinet_type['name'], cabinet_type['description'], cabinet_type['rows'], 
              cabinet_type['cols'], cabinet_type['icon']))
        print(f"Migrated cabinet type: {cabinet_type['name']}")
    
    db.commit()
    print(f"Successfully migrated {len(cabinet_types_data)} cabinet types to database")

def create_initial_admin():
    """Create or update admin user with standard password"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Use simple password for development/demo (change in production)
        initial_password = 'admin'
        password_hash = generate_password_hash(initial_password)
        
        # Check if admin user exists
        admin_exists = cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
        
        if admin_exists:
            # Update existing admin user password
            cursor.execute('''
                UPDATE users SET password_hash = ?, updated_at = ?
                WHERE username = ?
            ''', (password_hash, datetime.now(), 'admin'))
            print('='*50)
            print('Admin password updated!')
            print(f'Username: admin')
            print(f'Password: {initial_password}')
            print('='*50)
        else:
            # Create new admin user
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', 'admin@cvd.local', password_hash, 'admin', True))
            print('='*50)
            print('Initial admin user created!')
            print(f'Username: admin')
            print(f'Password: {initial_password}')
            print('='*50)
        
        db.commit()
        
        # Save initial password to file (delete after first login)
        with open('initial_admin_password.txt', 'w') as f:
            f.write(f'Username: admin\n')
            f.write(f'Password: {initial_password}\n')
            f.write(f'Email: admin@cvd.local\n')
            f.write('\nIMPORTANT: Delete this file after first login!\n')
            
    except Exception as e:
        print(f"Error creating/updating initial admin: {e}")
        db.rollback()

def init_sentinel_product():
    """Initialize the sentinel product that represents empty slots"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Ensure the is_system column exists
        table_info = cursor.execute("PRAGMA table_info(products)").fetchall()
        has_is_system = any(col[1] == 'is_system' for col in table_info)
        
        if not has_is_system:
            cursor.execute('ALTER TABLE products ADD COLUMN is_system BOOLEAN DEFAULT FALSE')
            print("Added is_system column to products table")
        
        # Create or update the sentinel product
        cursor.execute('''
            INSERT INTO products (id, name, category, price, is_system)
            VALUES (1, 'EMPTY_SLOT', 'system', 0.00, TRUE)
            ON CONFLICT(id) DO UPDATE SET
                name = 'EMPTY_SLOT',
                category = 'system',
                price = 0.00,
                is_system = TRUE
        ''')
        
        db.commit()
        print("Sentinel product initialized successfully")
    except Exception as e:
        print(f"Error initializing sentinel product: {e}")
        db.rollback()
    
    # Migrate routes table for driver assignment
    try:
        cursor = db.cursor()
        table_info = cursor.execute("PRAGMA table_info(routes)").fetchall()
        columns = {col[1] for col in table_info}
        
        if 'assigned_driver_id' not in columns:
            cursor.execute('ALTER TABLE routes ADD COLUMN assigned_driver_id INTEGER UNIQUE')
            cursor.execute('ALTER TABLE routes ADD COLUMN assigned_at TIMESTAMP')
            print("Added driver assignment columns to routes table")
            db.commit()
    except Exception as e:
        print(f"Error migrating routes table: {e}")
        db.rollback()

def create_all_planogram_slots(planogram_id, rows, cols, cursor):
    """Create all slots for a planogram, populated with sentinel product"""
    slots_data = []
    for row in range(rows):
        row_label = chr(65 + row)  # A, B, C...
        for col in range(1, cols + 1):
            slot_position = f"{row_label}{col}"
            slots_data.append((
                planogram_id, 
                slot_position, 
                1,  # Sentinel product ID
                'EMPTY_SLOT',
                0,  # quantity
                0,  # capacity
                0,  # par_level
                0.00  # price
            ))
    
    # Bulk insert all slots
    cursor.executemany('''
        INSERT INTO planogram_slots 
        (planogram_id, slot_position, product_id, product_name,
         quantity, capacity, par_level, price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', slots_data)
    
    return len(slots_data)

# Route Metrics Service Classes

class RouteMetricsService:
    """Service for calculating device metrics for route planning"""
    
    @staticmethod
    def calculate_device_metrics(device_id):
        """Calculate and cache all metrics for a device"""
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Calculate individual metrics
            sold_out_count = RouteMetricsService.calculate_sold_out_count(device_id)
            units_to_par = RouteMetricsService.calculate_units_to_par(device_id)
            product_level = RouteMetricsService.calculate_product_level(device_id)
            dri = RouteMetricsService.calculate_days_remaining_inventory(device_id)
            data_collection_rate = 100.0  # Placeholder - would check device connectivity
            
            # Cache the results
            cursor.execute('''
                INSERT INTO device_metrics 
                (device_id, sold_out_count, days_remaining_inventory, 
                 data_collection_rate, product_level_percent, units_to_par, last_calculated)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(device_id) DO UPDATE SET
                    sold_out_count = excluded.sold_out_count,
                    days_remaining_inventory = excluded.days_remaining_inventory,
                    data_collection_rate = excluded.data_collection_rate,
                    product_level_percent = excluded.product_level_percent,
                    units_to_par = excluded.units_to_par,
                    last_calculated = CURRENT_TIMESTAMP
            ''', (device_id, sold_out_count, dri, data_collection_rate, product_level, units_to_par))
            
            db.commit()
            
            return {
                'soldOutCount': sold_out_count,
                'daysRemainingInventory': dri,
                'dataCollectionRate': data_collection_rate,
                'productLevelPercent': product_level,
                'unitsToPar': units_to_par
            }
            
        except Exception as e:
            print(f"Error calculating metrics for device {device_id}: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def calculate_sold_out_count(device_id):
        """Count empty slots across all cabinets for a device"""
        db = get_db()
        cursor = db.cursor()
        
        count = cursor.execute('''
            SELECT COUNT(*) 
            FROM planogram_slots ps
            JOIN planograms p ON ps.planogram_id = p.id
            JOIN cabinet_configurations cc ON p.cabinet_id = cc.id
            WHERE cc.device_id = ? 
            AND ps.quantity = 0
            AND ps.product_id != 1  -- Exclude empty slot sentinel
        ''', (device_id,)).fetchone()[0]
        
        return count
    
    @staticmethod
    def calculate_units_to_par(device_id):
        """Calculate total units needed to reach par level"""
        db = get_db()
        cursor = db.cursor()
        
        result = cursor.execute('''
            SELECT SUM(ps.par_level - ps.quantity) as units_needed
            FROM planogram_slots ps
            JOIN planograms p ON ps.planogram_id = p.id
            JOIN cabinet_configurations cc ON p.cabinet_id = cc.id
            WHERE cc.device_id = ? 
            AND ps.product_id != 1  -- Exclude empty slot sentinel
            AND ps.par_level > ps.quantity
        ''', (device_id,)).fetchone()
        
        return result['units_needed'] or 0
    
    @staticmethod
    def calculate_product_level(device_id):
        """Calculate average fill percentage across all slots"""
        db = get_db()
        cursor = db.cursor()
        
        result = cursor.execute('''
            SELECT 
                AVG(CASE 
                    WHEN ps.capacity > 0 THEN (ps.quantity * 1.0 / ps.capacity) * 100
                    ELSE 0 
                END) as avg_fill
            FROM planogram_slots ps
            JOIN planograms p ON ps.planogram_id = p.id
            JOIN cabinet_configurations cc ON p.cabinet_id = cc.id
            WHERE cc.device_id = ?
            AND ps.product_id != 1  -- Exclude empty slot sentinel
        ''', (device_id,)).fetchone()
        
        return round(result['avg_fill'] or 0, 1)
    
    @staticmethod
    def calculate_days_remaining_inventory(device_id):
        """Calculate days until stockout based on sales velocity"""
        db = get_db()
        cursor = db.cursor()
        
        # Get sales data for last 30 days
        sales_data = cursor.execute('''
            SELECT 
                s.product_id,
                SUM(s.sale_units) as total_units,
                COUNT(DISTINCT DATE(s.created_at)) as days_with_sales
            FROM sales s
            WHERE s.device_id = ?
            AND s.created_at >= datetime('now', '-30 days')
            GROUP BY s.product_id
        ''', (device_id,)).fetchall()
        
        if not sales_data:
            return 999  # No sales data, assume infinite inventory
        
        # Calculate daily consumption rate per product
        consumption_rates = {}
        for row in sales_data:
            if row['days_with_sales'] > 0:
                daily_rate = row['total_units'] / row['days_with_sales']
                consumption_rates[row['product_id']] = daily_rate
        
        # Get current inventory levels
        inventory = cursor.execute('''
            SELECT 
                ps.product_id,
                SUM(ps.quantity) as total_quantity
            FROM planogram_slots ps
            JOIN planograms p ON ps.planogram_id = p.id
            JOIN cabinet_configurations cc ON p.cabinet_id = cc.id
            WHERE cc.device_id = ?
            AND ps.product_id != 1  -- Exclude empty slot sentinel
            GROUP BY ps.product_id
        ''', (device_id,)).fetchall()
        
        # Calculate days remaining for each product
        min_days = 999
        for inv_row in inventory:
            product_id = inv_row['product_id']
            quantity = inv_row['total_quantity']
            
            if product_id in consumption_rates and consumption_rates[product_id] > 0:
                days_remaining = quantity / consumption_rates[product_id]
                min_days = min(min_days, days_remaining)
        
        return round(min_days, 1)
    
    @staticmethod
    def get_days_since_service(device_id):
        """Get days since last service visit"""
        db = get_db()
        cursor = db.cursor()
        
        result = cursor.execute('''
            SELECT julianday('now') - julianday(service_date) as days
            FROM service_visits
            WHERE device_id = ?
            ORDER BY service_date DESC
            LIMIT 1
        ''', (device_id,)).fetchone()
        
        return round(result['days'], 1) if result else None


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

# Authentication Endpoints

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and create session"""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    ip_address = request.remote_addr
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    # Check if IP is blocked (brute force protection)
    if security_monitor and security_monitor.is_ip_blocked(ip_address):
        return jsonify({'error': 'Too many failed attempts. Please try again later.'}), 429
    
    db = get_db()
    cursor = db.cursor()
    
    # Get user by username or email
    user = cursor.execute('''
        SELECT id, username, email, password_hash, role, is_active, 
               failed_login_attempts, locked_until
        FROM users 
        WHERE (username = ? OR email = ?) AND is_active = 1
    ''', (username, username)).fetchone()
    
    if not user:
        # Track failed login for brute force detection
        if security_monitor:
            is_blocked, should_alert, alert_details = security_monitor.check_brute_force(
                ip_address, user_id=None, success=False
            )
            if should_alert:
                security_monitor.create_security_alert(alert_details)
            if is_blocked:
                return jsonify({'error': 'Too many failed attempts. Please try again later.'}), 429
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check if account is locked
    if user['locked_until'] and datetime.fromisoformat(user['locked_until']) > datetime.now():
        return jsonify({'error': 'Account temporarily locked'}), 401
    
    # Verify password
    if not check_password_hash(user['password_hash'], password):
        # Increment failed attempts
        failed_attempts = user['failed_login_attempts'] + 1
        locked_until = None
        
        if failed_attempts >= 5:
            locked_until = datetime.now() + timedelta(minutes=15)
        
        cursor.execute('''
            UPDATE users 
            SET failed_login_attempts = ?, locked_until = ?
            WHERE id = ?
        ''', (failed_attempts, locked_until, user['id']))
        db.commit()
        
        # Track failed login for brute force detection
        if security_monitor:
            is_blocked, should_alert, alert_details = security_monitor.check_brute_force(
                ip_address, user_id=user['id'], success=False
            )
            if should_alert:
                security_monitor.create_security_alert(alert_details)
            if is_blocked:
                return jsonify({'error': 'Too many failed attempts. Please try again later.'}), 429
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Reset failed attempts and create session
    cursor.execute('''
        UPDATE users 
        SET failed_login_attempts = 0, locked_until = NULL, last_login = ?
        WHERE id = ?
    ''', (datetime.now(), user['id']))
    
    session_id = auth_manager.create_session(user['id'], db)
    session['session_id'] = session_id
    session.permanent = True
    
    # Clear brute force tracking on successful login
    if security_monitor:
        security_monitor.check_brute_force(ip_address, user_id=user['id'], success=True)
        
        # Check for geographic anomaly
        is_anomaly, should_alert, alert_details = security_monitor.check_geographic_anomaly(
            user['id'], ip_address, request.headers.get('User-Agent')
        )
        if should_alert:
            security_monitor.create_security_alert(alert_details)
    
    db.commit()
    
    # Log the login
    log_audit_event(user['id'], 'LOGIN', 'user', user['id'], 'Successful login')
    
    return jsonify({
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role']
        },
        'session_id': session_id
    })

@app.route('/api/auth/logout', methods=['POST'])
@auth_manager.require_auth
def logout():
    """Logout user and destroy session"""
    session_id = session.get('session_id')
    if session_id:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
        db.commit()
        
        log_audit_event(g.user['id'], 'LOGOUT', 'user', g.user['id'], 'User logged out')
    
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/auth/current-user', methods=['GET'])
@auth_manager.require_auth
def get_current_user():
    """Get current authenticated user"""
    db = get_db()
    cursor = db.cursor()
    
    # Get additional user details
    user_details = cursor.execute('''
        SELECT created_at, last_login
        FROM users
        WHERE id = ?
    ''', (g.user['id'],)).fetchone()
    
    # Merge with g.user data
    user_data = {**g.user}
    if user_details:
        user_data['created_at'] = user_details['created_at']
        user_data['last_login'] = user_details['last_login']
    
    return jsonify({'user': user_data})

@app.route('/api/auth/change-password', methods=['POST'])
@auth_manager.require_auth
def change_password():
    """Change user password"""
    data = request.json
    current_password = data.get('currentPassword', '')
    new_password = data.get('newPassword', '')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password required'}), 400
    
    if len(new_password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Verify current password
    user = cursor.execute('''
        SELECT password_hash FROM users WHERE id = ?
    ''', (g.user['id'],)).fetchone()
    
    if not check_password_hash(user['password_hash'], current_password):
        return jsonify({'error': 'Current password incorrect'}), 401
    
    # Update password
    new_hash = generate_password_hash(new_password)
    cursor.execute('''
        UPDATE users SET password_hash = ?, updated_at = ?
        WHERE id = ?
    ''', (new_hash, datetime.now(), g.user['id']))
    
    db.commit()
    
    log_audit_event(g.user['id'], 'PASSWORD_CHANGE', 'user', g.user['id'], 'Password changed')
    
    return jsonify({'message': 'Password changed successfully'})

@app.route('/api/auth/update-profile', methods=['PUT'])
@auth_manager.require_auth
def update_profile():
    """Update user profile (email only for now)"""
    data = request.json
    new_email = data.get('email', '').strip()
    
    if not new_email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, new_email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if email is already in use by another user
    existing = cursor.execute('''
        SELECT id FROM users WHERE email = ? AND id != ?
    ''', (new_email, g.user['id'])).fetchone()
    
    if existing:
        return jsonify({'error': 'Email already in use'}), 400
    
    # Update email
    cursor.execute('''
        UPDATE users SET email = ?, updated_at = ?
        WHERE id = ?
    ''', (new_email, datetime.now(), g.user['id']))
    
    db.commit()
    
    # Update g.user with new email
    g.user['email'] = new_email
    
    log_audit_event(g.user['id'], 'PROFILE_UPDATE', 'user', g.user['id'], f'Email updated to {new_email}')
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': g.user
    })

@app.route('/api/auth/activity', methods=['GET'])
@auth_manager.require_auth
def get_current_user_activity():
    """Get current user's recent activity"""
    db = get_db()
    cursor = db.cursor()
    
    # Get last 10 login attempts
    activities = cursor.execute('''
        SELECT action, ip_address, created_at, details
        FROM audit_log
        WHERE user_id = ? AND action IN ('LOGIN_SUCCESS', 'LOGIN_FAILED', 'LOGOUT')
        ORDER BY created_at DESC
        LIMIT 10
    ''', (g.user['id'],)).fetchall()
    
    return jsonify({
        'activities': [dict(activity) for activity in activities]
    })

# User Management Endpoints

@app.route('/api/users', methods=['GET'])
@auth_manager.require_role(['admin'])
def get_users():
    """Get all users with pagination and filtering"""
    db = get_db()
    cursor = db.cursor()
    
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    offset = (page - 1) * per_page
    
    # Get filter parameters
    role_filter = request.args.get('role')
    status_filter = request.args.get('status')
    search = request.args.get('search')
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    
    # Build base query - exclude soft deleted by default and admin user
    base_query = '''
        SELECT id, username, email, role, is_active, created_at, 
               updated_at, last_login, failed_login_attempts, locked_until,
               is_deleted, deleted_at, deleted_by
        FROM users 
        WHERE 1=1 AND username != 'admin'
    '''
    
    params = []
    
    # Filter out soft deleted unless explicitly requested
    if not include_deleted:
        base_query += ' AND is_deleted = 0'
    
    # Apply filters
    if role_filter:
        base_query += ' AND role = ?'
        params.append(role_filter)
    
    if status_filter == 'active':
        base_query += ' AND is_active = 1'
    elif status_filter == 'inactive':
        base_query += ' AND is_active = 0'
    elif status_filter == 'deleted' and include_deleted:
        base_query += ' AND is_deleted = 1'
    elif status_filter == 'locked':
        base_query += ' AND locked_until > ?'
        params.append(datetime.now())
    
    if search:
        base_query += ' AND (username LIKE ? OR email LIKE ?)'
        search_param = f'%{search}%'
        params.extend([search_param, search_param])
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM ({base_query}) as filtered"
    total = cursor.execute(count_query, params).fetchone()[0]
    
    # Add ordering and pagination
    query = base_query + ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    users = cursor.execute(query, params).fetchall()
    
    # Convert to list of dictionaries and add deleted_by username
    users_list = []
    for user in users:
        user_dict = dict(user)
        
        # Get deleted_by username if applicable
        if user_dict['deleted_by']:
            deleted_by_user = cursor.execute(
                'SELECT username FROM users WHERE id = ?', 
                (user_dict['deleted_by'],)
            ).fetchone()
            user_dict['deleted_by_username'] = deleted_by_user['username'] if deleted_by_user else 'Unknown'
        else:
            user_dict['deleted_by_username'] = None
        
        # Remove sensitive data and add computed fields
        user_dict['is_locked'] = user_dict['locked_until'] and datetime.fromisoformat(user_dict['locked_until']) > datetime.now() if user_dict['locked_until'] else False
        users_list.append(user_dict)
    
    return jsonify({
        'users': users_list,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    })

@app.route('/api/users/<int:user_id>', methods=['GET'])
@auth_manager.require_role(['admin'])
def get_user(user_id):
    """Get individual user details - blocks access to admin user"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if this is the admin user and block access
    user = cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
    if user and user['username'] == 'admin':
        return jsonify({'error': 'User not found'}), 404
    
    # Get user details (excluding admin already filtered out)
    user = cursor.execute('''
        SELECT id, username, email, role, is_active, created_at, 
               updated_at, last_login, failed_login_attempts, locked_until,
               is_deleted, deleted_at, deleted_by
        FROM users 
        WHERE id = ? AND username != 'admin'
    ''', (user_id,)).fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_dict = dict(user)
    
    # Get deleted_by username if applicable
    if user_dict['deleted_by']:
        deleted_by_user = cursor.execute(
            'SELECT username FROM users WHERE id = ?', 
            (user_dict['deleted_by'],)
        ).fetchone()
        user_dict['deleted_by_username'] = deleted_by_user['username'] if deleted_by_user else 'Unknown'
    else:
        user_dict['deleted_by_username'] = None
    
    # Add computed fields
    user_dict['is_locked'] = user_dict['locked_until'] and datetime.fromisoformat(user_dict['locked_until']) > datetime.now() if user_dict['locked_until'] else False
    
    return jsonify(user_dict)

@app.route('/api/users', methods=['POST'])
@auth_manager.require_role(['admin'])
def create_user():
    """Create a new user"""
    data = request.json
    
    # Validate required fields
    required_fields = ['username', 'email', 'role']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Prevent creating users with username 'admin'
    if data['username'].lower() == 'admin':
        return jsonify({'error': 'Username not available'}), 400
    
    # Validate role
    valid_roles = ['admin', 'manager', 'driver', 'viewer']
    if data['role'] not in valid_roles:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Generate password if not provided
    password = data.get('password')
    if not password:
        password = secrets.token_urlsafe(12)
        generated_password = True
    else:
        generated_password = False
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if username or email already exists
    existing = cursor.execute('''
        SELECT username FROM users WHERE username = ? OR email = ?
    ''', (data['username'], data['email'])).fetchone()
    
    if existing:
        return jsonify({'error': 'Username or email already exists'}), 400
    
    # Create user
    try:
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['username'], data['email'], password_hash, data['role'], 
              data.get('is_active', True), datetime.now(), datetime.now()))
        
        user_id = cursor.lastrowid
        db.commit()
        
        log_audit_event(g.user['id'], 'USER_CREATE', 'user', user_id, 
                       f"Created user {data['username']} with role {data['role']}")
        
        response = {
            'id': user_id,
            'username': data['username'],
            'email': data['email'],
            'role': data['role'],
            'is_active': data.get('is_active', True)
        }
        
        if generated_password:
            response['generated_password'] = password
        
        return jsonify(response), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@auth_manager.require_role(['admin'])
def update_user(user_id):
    """Update user details"""
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists
    user = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent modification of admin user
    if user['username'] == 'admin':
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent self role/status changes
    if user_id == g.user['id'] and ('role' in data or 'is_active' in data):
        return jsonify({'error': 'Cannot modify your own role or status'}), 400
    
    # Build update query dynamically
    update_fields = []
    params = []
    
    allowed_fields = ['email', 'role', 'is_active']
    for field in allowed_fields:
        if field in data:
            if field == 'role' and data[field] not in ['admin', 'manager', 'driver', 'viewer']:
                return jsonify({'error': 'Invalid role'}), 400
            update_fields.append(f'{field} = ?')
            params.append(data[field])
    
    if not update_fields:
        return jsonify({'error': 'No valid fields to update'}), 400
    
    # Always update updated_at
    update_fields.append('updated_at = ?')
    params.append(datetime.now())
    
    # Add user_id for WHERE clause
    params.append(user_id)
    
    # Execute update
    try:
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        db.commit()
        
        # Log changes
        changes = ', '.join([f"{k}={v}" for k, v in data.items() if k in allowed_fields])
        log_audit_event(g.user['id'], 'USER_UPDATE', 'user', user_id, f"Updated: {changes}")
        
        return jsonify({'message': 'User updated successfully'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@auth_manager.require_role(['admin'])
def delete_user(user_id):
    """Soft delete a user"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists
    user = cursor.execute('SELECT username, role FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent deletion of admin user
    if user['username'] == 'admin':
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent self-deletion
    if user_id == g.user['id']:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    # Check if this is the last admin
    if user['role'] == 'admin':
        admin_count = cursor.execute('SELECT COUNT(*) FROM users WHERE role = ? AND is_active = 1 AND id != ?', 
                                   ('admin', user_id)).fetchone()[0]
        if admin_count == 0:
            return jsonify({'error': 'Cannot delete the last admin user'}), 400
    
    try:
        # Soft delete
        cursor.execute('''
            UPDATE users SET is_active = 0, updated_at = ?
            WHERE id = ?
        ''', (datetime.now(), user_id))
        
        # Invalidate all sessions for this user
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        
        db.commit()
        
        log_audit_event(g.user['id'], 'USER_DELETE', 'user', user_id, 
                       f"Deactivated user {user['username']}")
        
        return jsonify({'message': 'User deactivated successfully'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/reset-password', methods=['POST'])
@auth_manager.require_role(['admin'])
def reset_user_password(user_id):
    """Reset user password"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists
    user = cursor.execute('SELECT username, email FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Protect admin user from password reset
    if user['username'] == 'admin':
        return jsonify({'error': 'User not found'}), 404
    
    # Generate new password
    new_password = secrets.token_urlsafe(12)
    password_hash = generate_password_hash(new_password)
    
    try:
        cursor.execute('''
            UPDATE users SET password_hash = ?, updated_at = ?, failed_login_attempts = 0, locked_until = NULL
            WHERE id = ?
        ''', (password_hash, datetime.now(), user_id))
        
        db.commit()
        
        log_audit_event(g.user['id'], 'PASSWORD_RESET', 'user', user_id, 
                       f"Reset password for user {user['username']}")
        
        return jsonify({
            'message': 'Password reset successfully',
            'username': user['username'],
            'new_password': new_password
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/activity', methods=['GET'])
@auth_manager.require_role(['admin'])
def get_user_activity(user_id):
    """Get user activity log"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists
    user = cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Protect admin user activity from viewing
    if user['username'] == 'admin':
        return jsonify({'error': 'User not found'}), 404
    
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    offset = (page - 1) * per_page
    
    # Get activity logs
    total = cursor.execute('SELECT COUNT(*) FROM audit_log WHERE user_id = ?', (user_id,)).fetchone()[0]
    
    activities = cursor.execute('''
        SELECT id, action, resource_type, resource_id, details, ip_address, created_at
        FROM audit_log
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    ''', (user_id, per_page, offset)).fetchall()
    
    return jsonify({
        'activities': [dict(activity) for activity in activities],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'username': user['username']
    })

# User Lifecycle Management Endpoints

@app.route('/api/users/<int:user_id>/deactivate', methods=['PUT'])
@auth_manager.require_role(['admin', 'manager'])
def deactivate_user(user_id):
    """Deactivate user account"""
    from auth import check_user_service_orders, log_user_lifecycle_event
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists and is active
    user = cursor.execute('''
        SELECT id, username, email, role, is_active, is_deleted 
        FROM users WHERE id = ? AND is_deleted = 0
    ''', (user_id,)).fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Protect admin user from deactivation
    if user['username'] == 'admin':
        return jsonify({'error': 'User not found'}), 404
    
    if not user['is_active']:
        return jsonify({'error': 'User is already deactivated'}), 400
    
    # Prevent self-deactivation
    if user_id == g.user['id']:
        return jsonify({'error': 'Cannot deactivate your own account'}), 400
    
    # Check for pending service orders
    if check_user_service_orders(user_id, db):
        return jsonify({
            'error': 'Cannot deactivate user with pending or in-progress service orders',
            'code': 'CONSTRAINT_VIOLATION'
        }), 409
    
    # Check if this is the last admin
    if user['role'] == 'admin':
        admin_count = cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE role = 'admin' AND is_active = 1 AND is_deleted = 0 AND id != ?
        ''', (user_id,)).fetchone()[0]
        
        if admin_count == 0:
            return jsonify({'error': 'Cannot deactivate the last active admin'}), 400
    
    try:
        # Deactivate user
        cursor.execute('''
            UPDATE users 
            SET is_active = 0, updated_at = ?
            WHERE id = ?
        ''', (datetime.now(), user_id))
        
        # Invalidate all sessions for this user
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        
        db.commit()
        
        # Log audit event
        log_user_lifecycle_event(
            actor_id=g.user['id'],
            action='USER_DEACTIVATED',
            target_user_id=user_id,
            target_username=user['username'],
            details={'target_email': user['email'], 'target_role': user['role']}
        )
        
        return jsonify({
            'message': 'User deactivated successfully',
            'user_id': user_id,
            'username': user['username']
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to deactivate user: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>/activate', methods=['PUT'])
@auth_manager.require_role(['admin', 'manager'])
def activate_user(user_id):
    """Activate user account"""
    from auth import log_user_lifecycle_event
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists and is deactivated
    user = cursor.execute('''
        SELECT id, username, email, role, is_active, is_deleted 
        FROM users WHERE id = ? AND is_deleted = 0
    ''', (user_id,)).fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Protect admin user from activation operations (consistency)
    if user['username'] == 'admin':
        return jsonify({'error': 'User not found'}), 404
    
    if user['is_active']:
        return jsonify({'error': 'User is already active'}), 400
    
    try:
        # Activate user and clear any lock status
        cursor.execute('''
            UPDATE users 
            SET is_active = 1, updated_at = ?, failed_login_attempts = 0, locked_until = NULL
            WHERE id = ?
        ''', (datetime.now(), user_id))
        
        db.commit()
        
        # Log audit event
        log_user_lifecycle_event(
            actor_id=g.user['id'],
            action='USER_ACTIVATED',
            target_user_id=user_id,
            target_username=user['username'],
            details={'target_email': user['email'], 'target_role': user['role']}
        )
        
        return jsonify({
            'message': 'User activated successfully',
            'user_id': user_id,
            'username': user['username']
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to activate user: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>/soft-delete', methods=['DELETE'])
@auth_manager.require_role(['admin', 'manager'])
def soft_delete_user(user_id):
    """Soft delete a user"""
    from auth import check_user_service_orders, log_user_lifecycle_event
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists and is not already deleted
    user = cursor.execute('''
        SELECT id, username, email, role, is_active, is_deleted 
        FROM users WHERE id = ? AND is_deleted = 0
    ''', (user_id,)).fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Protect admin user from soft deletion
    if user['username'] == 'admin':
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent self-deletion
    if user_id == g.user['id']:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    # Check for pending service orders
    if check_user_service_orders(user_id, db):
        return jsonify({
            'error': 'Cannot delete user with pending or in-progress service orders',
            'code': 'CONSTRAINT_VIOLATION'
        }), 409
    
    # Check if this is the last admin
    if user['role'] == 'admin':
        admin_count = cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE role = 'admin' AND is_active = 1 AND is_deleted = 0 AND id != ?
        ''', (user_id,)).fetchone()[0]
        
        if admin_count == 0:
            return jsonify({'error': 'Cannot delete the last active admin'}), 400
    
    try:
        # Soft delete user
        cursor.execute('''
            UPDATE users 
            SET is_deleted = 1, deleted_at = ?, deleted_by = ?, 
                is_active = 0, updated_at = ?
            WHERE id = ?
        ''', (datetime.now(), g.user['id'], datetime.now(), user_id))
        
        # Invalidate all sessions for this user
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        
        db.commit()
        
        # Log audit event
        log_user_lifecycle_event(
            actor_id=g.user['id'],
            action='USER_SOFT_DELETED',
            target_user_id=user_id,
            target_username=user['username'],
            details={
                'target_email': user['email'],
                'target_role': user['role']
            }
        )
        
        return jsonify({
            'message': 'User soft deleted successfully',
            'user_id': user_id,
            'username': user['username']
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to soft delete user: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>/audit-trail', methods=['GET'])
@auth_manager.require_role(['admin'])
def get_user_audit_trail(user_id):
    """Get comprehensive audit trail for a user"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists (including soft deleted)
    user = cursor.execute('''
        SELECT username, email, role, is_deleted 
        FROM users WHERE id = ?
    ''', (user_id,)).fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Protect admin user audit trail from viewing
    if user['username'] == 'admin':
        return jsonify({'error': 'User not found'}), 404
    
    # Get audit trail
    audit_events = cursor.execute('''
        SELECT al.*, u.username as actor_username
        FROM audit_log al
        LEFT JOIN users u ON al.user_id = u.id
        WHERE al.resource_type IN ('user', 'user_lifecycle') 
        AND (al.resource_id = ? OR json_extract(al.details, '$.target_user_id') = ?)
        ORDER BY al.created_at DESC
    ''', (user_id, str(user_id))).fetchall()
    
    return jsonify({
        'user_id': user_id,
        'username': user['username'],
        'is_deleted': user['is_deleted'],
        'audit_events': [dict(event) for event in audit_events]
    })

@app.route('/api/users/batch-deactivate', methods=['POST'])
@auth_manager.require_role(['admin'])
def batch_deactivate_users():
    """Batch deactivate multiple users"""
    from auth import check_user_service_orders
    
    data = request.json
    user_ids = data.get('user_ids', [])
    
    if not user_ids:
        return jsonify({'error': 'No user IDs provided'}), 400
    
    db = get_db()
    results = []
    
    for user_id in user_ids:
        # Check constraints for each user
        if check_user_service_orders(user_id, db):
            results.append({
                'user_id': user_id,
                'status': 'failed',
                'reason': 'Has pending service orders'
            })
            continue
        
        # Check if user is self
        if user_id == g.user['id']:
            results.append({
                'user_id': user_id,
                'status': 'failed',
                'reason': 'Cannot deactivate your own account'
            })
            continue
        
        # Process deactivation
        try:
            cursor = db.cursor()
            user = cursor.execute('''
                SELECT username, role, is_active, is_deleted 
                FROM users WHERE id = ? AND is_deleted = 0
            ''', (user_id,)).fetchone()
            
            if not user:
                results.append({
                    'user_id': user_id,
                    'status': 'failed',
                    'reason': 'User not found'
                })
                continue
            
            # Protect admin user from batch operations
            if user['username'] == 'admin':
                results.append({
                    'user_id': user_id,
                    'status': 'failed',
                    'reason': 'User not found'
                })
                continue
            
            if not user['is_active']:
                results.append({
                    'user_id': user_id,
                    'status': 'failed',
                    'reason': 'User already deactivated'
                })
                continue
            
            # Deactivate user
            cursor.execute('''
                UPDATE users 
                SET is_active = 0, updated_at = ?
                WHERE id = ?
            ''', (datetime.now(), user_id))
            
            # Invalidate sessions
            cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
            
            results.append({
                'user_id': user_id,
                'status': 'success',
                'username': user['username']
            })
            
        except Exception as e:
            results.append({
                'user_id': user_id,
                'status': 'failed',
                'reason': str(e)
            })
    
    # Commit all changes
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Batch operation failed: {str(e)}'}), 500
    
    return jsonify({'results': results})

@app.route('/api/metrics/user-lifecycle', methods=['GET'])
@auth_manager.require_role(['admin'])
def get_user_lifecycle_metrics():
    """Get user lifecycle metrics"""
    db = get_db()
    cursor = db.cursor()
    
    # Get counts by status (excluding admin user)
    total_users = cursor.execute('SELECT COUNT(*) FROM users WHERE username != ?', ('admin',)).fetchone()[0]
    active_users = cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1 AND is_deleted = 0 AND username != ?', ('admin',)).fetchone()[0]
    inactive_users = cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 0 AND is_deleted = 0 AND username != ?', ('admin',)).fetchone()[0]
    deleted_users = cursor.execute('SELECT COUNT(*) FROM users WHERE is_deleted = 1 AND username != ?', ('admin',)).fetchone()[0]
    
    # Get recent activity counts (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_activations = cursor.execute('''
        SELECT COUNT(*) FROM audit_log 
        WHERE action = 'USER_ACTIVATED' AND created_at > ?
    ''', (thirty_days_ago,)).fetchone()[0]
    
    recent_deactivations = cursor.execute('''
        SELECT COUNT(*) FROM audit_log 
        WHERE action = 'USER_DEACTIVATED' AND created_at > ?
    ''', (thirty_days_ago,)).fetchone()[0]
    
    recent_deletions = cursor.execute('''
        SELECT COUNT(*) FROM audit_log 
        WHERE action = 'USER_SOFT_DELETED' AND created_at > ?
    ''', (thirty_days_ago,)).fetchone()[0]
    
    return jsonify({
        'user_counts': {
            'total': total_users,
            'active': active_users,
            'inactive': inactive_users,
            'deleted': deleted_users
        },
        'recent_activity': {
            'activations': recent_activations,
            'deactivations': recent_deactivations,
            'deletions': recent_deletions
        },
        'period': '30_days'
    })

# Security Monitoring Endpoints

@app.route('/api/security/dashboard', methods=['GET'])
def get_security_dashboard():
    """Get security monitoring dashboard data"""
    # Check admin access
    if not g.get('user') or g.user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    db = get_db()
    cursor = db.cursor()
    
    # Get overview metrics
    overview = cursor.execute('SELECT * FROM security_overview').fetchone()
    
    # Get recent alerts
    recent_alerts = cursor.execute('''
        SELECT 
            alert_type,
            severity,
            description,
            created_at,
            u.username
        FROM activity_alerts aa
        LEFT JOIN users u ON aa.user_id = u.id
        WHERE aa.status = 'pending'
        ORDER BY aa.created_at DESC
        LIMIT 10
    ''').fetchall()
    
    # Get high risk users
    high_risk = cursor.execute('SELECT * FROM high_risk_users LIMIT 10').fetchall()
    
    # Get blocked IPs
    blocked_ips = cursor.execute('''
        SELECT ip_address, reason, blocked_at, expires_at
        FROM ip_blocks
        WHERE expires_at > datetime('now')
        ORDER BY blocked_at DESC
    ''').fetchall()
    
    # Get recent suspicious activities
    suspicious = cursor.execute('''
        SELECT 
            al.action,
            al.ip_address,
            al.created_at,
            u.username
        FROM audit_log al
        JOIN users u ON al.user_id = u.id
        WHERE al.action LIKE 'failed_%' 
           OR al.action LIKE 'unauthorized_%'
        ORDER BY al.created_at DESC
        LIMIT 20
    ''').fetchall()
    
    return jsonify({
        'overview': dict_from_row(overview) if overview else {},
        'recent_alerts': [dict_from_row(a) for a in recent_alerts],
        'high_risk_users': [dict_from_row(u) for u in high_risk],
        'blocked_ips': [dict_from_row(ip) for ip in blocked_ips],
        'suspicious_activities': [dict_from_row(s) for s in suspicious]
    })

@app.route('/api/security/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_security_alert(alert_id):
    """Acknowledge a security alert"""
    if not g.get('user') or g.user['role'] not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        UPDATE activity_alerts
        SET status = 'acknowledged',
            acknowledged_at = ?,
            acknowledged_by = ?
        WHERE id = ?
    ''', (datetime.now(), g.user['id'], alert_id))
    
    db.commit()
    
    return jsonify({'success': True})

@app.route('/api/security/ip-blocks', methods=['GET'])
def get_ip_blocks():
    """Get list of blocked IP addresses"""
    if not g.get('user') or g.user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    db = get_db()
    cursor = db.cursor()
    
    blocks = cursor.execute('''
        SELECT * FROM ip_blocks
        WHERE expires_at > datetime('now')
        ORDER BY blocked_at DESC
    ''').fetchall()
    
    return jsonify([dict_from_row(b) for b in blocks])

@app.route('/api/security/ip-blocks/<ip_address>/unblock', methods=['POST'])
def unblock_ip(ip_address):
    """Manually unblock an IP address"""
    if not g.get('user') or g.user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        UPDATE ip_blocks
        SET expires_at = datetime('now')
        WHERE ip_address = ? AND expires_at > datetime('now')
    ''', (ip_address,))
    
    db.commit()
    
    log_audit_event(g.user['id'], 'unblock_ip', 'ip_block', None, 
                   f'Manually unblocked IP: {ip_address}', db)
    
    return jsonify({'success': True})

# Activity Monitoring Endpoints

@app.route('/api/admin/activity/current', methods=['GET'])
@auth_manager.require_role(['admin'])
def get_current_activity():
    """Get currently active user sessions (admin-only)"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get query parameters with error handling
        try:
            include_idle = request.args.get('include_idle', 'true').lower() == 'true'
            sort_by = request.args.get('sort', 'last_activity')
            order = request.args.get('order', 'desc').upper()
            role_filter = request.args.get('role_filter', 'all')
            page = int(request.args.get('page', 1))
            limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 per page
            offset = (page - 1) * limit
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'Invalid query parameters: {str(e)}'}), 400
        
        # Build query using the view
        query = 'SELECT * FROM active_sessions_view WHERE 1=1'
        params = []
        
        # Apply filters
        if not include_idle:
            query += ' AND status = ?'
            params.append('active')
        
        if role_filter != 'all':
            query += ' AND role = ?'
            params.append(role_filter)
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM ({query})"
        total = cursor.execute(count_query, params).fetchone()[0]
        
        # Add sorting
        valid_sort_fields = ['username', 'last_activity', 'login_time', 'role', 'activity_count']
        if sort_by not in valid_sort_fields:
            sort_by = 'last_activity'
        
        query += f' ORDER BY {sort_by} {order}'
        
        # Add pagination
        query += ' LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        # Execute query
        sessions = cursor.execute(query, params).fetchall()
        
        # Format sessions for response
        session_list = []
        for sess in sessions:
            session_dict = dict(sess)
            # Add display name (same as username for now)
            session_dict['display_name'] = session_dict['username']
            # Parse timestamps
            if session_dict.get('last_activity'):
                session_dict['last_activity'] = session_dict['last_activity']
            if session_dict.get('login_time'):
                session_dict['login_time'] = session_dict['login_time']
            session_list.append(session_dict)
        
        # Get summary statistics
        summary_stats = cursor.execute('''
            SELECT 
                COUNT(CASE WHEN status = 'active' THEN 1 END) as total_active,
                COUNT(CASE WHEN status = 'idle' THEN 1 END) as total_idle,
                COUNT(CASE WHEN status = 'warning' THEN 1 END) as total_warning,
                COUNT(*) as total_sessions
            FROM active_sessions_view
        ''').fetchone()
        
        # Get role distribution
        role_stats = cursor.execute('''
            SELECT role, COUNT(*) as count
            FROM active_sessions_view
            GROUP BY role
        ''').fetchall()
        
        by_role = {row['role']: row['count'] for row in role_stats}
        
        # Log the monitoring access
        log_audit_event(g.user['id'], 'VIEW_ACTIVITY_MONITOR', 'activity_monitor', None, 
                       f'Viewed activity monitor with filters: role={role_filter}, include_idle={include_idle}')
        
        return jsonify({
            'success': True,
            'data': {
                'sessions': session_list,
                'summary': {
                    'total_active': summary_stats['total_active'],
                    'total_idle': summary_stats['total_idle'],
                    'total_warning': summary_stats['total_warning'],
                    'by_role': by_role
                },
                'pagination': {
                    'total': total,
                    'page': page,
                    'limit': limit,
                    'pages': (total + limit - 1) // limit
                },
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        })
        
    except sqlite3.OperationalError as e:
        app.logger.error(f'Database error in get_current_activity: {e}')
        return jsonify({'error': 'Database temporarily unavailable. Please try again.'}), 503
    except Exception as e:
        app.logger.error(f'Unexpected error in get_current_activity: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/activity/track', methods=['POST'])
@auth_manager.require_auth
def track_activity():
    """Internal endpoint for tracking user activity"""
    # This endpoint is primarily called by the middleware
    # but can also be called directly for custom tracking
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required = ['page_url', 'action_type']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Add session and user info
    data['session_id'] = session.get('session_id')
    data['user_id'] = g.user['id']
    data['timestamp'] = data.get('timestamp', datetime.utcnow().isoformat())
    
    # Queue for processing if tracker is available
    if activity_tracker:
        try:
            activity_tracker.activity_queue.put_nowait(data)
            return jsonify({'success': True, 'activity_id': None}), 201
        except:
            # Queue full, but don't fail the request
            pass
    
    return jsonify({'success': True, 'activity_id': None}), 201

@app.route('/api/admin/activity/history/<int:user_id>', methods=['GET'])
@auth_manager.require_role(['admin'])
def get_user_activity_history(user_id):
    """Get activity history for a specific user"""
    db = get_db()
    cursor = db.cursor()
    
    # Get query parameters
    days = int(request.args.get('days', 7))
    page_filter = request.args.get('page_filter', '')
    page = int(request.args.get('page', 1))
    limit = min(int(request.args.get('limit', 100)), 500)
    offset = (page - 1) * limit
    
    # Calculate date range
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Build query
    query = '''
        SELECT id, timestamp, page_url, page_title, action_type, 
               duration_ms, ip_address, referrer
        FROM user_activity_log
        WHERE user_id = ? AND timestamp > ?
    '''
    params = [user_id, cutoff_date]
    
    if page_filter:
        query += ' AND page_url LIKE ?'
        params.append(f'%{page_filter}%')
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM ({query})"
    total = cursor.execute(count_query, params).fetchone()[0]
    
    # Add sorting and pagination
    query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    # Execute query
    activities = cursor.execute(query, params).fetchall()
    
    # Transform activities to match frontend expectations
    transformed_activities = []
    for activity in activities:
        activity_dict = dict(activity)
        
        # Map 'action_type' to 'action' for frontend
        if 'action_type' in activity_dict:
            activity_dict['action'] = activity_dict['action_type']
        
        # Create 'details' field combining relevant information
        details_parts = []
        if activity_dict.get('page_title'):
            details_parts.append(f"Page: {activity_dict['page_title']}")
        if activity_dict.get('page_url'):
            details_parts.append(f"URL: {activity_dict['page_url']}")
        if activity_dict.get('referrer'):
            details_parts.append(f"Referrer: {activity_dict['referrer']}")
        
        activity_dict['details'] = ' | '.join(details_parts) if details_parts else 'No additional details'
        
        transformed_activities.append(activity_dict)
    
    # Get user info
    user = cursor.execute('''
        SELECT id, username, email, role
        FROM users WHERE id = ?
    ''', (user_id,)).fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get summary statistics
    summary = cursor.execute('''
        SELECT 
            COUNT(*) as total_activities,
            COUNT(DISTINCT page_url) as unique_pages,
            COUNT(DISTINCT DATE(timestamp)) as active_days,
            AVG(duration_ms) as avg_duration_ms
        FROM user_activity_log
        WHERE user_id = ? AND timestamp > ?
    ''', (user_id, cutoff_date)).fetchone()
    
    # Get most visited pages
    top_pages = cursor.execute('''
        SELECT page_url, COUNT(*) as visit_count
        FROM user_activity_log
        WHERE user_id = ? AND timestamp > ? AND action_type = 'page_view'
        GROUP BY page_url
        ORDER BY visit_count DESC
        LIMIT 5
    ''', (user_id, cutoff_date)).fetchall()
    
    # Log the access
    log_audit_event(g.user['id'], 'VIEW_USER_ACTIVITY', 'user', user_id, 
                   f'Viewed activity history for user {user["username"]} ({days} days)')
    
    return jsonify({
        'success': True,
        'data': {
            'user': dict(user),
            'activities': transformed_activities,
            'summary': {
                'total_activities': summary['total_activities'],
                'unique_pages': summary['unique_pages'],
                'active_days': summary['active_days'],
                'avg_duration_ms': int(summary['avg_duration_ms']) if summary['avg_duration_ms'] else 0,
                'most_visited': [{'page': row['page_url'], 'count': row['visit_count']} 
                               for row in top_pages]
            },
            'pagination': {
                'total': total,
                'page': page,
                'limit': limit,
                'pages': (total + limit - 1) // limit
            }
        }
    })

@app.route('/api/admin/activity/summary', methods=['GET'])
@auth_manager.require_role(['admin', 'manager'])
def get_activity_summary():
    """Get aggregated activity statistics"""
    try:
        db = get_db()
        cursor = db.cursor()
    
        # Get query parameters
        period = request.args.get('period', 'day')  # day, week, month
        date_str = request.args.get('date', datetime.now().date().isoformat())
        
        try:
            target_date = datetime.fromisoformat(date_str).date()
        except:
            return jsonify({'error': 'Invalid date format'}), 400
    
        # Check if summary exists for the date
        summary = cursor.execute('''
            SELECT * FROM activity_summary_daily
            WHERE date = ?
        ''', (target_date,)).fetchone()
        
        if summary:
            # Return cached summary
            return jsonify({
                'success': True,
                'data': {
                    'period': period,
                    'date': str(target_date),
                    'metrics': {
                        'unique_users': summary['unique_users'],
                        'total_sessions': summary['total_sessions'],
                        'total_page_views': summary['total_page_views'],
                        'total_api_calls': summary['total_api_calls'],
                        'avg_session_duration_seconds': summary['avg_session_duration_seconds'],
                        'peak_concurrent_users': summary['peak_concurrent_users'],
                        'peak_hour': summary['peak_hour']
                    },
                    'top_pages': json.loads(summary['top_pages']) if summary['top_pages'] else [],
                    'user_distribution': json.loads(summary['user_distribution']) if summary['user_distribution'] else {},
                    'cached': True
                }
            })
        
        # Generate real-time summary for today or recent dates
        start_date = target_date
        end_date = target_date + timedelta(days=1)
    
        # Get metrics
        metrics = cursor.execute('''
            SELECT 
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT session_id) as total_sessions,
                SUM(CASE WHEN action_type = 'page_view' THEN 1 ELSE 0 END) as page_views,
                SUM(CASE WHEN action_type = 'api_call' THEN 1 ELSE 0 END) as api_calls
            FROM user_activity_log
            WHERE timestamp >= ? AND timestamp < ?
        ''', (start_date, end_date)).fetchone()
        
        # Get hourly distribution
        hourly = cursor.execute('''
            SELECT 
                strftime('%H', timestamp) as hour,
                COUNT(DISTINCT user_id) as users,
                COUNT(*) as activity_count
            FROM user_activity_log
            WHERE timestamp >= ? AND timestamp < ?
            GROUP BY hour
            ORDER BY hour
        ''', (start_date, end_date)).fetchall()
        
        hourly_dist = [{'hour': int(row['hour']), 'users': row['users'], 
                       'activity_count': row['activity_count']} for row in hourly]
        
        # Find peak hour
        peak_hour = None
        peak_users = 0
        for h in hourly_dist:
            if h['users'] > peak_users:
                peak_users = h['users']
                peak_hour = h['hour']
        
        # Get top pages
        top_pages = cursor.execute('''
            SELECT page_url, COUNT(*) as views, 
                   COUNT(DISTINCT user_id) as unique_users,
                   AVG(duration_ms) as avg_duration
            FROM user_activity_log
            WHERE timestamp >= ? AND timestamp < ? AND action_type = 'page_view'
            GROUP BY page_url
            ORDER BY views DESC
            LIMIT 10
        ''', (start_date, end_date)).fetchall()
        
        top_pages_list = [{
            'page': row['page_url'],
            'views': row['views'],
            'unique_users': row['unique_users'],
            'avg_duration_seconds': int(row['avg_duration'] / 1000) if row['avg_duration'] else 0
        } for row in top_pages]
    
        return jsonify({
            'success': True,
            'data': {
                'period': period,
                'date': str(target_date),
                'metrics': {
                    'unique_users': metrics['unique_users'] or 0,
                    'total_sessions': metrics['total_sessions'] or 0,
                    'total_page_views': metrics['page_views'] or 0,
                    'total_api_calls': metrics['api_calls'] or 0,
                    'peak_concurrent_users': peak_users,
                    'peak_hour': peak_hour
                },
                'top_pages': top_pages_list,
                'hourly_distribution': hourly_dist,
                'cached': False
            }
        })
        
    except sqlite3.OperationalError as e:
        app.logger.error(f'Database error in get_activity_summary: {e}')
        return jsonify({'error': 'Database temporarily unavailable. Please try again.'}), 503
    except Exception as e:
        app.logger.error(f'Unexpected error in get_activity_summary: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/activity/alerts', methods=['GET'])
@auth_manager.require_role(['admin'])
def get_activity_alerts():
    """Get activity alerts"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get query parameters with error handling
        try:
            status = request.args.get('status', 'pending')  # pending, acknowledged, resolved, dismissed
            severity = request.args.get('severity')  # info, warning, critical
            days = int(request.args.get('days', 7))
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'Invalid query parameters: {str(e)}'}), 400
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Build query
        query = '''
            SELECT a.*, u.username
            FROM activity_alerts a
            LEFT JOIN users u ON a.user_id = u.id
            WHERE a.created_at > ?
        '''
        params = [cutoff_date]
        
        if status != 'all':
            query += ' AND a.status = ?'
            params.append(status)
        
        if severity:
            query += ' AND a.severity = ?'
            params.append(severity)
        
        query += ' ORDER BY a.created_at DESC LIMIT 100'
        
        alerts = cursor.execute(query, params).fetchall()
        
        # Transform alerts to match frontend expectations
        transformed_alerts = []
        for alert in alerts:
            alert_dict = dict(alert)
            
            # Map 'description' field to 'message' for frontend
            if 'description' in alert_dict:
                alert_dict['message'] = alert_dict['description']
            
            # Map severity values: critical/warning -> high, info -> medium, others -> low
            if 'severity' in alert_dict:
                severity_val = alert_dict['severity']
                if severity_val in ['critical', 'warning']:
                    alert_dict['severity'] = 'high'
                elif severity_val == 'info':
                    alert_dict['severity'] = 'medium'
                else:
                    alert_dict['severity'] = 'low'
            
            transformed_alerts.append(alert_dict)
        
        # Wrap response in nested structure as expected by frontend
        return jsonify({
            'success': True,
            'data': {
                'alerts': transformed_alerts
            }
        })
        
    except sqlite3.OperationalError as e:
        app.logger.error(f'Database error in get_activity_alerts: {e}')
        return jsonify({'error': 'Database temporarily unavailable. Please try again.'}), 503
    except Exception as e:
        app.logger.error(f'Unexpected error in get_activity_alerts: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/activity/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@auth_manager.require_role(['admin'])
def acknowledge_alert(alert_id):
    """Acknowledge an activity alert"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        UPDATE activity_alerts
        SET status = 'acknowledged',
            acknowledged_at = ?,
            acknowledged_by = ?
        WHERE id = ? AND status = 'pending'
    ''', (datetime.now(), g.user['id'], alert_id))
    
    if cursor.rowcount == 0:
        return jsonify({'error': 'Alert not found or already acknowledged'}), 404
    
    db.commit()
    
    return jsonify({'success': True, 'message': 'Alert acknowledged'})

@app.route('/api/admin/sessions/<session_id>/terminate', methods=['POST'])
@auth_manager.require_role(['admin'])
def terminate_session(session_id):
    """Terminate a user session"""
    db = get_db()
    cursor = db.cursor()
    
    # Get session info before deletion
    session_info = cursor.execute('''
        SELECT s.*, u.username
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.id = ?
    ''', (session_id,)).fetchone()
    
    if not session_info:
        return jsonify({'error': 'Session not found'}), 404
    
    # Delete the session
    cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    db.commit()
    
    # Log the action
    log_audit_event(g.user['id'], 'TERMINATE_SESSION', 'session', None,
                   f'Terminated session for user {session_info["username"]} (session: {session_id})')
    
    return jsonify({
        'success': True,
        'message': f'Session terminated for user {session_info["username"]}'
    })

# Device Management Endpoints

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get all devices with their cabinet configurations"""
    db = get_db()
    cursor = db.cursor()
    
    # Get all devices with type information
    devices = cursor.execute('''
        SELECT 
            d.id, d.asset, d.cooler, d.location_id, d.model, 
            d.device_type_id, d.created_at, d.updated_at,
            dt.name as device_type_name, 
            dt.description as device_type_description,
            dt.allows_additional_cabinets,
            l.name as location
        FROM devices d
        JOIN device_types dt ON d.device_type_id = dt.id
        LEFT JOIN locations l ON d.location_id = l.id
        WHERE d.deleted_at IS NULL
        ORDER BY d.created_at DESC
    ''').fetchall()
    
    result = []
    for device in devices:
        device_dict = dict_from_row(device)
        
        # Get cabinet configurations for this device
        cabinets = cursor.execute('''
            SELECT 
                cc.model_name, cc.is_parent, cc.cabinet_index, cc.rows, cc.columns,
                ct.name as cabinet_type, ct.description, ct.icon
            FROM cabinet_configurations cc
            JOIN cabinet_types ct ON cc.cabinet_type_id = ct.id
            WHERE cc.device_id = ?
            ORDER BY cc.is_parent DESC, cc.cabinet_index
        ''', (device['id'],)).fetchall()
        
        # Convert to camelCase for frontend consistency
        cabinet_configs = []
        for cab in cabinets:
            cab_dict = dict_from_row(cab)
            # Convert snake_case to camelCase
            cabinet_configs.append({
                'cabinetType': cab_dict['cabinet_type'],
                'modelName': cab_dict['model_name'],
                'isParent': bool(cab_dict['is_parent']),
                'cabinetIndex': cab_dict['cabinet_index'],
                'rows': cab_dict['rows'],
                'columns': cab_dict['columns']
            })
        
        # Add cabinet configuration
        device_dict['cabinetConfiguration'] = cabinet_configs
        
        # Add enhanced device type details
        device_dict['deviceTypeDetails'] = {
            'id': device_dict['device_type_id'],
            'name': device_dict['device_type_name'],
            'description': device_dict['device_type_description'],
            'allowsAdditionalCabinets': bool(device_dict['allows_additional_cabinets'])
        }
        
        # Remove the raw fields (but keep device_type_id)
        del device_dict['device_type_name']
        del device_dict['device_type_description']
        del device_dict['allows_additional_cabinets']
        
        result.append(device_dict)
    
    return jsonify(result)

@app.route('/api/devices', methods=['POST'])
def create_device():
    """Create a new device with cabinet configurations"""
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get numeric device type ID
        device_type_id = data.get('device_type_id')
        
        if not device_type_id:
            return jsonify({'error': 'device_type_id is required'}), 400
        
        # Validate the device type ID exists
        cursor.execute('SELECT id FROM device_types WHERE id = ?', (device_type_id,))
        if not cursor.fetchone():
            return jsonify({'error': f'Invalid device type ID: {device_type_id}'}), 400
        
        # Get location_id from location name (for backward compatibility)
        location_id = data.get('location_id')
        if not location_id and 'location' in data:
            # Try to find location by name
            location_row = cursor.execute('SELECT id FROM locations WHERE name = ?', (data['location'],)).fetchone()
            if location_row:
                location_id = location_row[0]
            else:
                # Default to Warehouse if location not found
                location_id = 1
        elif not location_id:
            # Default to Warehouse
            location_id = 1
            
        # Insert device
        cursor.execute('''
            INSERT INTO devices (asset, cooler, location_id, model, device_type_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['asset'],
            data['cooler'],
            location_id,
            data['model'],
            device_type_id
        ))
        
        device_id = cursor.lastrowid
        
        # Insert cabinet configurations
        for idx, cabinet in enumerate(data.get('cabinetConfiguration', [])):
            # Look up cabinet type ID
            cabinet_type_name = cabinet.get('cabinetType', cabinet.get('modelName', ''))
            
            cursor.execute('SELECT id, rows, cols FROM cabinet_types WHERE name = ?', (cabinet_type_name,))
            cabinet_type_result = cursor.fetchone()
            
            if cabinet_type_result:
                cabinet_type_id = cabinet_type_result[0]
                rows = cabinet_type_result[1]
                columns = cabinet_type_result[2]
            else:
                # Unknown cabinet type - this shouldn't happen with current data
                return jsonify({'error': f'Invalid cabinet type: {cabinet_type_name}'}), 400
            
            cursor.execute('''
                INSERT INTO cabinet_configurations 
                (device_id, cabinet_type_id, model_name, is_parent, cabinet_index, rows, columns)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                device_id,
                cabinet_type_id,
                cabinet.get('modelName'),
                1 if cabinet.get('isParent', idx == 0) else 0,
                idx,
                rows,
                columns
            ))
        
        # After creating cabinet configurations, create planograms with all slots
        cabinet_configs = cursor.execute('''
            SELECT cc.*, ct.name as cabinet_type_name 
            FROM cabinet_configurations cc
            JOIN cabinet_types ct ON cc.cabinet_type_id = ct.id
            WHERE cc.device_id = ?
        ''', (device_id,)).fetchall()
        
        for config in cabinet_configs:
            # Generate planogram key
            planogram_key = f"{data['asset']}-{config['cabinet_type_name']}-{config['cabinet_index']}"
            
            # Create planogram for this cabinet
            cursor.execute('''
                INSERT INTO planograms (cabinet_id, planogram_key)
                VALUES (?, ?)
            ''', (config['id'], planogram_key))
            
            planogram_id = cursor.lastrowid
            
            # Create all slots with sentinel product
            slots_created = create_all_planogram_slots(
                planogram_id, 
                config['rows'], 
                config['columns'], 
                cursor
            )
            
            print(f"Created planogram with {slots_created} slots for {planogram_key}")
        
        db.commit()
        
        # Return the created device
        return jsonify({
            'id': device_id,
            'asset': data['asset'],
            'cooler': data['cooler'],
            'location_id': location_id,
            'model': data['model'],
            'device_type_id': device_type_id,
            'cabinetConfiguration': data.get('cabinetConfiguration', [])
        }), 201
        
    except sqlite3.IntegrityError as e:
        db.rollback()
        print(f"IntegrityError in create_device: {e}")
        return jsonify({'error': 'Device with this asset number already exists'}), 400
    except Exception as e:
        db.rollback()
        print(f"Exception in create_device: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    """Update an existing device"""
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get location_id from location name (for backward compatibility)
        location_id = data.get('location_id')
        if not location_id and 'location' in data:
            # Try to find location by name
            location_row = cursor.execute('SELECT id FROM locations WHERE name = ?', (data['location'],)).fetchone()
            if location_row:
                location_id = location_row[0]
            else:
                # Default to Warehouse if location not found
                location_id = 1
        elif not location_id:
            # Keep existing location_id
            existing = cursor.execute('SELECT location_id FROM devices WHERE id = ?', (device_id,)).fetchone()
            location_id = existing[0] if existing else 1
            
        # Check if device type ID is provided
        if 'device_type_id' in data:
            device_type_id = data['device_type_id']
            
            # Validate the device type ID exists
            cursor.execute('SELECT id FROM device_types WHERE id = ?', (device_type_id,))
            if not cursor.fetchone():
                return jsonify({'error': f'Invalid device type ID: {device_type_id}'}), 400
            
            cursor.execute('''
                UPDATE devices 
                SET cooler = ?, location_id = ?, model = ?, device_type_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data['cooler'],
                location_id,
                data['model'],
                device_type_id,
                device_id
            ))
        else:
            # Update without changing device type
            cursor.execute('''
                UPDATE devices 
                SET cooler = ?, location_id = ?, model = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data['cooler'],
                location_id,
                data['model'],
                device_id
            ))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Device not found'}), 404
        
        db.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    """Delete a device and all related data"""
    # Soft delete - marking as deleted rather than removing from database
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if device exists and is not already deleted
        cursor.execute('SELECT id FROM devices WHERE id = ? AND deleted_at IS NULL', (device_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Device not found'}), 404
        
        # Soft delete by setting deleted_at timestamp
        cursor.execute('UPDATE devices SET deleted_at = ? WHERE id = ?', 
                      (datetime.utcnow().isoformat(), device_id))
        
        db.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/bulk-delete', methods=['POST'])
def bulk_delete_devices():
    """Delete multiple devices"""
    # Soft delete - marking as deleted rather than removing from database
    device_ids = request.json.get('deviceIds', [])
    db = get_db()
    cursor = db.cursor()
    
    try:
        if not device_ids:
            return jsonify({'success': True, 'deletedCount': 0})
        
        # Soft delete by setting deleted_at timestamp for all devices
        placeholders = ','.join('?' * len(device_ids))
        timestamp = datetime.utcnow().isoformat()
        
        # Build parameters list: timestamp + all device IDs
        params = [timestamp] + device_ids
        
        cursor.execute(f'''UPDATE devices 
                          SET deleted_at = ? 
                          WHERE id IN ({placeholders}) 
                          AND deleted_at IS NULL''', params)
        
        deleted_count = cursor.rowcount
        db.commit()
        
        return jsonify({'success': True, 'deletedCount': deleted_count})
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

# Device Metrics Endpoints

@app.route('/api/devices/<int:device_id>/metrics', methods=['GET'])
def get_device_metrics(device_id):
    """Get or calculate metrics for a specific device"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if device exists
    device = cursor.execute('SELECT id FROM devices WHERE id = ? AND deleted_at IS NULL', 
                          (device_id,)).fetchone()
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    # Check for cached metrics
    cached = cursor.execute('''
        SELECT sold_out_count, days_remaining_inventory, data_collection_rate,
               product_level_percent, units_to_par, last_calculated
        FROM device_metrics
        WHERE device_id = ? 
        AND datetime(last_calculated) > datetime('now', '-15 minutes')
    ''', (device_id,)).fetchone()
    
    if cached:
        # Return cached metrics
        return jsonify({
            'deviceId': device_id,
            'soldOutCount': cached['sold_out_count'],
            'daysRemainingInventory': cached['days_remaining_inventory'],
            'dataCollectionRate': cached['data_collection_rate'],
            'productLevelPercent': cached['product_level_percent'],
            'unitsToPar': cached['units_to_par'],
            'lastCalculated': cached['last_calculated'],
            'cached': True
        })
    
    # Calculate fresh metrics
    metrics = RouteMetricsService.calculate_device_metrics(device_id)
    
    if metrics:
        # Add days since service
        days_since = RouteMetricsService.get_days_since_service(device_id)
        metrics['daysSinceService'] = days_since
        metrics['deviceId'] = device_id
        metrics['cached'] = False
        return jsonify(metrics)
    else:
        return jsonify({'error': 'Failed to calculate metrics'}), 500

@app.route('/api/devices/metrics/batch', methods=['POST'])
def get_batch_device_metrics():
    """Get metrics for multiple devices at once"""
    data = request.json
    
    if not data or 'deviceIds' not in data:
        return jsonify({'error': 'Device IDs array is required'}), 400
    
    device_ids = data['deviceIds']
    if not isinstance(device_ids, list):
        return jsonify({'error': 'deviceIds must be an array'}), 400
    
    db = get_db()
    cursor = db.cursor()
    results = {}
    
    for device_id in device_ids:
        # Check cache first
        cached = cursor.execute('''
            SELECT sold_out_count, days_remaining_inventory, data_collection_rate,
                   product_level_percent, units_to_par, last_calculated
            FROM device_metrics
            WHERE device_id = ? 
            AND datetime(last_calculated) > datetime('now', '-15 minutes')
        ''', (device_id,)).fetchone()
        
        if cached:
            results[device_id] = {
                'soldOutCount': cached['sold_out_count'],
                'daysRemainingInventory': cached['days_remaining_inventory'],
                'dataCollectionRate': cached['data_collection_rate'],
                'productLevelPercent': cached['product_level_percent'],
                'unitsToPar': cached['units_to_par'],
                'cached': True
            }
        else:
            # Calculate fresh
            metrics = RouteMetricsService.calculate_device_metrics(device_id)
            if metrics:
                days_since = RouteMetricsService.get_days_since_service(device_id)
                metrics['daysSinceService'] = days_since
                metrics['cached'] = False
                results[device_id] = metrics
    
    return jsonify(results)

# Service History Endpoints

@app.route('/api/devices/<int:device_id>/service-history', methods=['GET'])
def get_device_service_history(device_id):
    """Get service history for a device"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if device exists
    device = cursor.execute('SELECT id FROM devices WHERE id = ? AND deleted_at IS NULL', 
                          (device_id,)).fetchone()
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    # Get service visits
    visits = cursor.execute('''
        SELECT 
            sv.id, sv.route_id, sv.service_date, sv.units_restocked,
            sv.service_type, sv.technician_id, sv.duration_minutes, sv.notes,
            r.name as route_name
        FROM service_visits sv
        LEFT JOIN routes r ON sv.route_id = r.id
        WHERE sv.device_id = ?
        ORDER BY sv.service_date DESC
        LIMIT 50
    ''', (device_id,)).fetchall()
    
    results = []
    for visit in visits:
        results.append({
            'id': visit['id'],
            'routeId': visit['route_id'],
            'routeName': visit['route_name'],
            'serviceDate': visit['service_date'],
            'unitsRestocked': visit['units_restocked'],
            'serviceType': visit['service_type'],
            'technicianId': visit['technician_id'],
            'durationMinutes': visit['duration_minutes'],
            'notes': visit['notes']
        })
    
    return jsonify(results)

@app.route('/api/service-visits', methods=['POST'])
def create_service_visit():
    """Record a new service visit"""
    data = request.json
    
    required_fields = ['deviceId', 'serviceType']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO service_visits 
            (device_id, route_id, units_restocked, service_type, 
             technician_id, duration_minutes, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['deviceId'],
            data.get('routeId'),
            data.get('unitsRestocked', 0),
            data['serviceType'],
            data.get('technicianId'),
            data.get('durationMinutes'),
            data.get('notes')
        ))
        
        db.commit()
        
        return jsonify({
            'id': cursor.lastrowid,
            'message': 'Service visit recorded successfully'
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

# Service Order Endpoints

@app.route('/api/service-orders', methods=['GET'])
@auth_manager.require_auth
def get_service_orders():
    """Get service orders with driver filtering"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if current user is a driver
    is_driver = g.user and g.user.get('role') == 'driver'
    
    # Optional filters
    route_id = request.args.get('routeId', type=int)
    status = request.args.get('status')
    date = request.args.get('date')
    date_from = request.args.get('dateFrom')
    date_to = request.args.get('dateTo')
    
    query = '''
        SELECT 
            so.id, so.route_id, so.created_at, so.created_by, 
            so.status, so.total_units, so.estimated_duration_minutes,
            so.driver_id, r.name as route_name,
            u.username as driver_name, u.email as driver_email,
            so.last_modified
        FROM service_orders so
        LEFT JOIN routes r ON so.route_id = r.id
        LEFT JOIN users u ON so.driver_id = u.id
        WHERE 1=1
    '''
    params = []
    
    # CRITICAL: Filter by driver if user is driver role
    if is_driver:
        query += ' AND so.driver_id = ?'
        params.append(g.user['id'])
    
    if route_id:
        query += ' AND so.route_id = ?'
        params.append(route_id)
    
    if status:
        query += ' AND so.status = ?'
        params.append(status)
    
    if date:
        query += ' AND DATE(so.created_at) = ?'
        params.append(date)
    
    if date_from:
        query += ' AND DATE(so.created_at) >= DATE(?)'
        params.append(date_from)
    
    if date_to:
        query += ' AND DATE(so.created_at) <= DATE(?)'
        params.append(date_to)
    
    query += ' ORDER BY so.created_at DESC LIMIT 100'
    
    orders = cursor.execute(query, params).fetchall()
    
    results = []
    for order in orders:
        # Get device count, item count, and location for this order
        device_info = cursor.execute('''
            SELECT COUNT(DISTINCT cc.device_id) as device_count,
                   COUNT(DISTINCT soci.id) as item_count,
                   GROUP_CONCAT(DISTINCT l.name) as locations
            FROM service_order_cabinets soc
            JOIN cabinet_configurations cc ON soc.cabinet_configuration_id = cc.id
            LEFT JOIN service_order_cabinet_items soci ON soc.id = soci.service_order_cabinet_id
            LEFT JOIN devices d ON cc.device_id = d.id
            LEFT JOIN locations l ON d.location_id = l.id
            WHERE soc.service_order_id = ?
        ''', (order['id'],)).fetchone()
        
        results.append({
            'id': order['id'],
            'routeId': order['route_id'],
            'routeName': order['route_name'],
            'createdAt': order['created_at'],
            'createdBy': order['created_by'],
            'status': order['status'],
            'totalUnits': order['total_units'],
            'estimatedDurationMinutes': order['estimated_duration_minutes'],
            'driverId': order['driver_id'],
            'driverName': order['driver_name'],
            'driverEmail': order['driver_email'],
            'lastModified': order['last_modified'] if 'last_modified' in order.keys() else None,
            'deviceCount': device_info['device_count'] if device_info else 0,
            'itemCount': device_info['item_count'] if device_info else 0,
            'location': device_info['locations'] if device_info and device_info['locations'] else 'Unknown Location'
        })
    
    # Calculate average fill rate across all pending/in_progress orders
    try:
        avg_fill_rate_result = cursor.execute('''
            SELECT AVG(fill_rate) as avg_fill_rate
            FROM (
                SELECT 
                    soc.id,
                    AVG(CASE 
                        WHEN ps.capacity > 0 THEN ps.quantity * 100.0 / ps.capacity 
                        ELSE 0 
                    END) as fill_rate
                FROM service_order_cabinets soc
                JOIN service_orders so ON soc.service_order_id = so.id
                JOIN cabinet_configurations cc ON soc.cabinet_configuration_id = cc.id
                JOIN devices d ON cc.device_id = d.id
                LEFT JOIN planograms p ON p.planogram_key = d.asset || '_cabinet_' || cc.cabinet_index
                LEFT JOIN planogram_slots ps ON ps.planogram_id = p.id
                WHERE so.status IN ('pending', 'in_progress')
                AND soc.executed_at IS NULL
                GROUP BY soc.id
            )
        ''').fetchone()
        
        avg_fill_rate = round(avg_fill_rate_result['avg_fill_rate'] or 0, 1) if avg_fill_rate_result and avg_fill_rate_result['avg_fill_rate'] is not None else 0
    except Exception as e:
        print(f"Error calculating average fill rate: {e}")
        avg_fill_rate = 0
    
    # Return both orders and average fill rate
    return jsonify({
        'orders': results,
        'avgFillRate': avg_fill_rate
    })

@app.route('/api/service-orders', methods=['POST'])
def create_service_order():
    """Create a new service order"""
    data = request.json
    
    if not data or 'routeId' not in data or 'cabinetSelections' not in data:
        return jsonify({'error': 'routeId and cabinetSelections are required'}), 400
    
    try:
        result = ServiceOrderService.create_service_order(
            data['routeId'],
            data['cabinetSelections'],
            data.get('createdBy')
        )
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_cabinet_fill_rate(cabinet_id, db):
    """Calculate fill rate for a cabinet based on current inventory"""
    cursor = db.cursor()
    
    # Get planogram key for cabinet
    device_cabinet = cursor.execute('''
        SELECT d.asset, cc.cabinet_index 
        FROM cabinet_configurations cc
        JOIN devices d ON cc.device_id = d.id
        WHERE cc.id = ?
    ''', (cabinet_id,)).fetchone()
    
    if not device_cabinet:
        return 0.0
        
    planogram_key = f"{device_cabinet['asset']}_cabinet_{device_cabinet['cabinet_index']}"
    
    # Calculate fill rate from planogram slots
    fill_stats = cursor.execute('''
        SELECT 
            SUM(CASE WHEN ps.capacity > 0 THEN ps.quantity * 1.0 / ps.capacity ELSE 0 END) as total_fill,
            COUNT(CASE WHEN ps.capacity > 0 THEN 1 END) as slots_with_capacity
        FROM planograms p
        LEFT JOIN planogram_slots ps ON ps.planogram_id = p.id
        WHERE p.planogram_key = ?
    ''', (planogram_key,)).fetchone()
    
    if fill_stats and fill_stats['slots_with_capacity'] and fill_stats['slots_with_capacity'] > 0:
        return round((fill_stats['total_fill'] / fill_stats['slots_with_capacity']) * 100, 1)
    
    return 0.0

@app.route('/api/service-orders/<int:order_id>', methods=['GET'])
def get_service_order(order_id):
    """Get details of a specific service order"""
    db = get_db()
    cursor = db.cursor()
    
    # Get order details
    order = cursor.execute('''
        SELECT 
            so.id, so.route_id, so.created_at, so.created_by, 
            so.status, so.total_units, so.estimated_duration_minutes,
            so.driver_id, r.name as route_name,
            u.username as driver_name, u.email as driver_email
        FROM service_orders so
        LEFT JOIN routes r ON so.route_id = r.id
        LEFT JOIN users u ON so.driver_id = u.id
        WHERE so.id = ?
    ''', (order_id,)).fetchone()
    
    if not order:
        return jsonify({'error': 'Service order not found'}), 404
    
    # Get cabinets and their items
    cabinets = cursor.execute('''
        SELECT 
            soc.id as cabinet_order_id,
            cc.id as cabinet_id,
            cc.device_id, cc.cabinet_index,
            ct.name as cabinet_type,
            d.asset, d.cooler, l.name as location,
            sv.id as service_visit_id
        FROM service_order_cabinets soc
        JOIN cabinet_configurations cc ON soc.cabinet_configuration_id = cc.id
        JOIN cabinet_types ct ON cc.cabinet_type_id = ct.id
        JOIN devices d ON cc.device_id = d.id
        LEFT JOIN locations l ON d.location_id = l.id
        LEFT JOIN service_visits sv ON sv.service_order_cabinet_id = soc.id
        WHERE soc.service_order_id = ?
        ORDER BY d.asset, cc.cabinet_index
    ''', (order_id,)).fetchall()
    
    # Get items for each cabinet
    result_cabinets = []
    devices = {}
    
    for cabinet in cabinets:
        # Get items for this cabinet
        items = cursor.execute('''
            SELECT 
                soci.product_id, soci.quantity_needed,
                p.name as product_name, p.category
            FROM service_order_cabinet_items soci
            LEFT JOIN products p ON soci.product_id = p.id
            WHERE soci.service_order_cabinet_id = ?
            ORDER BY p.category, p.name
        ''', (cabinet['cabinet_order_id'],)).fetchall()
        
        cabinet_data = {
            'cabinetOrderId': cabinet['cabinet_order_id'],
            'deviceId': cabinet['device_id'],
            'asset': cabinet['asset'],
            'cooler': cabinet['cooler'],
            'location': cabinet['location'],
            'cabinetIndex': cabinet['cabinet_index'],
            'cabinetType': cabinet['cabinet_type'],
            'isExecuted': cabinet['service_visit_id'] is not None,
            'serviceVisitId': cabinet['service_visit_id'],
            'fillRate': calculate_cabinet_fill_rate(cabinet['cabinet_id'], db),
            'products': []
        }
        
        for item in items:
            cabinet_data['products'].append({
                'productId': item['product_id'],
                'productName': item['product_name'],
                'category': item['category'],
                'quantityNeeded': item['quantity_needed']
            })
        
        result_cabinets.append(cabinet_data)
        
        # Track devices for summary
        device_id = cabinet['device_id']
        if device_id not in devices:
            devices[device_id] = {
                'deviceId': device_id,
                'asset': cabinet['asset'],
                'cooler': cabinet['cooler'],
                'location': cabinet['location'],
                'cabinetCount': 0
            }
        devices[device_id]['cabinetCount'] += 1
    
    return jsonify({
        'id': order['id'],
        'routeId': order['route_id'],
        'routeName': order['route_name'],
        'createdAt': order['created_at'],
        'createdBy': order['created_by'],
        'status': order['status'],
        'totalUnits': order['total_units'],
        'estimatedDurationMinutes': order['estimated_duration_minutes'],
        'driverId': order['driver_id'],
        'driverName': order['driver_name'],
        'driverEmail': order['driver_email'],
        'cabinets': result_cabinets,
        'deviceSummary': list(devices.values())
    })

@app.route('/api/service-orders/<int:order_id>/pick-list', methods=['GET'])
def get_service_order_pick_list(order_id):
    """Get aggregated pick list for a service order"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if order exists
    order = cursor.execute('SELECT id FROM service_orders WHERE id = ?', (order_id,)).fetchone()
    if not order:
        return jsonify({'error': 'Service order not found'}), 404
    
    # Get aggregated pick list from cabinet items
    pick_list = cursor.execute('''
        SELECT 
            soci.product_id,
            p.name as product_name,
            p.category,
            SUM(soci.quantity_needed) as total_quantity
        FROM service_order_cabinet_items soci
        JOIN service_order_cabinets soc ON soci.service_order_cabinet_id = soc.id
        LEFT JOIN products p ON soci.product_id = p.id
        WHERE soc.service_order_id = ?
        GROUP BY soci.product_id, p.name, p.category
        ORDER BY p.category, p.name
    ''', (order_id,)).fetchall()
    
    results = []
    for item in pick_list:
        results.append({
            'productId': item['product_id'],
            'productName': item['product_name'],
            'category': item['category'],
            'quantity': item['total_quantity']
        })
    
    return jsonify(results)

@app.route('/api/service-orders/<int:order_id>', methods=['PUT'])
def update_service_order(order_id):
    """Update service order status"""
    data = request.json
    
    if not data or 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
    if data['status'] not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            UPDATE service_orders 
            SET status = ?
            WHERE id = ?
        ''', (data['status'], order_id))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Service order not found'}), 404
        
        db.commit()
        
        return jsonify({'message': 'Service order updated successfully'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/service-orders/cabinets/<int:cabinet_order_id>/execute', methods=['POST'])
def execute_service_order_cabinet(cabinet_order_id):
    """Execute a single cabinet from a service order"""
    data = request.json
    
    if not data or 'deliveredItems' not in data:
        return jsonify({'error': 'deliveredItems array is required'}), 400
    
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
        ''', (cabinet_order_id,)).fetchone()
        
        if not cabinet_info:
            return jsonify({'error': 'Service order cabinet not found'}), 404
        
        # Check if already executed
        existing_visit = cursor.execute('''
            SELECT id FROM service_visits WHERE service_order_cabinet_id = ?
        ''', (cabinet_order_id,)).fetchone()
        
        if existing_visit:
            return jsonify({'error': 'Cabinet already executed'}), 400
        
        # Create service visit for this cabinet
        cursor.execute('''
            INSERT INTO service_visits
            (service_order_cabinet_id, device_id, service_type, technician_id, notes)
            VALUES (?, ?, 'routine', ?, 'Service order execution')
        ''', (cabinet_order_id, cabinet_info['device_id'], data.get('userId', 1)))
        
        service_visit_id = cursor.lastrowid
        
        # Record delivered items
        total_units = 0
        for item in data['deliveredItems']:
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
        
        # Update service visit with duration
        cursor.execute('''
            UPDATE service_visits
            SET duration_minutes = 10
            WHERE id = ?
        ''', (service_visit_id,))
        
        # Check if all cabinets in the order are executed
        status_check = cursor.execute('''
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN sv.id IS NOT NULL THEN 1 ELSE 0 END) as executed
            FROM service_order_cabinets soc
            LEFT JOIN service_visits sv ON sv.service_order_cabinet_id = soc.id
            WHERE soc.service_order_id = ?
        ''', (cabinet_info['order_id'],)).fetchone()
        
        # Update order status
        if status_check['total'] == status_check['executed']:
            cursor.execute('''
                UPDATE service_orders
                SET status = 'completed'
                WHERE id = ?
            ''', (cabinet_info['order_id'],))
        elif cursor.execute('''SELECT status FROM service_orders WHERE id = ?''', 
                          (cabinet_info['order_id'],)).fetchone()['status'] == 'pending':
            cursor.execute('''
                UPDATE service_orders
                SET status = 'in_progress'
                WHERE id = ?
            ''', (cabinet_info['order_id'],))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'serviceVisitId': service_visit_id,
            'totalUnits': total_units
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/service-orders/cabinets/<int:cabinet_order_id>/rollback', methods=['POST'])
def rollback_service_order_cabinet(cabinet_order_id):
    """Rollback a previously executed cabinet"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get service visit for this cabinet
        visit = cursor.execute('''
            SELECT sv.id, soc.cabinet_configuration_id
            FROM service_visits sv
            JOIN service_order_cabinets soc ON sv.service_order_cabinet_id = soc.id
            WHERE sv.service_order_cabinet_id = ?
        ''', (cabinet_order_id,)).fetchone()
        
        if not visit:
            return jsonify({'error': 'No execution found for this cabinet'}), 404
        
        # Get delivered items
        items = cursor.execute('''
            SELECT product_id, quantity_filled
            FROM service_visit_items
            WHERE service_visit_id = ?
        ''', (visit['id'],)).fetchall()
        
        # Rollback planogram quantities
        for item in items:
            cursor.execute('''
                UPDATE planogram_slots
                SET quantity = quantity - ?
                WHERE planogram_id IN (
                    SELECT id FROM planograms WHERE cabinet_id = ?
                ) AND product_id = ?
            ''', (item['quantity_filled'], visit['cabinet_configuration_id'], item['product_id']))
        
        # Delete service visit items
        cursor.execute('DELETE FROM service_visit_items WHERE service_visit_id = ?', (visit['id'],))
        
        # Delete service visit
        cursor.execute('DELETE FROM service_visits WHERE id = ?', (visit['id'],))
        
        # Update order status if needed
        cabinet_info = cursor.execute('''
            SELECT service_order_id FROM service_order_cabinets WHERE id = ?
        ''', (cabinet_order_id,)).fetchone()
        
        if cabinet_info:
            # Check if any cabinets are still executed
            executed_count = cursor.execute('''
                SELECT COUNT(*) as count
                FROM service_order_cabinets soc
                JOIN service_visits sv ON sv.service_order_cabinet_id = soc.id
                WHERE soc.service_order_id = ?
            ''', (cabinet_info['service_order_id'],)).fetchone()
            
            if executed_count['count'] == 0:
                cursor.execute('''
                    UPDATE service_orders
                    SET status = 'pending'
                    WHERE id = ?
                ''', (cabinet_info['service_order_id'],))
            else:
                cursor.execute('''
                    UPDATE service_orders
                    SET status = 'in_progress'
                    WHERE id = ?
                ''', (cabinet_info['service_order_id'],))
        
        db.commit()
        
        return jsonify({'success': True, 'message': 'Cabinet execution rolled back successfully'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

# Route Planning Configuration Endpoints

@app.route('/api/route-planning/config', methods=['GET'])
def get_route_planning_config():
    """Get route planning configuration"""
    db = get_db()
    cursor = db.cursor()
    
    config = cursor.execute('''
        SELECT critical_dri_threshold, warning_dri_threshold, ok_dri_threshold,
               auto_select_critical, metrics_cache_ttl_minutes
        FROM route_planning_config
        LIMIT 1
    ''').fetchone()
    
    if config:
        return jsonify({
            'criticalDriThreshold': config['critical_dri_threshold'],
            'warningDriThreshold': config['warning_dri_threshold'],
            'okDriThreshold': config['ok_dri_threshold'],
            'autoSelectCritical': bool(config['auto_select_critical']),
            'metricsCacheTtlMinutes': config['metrics_cache_ttl_minutes']
        })
    else:
        # Return defaults
        return jsonify({
            'criticalDriThreshold': 1,
            'warningDriThreshold': 3,
            'okDriThreshold': 7,
            'autoSelectCritical': True,
            'metricsCacheTtlMinutes': 15
        })

@app.route('/api/route-planning/config', methods=['PUT'])
def update_route_planning_config():
    """Update route planning configuration"""
    data = request.json
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if config exists
        existing = cursor.execute('SELECT id FROM route_planning_config LIMIT 1').fetchone()
        
        if existing:
            # Update existing
            cursor.execute('''
                UPDATE route_planning_config SET
                    critical_dri_threshold = ?,
                    warning_dri_threshold = ?,
                    ok_dri_threshold = ?,
                    auto_select_critical = ?,
                    metrics_cache_ttl_minutes = ?
                WHERE id = ?
            ''', (
                data.get('criticalDriThreshold', 1),
                data.get('warningDriThreshold', 3),
                data.get('okDriThreshold', 7),
                data.get('autoSelectCritical', True),
                data.get('metricsCacheTtlMinutes', 15),
                existing['id']
            ))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO route_planning_config 
                (critical_dri_threshold, warning_dri_threshold, ok_dri_threshold,
                 auto_select_critical, metrics_cache_ttl_minutes)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data.get('criticalDriThreshold', 1),
                data.get('warningDriThreshold', 3),
                data.get('okDriThreshold', 7),
                data.get('autoSelectCritical', True),
                data.get('metricsCacheTtlMinutes', 15)
            ))
        
        db.commit()
        
        return jsonify({'message': 'Configuration updated successfully'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/service-orders/preview', methods=['POST'])
def preview_service_order():
    """Generate service order preview with configurable service date"""
    try:
        data = request.json
        route_id = data.get('routeId')
        service_date_str = data.get('serviceDate')
        cabinet_selections = data.get('cabinetSelections', [])
        
        # Validation
        if not route_id or not cabinet_selections:
            return jsonify({'error': 'Missing required fields: routeId and cabinetSelections'}), 400
        
        if not service_date_str:
            return jsonify({'error': 'Missing required field: serviceDate'}), 400
            
        try:
            service_date = datetime.strptime(service_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Date validation
        today = datetime.now().date()
        days_until_service = (service_date - today).days
        
        if days_until_service < 0:
            return jsonify({'error': 'Service date cannot be in the past'}), 400
        if days_until_service > 5:
            return jsonify({'error': 'Service date cannot be more than 5 days in future'}), 400
        
        # Process order
        response = generate_order_preview(route_id, service_date, cabinet_selections, days_until_service)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in preview_service_order: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def generate_order_preview(route_id, service_date, cabinet_selections, days_until_service):
    """Generate the order preview data structure"""
    response = {
        'routeId': route_id,
        'serviceDate': service_date.isoformat(),
        'daysUntilService': days_until_service,
        'totalUnits': 0,
        'totalProducts': 0,
        'devices': []
    }
    
    # Group selections by device
    device_cabinets = {}
    for selection in cabinet_selections:
        device_id = selection.get('deviceId')
        cabinet_index = selection.get('cabinetIndex')
        
        if device_id is None or cabinet_index is None:
            continue
            
        if device_id not in device_cabinets:
            device_cabinets[device_id] = []
        device_cabinets[device_id].append(cabinet_index)
    
    # Process each device
    db = get_db()
    cursor = db.cursor()
    
    for device_id, cabinet_indices in device_cabinets.items():
        try:
            device_data = process_device_order(cursor, device_id, cabinet_indices, days_until_service)
            if device_data and device_data['totalUnits'] > 0:
                response['devices'].append(device_data)
                response['totalUnits'] += device_data['totalUnits']
        except Exception as e:
            print(f"Error processing device {device_id}: {str(e)}")
            continue
    
    # Count unique products across all devices
    unique_products = set()
    for device in response['devices']:
        for cabinet in device['cabinets']:
            for product in cabinet['products']:
                unique_products.add(product['productId'])
    
    response['totalProducts'] = len(unique_products)
    
    return response

def process_device_order(cursor, device_id, cabinet_indices, days_until_service):
    """Calculate order for specific device cabinets"""
    print(f"[DEBUG] Processing device {device_id} with cabinet indices: {cabinet_indices}")
    
    # Get device info
    cursor.execute('''
        SELECT d.id, d.asset, COALESCE(l.name, 'Unknown') as location
        FROM devices d
        LEFT JOIN locations l ON d.location_id = l.id
        WHERE d.id = ? AND (d.deleted_at IS NULL OR d.deleted_at = '')
    ''', (device_id,))
    
    device_info = cursor.fetchone()
    if not device_info:
        raise ValueError(f"Device {device_id} not found or deleted")
    
    device_data = {
        'deviceId': device_info['id'],
        'asset': device_info['asset'],
        'location': device_info['location'],
        'totalUnits': 0,
        'cabinets': []
    }
    
    # Process each cabinet
    for cabinet_index in cabinet_indices:
        try:
            cabinet_order = calculate_cabinet_order(cursor, device_id, cabinet_index, days_until_service)
            if cabinet_order and cabinet_order['totalUnits'] > 0:
                device_data['cabinets'].append(cabinet_order)
                device_data['totalUnits'] += cabinet_order['totalUnits']
        except Exception as e:
            print(f"Error processing cabinet {cabinet_index} for device {device_id}: {str(e)}")
            continue
    
    return device_data

def calculate_cabinet_order(cursor, device_id, cabinet_index, days_until_service):
    """Calculate aggregated order for a cabinet"""
    print(f"[DEBUG] Calculating order for device {device_id}, cabinet index {cabinet_index}")
    
    # Get cabinet info
    cursor.execute('''
        SELECT model_name, rows, columns
        FROM cabinet_configurations
        WHERE device_id = ? AND cabinet_index = ?
    ''', (device_id, cabinet_index))
    
    cabinet_info = cursor.fetchone()
    if not cabinet_info:
        print(f"[DEBUG] Cabinet not found in database for device_id={device_id}, cabinet_index={cabinet_index}")
        raise ValueError(f"Cabinet not found: device {device_id}, index {cabinet_index}")
    
    # Get aggregated product data with comprehensive LEFT JOINs
    cursor.execute('''
        SELECT 
            ps.product_id,
            COALESCE(p.name, 'Unknown Product') as product_name,
            SUM(COALESCE(ps.quantity, 0)) as total_quantity,
            SUM(COALESCE(ps.par_level, 0)) as total_par_level,
            SUM(COALESCE(sm.daily_velocity, 0)) as total_daily_velocity
        FROM planogram_slots ps
        JOIN planograms pl ON ps.planogram_id = pl.id
        JOIN cabinet_configurations cc ON pl.cabinet_id = cc.id
        LEFT JOIN products p ON ps.product_id = p.id
        LEFT JOIN slot_metrics sm ON ps.id = sm.planogram_slot_id
        WHERE cc.device_id = ? 
            AND cc.cabinet_index = ?
            AND ps.product_id <> 1
        GROUP BY ps.product_id, p.name
        HAVING SUM(COALESCE(ps.par_level, 0)) > 0
    ''', (device_id, cabinet_index))
    
    products = cursor.fetchall()
    print(f"[DEBUG] Found {len(products)} products for cabinet")
    
    cabinet_data = {
        'cabinetIndex': cabinet_index,
        'cabinetType': cabinet_info['model_name'],
        'totalUnits': 0,
        'products': []
    }
    
    for product in products:
        quantity = product['total_quantity'] or 0
        par_level = product['total_par_level'] or 0
        daily_velocity = product['total_daily_velocity'] or 0
        
        # Calculate order quantity using business rules
        if daily_velocity > 0:
            order_quantity = round((par_level - quantity) + (daily_velocity * days_until_service))
        else:
            order_quantity = round(par_level - quantity)
        
        # Only include if order needed
        if order_quantity > 0:
            cabinet_data['products'].append({
                'productId': product['product_id'],
                'productName': product['product_name'],
                'orderQuantity': order_quantity,
                'currentQuantity': quantity,
                'parLevel': par_level,
                'dailyVelocity': daily_velocity
            })
            cabinet_data['totalUnits'] += order_quantity
    
    return cabinet_data

# Planogram Management Endpoints

@app.route('/api/planograms/<planogram_key>', methods=['GET'])
def get_planogram(planogram_key):
    """Get planogram data by key"""
    db = get_db()
    cursor = db.cursor()
    
    # Get planogram
    planogram = cursor.execute('''
        SELECT p.id, p.cabinet_id, p.planogram_key, p.updated_at
        FROM planograms p
        WHERE p.planogram_key = ?
    ''', (planogram_key,)).fetchone()
    
    if not planogram:
        return jsonify({}), 200  # Return empty object if not found
    
    # Get all slots for this planogram
    slots = cursor.execute('''
        SELECT slot_position, product_id, product_name, quantity, capacity, par_level, price
        FROM planogram_slots
        WHERE planogram_id = ?
    ''', (planogram['id'],)).fetchall()
    
    # Convert to the expected format
    result = {}
    for slot in slots:
        result[slot['slot_position']] = {
            'productId': slot['product_id'],
            'productName': slot['product_name'],
            'quantity': slot['quantity'],
            'capacity': slot['capacity'],
            'parLevel': slot['par_level'],
            'price': float(slot['price']) if slot['price'] else None
        }
    
    return jsonify(result)

@app.route('/api/planograms', methods=['POST'])
def save_planogram():
    """Save or update planogram data with sentinel product approach"""
    data = request.json
    
    # Use direct connection instead of Flask's g context
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    cursor = conn.cursor()
    
    # Track updates for validation
    updates_made = 0
    
    try:
        # Start explicit transaction
        conn.execute('BEGIN TRANSACTION')
        # Handle both data formats
        if 'planogramKey' in data:
            # Old format: {planogramKey: 'key', planogramData: {...}}
            planograms_to_save = {data['planogramKey']: data.get('planogramData', {})}
        else:
            # New format: {planogram_key: {slots...}, ...}
            planograms_to_save = data
        
        for planogram_key, slots in planograms_to_save.items():
            print(f"\nProcessing planogram: {planogram_key}")
            print(f"Number of slots to process: {len(slots)}")
            
            # Parse planogram key
            parts = planogram_key.split('-')
            if len(parts) < 3:
                continue
                
            asset_id = parts[0]
            cabinet_type = parts[1]
            cabinet_index = int(parts[2])
            
            # Find device and get planogram
            device = cursor.execute(
                'SELECT id FROM devices WHERE asset = ? AND deleted_at IS NULL', 
                (asset_id,)
            ).fetchone()
            
            if not device:
                continue
            
            # Look up cabinet type ID
            cabinet_type_result = cursor.execute(
                'SELECT id FROM cabinet_types WHERE name = ?', 
                (cabinet_type,)
            ).fetchone()
            
            if not cabinet_type_result:
                continue
                
            cabinet_type_id = cabinet_type_result['id']
            
            # Find the planogram by key
            planogram = cursor.execute('''
                SELECT id FROM planograms 
                WHERE planogram_key = ?
            ''', (planogram_key,)).fetchone()
            
            if not planogram:
                # This shouldn't happen with new system - planograms are created with devices
                print(f"Warning: No planogram found for {planogram_key}")
                continue
                
            planogram_id = planogram['id']
            
            # Process each slot - ALL slots already exist with sentinel approach
            for slot_id, slot_data in slots.items():
                # Get current slot data
                current_slot = cursor.execute('''
                    SELECT product_id, product_name 
                    FROM planogram_slots 
                    WHERE planogram_id = ? AND slot_position = ?
                ''', (planogram_id, slot_id)).fetchone()
                
                if not current_slot:
                    # This should never happen with the new system
                    print(f"Warning: Slot {slot_id} doesn't exist for planogram {planogram_id}")
                    continue
                
                # Default to sentinel if no product specified
                new_product_id = int(slot_data.get('productId', 1)) if slot_data else 1
                new_product_name = slot_data.get('productName', 'EMPTY_SLOT') if slot_data else 'EMPTY_SLOT'
                
                # Track changes and update
                if current_slot['product_id'] != new_product_id:
                    print(f"Slot {slot_id}: Changing product from {current_slot['product_id']} ({current_slot['product_name']}) to {new_product_id} ({new_product_name})")
                    
                    if current_slot['product_id'] != 1 and new_product_id == 1:
                        # Product removed (changed to sentinel)
                        print(f"  -> Removing product (setting to sentinel)")
                        cursor.execute('''
                            UPDATE planogram_slots
                            SET product_id = ?,
                                product_name = ?,
                                quantity = 0,
                                capacity = 0,
                                par_level = 0,
                                price = 0.00,
                                cleared_at = CURRENT_TIMESTAMP,
                                previous_product_id = ?
                            WHERE planogram_id = ? AND slot_position = ?
                        ''', (
                            new_product_id,
                            new_product_name,
                            current_slot['product_id'],
                            planogram_id,
                            slot_id
                        ))
                        if cursor.rowcount > 0:
                            updates_made += 1
                            print(f"  -> Successfully removed product from slot {slot_id}")
                    else:
                        # Product added or replaced
                        print(f"  -> Adding/replacing product")
                        cursor.execute('''
                            UPDATE planogram_slots
                            SET product_id = ?,
                                product_name = ?,
                                quantity = ?,
                                capacity = ?,
                                par_level = ?,
                                price = ?,
                                cleared_at = CURRENT_TIMESTAMP,
                                previous_product_id = CASE 
                                    WHEN ? != 1 AND ? != 1 THEN ?
                                    ELSE previous_product_id 
                                END
                            WHERE planogram_id = ? AND slot_position = ?
                        ''', (
                            new_product_id,
                            new_product_name,
                            slot_data.get('quantity', 0) if slot_data else 0,
                            slot_data.get('capacity', 0) if slot_data else 0,
                            slot_data.get('parLevel', 0) if slot_data else 0,
                            slot_data.get('price', 0.00) if slot_data else 0.00,
                            current_slot['product_id'],
                            new_product_id,
                            current_slot['product_id'],
                            planogram_id,
                            slot_id
                        ))
                        if cursor.rowcount > 0:
                            updates_made += 1
                            print(f"  -> Successfully updated slot {slot_id} with product {new_product_id}")
                else:
                    # Same product, just update quantities
                    cursor.execute('''
                        UPDATE planogram_slots
                        SET quantity = ?,
                            capacity = ?,
                            par_level = ?,
                            price = ?
                        WHERE planogram_id = ? AND slot_position = ?
                    ''', (
                        slot_data.get('quantity', 0) if slot_data else 0,
                        slot_data.get('capacity', 0) if slot_data else 0,
                        slot_data.get('parLevel', 0) if slot_data else 0,
                        slot_data.get('price', 0.00) if slot_data else 0.00,
                        planogram_id,
                        slot_id
                    ))
                    
                    # Verify the update
                    if cursor.rowcount > 0:
                        updates_made += 1
                        print(f"Updated slot {slot_id}: quantity={slot_data.get('quantity', 0)}")
        
        # Commit the transaction
        conn.execute('COMMIT')
        conn.close()
        
        print(f"Planogram save completed. Total slots updated: {updates_made}")
        
        if updates_made == 0:
            print("WARNING: No slots were actually updated!")
        
        return jsonify({'success': True, 'updates': updates_made})
        
    except Exception as e:
        conn.execute('ROLLBACK')
        conn.close()
        print(f"Error saving planogram: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/planograms/export', methods=['GET'])
def export_planograms():
    """Export all planogram data"""
    db = get_db()
    cursor = db.cursor()
    
    # Get all planograms with device and cabinet info (excluding soft-deleted devices)
    planograms = cursor.execute('''
        SELECT 
            p.planogram_key,
            d.asset,
            d.cooler,
            l.name as location,
            ct.name as cabinet_type,
            c.cabinet_index,
            COUNT(ps.id) as slot_count,
            SUM(CASE WHEN ps.product_id IS NOT NULL THEN 1 ELSE 0 END) as filled_slots
        FROM planograms p
        JOIN cabinet_configurations c ON p.cabinet_id = c.id
        JOIN devices d ON c.device_id = d.id
        LEFT JOIN locations l ON d.location_id = l.id
        JOIN cabinet_types ct ON c.cabinet_type_id = ct.id
        LEFT JOIN planogram_slots ps ON p.id = ps.planogram_id
        WHERE d.deleted_at IS NULL
        GROUP BY p.id
    ''').fetchall()
    
    result = [dict_from_row(p) for p in planograms]
    
    # Monitor data export for potential exfiltration
    if security_monitor and g.get('user'):
        is_excessive, should_alert, alert_details = security_monitor.check_data_export(
            g.user['id'], request.path, row_count=len(result)
        )
        if should_alert:
            security_monitor.create_security_alert(alert_details)
        
        # Check sensitive data access
        is_sensitive, should_alert, alert_details = security_monitor.check_sensitive_data_access(
            g.user['id'], request.path
        )
        if should_alert:
            security_monitor.create_security_alert(alert_details)
    
    return jsonify(result)

# AI Planogram Optimization Endpoints

@app.route('/api/planograms/ai-suggestions', methods=['POST'])
def get_planogram_ai_suggestions():
    """Get AI-powered planogram optimization suggestions."""
    try:
        data = request.json
        device_id = data.get('device_id')
        cabinet_index = data.get('cabinet_index', 0)
        optimization_type = data.get('optimization_type', 'full')
        
        # Validate inputs
        if not device_id:
            return jsonify({'error': 'device_id is required'}), 400
            
        # Check API key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({'error': 'AI service not configured'}), 503
            
        # Initialize optimizer and get recommendations
        optimizer = PlanogramOptimizer(api_key)
        result = optimizer.generate_recommendations(
            device_id=device_id,
            cabinet_index=cabinet_index,
            optimization_type=optimization_type
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/planograms/ai-available', methods=['GET'])
def check_ai_available():
    """Check if AI optimization service is available."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    return jsonify({'available': bool(api_key)})

# New AI-Powered Endpoints

@app.route('/api/planograms/realtime/score', methods=['POST'])
@auth_manager.require_auth
def realtime_planogram_score():
    """Real-time scoring for planogram placement"""
    try:
        from ai_services import PlanogramScorer
        
        data = request.json
        planogram_data = data.get('planogram', {})
        product_id = data.get('product_id')
        slot_position = data.get('position', {})
        historical_data = data.get('historical_data')
        
        if not product_id or not slot_position:
            return jsonify({'error': 'Product ID and position required'}), 400
        
        scorer = PlanogramScorer()
        result = scorer.score_placement(
            planogram_data=planogram_data,
            product_id=int(product_id),
            slot_position=slot_position,
            historical_data=historical_data
        )
        
        return jsonify(result)
        
    except ImportError:
        return jsonify({'error': 'AI services not available'}), 503
    except Exception as e:
        logger.error(f"Scoring error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/planograms/predict/revenue', methods=['POST'])
@auth_manager.require_role(['manager', 'admin'])
def predict_planogram_revenue():
    """Predict revenue impact of planogram changes"""
    try:
        from ai_services import RevenuePrediction
        
        data = request.json
        planogram_data = data.get('planogram', {})
        prediction_days = data.get('days', 30)
        include_seasonality = data.get('include_seasonality', True)
        
        # Get historical sales data
        db = get_db()
        cursor = db.cursor()
        
        # Fetch last 90 days of sales data
        historical_sales = cursor.execute("""
            SELECT 
                date,
                product_id,
                SUM(quantity) as quantity,
                SUM(revenue) as revenue
            FROM sales
            WHERE date >= date('now', '-90 days')
            GROUP BY date, product_id
            ORDER BY date DESC
        """).fetchall()
        
        # Convert to list of dicts
        sales_data = [
            {
                'date': row[0],
                'product_id': row[1],
                'quantity': row[2],
                'revenue': row[3]
            }
            for row in historical_sales
        ]
        
        predictor = RevenuePrediction()
        result = predictor.predict_revenue(
            planogram_data=planogram_data,
            historical_sales=sales_data,
            prediction_days=prediction_days,
            include_seasonality=include_seasonality
        )
        
        return jsonify(result)
        
    except ImportError:
        return jsonify({'error': 'AI services not available'}), 503
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/planograms/optimize/heat-zones', methods=['GET'])
@auth_manager.require_auth
def get_heat_zones():
    """Get heat zone optimization data for a device"""
    try:
        from ai_services import HeatZoneOptimizer
        
        device_id = request.args.get('device_id', type=int)
        
        if not device_id:
            return jsonify({'error': 'Device ID required'}), 400
        
        # Get historical sales by position
        db = get_db()
        cursor = db.cursor()
        
        sales_by_position = cursor.execute("""
            SELECT 
                ps.row,
                ps.column_position as column,
                s.product_id,
                SUM(s.quantity) as quantity,
                SUM(s.revenue) as revenue
            FROM sales s
            JOIN planogram_slots ps ON ps.planogram_id = s.planogram_id
            WHERE s.device_id = ?
                AND s.date >= date('now', '-30 days')
            GROUP BY ps.row, ps.column_position, s.product_id
        """, (device_id,)).fetchall()
        
        # Convert to required format
        historical_sales = [
            {
                'position': {'row': row[0], 'column': row[1]},
                'product_id': row[2],
                'quantity': row[3],
                'revenue': row[4]
            }
            for row in sales_by_position
        ]
        
        # Get cabinet configuration
        cabinet_config = cursor.execute("""
            SELECT 
                cc.cabinet_number,
                ct.model_name,
                cc.rows,
                cc.columns
            FROM cabinet_configurations cc
            JOIN cabinet_types ct ON cc.cabinet_type_id = ct.id
            WHERE cc.device_id = ?
        """, (device_id,)).fetchall()
        
        cabinet_data = {
            'cabinets': [
                {
                    'number': row[0],
                    'type': row[1],
                    'rows': row[2],
                    'columns': row[3]
                }
                for row in cabinet_config
            ]
        } if cabinet_config else None
        
        optimizer = HeatZoneOptimizer()
        result = optimizer.generate_heat_map(
            device_id=device_id,
            historical_sales=historical_sales,
            cabinet_config=cabinet_data
        )
        
        return jsonify(result)
        
    except ImportError:
        return jsonify({'error': 'AI services not available'}), 503
    except Exception as e:
        logger.error(f"Heat zone error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/planograms/optimize', methods=['POST'])
@auth_manager.require_role(['manager', 'admin'])
def optimize_planogram():
    """Optimize planogram based on heat zones and constraints"""
    try:
        from ai_services import HeatZoneOptimizer
        
        data = request.json
        current_planogram = data.get('planogram', {})
        heat_map = data.get('heat_map', {})
        constraints = data.get('constraints', {})
        
        optimizer = HeatZoneOptimizer()
        result = optimizer.optimize_placement(
            current_planogram=current_planogram,
            heat_map=heat_map,
            constraints=constraints
        )
        
        return jsonify(result)
        
    except ImportError:
        return jsonify({'error': 'AI services not available'}), 503
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Data Migration Endpoint

@app.route('/api/migrate', methods=['POST'])
def migrate_data():
    """Migrate data from localStorage format to database"""
    data = request.json
    devices = data.get('devices', [])
    planograms = data.get('planograms', {})
    
    db = get_db()
    cursor = db.cursor()
    
    migrated_devices = 0
    migrated_planograms = 0
    errors = []
    
    try:
        for device_data in devices:
            try:
                # Check if device already exists (excluding soft-deleted)
                existing = cursor.execute(
                    'SELECT id FROM devices WHERE asset = ? AND deleted_at IS NULL', 
                    (device_data['asset'],)
                ).fetchone()
                
                if not existing:
                    # Create device - handle legacy deviceType string
                    device_type_str = device_data.get('deviceType', 'picovision')
                    # Map legacy strings to IDs
                    if device_type_str == 'picovision':
                        device_type_id = 1
                    elif device_type_str == 'express':
                        device_type_id = 2
                    else:
                        device_type_id = 1  # Default to PicoVision
                    
                    # Get location_id from location name
                    location_name = device_data.get('location', 'Warehouse')
                    location_row = cursor.execute('SELECT id FROM locations WHERE name = ?', (location_name,)).fetchone()
                    location_id = location_row[0] if location_row else 1  # Default to Warehouse
                    
                    cursor.execute('''
                        INSERT INTO devices (asset, cooler, location_id, model, device_type_id)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        device_data['asset'],
                        device_data['cooler'],
                        location_id,
                        device_data['model'],
                        device_type_id
                    ))
                    
                    device_id = cursor.lastrowid
                    
                    # Insert cabinet configurations
                    for idx, cabinet in enumerate(device_data.get('cabinetConfiguration', [])):
                        # Look up cabinet type ID
                        cabinet_name = cabinet.get('cabinetType', cabinet.get('modelName', ''))
                        cursor.execute('SELECT id, rows, cols FROM cabinet_types WHERE name = ?', (cabinet_name,))
                        cabinet_type_result = cursor.fetchone()
                        
                        if cabinet_type_result:
                            cabinet_type_id = cabinet_type_result[0]
                            rows = cabinet_type_result[1]
                            columns = cabinet_type_result[2]
                        else:
                            # Default to Cooler if not found
                            cabinet_type_id = 1
                            rows = 5
                            columns = 8
                        
                        cursor.execute('''
                            INSERT INTO cabinet_configurations 
                            (device_id, cabinet_type_id, model_name, is_parent, cabinet_index, rows, columns)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            device_id,
                            cabinet_type_id,
                            cabinet.get('modelName'),
                            1 if cabinet.get('isParent', idx == 0) else 0,
                            idx,
                            rows,
                            columns
                        ))
                    
                    migrated_devices += 1
                    
            except Exception as e:
                errors.append(f"Error migrating device {device_data.get('asset', 'unknown')}: {str(e)}")
        
        # Migrate planograms
        for planogram_key, planogram_data in planograms.items():
            try:
                # Save planogram using existing endpoint logic
                parts = planogram_key.split('-')
                if len(parts) >= 3:
                    asset_id = parts[0]
                    
                    # Find device (excluding soft-deleted)
                    device = cursor.execute(
                        'SELECT id FROM devices WHERE asset = ? AND deleted_at IS NULL', 
                        (asset_id,)
                    ).fetchone()
                    
                    if device:
                        cabinet_index = int(parts[2])
                        cabinet = cursor.execute('''
                            SELECT id FROM cabinet_configurations 
                            WHERE device_id = ? AND cabinet_index = ?
                        ''', (device['id'], cabinet_index)).fetchone()
                        
                        if cabinet:
                            # Check if planogram exists
                            existing_planogram = cursor.execute(
                                'SELECT id FROM planograms WHERE planogram_key = ?',
                                (planogram_key,)
                            ).fetchone()
                            
                            if not existing_planogram:
                                cursor.execute('''
                                    INSERT INTO planograms (cabinet_id, planogram_key)
                                    VALUES (?, ?)
                                ''', (cabinet['id'], planogram_key))
                                
                                planogram_id = cursor.lastrowid
                                
                                # Insert slots
                                for slot_position, slot_data in planogram_data.items():
                                    if slot_data and slot_data.get('productId'):
                                        cursor.execute('''
                                            INSERT INTO planogram_slots 
                                            (planogram_id, slot_position, product_id, product_name, 
                                             quantity, capacity, par_level, price)
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                        ''', (
                                            planogram_id,
                                            slot_position,
                                            slot_data.get('productId'),
                                            slot_data.get('productName'),
                                            slot_data.get('quantity', 0),
                                            slot_data.get('capacity', 0),
                                            slot_data.get('parLevel', 0),
                                            slot_data.get('price')
                                        ))
                                
                                migrated_planograms += 1
                                
            except Exception as e:
                errors.append(f"Error migrating planogram {planogram_key}: {str(e)}")
        
        db.commit()
        
        return jsonify({
            'success': True,
            'migratedDevices': migrated_devices,
            'migratedPlanograms': migrated_planograms,
            'errors': errors
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e), 'errors': errors}), 500

# Product Management Endpoints

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with optional category filtering"""
    db = get_db()
    cursor = db.cursor()
    
    # Get category filter if provided
    category = request.args.get('category')
    
    if category and category != 'all':
        products = cursor.execute('''
            SELECT id, name, category, price, image, created_at
            FROM products
            WHERE category = ? 
              AND id != 1 
              AND (is_system IS NULL OR is_system = FALSE)
            ORDER BY name
        ''', (category,)).fetchall()
    else:
        products = cursor.execute('''
            SELECT id, name, category, price, image, created_at
            FROM products
            WHERE id != 1 
              AND (is_system IS NULL OR is_system = FALSE)
            ORDER BY name
        ''').fetchall()
    
    return jsonify([dict_from_row(product) for product in products])

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID"""
    db = get_db()
    cursor = db.cursor()
    
    product = cursor.execute('''
        SELECT id, name, category, price, image, created_at
        FROM products
        WHERE id = ?
    ''', (product_id,)).fetchone()
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify(dict_from_row(product))

@app.route('/api/products/categories', methods=['GET'])
def get_product_categories():
    """Get all distinct product categories"""
    db = get_db()
    cursor = db.cursor()
    
    categories = cursor.execute('''
        SELECT DISTINCT category
        FROM products
        ORDER BY category
    ''').fetchall()
    
    return jsonify([row[0] for row in categories])

@app.route('/api/products', methods=['POST'])
def create_product():
    """Create a new product"""
    data = request.json
    
    # Validate required fields
    if not data or 'name' not in data or 'category' not in data or 'price' not in data:
        return jsonify({'error': 'Name, category, and price are required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO products (name, category, price, image)
            VALUES (?, ?, ?, ?)
        ''', (
            data['name'],
            data['category'],
            data['price'],
            data.get('image')
        ))
        
        db.commit()
        
        product_id = cursor.lastrowid
        product = cursor.execute('''
            SELECT id, name, category, price, image, created_at
            FROM products
            WHERE id = ?
        ''', (product_id,)).fetchone()
        
        return jsonify(dict_from_row(product)), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product"""
    data = request.json
    
    if not data or 'name' not in data or 'category' not in data or 'price' not in data:
        return jsonify({'error': 'Name, category, and price are required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if product exists
        existing = cursor.execute('SELECT id FROM products WHERE id = ?', (product_id,)).fetchone()
        if not existing:
            return jsonify({'error': 'Product not found'}), 404
        
        cursor.execute('''
            UPDATE products 
            SET name = ?, category = ?, price = ?, image = ?
            WHERE id = ?
        ''', (
            data['name'],
            data['category'],
            data['price'],
            data.get('image'),
            product_id
        ))
        
        db.commit()
        
        product = cursor.execute('''
            SELECT id, name, category, price, image, created_at
            FROM products
            WHERE id = ?
        ''', (product_id,)).fetchone()
        
        return jsonify(dict_from_row(product))
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if product exists
        existing = cursor.execute('SELECT name FROM products WHERE id = ?', (product_id,)).fetchone()
        if not existing:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if product is used in any planograms
        slot_count = cursor.execute('SELECT COUNT(*) FROM planogram_slots WHERE product_id = ?', (product_id,)).fetchone()[0]
        if slot_count > 0:
            return jsonify({'error': f'Cannot delete product. It is used in {slot_count} planogram slot(s)'}), 400
        
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        db.commit()
        
        return jsonify({'message': f'Product "{existing[0]}" deleted successfully'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

# Device Type Management Endpoints

@app.route('/api/device-types', methods=['GET'])
def get_device_types():
    """Get all device types"""
    db = get_db()
    cursor = db.cursor()
    
    device_types = cursor.execute('''
        SELECT id, name, description, allows_additional_cabinets
        FROM device_types
        ORDER BY name
    ''').fetchall()
    
    # Convert to camelCase for frontend consistency
    result = []
    for dt in device_types:
        dt_dict = dict_from_row(dt)
        result.append({
            'id': dt_dict['id'],
            'name': dt_dict['name'],
            'description': dt_dict['description'],
            'allowsAdditionalCabinets': bool(dt_dict['allows_additional_cabinets'])
        })
    
    return jsonify(result)

@app.route('/api/device-types', methods=['POST'])
def create_device_type():
    """Create a new device type"""
    data = request.json
    
    # Validate required fields
    if not data or 'name' not in data or 'description' not in data:
        return jsonify({'error': 'Name and description are required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO device_types (name, description, allows_additional_cabinets)
            VALUES (?, ?, ?)
        ''', (
            data['name'],
            data['description'],
            data.get('allowsAdditionalCabinets', False)
        ))
        
        db.commit()
        
        # Return the created device type
        device_type_id = cursor.lastrowid
        device_type = cursor.execute('''
            SELECT id, name, description, allows_additional_cabinets
            FROM device_types
            WHERE id = ?
        ''', (device_type_id,)).fetchone()
        
        return jsonify({
            'id': device_type['id'],
            'name': device_type['name'],
            'description': device_type['description'],
            'allowsAdditionalCabinets': bool(device_type['allows_additional_cabinets'])
        }), 201
        
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': 'Device type with this name already exists'}), 400
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Location Management Endpoints

@app.route('/api/geocode', methods=['POST'])
def geocode_address_endpoint():
    """Geocode an address to get latitude and longitude"""
    data = request.json
    
    if not data or 'address' not in data:
        return jsonify({'error': 'Address is required'}), 400
    
    try:
        latitude, longitude = geocode_address(data['address'])
        
        if latitude is None or longitude is None:
            return jsonify({'error': 'Failed to geocode address'}), 400
            
        return jsonify({
            'address': data['address'],
            'latitude': latitude,
            'longitude': longitude
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Get all locations"""
    db = get_db()
    cursor = db.cursor()
    
    locations = cursor.execute('''
        SELECT id, name, address, latitude, longitude, created_at, updated_at
        FROM locations
        ORDER BY name
    ''').fetchall()
    
    return jsonify([dict_from_row(location) for location in locations])

@app.route('/api/locations', methods=['POST'])
def create_location():
    """Create a new location"""
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Geocode address if provided
        address = data.get('address')
        latitude, longitude = None, None
        
        if address:
            latitude, longitude = geocode_address(address)
        
        cursor.execute('''
            INSERT INTO locations (name, address, latitude, longitude)
            VALUES (?, ?, ?, ?)
        ''', (data['name'], address, latitude, longitude))
        
        db.commit()
        
        location_id = cursor.lastrowid
        location = cursor.execute('''
            SELECT id, name, address, latitude, longitude, created_at, updated_at
            FROM locations
            WHERE id = ?
        ''', (location_id,)).fetchone()
        
        return jsonify(dict_from_row(location)), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/locations/<int:location_id>', methods=['PUT'])
def update_location(location_id):
    """Update a location"""
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if location exists and get current address
        existing = cursor.execute('SELECT id, address FROM locations WHERE id = ?', (location_id,)).fetchone()
        if not existing:
            return jsonify({'error': 'Location not found'}), 404
        
        # Get new address
        address = data.get('address')
        latitude, longitude = None, None
        
        # Only geocode if address changed
        if address and address != existing['address']:
            latitude, longitude = geocode_address(address)
            cursor.execute('''
                UPDATE locations 
                SET name = ?, address = ?, latitude = ?, longitude = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (data['name'], address, latitude, longitude, location_id))
        else:
            # Keep existing coordinates if address unchanged
            cursor.execute('''
                UPDATE locations 
                SET name = ?, address = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (data['name'], address, location_id))
        
        db.commit()
        
        location = cursor.execute('''
            SELECT id, name, address, latitude, longitude, created_at, updated_at
            FROM locations
            WHERE id = ?
        ''', (location_id,)).fetchone()
        
        return jsonify(dict_from_row(location))
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/locations/<int:location_id>', methods=['DELETE'])
def delete_location(location_id):
    """Delete a location"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if location exists
        existing = cursor.execute('SELECT name FROM locations WHERE id = ?', (location_id,)).fetchone()
        if not existing:
            return jsonify({'error': 'Location not found'}), 404
        
        # Check if location is used by any devices
        device_count = cursor.execute('SELECT COUNT(*) FROM devices WHERE location_id = ?', (location_id,)).fetchone()[0]
        if device_count > 0:
            return jsonify({'error': f'Cannot delete location. It is used by {device_count} device(s)'}), 400
        
        cursor.execute('DELETE FROM locations WHERE id = ?', (location_id,))
        db.commit()
        
        return jsonify({'message': f'Location "{existing[0]}" deleted successfully'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

# Service Order Sync Endpoints

@app.route('/api/service-orders/<int:order_id>/sync', methods=['PUT'])
@auth_manager.require_auth
def sync_service_order(order_id):
    """Sync service order with conflict detection"""
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    # Verify driver has access to this order
    if g.user.get('role') == 'driver':
        order = cursor.execute('''
            SELECT * FROM service_orders 
            WHERE id = ? AND driver_id = ?
        ''', (order_id, g.user['id'])).fetchone()
        
        if not order:
            return jsonify({'error': 'Order not found or access denied'}), 404
    else:
        order = cursor.execute('''
            SELECT * FROM service_orders WHERE id = ?
        ''', (order_id,)).fetchone()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
    
    # Check for conflicts
    client_last_modified = data.get('lastModified')
    server_last_modified = order['last_modified']
    
    if client_last_modified and server_last_modified:
        # Convert to comparable format
        try:
            client_time = datetime.fromisoformat(client_last_modified.replace('Z', '+00:00'))
            server_time = datetime.fromisoformat(server_last_modified)
            
            if server_time > client_time:
                # Conflict detected - server has newer version
                return jsonify({
                    'conflict': True,
                    'serverVersion': dict(order),
                    'message': 'Server has newer version of this order'
                }), 409
        except Exception as e:
            print(f"Error comparing timestamps: {e}")
    
    # Apply updates
    allowed_fields = ['status', 'notes', 'completed_at', 'started_at']
    update_fields = []
    params = []
    
    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field} = ?")
            params.append(data[field])
    
    if not update_fields:
        return jsonify({'error': 'No valid fields to update'}), 400
    
    # Update sync version and last_modified
    update_fields.append("sync_version = sync_version + 1")
    update_fields.append("last_modified = datetime('now')")
    
    params.append(order_id)
    
    try:
        query = f"UPDATE service_orders SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        
        # Log the sync
        log_audit_event(g.user['id'], 'ORDER_SYNC', 'service_order', order_id, 
                       f"Synced order with status: {data.get('status', 'unknown')}")
        
        db.commit()
        
        # Return updated order
        updated_order = cursor.execute('''
            SELECT * FROM service_orders WHERE id = ?
        ''', (order_id,)).fetchone()
        
        return jsonify({
            'success': True,
            'order': dict(updated_order)
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/service-orders/execute', methods=['POST'])
@auth_manager.require_auth
def execute_service_order():
    """Execute service order delivery"""
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    required = ['orderId', 'cabinetId', 'deliveredItems']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    order_id = data['orderId']
    cabinet_id = data['cabinetId']
    delivered_items = data['deliveredItems']
    
    # Verify driver access
    if g.user.get('role') == 'driver':
        order = cursor.execute('''
            SELECT so.* FROM service_orders so
            JOIN service_order_cabinets soc ON so.id = soc.service_order_id
            WHERE so.id = ? AND so.driver_id = ? AND soc.id = ?
        ''', (order_id, g.user['id'], cabinet_id)).fetchone()
        
        if not order:
            return jsonify({'error': 'Order not found or access denied'}), 404
    
    try:
        # Record delivery details
        for item in delivered_items:
            cursor.execute('''
                UPDATE service_order_cabinet_items 
                SET quantity_filled = ?
                WHERE service_order_cabinet_id = ? AND product_id = ?
            ''', (item['quantity'], cabinet_id, item['productId']))
        
        # Update cabinet status
        cursor.execute('''
            UPDATE service_order_cabinets 
            SET status = 'completed',
                completed_at = datetime('now'),
                last_modified = datetime('now')
            WHERE id = ?
        ''', (cabinet_id,))
        
        # Check if all cabinets are completed
        pending_cabinets = cursor.execute('''
            SELECT COUNT(*) FROM service_order_cabinets
            WHERE service_order_id = ? AND status != 'completed'
        ''', (order_id,)).fetchone()[0]
        
        if pending_cabinets == 0:
            # All cabinets completed, update order status
            cursor.execute('''
                UPDATE service_orders 
                SET status = 'completed',
                    completed_at = datetime('now')
                WHERE id = ?
            ''', (order_id,))
        
        # Create service visit record
        cursor.execute('''
            INSERT INTO service_visits 
            (device_id, route_id, service_date, units_restocked, 
             service_type, technician_id, notes, service_order_cabinet_id)
            SELECT cc.device_id, so.route_id, datetime('now'),
                   SUM(soci.quantity_filled), 'routine', ?, ?, ?
            FROM service_order_cabinets soc
            JOIN cabinet_configurations cc ON soc.cabinet_configuration_id = cc.id
            JOIN service_orders so ON soc.service_order_id = so.id
            LEFT JOIN service_order_cabinet_items soci ON soc.id = soci.service_order_cabinet_id
            WHERE soc.id = ?
            GROUP BY cc.device_id, so.route_id
        ''', (g.user['id'], data.get('notes', ''), cabinet_id, cabinet_id))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Delivery recorded successfully',
            'allCabinetsCompleted': pending_cabinets == 0
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/service-orders/photos', methods=['POST'])
@auth_manager.require_auth
def upload_service_order_photo():
    """Upload photo for service order"""
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo provided'}), 400
    
    photo = request.files['photo']
    order_id = request.form.get('orderId')
    photo_type = request.form.get('type', 'delivery_proof')
    timestamp = request.form.get('timestamp')
    
    if not order_id:
        return jsonify({'error': 'Order ID required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Verify driver access
    if g.user.get('role') == 'driver':
        order = cursor.execute('''
            SELECT * FROM service_orders 
            WHERE id = ? AND driver_id = ?
        ''', (order_id, g.user['id'])).fetchone()
        
        if not order:
            return jsonify({'error': 'Order not found or access denied'}), 404
    
    # Create photos directory if it doesn't exist
    photos_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'service_photos')
    os.makedirs(photos_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(photo.filename)[1] or '.jpg'
    filename = f"order_{order_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}{file_ext}"
    filepath = os.path.join(photos_dir, filename)
    
    try:
        # Save photo
        photo.save(filepath)
        
        # Create database record
        cursor.execute('''
            INSERT INTO service_order_photos 
            (service_order_id, filename, photo_type, uploaded_by, capture_timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (order_id, filename, photo_type, g.user['id'], timestamp))
        
        photo_id = cursor.lastrowid
        db.commit()
        
        return jsonify({
            'success': True,
            'photoId': photo_id,
            'filename': filename
        })
        
    except Exception as e:
        # Clean up file if database operation failed
        if os.path.exists(filepath):
            os.remove(filepath)
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/service-orders/<int:order_id>/photos', methods=['GET'])
@auth_manager.require_auth
def get_service_order_photos(order_id):
    """Get photos for a service order"""
    db = get_db()
    cursor = db.cursor()
    
    # Verify access
    if g.user.get('role') == 'driver':
        order = cursor.execute('''
            SELECT * FROM service_orders 
            WHERE id = ? AND driver_id = ?
        ''', (order_id, g.user['id'])).fetchone()
        
        if not order:
            return jsonify({'error': 'Order not found or access denied'}), 404
    
    photos = cursor.execute('''
        SELECT p.*, u.username as uploaded_by_name
        FROM service_order_photos p
        JOIN users u ON p.uploaded_by = u.id
        WHERE p.service_order_id = ?
        ORDER BY p.uploaded_at DESC
    ''', (order_id,)).fetchall()
    
    return jsonify({
        'photos': [dict(photo) for photo in photos]
    })

# Route Management Endpoints

@app.route('/api/routes', methods=['GET'])
def get_routes():
    """Get all routes"""
    db = get_db()
    cursor = db.cursor()
    
    routes = cursor.execute('''
        SELECT r.id, r.name, r.route_number, r.created_at, r.updated_at, r.driver_id,
               u.username as driver_name, u.email as driver_email
        FROM routes r
        LEFT JOIN users u ON r.driver_id = u.id AND u.role = 'driver'
        ORDER BY r.route_number, r.name
    ''').fetchall()
    
    return jsonify([dict_from_row(route) for route in routes])

@app.route('/api/routes', methods=['POST'])
def create_route():
    """Create a new route"""
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO routes (name, route_number, driver_id)
            VALUES (?, ?, ?)
        ''', (data['name'], data.get('routeNumber'), data.get('driverId')))
        
        db.commit()
        
        route_id = cursor.lastrowid
        route = cursor.execute('''
            SELECT r.id, r.name, r.route_number, r.created_at, r.updated_at, r.driver_id,
                   u.username as driver_name, u.email as driver_email
            FROM routes r
            LEFT JOIN users u ON r.driver_id = u.id AND u.role = 'driver'
            WHERE r.id = ?
        ''', (route_id,)).fetchone()
        
        return jsonify(dict_from_row(route)), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/routes/<int:route_id>', methods=['PUT'])
def update_route(route_id):
    """Update a route"""
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if route exists
        existing = cursor.execute('SELECT id FROM routes WHERE id = ?', (route_id,)).fetchone()
        if not existing:
            return jsonify({'error': 'Route not found'}), 404
        
        cursor.execute('''
            UPDATE routes 
            SET name = ?, route_number = ?, driver_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (data['name'], data.get('routeNumber'), data.get('driverId'), route_id))
        
        db.commit()
        
        route = cursor.execute('''
            SELECT r.id, r.name, r.route_number, r.created_at, r.updated_at, r.driver_id,
                   u.username as driver_name, u.email as driver_email
            FROM routes r
            LEFT JOIN users u ON r.driver_id = u.id AND u.role = 'driver'
            WHERE r.id = ?
        ''', (route_id,)).fetchone()
        
        return jsonify(dict_from_row(route))
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/routes/<int:route_id>', methods=['DELETE'])
def delete_route(route_id):
    """Delete a route"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if route exists
        existing = cursor.execute('SELECT name FROM routes WHERE id = ?', (route_id,)).fetchone()
        if not existing:
            return jsonify({'error': 'Route not found'}), 404
        
        cursor.execute('DELETE FROM routes WHERE id = ?', (route_id,))
        db.commit()
        
        return jsonify({'message': f'Route "{existing[0]}" deleted successfully'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/routes/<int:route_id>/devices', methods=['GET'])
def get_route_devices(route_id):
    """Get all devices assigned to a specific route with their configurations and metrics"""
    db = get_db()
    cursor = db.cursor()
    
    # First check if route exists
    route = cursor.execute('SELECT name FROM routes WHERE id = ?', (route_id,)).fetchone()
    if not route:
        return jsonify({'error': 'Route not found'}), 404
    
    # Get all devices assigned to this route
    devices = cursor.execute('''
        SELECT 
            d.id, d.asset, d.cooler, d.location_id, d.model, 
            d.device_type_id, d.created_at, d.updated_at,
            dt.name as device_type_name, 
            dt.description as device_type_description,
            dt.allows_additional_cabinets,
            l.name as location,
            l.address as location_address,
            l.latitude as location_latitude,
            l.longitude as location_longitude,
            d.route_id
        FROM devices d
        JOIN device_types dt ON d.device_type_id = dt.id
        LEFT JOIN locations l ON d.location_id = l.id
        WHERE d.route_id = ? AND d.deleted_at IS NULL
        ORDER BY l.name, d.asset
    ''', (route_id,)).fetchall()
    
    result = []
    for device in devices:
        device_dict = dict_from_row(device)
        
        # Get cabinet configurations for this device
        cabinets = cursor.execute('''
            SELECT 
                cc.id, cc.model_name, cc.is_parent, cc.cabinet_index, cc.rows, cc.columns,
                ct.name as cabinet_type, ct.description, ct.icon
            FROM cabinet_configurations cc
            JOIN cabinet_types ct ON cc.cabinet_type_id = ct.id
            WHERE cc.device_id = ?
            ORDER BY cc.is_parent DESC, cc.cabinet_index
        ''', (device['id'],)).fetchall()
        
        # Convert to camelCase for frontend consistency
        cabinet_configs = []
        for cab in cabinets:
            cab_dict = dict_from_row(cab)
            cabinet_configs.append({
                'id': cab_dict['id'],
                'cabinetType': cab_dict['cabinet_type'],
                'modelName': cab_dict['model_name'],
                'isParent': bool(cab_dict['is_parent']),
                'cabinetIndex': cab_dict['cabinet_index'],
                'rows': cab_dict['rows'],
                'columns': cab_dict['columns']
            })
        
        # Get device metrics (check if cached and recent)
        metrics = cursor.execute('''
            SELECT sold_out_count, days_remaining_inventory, data_collection_rate,
                   product_level_percent, units_to_par, last_calculated
            FROM device_metrics
            WHERE device_id = ? 
            AND datetime(last_calculated) > datetime('now', '-15 minutes')
        ''', (device['id'],)).fetchone()
        
        # If no recent metrics, calculate them
        if not metrics:
            calculated_metrics = RouteMetricsService.calculate_device_metrics(device['id'])
            if calculated_metrics:
                metrics_dict = calculated_metrics
            else:
                # Fallback to placeholder values if calculation fails
                metrics_dict = {
                    'soldOutCount': 0,
                    'daysRemainingInventory': 999,
                    'dataCollectionRate': 100.0,
                    'productLevelPercent': 100.0,
                    'unitsToPar': 0
                }
        else:
            metrics_dict = {
                'soldOutCount': metrics['sold_out_count'],
                'daysRemainingInventory': metrics['days_remaining_inventory'],
                'dataCollectionRate': metrics['data_collection_rate'],
                'productLevelPercent': metrics['product_level_percent'],
                'unitsToPar': metrics['units_to_par']
            }
        
        # Get days since last service
        last_service = cursor.execute('''
            SELECT service_date FROM service_visits
            WHERE device_id = ?
            ORDER BY service_date DESC
            LIMIT 1
        ''', (device['id'],)).fetchone()
        
        if last_service:
            days_since_service = cursor.execute('''
                SELECT julianday('now') - julianday(?)
            ''', (last_service['service_date'],)).fetchone()[0]
            metrics_dict['daysSinceService'] = round(days_since_service, 1)
        else:
            metrics_dict['daysSinceService'] = None
        
        # Get cabinet-level slot metrics for accordion view
        cabinet_metrics = cursor.execute('''
            SELECT 
                cc.id as cabinet_id,
                cc.cabinet_index,
                cc.is_parent,
                ct.name as cabinet_type,
                cc.model_name,
                sm.is_sold_out,
                sm.days_remaining_inventory,
                sm.product_level_percent,
                sm.daily_velocity,
                ps.capacity,
                ps.quantity
            FROM cabinet_configurations cc
            JOIN cabinet_types ct ON cc.cabinet_type_id = ct.id
            LEFT JOIN planograms p ON cc.id = p.cabinet_id
            LEFT JOIN planogram_slots ps ON p.id = ps.planogram_id
            LEFT JOIN slot_metrics sm ON ps.id = sm.planogram_slot_id
            WHERE cc.device_id = ?
            AND (ps.product_id != 1 OR ps.product_id IS NULL)  -- Exclude empty slot sentinel
            ORDER BY cc.cabinet_index
        ''', (device['id'],)).fetchall()
        
        # Process cabinet metrics
        device_cabinets = []
        device_level_metrics = {
            'soldOutCount': 0,
            'daysRemainingInventory': 999,
            'dailyConsumptionRate': 0.0,
            'productLevelPercent': 0.0,
            'unitsToPick': 0,
            'totalSlots': 0
        }
        
        # Group metrics by cabinet
        cabinet_data = {}
        for row in cabinet_metrics:
            row_dict = dict_from_row(row)
            cabinet_id = row_dict['cabinet_id']
            
            if cabinet_id not in cabinet_data:
                cabinet_data[cabinet_id] = {
                    'cabinetId': cabinet_id,
                    'cabinetIndex': row_dict['cabinet_index'],
                    'isParent': bool(row_dict['is_parent']),
                    'cabinetType': row_dict['cabinet_type'],
                    'modelName': row_dict['model_name'],
                    'slots': []
                }
            
            # Add slot data if it exists
            if row_dict['is_sold_out'] is not None:
                cabinet_data[cabinet_id]['slots'].append({
                    'is_sold_out': row_dict['is_sold_out'],
                    'days_remaining_inventory': row_dict['days_remaining_inventory'],
                    'product_level_percent': row_dict['product_level_percent'],
                    'daily_velocity': row_dict['daily_velocity'],
                    'capacity': row_dict['capacity'],
                    'quantity': row_dict['quantity']
                })
        
        # Calculate metrics for each cabinet
        for cabinet_id, cabinet in cabinet_data.items():
            slots = cabinet['slots']
            
            if slots:
                # Calculate cabinet-level metrics
                sold_out_count = sum(1 for slot in slots if slot['is_sold_out'])
                # DRI: MIN of all slots, excluding zero velocity slots AND sold out slots
                dri_values = [slot['days_remaining_inventory'] for slot in slots 
                             if slot['daily_velocity'] > 0 and slot['days_remaining_inventory'] > 0]
                min_dri = min(dri_values, default=999)
                # DCR: SUM of all daily_velocity values in cabinet
                sum_daily_velocity = sum(slot['daily_velocity'] for slot in slots)
                avg_product_level = sum(slot['product_level_percent'] for slot in slots) / len(slots)
                
                # Calculate units to reach capacity
                units_to_capacity = 0
                for slot in slots:
                    if slot['capacity'] > 0:
                        current_fill_rate = slot['product_level_percent'] / 100.0
                        current_quantity = int(slot['capacity'] * current_fill_rate)
                        units_to_capacity += max(0, slot['capacity'] - current_quantity)
                
                cabinet['metrics'] = {
                    'soldOutCount': sold_out_count,
                    'daysRemainingInventory': min_dri,
                    'dailyConsumptionRate': round(sum_daily_velocity, 2),
                    'productLevelPercent': round(avg_product_level, 1),
                    'unitsToPick': units_to_capacity,
                    'totalSlots': len(slots)
                }
                
                # Aggregate to device level
                device_level_metrics['soldOutCount'] += sold_out_count
                device_level_metrics['dailyConsumptionRate'] += sum_daily_velocity
                device_level_metrics['productLevelPercent'] += avg_product_level
                device_level_metrics['unitsToPick'] += units_to_capacity
                device_level_metrics['totalSlots'] += len(slots)
                
                if min_dri < device_level_metrics['daysRemainingInventory']:
                    device_level_metrics['daysRemainingInventory'] = min_dri
                    
            else:
                # No slots for this cabinet
                cabinet['metrics'] = {
                    'soldOutCount': 0,
                    'daysRemainingInventory': 999,
                    'dailyConsumptionRate': 0.0,
                    'productLevelPercent': 0.0,
                    'unitsToPick': 0,
                    'totalSlots': 0
                }
            
            # Remove raw slots data
            del cabinet['slots']
            device_cabinets.append(cabinet)
        
        # Finalize device-level metrics
        cabinet_count = len(device_cabinets)
        if cabinet_count > 0 and device_level_metrics['totalSlots'] > 0:
            # DCR should be sum of all cabinet DCRs, not averaged
            device_level_metrics['dailyConsumptionRate'] = round(device_level_metrics['dailyConsumptionRate'], 2)
            device_level_metrics['productLevelPercent'] = round(device_level_metrics['productLevelPercent'] / cabinet_count, 1)
        
        # Add both cabinet and device level metrics to response
        device_dict['cabinets'] = device_cabinets
        device_dict['slotMetrics'] = device_level_metrics
        
        # Build device response
        device_dict['cabinetConfiguration'] = cabinet_configs
        device_dict['metrics'] = metrics_dict
        device_dict['deviceTypeDetails'] = {
            'id': device_dict['device_type_id'],
            'name': device_dict['device_type_name'],
            'description': device_dict['device_type_description'],
            'allowsAdditionalCabinets': bool(device_dict['allows_additional_cabinets'])
        }
        device_dict['locationAddress'] = device_dict.get('location_address')
        device_dict['locationLatitude'] = device_dict.get('location_latitude')
        device_dict['locationLongitude'] = device_dict.get('location_longitude')
        
        # Remove raw fields
        del device_dict['device_type_name']
        del device_dict['device_type_description']
        del device_dict['allows_additional_cabinets']
        del device_dict['route_id']
        if 'location_address' in device_dict:
            del device_dict['location_address']
        if 'location_latitude' in device_dict:
            del device_dict['location_latitude']
        if 'location_longitude' in device_dict:
            del device_dict['location_longitude']
        
        result.append(device_dict)
    
    return jsonify({
        'routeId': route_id,
        'routeName': route[0],
        'devices': result
    })

@app.route('/api/routes/<int:route_id>/assign-device', methods=['POST'])
def assign_device_to_route(route_id):
    """Assign a device to a route"""
    data = request.json
    
    if not data or 'deviceId' not in data:
        return jsonify({'error': 'Device ID is required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if route exists
        route = cursor.execute('SELECT id FROM routes WHERE id = ?', (route_id,)).fetchone()
        if not route:
            return jsonify({'error': 'Route not found'}), 404
        
        # Check if device exists
        device = cursor.execute('SELECT id FROM devices WHERE id = ? AND deleted_at IS NULL', 
                              (data['deviceId'],)).fetchone()
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        # Check if already assigned
        existing = cursor.execute('''
            SELECT route_id FROM devices 
            WHERE id = ? AND route_id = ?
        ''', (data['deviceId'], route_id)).fetchone()
        
        if existing:
            return jsonify({'error': 'Device already assigned to this route'}), 400
        
        # Assign device to route by updating the device's route_id
        cursor.execute('''
            UPDATE devices SET route_id = ? WHERE id = ?
        ''', (route_id, data['deviceId']))
        
        db.commit()
        
        return jsonify({'message': 'Device assigned to route successfully'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/routes/<int:route_id>/remove-device', methods=['DELETE'])
def remove_device_from_route(route_id):
    """Remove a device from a route"""
    device_id = request.args.get('deviceId')
    
    if not device_id:
        return jsonify({'error': 'Device ID is required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Clear route_id in devices table
        cursor.execute('''
            UPDATE devices SET route_id = NULL 
            WHERE id = ? AND route_id = ?
        ''', (device_id, route_id))
        
        affected_rows = cursor.rowcount
        db.commit()
        
        if affected_rows == 0:
            return jsonify({'error': 'Device not found on this route'}), 404
        
        return jsonify({'message': 'Device removed from route successfully'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

# Driver Management Endpoints

@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    """Get all users with driver role"""
    db = get_db()
    cursor = db.cursor()
    
    drivers = cursor.execute('''
        SELECT id, username, email, created_at, is_active
        FROM users
        WHERE role = 'driver'
        ORDER BY username
    ''').fetchall()
    
    return jsonify([dict_from_row(driver) for driver in drivers])

# Cabinet Type Management Endpoints

@app.route('/api/cabinet-types', methods=['GET'])
def get_cabinet_types():
    """Get all cabinet types"""
    db = get_db()
    cursor = db.cursor()
    
    cabinet_types = cursor.execute('''
        SELECT id, name, description, rows, cols, icon
        FROM cabinet_types
        ORDER BY name
    ''').fetchall()
    
    # Convert to camelCase for frontend consistency
    result = []
    for ct in cabinet_types:
        ct_dict = dict_from_row(ct)
        result.append({
            'id': ct_dict['id'],
            'name': ct_dict['name'],
            'description': ct_dict['description'],
            'rows': ct_dict['rows'],
            'cols': ct_dict['cols'],
            'icon': ct_dict['icon']
        })
    
    return jsonify(result)

@app.route('/api/cabinet-types', methods=['POST'])
def create_cabinet_type():
    """Create a new cabinet type"""
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'description', 'rows', 'cols', 'icon']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Name, description, rows, cols, and icon are required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO cabinet_types (name, description, rows, cols, icon)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['description'],
            data['rows'],
            data['cols'],
            data['icon']
        ))
        
        db.commit()
        
        # Return the created cabinet type
        cabinet_type_id = cursor.lastrowid
        cabinet_type = cursor.execute('''
            SELECT id, name, description, rows, cols, icon
            FROM cabinet_types
            WHERE id = ?
        ''', (cabinet_type_id,)).fetchone()
        
        return jsonify({
            'id': cabinet_type['id'],
            'name': cabinet_type['name'],
            'description': cabinet_type['description'],
            'rows': cabinet_type['rows'],
            'cols': cabinet_type['cols'],
            'icon': cabinet_type['icon']
        }), 201
        
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': 'Cabinet type with this name already exists'}), 400
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'database': DATABASE})

@app.route('/api/query', methods=['POST'])
def execute_query():
    """Execute a read-only SQL query (SELECT only)"""
    query = request.json.get('query', '').strip()
    
    # Safety check - only allow SELECT queries
    if not query.upper().startswith('SELECT'):
        return jsonify({'error': 'Only SELECT queries are allowed'}), 400
    
    # Additional safety checks
    forbidden_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']
    query_upper = query.upper()
    for keyword in forbidden_keywords:
        if keyword in query_upper:
            return jsonify({'error': f'Query contains forbidden keyword: {keyword}'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute(query)
        columns = [description[0] for description in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        
        # Convert rows to list of dicts
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        
        return jsonify({
            'columns': columns,
            'rows': result,
            'count': len(result)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Admin Recovery Endpoints
# TODO: Add authentication for these admin-only endpoints

@app.route('/api/admin/devices/deleted', methods=['GET'])
def get_deleted_devices():
    """Get all soft-deleted devices"""
    db = get_db()
    cursor = db.cursor()
    
    devices = cursor.execute('''
        SELECT 
            d.id, d.asset, d.cooler, d.location_id, d.model, 
            d.device_type_id, d.deleted_at, d.deleted_by,
            dt.name as device_type_name,
            l.name as location
        FROM devices d
        JOIN device_types dt ON d.device_type_id = dt.id
        LEFT JOIN locations l ON d.location_id = l.id
        WHERE d.deleted_at IS NOT NULL
        ORDER BY d.deleted_at DESC
    ''').fetchall()
    
    result = []
    for device in devices:
        device_dict = dict_from_row(device)
        result.append(device_dict)
    
    return jsonify(result)

@app.route('/api/admin/devices/<int:device_id>/recover', methods=['POST'])
def recover_device(device_id):
    """Recover a soft-deleted device"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if device exists and is deleted
        device = cursor.execute(
            'SELECT id, deleted_at FROM devices WHERE id = ? AND deleted_at IS NOT NULL', 
            (device_id,)
        ).fetchone()
        
        if not device:
            return jsonify({'error': 'Deleted device not found'}), 404
        
        # Recover by clearing deleted_at
        cursor.execute(
            'UPDATE devices SET deleted_at = NULL, deleted_by = NULL WHERE id = ?',
            (device_id,)
        )
        
        db.commit()
        
        # Return recovered device
        recovered = cursor.execute('''
            SELECT 
                d.id, d.asset, d.cooler, d.location_id, d.model, 
                d.device_type_id, d.created_at, d.updated_at,
                dt.name as device_type_name,
                l.name as location
            FROM devices d
            JOIN device_types dt ON d.device_type_id = dt.id
            LEFT JOIN locations l ON d.location_id = l.id
            WHERE d.id = ?
        ''', (device_id,)).fetchone()
        
        return jsonify(dict_from_row(recovered))
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/planograms/<planogram_key>/cleared-slots', methods=['GET'])
def get_cleared_slots(planogram_key):
    """Get cleared slots for a planogram"""
    db = get_db()
    cursor = db.cursor()
    
    # Find planogram
    planogram = cursor.execute(
        'SELECT id FROM planograms WHERE planogram_key = ?',
        (planogram_key,)
    ).fetchone()
    
    if not planogram:
        return jsonify({'error': 'Planogram not found'}), 404
    
    # Get cleared slots
    cleared_slots = cursor.execute('''
        SELECT 
            ps.slot_position,
            ps.cleared_at,
            ps.cleared_by,
            ps.previous_product_id,
            p.product_name as previous_product_name
        FROM planogram_slots ps
        LEFT JOIN products p ON ps.previous_product_id = p.id
        WHERE ps.planogram_id = ? AND ps.cleared_at IS NOT NULL
        ORDER BY ps.cleared_at DESC
    ''', (planogram['id'],)).fetchall()
    
    result = []
    for slot in cleared_slots:
        slot_dict = dict_from_row(slot)
        result.append(slot_dict)
    
    return jsonify({
        'planogram_key': planogram_key,
        'cleared_slots': result
    })

# Sales API endpoints
@app.route('/api/sales', methods=['GET'])
def get_sales():
    """Get sales data with optional filtering"""
    db = get_db()
    cursor = db.cursor()
    
    # Get query parameters
    device_id = request.args.get('device_id')
    product_id = request.args.get('product_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    query = '''
        SELECT 
            s.id,
            s.device_id,
            d.asset as device_asset,
            d.cooler as device_cooler,
            s.product_id,
            p.name as product_name,
            p.category as product_category,
            s.sale_units,
            s.sale_cash,
            s.created_at,
            s.updated_at
        FROM sales s
        JOIN devices d ON s.device_id = d.id
        JOIN products p ON s.product_id = p.id
        WHERE 1=1
    '''
    params = []
    
    if device_id:
        query += ' AND s.device_id = ?'
        params.append(device_id)
    
    if product_id:
        query += ' AND s.product_id = ?'
        params.append(product_id)
    
    if start_date:
        query += ' AND s.created_at >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND s.created_at <= ?'
        params.append(end_date)
    
    query += ' ORDER BY s.created_at DESC'
    
    sales = cursor.execute(query, params).fetchall()
    
    return jsonify([{
        'id': sale['id'],
        'deviceId': sale['device_id'],
        'deviceAsset': sale['device_asset'],
        'deviceCooler': sale['device_cooler'],
        'productId': sale['product_id'],
        'productName': sale['product_name'],
        'productCategory': sale['product_category'],
        'saleUnits': sale['sale_units'],
        'saleCash': float(sale['sale_cash']),
        'createdAt': sale['created_at'],
        'updatedAt': sale['updated_at']
    } for sale in sales])

@app.route('/api/sales', methods=['POST'])
def create_sale():
    """Create a new sale record"""
    data = request.json
    
    # Validate required fields
    required_fields = ['deviceId', 'productId', 'saleUnits', 'saleCash']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Verify device exists
        device = cursor.execute('SELECT id FROM devices WHERE id = ? AND deleted_at IS NULL', 
                              (data['deviceId'],)).fetchone()
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        # Verify product exists
        product = cursor.execute('SELECT id FROM products WHERE id = ?', 
                               (data['productId'],)).fetchone()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Insert sale
        cursor.execute('''
            INSERT INTO sales (device_id, product_id, sale_units, sale_cash)
            VALUES (?, ?, ?, ?)
        ''', (
            data['deviceId'],
            data['productId'],
            data['saleUnits'],
            data['saleCash']
        ))
        
        sale_id = cursor.lastrowid
        db.commit()
        
        # Fetch the created sale
        sale = cursor.execute('''
            SELECT 
                s.id,
                s.device_id,
                d.asset as device_asset,
                d.cooler as device_cooler,
                s.product_id,
                p.name as product_name,
                p.category as product_category,
                s.sale_units,
                s.sale_cash,
                s.created_at,
                s.updated_at
            FROM sales s
            JOIN devices d ON s.device_id = d.id
            JOIN products p ON s.product_id = p.id
            WHERE s.id = ?
        ''', (sale_id,)).fetchone()
        
        return jsonify({
            'id': sale['id'],
            'deviceId': sale['device_id'],
            'deviceAsset': sale['device_asset'],
            'deviceCooler': sale['device_cooler'],
            'productId': sale['product_id'],
            'productName': sale['product_name'],
            'productCategory': sale['product_category'],
            'saleUnits': sale['sale_units'],
            'saleCash': float(sale['sale_cash']),
            'createdAt': sale['created_at'],
            'updatedAt': sale['updated_at']
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/sales/summary', methods=['GET'])
def get_sales_summary():
    """Get sales summary aggregated by device, product, or time period"""
    db = get_db()
    cursor = db.cursor()
    
    group_by = request.args.get('groupBy', 'device')  # device, product, or date
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    base_query = '''
        FROM sales s
        JOIN devices d ON s.device_id = d.id
        JOIN products p ON s.product_id = p.id
        WHERE 1=1
    '''
    params = []
    
    if start_date:
        base_query += ' AND s.created_at >= ?'
        params.append(start_date)
    
    if end_date:
        base_query += ' AND s.created_at <= ?'
        params.append(end_date)
    
    if group_by == 'device':
        query = f'''
            SELECT 
                d.id as device_id,
                d.asset,
                d.cooler,
                COUNT(DISTINCT s.id) as total_transactions,
                SUM(s.sale_units) as total_units,
                SUM(s.sale_cash) as total_cash
            {base_query}
            GROUP BY d.id, d.asset, d.cooler
            ORDER BY total_cash DESC
        '''
    elif group_by == 'product':
        query = f'''
            SELECT 
                p.id as product_id,
                p.name,
                p.category,
                COUNT(DISTINCT s.id) as total_transactions,
                SUM(s.sale_units) as total_units,
                SUM(s.sale_cash) as total_cash
            {base_query}
            GROUP BY p.id, p.name, p.category
            ORDER BY total_units DESC
        '''
    else:  # group by date
        query = f'''
            SELECT 
                DATE(s.created_at) as sale_date,
                COUNT(DISTINCT s.id) as total_transactions,
                COUNT(DISTINCT s.device_id) as unique_devices,
                COUNT(DISTINCT s.product_id) as unique_products,
                SUM(s.sale_units) as total_units,
                SUM(s.sale_cash) as total_cash
            {base_query}
            GROUP BY DATE(s.created_at)
            ORDER BY sale_date DESC
        '''
    
    results = cursor.execute(query, params).fetchall()
    
    if group_by == 'device':
        return jsonify([{
            'deviceId': row['device_id'],
            'asset': row['asset'],
            'cooler': row['cooler'],
            'totalTransactions': row['total_transactions'],
            'totalUnits': row['total_units'],
            'totalCash': float(row['total_cash'])
        } for row in results])
    elif group_by == 'product':
        return jsonify([{
            'productId': row['product_id'],
            'name': row['name'],
            'category': row['category'],
            'totalTransactions': row['total_transactions'],
            'totalUnits': row['total_units'],
            'totalCash': float(row['total_cash'])
        } for row in results])
    else:
        return jsonify([{
            'date': row['sale_date'],
            'totalTransactions': row['total_transactions'],
            'uniqueDevices': row['unique_devices'],
            'uniqueProducts': row['unique_products'],
            'totalUnits': row['total_units'],
            'totalCash': float(row['total_cash'])
        } for row in results])

@app.route('/api/sales/asset-report', methods=['GET'])
def get_asset_sales_report():
    """Get aggregated sales data by device for asset sales report"""
    db = get_db()
    cursor = db.cursor()
    
    # Get date range parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # If no dates provided, default to current week (Sunday to Saturday)
    if not start_date or not end_date:
        from datetime import datetime, timedelta
        today = datetime.now()
        # Calculate last Sunday
        days_since_sunday = today.weekday() + 1 if today.weekday() != 6 else 0
        start_of_week = today - timedelta(days=days_since_sunday)
        start_date = start_of_week.strftime('%Y-%m-%d')
        end_date = (start_of_week + timedelta(days=6)).strftime('%Y-%m-%d')
    
    # Calculate number of days in range for daily average
    from datetime import datetime
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    days_in_range = (end_dt - start_dt).days + 1
    
    query = '''
        SELECT 
            d.id as device_id,
            d.asset,
            d.cooler,
            l.name as location,
            r.name as route_name,
            r.route_number,
            COUNT(DISTINCT s.id) as total_transactions,
            SUM(s.sale_units) as total_units,
            SUM(s.sale_cash) as total_sales,
            ROUND(SUM(s.sale_cash) / ?, 2) as daily_average
        FROM devices d
        LEFT JOIN sales s ON d.id = s.device_id 
            AND DATE(s.created_at) >= ? 
            AND DATE(s.created_at) <= ?
        LEFT JOIN locations l ON d.location_id = l.id
        LEFT JOIN routes r ON d.route_id = r.id
        WHERE d.deleted_at IS NULL
        GROUP BY d.id, d.asset, d.cooler, l.name, r.name, r.route_number
        ORDER BY d.asset
    '''
    
    results = cursor.execute(query, (days_in_range, start_date, end_date)).fetchall()
    
    return jsonify({
        'startDate': start_date,
        'endDate': end_date,
        'daysInRange': days_in_range,
        'devices': [{
            'deviceId': row['device_id'],
            'asset': row['asset'],
            'cooler': row['cooler'],
            'location': row['location'] or 'Unknown',
            'routeName': row['route_name'] or 'Unassigned',
            'routeNumber': row['route_number'],
            'totalTransactions': row['total_transactions'] or 0,
            'totalUnits': row['total_units'] or 0,
            'totalSales': float(row['total_sales'] or 0),
            'dailyAverage': float(row['daily_average'] or 0)
        } for row in results]
    })

@app.route('/api/sales/product-report', methods=['GET'])
def get_product_sales_report():
    """Get aggregated sales data by product for product sales report"""
    db = get_db()
    cursor = db.cursor()
    
    # Get date range parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Validate date parameters
    if not start_date or not end_date:
        return jsonify({'error': 'Both start_date and end_date are required'}), 400
    
    try:
        # Validate date formats and calculate days in range
        from datetime import datetime
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Check if start date is after end date
        if start_dt > end_dt:
            return jsonify({'error': 'Start date must be before or equal to end date'}), 400
            
        days_in_range = (end_dt - start_dt).days + 1
        
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Query to aggregate sales by product
    query = '''
        SELECT 
            p.id as productId,
            p.name as productName,
            p.category,
            p.price as price,
            COALESCE(SUM(s.sale_cash), 0) as totalSales,
            COALESCE(SUM(s.sale_units), 0) as totalUnits
        FROM products p
        LEFT JOIN sales s ON p.id = s.product_id 
            AND DATE(s.created_at) >= ? 
            AND DATE(s.created_at) <= ?
        WHERE p.id != 1  -- Exclude 'None' product
        GROUP BY p.id, p.name, p.category, p.price
        HAVING totalSales > 0 OR totalUnits > 0
        ORDER BY totalSales DESC
    '''
    
    try:
        results = cursor.execute(query, (start_date, end_date)).fetchall()
        
        # Format response
        products = []
        for row in results:
            daily_average = round(float(row['totalSales']) / days_in_range, 2) if days_in_range > 0 else 0
            
            products.append({
                'productId': row['productId'],
                'productName': row['productName'],
                'category': row['category'],
                'price': float(row['price']),
                'totalSales': float(row['totalSales']),
                'totalUnits': row['totalUnits'],
                'dailyAverage': daily_average
            })
        
        return jsonify({
            'products': products,
            'daysInRange': days_in_range
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve sales data: ' + str(e)}), 500

@app.route('/api/sales/generate-demo-data', methods=['POST'])
def generate_demo_sales_data():
    """Generate demo sales data for testing"""
    import random
    from datetime import datetime, timedelta
    
    db = get_db()
    cursor = db.cursor()
    
    # Get parameters
    data = request.json or {}
    date_from = data.get('date_from')
    date_to = data.get('date_to')
    devices_per_day = data.get('devicesPerDay', 1.0)  # 100% of devices have sales each day
    
    # Parse and validate date parameters
    if date_from and date_to:
        try:
            # Parse dates
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            end_date = datetime.strptime(date_to, '%Y-%m-%d')
            
            # Validate date range
            if start_date > end_date:
                return jsonify({'error': 'date_from must be less than or equal to date_to'}), 400
            
            # Calculate days in range
            days = (end_date - start_date).days + 1
            
            # Optional: Limit maximum range to prevent excessive data generation
            if days > 365:
                return jsonify({'error': 'Date range cannot exceed 365 days'}), 400
                
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    else:
        # Fallback to legacy behavior for backward compatibility
        days = data.get('days', 30)  # Default 30 days of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days - 1)
    
    # Get all active devices
    devices = cursor.execute('''
        SELECT id FROM devices WHERE deleted_at IS NULL
    ''').fetchall()
    
    if not devices:
        return jsonify({'error': 'No devices found'}), 400
    
    # Get all products
    products = cursor.execute('''
        SELECT id, price FROM products WHERE id != 1
    ''').fetchall()
    
    if not products:
        return jsonify({'error': 'No products found'}), 400
    
    # Clear existing sales data if requested
    if data.get('clearExisting', False):
        cursor.execute('DELETE FROM sales')
        db.commit()
    
    # Generate sales for the specified date range
    total_sales_created = 0
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        
        # Determine which devices have sales this day
        num_devices_with_sales = int(len(devices) * devices_per_day)
        devices_with_sales = random.sample(devices, num_devices_with_sales)
        
        for device in devices_with_sales:
            device_id = device['id']
            
            # Generate 1-5 transactions per device per day
            num_transactions = random.randint(1, 5)
            
            for _ in range(num_transactions):
                # Select a random product
                product = random.choice(products)
                product_id = product['id']
                base_price = float(product['price'])
                
                # Generate sale units (1-10 items)
                sale_units = random.randint(1, 10)
                
                # Calculate sale cash with some variation (±10%)
                price_variation = random.uniform(0.9, 1.1)
                sale_cash = round(base_price * sale_units * price_variation, 2)
                
                # Set created_at to a random time during the day
                hour = random.randint(6, 22)  # 6 AM to 10 PM
                minute = random.randint(0, 59)
                created_at = current_date.replace(hour=hour, minute=minute, second=0)
                
                cursor.execute('''
                    INSERT INTO sales (device_id, product_id, sale_units, sale_cash, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (device_id, product_id, sale_units, sale_cash, 
                     created_at.strftime('%Y-%m-%d %H:%M:%S'),
                     created_at.strftime('%Y-%m-%d %H:%M:%S')))
                
                total_sales_created += 1
    
    db.commit()
    
    return jsonify({
        'success': True,
        'count': total_sales_created,  # Frontend expects 'count' field
        'salesCreated': total_sales_created,  # Keep for backward compatibility
        'daysOfData': days,
        'dateFrom': start_date.strftime('%Y-%m-%d'),
        'dateTo': end_date.strftime('%Y-%m-%d'),
        'startDate': start_date.strftime('%Y-%m-%d'),  # Keep for backward compatibility
        'endDate': end_date.strftime('%Y-%m-%d')      # Keep for backward compatibility
    })

# Slot Metrics Endpoints

@app.route('/api/metrics/calculate', methods=['POST'])
def calculate_all_metrics():
    """Manually trigger metrics calculation for all devices"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get all active planogram slots with required relationships
        slots = cursor.execute('''
            SELECT 
                ps.id as slot_id,
                ps.quantity,
                ps.capacity,
                ps.product_id,
                cc.device_id
            FROM planogram_slots ps
            JOIN planograms p ON ps.planogram_id = p.id
            JOIN cabinet_configurations cc ON p.cabinet_id = cc.id
            JOIN devices d ON cc.device_id = d.id
            WHERE d.deleted_at IS NULL
            AND ps.product_id IS NOT NULL
            ORDER BY cc.device_id, ps.id
        ''').fetchall()
        
        processed = 0
        for slot in slots:
            calculate_slot_metrics(
                slot['slot_id'],
                slot['quantity'],
                slot['capacity'],
                slot['device_id'],
                slot['product_id']
            )
            processed += 1
        
        db.commit()
        return jsonify({
            'success': True,
            'processed': processed,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

def calculate_slot_metrics(slot_id, quantity, capacity, device_id, product_id):
    """Calculate metrics for a single slot"""
    db = get_db()
    cursor = db.cursor()
    
    # Calculate SO (Sold Out)
    is_sold_out = 1 if quantity == 0 else 0
    
    # Calculate PL (Product Level)
    product_level_percent = round((quantity * 100.0) / capacity) if capacity > 0 else 0
    
    # Calculate UTP (Units to Par)
    units_to_par = capacity - quantity
    
    # Calculate DRI (Days Remaining Inventory)
    # Get 28-day sales
    sales_28 = cursor.execute('''
        SELECT COALESCE(SUM(sale_units), 0) as total
        FROM sales
        WHERE device_id = ? 
        AND product_id = ?
        AND datetime(created_at) >= datetime('now', '-28 days')
    ''', (device_id, product_id)).fetchone()['total']
    
    if sales_28 > 0:
        daily_velocity = sales_28 / 28.0
    else:
        # Get historical average
        historical = cursor.execute('''
            SELECT 
                COALESCE(SUM(sale_units), 0) as total_sales,
                julianday('now') - julianday(MIN(created_at)) as days_active
            FROM sales
            WHERE device_id = ? AND product_id = ?
        ''', (device_id, product_id)).fetchone()
        
        if historical['total_sales'] and historical['total_sales'] > 0 and historical['days_active'] and historical['days_active'] > 0:
            daily_velocity = historical['total_sales'] / historical['days_active']
        else:
            daily_velocity = 0.1  # Default minimum
    
    # Calculate DRI
    if daily_velocity > 0 and quantity > 0:
        dri = int(quantity / daily_velocity)
    else:
        dri = 0 if quantity == 0 else 999
    
    dri = min(dri, 999)  # Cap at 999
    
    # Get all-time sales for additional stats
    all_time_stats = cursor.execute('''
        SELECT 
            COALESCE(SUM(sale_units), 0) as total_sales,
            COUNT(DISTINCT date(created_at)) as days_with_sales
        FROM sales
        WHERE device_id = ? AND product_id = ?
    ''', (device_id, product_id)).fetchone()
    
    # Upsert metrics
    cursor.execute('''
        INSERT OR REPLACE INTO slot_metrics (
            planogram_slot_id, is_sold_out, days_remaining_inventory, 
            product_level_percent, units_to_par,
            sales_28_day, sales_all_time, days_with_sales, daily_velocity, 
            last_calculated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (
        slot_id, is_sold_out, dri, product_level_percent, units_to_par,
        sales_28, all_time_stats['total_sales'], all_time_stats['days_with_sales'], 
        daily_velocity
    ))

# Dashboard Metrics API Endpoints

@app.route('/api/metrics/weekly', methods=['GET'])
def get_weekly_metrics():
    """Get weekly metrics for dashboard"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get current week and previous week date ranges
        from datetime import datetime, timedelta
        import calendar
        
        now = datetime.now()
        # Get start of current week (Monday)
        current_week_start = now - timedelta(days=now.weekday())
        current_week_start = current_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        current_week_end = current_week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        # Previous week
        prev_week_start = current_week_start - timedelta(days=7)
        prev_week_end = current_week_start - timedelta(microseconds=1)
        
        # Current week revenue
        current_week_revenue = cursor.execute('''
            SELECT COALESCE(SUM(sale_cash), 0) as revenue
            FROM sales 
            WHERE created_at >= ? AND created_at <= ?
        ''', (current_week_start.isoformat(), current_week_end.isoformat())).fetchone()[0]
        
        # Previous week revenue
        prev_week_revenue = cursor.execute('''
            SELECT COALESCE(SUM(sale_cash), 0) as revenue
            FROM sales 
            WHERE created_at >= ? AND created_at <= ?
        ''', (prev_week_start.isoformat(), prev_week_end.isoformat())).fetchone()[0]
        
        # Calculate growth percentage
        if prev_week_revenue > 0:
            growth_percentage = ((current_week_revenue - prev_week_revenue) / prev_week_revenue) * 100
        else:
            growth_percentage = 100 if current_week_revenue > 0 else 0
        
        # Get device count (active devices)
        device_count = cursor.execute('''
            SELECT COUNT(*) FROM devices WHERE deleted_at IS NULL
        ''').fetchone()[0]
        
        # Average revenue per device
        avg_revenue_per_device = current_week_revenue / device_count if device_count > 0 else 0
        
        # Top performing location this week
        top_location = cursor.execute('''
            SELECT l.name, COALESCE(SUM(s.sale_cash), 0) as revenue
            FROM devices d
            LEFT JOIN locations l ON d.location_id = l.id
            LEFT JOIN sales s ON d.id = s.device_id 
                AND s.created_at >= ? AND s.created_at <= ?
            WHERE d.deleted_at IS NULL
            GROUP BY l.name
            ORDER BY revenue DESC
            LIMIT 1
        ''', (current_week_start.isoformat(), current_week_end.isoformat())).fetchone()
        
        top_location_name = top_location[0] if top_location and top_location[0] else "No Location"
        top_location_revenue = top_location[1] if top_location else 0
        
        return jsonify({
            'weeklyRevenue': round(current_week_revenue, 2),
            'weeklyGrowth': round(growth_percentage, 1),
            'deviceCount': device_count,
            'avgRevenuePerDevice': round(avg_revenue_per_device, 2),
            'topLocation': top_location_name,
            'topLocationRevenue': round(top_location_revenue, 2),
            'weekStart': current_week_start.isoformat(),
            'weekEnd': current_week_end.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve weekly metrics: ' + str(e)}), 500

@app.route('/api/metrics/timeline', methods=['GET'])
def get_growth_timeline():
    """Get monthly revenue timeline for growth visualization"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get last 6 months of data
        from datetime import datetime, timedelta
        import calendar
        
        now = datetime.now()
        timeline = []
        
        for i in range(5, -1, -1):  # Last 6 months
            # Calculate month start and end
            target_date = now - timedelta(days=i*30)  # Approximate month
            month_start = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Get last day of month
            last_day = calendar.monthrange(month_start.year, month_start.month)[1]
            month_end = month_start.replace(day=last_day, hour=23, minute=59, second=59)
            
            # Get revenue for this month
            revenue = cursor.execute('''
                SELECT COALESCE(SUM(sale_cash), 0) as revenue
                FROM sales 
                WHERE created_at >= ? AND created_at <= ?
            ''', (month_start.isoformat(), month_end.isoformat())).fetchone()[0]
            
            # Determine if this is a milestone month (>$2000 revenue)
            is_milestone = revenue >= 2000
            
            timeline.append({
                'period': month_start.strftime('%b'),
                'revenue': round(revenue, 2),
                'milestone': is_milestone,
                'month': month_start.month,
                'year': month_start.year
            })
        
        return jsonify(timeline)
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve timeline data: ' + str(e)}), 500

@app.route('/api/metrics/achievements', methods=['GET'])
def get_achievements():
    """Get current achievement progress"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get current month revenue
        from datetime import datetime
        import calendar
        
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day = calendar.monthrange(now.year, now.month)[1]
        month_end = now.replace(day=last_day, hour=23, minute=59, second=59)
        
        current_month_revenue = cursor.execute('''
            SELECT COALESCE(SUM(sale_cash), 0) as revenue
            FROM sales 
            WHERE created_at >= ? AND created_at <= ?
        ''', (month_start.isoformat(), month_end.isoformat())).fetchone()[0]
        
        # Achievement targets
        monthly_target = 4000
        
        # Calculate progress
        progress = min(100, (current_month_revenue / monthly_target) * 100)
        
        # Determine achievement title and description
        if progress >= 100:
            title = "Monthly Revenue Champion! 🏆"
            description = f"Congratulations! You've exceeded your ${monthly_target:,} monthly goal!"
        elif progress >= 75:
            title = "Nearly There! 🎯"
            description = f"You're {progress:.0f}% toward your ${monthly_target:,} monthly goal"
        elif progress >= 50:
            title = "Great Progress! 📈"
            description = f"You're {progress:.0f}% toward your ${monthly_target:,} monthly goal"
        else:
            title = "Building Momentum! 🚀"
            description = f"You're {progress:.0f}% toward your ${monthly_target:,} monthly goal"
        
        return jsonify({
            'title': title,
            'description': description,
            'progress': round(progress, 1),
            'target': monthly_target,
            'current': round(current_month_revenue, 2),
            'remaining': round(monthly_target - current_month_revenue, 2)
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve achievements: ' + str(e)}), 500

@app.route('/api/metrics/top-performers', methods=['GET'])
def get_top_performers():
    """Get top performing devices and locations this week"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get current week date range
        from datetime import datetime, timedelta
        
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        # Top performing device by revenue
        top_device = cursor.execute('''
            SELECT d.asset, COALESCE(SUM(s.sale_cash), 0) as revenue
            FROM devices d
            LEFT JOIN sales s ON d.id = s.device_id 
                AND s.created_at >= ? AND s.created_at <= ?
            WHERE d.deleted_at IS NULL
            GROUP BY d.id, d.asset
            ORDER BY revenue DESC
            LIMIT 1
        ''', (week_start.isoformat(), week_end.isoformat())).fetchone()
        
        # Top performing location by revenue
        top_location = cursor.execute('''
            SELECT l.name, COALESCE(SUM(s.sale_cash), 0) as revenue
            FROM devices d
            LEFT JOIN locations l ON d.location_id = l.id
            LEFT JOIN sales s ON d.id = s.device_id 
                AND s.created_at >= ? AND s.created_at <= ?
            WHERE d.deleted_at IS NULL
            GROUP BY l.name
            ORDER BY revenue DESC
            LIMIT 1
        ''', (week_start.isoformat(), week_end.isoformat())).fetchone()
        
        # Device with highest growth (current week vs previous week)
        prev_week_start = week_start - timedelta(days=7)
        prev_week_end = week_start - timedelta(microseconds=1)
        
        growth_leader = cursor.execute('''
            SELECT 
                d.asset,
                COALESCE(SUM(CASE WHEN s.created_at >= ? AND s.created_at <= ? THEN s.sale_cash ELSE 0 END), 0) as current_week,
                COALESCE(SUM(CASE WHEN s.created_at >= ? AND s.created_at <= ? THEN s.sale_cash ELSE 0 END), 0) as prev_week
            FROM devices d
            LEFT JOIN sales s ON d.id = s.device_id
            WHERE d.deleted_at IS NULL
            GROUP BY d.id, d.asset
            HAVING prev_week > 0
            ORDER BY (current_week - prev_week) / prev_week DESC
            LIMIT 1
        ''', (week_start.isoformat(), week_end.isoformat(), 
              prev_week_start.isoformat(), prev_week_end.isoformat())).fetchone()
        
        performers = []
        
        if top_device:
            performers.append({
                'title': 'Best Device',
                'name': f"Device #{top_device[0]}",
                'value': f"${top_device[1]:.2f}"
            })
        
        if top_location:
            performers.append({
                'title': 'Top Location',
                'name': top_location[0] or "Unknown Location",
                'value': f"${top_location[1]:.2f}"
            })
        
        if growth_leader:
            current_week_revenue = growth_leader[1]
            prev_week_revenue = growth_leader[2]
            if prev_week_revenue > 0:
                growth_percentage = ((current_week_revenue - prev_week_revenue) / prev_week_revenue) * 100
                performers.append({
                    'title': 'Growth Leader',
                    'name': f"Device #{growth_leader[0]}",
                    'value': f"+{growth_percentage:.1f}%"
                })
        
        # Fill with default if we don't have enough data
        while len(performers) < 3:
            if len(performers) == 0:
                performers.append({
                    'title': 'Best Device',
                    'name': 'No data yet',
                    'value': '$0.00'
                })
            elif len(performers) == 1:
                performers.append({
                    'title': 'Top Location',
                    'name': 'No data yet',
                    'value': '$0.00'
                })
            else:
                performers.append({
                    'title': 'Growth Leader',
                    'name': 'No data yet',
                    'value': '+0%'
                })
        
        return jsonify(performers)
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve top performers: ' + str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """AI chat endpoint for business insights and system guidance"""
    try:
        import os
        from knowledge_base import get_page_knowledge, search_knowledge, get_navigation_help, get_workflow_help, get_troubleshooting_help
        
        # Check if API key is available
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({
                'response': 'AI chat is not configured. Please set the ANTHROPIC_API_KEY environment variable to enable AI assistance.'
            })
        
        data = request.json
        user_message = data.get('message', '')
        context = data.get('context', {})
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Create comprehensive business context summary
        weekly_metrics = context.get('weekly', {})
        achievements = context.get('achievements', {})
        performers = context.get('performers', [])
        sales_summary = context.get('salesSummary', {})
        devices = context.get('devices', [])
        page_context = context.get('pageContext', {})
        
        # Get recent sales data for more context
        db = get_db()
        cursor = db.cursor()
        
        # Recent sales (last 7 days)
        recent_sales = cursor.execute('''
            SELECT COUNT(*) as transactions, SUM(sale_cash) as revenue
            FROM sales 
            WHERE created_at >= datetime('now', '-7 days')
        ''').fetchone()
        
        # Top selling products
        top_products = cursor.execute('''
            SELECT p.name, SUM(s.sale_units) as units_sold, SUM(s.sale_cash) as revenue
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.created_at >= datetime('now', '-30 days')
            GROUP BY p.id, p.name
            ORDER BY units_sold DESC
            LIMIT 3
        ''').fetchall()
        
        # Get page-specific knowledge
        current_page = page_context.get('currentPage', '')
        page_knowledge = get_page_knowledge(current_page)
        
        # Determine intent and add relevant knowledge
        user_lower = user_message.lower()
        system_knowledge = ""
        
        # Check for navigation/feature questions
        if any(word in user_lower for word in ['how', 'where', 'what', 'navigate', 'find', 'access', 'use', 'do']):
            if page_knowledge:
                system_knowledge = f"""
CURRENT PAGE HELP ({page_knowledge.get('name', 'Unknown Page')}):
Purpose: {page_knowledge.get('purpose', 'No description available')}
Navigation: {page_knowledge.get('navigation', 'No navigation info')}
Key Features: {', '.join(page_knowledge.get('key_features', [])[:3])}
"""
            
            # Add navigation help for general questions
            nav_help = get_navigation_help()
            if 'navigate' in user_lower or 'where' in user_lower or 'find' in user_lower:
                system_knowledge += f"""
NAVIGATION HELP:
- Use top menu: {', '.join([item.split(' - ')[0] for item in nav_help['main_menu']['items'][:4]])}
- Direct URLs: Use hash navigation like #coolers, #planogram, #database
- Cross-page: Actions on one page automatically update others
"""
        
        # Check for workflow/task questions
        if any(word in user_lower for word in ['add', 'create', 'configure', 'setup', 'planogram', 'route', 'device']):
            workflows = get_workflow_help()
            if 'device' in user_lower and 'add' in user_lower:
                workflow = workflows.get('adding_new_device', {})
                system_knowledge += f"""
WORKFLOW HELP - Adding New Device:
{workflow.get('description', '')}
Steps: {' → '.join(workflow.get('steps', [])[:3])}
"""
            elif 'planogram' in user_lower:
                workflow = workflows.get('creating_planogram', {})
                system_knowledge += f"""
WORKFLOW HELP - Creating Planogram:
{workflow.get('description', '')}
Steps: {' → '.join(workflow.get('steps', [])[:3])}
"""
        
        business_context = f"""
COMPREHENSIVE BUSINESS DATA:

Financial Performance:
- Weekly Revenue: ${weekly_metrics.get('weeklyRevenue', 0):.2f} (Growth: {weekly_metrics.get('weeklyGrowth', 0):+.1f}%)
- Monthly Goal: {achievements.get('progress', 0):.1f}% complete (${achievements.get('current', 0):.2f} of ${achievements.get('target', 4000):.2f})
- Recent Activity: {recent_sales[0] if recent_sales else 0} transactions, ${recent_sales[1] if recent_sales and recent_sales[1] else 0:.2f} in last 7 days

Device Portfolio:
- Active Devices: {weekly_metrics.get('deviceCount', 0)}
- Average Revenue/Device: ${weekly_metrics.get('avgRevenuePerDevice', 0):.2f}
- Top Location: {weekly_metrics.get('topLocation', 'Unknown')} (${weekly_metrics.get('topLocationRevenue', 0):.2f})
- Device List: {len(devices)} total devices in system

Top Products (Last 30 Days):
{chr(10).join([f"- {product[0]}: {product[1]} units sold, ${product[2]:.2f}" for product in top_products[:3]]) if top_products else "- No recent sales data"}

Current Context:
- User is viewing: {page_context.get('currentPage', 'unknown page')}
- Time: {page_context.get('timestamp', 'unknown')}

{system_knowledge}

This is a small business vending machine operation. You can help with both business insights from their data AND system guidance for using the CVD application.
"""
        
        # Use real Anthropic API
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=api_key)
            
            response = client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=150,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are a comprehensive assistant for a small vending machine operation. You help with both business insights AND system guidance for using the CVD application.

{business_context}

The business owner is asking: "{user_message}"

For business questions: Use their actual data and be encouraging with specific actionable tips.
For system/navigation questions: Provide clear step-by-step guidance based on the system knowledge above.
For workflow questions: Give specific steps from the workflow help.

Respond in 1-3 sentences. Be helpful and specific."""
                    }
                ]
            )
            
            ai_response = response.content[0].text
            return jsonify({'response': ai_response})
            
        except Exception as api_error:
            print(f"Anthropic API error: {api_error}")
            # Fallback to rule-based responses if API fails
            response = generate_business_response(user_message.lower(), context)
            return jsonify({'response': f"[Fallback Mode] {response}"})
        
    except Exception as e:
        return jsonify({'error': 'Failed to process chat request: ' + str(e)}), 500

def generate_business_response(user_message, context):
    """Generate contextual business responses and system guidance based on keywords"""
    from knowledge_base import get_page_knowledge, get_navigation_help, get_workflow_help, get_troubleshooting_help
    
    weekly_metrics = context.get('weekly', {})
    achievements = context.get('achievements', {})
    performers = context.get('performers', [])
    page_context = context.get('pageContext', {})
    current_page = page_context.get('currentPage', '')
    
    # Navigation and feature questions
    if any(word in user_message for word in ['how', 'where', 'navigate', 'find', 'access', 'get to', 'go to']):
        if 'device' in user_message:
            if 'add' in user_message or 'new' in user_message:
                return "To add a new device, click 'Add New Device' in the top menu or navigate to #new-device. Follow the 5-step wizard to configure your device with cabinets, location, and route assignment."
            else:
                return "To view all devices, click 'Coolers' in the top menu or navigate to #coolers. You can search, sort, and manage your entire device fleet from there."
        elif 'planogram' in user_message:
            return "To create planograms, click 'Planogram' in the top menu or navigate to #planogram. Select your device and cabinet, then drag products from the catalog to design your layout."
        elif 'sales' in user_message or 'report' in user_message:
            return "For sales reports, use 'Asset Sales' for device performance or 'Product Sales' for product analytics. Both are available in the top menu with filtering and export options."
        elif 'route' in user_message:
            return "For route management, click 'Routes' in the top menu or navigate to #route-planning. You can create routes, assign devices, and use the map view for optimization."
        else:
            return "Navigate using the top menu: Coolers (devices), Add New Device, Planogram (layouts), Database (data), Routes (planning), and Sales reports. You can also use direct URLs like #coolers, #planogram, etc."
    
    # Workflow and task questions
    elif any(word in user_message for word in ['create', 'make', 'setup', 'configure', 'build']):
        if 'device' in user_message:
            return "To create a new device: Navigate to #new-device, enter device info (asset, model, location), configure cabinets (type and layout), assign route, upload photos, and save. The wizard guides you through each step."
        elif 'planogram' in user_message:
            return "To create a planogram: Go to #planogram, select your device and cabinet, drag products from the catalog to slots, set quantities and par levels, and adjust pricing. Changes auto-save to the database."
        elif 'route' in user_message:
            return "To create a route: Go to #route-planning, define the route name and number, assign devices by location, use #route-schedule for map visualization, and optimize the sequence for efficiency."
        else:
            return "For creating anything in the system, use the appropriate page: #new-device for devices, #planogram for layouts, #route-planning for routes. Each page has guided workflows to help you complete tasks."
    
    # Troubleshooting questions
    elif any(word in user_message for word in ['not working', 'broken', 'error', 'problem', 'issue', 'help', 'stuck']):
        if 'device' in user_message and 'not' in user_message:
            return "If devices aren't appearing, ensure all wizard steps were completed and the asset number is unique. Try refreshing the page or checking #coolers to see if it was saved."
        elif 'planogram' in user_message and 'not' in user_message:
            return "If planograms won't load, make sure the device has cabinet configuration. Check that the device was saved properly and try refreshing the planogram page."
        elif 'drag' in user_message or 'drop' in user_message:
            return "If drag-and-drop isn't working, ensure the planogram loaded first and the target slot is empty. Try refreshing the page and waiting for the product catalog to load completely."
        else:
            return "For general issues: refresh the page, check your internet connection, ensure required fields are filled, and verify you're using a supported browser. Contact support if problems persist."
    
    # Revenue-related questions
    if any(word in user_message for word in ['revenue', 'sales', 'money', 'earning', 'profit', 'income', 'business', 'doing', 'perform']):
        revenue = weekly_metrics.get('weeklyRevenue', 0)
        growth = weekly_metrics.get('weeklyGrowth', 0)
        if growth > 0:
            return f"Great news! Your weekly revenue is ${revenue:.2f}, which is up {growth:.1f}% from last week. This shows strong business growth. Keep focusing on your top-performing locations!"
        else:
            return f"Your weekly revenue is ${revenue:.2f}. While this is {abs(growth):.1f}% lower than last week, this is normal for vending businesses. Consider checking your top locations or refreshing inventory."
    
    # Route optimization questions
    elif any(word in user_message for word in ['route', 'optimize', 'efficiency', 'delivery', 'visit', 'plan', 'schedule', 'trip']):
        top_location = weekly_metrics.get('topLocation', 'Unknown')
        return f"For route optimization, I recommend starting with your highest-performing location: {top_location}. Visit locations showing declining performance more frequently, and consider restocking your best-selling items during peak hours."
    
    # Device performance questions
    elif any(word in user_message for word in ['device', 'machine', 'performance', 'vending', 'equipment', 'unit', 'cooler']):
        device_count = weekly_metrics.get('deviceCount', 0)
        avg_revenue = weekly_metrics.get('avgRevenuePerDevice', 0)
        if len(performers) > 0:
            best_device = performers[0].get('name', 'Unknown')
            return f"You have {device_count} active devices averaging ${avg_revenue:.2f} each. Your best performer is {best_device}. Consider analyzing what makes this device successful and apply those insights to underperforming locations."
        return f"You have {device_count} active devices averaging ${avg_revenue:.2f} each. Monitor individual device performance regularly to identify optimization opportunities."
    
    # Goal and achievement questions
    elif any(word in user_message for word in ['goal', 'target', 'achievement', 'progress', 'milestone', 'reach', 'hit']):
        progress = achievements.get('progress', 0)
        current = achievements.get('current', 0)
        target = achievements.get('target', 4000)
        remaining = target - current
        return f"You're {progress:.1f}% toward your monthly goal of ${target:.2f}. You need ${remaining:.2f} more to reach your target. Based on your current weekly performance, you're on track to meet this goal!"
    
    # Inventory questions
    elif any(word in user_message for word in ['inventory', 'stock', 'product', 'merchandise', 'supply', 'restock', 'items']):
        return "Monitor your planogram data regularly to identify fast-moving products. Increase par levels for popular items and consider seasonal adjustments. Check the Merchandise section for detailed inventory insights."
    
    # General business advice
    elif any(word in user_message for word in ['improve', 'grow', 'advice', 'tips', 'help', 'better', 'increase', 'boost']):
        return "To grow your business: 1) Focus on your top-performing locations and replicate their success elsewhere, 2) Maintain optimal inventory levels based on sales velocity, 3) Visit underperforming devices more frequently, and 4) Consider expanding to similar high-traffic locations."
    
    # Default response
    else:
        return "I can help you with revenue analysis, route optimization, device performance, goal tracking, and inventory management. What specific aspect of your vending business would you like to discuss?"

# Knowledge Base API Endpoints
@app.route('/api/knowledge-base/articles', methods=['GET'])
@auth_manager.require_auth
def get_knowledge_base_articles():
    """Get all knowledge base articles with metadata"""
    try:
        from services.knowledge_base_service import KnowledgeBaseService
        
        kb_service = KnowledgeBaseService()
        articles = kb_service.scan_articles()
        categories = kb_service.get_categories()
        
        # Build category counts
        category_counts = {}
        for article in articles:
            category = article['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return jsonify({
            'success': True,
            'articles': articles,
            'total_count': len(articles),
            'categories': category_counts
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to load articles: {str(e)}'
        }), 500

@app.route('/api/knowledge-base/articles/<article_id>', methods=['GET'])
@auth_manager.require_auth
def get_knowledge_base_article(article_id):
    """Get specific knowledge base article with content"""
    try:
        from services.knowledge_base_service import KnowledgeBaseService
        
        kb_service = KnowledgeBaseService()
        article = kb_service.get_article_by_id(article_id)
        
        if not article:
            return jsonify({
                'success': False,
                'error': 'Article not found'
            }), 404
            
        # Convert markdown to HTML for frontend
        import markdown
        content_html = markdown.markdown(article['content'], extensions=['codehilite', 'fenced_code'])
        
        return jsonify({
            'success': True,
            'article': {
                'id': article['id'],
                'title': article['title'],
                'content_html': content_html,
                'content_raw': article['content'],
                'metadata': {
                    'author': article['author'],
                    'category': article['category'],
                    'tags': article['tags'],
                    'difficulty': article['difficulty'],
                    'last_updated': article['last_updated'].isoformat() if hasattr(article['last_updated'], 'isoformat') else str(article['last_updated']),
                    'description': article.get('description', ''),
                    'word_count': article['word_count'],
                    'read_time_minutes': article['read_time_minutes']
                },
                'navigation': article.get('navigation', {})
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to load article: {str(e)}'
        }), 500

@app.route('/api/knowledge-base/search', methods=['GET'])
@auth_manager.require_auth
def search_knowledge_base():
    """Search knowledge base articles"""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip() or None
        difficulty = request.args.get('difficulty', '').strip() or None
        
        if not query or len(query) < 2:
            return jsonify({
                'success': False,
                'error': 'Query must be at least 2 characters'
            }), 400
            
        from services.knowledge_base_service import KnowledgeBaseService
        import time
        
        start_time = time.time()
        kb_service = KnowledgeBaseService()
        results = kb_service.search_articles(query, category, difficulty)
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total_results': len(results),
            'search_time_ms': round(search_time, 2),
            'filters': {
                'category': category,
                'difficulty': difficulty
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}'
        }), 500

@app.route('/api/knowledge-base/categories', methods=['GET'])
@auth_manager.require_auth
def get_knowledge_base_categories():
    """Get all knowledge base categories with metadata"""
    try:
        from services.knowledge_base_service import KnowledgeBaseService
        
        kb_service = KnowledgeBaseService()
        categories = kb_service.get_categories()
        
        return jsonify({
            'success': True,
            'categories': categories
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to load categories: {str(e)}'
        }), 500

@app.route('/api/knowledge-base/stats', methods=['GET'])
@auth_manager.require_auth
def get_knowledge_base_stats():
    """Get knowledge base statistics"""
    try:
        from services.knowledge_base_service import KnowledgeBaseService
        
        kb_service = KnowledgeBaseService()
        stats = kb_service.get_article_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to load stats: {str(e)}'
        }), 500

# DEX Parser Engine - moved to dex_parser.py

# DEX API Endpoints
@app.route('/api/dex/parse', methods=['POST'])
def parse_dex_file():
    """Parse uploaded DEX file with comprehensive error handling"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': {'message': 'No file uploaded', 'line': 0, 'field': 0}
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': {'message': 'No file selected', 'line': 0, 'field': 0}
            }), 400
        
        if not file.filename.endswith('.txt'):
            return jsonify({
                'success': False,
                'error': {'message': 'File must be a .txt file', 'line': 0, 'field': 0}
            }), 400
        
        # Read file content
        content = file.read().decode('utf-8', errors='ignore')
        
        # Parse DEX file
        parser = DEXParser()
        result = parser.parse_file(content, file.filename)
        
        if not result['success']:
            return jsonify(result), 400
        
        # Store in database using transaction
        db = get_db()
        db.execute('BEGIN TRANSACTION')
        
        try:
            # Insert main DEX read record
            cursor = db.cursor()
            cursor.execute('''
                INSERT INTO dex_reads (
                    filename, machine_serial, manufacturer, dex_version,
                    raw_content, total_records, parsed_successfully, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file.filename,
                result['machine_info'].get('machine_serial', ''),
                result['machine_info'].get('manufacturer', ''),
                result['machine_info'].get('version', ''),
                content,
                result['total_records'],
                result['parsed_successfully'],
                result.get('error_message')
            ))
            
            dex_read_id = cursor.lastrowid
            
            # Insert all DEX records
            for record in result['parsed_records']:
                cursor.execute('''
                    INSERT INTO dex_records (
                        dex_read_id, record_type, record_subtype, line_number,
                        raw_record, parsed_data
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    dex_read_id,
                    record['record_type'],
                    record['record_subtype'],
                    record['line_number'],
                    record['raw_record'],
                    json.dumps(record['parsed_data'])
                ))
            
            # Insert consolidated PA records
            for pa_record in result['pa_records']:
                data = pa_record['data']
                cursor.execute('''
                    INSERT INTO dex_pa_records (
                        dex_read_id, record_subtype, selection_number,
                        price_cents, capacity, units_sold, revenue_cents,
                        test_vends, free_vends, cash_sales, cash_sales_cents,
                        cashless_sales, cashless_sales_cents, discount_sales,
                        discount_sales_cents, line_number, row, "column"
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    dex_read_id,
                    'CONSOLIDATED',  # New record_subtype to indicate consolidated record
                    data['selection_number'],
                    data['price_cents'],
                    data['capacity'],
                    data['units_sold'],
                    data['revenue_cents'],
                    data['test_vends'],
                    data['free_vends'],
                    data['cash_sales'],
                    data['cash_sales_cents'],
                    data['cashless_sales'],
                    data['cashless_sales_cents'],
                    data['discount_sales'],
                    data['discount_sales_cents'],
                    pa_record['line_number'],
                    data.get('row'),
                    data.get('column')
                ))
            
            db.execute('COMMIT')
            
            return jsonify({
                'success': True,
                'dex_read_id': dex_read_id,
                'machine_info': result['machine_info'],
                'total_records': result['total_records'],
                'pa_records_count': len(result['pa_records']),
                'message': 'DEX file parsed and stored successfully'
            })
            
        except Exception as e:
            db.execute('ROLLBACK')
            return jsonify({
                'success': False,
                'error': {'message': f'Database error: {str(e)}', 'line': 0, 'field': 0}
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'message': f'Server error: {str(e)}', 'line': 0, 'field': 0}
        }), 500

@app.route('/api/dex/reads', methods=['GET'])
def get_dex_reads():
    """Get list of all DEX reads with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        offset = (page - 1) * per_page
        
        db = get_db()
        
        # Get total count
        total = db.execute('SELECT COUNT(*) FROM dex_reads').fetchone()[0]
        
        # Get paginated results
        reads = db.execute('''
            SELECT id, filename, machine_serial, manufacturer, dex_version,
                   upload_timestamp, total_records, parsed_successfully,
                   error_message, error_line, error_field
            FROM dex_reads
            ORDER BY upload_timestamp DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset)).fetchall()
        
        return jsonify({
            'success': True,
            'reads': [dict_from_row(row) for row in reads],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'message': f'Server error: {str(e)}'}
        }), 500

@app.route('/api/dex/reads/<int:read_id>', methods=['GET'])
def get_dex_read_details(read_id):
    """Get detailed information about a specific DEX read"""
    try:
        db = get_db()
        
        # Get main read info
        read_info = db.execute('''
            SELECT * FROM dex_reads WHERE id = ?
        ''', (read_id,)).fetchone()
        
        if not read_info:
            return jsonify({
                'success': False,
                'error': {'message': 'DEX read not found'}
            }), 404
        
        # Get all records for this read
        records = db.execute('''
            SELECT * FROM dex_records WHERE dex_read_id = ?
            ORDER BY line_number
        ''', (read_id,)).fetchall()
        
        # Get PA records for this read
        pa_records = db.execute('''
            SELECT * FROM dex_pa_records WHERE dex_read_id = ?
            ORDER BY line_number
        ''', (read_id,)).fetchall()
        
        return jsonify({
            'success': True,
            'read_info': dict_from_row(read_info),
            'records': [dict_from_row(row) for row in records],
            'pa_records': [dict_from_row(row) for row in pa_records]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'message': f'Server error: {str(e)}'}
        }), 500

@app.route('/api/dex/pa-records/<int:read_id>', methods=['GET'])
def get_pa_records(read_id):
    """Get PA records for selection grid display with enhanced grid data"""
    try:
        db = get_db()
        
        pa_records = db.execute('''
            SELECT * FROM dex_pa_records WHERE dex_read_id = ?
            ORDER BY selection_number, line_number
        ''', (read_id,)).fetchall()
        
        # Calculate grid metadata
        grid_info = calculate_grid_metadata(pa_records)
        
        return jsonify({
            'success': True,
            'pa_records': [dict_from_row(row) for row in pa_records],
            'grid_info': grid_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'message': f'Server error: {str(e)}'}
        }), 500

@app.route('/api/dex/grid-layout/<int:read_id>', methods=['GET'])
def get_grid_layout(read_id):
    """Get structured grid layout data for visualization"""
    try:
        db = get_db()
        
        pa_records = db.execute('''
            SELECT selection_number, row, "column", units_sold, revenue_cents, 
                   price_cents, capacity
            FROM dex_pa_records 
            WHERE dex_read_id = ? AND row IS NOT NULL AND "column" IS NOT NULL
            ORDER BY row, "column"
        ''', (read_id,)).fetchall()
        
        if not pa_records:
            return jsonify({
                'success': False,
                'error': {'message': 'No grid data found for this DEX file'}
            }), 404
        
        # Build grid structure
        grid_structure = build_grid_structure(pa_records)
        
        return jsonify({
            'success': True,
            'grid_layout': grid_structure['grid'],
            'dimensions': grid_structure['dimensions'],
            'metadata': grid_structure['metadata']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'message': f'Server error: {str(e)}'}
        }), 500

@app.route('/api/dex/grid-info/<int:read_id>', methods=['GET'])
def get_grid_info(read_id):
    """Get grid pattern detection metadata"""
    try:
        db = get_db()
        
        # Get selection numbers to re-analyze pattern
        selections = db.execute('''
            SELECT DISTINCT selection_number 
            FROM dex_pa_records 
            WHERE dex_read_id = ? AND selection_number IS NOT NULL
            ORDER BY selection_number
        ''', (read_id,)).fetchall()
        
        if not selections:
            return jsonify({
                'success': False,
                'error': {'message': 'No selection data found'}
            }), 404
        
        # Re-analyze pattern for metadata
        from grid_pattern_analyzer import GridPatternAnalyzer
        analyzer = GridPatternAnalyzer()
        selection_numbers = [row[0] for row in selections]
        grid_result = analyzer.analyze_selections(selection_numbers)
        
        # Get current grid data coverage
        grid_coverage = db.execute('''
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN row IS NOT NULL THEN 1 END) as with_grid
            FROM dex_pa_records 
            WHERE dex_read_id = ?
        ''', (read_id,)).fetchone()
        
        return jsonify({
            'success': True,
            'pattern_type': grid_result['pattern_type'],
            'confidence': grid_result['confidence'],
            'grid_dimensions': grid_result['grid_dimensions'],
            'coverage': {
                'total_records': grid_coverage[0],
                'with_grid': grid_coverage[1],
                'percentage': (grid_coverage[1] / grid_coverage[0] * 100) if grid_coverage[0] > 0 else 0
            },
            'errors': grid_result.get('errors', [])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'message': f'Server error: {str(e)}'}
        }), 500

@app.route('/api/dex/records/<int:read_id>', methods=['GET'])
def get_all_dex_records(read_id):
    """Get all parsed DEX records for a specific read"""
    try:
        db = get_db()
        
        records = db.execute('''
            SELECT * FROM dex_records WHERE dex_read_id = ?
            ORDER BY line_number
        ''', (read_id,)).fetchall()
        
        return jsonify({
            'success': True,
            'records': [dict_from_row(row) for row in records]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'message': f'Server error: {str(e)}'}
        }), 500

# Error handlers for API routes - return JSON instead of HTML
@app.errorhandler(500)
def handle_internal_error(e):
    """Return JSON for API errors, HTML for others"""
    if request.path.startswith('/api/'):
        app.logger.error(f"API 500 error on {request.path}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    # Default HTML error page for non-API routes
    return f"<h1>500 Internal Server Error</h1><p>{str(e)}</p>", 500

@app.errorhandler(404)
def handle_not_found(e):
    """Return JSON for API 404s, HTML for others"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    # Default HTML error page for non-API routes
    return "<h1>404 Not Found</h1>", 404

# Static file serving routes for frontend compatibility
@app.route('/')
def serve_index():
    """Serve the main index.html file"""
    return send_from_directory('.', 'index.html')

@app.route('/pages/<path:filename>')
def serve_pages(filename):
    """Serve files from the pages directory"""
    return send_from_directory('pages', filename)

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve other static files (CSS, JS, images, etc.)"""
    # Fix: Exclude API routes from static file serving
    if filename.startswith('api/'):
        abort(404)  # Let Flask find the actual API route
    
    try:
        # Try to serve from root directory
        return send_from_directory('.', filename)
    except FileNotFoundError:
        # If file not found, return 404
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    # Initialize database (will create tables if they don't exist)
    print(f"Initializing database: {DATABASE}")
    init_db()
    
    # Run migrations
    with app.app_context():
        migrate_database_schema()  # Handle schema updates for existing databases
        migrate_products()
        migrate_device_types()
        migrate_cabinet_types()
        init_sentinel_product()
        create_initial_admin()
    
    # Initialize activity tracker after database is ready
    print("Initializing activity tracker...")
    activity_tracker = ActivityTracker(app, DATABASE)
    
    # Initialize security monitor
    print("Initializing security monitor...")
    security_monitor = SecurityMonitor(DATABASE, activity_tracker)
    
    # Initialize activity trends module
    print("Initializing activity trends module...")
    try:
        with app.app_context():
            init_trends_module(app, DATABASE)
            
            # Verify all components initialized
            import activity_trends_api
            if not all([
                activity_trends_api.trends_cache,
                activity_trends_api.trends_service,
                activity_trends_api.performance_monitor,
                activity_trends_api.rate_limiter
            ]):
                missing = []
                if not activity_trends_api.trends_cache: missing.append('cache')
                if not activity_trends_api.trends_service: missing.append('service')
                if not activity_trends_api.performance_monitor: missing.append('monitor')
                if not activity_trends_api.rate_limiter: missing.append('rate_limiter')
                raise RuntimeError(f"Activity trends module initialization failed - missing: {', '.join(missing)}")
                
        print("✓ Activity trends module initialized successfully")
    except Exception as e:
        print(f"✗ CRITICAL: Failed to initialize activity trends: {e}")
        # Continue running but trends API will be unavailable
        print("Warning: Activity Trends API will not be available")
    
    # Run the server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print(f"Starting CVD API server on port {port}")
    
    try:
        app.run(debug=debug, host='0.0.0.0', port=port)
    finally:
        # Cleanup activity tracker on shutdown
        if activity_tracker:
            activity_tracker.shutdown()