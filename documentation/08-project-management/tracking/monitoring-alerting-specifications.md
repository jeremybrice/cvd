# AI Planogram Monitoring & Alerting Specifications

## Executive Summary

This document defines comprehensive monitoring, alerting, and observability requirements for the AI Planogram Enhancement System, including dashboard designs, alert thresholds, SLA definitions, and incident response procedures.

## 1. Monitoring Architecture

### Monitoring Stack Components
```yaml
monitoring_stack:
  metrics:
    primary: Prometheus
    storage: 90 days retention
    scrape_interval: 15s
    
  visualization:
    primary: Grafana
    dashboards: 12 custom dashboards
    refresh_rate: 30s default
    
  logging:
    aggregation: ELK Stack (Elasticsearch, Logstash, Kibana)
    retention: 30 days hot, 90 days warm
    
  tracing:
    system: Jaeger
    sampling_rate: 10% (100% for errors)
    
  alerting:
    manager: AlertManager
    channels: [email, slack, pagerduty]
    
  synthetic_monitoring:
    tool: Pingdom/Datadog Synthetics
    frequency: 5 minutes
```

## 2. Key Performance Indicators (KPIs)

### Business Metrics
| Metric | Target | Warning | Critical | Measurement |
|--------|--------|---------|----------|-------------|
| AI Feature Adoption | >80% | <60% | <40% | Daily active users |
| Revenue Lift from AI | >10% | <5% | <0% | Weekly comparison |
| Prediction Accuracy | >85% | <75% | <60% | MAPE calculation |
| User Satisfaction | >4.0/5 | <3.5 | <3.0 | NPS survey |
| Cost per Prediction | <$0.10 | >$0.15 | >$0.25 | Token usage tracking |

### Technical Metrics
| Metric | Target | Warning | Critical | Measurement |
|--------|--------|---------|----------|-------------|
| API Response Time (p95) | <500ms | >750ms | >1000ms | Request duration |
| System Availability | 99.9% | <99.5% | <99% | Uptime monitoring |
| Error Rate | <1% | >2% | >5% | HTTP 5xx responses |
| Cache Hit Rate | >70% | <60% | <40% | Redis statistics |
| Token Usage | <4M/day | >5M/day | >6M/day | Claude API usage |

## 3. Dashboard Specifications

### Dashboard 1: AI System Overview
```yaml
dashboard:
  name: "AI Planogram System Overview"
  refresh: 30s
  
  panels:
    - title: "System Health Score"
      type: stat
      query: |
        (api_health * 0.4 + 
         cache_health * 0.2 + 
         ai_service_health * 0.3 + 
         db_health * 0.1)
      thresholds:
        - value: 90
          color: green
        - value: 70
          color: yellow
        - value: 0
          color: red
          
    - title: "Real-Time Request Volume"
      type: timeseries
      queries:
        - "rate(http_requests_total[5m])"
        - "rate(ai_requests_total[5m])"
      
    - title: "AI Model Performance"
      type: gauge
      panels:
        - "Placement Score Accuracy"
        - "Revenue Prediction MAPE"
        - "Demand Forecast MAPE"
        
    - title: "Cost Tracking"
      type: stat
      query: "sum(ai_tokens_used) * 0.00003"
      unit: "USD/hour"
      
    - title: "Active Users by Feature"
      type: piechart
      query: |
        count by (feature) (
          ai_feature_usage{time="24h"}
        )
```

### Dashboard 2: API Performance
```yaml
dashboard:
  name: "API Performance Monitoring"
  
  panels:
    - title: "Request Latency Distribution"
      type: heatmap
      query: "http_request_duration_seconds"
      
    - title: "Endpoint Performance (p50, p95, p99)"
      type: table
      columns:
        - endpoint
        - p50_latency
        - p95_latency
        - p99_latency
        - request_rate
        - error_rate
        
    - title: "Rate Limiting"
      type: timeseries
      queries:
        - "rate_limit_exceeded_total"
        - "rate_limit_remaining"
        
    - title: "Cache Performance"
      type: graph
      metrics:
        - cache_hits
        - cache_misses
        - cache_evictions
        - hit_rate_percentage
```

### Dashboard 3: AI Model Insights
```yaml
dashboard:
  name: "AI Model Performance"
  
  panels:
    - title: "Prediction Accuracy Trends"
      type: timeseries
      queries:
        - "ai_prediction_accuracy{model='placement'}"
        - "ai_prediction_accuracy{model='revenue'}"
        - "ai_prediction_accuracy{model='demand'}"
        
    - title: "Token Usage by Model"
      type: bargraph
      breakdown:
        - claude-3-haiku
        - claude-3-sonnet
        - claude-3-opus
        
    - title: "Prediction Confidence Distribution"
      type: histogram
      query: "ai_confidence_score_bucket"
      
    - title: "Feature Importance"
      type: table
      data:
        - feature_name
        - importance_score
        - usage_count
```

### Dashboard 4: Business Impact
```yaml
dashboard:
  name: "Business Impact Analytics"
  
  panels:
    - title: "Revenue Impact by Device"
      type: bargraph
      query: |
        sum by (device) (
          revenue_lift_percentage
        )
        
    - title: "Optimization Adoption Rate"
      type: timeseries
      query: "optimizations_accepted / optimizations_suggested"
      
    - title: "Top Performing Predictions"
      type: table
      columns:
        - prediction_id
        - actual_lift
        - predicted_lift
        - accuracy
        
    - title: "ROI Calculator"
      type: stat
      calculation: |
        (revenue_increase - ai_costs) / ai_costs * 100
```

## 4. Alert Configurations

### Critical Alerts (Page Immediately)
```yaml
alerts:
  - name: "AI Service Down"
    condition: ai_service_health == 0
    duration: 1m
    severity: critical
    channels: [pagerduty, slack-critical]
    runbook: "https://wiki/runbooks/ai-service-down"
    
  - name: "Database Connection Lost"
    condition: sqlite_up == 0
    duration: 30s
    severity: critical
    channels: [pagerduty, slack-critical]
    
  - name: "API Error Rate Critical"
    condition: error_rate > 0.05
    duration: 2m
    severity: critical
    channels: [pagerduty, slack-critical]
    
  - name: "Token Budget Exceeded"
    condition: daily_token_usage > daily_token_limit
    duration: 1m
    severity: critical
    channels: [pagerduty, email-finance]
```

### High Priority Alerts (Page Within 15 min)
```yaml
alerts:
  - name: "Cache Hit Rate Low"
    condition: cache_hit_rate < 0.40
    duration: 10m
    severity: high
    channels: [slack-ops, email-ops]
    
  - name: "Response Time Degraded"
    condition: p95_latency > 1000
    duration: 5m
    severity: high
    channels: [slack-ops]
    
  - name: "Prediction Accuracy Degraded"
    condition: prediction_accuracy < 0.70
    duration: 30m
    severity: high
    channels: [slack-ml, email-ml]
    
  - name: "Memory Usage High"
    condition: memory_usage_percent > 85
    duration: 10m
    severity: high
    channels: [slack-ops]
```

### Warning Alerts (Notify Team)
```yaml
alerts:
  - name: "Disk Space Warning"
    condition: disk_free_percent < 20
    duration: 30m
    severity: warning
    channels: [email-ops]
    
  - name: "Rate Limit Approaching"
    condition: rate_limit_remaining < 100
    duration: 5m
    severity: warning
    channels: [slack-dev]
    
  - name: "Slow Database Queries"
    condition: slow_query_count > 10
    duration: 15m
    severity: warning
    channels: [email-dba]
```

## 5. Service Level Agreements (SLAs)

### API SLAs
```yaml
sla_definitions:
  availability:
    target: 99.9%
    measurement: "Uptime percentage per month"
    calculation: "(Total time - Downtime) / Total time * 100"
    exclusions:
      - "Scheduled maintenance windows"
      - "Force majeure events"
      
  latency:
    realtime_scoring:
      p50: 200ms
      p95: 450ms
      p99: 490ms
    revenue_prediction:
      p50: 2s
      p95: 6s
      p99: 8s
      
  error_rate:
    target: "<1% of requests"
    measurement: "HTTP 5xx responses"
    
  data_freshness:
    sales_data: "< 4 hours old"
    predictions: "< 24 hours cached"
```

### SLA Monitoring
```sql
-- SLA compliance query
WITH sla_metrics AS (
  SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE status_code >= 500) as errors,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time) as p95_latency
  FROM request_log
  WHERE timestamp >= NOW() - INTERVAL '30 days'
  GROUP BY 1
)
SELECT 
  COUNT(*) FILTER (WHERE errors::float / total_requests < 0.01) * 100.0 / COUNT(*) as error_sla_compliance,
  COUNT(*) FILTER (WHERE p95_latency < 500) * 100.0 / COUNT(*) as latency_sla_compliance
FROM sla_metrics;
```

## 6. Log Aggregation & Analysis

### Structured Logging Format
```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "INFO",
  "service": "ai-planogram",
  "trace_id": "abc123def456",
  "user_id": 42,
  "endpoint": "/api/planograms/realtime/score",
  "method": "POST",
  "status_code": 200,
  "response_time_ms": 234,
  "ai_model": "claude-3-haiku",
  "tokens_used": 450,
  "cache_hit": false,
  "error": null,
  "metadata": {
    "device_id": 123,
    "product_id": 5,
    "prediction_score": 85
  }
}
```

### Log Queries
```yaml
common_queries:
  error_analysis:
    query: |
      service:"ai-planogram" AND level:"ERROR"
      | stats count by error.type
      
  slow_requests:
    query: |
      response_time_ms:>1000
      | stats avg(response_time_ms) by endpoint
      
  token_usage:
    query: |
      ai_model:* 
      | sum(tokens_used) by ai_model
      
  user_activity:
    query: |
      user_id:* 
      | unique_count(user_id) by endpoint
```

## 7. Synthetic Monitoring

### Synthetic Test Scenarios
```python
# synthetic_tests.py
class SyntheticMonitor:
    def __init__(self):
        self.tests = []
        
    def test_critical_user_journey(self):
        """Test complete planogram optimization flow"""
        
        # 1. Login
        response = self.login("test_user", "test_pass")
        assert response.status_code == 200
        
        # 2. Get device planogram
        planogram = self.get_planogram(device_id=1)
        assert planogram is not None
        
        # 3. Request AI optimization
        optimization = self.request_optimization(planogram)
        assert optimization['score'] > 0
        
        # 4. Apply optimization
        result = self.apply_optimization(optimization)
        assert result['success'] == True
        
        # 5. Verify changes
        new_planogram = self.get_planogram(device_id=1)
        assert new_planogram != planogram
        
        return True
        
    def test_ai_endpoint_health(self):
        """Test all AI endpoints are responsive"""
        
        endpoints = [
            '/api/planograms/realtime/score',
            '/api/planograms/predict/revenue',
            '/api/planograms/optimize/heat-zones',
            '/api/planograms/optimize/affinity',
            '/api/planograms/predict/demand'
        ]
        
        for endpoint in endpoints:
            response = self.health_check(endpoint)
            assert response.status_code < 500
            assert response.time < 5000  # 5 seconds max
```

### Synthetic Test Schedule
```yaml
synthetic_schedule:
  critical_flow:
    frequency: 5_minutes
    locations: [us-east-1, us-west-2, eu-west-1]
    alert_after: 2_consecutive_failures
    
  api_health:
    frequency: 1_minute
    locations: [us-east-1]
    alert_after: 3_consecutive_failures
    
  full_regression:
    frequency: hourly
    locations: [us-east-1]
    alert_after: 1_failure
```

## 8. Capacity Monitoring

### Resource Utilization Metrics
```yaml
capacity_metrics:
  compute:
    - metric: cpu_usage_percent
      warning: 70
      critical: 85
      
    - metric: memory_usage_percent
      warning: 75
      critical: 90
      
  storage:
    - metric: disk_usage_percent
      warning: 70
      critical: 85
      
    - metric: database_size_gb
      warning: 80
      critical: 95
      
  network:
    - metric: bandwidth_usage_mbps
      warning: 800
      critical: 950
      
  application:
    - metric: connection_pool_usage
      warning: 80
      critical: 95
      
    - metric: thread_pool_usage
      warning: 75
      critical: 90
```

### Capacity Planning Queries
```sql
-- Growth projection
WITH daily_growth AS (
  SELECT 
    DATE(created_at) as date,
    COUNT(*) as daily_records
  FROM ai_predictions
  WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY 1
)
SELECT 
  AVG(daily_records) as avg_daily_records,
  MAX(daily_records) as peak_daily_records,
  REGR_SLOPE(daily_records, EXTRACT(EPOCH FROM date)) as growth_rate,
  -- Project 90 days out
  AVG(daily_records) + (REGR_SLOPE(daily_records, EXTRACT(EPOCH FROM date)) * 90) as projected_90_days
FROM daily_growth;
```

## 9. Incident Response Integration

### Incident Classification
```yaml
incident_levels:
  P1_Critical:
    description: "Complete service outage or data loss"
    response_time: 15_minutes
    escalation: immediate
    examples:
      - "AI service completely down"
      - "Database corruption"
      - "Security breach"
      
  P2_High:
    description: "Significant degradation affecting many users"
    response_time: 1_hour
    escalation: 30_minutes
    examples:
      - "API response time >5s"
      - "Prediction accuracy <50%"
      - "Cache layer failure"
      
  P3_Medium:
    description: "Partial degradation affecting some users"
    response_time: 4_hours
    escalation: 2_hours
    examples:
      - "Slow queries affecting reports"
      - "UI rendering issues"
      
  P4_Low:
    description: "Minor issues with workarounds"
    response_time: 24_hours
    escalation: none
```

### Runbook Integration
```yaml
runbooks:
  high_error_rate:
    dashboard_link: "https://grafana/d/api-errors"
    investigation_steps:
      1: "Check recent deployments"
      2: "Review error logs for patterns"
      3: "Verify database connectivity"
      4: "Check AI service status"
    remediation:
      - "Rollback if deployment-related"
      - "Scale up if load-related"
      - "Clear cache if corruption suspected"
      
  ai_service_degradation:
    dashboard_link: "https://grafana/d/ai-performance"
    investigation_steps:
      1: "Check Claude API status"
      2: "Verify API key validity"
      3: "Review token usage"
      4: "Check rate limiting"
    remediation:
      - "Switch to fallback AI model"
      - "Increase cache TTL"
      - "Enable request queuing"
```

## 10. Custom Metrics Implementation

### Application Metrics
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
ai_request_counter = Counter(
    'ai_requests_total',
    'Total AI requests',
    ['endpoint', 'model', 'status']
)

ai_request_duration = Histogram(
    'ai_request_duration_seconds',
    'AI request duration',
    ['endpoint', 'model'],
    buckets=[0.1, 0.25, 0.5, 1, 2, 5, 10]
)

# Business metrics
prediction_accuracy = Gauge(
    'ai_prediction_accuracy',
    'Prediction accuracy percentage',
    ['model', 'prediction_type']
)

revenue_lift = Gauge(
    'ai_revenue_lift_percentage',
    'Revenue lift from AI optimization',
    ['device_id']
)

# Resource metrics
token_usage = Counter(
    'ai_tokens_used_total',
    'Total tokens consumed',
    ['model', 'endpoint']
)

cache_operations = Counter(
    'cache_operations_total',
    'Cache operations',
    ['operation', 'result']
)
```

### Metric Collection
```python
# Decorator for automatic metric collection
def track_ai_request(endpoint, model):
    def decorator(func):
        def wrapper(*args, **kwargs):
            with ai_request_duration.labels(
                endpoint=endpoint,
                model=model
            ).time():
                try:
                    result = func(*args, **kwargs)
                    ai_request_counter.labels(
                        endpoint=endpoint,
                        model=model,
                        status='success'
                    ).inc()
                    return result
                except Exception as e:
                    ai_request_counter.labels(
                        endpoint=endpoint,
                        model=model,
                        status='error'
                    ).inc()
                    raise
        return wrapper
    return decorator
```

## 11. Reporting & Analytics

### Weekly Performance Report
```yaml
weekly_report:
  sections:
    - executive_summary:
        - total_ai_requests
        - average_accuracy
        - revenue_impact
        - total_cost
        
    - system_health:
        - availability_percentage
        - average_response_time
        - error_rate
        - incidents_count
        
    - usage_analytics:
        - top_features_used
        - user_adoption_rate
        - peak_usage_times
        
    - cost_analysis:
        - token_usage_by_model
        - cost_per_prediction
        - roi_calculation
```

### Monthly Business Review
```sql
-- Monthly metrics summary
WITH monthly_metrics AS (
  SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(*) as total_predictions,
    AVG(confidence_score) as avg_confidence,
    SUM(tokens_used) as total_tokens
  FROM ai_predictions
  WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '3 months')
  GROUP BY 1
)
SELECT 
  month,
  unique_users,
  total_predictions,
  ROUND(avg_confidence * 100, 1) as avg_confidence_pct,
  total_tokens,
  ROUND(total_tokens * 0.00003, 2) as estimated_cost_usd
FROM monthly_metrics
ORDER BY month DESC;
```

## 12. Implementation Checklist

- [ ] Deploy Prometheus with configured scrape targets
- [ ] Create Grafana dashboards from specifications
- [ ] Configure AlertManager with routing rules
- [ ] Set up log aggregation pipeline
- [ ] Implement custom metrics in application
- [ ] Create synthetic monitoring tests
- [ ] Document runbooks for all critical alerts
- [ ] Set up on-call rotation in PagerDuty
- [ ] Configure SLA tracking and reporting
- [ ] Test alert routing and escalation
- [ ] Train team on dashboard usage
- [ ] Schedule regular review meetings

---

Document Version: 1.0
Date: 2025
Status: Ready for DevOps Review