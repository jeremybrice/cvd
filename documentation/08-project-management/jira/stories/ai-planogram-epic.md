# AI Planogram Enhancement - JIRA Stories

## EPIC: AI-Powered Planogram Enhancement System

**Epic Title**  
Implement AI-Powered Planogram Optimization System

---

**Epic Description**

Transform CVD's planogram management with intelligent AI capabilities that provide real-time placement recommendations, revenue predictions, and data-driven optimization. This epic encompasses the complete implementation of AI features into the existing NSPT.html planogram interface, delivering measurable ROI through improved product placement and reduced stockouts.

**Target Outcomes:**
- 20-30% revenue increase per device
- 70% reduction in planogram creation time
- 30% reduction in stockouts
- 15% reduction in service costs

**Phases:**
1. **Phase 1 (Weeks 1-2):** MVP Foundation - Real-time AI feedback, revenue prediction, heat zones
2. **Phase 2 (Weeks 3-6):** Enhancement - Product affinity, demand forecasting, personalization
3. **Phase 3 (Weeks 7-12):** Scale - Route optimization, production deployment, monitoring

---

## Phase 1 Stories (MVP - Weeks 1-2)

### Story 1: Setup AI Services Infrastructure

**Story Title**  
Initialize AI Services Module and Claude API Integration

---

**Background / Context**

Currently, the CVD application operates without AI assistance for planogram optimization. Merchandising managers spend 45+ minutes manually creating planograms based on intuition rather than data-driven insights. This leads to suboptimal product placement and missed revenue opportunities. We need to establish the foundational AI infrastructure to enable intelligent features throughout the planogram management system.

---

**Feature Requirements / Functional Behavior**

**UI Behavior**
* No direct UI changes in this story
* System continues to function normally during infrastructure setup
* Existing planogram functionality remains unchanged

**System Logic**
* Create new `/ai_services/` module structure in the codebase
* Implement Claude API client wrapper with retry logic and error handling
* Setup multi-tier caching system (L1 Memory, L2 Redis, L3 SQLite)
* Configure environment variables for ANTHROPIC_API_KEY
* Implement token optimization and rate limiting
* Create base exception handling for AI service failures
* Setup logging for AI service calls and responses
* Implement fallback mechanisms when AI is unavailable

---

**Acceptance Tests**

**Test 1: AI Service Initialization**
* **Steps**:
  1. Set ANTHROPIC_API_KEY in environment
  2. Start the application
  3. Check logs for AI service initialization
* **Expected Result**: AI services initialize successfully with "AI Services Ready" log entry

**Test 2: API Key Validation**
* **Steps**:
  1. Configure invalid API key
  2. Start the application
  3. Attempt to load planogram page
* **Expected Result**: Application starts normally, planogram works without AI features, warning logged

**Test 3: Cache Layer Verification**
* **Steps**:
  1. Make identical AI request twice
  2. Check response times
  3. Verify cache hit in logs
* **Expected Result**: Second request returns from cache in <50ms

**Test 4: Rate Limiting**
* **Steps**:
  1. Send 10 rapid AI requests
  2. Monitor response behavior
* **Expected Result**: Requests are throttled appropriately, no API errors

---

**Technical Notes / Considerations**
* Use anthropic==0.57.1 Python package
* Implement exponential backoff for retries
* Cache TTL: 5 minutes for real-time, 1 hour for analysis
* Store API key in AWS Secrets Manager for production
* Monitor token usage to control costs
* Consider implementing request batching for efficiency
* Database migrations for new AI tables (ai_predictions, zone_performance)

---

### Story 2: Implement Real-time Placement Scoring

**Story Title**  
Add Real-time AI Scoring for Product Placement in Planograms

---

**Background / Context**

Merchandising managers currently place products in planogram slots without immediate feedback on placement quality. They must rely on sales data weeks later to determine if their decisions were optimal. This delay prevents rapid iteration and learning. By providing instant AI-powered placement scoring, managers can make better decisions during the planning process, leading to immediate revenue improvements.

---

**Feature Requirements / Functional Behavior**

**UI Behavior**
* Add floating AI feedback panel (360px wide on desktop, bottom sheet on mobile)
* Display placement score (0-100) with color coding:
  - 80-100: Green (#28a745)
  - 60-79: Yellow (#ffc107)
  - 0-59: Red (#dc3545)
* Show reasoning text below score
* Panel appears on product drag, updates during drag
* Smooth fade-in animation (250ms)
* Panel follows product during drag with 16px offset
* Include minimize/maximize toggle button

**System Logic**
* Call `/api/planograms/realtime/score` endpoint on drag events
* Throttle API calls to maximum 2 per second
* Calculate score based on:
  - Zone visibility (eye-level = higher score)
  - Product velocity match to position value
  - Temperature zone requirements
  - Adjacent product compatibility
  - Category clustering
* Cache scores for 5 minutes per product-slot combination
* Return score within 500ms SLA
* Include constraint validation (temperature, weight limits)

---

**Acceptance Tests**

**Test 1: Drag Product to Optimal Position**
* **Steps**:
  1. Open planogram for device VM-001
  2. Drag Coca-Cola to eye-level position B3
  3. Observe AI panel during drag
* **Expected Result**: Score shows 85-95, green color, reasoning mentions "eye-level placement for high-velocity product"

**Test 2: Drag Product to Poor Position**
* **Steps**:
  1. Open planogram for device VM-001
  2. Drag premium water to bottom row position E1
  3. Observe AI panel
* **Expected Result**: Score shows 30-45, red color, reasoning mentions "low visibility for high-margin product"

**Test 3: Mobile Responsive Behavior**
* **Steps**:
  1. Open planogram on mobile device
  2. Drag any product
  3. Observe panel position
* **Expected Result**: Panel appears as bottom sheet, swipeable to see full content

**Test 4: API Failure Handling**
* **Steps**:
  1. Disable network connection
  2. Drag product in planogram
  3. Observe behavior
* **Expected Result**: Planogram continues to work, no AI panel shown, no errors displayed

**Test 5: Performance Under Load**
* **Steps**:
  1. Rapidly drag products between multiple positions
  2. Monitor response times
* **Expected Result**: All scores return within 500ms, no lag in drag functionality

---

**Technical Notes / Considerations**
* Use Claude Haiku model for sub-500ms responses
* Implement WebSocket connection for lower latency
* Add performance monitoring for p50, p95, p99 metrics
* Consider pre-computing scores for common products
* Store scoring history for analytics
* Add feature flag to enable/disable AI scoring
* Ensure drag-and-drop remains smooth even with AI calls

---

### Story 3: Create Revenue Impact Prediction

**Story Title**  
Display Revenue Predictions for Planogram Changes

---

**Background / Context**

Operations directors and merchandising managers need to understand the financial impact of planogram changes before implementing them. Currently, they make changes and wait weeks to see if revenue improves. This story adds predictive analytics that show expected revenue impact immediately when changes are made, enabling data-driven decision making and faster optimization cycles.

---

**Feature Requirements / Functional Behavior**

**UI Behavior**
* Add revenue prediction card to right sidebar (320px wide)
* Display metrics:
  - Current daily revenue: $XXX.XX
  - Predicted daily revenue: $XXX.XX
  - Revenue change: +/- $XX.XX (XX%)
  - Confidence interval: $XXX - $XXX
  - ROI timeline: "Break even in X days"
* Use up/down arrow icons for positive/negative changes
* Color code changes (green for positive, red for negative)
* Update predictions within 2 seconds of planogram change
* Include "Calculate Impact" button for manual refresh
* Show loading skeleton during calculation

**System Logic**
* Call `/api/planograms/predict/revenue` on planogram save
* Analyze last 90 days of sales data for baseline
* Factor in:
  - Product placement changes
  - Historical performance in similar positions
  - Seasonal trends
  - Day of week patterns
  - Location-specific factors
* Use ensemble model combining ML and Claude Sonnet
* Return predictions within 7 seconds
* Store predictions for later validation
* Track prediction accuracy for model improvement

---

**Acceptance Tests**

**Test 1: Positive Revenue Impact**
* **Steps**:
  1. Open planogram with suboptimal layout
  2. Move high-velocity items to eye-level
  3. Click "Calculate Impact"
* **Expected Result**: Shows positive revenue increase 10-20%, break-even immediate

**Test 2: Negative Revenue Impact**
* **Steps**:
  1. Open optimized planogram
  2. Move bestsellers to bottom row
  3. Observe prediction update
* **Expected Result**: Shows negative revenue impact -15-25%, red indicators

**Test 3: Confidence Intervals**
* **Steps**:
  1. Make minor change (1 product)
  2. Note confidence interval
  3. Make major changes (10+ products)
  4. Compare confidence intervals
* **Expected Result**: Major changes show wider confidence intervals

**Test 4: Historical Validation**
* **Steps**:
  1. View planogram changed 30 days ago
  2. Check stored prediction
  3. Compare to actual revenue
* **Expected Result**: Actual revenue within confidence interval

**Test 5: Loading State**
* **Steps**:
  1. Make planogram change
  2. Immediately observe prediction panel
* **Expected Result**: Skeleton loader shows, then results appear within 7 seconds

---

**Technical Notes / Considerations**
* Cache baseline calculations for 1 hour
* Use SQLite with proper indexing for analytics queries
* Implement gradual rollout with A/B testing
* Track MAPE (Mean Absolute Percentage Error) < 15%
* Consider seasonal adjustment factors
* Store predictions in ai_predictions table
* Add export functionality for predictions
* Implement confidence scoring algorithm

---

### Story 4: Implement Visual Heat Zone Analysis

**Story Title**  
Add Heat Map Overlay Showing Revenue Potential by Zone

---

**Background / Context**

Planogram creators lack visual understanding of which slots generate the most revenue. They treat all positions equally when some slots naturally perform 3-4x better than others due to visibility and accessibility. Adding a heat map overlay will immediately show high-value zones, helping managers place high-margin products in optimal positions for maximum revenue generation.

---

**Feature Requirements / Functional Behavior**

**UI Behavior**
* Add toggle button "Show Heat Zones" in planogram toolbar
* Overlay semi-transparent heat map on planogram grid
* Color gradient from blue (low) to red (high):
  - Level 5 (Highest): #dc3545 (90-100% revenue potential)
  - Level 4: #fd7e14 (70-89% revenue potential)
  - Level 3: #ffc107 (50-69% revenue potential)
  - Level 2: #0dcaf0 (30-49% revenue potential)
  - Level 1 (Lowest): #0d6efd (0-29% revenue potential)
* Opacity at 40% to maintain product visibility
* Show exact percentage on hover tooltip
* Include legend in bottom-left corner
* Smooth fade transition when toggling (350ms)
* Maintain heat map during drag operations

**System Logic**
* Calculate zones based on:
  - Eye-level premium (rows B-C get 1.5x multiplier)
  - Reach accessibility (top/bottom rows get 0.7x multiplier)
  - Left-right scan patterns (left side slight premium)
  - Door proximity for grab-and-go items
  - Temperature zones for refrigerated units
* Pull historical performance data by position
* Update heat map when device type changes
* Cache zone calculations for 24 hours
* Adjust for device-specific patterns

---

**Acceptance Tests**

**Test 1: Heat Map Toggle**
* **Steps**:
  1. Open planogram editor
  2. Click "Show Heat Zones" button
  3. Observe overlay appearance
  4. Click button again to hide
* **Expected Result**: Heat map fades in/out smoothly, button shows active state

**Test 2: Eye-Level Premium Zones**
* **Steps**:
  1. Enable heat map
  2. Examine rows B and C
  3. Compare to rows A and E
* **Expected Result**: Rows B-C show red/orange (high value), rows A/E show blue/cyan (lower value)

**Test 3: Hover Information**
* **Steps**:
  1. Enable heat map
  2. Hover over different zones
  3. Read tooltip values
* **Expected Result**: Tooltip shows "Revenue Potential: XX%" with exact percentage

**Test 4: Drag with Heat Map**
* **Steps**:
  1. Enable heat map
  2. Drag product across grid
  3. Observe heat map visibility
* **Expected Result**: Heat map remains visible, product draggable above overlay

**Test 5: Device-Specific Patterns**
* **Steps**:
  1. View heat map for snack machine
  2. Switch to beverage cooler
  3. Compare heat patterns
* **Expected Result**: Different patterns based on device type (coolers favor eye-level more)

**Test 6: Mobile Responsiveness**
* **Steps**:
  1. Open on tablet/mobile
  2. Enable heat map
  3. Pinch to zoom
* **Expected Result**: Heat map scales properly, remains aligned with grid

---

**Technical Notes / Considerations**
* Use CSS Grid for overlay alignment
* Implement with Canvas API for performance
* Calculate zones using zone_performance table
* Consider WebGL for complex visualizations
* Add print styles to hide overlay
* Store zone data in IndexedDB for offline
* Update calculations weekly based on new data
* Consider customizable heat map themes

---

### Story 5: Database Schema Updates for AI Features

**Story Title**  
Create Database Tables and Migrations for AI System

---

**Background / Context**

The AI features require new database tables to store predictions, performance metrics, zone analytics, and experiment data. Without proper data persistence, the system cannot track accuracy, learn from outcomes, or provide historical analysis. These schema changes establish the foundation for all AI-powered features and enable continuous improvement through data collection.

---

**Feature Requirements / Functional Behavior**

**UI Behavior**
* No direct UI changes
* Existing functionality continues uninterrupted
* Migration runs automatically on deployment

**System Logic**
* Create migration script for new tables:
  - ai_predictions: Store all AI predictions with confidence scores
  - zone_performance: Track revenue by planogram position
  - product_affinity: Store product relationship scores
  - ai_experiments: Manage A/B testing data
* Add indexes for query performance
* Include soft delete capability
* Set up automatic data retention (90 days for predictions)
* Create views for common analytics queries
* Add triggers for audit logging
* Implement partitioning for large tables

---

**Acceptance Tests**

**Test 1: Migration Execution**
* **Steps**:
  1. Run migration script on test database
  2. Check for errors
  3. Verify all tables created
* **Expected Result**: Migration completes successfully, all 4 tables exist

**Test 2: Data Persistence**
* **Steps**:
  1. Make AI prediction through API
  2. Query ai_predictions table
  3. Verify data stored correctly
* **Expected Result**: Prediction data present with timestamp and confidence score

**Test 3: Performance Queries**
* **Steps**:
  1. Insert 10,000 test predictions
  2. Run analytics query
  3. Check execution time
* **Expected Result**: Query returns in <100ms with proper indexes

**Test 4: Retention Policy**
* **Steps**:
  1. Insert prediction with created_at 91 days ago
  2. Run retention cleanup job
  3. Query for old prediction
* **Expected Result**: Old prediction removed, recent data retained

**Test 5: Rollback Capability**
* **Steps**:
  1. Apply migration
  2. Run rollback script
  3. Check table existence
* **Expected Result**: All AI tables removed cleanly, system continues to function

---

**Technical Notes / Considerations**
* Use Alembic or similar for migration management
* Use SQLite for both development and production
* Add composite indexes for common JOIN operations
* Implement table partitioning by month for predictions
* Optimize SQLite for concurrent reads
* Add VACUUM schedule for SQLite optimization
* Document all schema changes in /docs/database/
* Consider JSONB columns for flexible prediction data
* Add database monitoring for table growth

---

## Phase 2 Stories (Weeks 3-6)

### Story 6: Product Affinity Analysis

**Story Title**  
Implement AI-Powered Product Affinity Recommendations

---

**Background / Context**

Merchandising managers currently place products without understanding which items sell better together. Customer purchase patterns show that certain products have strong affinities (chips with drinks, candy with coffee), but this insight isn't available during planogram creation. By analyzing transaction data and providing affinity-based recommendations, we can increase basket size and improve customer satisfaction through better product adjacency.

---

**Feature Requirements / Functional Behavior**

**UI Behavior**
* Add "Suggested Neighbors" panel when product is selected
* Display top 3 affinity products with scores:
  - Strong Affinity (80-100): Green badge with checkmark icon
  - Moderate Affinity (50-79): Yellow badge with info icon  
  - Weak Affinity (0-49): Gray badge, no icon
* Show lift percentage: "28% more likely to sell together"
* Highlight suggested positions with pulsing green border
* Click suggestion to auto-place product
* Panel slides in from right (350ms animation)

**System Logic**
* Analyze last 180 days of transaction data
* Calculate lift scores using market basket analysis
* Update affinity matrix weekly via batch job
* Consider:
  - Co-purchase frequency
  - Category relationships
  - Time-of-day patterns
  - Seasonal correlations
* Store in product_affinity table
* Return suggestions within 1 second
* Account for space constraints

---

**Acceptance Tests**

**Test 1: High Affinity Products**
* **Steps**:
  1. Select Coca-Cola in planogram
  2. View Suggested Neighbors panel
  3. Verify chips/snacks appear
* **Expected Result**: Shows chips with 85+ affinity score, "32% more likely to sell together"

**Test 2: Auto-Placement**
* **Steps**:
  1. Select coffee product
  2. Click on suggested donut item
  3. Observe planogram update
* **Expected Result**: Donut placed adjacent to coffee, positions highlighted briefly

**Test 3: No Affinity Data**
* **Steps**:
  1. Select new product with no sales history
  2. Check suggestions panel
* **Expected Result**: Shows "Insufficient data for recommendations" message

**Test 4: Space Constraints**
* **Steps**:
  1. Select product in full planogram
  2. View suggestions
  3. Verify placement options
* **Expected Result**: Only suggests products that fit in available spaces

**Test 5: Affinity Trends**
* **Steps**:
  1. View affinity in summer for ice cream
  2. Compare to winter affinity
* **Expected Result**: Seasonal products show different affinities by season

---

**Technical Notes / Considerations**
* Use Apache Spark or similar for market basket analysis
* Implement FP-Growth algorithm for efficiency
* Minimum 10 transactions for affinity calculation
* Cache affinity scores in Redis
* Consider real-time updates for high-velocity items
* Add configuration for affinity thresholds
* Track suggestion acceptance rate
* A/B test affinity-based layouts

---

### Story 7: Demand Forecasting Integration

**Story Title**  
Add AI Demand Forecasting to Prevent Stockouts

---

**Background / Context**

Service teams currently stock machines based on static par levels, leading to frequent stockouts of popular items and overstocking of slow movers. This wastes service time, reduces revenue, and frustrates customers. By implementing AI-powered demand forecasting that considers multiple factors, we can optimize stock levels, reduce stockouts by 30%, and improve service efficiency.

---

**Feature Requirements / Functional Behavior**

**UI Behavior**
* Add "Demand Forecast" tab in planogram editor
* Display 7-day demand forecast for each product:
  - Daily units expected with confidence intervals
  - Stock-out risk indicator (High/Medium/Low)
  - Suggested par level adjustments
  - Graphical trend line with shaded confidence bands
* Color code by risk:
  - High risk (>70%): Red background
  - Medium risk (30-70%): Yellow background
  - Low risk (<30%): Green background
* Include "Apply Suggestions" button to update par levels
* Show factors influencing forecast (weather, events, seasonality)

**System Logic**
* Use time series analysis (Prophet or similar)
* Consider factors:
  - Historical sales patterns
  - Day of week/month seasonality
  - Weather forecast integration
  - Local events calendar
  - Holiday schedules
  - Recent trend changes
* Update forecasts every 6 hours
* Calculate safety stock recommendations
* Generate service order adjustments
* Track forecast accuracy (MAPE target <20%)

---

**Acceptance Tests**

**Test 1: Weekday vs Weekend Forecast**
* **Steps**:
  1. View forecast for office building location
  2. Compare Monday vs Saturday forecasts
  3. Check coffee/snack predictions
* **Expected Result**: Weekday shows 3-4x higher demand for coffee/snacks

**Test 2: Weather Impact**
* **Steps**:
  1. View forecast during heat wave prediction
  2. Check cold beverage forecasts
  3. Compare to normal weather
* **Expected Result**: Cold drinks show 40-60% increased demand during heat

**Test 3: Stock-out Prevention**
* **Steps**:
  1. Identify high-risk item
  2. Apply suggested par level
  3. Monitor actual vs predicted
* **Expected Result**: Stock-out risk reduces to <10% with new par level

**Test 4: Event-Based Spikes**
* **Steps**:
  1. Add local sports event to calendar
  2. View forecast for game day
  3. Check beverage/snack predictions
* **Expected Result**: 2-3x demand spike predicted for event day

**Test 5: Forecast Accuracy Tracking**
* **Steps**:
  1. Compare week-old forecast to actual sales
  2. Calculate MAPE
  3. View accuracy dashboard
* **Expected Result**: MAPE <20% for 80% of products

---

**Technical Notes / Considerations**
* Integrate weather API (OpenWeatherMap or similar)
* Use Facebook Prophet for time series forecasting
* Implement ensemble model for better accuracy
* Store forecasts for accuracy tracking
* Consider real-time adjustments for rapid changes
* Add manual override capability
* Cache forecasts for 6 hours
* Implement gradual par level changes
* Monitor and alert on forecast drift

---

## Infrastructure & Deployment Stories

### Story 8: Setup Docker Containerization

**Story Title**  
Containerize AI Services for Development and Production

---

**Background / Context**

The AI services have different dependencies and resource requirements than the main application. Without proper containerization, deployment is complex, environments drift, and scaling is difficult. Docker containers will ensure consistent environments, simplify deployment, and enable independent scaling of AI workloads.

---

**Feature Requirements / Functional Behavior**

**UI Behavior**
* No UI changes
* System maintains full functionality

**System Logic**
* Create Dockerfile for main application
* Create separate Dockerfile for AI worker services
* Setup docker-compose.yml for local development:
  - App container (Flask application)
  - AI worker container (Celery workers)
  - SQLite database
  - Redis cache
  - Nginx reverse proxy
* Configure production docker-compose with:
  - Resource limits (CPU, memory)
  - Health checks
  - Restart policies
  - Volume mounts for data persistence
* Implement proper secrets management
* Setup container registry (Docker Hub/ECR)

---

**Acceptance Tests**

**Test 1: Local Development Setup**
* **Steps**:
  1. Run `docker-compose up`
  2. Access application at localhost:8000
  3. Test AI features
* **Expected Result**: Full application runs with all AI features functional

**Test 2: Container Health Checks**
* **Steps**:
  1. Start containers
  2. Kill AI worker process
  3. Monitor container status
* **Expected Result**: Container auto-restarts, service recovers within 30 seconds

**Test 3: Resource Limits**
* **Steps**:
  1. Generate high AI load
  2. Monitor container resources
  3. Check for throttling
* **Expected Result**: Container respects memory/CPU limits, doesn't crash

**Test 4: Data Persistence**
* **Steps**:
  1. Create planogram with AI features
  2. Stop and remove containers
  3. Restart containers
  4. Check data exists
* **Expected Result**: All data persists across container restarts

**Test 5: Production Build**
* **Steps**:
  1. Build production images
  2. Check image sizes
  3. Run security scan
* **Expected Result**: Images <500MB, no critical vulnerabilities

---

**Technical Notes / Considerations**
* Use multi-stage builds to reduce image size
* Pin all dependency versions
* Implement proper logging to stdout
* Use non-root user in containers
* Add .dockerignore file
* Consider Alpine Linux for smaller images
* Setup GitHub Actions for automated builds
* Implement container scanning in CI/CD
* Document all environment variables

---

### Story 9: Implement CI/CD Pipeline

**Story Title**  
Create Automated Testing and Deployment Pipeline

---

**Background / Context**

Manual deployment of AI features is error-prone and time-consuming. Without automated testing, bugs reach production. Without automated deployment, releases are delayed and inconsistent. A CI/CD pipeline will ensure code quality, automate testing, and enable rapid, reliable deployments of AI enhancements.

---

**Feature Requirements / Functional Behavior**

**UI Behavior**
* Add deployment status badge to repository README
* No changes to application UI

**System Logic**
* Setup GitHub Actions workflow:
  - Trigger on pull request and tag push
  - Run linting (flake8, eslint)
  - Execute unit tests (pytest)
  - Run integration tests
  - Check test coverage (>80%)
  - Build Docker images
  - Run security scans
  - Deploy to staging on merge to main
  - Deploy to production on version tag
* Implement smoke tests post-deployment
* Setup rollback capability
* Configure monitoring alerts
* Add deployment notifications to Slack

---

**Acceptance Tests**

**Test 1: Pull Request Validation**
* **Steps**:
  1. Create PR with code changes
  2. Push to GitHub
  3. Check Actions tab
* **Expected Result**: All tests run, status reported to PR within 5 minutes

**Test 2: Staging Deployment**
* **Steps**:
  1. Merge PR to main branch
  2. Monitor GitHub Actions
  3. Check staging environment
* **Expected Result**: Code deploys to staging within 10 minutes

**Test 3: Production Release**
* **Steps**:
  1. Create version tag v1.1.0
  2. Push tag to GitHub
  3. Monitor deployment
* **Expected Result**: Production deployment completes within 15 minutes

**Test 4: Failed Test Blocking**
* **Steps**:
  1. Create PR with failing test
  2. Try to merge
* **Expected Result**: Merge blocked until tests pass

**Test 5: Rollback Procedure**
* **Steps**:
  1. Deploy broken version
  2. Trigger rollback
  3. Verify previous version restored
* **Expected Result**: Rollback completes within 5 minutes

---

**Technical Notes / Considerations**
* Use GitHub Actions for CI/CD
* Implement blue-green deployment strategy
* Store secrets in GitHub Secrets
* Use semantic versioning for releases
* Implement database migration checks
* Add performance regression tests
* Setup deployment windows
* Document deployment procedures
* Monitor deployment metrics

---

## Summary

This document contains the initial JIRA stories for the AI Planogram Enhancement project, organized by phases:

**Phase 1 (Weeks 1-2) - MVP:**
1. Setup AI Services Infrastructure
2. Implement Real-time Placement Scoring
3. Create Revenue Impact Prediction
4. Implement Visual Heat Zone Analysis
5. Database Schema Updates for AI Features

**Phase 2 (Weeks 3-6) - Enhancement:**
6. Product Affinity Analysis
7. Demand Forecasting Integration

**Infrastructure & Deployment:**
8. Setup Docker Containerization
9. Implement CI/CD Pipeline

Each story follows the CVD JIRA story format with:
- Clear, action-oriented titles
- Comprehensive background/context
- Detailed UI and system behavior requirements
- 4-6 specific acceptance tests
- Technical implementation notes

Additional stories for Phase 3 (Scale & Optimization) and comprehensive testing/monitoring will be created in subsequent documents.