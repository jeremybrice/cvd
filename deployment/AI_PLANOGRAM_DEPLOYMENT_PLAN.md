# AI Planogram Enhancement System - Comprehensive Deployment Plan

## Executive Summary

This deployment plan provides a complete infrastructure strategy for the AI-powered planogram enhancement system, covering local development through production deployment. The plan follows a progressive enhancement approach, starting with simple containerization for rapid development and scaling to full cloud infrastructure for production readiness.

## Table of Contents

1. [Infrastructure Requirements](#infrastructure-requirements)
2. [Docker Containerization Strategy](#docker-containerization-strategy)
3. [CI/CD Pipeline Configuration](#cicd-pipeline-configuration)
4. [Environment Setup](#environment-setup)
5. [Database Migration Strategy](#database-migration-strategy)
6. [Monitoring and Observability](#monitoring-and-observability)
7. [Rollback Procedures](#rollback-procedures)
8. [Scaling Strategy](#scaling-strategy)
9. [Security Considerations](#security-considerations)
10. [Cost Optimization](#cost-optimization)

## Infrastructure Requirements

### Core Infrastructure Components

#### Application Tier
- **Flask Application Server**: 2-4 instances (auto-scaling)
- **Static Content Server**: Nginx for frontend assets
- **WebSocket Server**: For real-time AI feedback
- **Background Workers**: Celery for async AI processing

#### AI Services Tier
- **Claude API Gateway**: Rate limiting and token management
- **ML Model Server**: For custom predictive models
- **Cache Layer**: Redis for AI response caching
- **Queue System**: RabbitMQ/Redis for job processing

#### Data Tier
- **Primary Database**: PostgreSQL (migration from SQLite)
- **Cache Database**: Redis for session and AI caching
- **Vector Database**: Pinecone/Weaviate for similarity search
- **Object Storage**: S3 for service photos and DEX files

#### Infrastructure Services
- **Load Balancer**: AWS ALB/Nginx
- **CDN**: CloudFront for static assets
- **Service Mesh**: Optional Istio for microservices
- **Container Registry**: ECR/Docker Hub

### Resource Specifications

#### Development Environment
```yaml
resources:
  flask_app:
    cpu: 1 core
    memory: 2GB
    storage: 10GB
  
  ai_services:
    cpu: 2 cores
    memory: 4GB
    storage: 20GB
  
  database:
    cpu: 1 core
    memory: 2GB
    storage: 50GB
  
  redis:
    cpu: 0.5 core
    memory: 1GB
    storage: 5GB
```

#### Production Environment
```yaml
resources:
  flask_app:
    instances: 2-4 (auto-scaling)
    cpu: 2 cores per instance
    memory: 4GB per instance
    storage: 20GB per instance
  
  ai_services:
    instances: 2-3 (auto-scaling)
    cpu: 4 cores per instance
    memory: 8GB per instance
    storage: 50GB per instance
  
  database:
    type: RDS PostgreSQL
    instance_class: db.r6g.xlarge
    storage: 500GB SSD
    read_replicas: 1-2
  
  redis:
    type: ElastiCache
    node_type: cache.r6g.large
    nodes: 2 (cluster mode)
  
  cdn:
    type: CloudFront
    edge_locations: US/Canada
```

## Docker Containerization Strategy

### Development Containerization

#### 1. Application Dockerfile
```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY . .

# Development environment variables
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

# Hot reload support
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]
```

#### 2. Docker Compose for Local Development
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "5000:5000"
    volumes:
      - .:/app  # Hot reload
      - ./data:/app/data
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=postgresql://cvd:cvd@db:5432/cvd_dev
      - REDIS_URL=redis://redis:6379/0
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - db
      - redis
    networks:
      - cvd-network

  frontend:
    image: nginx:alpine
    ports:
      - "8000:80"
    volumes:
      - ./:/usr/share/nginx/html:ro
      - ./config/nginx-dev.conf:/etc/nginx/nginx.conf:ro
    networks:
      - cvd-network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=cvd_dev
      - POSTGRES_USER=cvd
      - POSTGRES_PASSWORD=cvd
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migration/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - cvd-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - cvd-network

  ai-worker:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: celery -A ai_services.tasks worker --loglevel=info
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql://cvd:cvd@db:5432/cvd_dev
      - REDIS_URL=redis://redis:6379/0
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - db
      - redis
    networks:
      - cvd-network

volumes:
  postgres_data:

networks:
  cvd-network:
    driver: bridge
```

### Production Containerization

#### 1. Multi-Stage Production Dockerfile
```dockerfile
# Dockerfile
# Stage 1: Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 cvduser && chown -R cvduser:cvduser /app
USER cvduser

# Make sure scripts in .local are callable
ENV PATH=/root/.local/bin:$PATH

# Production settings
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "120", "app:app"]
```

#### 2. AI Services Container
```dockerfile
# Dockerfile.ai
FROM python:3.11-slim

WORKDIR /app

# Install AI-specific dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python AI packages
COPY requirements-ai.txt ./
RUN pip install --no-cache-dir -r requirements-ai.txt

# Copy AI services code
COPY ai_services/ ./ai_services/
COPY ai_prompts/ ./ai_prompts/

# Non-root user
RUN useradd -m -u 1000 aiuser && chown -R aiuser:aiuser /app
USER aiuser

# Environment
ENV PYTHONUNBUFFERED=1

# Run AI service
CMD ["python", "-m", "ai_services.server"]
```

## CI/CD Pipeline Configuration

### GitHub Actions Workflow

#### 1. CI Pipeline
```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: cvd_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:test@localhost:5432/cvd_test
        REDIS_URL: redis://localhost:6379/0
      run: |
        pytest tests/ --cov=. --cov-report=xml --cov-report=html
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
    
    - name: Security scan
      run: |
        pip install safety bandit
        safety check
        bandit -r . -f json -o bandit-report.json
    
    - name: Lint code
      run: |
        pip install flake8 black
        flake8 . --count --max-line-length=120 --statistics
        black --check .

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to GitHub Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=sha,prefix={{branch}}-
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

#### 2. CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy Pipeline

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  deploy-staging:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Deploy to ECS Staging
      run: |
        # Update task definition
        aws ecs register-task-definition \
          --cli-input-json file://deploy/ecs-task-staging.json
        
        # Update service
        aws ecs update-service \
          --cluster cvd-staging \
          --service cvd-app \
          --task-definition cvd-app-staging \
          --force-new-deployment
    
    - name: Run smoke tests
      run: |
        ./scripts/smoke-test.sh https://staging.cvd.example.com
    
    - name: Notify Slack
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        text: 'Staging deployment ${{ job.status }}'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}

  deploy-production:
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Create database backup
      run: |
        ./scripts/backup-database.sh production
    
    - name: Deploy to ECS Production (Blue/Green)
      run: |
        # Deploy to green environment
        aws ecs register-task-definition \
          --cli-input-json file://deploy/ecs-task-prod.json
        
        # Update green service
        aws ecs update-service \
          --cluster cvd-production \
          --service cvd-app-green \
          --task-definition cvd-app-prod \
          --force-new-deployment
        
        # Wait for healthy
        aws ecs wait services-stable \
          --cluster cvd-production \
          --services cvd-app-green
        
        # Switch traffic
        ./scripts/switch-traffic.sh green
    
    - name: Run health checks
      run: |
        ./scripts/health-check.sh https://api.cvd.example.com
    
    - name: Create release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        body: |
          AI Planogram Enhancement System Release
          See [CHANGELOG](CHANGELOG.md) for details
```

## Environment Setup

### Environment Configuration Structure

#### 1. Development Environment
```bash
# .env.development
# Application Settings
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production

# Database
DATABASE_URL=postgresql://cvd:cvd@localhost:5432/cvd_dev
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=300

# AI Services
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
CLAUDE_MODEL_REALTIME=claude-3-haiku-20240307
CLAUDE_MODEL_ANALYSIS=claude-3-sonnet-20240229
CLAUDE_MODEL_COMPLEX=claude-3-opus-20240229
AI_CACHE_ENABLED=true
AI_CACHE_TTL=3600

# Monitoring
SENTRY_DSN=
LOG_LEVEL=DEBUG

# Feature Flags
FEATURE_AI_REALTIME=true
FEATURE_AI_PREDICTIONS=true
FEATURE_AI_OPTIMIZATION=true
```

#### 2. Staging Environment
```bash
# .env.staging
# Application Settings
FLASK_ENV=staging
SECRET_KEY=${SECRET_KEY}  # From AWS Secrets Manager

# Database
DATABASE_URL=${DATABASE_URL}  # From AWS Secrets Manager
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis
REDIS_URL=${REDIS_URL}  # From AWS Parameter Store
REDIS_CACHE_TTL=600

# AI Services
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}  # From AWS Secrets Manager
AI_RATE_LIMIT=1000
AI_CACHE_ENABLED=true
AI_CACHE_TTL=7200

# Monitoring
SENTRY_DSN=${SENTRY_DSN}
LOG_LEVEL=INFO
DATADOG_API_KEY=${DATADOG_API_KEY}

# Feature Flags
FEATURE_AI_REALTIME=true
FEATURE_AI_PREDICTIONS=true
FEATURE_AI_OPTIMIZATION=false  # Testing in staging
```

#### 3. Production Environment
```bash
# .env.production
# Application Settings
FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}  # From AWS Secrets Manager

# Database
DATABASE_URL=${DATABASE_URL}  # From AWS Secrets Manager
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
DATABASE_READ_REPLICA_URL=${DATABASE_READ_REPLICA_URL}

# Redis
REDIS_URL=${REDIS_URL}  # From AWS Parameter Store
REDIS_CLUSTER_ENABLED=true
REDIS_CACHE_TTL=1800

# AI Services
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}  # From AWS Secrets Manager
AI_RATE_LIMIT=5000
AI_CACHE_ENABLED=true
AI_CACHE_TTL=14400
AI_FALLBACK_ENABLED=true

# Monitoring
SENTRY_DSN=${SENTRY_DSN}
LOG_LEVEL=WARNING
DATADOG_API_KEY=${DATADOG_API_KEY}
NEW_RELIC_LICENSE_KEY=${NEW_RELIC_LICENSE_KEY}

# Feature Flags
FEATURE_FLAGS_SERVICE=launchdarkly
LAUNCHDARKLY_SDK_KEY=${LAUNCHDARKLY_SDK_KEY}
```

### Infrastructure as Code

#### 1. Terraform Configuration
```hcl
# terraform/main.tf
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "cvd-terraform-state"
    key    = "ai-planogram/terraform.tfstate"
    region = "us-east-1"
  }
}

# VPC Configuration
module "vpc" {
  source = "./modules/vpc"
  
  name = "cvd-${var.environment}"
  cidr = var.vpc_cidr
  
  azs             = var.availability_zones
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets
  
  enable_nat_gateway = true
  enable_vpn_gateway = false
  
  tags = local.common_tags
}

# ECS Cluster
module "ecs" {
  source = "./modules/ecs"
  
  cluster_name = "cvd-${var.environment}"
  vpc_id       = module.vpc.vpc_id
  
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
  
  tags = local.common_tags
}

# RDS Database
module "database" {
  source = "./modules/rds"
  
  identifier = "cvd-${var.environment}"
  
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = var.db_instance_class
  allocated_storage    = var.db_storage_size
  
  database_name = "cvd"
  username      = "cvd_admin"
  
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.private_subnets
  
  backup_retention_period = var.environment == "production" ? 30 : 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  create_read_replica = var.environment == "production"
  
  tags = local.common_tags
}

# ElastiCache Redis
module "redis" {
  source = "./modules/elasticache"
  
  cluster_id = "cvd-${var.environment}"
  
  node_type              = var.redis_node_type
  number_cache_nodes     = var.redis_node_count
  parameter_group_family = "redis7"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  automatic_failover_enabled = var.environment == "production"
  
  tags = local.common_tags
}

# Application Load Balancer
module "alb" {
  source = "./modules/alb"
  
  name = "cvd-${var.environment}"
  
  vpc_id          = module.vpc.vpc_id
  subnets         = module.vpc.public_subnets
  certificate_arn = var.ssl_certificate_arn
  
  health_check_path = "/health"
  
  tags = local.common_tags
}

# ECS Services
module "app_service" {
  source = "./modules/ecs-service"
  
  name            = "cvd-app"
  cluster_id      = module.ecs.cluster_id
  task_definition = module.task_definitions.app_task_arn
  
  desired_count = var.app_desired_count
  
  target_group_arn = module.alb.target_group_arn
  
  autoscaling_enabled = true
  autoscaling_min     = var.app_min_count
  autoscaling_max     = var.app_max_count
  
  tags = local.common_tags
}

module "ai_service" {
  source = "./modules/ecs-service"
  
  name            = "cvd-ai"
  cluster_id      = module.ecs.cluster_id
  task_definition = module.task_definitions.ai_task_arn
  
  desired_count = var.ai_desired_count
  
  autoscaling_enabled = true
  autoscaling_min     = var.ai_min_count
  autoscaling_max     = var.ai_max_count
  
  tags = local.common_tags
}
```

## Database Migration Strategy

### Migration Plan from SQLite to PostgreSQL

#### Phase 1: Schema Migration
```sql
-- migration/001_create_base_schema.sql
-- Core tables with AI enhancements

CREATE SCHEMA IF NOT EXISTS cvd;
CREATE SCHEMA IF NOT EXISTS ai;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "vector";   -- For embeddings

-- Migrate existing tables
-- (Use existing migration scripts from migration/ directory)

-- AI-specific tables
CREATE TABLE ai.predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    planogram_id INTEGER REFERENCES cvd.planograms(id),
    prediction_type VARCHAR(50) NOT NULL,
    input_data JSONB NOT NULL,
    prediction JSONB NOT NULL,
    confidence DECIMAL(3,2),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_predictions_planogram (planogram_id),
    INDEX idx_predictions_type (prediction_type),
    INDEX idx_predictions_created (created_at DESC)
);

CREATE TABLE ai.optimization_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id INTEGER REFERENCES cvd.devices(id),
    cabinet_index INTEGER,
    optimization_type VARCHAR(50),
    parameters JSONB,
    results JSONB,
    performance_metrics JSONB,
    accepted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES cvd.users(id)
);

CREATE TABLE ai.feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    feedback_type VARCHAR(50),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES cvd.users(id)
);

-- Performance indexes
CREATE INDEX idx_optimization_device ON ai.optimization_runs(device_id, cabinet_index);
CREATE INDEX idx_feedback_entity ON ai.feedback(entity_type, entity_id);
```

#### Phase 2: Data Migration Script
```python
# migration/migrate_to_postgres.py
import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
import logging
from datetime import datetime

class DatabaseMigrator:
    def __init__(self, sqlite_path, postgres_url):
        self.sqlite_conn = sqlite3.connect(sqlite_path)
        self.sqlite_conn.row_factory = sqlite3.Row
        self.pg_conn = psycopg2.connect(postgres_url)
        self.batch_size = 1000
        
    def migrate(self):
        """Execute full migration"""
        try:
            # Create checkpoint
            self.create_checkpoint()
            
            # Migrate in order of dependencies
            tables_order = [
                'users', 'locations', 'routes', 'device_types',
                'cabinet_types', 'products', 'devices',
                'cabinet_configurations', 'planograms',
                'planogram_slots', 'service_orders',
                'service_order_cabinets', 'service_order_cabinet_items',
                'sales', 'device_metrics', 'dex_reads'
            ]
            
            for table in tables_order:
                self.migrate_table(table)
                
            # Update sequences
            self.update_sequences()
            
            # Verify migration
            self.verify_migration()
            
            self.pg_conn.commit()
            logging.info("Migration completed successfully")
            
        except Exception as e:
            self.pg_conn.rollback()
            logging.error(f"Migration failed: {e}")
            raise
            
    def migrate_table(self, table_name):
        """Migrate single table with progress tracking"""
        logging.info(f"Migrating table: {table_name}")
        
        # Get data from SQLite
        cursor = self.sqlite_conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            logging.info(f"No data in {table_name}")
            return
            
        # Prepare PostgreSQL insert
        columns = [desc[0] for desc in cursor.description]
        placeholders = ','.join(['%s'] * len(columns))
        insert_query = f"""
            INSERT INTO cvd.{table_name} ({','.join(columns)})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """
        
        # Batch insert
        pg_cursor = self.pg_conn.cursor()
        data = [tuple(row) for row in rows]
        
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            execute_batch(pg_cursor, insert_query, batch)
            logging.info(f"Migrated {min(i + self.batch_size, len(data))}/{len(data)} rows")
            
        pg_cursor.close()
        logging.info(f"Completed migration of {table_name}: {len(data)} rows")
        
    def update_sequences(self):
        """Update PostgreSQL sequences to match data"""
        pg_cursor = self.pg_conn.cursor()
        
        sequences = [
            ('devices_id_seq', 'devices'),
            ('users_id_seq', 'users'),
            ('planograms_id_seq', 'planograms'),
            ('service_orders_id_seq', 'service_orders')
        ]
        
        for seq_name, table_name in sequences:
            pg_cursor.execute(f"""
                SELECT setval('cvd.{seq_name}', 
                    COALESCE((SELECT MAX(id) FROM cvd.{table_name}), 0) + 1, 
                    false)
            """)
            
        pg_cursor.close()
        
    def verify_migration(self):
        """Verify row counts match"""
        sqlite_cursor = self.sqlite_conn.cursor()
        pg_cursor = self.pg_conn.cursor()
        
        tables = ['devices', 'planograms', 'sales', 'users']
        
        for table in tables:
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = sqlite_cursor.fetchone()[0]
            
            pg_cursor.execute(f"SELECT COUNT(*) FROM cvd.{table}")
            pg_count = pg_cursor.fetchone()[0]
            
            if sqlite_count != pg_count:
                raise Exception(f"Count mismatch for {table}: SQLite={sqlite_count}, PostgreSQL={pg_count}")
                
            logging.info(f"Verified {table}: {pg_count} rows")
            
    def create_checkpoint(self):
        """Create migration checkpoint"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        checkpoint = {
            'timestamp': timestamp,
            'source': 'sqlite',
            'target': 'postgresql'
        }
        logging.info(f"Created checkpoint: {checkpoint}")
        return checkpoint

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    migrator = DatabaseMigrator(
        sqlite_path='cvd.db',
        postgres_url='postgresql://cvd:cvd@localhost:5432/cvd'
    )
    
    migrator.migrate()
```

## Monitoring and Observability

### Monitoring Stack Components

#### 1. Application Monitoring
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    volumes:
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=redis-datasource
    ports:
      - "3000:3000"
    networks:
      - monitoring

  loki:
    image: grafana/loki:latest
    volumes:
      - ./monitoring/loki-config.yml:/etc/loki/local-config.yaml
      - loki_data:/loki
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - monitoring

  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./monitoring/promtail-config.yml:/etc/promtail/config.yml
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    command: -config.file=/etc/promtail/config.yml
    networks:
      - monitoring

volumes:
  prometheus_data:
  grafana_data:
  loki_data:

networks:
  monitoring:
    external: true
```

#### 2. Custom Metrics Implementation
```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from functools import wraps
import time

# AI Service Metrics
ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI API requests',
    ['service', 'model', 'status']
)

ai_request_duration = Histogram(
    'ai_request_duration_seconds',
    'AI request duration',
    ['service', 'model']
)

ai_tokens_used = Counter(
    'ai_tokens_used_total',
    'Total tokens used',
    ['model', 'operation']
)

ai_cache_hits = Counter(
    'ai_cache_hits_total',
    'AI response cache hits',
    ['service']
)

planogram_optimizations = Counter(
    'planogram_optimizations_total',
    'Total planogram optimizations',
    ['status', 'type']
)

active_ai_requests = Gauge(
    'active_ai_requests',
    'Currently active AI requests'
)

# Decorator for monitoring AI calls
def monitor_ai_call(service, model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            active_ai_requests.inc()
            
            try:
                result = func(*args, **kwargs)
                ai_requests_total.labels(
                    service=service,
                    model=model,
                    status='success'
                ).inc()
                return result
                
            except Exception as e:
                ai_requests_total.labels(
                    service=service,
                    model=model,
                    status='error'
                ).inc()
                raise
                
            finally:
                duration = time.time() - start_time
                ai_request_duration.labels(
                    service=service,
                    model=model
                ).observe(duration)
                active_ai_requests.dec()
                
        return wrapper
    return decorator

# Application metrics endpoint
def metrics_endpoint():
    return generate_latest()
```

#### 3. Logging Configuration
```python
# monitoring/logging_config.py
import logging
import json
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

def setup_logging(app, environment):
    """Configure structured logging"""
    
    # JSON formatter for structured logs
    formatter = jsonlogger.JsonFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s',
        rename_fields={'timestamp': '@timestamp'}
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configure Sentry for error tracking
    if environment in ['staging', 'production']:
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
            environment=environment
        )
    
    # AI service specific logger
    ai_logger = logging.getLogger('ai_services')
    ai_logger.setLevel(logging.DEBUG if environment == 'development' else logging.INFO)
    
    # Audit logger for sensitive operations
    audit_logger = logging.getLogger('audit')
    audit_handler = RotatingFileHandler(
        'logs/audit.log',
        maxBytes=10485760,
        backupCount=30
    )
    audit_handler.setFormatter(formatter)
    audit_logger.addHandler(audit_handler)
    
    return {
        'app': root_logger,
        'ai': ai_logger,
        'audit': audit_logger
    }
```

#### 4. Health Check Implementation
```python
# monitoring/health.py
from flask import Blueprint, jsonify
import psycopg2
import redis
import requests
from datetime import datetime

health_bp = Blueprint('health', __name__)

def check_database(db_url):
    """Check database connectivity"""
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {'status': 'healthy', 'response_time_ms': 10}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}

def check_redis(redis_url):
    """Check Redis connectivity"""
    try:
        r = redis.from_url(redis_url)
        r.ping()
        return {'status': 'healthy', 'response_time_ms': 5}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}

def check_ai_service():
    """Check AI service availability"""
    try:
        # Test with minimal API call
        response = requests.post(
            'http://localhost:5001/health',
            timeout=5
        )
        if response.status_code == 200:
            return {'status': 'healthy', 'response_time_ms': response.elapsed.total_seconds() * 1000}
        return {'status': 'unhealthy', 'status_code': response.status_code}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}

@health_bp.route('/health')
def health():
    """Comprehensive health check endpoint"""
    checks = {
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'healthy',
        'checks': {}
    }
    
    # Run health checks
    checks['checks']['database'] = check_database(app.config['DATABASE_URL'])
    checks['checks']['redis'] = check_redis(app.config['REDIS_URL'])
    checks['checks']['ai_service'] = check_ai_service()
    
    # Determine overall status
    for service, result in checks['checks'].items():
        if result['status'] == 'unhealthy':
            checks['status'] = 'degraded'
            break
    
    status_code = 200 if checks['status'] == 'healthy' else 503
    return jsonify(checks), status_code

@health_bp.route('/health/live')
def liveness():
    """Simple liveness check"""
    return jsonify({'status': 'alive'}), 200

@health_bp.route('/health/ready')
def readiness():
    """Readiness check for load balancer"""
    # Check if application is ready to serve traffic
    try:
        # Quick database check
        check_database(app.config['DATABASE_URL'])
        return jsonify({'status': 'ready'}), 200
    except:
        return jsonify({'status': 'not_ready'}), 503
```

## Rollback Procedures

### Automated Rollback Strategy

#### 1. Database Rollback
```bash
#!/bin/bash
# scripts/rollback-database.sh

set -e

ENVIRONMENT=$1
BACKUP_ID=$2

if [ -z "$ENVIRONMENT" ] || [ -z "$BACKUP_ID" ]; then
    echo "Usage: ./rollback-database.sh <environment> <backup_id>"
    exit 1
fi

echo "Starting database rollback for $ENVIRONMENT to backup $BACKUP_ID"

# Stop application services
echo "Stopping application services..."
aws ecs update-service \
    --cluster cvd-$ENVIRONMENT \
    --service cvd-app \
    --desired-count 0

# Wait for services to stop
aws ecs wait services-stable \
    --cluster cvd-$ENVIRONMENT \
    --services cvd-app

# Restore database
echo "Restoring database from backup..."
if [ "$ENVIRONMENT" == "production" ]; then
    aws rds restore-db-instance-from-db-snapshot \
        --db-instance-identifier cvd-prod-rollback \
        --db-snapshot-identifier $BACKUP_ID
    
    # Wait for restoration
    aws rds wait db-instance-available \
        --db-instance-identifier cvd-prod-rollback
    
    # Switch DNS
    echo "Switching database DNS..."
    aws route53 change-resource-record-sets \
        --hosted-zone-id $HOSTED_ZONE_ID \
        --change-batch file://rollback-dns.json
else
    # For staging, direct restore
    pg_restore -h $DB_HOST -U $DB_USER -d cvd_staging < backups/$BACKUP_ID.sql
fi

# Restart application services
echo "Restarting application services..."
aws ecs update-service \
    --cluster cvd-$ENVIRONMENT \
    --service cvd-app \
    --desired-count 2

echo "Database rollback completed"
```

#### 2. Application Rollback
```bash
#!/bin/bash
# scripts/rollback-application.sh

set -e

ENVIRONMENT=$1
VERSION=$2

if [ -z "$ENVIRONMENT" ] || [ -z "$VERSION" ]; then
    echo "Usage: ./rollback-application.sh <environment> <version>"
    exit 1
fi

echo "Rolling back application to version $VERSION"

# Update task definition to previous version
aws ecs register-task-definition \
    --cli-input-json file://deploy/task-definitions/$VERSION.json

# Update service with previous task definition
aws ecs update-service \
    --cluster cvd-$ENVIRONMENT \
    --service cvd-app \
    --task-definition cvd-app:$VERSION \
    --force-new-deployment

# Wait for rollback to complete
aws ecs wait services-stable \
    --cluster cvd-$ENVIRONMENT \
    --services cvd-app

# Verify health
./scripts/health-check.sh https://$ENVIRONMENT.cvd.example.com

echo "Application rollback completed"
```

#### 3. Feature Flag Rollback
```python
# rollback/feature_flags.py
import launchdarkly
from launchdarkly import Config

class FeatureFlagManager:
    def __init__(self, sdk_key):
        self.client = launchdarkly.LDClient(Config(sdk_key))
        
    def emergency_disable_ai_features(self):
        """Disable all AI features in case of issues"""
        flags_to_disable = [
            'ai-realtime-assistant',
            'ai-predictions',
            'ai-optimization',
            'ai-visual-analysis'
        ]
        
        for flag in flags_to_disable:
            self.client.variation(flag, {'key': 'system'}, False)
            
        print(f"Disabled {len(flags_to_disable)} AI feature flags")
        
    def rollback_to_safe_state(self):
        """Rollback to known safe configuration"""
        safe_config = {
            'ai-realtime-assistant': False,
            'ai-predictions': False,
            'ai-optimization': False,
            'ai-visual-analysis': False,
            'ai-cache-enabled': True,
            'ai-fallback-mode': True
        }
        
        for flag, value in safe_config.items():
            self.client.variation(flag, {'key': 'system'}, value)
            
        print("Rolled back to safe feature flag configuration")
```

## Scaling Strategy

### Horizontal Scaling Configuration

#### 1. Auto-Scaling Policies
```yaml
# terraform/autoscaling.tf
resource "aws_appautoscaling_target" "app_service" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${var.cluster_name}/${var.service_name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# CPU-based scaling
resource "aws_appautoscaling_policy" "cpu_scaling" {
  name               = "${var.service_name}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.app_service.resource_id
  scalable_dimension = aws_appautoscaling_target.app_service.scalable_dimension
  service_namespace  = aws_appautoscaling_target.app_service.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Memory-based scaling
resource "aws_appautoscaling_policy" "memory_scaling" {
  name               = "${var.service_name}-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.app_service.resource_id
  scalable_dimension = aws_appautoscaling_target.app_service.scalable_dimension
  service_namespace  = aws_appautoscaling_target.app_service.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = 80.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# AI service specific scaling
resource "aws_appautoscaling_policy" "ai_request_scaling" {
  name               = "ai-service-request-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ai_service.resource_id
  scalable_dimension = aws_appautoscaling_target.ai_service.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ai_service.service_namespace

  target_tracking_scaling_policy_configuration {
    customized_metric_specification {
      metric_name = "AIRequestsPerSecond"
      namespace   = "CVD/AI"
      statistic   = "Average"
    }
    target_value = 100.0
    scale_in_cooldown  = 600
    scale_out_cooldown = 120
  }
}
```

#### 2. Database Scaling
```sql
-- Database read replica configuration
-- terraform/modules/rds/read_replica.tf

resource "aws_db_instance" "read_replica" {
  count = var.create_read_replica ? var.read_replica_count : 0
  
  identifier = "${var.identifier}-read-${count.index + 1}"
  
  replicate_source_db = aws_db_instance.main.identifier
  
  instance_class = var.read_replica_instance_class
  
  publicly_accessible = false
  
  auto_minor_version_upgrade = false
  
  performance_insights_enabled = true
  performance_insights_retention_period = 7
  
  tags = merge(
    var.tags,
    {
      Name = "${var.identifier}-read-${count.index + 1}"
      Type = "read-replica"
    }
  )
}

-- Connection pooling with PgBouncer
-- docker/pgbouncer/pgbouncer.ini
[databases]
cvd_read = host=cvd-read-1.cluster.amazonaws.com port=5432 dbname=cvd
cvd_write = host=cvd-primary.cluster.amazonaws.com port=5432 dbname=cvd

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3
max_db_connections = 100
```

#### 3. Caching Strategy
```python
# scaling/cache_strategy.py
import redis
import hashlib
import json
from functools import wraps
from datetime import datetime, timedelta

class MultiTierCache:
    """Multi-tier caching strategy for AI responses"""
    
    def __init__(self, redis_url):
        self.redis_client = redis.from_url(redis_url)
        self.local_cache = {}  # In-memory L1 cache
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'l1_hits': 0,
            'l2_hits': 0
        }
        
    def cache_key(self, service, operation, params):
        """Generate cache key"""
        key_data = {
            'service': service,
            'operation': operation,
            'params': params
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"ai:cache:{hashlib.md5(key_string.encode()).hexdigest()}"
        
    def get(self, key):
        """Get from cache with multi-tier lookup"""
        # L1: Local memory cache
        if key in self.local_cache:
            self.cache_stats['l1_hits'] += 1
            self.cache_stats['hits'] += 1
            return self.local_cache[key]
            
        # L2: Redis cache
        value = self.redis_client.get(key)
        if value:
            self.cache_stats['l2_hits'] += 1
            self.cache_stats['hits'] += 1
            # Promote to L1
            self.local_cache[key] = json.loads(value)
            return self.local_cache[key]
            
        self.cache_stats['misses'] += 1
        return None
        
    def set(self, key, value, ttl=3600):
        """Set in both cache tiers"""
        # L1: Local cache
        self.local_cache[key] = value
        
        # L2: Redis cache
        self.redis_client.setex(
            key,
            ttl,
            json.dumps(value)
        )
        
    def invalidate_pattern(self, pattern):
        """Invalidate cache entries matching pattern"""
        # Clear L1 cache
        keys_to_remove = [k for k in self.local_cache if pattern in k]
        for key in keys_to_remove:
            del self.local_cache[key]
            
        # Clear L2 cache
        for key in self.redis_client.scan_iter(f"ai:cache:{pattern}*"):
            self.redis_client.delete(key)

def cached_ai_response(cache, ttl=3600):
    """Decorator for caching AI responses"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Generate cache key
            cache_key = cache.cache_key(
                service=self.__class__.__name__,
                operation=func.__name__,
                params={'args': args, 'kwargs': kwargs}
            )
            
            # Check cache
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
                
            # Call function
            result = func(self, *args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
```

## Security Considerations

### Security Implementation

#### 1. API Security
```python
# security/api_security.py
from functools import wraps
from flask import request, jsonify
import jwt
import redis
from datetime import datetime, timedelta
import hashlib

class APISecurityManager:
    def __init__(self, app, redis_client):
        self.app = app
        self.redis = redis_client
        self.rate_limits = {
            'ai_realtime': (100, 60),  # 100 requests per minute
            'ai_optimization': (10, 3600),  # 10 per hour
            'ai_prediction': (50, 300)  # 50 per 5 minutes
        }
        
    def require_api_key(self, f):
        """Validate API key"""
        @wraps(f)
        def decorated(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                return jsonify({'error': 'API key required'}), 401
                
            # Validate API key
            if not self.validate_api_key(api_key):
                return jsonify({'error': 'Invalid API key'}), 401
                
            return f(*args, **kwargs)
        return decorated
        
    def rate_limit(self, endpoint_type):
        """Rate limiting decorator"""
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                # Get client identifier
                client_id = self.get_client_id(request)
                
                # Check rate limit
                limit, window = self.rate_limits.get(endpoint_type, (100, 60))
                
                key = f"rate_limit:{endpoint_type}:{client_id}"
                
                try:
                    current = self.redis.incr(key)
                    if current == 1:
                        self.redis.expire(key, window)
                        
                    if current > limit:
                        return jsonify({
                            'error': 'Rate limit exceeded',
                            'retry_after': self.redis.ttl(key)
                        }), 429
                        
                except redis.RedisError:
                    # Redis failure shouldn't break the API
                    pass
                    
                return f(*args, **kwargs)
            return decorated
        return decorator
        
    def validate_api_key(self, api_key):
        """Validate API key against database"""
        # Hash the API key for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Check in cache first
        cache_key = f"api_key:valid:{key_hash}"
        if self.redis.get(cache_key):
            return True
            
        # Check database
        # (Implementation depends on your user/api_key model)
        valid = self.check_api_key_in_db(key_hash)
        
        if valid:
            # Cache for 5 minutes
            self.redis.setex(cache_key, 300, "1")
            
        return valid
        
    def get_client_id(self, request):
        """Get unique client identifier"""
        # Try to get from authenticated user
        if hasattr(request, 'user') and request.user:
            return f"user:{request.user.id}"
            
        # Fall back to IP address
        return f"ip:{request.remote_addr}"
```

#### 2. Secrets Management
```yaml
# kubernetes/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: cvd-secrets
  namespace: cvd
type: Opaque
data:
  database-url: <base64-encoded-url>
  anthropic-api-key: <base64-encoded-key>
  redis-password: <base64-encoded-password>
  jwt-secret: <base64-encoded-secret>

---
# AWS Secrets Manager configuration
# terraform/secrets.tf
resource "aws_secretsmanager_secret" "app_secrets" {
  name = "cvd-${var.environment}-secrets"
  
  rotation_rules {
    automatically_after_days = 90
  }
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  
  secret_string = jsonencode({
    database_url     = var.database_url
    anthropic_api_key = var.anthropic_api_key
    redis_password   = random_password.redis.result
    jwt_secret       = random_password.jwt.result
  })
}

resource "random_password" "redis" {
  length  = 32
  special = true
}

resource "random_password" "jwt" {
  length  = 64
  special = false
}
```

## Cost Optimization

### Cost Management Strategy

#### 1. AI Token Optimization
```python
# cost_optimization/token_optimizer.py
class AITokenOptimizer:
    """Optimize AI API token usage"""
    
    def __init__(self):
        self.token_limits = {
            'claude-3-haiku': 200000,
            'claude-3-sonnet': 200000,
            'claude-3-opus': 200000
        }
        self.cost_per_1k_tokens = {
            'claude-3-haiku': {'input': 0.00025, 'output': 0.00125},
            'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
            'claude-3-opus': {'input': 0.015, 'output': 0.075}
        }
        
    def optimize_prompt(self, prompt, context):
        """Optimize prompt to reduce tokens"""
        # Remove unnecessary whitespace
        prompt = ' '.join(prompt.split())
        
        # Truncate context if too long
        max_context_tokens = 50000
        if self.estimate_tokens(context) > max_context_tokens:
            context = self.truncate_context(context, max_context_tokens)
            
        # Use structured format
        optimized = {
            'system': 'You are an AI assistant for planogram optimization.',
            'context': context,
            'task': prompt,
            'format': 'json'
        }
        
        return optimized
        
    def select_model_by_complexity(self, task_complexity):
        """Select appropriate model based on task"""
        if task_complexity == 'simple':
            return 'claude-3-haiku'  # Fast and cheap
        elif task_complexity == 'medium':
            return 'claude-3-sonnet'  # Balanced
        else:
            return 'claude-3-opus'  # Most capable
            
    def estimate_cost(self, model, input_tokens, output_tokens):
        """Estimate cost for API call"""
        costs = self.cost_per_1k_tokens[model]
        input_cost = (input_tokens / 1000) * costs['input']
        output_cost = (output_tokens / 1000) * costs['output']
        return input_cost + output_cost
```

#### 2. Infrastructure Cost Optimization
```yaml
# terraform/cost_optimization.tf
# Use Spot instances for non-critical workloads
resource "aws_ecs_capacity_provider" "spot" {
  name = "spot-capacity-provider"
  
  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.spot.arn
    
    managed_scaling {
      status                    = "ENABLED"
      target_capacity           = 100
      minimum_scaling_step_size = 1
      maximum_scaling_step_size = 10
    }
    
    managed_termination_protection = "DISABLED"
  }
}

# Reserved capacity for baseline load
resource "aws_ec2_capacity_reservation" "baseline" {
  instance_type     = "t3.medium"
  instance_platform = "Linux/UNIX"
  availability_zone = var.availability_zones[0]
  instance_count    = 2
}

# Auto-shutdown for development environments
resource "aws_lambda_function" "auto_shutdown" {
  filename      = "lambda/auto_shutdown.zip"
  function_name = "cvd-dev-auto-shutdown"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  
  environment {
    variables = {
      ENVIRONMENT = "development"
      SHUTDOWN_TIME = "19:00"
      STARTUP_TIME = "07:00"
    }
  }
}

# CloudWatch Events for scheduled shutdown
resource "aws_cloudwatch_event_rule" "shutdown_schedule" {
  name                = "cvd-dev-shutdown"
  schedule_expression = "cron(0 19 * * ? *)"
}

resource "aws_cloudwatch_event_target" "shutdown_lambda" {
  rule      = aws_cloudwatch_event_rule.shutdown_schedule.name
  target_id = "ShutdownLambda"
  arn       = aws_lambda_function.auto_shutdown.arn
}
```

## Deployment Checklist

### Pre-Deployment Checklist

- [ ] **Code Review**
  - [ ] All PRs reviewed and approved
  - [ ] Security scan passed
  - [ ] Code coverage > 80%

- [ ] **Testing**
  - [ ] Unit tests passing
  - [ ] Integration tests passing
  - [ ] Performance tests completed
  - [ ] Load testing completed

- [ ] **Infrastructure**
  - [ ] Database backup created
  - [ ] Infrastructure provisioned
  - [ ] SSL certificates valid
  - [ ] DNS configured

- [ ] **Configuration**
  - [ ] Environment variables set
  - [ ] Secrets configured
  - [ ] Feature flags configured
  - [ ] Rate limits configured

- [ ] **Monitoring**
  - [ ] Alerts configured
  - [ ] Dashboards created
  - [ ] Log aggregation working
  - [ ] APM configured

- [ ] **Documentation**
  - [ ] API documentation updated
  - [ ] Runbook updated
  - [ ] Architecture diagrams current
  - [ ] Change log updated

### Post-Deployment Checklist

- [ ] **Verification**
  - [ ] Health checks passing
  - [ ] Smoke tests passing
  - [ ] Key metrics normal
  - [ ] No error spike

- [ ] **Monitoring**
  - [ ] Watch error rates for 30 minutes
  - [ ] Monitor performance metrics
  - [ ] Check AI service latency
  - [ ] Verify cache hit rates

- [ ] **Communication**
  - [ ] Team notified
  - [ ] Release notes published
  - [ ] Customer communication sent
  - [ ] Support team briefed

## Conclusion

This comprehensive deployment plan provides a complete infrastructure strategy for the AI-powered planogram enhancement system. It covers all aspects from local development to production deployment, ensuring:

1. **Scalability**: Auto-scaling and load balancing for handling growth
2. **Reliability**: Health checks, monitoring, and rollback procedures
3. **Security**: API security, secrets management, and access controls
4. **Performance**: Caching, optimization, and CDN integration
5. **Cost Efficiency**: Token optimization and infrastructure cost management
6. **Maintainability**: CI/CD pipelines and infrastructure as code

The phased approach allows for progressive enhancement, starting with simple local development containers and scaling to full production infrastructure as needed.