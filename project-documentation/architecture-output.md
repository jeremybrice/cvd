# Activity Monitor Enhancement - Technical Architecture Document

## Executive Summary

### Project Overview
Enhancement of the CVD Activity Monitor to replace the static Activity History search section with dynamic daily trends visualization while relocating user search functionality to a modal dialog. This improves screen utilization and provides immediate visual insights into system usage patterns.

### Key Architectural Decisions
- **Frontend Framework**: Vanilla JavaScript with Chart.js for visualization (consistent with existing CVD architecture)
- **Backend**: Flask REST API with SQLite (maintaining existing stack)
- **Data Architecture**: Leverage existing `activity_summary_daily` table with optimized aggregation queries
- **Caching Strategy**: Multi-layer caching with Redis-compatible in-memory store for trends data
- **Performance Target**: Sub-2 second initial load with 365 days of data

### Technology Stack Summary
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Visualization | Chart.js 4.x | Lightweight, accessible, no build step required |
| Backend API | Flask (existing) | Maintains consistency with current architecture |
| Database | SQLite | Existing system, proven scalability for use case |
| Caching | In-memory dict + TTL | Simple, effective for read-heavy workload |
| State Management | Session Storage | Client-side preference persistence |

### System Component Overview
```
┌─────────────────────────────────────────────────────┐
│                Activity Monitor Page                 │
├─────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────┐   │
│  │        Current Active Sessions              │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │        Daily Activity Trends Graph          │   │
│  │   - Multi-metric line chart                 │   │
│  │   - Date range selector                     │   │
│  │   - Export functionality                    │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │        User History Modal (Hidden)          │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Critical Technical Constraints and Assumptions
- SQLite database will handle aggregation queries efficiently with proper indexing
- Browser support for ES6+ features (current CVD requirement)
- Maximum 1000 concurrent admin users (based on enterprise deployment)
- 365-day data retention policy for activity summaries
- Network latency < 100ms for typical enterprise deployments

---

## For Backend Engineers

### API Endpoint Specifications

#### 1. GET /api/admin/activity/trends

**Purpose**: Retrieve aggregated daily activity trends for visualization

**Authentication**: Required (Admin role)

**Request Schema**:
```python
{
    "start_date": str,  # ISO format: "2025-07-14" (required)
    "end_date": str,    # ISO format: "2025-08-13" (required)
    "metrics": List[str],  # Optional: ["unique_users", "total_sessions", "total_page_views"]
    "interval": str,    # Default: "daily", Future: "hourly", "weekly"
    "cache_bypass": bool  # Optional: Force cache refresh (default: false)
}
```

**Response Schema**:
```python
{
    "success": bool,
    "data": {
        "period": {
            "start": str,  # ISO date
            "end": str     # ISO date
        },
        "metrics": {
            "unique_users": [
                {"date": str, "value": int},
                ...
            ],
            "total_sessions": [...],
            "total_page_views": [...],
            "total_api_calls": [...],
            "avg_session_duration_seconds": [...],
            "peak_concurrent_users": [...]
        },
        "summary": {
            "average_daily_users": float,
            "peak_day": str,
            "trend": str,  # "increasing" | "decreasing" | "stable"
            "trend_percentage": float  # Change percentage
        }
    },
    "cached": bool,
    "cache_ttl": int  # Seconds remaining
}
```

**Implementation Requirements**:
```python
@app.route('/api/admin/activity/trends', methods=['GET'])
@auth_manager.require_role(['admin'])
@cache_with_ttl(seconds=3600)  # 1-hour cache
def get_activity_trends():
    # Validate date range (max 365 days)
    # Query activity_summary_daily table
    # Calculate trend analysis
    # Return formatted response
```

#### 2. GET /api/admin/activity/export

**Purpose**: Export activity data in CSV/JSON format

**Request Schema**:
```python
{
    "start_date": str,
    "end_date": str,
    "format": str,  # "csv" | "json"
    "metrics": List[str],
    "include_raw": bool  # Include raw data points
}
```

**Response**: File download or JSON data

### Database Schema & Relationships

**Existing Table: activity_summary_daily**
```sql
-- Already exists, no migration needed
CREATE TABLE activity_summary_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    unique_users INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    total_page_views INTEGER DEFAULT 0,
    total_api_calls INTEGER DEFAULT 0,
    avg_session_duration_seconds INTEGER DEFAULT 0,
    peak_concurrent_users INTEGER DEFAULT 0,
    peak_hour INTEGER,
    top_pages TEXT,  -- JSON array
    user_distribution TEXT,  -- JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Required indexes for performance
CREATE INDEX idx_activity_summary_date_range 
ON activity_summary_daily(date DESC);

CREATE INDEX idx_activity_summary_metrics 
ON activity_summary_daily(date, unique_users, total_sessions);
```

### Business Logic Organization

**Module: activity_trends_service.py**
```python
class ActivityTrendsService:
    def __init__(self, db_path: str, cache_manager: CacheManager):
        self.db_path = db_path
        self.cache = cache_manager
        
    def get_trends(self, start_date: date, end_date: date, 
                   metrics: List[str]) -> Dict:
        """
        Main entry point for trends data
        1. Validate date range (max 365 days)
        2. Check cache for existing data
        3. Query database for missing periods
        4. Aggregate and format response
        5. Calculate trend analysis
        6. Update cache
        """
        
    def calculate_trend_direction(self, data_points: List) -> str:
        """
        Analyze trend using linear regression
        Returns: "increasing" | "decreasing" | "stable"
        """
        
    def aggregate_metrics(self, raw_data: List[Dict]) -> Dict:
        """
        Transform database rows into chart-ready format
        Groups by date and metric type
        """
```

### Authentication & Authorization Implementation

```python
# Middleware enhancement in activity_tracker.py
class ActivityTrendsMiddleware:
    @staticmethod
    def validate_admin_access(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user_role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def rate_limit(requests_per_minute: int = 100):
        # Implement token bucket algorithm
        # Store in session or Redis
```

### Error Handling & Validation Strategies

```python
class TrendsValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def validate_trends_request(request_data: Dict) -> Dict:
    """
    Validates and sanitizes request parameters
    
    Raises:
        TrendsValidationError: Invalid parameters
    
    Returns:
        Sanitized parameters dict
    """
    # Date range validation
    if (end_date - start_date).days > 365:
        raise TrendsValidationError("Date range exceeds 365 days")
    
    # Metrics validation
    valid_metrics = [
        'unique_users', 'total_sessions', 'total_page_views',
        'total_api_calls', 'avg_session_duration_seconds', 
        'peak_concurrent_users'
    ]
    
    # Return sanitized params
```

---

## For Frontend Engineers

### Component Architecture

**File Structure**:
```
pages/admin/
├── activity-monitor.html (modified)
├── js/
│   ├── activity-trends-chart.js (new)
│   ├── user-history-modal.js (new)
│   └── activity-monitor-state.js (new)
└── css/
    └── activity-monitor-enhanced.css (new)
```

### State Management Approach

```javascript
// activity-monitor-state.js
class ActivityMonitorState {
    constructor() {
        this.trends = {
            dateRange: { start: null, end: null },
            selectedMetrics: ['unique_users', 'total_sessions'],
            chartInstance: null,
            cachedData: null,
            lastFetch: null
        };
        
        this.modal = {
            isOpen: false,
            searchQuery: '',
            searchResults: [],
            currentPage: 1
        };
        
        this.preferences = this.loadPreferences();
    }
    
    loadPreferences() {
        return JSON.parse(sessionStorage.getItem('activity_preferences') || '{}');
    }
    
    savePreferences() {
        sessionStorage.setItem('activity_preferences', 
                              JSON.stringify(this.preferences));
    }
}
```

### API Integration Patterns

```javascript
// Enhanced api.js integration
class ActivityTrendsAPI extends CVDApi {
    async fetchTrends(startDate, endDate, metrics = null) {
        try {
            const params = new URLSearchParams({
                start_date: startDate,
                end_date: endDate,
                ...(metrics && { metrics: metrics.join(',') })
            });
            
            const response = await this.request(`/api/admin/activity/trends?${params}`, {
                method: 'GET',
                headers: this.getHeaders()
            });
            
            if (!response.success) {
                throw new Error(response.error || 'Failed to fetch trends');
            }
            
            return response.data;
        } catch (error) {
            console.error('Trends fetch error:', error);
            this.handleError(error);
            throw error;
        }
    }
    
    handleError(error) {
        // Graceful degradation
        if (error.status === 503) {
            // Show cached data if available
            return this.getCachedTrends();
        }
        // Display user-friendly error message
        this.showNotification('Unable to load trends. Please try again.', 'error');
    }
}
```

### Chart.js Implementation

```javascript
// activity-trends-chart.js
class ActivityTrendsChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.chart = null;
        this.config = this.getDefaultConfig();
    }
    
    getDefaultConfig() {
        return {
            type: 'line',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: this.formatTooltipLabel
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day',
                            displayFormats: {
                                day: 'MMM DD'
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: this.formatYAxisLabel
                        }
                    }
                }
            }
        };
    }
    
    updateChart(data, metrics) {
        const datasets = this.buildDatasets(data, metrics);
        
        if (!this.chart) {
            this.config.data.datasets = datasets;
            this.chart = new Chart(this.ctx, this.config);
        } else {
            this.chart.data.datasets = datasets;
            this.chart.update('active');  // Smooth animation
        }
    }
    
    buildDatasets(data, metrics) {
        const colors = {
            unique_users: 'rgb(54, 162, 235)',
            total_sessions: 'rgb(255, 99, 132)',
            total_page_views: 'rgb(75, 192, 192)',
            total_api_calls: 'rgb(255, 159, 64)'
        };
        
        return metrics.map(metric => ({
            label: this.formatMetricLabel(metric),
            data: data.metrics[metric].map(point => ({
                x: point.date,
                y: point.value
            })),
            borderColor: colors[metric],
            backgroundColor: colors[metric] + '20',
            tension: 0.1
        }));
    }
}
```

### Modal Component Implementation

```javascript
// user-history-modal.js
class UserHistoryModal {
    constructor() {
        this.modal = null;
        this.searchInput = null;
        this.resultsContainer = null;
        this.init();
    }
    
    init() {
        this.createModalHTML();
        this.attachEventListeners();
    }
    
    createModalHTML() {
        const modalHTML = `
            <div class="modal-overlay" id="userHistoryModalOverlay">
                <div class="modal-container" role="dialog" 
                     aria-labelledby="modalTitle" aria-modal="true">
                    <div class="modal-header">
                        <h2 id="modalTitle">User Activity History</h2>
                        <button class="modal-close" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="search-section">
                            <input type="text" 
                                   id="userSearchInput" 
                                   placeholder="Enter username..."
                                   aria-label="Search username">
                            <button class="btn btn-primary" id="searchBtn">
                                Search
                            </button>
                        </div>
                        <div id="searchResults" class="results-container">
                            <!-- Results rendered here -->
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    
    attachEventListeners() {
        // ESC key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen()) {
                this.close();
            }
        });
        
        // Click outside to close
        document.getElementById('userHistoryModalOverlay')
                .addEventListener('click', (e) => {
            if (e.target.id === 'userHistoryModalOverlay') {
                this.close();
            }
        });
    }
}
```

### Performance Optimization Strategies

```javascript
// Debounced resize handler for chart
const debouncedResize = debounce(() => {
    if (chart) {
        chart.resize();
    }
}, 250);

window.addEventListener('resize', debouncedResize);

// Virtual scrolling for large result sets in modal
class VirtualScroller {
    constructor(container, itemHeight, renderItem) {
        this.container = container;
        this.itemHeight = itemHeight;
        this.renderItem = renderItem;
        this.visibleItems = Math.ceil(container.clientHeight / itemHeight);
    }
    
    render(items) {
        const scrollTop = this.container.scrollTop;
        const startIndex = Math.floor(scrollTop / this.itemHeight);
        const endIndex = startIndex + this.visibleItems + 1;
        
        const visibleItems = items.slice(startIndex, endIndex);
        // Render only visible items
    }
}

// Intelligent data caching
class TrendsCache {
    constructor(maxAge = 3600000) { // 1 hour
        this.cache = new Map();
        this.maxAge = maxAge;
    }
    
    set(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }
    
    get(key) {
        const cached = this.cache.get(key);
        if (!cached) return null;
        
        if (Date.now() - cached.timestamp > this.maxAge) {
            this.cache.delete(key);
            return null;
        }
        
        return cached.data;
    }
}
```

---

## For QA Engineers

### Testable Component Boundaries

#### API Testing Boundaries
```python
# Test scenarios for /api/admin/activity/trends
class TestActivityTrendsAPI:
    def test_valid_date_range(self):
        # Test with 30-day range
        # Assert response structure
        # Verify data points count
    
    def test_max_date_range_boundary(self):
        # Test exactly 365 days
        # Test 366 days (should fail)
    
    def test_invalid_metrics(self):
        # Test with non-existent metric names
        # Verify error response
    
    def test_cache_headers(self):
        # Verify Cache-Control headers
        # Test cache bypass parameter
    
    def test_concurrent_requests(self):
        # Simulate 100 concurrent requests
        # Verify response times < 2s
```

#### Frontend Component Testing
```javascript
// Chart component test boundaries
describe('ActivityTrendsChart', () => {
    it('should handle empty data gracefully', () => {
        // Render with no data points
        // Verify "No data" message
    });
    
    it('should update without re-rendering', () => {
        // Initial render with data
        // Update with new data
        // Verify canvas not recreated
    });
    
    it('should handle metric toggle correctly', () => {
        // Toggle metrics on/off
        // Verify dataset visibility
    });
});

// Modal component test boundaries
describe('UserHistoryModal', () => {
    it('should trap focus when open', () => {
        // Open modal
        // Tab through elements
        // Verify focus stays within modal
    });
    
    it('should handle search errors', () => {
        // Search for non-existent user
        // Verify error message display
    });
});
```

### Data Validation Requirements

#### Input Validation Matrix
| Input | Valid Range | Edge Cases | Expected Behavior |
|-------|------------|------------|-------------------|
| start_date | Today - 365 days | Future date | 400 Bad Request |
| end_date | >= start_date | Before start_date | 400 Bad Request |
| metrics[] | Valid metric names | Empty array | Return all metrics |
| username | 2-50 chars | Special chars | Sanitize, search |
| page | 1-N | 0, negative | Default to 1 |

### Integration Testing Points

```yaml
Integration Test Suites:
  1. Database to API:
    - Verify activity_summary_daily queries
    - Test index performance
    - Validate JSON parsing from TEXT fields
    
  2. API to Frontend:
    - Test authentication flow
    - Verify CORS headers
    - Test rate limiting
    
  3. Frontend Components:
    - Chart.js library loading
    - Modal state management
    - Cross-browser compatibility
    
  4. End-to-End Flows:
    - Login → View Trends → Export Data
    - Open Modal → Search User → View History
    - Change Date Range → Update Chart → Save Preferences
```

### Performance Benchmarks

```javascript
// Performance test criteria
const performanceTargets = {
    initialPageLoad: 2000,      // ms
    chartRender: 500,           // ms
    modalOpen: 300,             // ms
    searchResponse: 1000,       // ms
    metricToggle: 100,          // ms
    dateRangeUpdate: 500,       // ms
    exportGeneration: 5000,     // ms
    
    // Memory usage
    maxMemoryUsage: 50 * 1024 * 1024,  // 50MB
    
    // Concurrent users
    concurrentUsers: 1000,
    
    // API rate limits
    requestsPerMinute: 100
};
```

---

## For Security Analysts

### Authentication Flow

```python
# Enhanced authentication for activity trends
class ActivityMonitorAuth:
    def verify_admin_access(self, session_id: str) -> bool:
        """
        1. Validate session exists and not expired
        2. Verify user role === 'admin'
        3. Check for concurrent session limits
        4. Log access attempt
        """
        
    def enforce_rate_limiting(self, user_id: int, endpoint: str) -> bool:
        """
        Token bucket algorithm:
        - 100 requests per minute per user
        - Separate buckets per endpoint
        - Return 429 if exceeded
        """
```

### Data Protection Requirements

```python
# Sensitive data handling
class DataSanitizer:
    @staticmethod
    def sanitize_username(username: str) -> str:
        """
        - Remove SQL injection attempts
        - Escape HTML entities
        - Validate against username regex: ^[a-zA-Z0-9_.-]+$
        """
        
    @staticmethod
    def anonymize_export_data(data: Dict, user_role: str) -> Dict:
        """
        - Hash user IDs for non-admin exports
        - Remove IP addresses
        - Redact sensitive page URLs
        """
```

### Security Testing Requirements

```yaml
Security Test Checklist:
  Authentication:
    - [ ] Non-admin users cannot access /api/admin/activity/trends
    - [ ] Session timeout after 30 minutes of inactivity
    - [ ] Concurrent session detection and alerting
    
  Input Validation:
    - [ ] SQL injection prevention in date parameters
    - [ ] XSS prevention in username search
    - [ ] Path traversal prevention in export filename
    
  Data Protection:
    - [ ] HTTPS only for all endpoints
    - [ ] Secure headers (CSP, X-Frame-Options, etc.)
    - [ ] No sensitive data in URL parameters
    
  Rate Limiting:
    - [ ] 100 req/min per user enforced
    - [ ] Gradual backoff for repeated violations
    - [ ] Bypass for system health checks
```

### Compliance Considerations

```python
# Audit logging for compliance
class ActivityAuditLogger:
    def log_data_access(self, user_id: int, action: str, details: Dict):
        """
        Log entry format:
        {
            "timestamp": ISO8601,
            "user_id": int,
            "action": "VIEW_TRENDS|EXPORT_DATA|SEARCH_USER",
            "ip_address": str,
            "details": {
                "date_range": str,
                "metrics": List[str],
                "export_format": str
            }
        }
        """
        
    def log_export_event(self, user_id: int, export_params: Dict):
        """
        Special handling for data exports:
        - Record exact data exported
        - Duration of export
        - File size
        - Destination (download/email)
        """
```

---

## Technical Feasibility Assessment

### Performance Analysis

**Current State Analysis**:
- Existing `activity_summary_daily` table is pre-aggregated (optimal)
- Maximum data volume: 365 rows × 6 metrics = 2,190 data points
- SQLite can handle this with proper indexing in < 100ms

**Performance Optimizations Required**:
1. **Database**: Add composite index on (date, metrics)
2. **API**: Implement response caching (1-hour TTL)
3. **Frontend**: Use requestAnimationFrame for smooth chart updates
4. **Network**: Enable gzip compression for API responses

### Scalability Assessment

**Load Calculations**:
```
Concurrent Users: 1000
Requests/User/Min: 1 (average)
Total Requests/Min: 1000
Cache Hit Rate: 80% (expected)
Database Queries/Min: 200
```

**Bottleneck Analysis**:
- SQLite can handle 200 queries/min easily with indexes
- Flask with proper connection pooling supports 1000+ concurrent
- Chart.js handles 365 data points without performance issues
- Browser memory usage: ~10MB for chart with all metrics

---

## Performance Optimization Recommendations

### Database Query Optimization

```sql
-- Optimized query for trends data
WITH date_range AS (
    SELECT date, unique_users, total_sessions, total_page_views,
           total_api_calls, avg_session_duration_seconds, peak_concurrent_users
    FROM activity_summary_daily
    WHERE date BETWEEN ? AND ?
    ORDER BY date ASC
)
SELECT 
    date,
    unique_users,
    total_sessions,
    total_page_views,
    total_api_calls,
    avg_session_duration_seconds,
    peak_concurrent_users,
    -- Calculate running averages for trend analysis
    AVG(unique_users) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as users_7day_avg,
    AVG(total_sessions) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as sessions_7day_avg
FROM date_range;
```

### Caching Layer Implementation

```python
class TrendsCacheManager:
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        self.ttl = 3600  # 1 hour
        
    def get_cache_key(self, start_date: str, end_date: str, metrics: List[str]) -> str:
        return f"trends_{start_date}_{end_date}_{'_'.join(sorted(metrics))}"
    
    def get(self, key: str) -> Optional[Dict]:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['data']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Dict):
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
        
        # Implement LRU eviction if cache grows too large
        if len(self.cache) > 100:
            self._evict_oldest()
```

### Client-Side Optimization

```javascript
// Progressive data loading strategy
class ProgressiveLoader {
    async loadTrends(startDate, endDate) {
        // First: Load last 30 days (fast)
        const recentData = await this.api.fetchTrends(
            this.getDateOffset(30), 
            new Date()
        );
        this.chart.update(recentData);
        
        // Then: Load remaining data if needed
        if (this.needsMoreData(startDate, endDate)) {
            const historicalData = await this.api.fetchTrends(
                startDate, 
                this.getDateOffset(31)
            );
            this.chart.appendData(historicalData);
        }
    }
}
```

---

## Alternative Technical Approaches

### Alternative 1: Server-Side Rendering with Matplotlib
**Pros**: 
- Reduced client-side processing
- Consistent rendering across browsers
- Better for low-powered devices

**Cons**:
- Increased server load
- No interactivity without round-trips
- Larger payload sizes

**Recommendation**: Not recommended due to interactivity requirements

### Alternative 2: D3.js Instead of Chart.js
**Pros**:
- More customization options
- Better for complex visualizations
- Smaller bundle size if tree-shaken

**Cons**:
- Steeper learning curve
- More code to maintain
- Requires more development time

**Recommendation**: Consider for Phase 2 if advanced features needed

### Alternative 3: WebSocket for Real-Time Updates
**Pros**:
- True real-time data
- Reduced polling overhead
- Better user experience

**Cons**:
- Increased complexity
- Requires WebSocket infrastructure
- Connection management overhead

**Recommendation**: Implement in Phase 3 after MVP validation

---

## Critical Technical Decisions

### Early Phase Decisions (Week 1)

1. **Chart Library Selection**: Chart.js
   - Rationale: No build step, good accessibility, adequate features
   - Alternative: Postpone D3.js to Phase 2

2. **Caching Strategy**: In-memory Python dict
   - Rationale: Simple, effective for current scale
   - Migration path: Redis when scaling beyond single server

3. **Date Range Limits**: 365 days maximum
   - Rationale: Balances data volume with usability
   - Future: Implement data aggregation for longer ranges

4. **Modal Framework**: Vanilla JavaScript
   - Rationale: Consistency with existing codebase
   - Avoids framework dependencies

### Technical Debt Considerations

```yaml
Acceptable Technical Debt (MVP):
  - Simple in-memory caching (upgrade to Redis later)
  - Single Y-axis for all metrics (dual-axis in Phase 2)
  - Basic trend calculation (ML-based in future)
  - Session storage for preferences (database in Phase 2)

Unacceptable Technical Debt:
  - Missing input validation
  - No error handling
  - Skipping accessibility features
  - No rate limiting
```

---

## Risk Mitigation Strategies

### Risk 1: SQLite Performance at Scale
**Likelihood**: Low
**Impact**: High
**Mitigation**:
- Pre-aggregate data in background job
- Implement materialized view pattern
- Ready PostgreSQL migration path if needed

### Risk 2: Browser Memory Issues with Large Datasets
**Likelihood**: Medium
**Impact**: Medium
**Mitigation**:
- Implement data windowing (show max 180 days)
- Use data decimation for older periods
- Provide "View Less Data" option

### Risk 3: Cache Invalidation Complexity
**Likelihood**: Medium
**Impact**: Low
**Mitigation**:
- Simple TTL-based expiration
- Manual cache clear option for admins
- Cache warming on schedule

### Risk 4: Chart.js Library Updates Breaking Changes
**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Pin to specific version (4.4.0)
- Maintain fallback to table view
- Abstract chart interface for easy replacement

---

## Implementation Checklist

### Phase 1: MVP (Week 1-2)
- [ ] Create `/api/admin/activity/trends` endpoint
- [ ] Add database indexes for performance
- [ ] Implement basic caching layer
- [ ] Create Chart.js integration
- [ ] Build modal component
- [ ] Move search functionality to modal
- [ ] Update page layout
- [ ] Add loading states
- [ ] Implement error handling
- [ ] Create unit tests

### Phase 2: Enhanced Features (Week 3)
- [ ] Multi-metric selection UI
- [ ] Date range picker component
- [ ] Export functionality
- [ ] Chart interactivity (zoom, pan)
- [ ] Advanced trend analysis
- [ ] User preference persistence
- [ ] Integration tests
- [ ] Performance testing

### Phase 3: Polish (Week 4)
- [ ] Mobile responsive design
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Cross-browser testing
- [ ] Documentation
- [ ] Security audit
- [ ] Load testing
- [ ] Deployment scripts
- [ ] Monitoring setup

---

## Summary

This architecture provides a robust, scalable solution for the Activity Monitor enhancement that:

1. **Leverages existing infrastructure** (Flask, SQLite, vanilla JS)
2. **Minimizes risk** through proven technologies
3. **Enables parallel development** with clear module boundaries
4. **Supports future enhancements** through modular design
5. **Maintains performance** through intelligent caching and optimization
6. **Ensures security** through proper authentication and validation

The phased approach allows for early validation of core features while maintaining flexibility for future enhancements based on user feedback.