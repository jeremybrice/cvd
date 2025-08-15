# AI Planogram Enhancement - Master Implementation Plan

## Executive Summary

This comprehensive implementation plan coordinates the transformation of CVD's planogram management system with advanced AI capabilities. Developed through collaboration of specialized technical experts, this plan provides a complete roadmap from requirements to production deployment.

**Target Outcomes:**
- 20-30% revenue increase per device
- 70% reduction in planogram creation time
- 30% reduction in stockouts
- 15% reduction in service costs
- ROI of 800-1,100% annually

## Table of Contents

1. [Product Requirements](#1-product-requirements)
2. [Technical Architecture](#2-technical-architecture)
3. [Backend Implementation](#3-backend-implementation)
4. [Frontend Implementation](#4-frontend-implementation)
5. [LLM Integration Pipeline](#5-llm-integration-pipeline)
6. [Testing Strategy](#6-testing-strategy)
7. [Deployment Plan](#7-deployment-plan)
8. [Implementation Timeline](#8-implementation-timeline)
9. [Risk Management](#9-risk-management)
10. [Success Metrics](#10-success-metrics)

---

## 1. Product Requirements

### User Personas

| Persona | Role | Primary Goals | Key Features |
|---------|------|---------------|--------------|
| Sarah | Merchandising Manager | Maximize revenue, optimize placement | Real-time AI feedback, revenue prediction |
| Mike | Field Service Driver | Efficient service, accurate pick lists | Route optimization, demand forecasting |
| Jennifer | Operations Director | Fleet-wide optimization, ROI tracking | Analytics dashboard, A/B testing |
| Tom | Route Manager | Minimize costs, prevent stockouts | Service scheduling, spoilage prediction |

### Feature Priority Matrix

| Feature | Priority | Business Value | Technical Complexity | Phase |
|---------|----------|----------------|---------------------|-------|
| Real-Time AI Assistant | P0 | Critical | Medium | 1 |
| Revenue Prediction | P0 | Critical | High | 1 |
| Heat Zone Analysis | P0 | High | Low | 1 |
| Product Affinity | P1 | High | Medium | 2 |
| Demand Forecasting | P1 | High | High | 2 |
| Location Personalization | P1 | Medium | High | 2 |
| Route Optimization | P2 | Medium | High | 3 |

### MVP Definition (Phase 1 - 2 Weeks)

**Core Features:**
1. Real-time placement scoring with visual feedback
2. Revenue impact prediction for changes
3. Visual heat zone optimization

**Success Criteria:**
- 5-10% revenue increase in A/B testing
- <500ms response time for real-time feedback
- 70% user adoption within 30 days

---

## 2. Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────┐
│            Frontend Layer (NSPT.html)           │
├─────────────────────────────────────────────────┤
│ • Enhanced drag-and-drop with AI feedback       │
│ • Heat map visualizations                       │
│ • Performance metrics dashboard                 │
│ • Responsive design for mobile/tablet           │
└────────────────────┬────────────────────────────┘
                     │ WebSocket/SSE
┌────────────────────▼────────────────────────────┐
│              API Layer (Flask)                  │
├─────────────────────────────────────────────────┤
│ • /api/planograms/realtime/* - Live scoring    │
│ • /api/planograms/predict/* - Predictions      │
│ • /api/planograms/optimize/* - Optimization    │
│ • /api/planograms/batch/* - Bulk operations    │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│           AI Services Layer                     │
├─────────────────────────────────────────────────┤
│ • RealtimeAssistant (Claude Haiku)             │
│ • PredictiveModeler (Claude Sonnet + ML)       │
│ • AffinityEngine (Statistical Analysis)         │
│ • DemandForecaster (Time Series ML)            │
│ • LocationPersonalizer (Claude Opus)           │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              Data Layer (SQLite)                │
├─────────────────────────────────────────────────┤
│ • Core tables: devices, planograms, products    │
│ • AI tables: predictions, experiments, metrics  │
│ • Cache layer: Redis for performance           │
└─────────────────────────────────────────────────┘
```

### API Contracts

#### Real-time Placement Analysis
```http
POST /api/planograms/realtime/score
{
  "product_id": 5,
  "slot_position": "B4",
  "device_id": 123,
  "cabinet_index": 0
}

Response (200ms SLA):
{
  "score": 85,
  "reasoning": "Eye-level placement, high velocity product",
  "constraints_passed": true,
  "suggestions": ["Consider adjacent affinity products"]
}
```

#### Revenue Prediction
```http
POST /api/planograms/predict/revenue
{
  "current_planogram": {...},
  "proposed_planogram": {...},
  "forecast_days": 30
}

Response:
{
  "baseline_revenue": 450.00,
  "predicted_revenue": 495.00,
  "lift_percentage": 10.0,
  "confidence_interval": [475, 515],
  "break_even_days": 3
}
```

---

## 3. Backend Implementation

### Module Structure

```
/ai_services/
├── base/
│   ├── ai_client.py           # Claude API wrapper
│   ├── cache_manager.py       # Multi-tier caching
│   └── exceptions.py          # Error handling
├── core/
│   ├── realtime_assistant.py  # Real-time scoring
│   ├── revenue_predictor.py   # Revenue forecasting
│   ├── affinity_analyzer.py   # Product clustering
│   ├── demand_forecaster.py   # Demand prediction
│   └── zone_optimizer.py      # Heat zone analysis
├── pipelines/
│   ├── realtime_pipeline.py   # Streaming pipeline
│   ├── batch_pipeline.py      # Bulk processing
│   └── experiment_pipeline.py # A/B testing
└── utils/
    ├── data_validator.py       # Input validation
    ├── prompt_builder.py       # LLM templates
    └── metrics_calculator.py   # Performance metrics
```

### Database Schema Changes

```sql
-- AI Predictions Storage
CREATE TABLE ai_predictions (
    id INTEGER PRIMARY KEY,
    planogram_id INTEGER NOT NULL,
    prediction_type TEXT NOT NULL,
    prediction_data JSON NOT NULL,
    confidence_score DECIMAL(3,2),
    model_version TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (planogram_id) REFERENCES planograms(id)
);

-- Zone Performance Metrics
CREATE TABLE zone_performance (
    id INTEGER PRIMARY KEY,
    cabinet_configuration_id INTEGER NOT NULL,
    zone_code TEXT NOT NULL,
    visibility_score DECIMAL(3,2),
    revenue_multiplier DECIMAL(3,2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Affinity Matrix
CREATE TABLE product_affinity (
    id INTEGER PRIMARY KEY,
    product_a_id INTEGER NOT NULL,
    product_b_id INTEGER NOT NULL,
    affinity_score DECIMAL(3,2),
    co_purchase_count INTEGER DEFAULT 0,
    lift_score DECIMAL(3,2)
);

-- A/B Testing Experiments
CREATE TABLE ai_experiments (
    id INTEGER PRIMARY KEY,
    experiment_name TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    control_planogram_id INTEGER,
    variant_planogram_ids JSON,
    metrics JSON,
    results JSON
);
```

### Caching Strategy

**Multi-tier Cache Implementation:**
- **L1 Memory Cache**: 5-minute TTL for real-time operations
- **L2 Redis Cache**: 1-hour TTL for frequent queries
- **L3 Database Cache**: 24-hour TTL for expensive computations

---

## 4. Frontend Implementation

### Enhanced UI Components

#### Real-time AI Feedback Panel
```javascript
class AIPlanogramAssistant {
    constructor() {
        this.api = new CVDApi();
        this.dragHandler = new AIEnhancedDragDrop(this);
        this.heatMap = new RevenueHeatMap();
        this.metrics = new PerformanceMetrics();
    }
    
    async analyzePlacement(productId, slotPosition) {
        const score = await this.api.getPlacementScore({
            product_id: productId,
            slot_position: slotPosition,
            device_id: this.deviceId
        });
        
        this.showFeedback(score);
        this.updateMetrics();
    }
    
    showFeedback(score) {
        const overlay = document.getElementById('ai-feedback');
        overlay.className = this.getScoreClass(score.score);
        overlay.innerHTML = `
            <div class="score">${score.score}/100</div>
            <div class="reasoning">${score.reasoning}</div>
        `;
    }
}
```

#### Heat Map Visualization
```javascript
class RevenueHeatMap {
    render(planogramData) {
        const canvas = document.getElementById('heatmap-canvas');
        const ctx = canvas.getContext('2d');
        
        planogramData.slots.forEach(slot => {
            const color = this.getHeatColor(slot.revenue_potential);
            ctx.fillStyle = color;
            ctx.fillRect(slot.x, slot.y, slot.width, slot.height);
        });
    }
    
    getHeatColor(value) {
        // Gradient from blue (low) to red (high)
        const ratio = value / 100;
        return `hsl(${240 - ratio * 240}, 100%, 50%)`;
    }
}
```

### Responsive Design

```css
/* Mobile-first responsive design */
@media (max-width: 768px) {
    .ai-panel {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        transform: translateY(calc(100% - 60px));
        transition: transform 0.3s;
    }
    
    .ai-panel.expanded {
        transform: translateY(0);
    }
}

@media (min-width: 1024px) {
    .ai-panel {
        position: fixed;
        right: 20px;
        top: 100px;
        width: 320px;
    }
}
```

---

## 5. LLM Integration Pipeline

### Model Selection Strategy

| Use Case | Model | Response Time | Cost/1K requests |
|----------|-------|---------------|------------------|
| Real-time scoring | Claude Haiku | <500ms | $0.25 |
| Standard analysis | Claude Sonnet | <7s | $3.00 |
| Complex optimization | Claude Opus | <15s | $15.00 |
| Vision analysis | Claude Opus | <20s | $15.00 |

### Prompt Engineering Templates

#### Real-time Placement Analysis
```xml
<placement_analysis>
    <product>
        <id>{product_id}</id>
        <category>{category}</category>
        <velocity>{units_per_day}</velocity>
        <price>{price}</price>
    </product>
    
    <position>
        <slot>{slot_code}</slot>
        <zone>{visibility_zone}</zone>
        <temperature>{temp_zone}</temperature>
    </position>
    
    <context>
        <adjacent_products>{adjacent_list}</adjacent_products>
        <device_type>{device_type}</device_type>
        <location_type>{venue_type}</location_type>
    </context>
    
    <task>
        Score this placement from 0-100 considering:
        1. Visibility and accessibility
        2. Product velocity match to position value
        3. Temperature zone requirements
        4. Adjacent product affinity
        5. Category clustering
        
        Return JSON: {score, reasoning, constraints_passed}
    </task>
</placement_analysis>
```

### Token Optimization

```python
class TokenOptimizer:
    def optimize_prompt(self, prompt: str, max_tokens: int) -> str:
        # Remove redundant whitespace
        prompt = ' '.join(prompt.split())
        
        # Truncate repetitive data
        if len(prompt) > max_tokens * 4:
            sections = prompt.split('\n\n')
            essential = sections[:3] + ['...'] + sections[-2:]
            prompt = '\n\n'.join(essential)
        
        return prompt
    
    def estimate_tokens(self, text: str) -> int:
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
```

### Streaming Implementation

```python
async def stream_analysis(self, planogram_data):
    """Stream AI analysis progressively to UI"""
    
    async with self.client.messages.stream(
        model="claude-3-sonnet-20240229",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    ) as stream:
        async for chunk in stream:
            if chunk.type == 'content_block_delta':
                yield {
                    'type': 'partial',
                    'content': chunk.delta.text
                }
        
        final = await stream.get_final_message()
        yield {
            'type': 'complete',
            'content': final.content[0].text
        }
```

---

## 6. Testing Strategy

### Test Coverage Matrix

| Component | Unit Tests | Integration | E2E | Performance |
|-----------|------------|-------------|-----|-------------|
| Real-time Assistant | ✓ | ✓ | ✓ | <500ms |
| Revenue Predictor | ✓ | ✓ | ✓ | <7s |
| Heat Zone Analysis | ✓ | ✓ | ✓ | <100ms |
| Affinity Engine | ✓ | ✓ | ✓ | <3s |
| Demand Forecaster | ✓ | ✓ | ✓ | <5s |
| Location Personalizer | ✓ | ✓ | ✓ | <10s |
| Route Optimizer | ✓ | ✓ | ✓ | <15s |

### A/B Testing Framework

```python
class ABTestFramework:
    def create_experiment(self, name: str, hypothesis: str):
        """Create new A/B test experiment"""
        return {
            'id': generate_id(),
            'name': name,
            'hypothesis': hypothesis,
            'control_group': [],
            'treatment_group': [],
            'metrics': {
                'revenue': [],
                'stockouts': [],
                'service_time': []
            },
            'status': 'active'
        }
    
    def calculate_significance(self, control, treatment):
        """Calculate statistical significance"""
        from scipy import stats
        
        t_stat, p_value = stats.ttest_ind(control, treatment)
        effect_size = (np.mean(treatment) - np.mean(control)) / np.std(control)
        
        return {
            'p_value': p_value,
            'effect_size': effect_size,
            'significant': p_value < 0.05
        }
```

### AI Accuracy Validation

```python
def validate_predictions(predictions, actuals):
    """Validate AI prediction accuracy"""
    
    mape = np.mean(np.abs((actuals - predictions) / actuals)) * 100
    rmse = np.sqrt(np.mean((predictions - actuals) ** 2))
    r2 = 1 - (np.sum((actuals - predictions) ** 2) / 
              np.sum((actuals - np.mean(actuals)) ** 2))
    
    return {
        'mape': mape,  # Target: <15%
        'rmse': rmse,
        'r2_score': r2,  # Target: >0.8
        'within_confidence': calculate_confidence_accuracy(predictions, actuals)
    }
```

---

## 7. Deployment Plan

### Infrastructure Stack

```yaml
# docker-compose.yml (Production)
version: '3.8'

services:
  app:
    image: cvd-app:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
    environment:
      - DATABASE_URL=sqlite:///data/cvd.db
      - REDIS_URL=redis://...
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    
  ai-worker:
    image: cvd-ai-worker:latest
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '4'
          memory: 8G
    command: celery worker -A ai_services
    
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "443:443"
      
  redis:
    image: redis:7-alpine
    deploy:
      resources:
        limits:
          memory: 2G
  # SQLite database file mounted as volume
  # No separate database container needed
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy AI Planogram

on:
  push:
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit
          
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          aws ecs update-service \
            --cluster cvd-cluster \
            --service cvd-app \
            --force-new-deployment
            
      - name: Run smoke tests
        run: ./scripts/smoke-test.sh $PROD_URL
        
      - name: Monitor deployment
        run: |
          aws cloudwatch get-metric-statistics \
            --namespace AWS/ECS \
            --metric-name CPUUtilization \
            --dimensions Name=ServiceName,Value=cvd-app
```

### Monitoring & Observability

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

ai_requests = Counter('ai_requests_total', 'Total AI requests', ['service', 'model'])
ai_latency = Histogram('ai_request_duration_seconds', 'AI request latency', ['service'])
ai_accuracy = Gauge('ai_prediction_accuracy', 'AI prediction accuracy', ['model'])
token_usage = Counter('ai_tokens_used', 'Total tokens consumed', ['model'])

# Custom metrics endpoint
@app.route('/metrics')
def metrics():
    return generate_latest()
```

---

## 8. Implementation Timeline

### Phase 1: Foundation (Weeks 1-2)
**Goal:** MVP with core AI features

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 1 | • Set up AI services structure<br>• Implement real-time assistant<br>• Create basic UI feedback<br>• Database migrations | Working real-time scoring |
| 2 | • Revenue prediction engine<br>• Heat zone analysis<br>• Integration testing<br>• Performance optimization | MVP release |

### Phase 2: Enhancement (Weeks 3-6)
**Goal:** Advanced AI capabilities

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 3-4 | • Product affinity engine<br>• Demand forecasting<br>• Enhanced visualizations | Affinity clustering live |
| 5-6 | • Location personalization<br>• A/B testing framework<br>• Batch optimization | Full feature set |

### Phase 3: Scale (Weeks 7-12)
**Goal:** Production optimization

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 7-8 | • Route optimization<br>• Service scheduling AI<br>• Performance tuning | Route AI live |
| 9-10 | • Monitoring dashboards<br>• Cost optimization<br>• Documentation | Observability complete |
| 11-12 | • User training<br>• Rollout to full fleet<br>• Performance validation | Full production |

---

## 9. Risk Management

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| API rate limits | Medium | High | Implement caching, batch requests |
| Model accuracy | Low | High | A/B testing, human validation |
| Response time SLA | Medium | Medium | Optimize prompts, use Haiku |
| Infrastructure costs | Low | Medium | Monitor usage, set budgets |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| User adoption | Medium | High | Training, gradual rollout |
| ROI achievement | Low | High | Track metrics, iterate quickly |
| Competitor response | Medium | Low | Rapid innovation cycle |

### Contingency Plans

1. **API Failure**: Fallback to rule-based system
2. **Performance Issues**: Degrade to basic features
3. **Budget Overrun**: Implement usage caps
4. **Low Adoption**: Enhanced training, UI improvements

---

## 10. Success Metrics

### Technical KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Real-time response | <500ms p95 | APM monitoring |
| API availability | 99.9% | Uptime monitoring |
| Cache hit rate | >40% | Redis metrics |
| Error rate | <1% | Error tracking |

### Business KPIs

| Metric | Baseline | Target (90 days) | Measurement |
|--------|----------|------------------|-------------|
| Revenue per device | $100/day | $120/day (+20%) | Sales data |
| Stockout frequency | 15% | 10% (-33%) | Inventory system |
| Planogram creation time | 45 min | 10 min (-78%) | User analytics |
| Service cost | $50/week | $42/week (-16%) | Operations data |

### AI Performance Metrics

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| Placement recommendation accuracy | 85% | A/B testing |
| Revenue prediction MAPE | <15% | Historical comparison |
| Demand forecast MAPE | <20% | Actual vs predicted |
| User acceptance rate | >60% | Recommendation tracking |

---

## Implementation Checklist

### Week 1
- [ ] Set up development environment
- [ ] Create AI services module structure
- [ ] Implement Claude API client
- [ ] Database migrations
- [ ] Basic real-time scoring
- [ ] Initial UI integration

### Week 2
- [ ] Revenue prediction engine
- [ ] Heat zone analysis
- [ ] Caching implementation
- [ ] Integration testing
- [ ] Performance optimization
- [ ] MVP deployment

### Week 3-4
- [ ] Product affinity analysis
- [ ] Demand forecasting
- [ ] Enhanced visualizations
- [ ] A/B testing framework
- [ ] User training materials

### Week 5-6
- [ ] Location personalization
- [ ] Batch optimization
- [ ] Monitoring setup
- [ ] Documentation
- [ ] Staging deployment

### Week 7-12
- [ ] Route optimization
- [ ] Full production rollout
- [ ] Performance validation
- [ ] Cost optimization
- [ ] Success metrics review

---

## Appendices

### A. API Documentation
Complete API specifications available in `/docs/api/`

### B. Database Schema
Full schema documentation in `/docs/database/`

### C. Testing Procedures
Detailed test plans in `/tests/ai-planogram-test-strategy.md`

### D. Deployment Runbooks
Operational procedures in `/deployment/README.md`

### E. Training Materials
User guides and training videos in `/docs/training/`

---

## Conclusion

This master implementation plan provides a comprehensive roadmap for transforming CVD's planogram management with AI capabilities. By following this structured approach, the team can deliver incremental value while building toward a transformative system that achieves the projected 800-1,100% ROI.

The plan balances ambitious goals with practical implementation concerns, ensuring that each phase delivers measurable business value while maintaining system stability and user satisfaction.

**Next Steps:**
1. Review and approve the implementation plan
2. Allocate resources (2 developers, 1 QA engineer)
3. Set up development environment
4. Begin Phase 1 implementation
5. Schedule weekly progress reviews

---

*Document Version: 1.0*
*Last Updated: 2025*
*Owner: CVD Development Team*