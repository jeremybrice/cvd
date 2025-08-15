# CVD AI Planogram Enhancement System - Deployment Guide

## Quick Start

### Local Development with Docker

1. **Prerequisites**
   - Docker Desktop installed
   - Docker Compose v2.0+
   - 8GB RAM minimum
   - `.env` file configured (copy from `.env.example`)

2. **Start Development Environment**
   ```bash
   # Clone repository
   git clone https://github.com/your-org/cvd-ai-planogram.git
   cd cvd-ai-planogram
   
   # Copy environment template
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   
   # Start all services
   docker-compose -f docker-compose.dev.yml up -d
   
   # View logs
   docker-compose -f docker-compose.dev.yml logs -f
   
   # Access applications
   # Frontend: http://localhost:8000
   # Backend API: http://localhost:5000
   # pgAdmin: http://localhost:5050
   # Redis Commander: http://localhost:8081
   # Flower (Celery monitor): http://localhost:5555
   ```

3. **Initialize Database**
   ```bash
   # Run migrations
   docker-compose -f docker-compose.dev.yml exec app python migration/migrate_to_postgres.py
   
   # Load sample data (optional)
   docker-compose -f docker-compose.dev.yml exec app python tools/load_sample_data.py
   ```

4. **Stop Development Environment**
   ```bash
   docker-compose -f docker-compose.dev.yml down
   
   # To remove volumes (database data)
   docker-compose -f docker-compose.dev.yml down -v
   ```

## Production Deployment

### AWS ECS Deployment

1. **Prerequisites**
   - AWS CLI configured
   - Terraform installed (v1.0+)
   - Docker Hub or ECR access
   - Domain name with Route53 hosted zone

2. **Infrastructure Setup**
   ```bash
   cd terraform
   
   # Initialize Terraform
   terraform init
   
   # Create workspace for environment
   terraform workspace new production
   
   # Plan infrastructure
   terraform plan -var-file=environments/production.tfvars
   
   # Apply infrastructure
   terraform apply -var-file=environments/production.tfvars
   ```

3. **Deploy Application**
   ```bash
   # Build and push Docker image
   docker build -t cvd-app:latest .
   docker tag cvd-app:latest your-registry/cvd-app:v1.0.0
   docker push your-registry/cvd-app:v1.0.0
   
   # Deploy using GitHub Actions (recommended)
   git tag v1.0.0
   git push origin v1.0.0
   # This triggers the deployment pipeline
   
   # OR deploy manually
   ./scripts/deploy.sh production v1.0.0
   ```

4. **Verify Deployment**
   ```bash
   # Run smoke tests
   ./scripts/smoke-test.sh https://api.cvd.example.com
   
   # Check health
   curl https://api.cvd.example.com/health
   ```

### Kubernetes Deployment

1. **Prerequisites**
   - kubectl configured
   - Helm 3+ installed
   - Kubernetes cluster (EKS, GKE, AKS)

2. **Deploy with Helm**
   ```bash
   # Add Helm repository
   helm repo add cvd https://charts.cvd.example.com
   helm repo update
   
   # Install application
   helm install cvd-app cvd/cvd-ai-planogram \
     --namespace cvd \
     --create-namespace \
     --values values.production.yaml
   
   # Check deployment
   kubectl get pods -n cvd
   kubectl get svc -n cvd
   ```

## Environment Configuration

### Required Environment Variables

```bash
# Application
FLASK_ENV=production
SESSION_SECRET=<generate-secure-secret>

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://host:6379/0
REDIS_PASSWORD=<redis-password>

# AI Services
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
CLAUDE_MODEL_REALTIME=claude-3-haiku-20240307
CLAUDE_MODEL_ANALYSIS=claude-3-sonnet-20240229
AI_RATE_LIMIT=5000
AI_CACHE_TTL=14400

# Push Notifications
VAPID_PUBLIC_KEY=<your-public-key>
VAPID_PRIVATE_KEY=<your-private-key>
VAPID_SUBJECT=mailto:admin@cvd.example.com

# Monitoring (optional)
SENTRY_DSN=https://xxx@sentry.io/xxx
DATADOG_API_KEY=<datadog-key>
NEW_RELIC_LICENSE_KEY=<new-relic-key>
```

### SSL/TLS Configuration

1. **Generate SSL Certificate**
   ```bash
   # Using Let's Encrypt
   certbot certonly --standalone -d api.cvd.example.com
   
   # Or using AWS Certificate Manager
   aws acm request-certificate \
     --domain-name api.cvd.example.com \
     --validation-method DNS
   ```

2. **Configure Nginx**
   - Update `/config/nginx.conf` with certificate paths
   - Ensure TLS 1.2+ is enforced
   - Enable HSTS headers

## Database Management

### Migration from SQLite to PostgreSQL

```bash
# Backup SQLite database
cp cvd.db cvd.db.backup

# Run migration script
python migration/migrate_to_postgres.py \
  --source cvd.db \
  --target postgresql://user:pass@host:5432/cvd

# Verify migration
python migration/verify_migration.py
```

### Backup and Restore

```bash
# Create backup
docker-compose exec db pg_dump -U cvd cvd > backup.sql

# Restore backup
docker-compose exec -T db psql -U cvd cvd < backup.sql

# Automated backups (production)
# Configured in docker-compose.yml to run daily
```

## Monitoring and Observability

### Health Checks

- **Application Health**: `GET /health`
- **Database Health**: `GET /api/health/db`
- **Redis Health**: `GET /api/health/redis`
- **AI Service Health**: `GET /api/ai/health`

### Metrics and Dashboards

1. **Prometheus Metrics**
   - Endpoint: `/metrics`
   - Scrape interval: 30s
   - Key metrics: request rate, latency, AI token usage

2. **Grafana Dashboards**
   - Import dashboard ID: 12345 (CVD Overview)
   - Custom dashboards in `/monitoring/dashboards/`

3. **Application Logs**
   ```bash
   # View logs
   docker-compose logs -f app
   
   # AWS CloudWatch
   aws logs tail /ecs/cvd-app --follow
   
   # Kubernetes
   kubectl logs -f deployment/cvd-app -n cvd
   ```

## Scaling Guidelines

### Horizontal Scaling

```yaml
# Auto-scaling configuration
scaling:
  metrics:
    - type: cpu
      target: 70%
    - type: memory
      target: 80%
    - type: requests_per_second
      target: 100
  
  min_replicas: 2
  max_replicas: 10
  
  scale_up:
    cooldown: 60s
    increment: 2
  
  scale_down:
    cooldown: 300s
    decrement: 1
```

### Vertical Scaling

| Component | Dev | Staging | Production |
|-----------|-----|---------|------------|
| App Server | 1 CPU, 2GB RAM | 2 CPU, 4GB RAM | 4 CPU, 8GB RAM |
| AI Worker | 2 CPU, 4GB RAM | 4 CPU, 8GB RAM | 8 CPU, 16GB RAM |
| Database | db.t3.micro | db.t3.small | db.r6g.xlarge |
| Redis | cache.t3.micro | cache.t3.small | cache.r6g.large |

## Rollback Procedures

### Application Rollback

```bash
# Automated rollback (GitHub Actions)
# Triggered automatically on deployment failure

# Manual rollback
./scripts/rollback-application.sh production v1.0.0

# Feature flag disable (emergency)
./scripts/disable-ai-features.sh
```

### Database Rollback

```bash
# Restore from snapshot
./scripts/rollback-database.sh production snapshot-20240101

# Point-in-time recovery
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier cvd-production \
  --target-db-instance-identifier cvd-production-pitr \
  --restore-time 2024-01-01T12:00:00.000Z
```

## Security Checklist

- [ ] SSL/TLS certificates configured
- [ ] Secrets stored in AWS Secrets Manager
- [ ] Database encryption at rest enabled
- [ ] Network security groups configured
- [ ] WAF rules enabled
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Authentication required for all API endpoints
- [ ] Audit logging enabled
- [ ] Backup encryption enabled
- [ ] Vulnerability scanning in CI/CD
- [ ] Container security scanning enabled

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check database status
   docker-compose exec db pg_isready
   
   # Check connection string
   echo $DATABASE_URL
   
   # Test connection
   docker-compose exec app python -c "from app import db; db.engine.execute('SELECT 1')"
   ```

2. **AI Service Timeout**
   ```bash
   # Check API key
   curl -H "X-API-Key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/health
   
   # Check rate limits
   docker-compose exec app python tools/check_ai_limits.py
   
   # View AI worker logs
   docker-compose logs ai-worker
   ```

3. **High Memory Usage**
   ```bash
   # Check container stats
   docker stats
   
   # Restart services
   docker-compose restart app ai-worker
   
   # Increase memory limits
   # Edit docker-compose.yml deploy.resources.limits
   ```

## Support and Documentation

- **Documentation**: `/docs/`
- **API Documentation**: `https://api.cvd.example.com/docs`
- **Issue Tracker**: GitHub Issues
- **Support Email**: support@cvd.example.com
- **Slack Channel**: #cvd-deployment

## Performance Benchmarks

### Expected Performance Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| API Response Time (p50) | <200ms | - |
| API Response Time (p99) | <1s | - |
| AI Response Time (realtime) | <500ms | - |
| AI Response Time (analysis) | <7s | - |
| Database Query Time (p50) | <50ms | - |
| Cache Hit Rate | >80% | - |
| Uptime | 99.9% | - |

## Cost Optimization Tips

1. **Use Spot Instances** for non-critical workloads
2. **Enable Auto-shutdown** for development environments
3. **Implement Caching** aggressively
4. **Use Reserved Instances** for production
5. **Monitor AI Token Usage** to control costs
6. **Compress Static Assets** with CDN
7. **Use Database Read Replicas** wisely
8. **Archive Old Logs** to cheaper storage

## Maintenance Windows

- **Production**: Sundays 2-4 AM UTC
- **Staging**: Anytime with notice
- **Development**: No restrictions

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-01 | Initial AI deployment |
| 1.1.0 | TBD | Performance optimizations |
| 1.2.0 | TBD | Enhanced monitoring |

---

For detailed information, see the [AI_PLANOGRAM_DEPLOYMENT_PLAN.md](AI_PLANOGRAM_DEPLOYMENT_PLAN.md)