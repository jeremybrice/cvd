# Vending Machine Feature Implementation Workflow

This workflow coordinates multiple agents for implementing CVD-specific features.

## Workflow: Add New Vending Machine Feature

### Phase 1: Requirements & Design
**Lead:** product-manager
**Support:** merchandising-analyst, system-architect

```markdown
1. Product Manager:
   - Gather business requirements
   - Define user stories
   - Set success metrics
   
2. Merchandising Analyst:
   - Analyze impact on sales/operations
   - Define optimization opportunities
   - Set performance targets
   
3. System Architect:
   - Design technical solution
   - Define API contracts
   - Plan database changes
```

### Phase 2: Implementation
**Lead:** backend-engineer, frontend-engineer
**Support:** designer

```markdown
4. Backend Engineer:
   - Create database migrations
   - Implement API endpoints
   - Add business logic
   - Update service_order_service.py if needed
   
5. Frontend Engineer:
   - Build UI components
   - Integrate with API
   - Implement offline support for PWA
   - Update navigation in index.html
   
6. Designer:
   - Review UI/UX
   - Ensure mobile responsiveness
   - Validate accessibility
```

### Phase 3: Testing & Security
**Lead:** qa-test-engineer, security-analyst

```markdown
7. QA Test Engineer:
   - Write test cases
   - Test edge cases
   - Verify PWA functionality
   - Test offline scenarios
   
8. Security Analyst:
   - Review authentication/authorization
   - Check for vulnerabilities
   - Validate data encryption
   - Audit role-based access
```

### Phase 4: Deployment & Documentation
**Lead:** deployment-engineer, documentation-specialist

```markdown
9. Deployment Engineer:
   - Update deployment scripts
   - Configure service worker
   - Set up monitoring
   - Deploy to staging
   
10. Documentation Specialist:
    - Update CLAUDE.md
    - Document API changes
    - Create user guides
    - Update context files
```

## Workflow: Optimize Service Order Process

### Phase 1: Analysis
**Agents:** merchandising-analyst + debugger

```bash
# Analyze current performance
@merchandising-analyst analyze service order efficiency for last 30 days
@debugger profile service_order_service.py for bottlenecks
```

### Phase 2: Optimization
**Agents:** system-architect + backend-engineer

```bash
# Design improvements
@system-architect design optimized pick list generation algorithm
@backend-engineer implement batch processing for multi-cabinet orders
```

### Phase 3: Testing
**Agents:** qa-test-engineer

```bash
# Verify improvements
@qa-test-engineer create performance benchmarks
@qa-test-engineer test with 100+ simultaneous orders
```

## Workflow: Enhance Planogram AI

### Phase 1: Data Analysis
**Agents:** merchandising-analyst

```bash
@merchandising-analyst analyze planogram performance across all devices
@merchandising-analyst identify optimization patterns
```

### Phase 2: AI Enhancement
**Agents:** backend-engineer + system-architect

```bash
@system-architect design enhanced AI optimization algorithm
@backend-engineer integrate with Claude API for recommendations
```

### Phase 3: UI Updates
**Agents:** frontend-engineer + designer

```bash
@frontend-engineer add AI recommendations panel to NSPT.html
@designer create intuitive visualization for recommendations
```

## Agent Handoff Protocols

### Context Transfer Template
```markdown
## Handoff from [Agent A] to [Agent B]

### Completed Work
- [List what was done]
- [Key decisions made]
- [Files modified]

### Next Steps
- [What needs to be done]
- [Specific requirements]
- [Dependencies]

### Important Context
- [Critical information]
- [Potential issues]
- [Testing needs]

### Files to Review
- [Primary files]
- [Related files]
- [Documentation]
```

### Example Handoff
```markdown
## Handoff from backend-engineer to frontend-engineer

### Completed Work
- Created /api/service-orders/optimize endpoint
- Returns optimized pick list with warehouse locations
- Added caching for 5-minute TTL

### Next Steps
- Add "Optimize" button to service-orders.html
- Display optimized pick list with grouping
- Show estimated time savings

### Important Context
- Response includes 'optimization_score' (0-100)
- Groups products by warehouse aisle
- Includes 'estimated_minutes' for picking

### Files to Review
- /home/jbrice/Projects/365/service_order_service.py (lines 450-550)
- /home/jbrice/Projects/365/api.js (add new endpoint)
- /home/jbrice/Projects/365/pages/service-orders.html
```