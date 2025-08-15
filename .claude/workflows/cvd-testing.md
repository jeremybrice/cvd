# CVD Testing Workflow with QA Test Engineer

This workflow integrates the qa-test-engineer agent with CVD-specific testing needs.

## Test Categories for CVD

### 1. Service Order Testing
```python
# Test Suite: Service Orders
tests = [
    "test_order_creation_with_multiple_cabinets",
    "test_pick_list_generation_accuracy",
    "test_par_level_calculations",
    "test_driver_assignment_logic",
    "test_order_execution_workflow",
    "test_photo_upload_verification",
    "test_offline_order_sync"
]

# Critical Paths
- Order creation → Pick list → Assignment → Execution → Completion
- Offline creation → Queue → Sync → Server update
- Photo capture → Upload → Verification → Storage
```

### 2. Planogram Testing
```python
# Test Suite: Planogram Management
tests = [
    "test_drag_drop_product_placement",
    "test_slot_capacity_validation",
    "test_temperature_zone_constraints",
    "test_ai_optimization_recommendations",
    "test_par_level_updates",
    "test_multi_cabinet_planogram",
    "test_product_catalog_integration"
]

# Edge Cases
- Empty planogram initialization
- Moving products between temperature zones
- Handling discontinued products
- Slot dimension mismatches
```

### 3. DEX Parser Testing
```python
# Test Suite: DEX File Processing
tests = [
    "test_dex_format_validation",
    "test_grid_pattern_detection_accuracy",
    "test_multi_manufacturer_support",
    "test_corrupt_file_handling",
    "test_duplicate_record_detection",
    "test_sales_data_extraction",
    "test_cash_accounting_reconciliation"
]

# Test Data
- Use files from: /home/jbrice/Projects/365/docs/examples/dex files/
- Test each manufacturer format
- Include malformed files for error testing
```

### 4. PWA Testing
```javascript
// Test Suite: Driver PWA
tests = [
    "test_offline_mode_activation",
    "test_indexeddb_storage",
    "test_background_sync_queue",
    "test_push_notification_receipt",
    "test_gps_tracking_accuracy",
    "test_photo_capture_quality",
    "test_service_worker_caching"
]

// Test Scenarios
- No network → Offline mode → Network restore → Sync
- Background app → Push notification → App activation
- Multiple photos → Queue → Batch upload
```

## Testing Workflow Commands

### Run Comprehensive Test Suite
```bash
# Activate QA Test Engineer
@qa-test-engineer run comprehensive test suite for CVD

# The agent will:
1. Run Python backend tests: pytest tests/
2. Check API endpoints with test client
3. Validate database integrity
4. Test frontend interactions
5. Verify PWA functionality
6. Generate test report
```

### Test Specific Feature
```bash
# Test service order workflow
@qa-test-engineer test service order creation and execution flow

# Test planogram optimization
@qa-test-engineer verify planogram AI optimization with test data

# Test DEX parser
@qa-test-engineer validate DEX parser with all sample files
```

### Performance Testing
```bash
# Load testing
@qa-test-engineer perform load test with 100 concurrent users

# Optimization verification
@qa-test-engineer benchmark planogram optimization performance

# PWA performance
@qa-test-engineer test PWA performance on slow 3G connection
```

## Test Data Management

### Setup Test Database
```python
# Create test fixtures
fixtures = {
    'devices': create_test_devices(50),
    'products': load_product_catalog(),
    'users': create_test_users(['admin', 'manager', 'driver']),
    'orders': generate_test_orders(100),
    'sales': generate_sales_data(30_days)
}

# Reset to known state
def reset_test_db():
    restore_from_snapshot('test_baseline.db')
    apply_fixtures(fixtures)
```

### Test Data Scenarios

#### Scenario 1: High Volume Operations
```python
# Generate stress test data
create_devices(1000)
create_service_orders(500)
create_planograms(1000)
simulate_concurrent_users(50)
```

#### Scenario 2: Edge Cases
```python
# Boundary conditions
test_empty_planogram()
test_max_cabinet_capacity()
test_zero_inventory()
test_expired_products()
test_offline_for_24_hours()
```

#### Scenario 3: Real-World Simulation
```python
# Realistic usage patterns
simulate_daily_operations()
simulate_route_completion()
simulate_planogram_updates()
simulate_sales_reporting()
```

## Integration with CI/CD

### Pre-Commit Tests
```yaml
# Quick tests before commit
pre-commit:
  - pytest tests/unit/ --quick
  - check_api_contracts()
  - validate_schema_migrations()
```

### Pull Request Tests
```yaml
# Comprehensive tests for PR
pull-request:
  - pytest tests/ --full
  - test_frontend_integration()
  - test_pwa_functionality()
  - security_scan()
```

### Deployment Tests
```yaml
# Production readiness
deployment:
  - smoke_tests()
  - performance_benchmarks()
  - rollback_verification()
  - monitoring_setup()
```

## Test Report Template

```markdown
## CVD Test Report - [Date]

### Summary
- Total Tests: X
- Passed: X
- Failed: X
- Skipped: X
- Coverage: X%

### Backend Tests
- ✅ Authentication/Authorization
- ✅ Service Order Management
- ✅ Planogram Operations
- ⚠️ DEX Parser (1 edge case)
- ✅ Database Operations

### Frontend Tests
- ✅ Navigation
- ✅ API Integration
- ✅ Drag-Drop Functionality
- ✅ Form Validation
- ✅ Error Handling

### PWA Tests
- ✅ Offline Mode
- ✅ Background Sync
- ⚠️ Push Notifications (iOS limited)
- ✅ IndexedDB Storage
- ✅ Service Worker

### Performance
- API Response: <200ms (avg)
- Page Load: <2s
- PWA Startup: <1s
- Database Queries: <50ms

### Security
- ✅ SQL Injection: Protected
- ✅ XSS: Sanitized
- ✅ CSRF: Token Validated
- ✅ Auth: Session Secured

### Recommendations
1. [Priority fixes]
2. [Performance improvements]
3. [Security enhancements]
```

## QA Agent Integration Commands

### Daily Testing Routine
```bash
# Morning validation
@qa-test-engineer run morning smoke tests

# After deployment
@qa-test-engineer verify deployment success

# Before major changes
@qa-test-engineer create baseline snapshot
```

### Issue Investigation
```bash
# Debug failing test
@qa-test-engineer investigate failing test: test_service_order_creation

# Reproduce user issue
@qa-test-engineer reproduce issue: "cannot save planogram"

# Performance regression
@qa-test-engineer compare performance with baseline
```