# AI Infrastructure Sizing & Capacity Planning

## Executive Summary

This document provides detailed infrastructure sizing requirements, capacity planning, and cost projections for the AI Planogram Enhancement System deployment.

## 1. Current System Baseline

### Existing Infrastructure
- **Application**: Flask on single server
- **Database**: SQLite (4.1MB)
- **Users**: 6 active users
- **Devices**: 14 vending machines
- **Traffic**: ~500 requests/day

## 2. AI Workload Projections

### Request Volume Projections

| Feature | Year 1 | Year 2 | Year 3 |
|---------|--------|--------|--------|
| **Devices** | 100-500 | 500-2,000 | 2,000-10,000 |
| **Daily Active Users** | 50 | 200 | 1,000 |
| **Real-time Scoring Requests/Day** | 5,000 | 25,000 | 100,000 |
| **Revenue Predictions/Day** | 500 | 2,500 | 10,000 |
| **Demand Forecasts/Day** | 200 | 1,000 | 5,000 |
| **Total API Calls/Day** | 6,000 | 30,000 | 120,000 |

### Claude API Token Usage

```yaml
token_consumption:
  realtime_scoring:
    avg_tokens_per_request: 500
    requests_per_day_y1: 5000
    daily_tokens_y1: 2,500,000
    
  revenue_prediction:
    avg_tokens_per_request: 3000
    requests_per_day_y1: 500
    daily_tokens_y1: 1,500,000
    
  demand_forecasting:
    avg_tokens_per_request: 2000
    requests_per_day_y1: 200
    daily_tokens_y1: 400,000
    
  total_daily_tokens_y1: 4,400,000
  total_monthly_tokens_y1: 132,000,000
```

## 3. Infrastructure Components

### Application Tier

#### Year 1 Requirements
```yaml
application_servers:
  type: AWS EC2 t3.large
  count: 2-4 (auto-scaling)
  specs:
    vcpu: 2
    memory: 8GB
    network: Up to 5 Gbps
  
  load_balancer:
    type: Application Load Balancer
    zones: 2
    health_checks: /health
    
  auto_scaling:
    min_instances: 2
    max_instances: 4
    target_cpu: 70%
    scale_out_cooldown: 60s
    scale_in_cooldown: 300s
```

#### Year 2-3 Scaling
```yaml
application_servers_scaled:
  type: AWS EC2 m5.xlarge
  count: 4-10 (auto-scaling)
  specs:
    vcpu: 4
    memory: 16GB
    network: Up to 10 Gbps
```

### Database Tier

#### SQLite Database
```yaml
database:
  year_1:
    type: SQLite
    storage: Local filesystem
    specs:
      vcpu: 2
      memory: 8GB
      storage: 100GB GP3
      iops: 3000
    configuration:
      multi_az: true
      read_replicas: 1
      backup_retention: 7 days
      
  year_2:
    instance: db.m5.xlarge
    specs:
      vcpu: 4
      memory: 16GB
      storage: 500GB GP3
      iops: 6000
    read_replicas: 2
    
  year_3:
    instance: db.m5.2xlarge
    specs:
      vcpu: 8
      memory: 32GB
      storage: 1TB GP3
      iops: 12000
    read_replicas: 3
```

### Caching Tier

#### Redis Configuration
```yaml
redis_cache:
  year_1:
    type: AWS ElastiCache Redis
    node_type: cache.m5.large
    nodes: 2
    specs:
      memory: 6.38GB
      network: Up to 10 Gbps
    configuration:
      cluster_mode: disabled
      multi_az: true
      automatic_failover: true
      
  year_2_3:
    node_type: cache.m5.xlarge
    nodes: 3
    specs:
      memory: 12.93GB
    configuration:
      cluster_mode: enabled
      shards: 3
      replicas_per_shard: 1
```

### AI Processing Tier

#### Dedicated AI Workers
```yaml
ai_workers:
  type: AWS EC2 c5.2xlarge
  count: 2-6 (auto-scaling)
  specs:
    vcpu: 8
    memory: 16GB
    network: Up to 10 Gbps
  
  configuration:
    queue: AWS SQS or Redis Queue
    concurrency: 4 workers per instance
    timeout: 30 seconds per request
    retry: 3 attempts with exponential backoff
```

## 4. Cost Analysis

### Monthly Cost Projections

#### Year 1 Costs
```yaml
year_1_monthly:
  # Application Tier
  ec2_instances: $220  # 2x t3.large
  load_balancer: $25
  
  # Database Tier
  rds_instance: $140  # db.m5.large Multi-AZ
  rds_storage: $12    # 100GB
  rds_backup: $10
  read_replica: $70
  
  # Cache Tier
  elasticache: $102   # 2x cache.m5.large
  
  # AI Workers
  ai_workers: $440    # 2x c5.2xlarge
  
  # Claude API
  api_tokens: $3,960  # 132M tokens @ $0.03/1K
  
  # Storage & Transfer
  s3_storage: $50
  data_transfer: $100
  cloudwatch: $50
  
  total_monthly: $5,179
  total_annual: $62,148
```

#### Year 2 Costs
```yaml
year_2_monthly:
  infrastructure: $2,500
  claude_api: $19,800  # 5x token usage
  total_monthly: $22,300
  total_annual: $267,600
```

#### Year 3 Costs
```yaml
year_3_monthly:
  infrastructure: $5,000
  claude_api: $79,200  # 20x token usage
  total_monthly: $84,200
  total_annual: $1,010,400
```

### Cost Optimization Strategies

```yaml
optimization_strategies:
  reserved_instances:
    savings: 30-40%
    commitment: 1 year
    
  spot_instances:
    use_for: AI workers (non-critical)
    savings: 60-70%
    
  caching:
    cache_hit_target: 70%
    token_savings: 40%
    
  model_selection:
    use_haiku: 80% of requests
    use_sonnet: 15% of requests
    use_opus: 5% of requests
    
  batch_processing:
    group_similar_requests: true
    savings: 20% on tokens
```

## 5. Network Architecture

### VPC Design
```yaml
vpc_configuration:
  cidr: 10.0.0.0/16
  
  subnets:
    public:
      - 10.0.1.0/24  # AZ-1
      - 10.0.2.0/24  # AZ-2
    private:
      - 10.0.10.0/24 # AZ-1 App
      - 10.0.11.0/24 # AZ-2 App
      - 10.0.20.0/24 # AZ-1 DB
      - 10.0.21.0/24 # AZ-2 DB
      
  security_groups:
    alb:
      ingress:
        - 443/tcp from 0.0.0.0/0
        - 80/tcp from 0.0.0.0/0
    app:
      ingress:
        - 5000/tcp from ALB
    db:
      ingress:
        - 5432/tcp from App
    cache:
      ingress:
        - 6379/tcp from App
```

### CDN Configuration
```yaml
cloudfront:
  origins:
    - domain: alb.cvd.com
      protocol: https
      
  behaviors:
    default:
      cache: false
      
    static_assets:
      path_pattern: /static/*
      cache: true
      ttl: 86400
      
    api_responses:
      path_pattern: /api/planograms/optimize/heat-zones
      cache: true
      ttl: 3600
      
  estimated_requests: 1M/month
  estimated_cost: $100/month
```

## 6. Scaling Triggers

### Auto-Scaling Policies

```yaml
scaling_policies:
  application_tier:
    scale_out:
      cpu: "> 70% for 2 minutes"
      memory: "> 80% for 2 minutes"
      request_latency: "> 1s for 5 minutes"
      
    scale_in:
      cpu: "< 30% for 10 minutes"
      instances: "keep minimum 2"
      
  ai_workers:
    scale_out:
      queue_depth: "> 100 messages"
      processing_time: "> 5s average"
      
    scale_in:
      queue_depth: "< 10 messages for 10 minutes"
      instances: "keep minimum 2"
      
  database:
    read_replica_trigger:
      read_latency: "> 100ms"
      connections: "> 80% of max"
```

## 7. Disaster Recovery

### Backup Strategy
```yaml
backup_configuration:
  database:
    automated_backups: daily
    retention: 35 days
    snapshot_on_delete: true
    cross_region_copy: true
    
  application_state:
    config_backup: S3 versioning
    session_backup: Redis persistence
    
  ai_models:
    cache_backup: daily export to S3
    prediction_history: 90 day retention
```

### Recovery Targets
- **RPO**: 1 hour
- **RTO**: 2 hours
- **Degraded Mode**: Cache-only operation possible

## 8. Monitoring Infrastructure

### Metrics Collection
```yaml
monitoring:
  cloudwatch:
    custom_metrics:
      - ai_request_latency
      - token_usage_rate
      - cache_hit_ratio
      - prediction_accuracy
      
    alarms:
      - high_api_latency: "> 2s for 5 minutes"
      - token_budget_exceeded: "> daily limit"
      - cache_miss_rate: "> 50%"
      - error_rate: "> 1%"
      
  datadog_apm:
    traces: 100% for first month, 10% ongoing
    custom_dashboards:
      - AI Performance
      - Token Usage
      - Cost Tracking
```

## 9. Development & Staging Environments

### Development Environment
```yaml
dev_environment:
  scale: 20% of production
  
  infrastructure:
    app_servers: 1x t3.medium
    database: db.t3.medium
    cache: cache.t3.micro
    ai_workers: 1x t3.large
    
  cost: $500/month
  
  features:
    ai_mock_mode: true
    token_limit: 1M/day
```

### Staging Environment
```yaml
staging_environment:
  scale: 50% of production
  
  infrastructure:
    app_servers: 2x t3.large
    database: db.m5.large (single AZ)
    cache: cache.m5.large
    ai_workers: 1x c5.xlarge
    
  cost: $1,500/month
  
  features:
    real_ai_calls: true
    token_limit: 10M/day
```

## 10. Implementation Roadmap

### Phase 1: Foundation (Months 1-2)
- Provision Year 1 infrastructure
- Set up CI/CD pipelines
- Configure monitoring
- Implement caching layer
- **Budget**: $10,000 setup + $5,000/month

### Phase 2: Optimization (Months 3-4)
- Implement auto-scaling
- Optimize caching strategies
- Add CDN
- Reserved instance purchasing
- **Budget**: $4,000/month (with optimizations)

### Phase 3: Scale (Months 5-12)
- Add read replicas
- Implement sharding if needed
- Enhance monitoring
- Disaster recovery testing
- **Budget**: Gradual increase to $8,000/month

## 11. Capacity Planning Checklist

- [ ] Provision production infrastructure
- [ ] Configure auto-scaling groups
- [ ] Set up load balancers
- [ ] Initialize database with proper sizing
- [ ] Configure Redis cluster
- [ ] Set up AI worker pool
- [ ] Implement monitoring
- [ ] Configure backups
- [ ] Test disaster recovery
- [ ] Optimize costs with reserved instances
- [ ] Set up billing alerts
- [ ] Document runbooks

---

Document Version: 1.0
Date: 2025
Status: Ready for Infrastructure Review