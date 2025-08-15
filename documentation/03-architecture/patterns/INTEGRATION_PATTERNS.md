# Integration Architecture Patterns


## Metadata
- **ID**: 03_ARCHITECTURE_PATTERNS_INTEGRATION_PATTERNS
- **Type**: Architecture
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #architecture #authentication #data-exchange #data-layer #database #debugging #device-management #dex-parser #integration #logistics #machine-learning #metrics #optimization #performance #planogram #product-placement #quality-assurance #reporting #route-management #security #system-design #technical #testing #troubleshooting #vending-machine
- **Intent**: Architecture for Integration Architecture Patterns
- **Audience**: system administrators, managers, end users, architects
- **Related**: BEST_PRACTICES.md, FRONTEND_PATTERNS.md, API_PATTERNS.md, SECURITY_PATTERNS.md
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/03-architecture/patterns/
- **Category**: Patterns
- **Search Keywords**: 1.0, 2025-08-12, actively, architecture, attempt), authentication, cabinet, cache, caching, carefully, clearly, cvd:, device, dex, discovery

**Document Version:** 1.0  
**Last Updated:** 2025-08-12  
**Status:** Complete

## Introduction

This document outlines the integration architecture patterns, service composition strategies, and external system integration approaches implemented in the CVD system. These patterns enable seamless integration with external services while maintaining system reliability and performance.

## Table of Contents

1. [External Service Integration Patterns](#external-service-integration-patterns)
2. [API Composition Patterns](#api-composition-patterns)
3. [Data Synchronization Patterns](#data-synchronization-patterns)
4. [Event-Driven Integration](#event-driven-integration)
5. [Caching and Performance Patterns](#caching-and-performance-patterns)
6. [Error Handling and Resilience](#error-handling-and-resilience)
7. [Service Discovery and Configuration](#service-discovery-and-configuration)
8. [Monitoring and Observability](#monitoring-and-observability)
9. [Security Integration Patterns](#security-integration-patterns)
10. [Testing Integration Patterns](#testing-integration-patterns)

## External Service Integration Patterns

### HTTP Client Integration Pattern

**Implementation in CVD:**
```python
import requests
import time
from datetime import datetime, timedelta
from functools import wraps
import json

class ExternalServiceClient:
    """Base class for external service integrations"""
    
    def __init__(self, base_url, api_key=None, timeout=30, max_retries=3):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # Configure session
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'CVD-System/1.0'
            })
    
    def with_retry(self, func):
        """Decorator for automatic retries with exponential backoff"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.ConnectionError, 
                        requests.exceptions.Timeout,
                        requests.exceptions.RequestException) as e:
                    
                    if attempt == self.max_retries:
                        raise e
                    
                    # Exponential backoff
                    wait_time = (2 ** attempt) * 1  # 1s, 2s, 4s
                    time.sleep(wait_time)
                    
            return None
        return wrapper
    
    @with_retry
    def get(self, endpoint, params=None):
        """GET request with retry logic"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    @with_retry
    def post(self, endpoint, data=None, json_data=None):
        """POST request with retry logic"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(
            url, 
            data=data, 
            json=json_data, 
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def close(self):
        """Clean up session"""
        self.session.close()
```

### Geocoding Service Integration

**Implementation in CVD (app.py):**
```python
def geocode_address(address):
    """
    Geocode address using Nominatim service with caching and rate limiting
    Returns: (latitude, longitude) or (None, None) if failed
    """
    if not address or len(address.strip()) < 5:
        return None, None
    
    # Normalize address for caching
    normalized_address = address.strip().lower()
    
    # Check cache first
    cache_key = f"geocode:{normalized_address}"
    cached_result = get_from_cache(cache_key)
    if cached_result:
        return cached_result['lat'], cached_result['lon']
    
    try:
        # Respect Nominatim rate limit (1 request per second)
        time.sleep(1)
        
        # Prepare request
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': 'CVD-System/1.0 (vending-management)',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0:
            location = data[0]
            latitude = float(location['lat'])
            longitude = float(location['lon'])
            
            # Cache successful result for 24 hours
            cache_result = {'lat': latitude, 'lon': longitude}
            set_cache(cache_key, cache_result, expires_in=86400)
            
            return latitude, longitude
        else:
            # Cache negative result for 1 hour to avoid repeated requests
            set_cache(cache_key, {'lat': None, 'lon': None}, expires_in=3600)
            return None, None
                
    except Exception as e:
        print(f"Geocoding error for {address}: {e}")
        return None, None

@app.route('/api/geocode', methods=['POST'])
@require_auth
def geocode_address_endpoint():
    """API endpoint for address geocoding"""
    data = request.json
    
    if not data or 'address' not in data:
        return jsonify({'error': 'Address is required'}), 400
    
    try:
        latitude, longitude = geocode_address(data['address'])
        
        if latitude is not None and longitude is not None:
            return jsonify({
                'latitude': latitude,
                'longitude': longitude,
                'address': data['address']
            })
        else:
            return jsonify({'error': 'Failed to geocode address'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### AI Service Integration

**Implementation in CVD (planogram_optimizer.py):**
```python
class PlanogramOptimizer:
    """AI-powered planogram optimization using Claude API"""
    
    def __init__(self, api_key: str, db_path: str = 'cvd.db'):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.db_path = db_path
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 3600  # 1 hour cache
    
    def optimize_planogram(self, device_id: int, cabinet_index: int = 0, 
                          days: int = 30) -> Optional[Dict]:
        """
        Generate AI-powered planogram optimization recommendations
        """
        # Check cache first
        cache_key = f"optimize_{device_id}_{cabinet_index}_{days}"
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        # Gather data
        sales_data = self.get_sales_data(device_id, days)
        current_planogram = self.get_current_planogram(device_id, cabinet_index)
        
        if not current_planogram or not sales_data:
            return None
        
        try:
            # Prepare AI prompt
            prompt = self._build_optimization_prompt(
                sales_data, current_planogram, device_id, cabinet_index
            )
            
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                temperature=0.1,
                system=self._get_system_prompt(),
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse response
            content = response.content[0].text
            optimization_result = self._parse_optimization_response(content)
            
            # Cache result
            self._cache_result(cache_key, optimization_result)
            
            return optimization_result
            
        except Exception as e:
            print(f"AI optimization error: {e}")
            return None
    
    def _build_optimization_prompt(self, sales_data, planogram, device_id, cabinet_index):
        """Build AI prompt for optimization"""
        
        prompt = f"""
        PLANOGRAM OPTIMIZATION REQUEST
        
        Device ID: {device_id}
        Cabinet Index: {cabinet_index}
        Cabinet Size: {planogram['cabinet']['rows']}x{planogram['cabinet']['columns']}
        
        CURRENT SALES PERFORMANCE (last 30 days):
        """
        
        for product in sales_data:
            prompt += f"""
        - {product['product_name']} ({product['category']}):
          * Units sold: {product['total_units']}
          * Revenue: ${product['total_revenue']:.2f}
          * Price: ${product['price']:.2f}
          * Days active: {product['days_sold']}/30
        """
        
        prompt += f"""
        
        CURRENT PLANOGRAM LAYOUT:
        Total slots: {len(planogram['slots'])}
        """
        
        # Group slots by product
        products_in_slots = {}
        for slot in planogram['slots']:
            if slot['product_id']:
                product_key = f"{slot['product_name']} (ID: {slot['product_id']})"
                if product_key not in products_in_slots:
                    products_in_slots[product_key] = []
                products_in_slots[product_key].append({
                    'position': slot['slot_position'],
                    'quantity': slot['quantity'],
                    'capacity': slot['capacity'],
                    'par_level': slot['par_level']
                })
        
        for product, slots in products_in_slots.items():
            prompt += f"""
        
        {product}:
          * Positions: {', '.join([s['position'] for s in slots])}
          * Total capacity: {sum([s['capacity'] for s in slots])}
          * Current stock: {sum([s['quantity'] for s in slots])}
        """
        
        prompt += """
        
        Please analyze this data and provide optimization recommendations.
        Focus on maximizing revenue and product visibility based on sales performance.
        """
        
        return prompt
    
    def _get_system_prompt(self):
        """System prompt for AI optimization"""
        return """
        You are a vending machine planogram optimization expert. 
        Analyze sales data and current product placement to recommend improvements.
        
        Consider these factors:
        1. High-performing products should get prime positions (eye level, easy access)
        2. Product variety and category balance
        3. Impulse purchase positioning
        4. Inventory turnover optimization
        5. Revenue per slot maximization
        
        Provide specific, actionable recommendations in JSON format with:
        - Recommended changes with reasons
        - Expected impact on sales
        - Priority level (high/medium/low)
        """
    
    def _is_cached(self, cache_key):
        """Check if result is cached and valid"""
        if cache_key in self.cache:
            cached_time = self.cache[cache_key]['timestamp']
            if datetime.now().timestamp() - cached_time < self.cache_ttl:
                return True
        return False
    
    def _cache_result(self, cache_key, result):
        """Cache optimization result"""
        self.cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now().timestamp()
        }
```

## API Composition Patterns

### Service Aggregation Pattern

**Implementation in CVD:**
```python
class ServiceAggregator:
    """Aggregate data from multiple services for dashboard views"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.geocoder = None  # Initialized when needed
        self.ai_optimizer = None  # Initialized when needed
    
    def get_dashboard_data(self, user_id, user_role):
        """Aggregate dashboard data based on user role"""
        aggregated_data = {}
        
        # Get base metrics (all roles)
        aggregated_data['metrics'] = self._get_base_metrics(user_id, user_role)
        
        # Role-specific data aggregation
        if user_role in ['admin', 'manager']:
            aggregated_data['fleet_overview'] = self._get_fleet_overview()
            aggregated_data['recent_activities'] = self._get_recent_activities()
            aggregated_data['alerts'] = self._get_system_alerts()
            
        if user_role == 'admin':
            aggregated_data['user_metrics'] = self._get_user_metrics()
            aggregated_data['system_health'] = self._get_system_health()
            
        if user_role == 'driver':
            aggregated_data['my_routes'] = self._get_driver_routes(user_id)
            aggregated_data['pending_orders'] = self._get_driver_orders(user_id)
        
        # Enhance with location data if available
        if self.geocoder and 'fleet_overview' in aggregated_data:
            aggregated_data['fleet_overview'] = self._enhance_with_locations(
                aggregated_data['fleet_overview']
            )
        
        return aggregated_data
    
    def _get_base_metrics(self, user_id, user_role):
        """Get metrics based on user access level"""
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        
        if user_role == 'admin':
            # Full system metrics
            query = """
            SELECT 
                COUNT(*) as total_devices,
                COUNT(CASE WHEN deleted = 0 THEN 1 END) as active_devices,
                (SELECT COUNT(*) FROM users WHERE is_deleted = 0) as total_users,
                (SELECT COUNT(*) FROM service_orders WHERE status = 'pending') as pending_orders
            FROM devices
            """
        elif user_role == 'manager':
            # Manager's territory metrics
            query = """
            SELECT 
                COUNT(*) as total_devices,
                COUNT(CASE WHEN deleted = 0 THEN 1 END) as active_devices,
                (SELECT COUNT(*) FROM service_orders 
                 WHERE status = 'pending' AND route_id IN 
                 (SELECT id FROM routes WHERE manager_id = ?)) as pending_orders
            FROM devices 
            WHERE route_id IN (SELECT id FROM routes WHERE manager_id = ?)
            """
            params = (user_id, user_id)
        else:
            # Limited metrics for other roles
            return {'message': 'Limited access'}
        
        cursor = db.cursor()
        cursor.execute(query, params if user_role == 'manager' else ())
        metrics = dict(cursor.fetchone())
        
        db.close()
        return metrics
    
    def _enhance_with_locations(self, fleet_data):
        """Enhance fleet data with geocoded locations"""
        enhanced_devices = []
        
        for device in fleet_data.get('devices', []):
            if device.get('address') and not device.get('latitude'):
                # Geocode address
                lat, lon = self.geocoder.geocode_address(device['address'])
                if lat and lon:
                    device['latitude'] = lat
                    device['longitude'] = lon
            
            enhanced_devices.append(device)
        
        fleet_data['devices'] = enhanced_devices
        return fleet_data

@app.route('/api/dashboard/aggregate')
@require_auth
def get_aggregated_dashboard():
    """API endpoint for aggregated dashboard data"""
    try:
        aggregator = ServiceAggregator(DATABASE)
        
        # Initialize external services if available
        if os.environ.get('ENABLE_GEOCODING', 'false').lower() == 'true':
            aggregator.geocoder = geocode_address
        
        user_role = g.current_user['role']
        user_id = g.current_user['user_id']
        
        dashboard_data = aggregator.get_dashboard_data(user_id, user_role)
        
        return jsonify({
            'success': True,
            'data': dashboard_data,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

## Data Synchronization Patterns

### Batch Synchronization Pattern

```python
import threading
from queue import Queue
from datetime import datetime

class DataSyncManager:
    """Manage data synchronization with external systems"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.sync_queue = Queue()
        self.sync_workers = []
        self.is_running = False
        
        # Sync configurations
        self.sync_configs = {
            'sales_data': {
                'batch_size': 100,
                'frequency': 300,  # 5 minutes
                'endpoint': '/api/external/sales',
                'retry_count': 3
            },
            'device_status': {
                'batch_size': 50,
                'frequency': 600,  # 10 minutes
                'endpoint': '/api/external/devices',
                'retry_count': 2
            }
        }
    
    def start_sync_workers(self, worker_count=2):
        """Start background sync worker threads"""
        self.is_running = True
        
        for i in range(worker_count):
            worker = threading.Thread(
                target=self._sync_worker,
                name=f"SyncWorker-{i}",
                daemon=True
            )
            worker.start()
            self.sync_workers.append(worker)
        
        print(f"Started {worker_count} sync workers")
    
    def _sync_worker(self):
        """Background worker for processing sync tasks"""
        while self.is_running:
            try:
                # Get sync task from queue (blocks until available)
                sync_task = self.sync_queue.get(timeout=30)
                
                if sync_task:
                    self._process_sync_task(sync_task)
                    
            except Queue.Empty:
                continue
            except Exception as e:
                print(f"Sync worker error: {e}")
    
    def _process_sync_task(self, task):
        """Process individual sync task"""
        try:
            sync_type = task['type']
            config = self.sync_configs.get(sync_type)
            
            if not config:
                print(f"Unknown sync type: {sync_type}")
                return
            
            # Get data to sync
            data_batch = self._get_sync_data(sync_type, config['batch_size'])
            
            if data_batch:
                # Send to external system
                success = self._send_sync_data(data_batch, config)
                
                if success:
                    self._mark_synced(data_batch, sync_type)
                else:
                    self._handle_sync_failure(task)
            
        except Exception as e:
            print(f"Sync task processing error: {e}")
        finally:
            self.sync_queue.task_done()
    
    def _get_sync_data(self, sync_type, batch_size):
        """Get data that needs to be synced"""
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        
        if sync_type == 'sales_data':
            query = """
            SELECT * FROM sales 
            WHERE sync_status IS NULL OR sync_status = 'pending'
            ORDER BY created_at ASC
            LIMIT ?
            """
        elif sync_type == 'device_status':
            query = """
            SELECT d.*, dm.* FROM devices d
            LEFT JOIN device_metrics dm ON d.id = dm.device_id
            WHERE d.sync_status IS NULL OR d.sync_status = 'pending'
            LIMIT ?
            """
        else:
            return []
        
        cursor = db.cursor()
        cursor.execute(query, (batch_size,))
        results = [dict(row) for row in cursor.fetchall()]
        
        db.close()
        return results
    
    def _send_sync_data(self, data_batch, config):
        """Send data to external system"""
        try:
            # Prepare payload
            payload = {
                'timestamp': datetime.now().isoformat(),
                'batch_id': f"batch_{int(datetime.now().timestamp())}",
                'data': data_batch
            }
            
            # Send HTTP request
            response = requests.post(
                config['endpoint'],
                json=payload,
                timeout=30,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f"Bearer {os.environ.get('SYNC_API_KEY')}"
                }
            )
            
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"Sync send error: {e}")
            return False
    
    def schedule_sync(self, sync_type):
        """Schedule a sync task"""
        task = {
            'type': sync_type,
            'created_at': datetime.now(),
            'retry_count': 0
        }
        
        self.sync_queue.put(task)
    
    def stop_sync_workers(self):
        """Stop all sync workers"""
        self.is_running = False
        
        # Wait for workers to finish
        for worker in self.sync_workers:
            worker.join(timeout=5)
        
        print("Sync workers stopped")

# Usage
sync_manager = DataSyncManager(DATABASE)
sync_manager.start_sync_workers()

# Schedule periodic syncs
import schedule

schedule.every(5).minutes.do(lambda: sync_manager.schedule_sync('sales_data'))
schedule.every(10).minutes.do(lambda: sync_manager.schedule_sync('device_status'))
```

## Event-Driven Integration

### Webhook Integration Pattern

```python
from flask import request
import hmac
import hashlib

class WebhookHandler:
    """Handle incoming webhooks from external systems"""
    
    def __init__(self, app, db_path):
        self.app = app
        self.db_path = db_path
        self.webhook_secrets = {
            'payment_processor': os.environ.get('PAYMENT_WEBHOOK_SECRET'),
            'device_monitor': os.environ.get('DEVICE_WEBHOOK_SECRET')
        }
        
        self.setup_webhook_routes()
    
    def setup_webhook_routes(self):
        """Setup webhook endpoints"""
        
        @self.app.route('/webhooks/payments', methods=['POST'])
        def handle_payment_webhook():
            return self._handle_webhook('payment_processor', self._process_payment_event)
        
        @self.app.route('/webhooks/devices', methods=['POST'])
        def handle_device_webhook():
            return self._handle_webhook('device_monitor', self._process_device_event)
    
    def _handle_webhook(self, source, processor_func):
        """Generic webhook handler with signature verification"""
        try:
            # Verify webhook signature
            if not self._verify_signature(source, request.data, request.headers):
                return jsonify({'error': 'Invalid signature'}), 403
            
            # Parse payload
            payload = request.json
            if not payload:
                return jsonify({'error': 'Invalid payload'}), 400
            
            # Process event
            result = processor_func(payload)
            
            if result['success']:
                return jsonify({'status': 'processed'}), 200
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            print(f"Webhook processing error: {e}")
            return jsonify({'error': 'Internal error'}), 500
    
    def _verify_signature(self, source, payload, headers):
        """Verify webhook signature"""
        secret = self.webhook_secrets.get(source)
        if not secret:
            return False
        
        signature_header = headers.get('X-Signature-256') or headers.get('X-Hub-Signature-256')
        if not signature_header:
            return False
        
        # Calculate expected signature
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        provided_signature = signature_header.replace('sha256=', '')
        return hmac.compare_digest(expected_signature, provided_signature)
    
    def _process_payment_event(self, payload):
        """Process payment webhook event"""
        try:
            event_type = payload.get('type')
            event_data = payload.get('data', {})
            
            if event_type == 'payment.completed':
                return self._handle_payment_completed(event_data)
            elif event_type == 'payment.failed':
                return self._handle_payment_failed(event_data)
            else:
                return {'success': False, 'error': f'Unknown event type: {event_type}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_payment_completed(self, event_data):
        """Handle completed payment event"""
        db = sqlite3.connect(self.db_path)
        
        try:
            transaction_id = event_data.get('transaction_id')
            device_id = event_data.get('device_id')
            amount = event_data.get('amount')
            products = event_data.get('products', [])
            
            # Create sales records
            cursor = db.cursor()
            
            for product in products:
                cursor.execute('''
                    INSERT INTO sales 
                    (device_id, product_id, sale_units, sale_cash, transaction_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (device_id, product['id'], product['quantity'], 
                      product['total'], transaction_id, datetime.now()))
            
            db.commit()
            
            # Trigger inventory update
            self._update_device_inventory(device_id, products)
            
            return {'success': True}
            
        except Exception as e:
            db.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            db.close()
```

## Caching and Performance Patterns

### Multi-Level Caching Pattern

```python
import redis
import pickle
from functools import wraps

class CacheManager:
    """Multi-level caching with Redis and in-memory fallback"""
    
    def __init__(self, redis_url=None):
        # Redis cache (L1)
        try:
            self.redis_client = redis.from_url(redis_url) if redis_url else None
            if self.redis_client:
                self.redis_client.ping()  # Test connection
        except:
            self.redis_client = None
        
        # In-memory cache (L2)
        self.memory_cache = {}
        self.memory_cache_ttl = {}
        
    def get(self, key):
        """Get value from cache (try Redis first, then memory)"""
        # Try Redis first
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value is not None:
                    return pickle.loads(value)
            except Exception as e:
                print(f"Redis get error: {e}")
        
        # Fallback to memory cache
        if key in self.memory_cache:
            # Check TTL
            if key in self.memory_cache_ttl:
                if time.time() > self.memory_cache_ttl[key]:
                    del self.memory_cache[key]
                    del self.memory_cache_ttl[key]
                    return None
            
            return self.memory_cache[key]
        
        return None
    
    def set(self, key, value, ttl=3600):
        """Set value in cache"""
        # Set in Redis
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key, 
                    ttl, 
                    pickle.dumps(value)
                )
            except Exception as e:
                print(f"Redis set error: {e}")
        
        # Set in memory cache as fallback
        self.memory_cache[key] = value
        self.memory_cache_ttl[key] = time.time() + ttl
        
        # Cleanup old memory cache entries occasionally
        if len(self.memory_cache) > 1000:
            self._cleanup_memory_cache()
    
    def delete(self, key):
        """Delete from cache"""
        # Delete from Redis
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                print(f"Redis delete error: {e}")
        
        # Delete from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
        if key in self.memory_cache_ttl:
            del self.memory_cache_ttl[key]
    
    def _cleanup_memory_cache(self):
        """Clean up expired memory cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, expiry in self.memory_cache_ttl.items()
            if current_time > expiry
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
            del self.memory_cache_ttl[key]

# Cache decorator
cache_manager = CacheManager(os.environ.get('REDIS_URL'))

def cached(ttl=3600, key_prefix=''):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Usage examples
@cached(ttl=1800, key_prefix='device_metrics:')
def get_device_metrics(device_id):
    """Cached device metrics retrieval"""
    # Expensive database query
    return calculate_device_performance(device_id)

@cached(ttl=3600, key_prefix='geocode:')
def geocode_address_cached(address):
    """Cached geocoding to avoid API rate limits"""
    return geocode_address(address)
```

## Error Handling and Resilience

### Circuit Breaker Pattern

```python
import time
from enum import Enum

class CircuitBreakerState(Enum):
    CLOSED = 1      # Normal operation
    OPEN = 2        # Circuit open, failing fast
    HALF_OPEN = 3   # Testing if service is back

class CircuitBreaker:
    """Circuit breaker for external service calls"""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60, expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self):
        """Check if enough time has passed to attempt reset"""
        return (
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

# Usage with external services
geocoding_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=300,  # 5 minutes
    expected_exception=requests.exceptions.RequestException
)

ai_service_breaker = CircuitBreaker(
    failure_threshold=2,
    recovery_timeout=600,  # 10 minutes
    expected_exception=Exception
)

def safe_geocode_address(address):
    """Geocode with circuit breaker protection"""
    try:
        return geocoding_breaker.call(geocode_address, address)
    except Exception as e:
        print(f"Geocoding circuit breaker triggered: {e}")
        return None, None

def safe_ai_optimization(device_id, cabinet_index):
    """AI optimization with circuit breaker protection"""
    try:
        return ai_service_breaker.call(
            lambda: optimizer.optimize_planogram(device_id, cabinet_index)
        )
    except Exception as e:
        print(f"AI service circuit breaker triggered: {e}")
        return None
```

## Implementation Guidelines

### Integration Implementation Checklist

- [ ] **Service Discovery**: Proper service endpoint configuration
- [ ] **Authentication**: Secure API key and token management
- [ ] **Error Handling**: Comprehensive error handling and fallbacks
- [ ] **Rate Limiting**: Respect external service rate limits
- [ ] **Caching**: Implement appropriate caching strategies
- [ ] **Monitoring**: Integration health monitoring and alerting
- [ ] **Testing**: Integration tests with mocked external services
- [ ] **Documentation**: Clear integration documentation
- [ ] **Security**: Secure credential storage and transmission

### Best Practices

1. **Fail Gracefully**: Always have fallback strategies for external service failures
2. **Cache Strategically**: Cache external service responses to reduce dependency
3. **Monitor Actively**: Monitor integration health and performance metrics
4. **Test Thoroughly**: Test integration scenarios including failure cases
5. **Secure Properly**: Use secure authentication and encrypt sensitive data
6. **Document Clearly**: Maintain clear documentation for all integrations
7. **Version Carefully**: Handle API versioning and backward compatibility

## Related Documentation

- [API Patterns](./API_PATTERNS.md) - Internal API design patterns
- [Security Patterns](./SECURITY_PATTERNS.md) - Integration security
- [Frontend Patterns](./FRONTEND_PATTERNS.md) - Client-side integration
- [Performance Optimization](../BEST_PRACTICES.md) - Performance best practices

## References

- Enterprise Integration Patterns
- Microservices Integration Strategies
- API Gateway Patterns
- Circuit Breaker Pattern
- Event-Driven Architecture Patterns