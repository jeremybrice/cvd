# AI Planogram Integration Test Plan

## Executive Summary

This document provides comprehensive integration test scenarios, test data specifications, and performance benchmarks for the AI Planogram Enhancement System. All tests ensure end-to-end functionality across API endpoints, database operations, and AI service integrations.

## 1. Test Environment Setup

### Required Services
```yaml
test_environment:
  database: SQLite (test instance)
  cache: Redis 7.0
  api: Flask application (test mode)
  ai_services:
    - Claude API (test key with limited quota)
    - Mock services for expensive operations
  
  test_data:
    devices: 5 test devices
    products: 50 test products
    users: 10 test users (various roles)
    historical_sales: 90 days synthetic data
```

### Environment Variables
```bash
# Test environment configuration
export FLASK_ENV=testing
export DATABASE_URL=sqlite:///cvd_test.db
export REDIS_URL=redis://localhost:6379/1
export ANTHROPIC_API_KEY=test_sk_ant_xxxxx
export AI_USE_MOCK=true  # Use mock for expensive AI calls
export TEST_DATA_SEED=42  # Consistent test data generation
```

## 2. Integration Test Scenarios

### Scenario 1: Real-Time Placement Scoring Flow

#### Test ID: INT-001
**Description**: End-to-end test of product placement scoring

**Test Steps**:
```python
def test_realtime_placement_scoring():
    # 1. Setup: Create test planogram
    device_id = create_test_device()
    planogram_id = create_test_planogram(device_id)
    
    # 2. Action: Request placement score
    response = api.post('/api/planograms/realtime/score', json={
        'product_id': 5,  # Coca-Cola
        'slot_position': 'B3',
        'device_id': device_id,
        'cabinet_index': 0
    })
    
    # 3. Verify: Response structure
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data['score'] <= 100
    assert 'reasoning' in data
    assert data['response_time_ms'] < 500
    
    # 4. Verify: Cache creation
    cache_key = f"score:{device_id}:5:B3"
    cached = redis.get(cache_key)
    assert cached is not None
    
    # 5. Verify: Database logging
    prediction = db.query(
        "SELECT * FROM ai_predictions WHERE planogram_id = %s",
        [planogram_id]
    )
    assert len(prediction) == 1
```

**Expected Results**:
- Response time < 500ms
- Score between 0-100
- Cache entry created
- Prediction logged to database

---

### Scenario 2: Revenue Prediction with Historical Data

#### Test ID: INT-002
**Description**: Test revenue prediction using historical sales data

**Test Steps**:
```python
def test_revenue_prediction_with_history():
    # 1. Setup: Create device with sales history
    device_id = create_device_with_sales_history(days=90)
    current = create_planogram(device_id, layout='standard')
    proposed = create_planogram(device_id, layout='optimized')
    
    # 2. Action: Request revenue prediction
    response = api.post('/api/planograms/predict/revenue', json={
        'current_planogram': serialize_planogram(current),
        'proposed_planogram': serialize_planogram(proposed),
        'forecast_days': 30
    })
    
    # 3. Verify: Prediction logic
    assert response.status_code == 200
    data = response.json()
    assert data['baseline_revenue'] > 0
    assert data['predicted_revenue'] > 0
    assert -50 <= data['lift_percentage'] <= 100
    
    # 4. Verify: Confidence intervals
    assert data['confidence_interval']['lower'] <= data['predicted_revenue']
    assert data['confidence_interval']['upper'] >= data['predicted_revenue']
    
    # 5. Verify: Factors provided
    assert len(data['factors']) > 0
    total_impact = sum(f['impact'] for f in data['factors'])
    assert abs(total_impact - data['lift_percentage']) < 1.0
```

**Expected Results**:
- Valid revenue predictions
- Confidence intervals contain prediction
- Factors sum to total lift

---

### Scenario 3: Heat Zone Calculation and Caching

#### Test ID: INT-003
**Description**: Test heat zone generation and 24-hour caching

**Test Steps**:
```python
def test_heat_zone_caching():
    # 1. Setup: Create device with performance data
    device_id = create_device_with_performance_data()
    
    # 2. Action: First request (cache miss)
    start = time.time()
    response1 = api.get(f'/api/planograms/optimize/heat-zones?device_id={device_id}')
    time1 = time.time() - start
    
    # 3. Verify: Zone data structure
    assert response1.status_code == 200
    zones = response1.json()['zones']
    assert len(zones) > 0
    for zone in zones:
        assert 0 <= zone['revenue_potential'] <= 100
        assert 1 <= zone['level'] <= 5
        assert zone['color'].startswith('#')
    
    # 4. Action: Second request (cache hit)
    start = time.time()
    response2 = api.get(f'/api/planograms/optimize/heat-zones?device_id={device_id}')
    time2 = time.time() - start
    
    # 5. Verify: Cache performance
    assert time2 < time1 * 0.1  # 10x faster from cache
    assert response1.json() == response2.json()  # Same data
    
    # 6. Verify: Cache TTL
    cache_key = f"zones:{device_id}:0"
    ttl = redis.ttl(cache_key)
    assert 86000 < ttl <= 86400  # ~24 hours
```

**Expected Results**:
- First request generates zones
- Second request 10x faster (from cache)
- Cache TTL set to 24 hours

---

### Scenario 4: Product Affinity Analysis

#### Test ID: INT-004
**Description**: Test product affinity recommendations

**Test Steps**:
```python
def test_product_affinity_recommendations():
    # 1. Setup: Create sales data with co-purchases
    create_copurchase_data([
        {'products': [1, 5], 'count': 100},  # Chips & Soda
        {'products': [1, 8], 'count': 80},   # Chips & Candy
        {'products': [5, 12], 'count': 60}   # Soda & Water
    ])
    
    # 2. Action: Request affinity for chips
    response = api.post('/api/planograms/optimize/affinity', json={
        'product_id': 1,  # Chips
        'device_id': test_device_id,
        'max_results': 3
    })
    
    # 3. Verify: Recommendations ordered by affinity
    assert response.status_code == 200
    recommendations = response.json()['recommendations']
    assert len(recommendations) <= 3
    
    # Verify ordering
    scores = [r['affinity_score'] for r in recommendations]
    assert scores == sorted(scores, reverse=True)
    
    # 4. Verify: Expected products recommended
    product_ids = [r['product_id'] for r in recommendations]
    assert 5 in product_ids  # Soda should be recommended
    
    # 5. Verify: Suggested positions provided
    for rec in recommendations:
        assert len(rec['suggested_positions']) > 0
```

**Expected Results**:
- Top affinity products returned
- Ordered by affinity score
- Includes placement suggestions

---

### Scenario 5: Demand Forecasting Accuracy

#### Test ID: INT-005
**Description**: Test demand forecast with known patterns

**Test Steps**:
```python
def test_demand_forecast_accuracy():
    # 1. Setup: Create predictable sales pattern
    device_id = create_device_with_pattern({
        'weekday_sales': 10,
        'weekend_sales': 20,
        'product_id': 5
    })
    
    # 2. Action: Request 7-day forecast
    response = api.post('/api/planograms/predict/demand', json={
        'device_id': device_id,
        'products': [5],
        'forecast_days': 7
    })
    
    # 3. Verify: Forecast reflects pattern
    assert response.status_code == 200
    forecast = response.json()['forecasts'][0]
    daily = forecast['daily_forecast']
    
    for day in daily:
        date = datetime.strptime(day['date'], '%Y-%m-%d')
        if date.weekday() < 5:  # Weekday
            assert 8 <= day['predicted_units'] <= 12
        else:  # Weekend
            assert 18 <= day['predicted_units'] <= 22
    
    # 4. Verify: Confidence intervals
    for day in daily:
        assert day['confidence_lower'] <= day['predicted_units']
        assert day['confidence_upper'] >= day['predicted_units']
    
    # 5. Verify: Stock risk assessment
    assert forecast['stockout_risk'] in ['LOW', 'MEDIUM', 'HIGH']
    assert forecast['suggested_par_level'] > max(d['predicted_units'] for d in daily)
```

**Expected Results**:
- Forecast matches known pattern
- Confidence intervals are reasonable
- Par level prevents stockouts

---

### Scenario 6: Location-Based Optimization

#### Test ID: INT-006
**Description**: Test location-specific recommendations

**Test Steps**:
```python
def test_location_optimization():
    # 1. Setup: Create devices in different venues
    office_device = create_device(location_type='OFFICE')
    gym_device = create_device(location_type='GYM')
    
    # 2. Action: Get recommendations for each
    office_response = api.post('/api/planograms/optimize/location', json={
        'device_id': office_device,
        'location_id': 1
    })
    
    gym_response = api.post('/api/planograms/optimize/location', json={
        'device_id': gym_device,
        'location_id': 2,
        'venue_type_override': 'GYM'
    })
    
    # 3. Verify: Different recommendations
    office_recs = office_response.json()['recommendations']
    gym_recs = gym_response.json()['recommendations']
    
    # Office should recommend coffee/snacks
    office_products = [r['recommended_product_id'] for r in office_recs]
    assert any(p in office_products for p in COFFEE_PRODUCTS)
    
    # Gym should recommend protein/sports drinks
    gym_products = [r['recommended_product_id'] for r in gym_recs]
    assert any(p in gym_products for p in PROTEIN_PRODUCTS)
    
    # 4. Verify: Confidence scores
    assert 0 <= office_response.json()['confidence_score'] <= 100
    assert 0 <= gym_response.json()['confidence_score'] <= 100
```

**Expected Results**:
- Office recommends coffee/snacks
- Gym recommends protein/sports drinks
- Valid confidence scores

---

### Scenario 7: Concurrent Request Handling

#### Test ID: INT-007
**Description**: Test system under concurrent load

**Test Steps**:
```python
def test_concurrent_request_handling():
    import concurrent.futures
    import statistics
    
    # 1. Setup: Prepare test data
    device_ids = [create_test_device() for _ in range(5)]
    
    # 2. Action: Send concurrent requests
    def make_request(device_id):
        start = time.time()
        response = api.post('/api/planograms/realtime/score', json={
            'product_id': random.randint(1, 50),
            'slot_position': f"{random.choice('ABCDE')}{random.randint(1,10)}",
            'device_id': device_id
        })
        elapsed = time.time() - start
        return response.status_code, elapsed
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_request, random.choice(device_ids)) 
                  for _ in range(100)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    # 3. Verify: All requests successful
    status_codes = [r[0] for r in results]
    assert all(code == 200 for code in status_codes)
    
    # 4. Verify: Response times acceptable
    response_times = [r[1] for r in results]
    assert statistics.mean(response_times) < 1.0  # Average < 1s
    assert statistics.quantiles(response_times, n=100)[94] < 2.0  # p95 < 2s
    
    # 5. Verify: Database operations complete successfully
    # SQLite uses file-based storage with automatic connection management
    # Verify database is accessible and responsive
```

**Expected Results**:
- All requests succeed
- Average response < 1s
- p95 response < 2s
- Connection pool effective

---

### Scenario 8: Error Handling and Recovery

#### Test ID: INT-008
**Description**: Test error handling and graceful degradation

**Test Steps**:
```python
def test_error_handling():
    # 1. Test: Invalid input handling
    response = api.post('/api/planograms/realtime/score', json={
        'product_id': -1,  # Invalid
        'slot_position': 'ZZ99',  # Invalid format
        'device_id': 999999  # Non-existent
    })
    assert response.status_code == 400
    assert 'error' in response.json()
    
    # 2. Test: Rate limiting
    for i in range(150):  # Exceed rate limit
        api.post('/api/planograms/realtime/score', json=valid_request)
    
    response = api.post('/api/planograms/realtime/score', json=valid_request)
    assert response.status_code == 429
    assert 'X-RateLimit-Reset' in response.headers
    
    # 3. Test: AI service failure handling
    with mock.patch('ai_services.claude_client.complete') as mock_ai:
        mock_ai.side_effect = Exception("AI service down")
        
        response = api.post('/api/planograms/predict/revenue', json=valid_request)
        assert response.status_code == 503
        
        # Verify fallback to cache if available
        cached_response = api.get(f'/api/planograms/optimize/heat-zones?device_id=1')
        assert cached_response.status_code == 200  # Still works from cache
    
    # 4. Test: Database failure recovery
    with mock.patch('database.execute') as mock_db:
        mock_db.side_effect = Exception("Database connection lost")
        
        # Should return error but not crash
        response = api.post('/api/planograms/realtime/score', json=valid_request)
        assert response.status_code == 500
        assert 'request_id' in response.json()  # For debugging
```

**Expected Results**:
- Invalid input returns 400
- Rate limiting returns 429
- AI failure returns 503
- Database errors handled gracefully

## 3. Performance Benchmarks

### Response Time Requirements

| Endpoint | p50 Target | p95 Target | p99 Target |
|----------|------------|------------|------------|
| `/realtime/score` | 200ms | 450ms | 490ms |
| `/predict/revenue` | 2s | 6s | 8s |
| `/optimize/heat-zones` | 100ms | 300ms | 500ms |
| `/optimize/affinity` | 500ms | 1s | 2s |
| `/predict/demand` | 1s | 3s | 5s |
| `/optimize/location` | 3s | 7s | 10s |

### Load Testing Scenarios

```yaml
load_test_scenarios:
  normal_load:
    users: 50
    duration: 10m
    requests_per_user: 10
    
  peak_load:
    users: 200
    duration: 5m
    requests_per_user: 20
    
  stress_test:
    users: 500
    duration: 2m
    requests_per_user: 50
```

## 4. Test Data Specifications

### Synthetic Data Generation

```python
class TestDataGenerator:
    def generate_sales_history(self, device_id, days=90):
        """Generate realistic sales patterns"""
        base_sales = {
            'weekday': {'mean': 50, 'std': 10},
            'weekend': {'mean': 80, 'std': 15}
        }
        
        sales = []
        for day in range(days):
            date = datetime.now() - timedelta(days=day)
            is_weekend = date.weekday() >= 5
            
            daily_sales = random.gauss(
                base_sales['weekend' if is_weekend else 'weekday']['mean'],
                base_sales['weekend' if is_weekend else 'weekday']['std']
            )
            
            # Distribute across products
            for product_id in range(1, 20):
                if random.random() < 0.7:  # 70% chance of sale
                    sales.append({
                        'device_id': device_id,
                        'product_id': product_id,
                        'quantity': max(1, int(random.gauss(3, 1))),
                        'price': PRODUCT_PRICES[product_id],
                        'transaction_date': date
                    })
        
        return sales
```

### Test Fixtures

```sql
-- Test devices
INSERT INTO devices (asset, serial_number, location_id) VALUES
('TEST-VM-001', 'TST001', 1),
('TEST-VM-002', 'TST002', 2),
('TEST-VM-003', 'TST003', 3),
('TEST-VM-004', 'TST004', 4),
('TEST-VM-005', 'TST005', 5);

-- Test products (subset of real products)
INSERT INTO products (id, name, category, price) VALUES
(1, 'Test Chips', 'Snacks', 2.00),
(5, 'Test Cola', 'Beverages', 2.50),
(8, 'Test Candy', 'Candy', 1.50),
(12, 'Test Water', 'Beverages', 2.00),
(15, 'Test Protein Bar', 'Health', 3.50);

-- Test users with different roles
INSERT INTO users (username, role) VALUES
('test_admin', 'Admin'),
('test_manager', 'Manager'),
('test_driver', 'Driver'),
('test_viewer', 'Viewer');
```

## 5. CI/CD Integration

### GitHub Actions Workflow

```yaml
name: AI Integration Tests

on:
  pull_request:
    paths:
      - 'ai_services/**'
      - 'api/**'
      - 'tests/**'

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    # SQLite used for testing - no external services needed
    # Database file created automatically during test setup
          --health-timeout 5s
          --health-retries 5
          
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-ai.txt
          pip install pytest pytest-cov
          
      - name: Setup test database
        run: |
          python tools/setup_test_db.py
          python tools/generate_test_data.py
          
      - name: Run integration tests
        env:
          AI_USE_MOCK: true
        run: |
          pytest tests/integration/ -v --cov=ai_services --cov-report=xml
          
      - name: Run performance tests
        run: |
          pytest tests/performance/ -v --benchmark-only
          
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## 6. Test Execution Schedule

| Test Suite | Frequency | Trigger | Duration |
|------------|-----------|---------|----------|
| Unit Tests | Every commit | Push | 2 min |
| Integration Tests | Every PR | Pull request | 10 min |
| Performance Tests | Daily | Scheduled | 30 min |
| Load Tests | Weekly | Manual/Scheduled | 1 hour |
| Full Regression | Before release | Tag creation | 2 hours |

## 7. Success Criteria

### Test Coverage
- Unit test coverage: >90%
- Integration test coverage: >80%
- Critical path coverage: 100%

### Performance Metrics
- All endpoints meet p95 targets
- System handles 200 concurrent users
- Cache hit rate >60%
- No memory leaks over 24-hour test

### Reliability Metrics
- Error rate <1%
- Recovery from failure <2 minutes
- Data consistency 100%
- No data loss during failures

---

Document Version: 1.0
Date: 2025
Status: Ready for Engineering Review