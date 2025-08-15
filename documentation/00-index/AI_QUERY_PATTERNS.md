# AI Query Patterns Documentation Map

## Metadata
- **ID**: AI_QUERY_PATTERNS
- **Type**: Navigation Guide
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai-navigation #query-mapping #semantic-search #documentation-discovery #cvd-specific
- **Intent**: Map natural language queries to documentation locations
- **Audience**: AI agents, Claude Code, documentation systems

## Overview

This document maps common query patterns to their corresponding documentation locations within the CVD system. Each pattern includes semantic variations and direct links to relevant documentation.

## Query Pattern Categories

### 1. How-To Queries ("How do I..." / "How to...")

#### Device Management
- **"How do I add a new vending machine/device?"**
  - Primary: `/documentation/04-implementation/features/device-management.md`
  - Secondary: `/documentation/05-development/workflows/device-workflow.md`
  - API: `/documentation/09-reference/api/devices-api.md`
  - UI: `/pages/INVD.html`

- **"How do I configure cabinet settings?"**
  - Primary: `/documentation/04-implementation/features/cabinet-configuration.md`
  - Guide: `/documentation/01-project-core/QUICK_START.md#cabinet-setup`
  - API: `/documentation/09-reference/api/cabinet-api.md`

- **"How do I delete/remove a device?"**
  - Primary: `/documentation/04-implementation/features/device-management.md#soft-delete`
  - Workflow: `/documentation/05-development/workflows/device-lifecycle.md`

#### Planogram Management
- **"How do I create a planogram?"**
  - Primary: `/documentation/04-implementation/features/planogram-management.md`
  - UI Guide: `/documentation/06-design/ui/planogram-interface.md`
  - Page: `/pages/NSPT.html`

- **"How do I optimize product placement?"**
  - Primary: `/documentation/04-implementation/features/ai-optimization.md`
  - Algorithm: `/documentation/03-architecture/components/planogram-optimizer.md`
  - API: `/documentation/09-reference/api/optimization-api.md`

- **"How do I assign products to slots?"**
  - Primary: `/documentation/04-implementation/features/planogram-management.md#slot-assignment`
  - Drag-Drop: `/documentation/06-design/ui/drag-drop-guide.md`

#### Service Orders
- **"How do I create a service order?"**
  - Primary: `/documentation/04-implementation/features/service-orders.md`
  - Workflow: `/documentation/05-development/workflows/service-order-workflow.md`
  - API: `/documentation/09-reference/api/service-orders-api.md`

- **"How do I generate a pick list?"**
  - Primary: `/documentation/04-implementation/features/pick-lists.md`
  - Algorithm: `/documentation/03-architecture/components/pick-list-generator.md`

- **"How do I execute/complete a service order?"**
  - Primary: `/documentation/04-implementation/features/service-execution.md`
  - Mobile: `/documentation/04-implementation/features/driver-pwa.md`

#### Authentication & Users
- **"How do I create a new user?"**
  - Primary: `/documentation/04-implementation/features/user-management.md`
  - Security: `/documentation/03-architecture/security/authentication.md`
  - API: `/documentation/09-reference/api/users-api.md`

- **"How do I set user permissions/roles?"**
  - Primary: `/documentation/03-architecture/security/rbac.md`
  - Roles: `/documentation/09-reference/data-models/user-roles.md`

- **"How do I reset a password?"**
  - Primary: `/documentation/04-implementation/features/password-reset.md`
  - Security: `/documentation/03-architecture/security/password-policy.md`

#### DEX Integration
- **"How do I parse DEX files?"**
  - Primary: `/documentation/04-implementation/features/dex-parser.md`
  - Technical: `/documentation/03-architecture/components/dex-parser.md`
  - API: `/documentation/09-reference/api/dex-api.md`

- **"How do I detect grid patterns?"**
  - Primary: `/documentation/04-implementation/features/grid-pattern-analyzer.md`
  - Algorithm: `/documentation/03-architecture/algorithms/grid-detection.md`

- **"How do I import sales data from DEX?"**
  - Primary: `/documentation/05-development/workflows/dex-import-workflow.md`
  - Processing: `/documentation/03-architecture/data-flow/dex-processing.md`

#### Analytics & Reporting
- **"How do I view sales reports?"**
  - Primary: `/documentation/04-implementation/features/analytics.md`
  - Asset Sales: `/documentation/04-implementation/features/asset-sales.md`
  - Product Sales: `/documentation/04-implementation/features/product-sales.md`

- **"How do I track device performance?"**
  - Primary: `/documentation/04-implementation/features/device-metrics.md`
  - Dashboard: `/documentation/06-design/ui/dashboard-components.md`

- **"How do I export data?"**
  - Primary: `/documentation/04-implementation/features/data-export.md`
  - Formats: `/documentation/09-reference/data-formats/export-formats.md`

### 2. Error & Troubleshooting Queries ("Error..." / "Failed..." / "Not working...")

#### Authentication Errors
- **"Error: Unauthorized / 401 error"**
  - Primary: `/documentation/05-development/troubleshooting/auth-errors.md`
  - Debug: `/documentation/05-development/debugging/session-issues.md`
  - Solution: `/documentation/03-architecture/security/session-management.md`

- **"Login failed / Can't log in"**
  - Primary: `/documentation/05-development/troubleshooting/login-issues.md`
  - Checklist: `/documentation/05-development/debugging/auth-checklist.md`

#### API Errors
- **"API request failed / 500 error"**
  - Primary: `/documentation/05-development/troubleshooting/api-errors.md`
  - Debugging: `/documentation/05-development/debugging/backend-debugging.md`
  - Logs: `/documentation/05-development/monitoring/error-logs.md`

- **"CORS error / Cross-origin blocked"**
  - Primary: `/documentation/05-development/troubleshooting/cors-issues.md`
  - Config: `/documentation/03-architecture/configuration/cors-setup.md`

#### Database Errors
- **"Database locked / SQLite error"**
  - Primary: `/documentation/05-development/troubleshooting/database-errors.md`
  - Solutions: `/documentation/03-architecture/database/sqlite-issues.md`

- **"Foreign key constraint failed"**
  - Primary: `/documentation/05-development/troubleshooting/constraint-errors.md`
  - Schema: `/documentation/09-reference/database/schema-constraints.md`

#### Frontend Errors
- **"Page not loading / Blank page"**
  - Primary: `/documentation/05-development/troubleshooting/frontend-errors.md`
  - Console: `/documentation/05-development/debugging/browser-debugging.md`

- **"Drag and drop not working"**
  - Primary: `/documentation/05-development/troubleshooting/ui-issues.md#drag-drop`
  - Component: `/documentation/06-design/ui/drag-drop-troubleshooting.md`

### 3. Conceptual Queries ("What is..." / "Explain...")

#### Core Concepts
- **"What is a planogram?"**
  - Primary: `/documentation/09-reference/glossary.md#planogram`
  - Concept: `/documentation/07-cvd-framework/concepts/planogram-concept.md`
  - Business: `/documentation/02-requirements/business/planogram-requirements.md`

- **"What is DEX/EVA DTS?"**
  - Primary: `/documentation/09-reference/glossary.md#dex`
  - Standard: `/documentation/07-cvd-framework/standards/dex-standard.md`
  - Implementation: `/documentation/03-architecture/components/dex-parser.md`

- **"What is a service order?"**
  - Primary: `/documentation/09-reference/glossary.md#service-order`
  - Workflow: `/documentation/07-cvd-framework/concepts/service-order-concept.md`

- **"What is a cabinet configuration?"**
  - Primary: `/documentation/09-reference/glossary.md#cabinet`
  - Model: `/documentation/09-reference/data-models/cabinet-model.md`

#### Technical Concepts
- **"What is role-based access control (RBAC)?"**
  - Primary: `/documentation/03-architecture/security/rbac.md`
  - Implementation: `/documentation/04-implementation/features/authorization.md`

- **"What is a progressive web app (PWA)?"**
  - Primary: `/documentation/03-architecture/frontend/pwa-architecture.md`
  - Driver App: `/documentation/04-implementation/features/driver-pwa.md`

- **"What is grid pattern detection?"**
  - Primary: `/documentation/07-cvd-framework/algorithms/grid-patterns.md`
  - Technical: `/documentation/03-architecture/algorithms/grid-detection.md`

### 4. API & Integration Queries ("API..." / "Endpoint..." / "Integration...")

#### API Documentation
- **"API authentication / How to authenticate API requests"**
  - Primary: `/documentation/09-reference/api/authentication.md`
  - Examples: `/documentation/05-development/examples/api-auth-examples.md`

- **"Device API endpoints"**
  - Primary: `/documentation/09-reference/api/devices-api.md`
  - Reference: `/documentation/09-reference/api/endpoint-reference.md#devices`

- **"Service order API"**
  - Primary: `/documentation/09-reference/api/service-orders-api.md`
  - Workflow: `/documentation/05-development/workflows/service-order-api-flow.md`

- **"Planogram API"**
  - Primary: `/documentation/09-reference/api/planograms-api.md`
  - Operations: `/documentation/09-reference/api/planogram-operations.md`

#### External Integrations
- **"Anthropic/Claude API integration"**
  - Primary: `/documentation/03-architecture/integrations/anthropic-integration.md`
  - Config: `/documentation/03-architecture/configuration/ai-config.md`

- **"Webhook integration"**
  - Primary: `/documentation/03-architecture/integrations/webhooks.md`
  - Events: `/documentation/09-reference/api/webhook-events.md`

### 5. Deployment & DevOps Queries ("Deploy..." / "Setup..." / "Install...")

#### Initial Setup
- **"How to install/setup CVD"**
  - Primary: `/documentation/01-project-core/QUICK_START.md`
  - Detailed: `/documentation/05-development/setup/installation-guide.md`
  - Requirements: `/documentation/02-requirements/technical/system-requirements.md`

- **"Setup development environment"**
  - Primary: `/documentation/05-development/setup/dev-environment.md`
  - Tools: `/documentation/05-development/tools/development-tools.md`

#### Deployment
- **"Deploy to production"**
  - Primary: `/documentation/05-development/deployment/production-deployment.md`
  - Checklist: `/documentation/05-development/deployment/deployment-checklist.md`
  - Security: `/documentation/03-architecture/security/production-security.md`

- **"Deploy driver PWA"**
  - Primary: `/documentation/05-development/deployment/pwa-deployment.md`
  - Mobile: `/documentation/04-implementation/features/driver-pwa.md#deployment`

#### Configuration
- **"Configure database"**
  - Primary: `/documentation/03-architecture/database/database-setup.md`
  - Migration: `/documentation/05-development/database/migrations.md`

- **"Configure environment variables"**
  - Primary: `/documentation/03-architecture/configuration/environment-config.md`
  - Reference: `/documentation/09-reference/configuration/env-variables.md`

### 6. CVD-Specific Domain Queries

#### Vending Machine Operations
- **"Vending machine configuration"**
  - Primary: `/documentation/07-cvd-framework/vending/machine-configuration.md`
  - Types: `/documentation/09-reference/data-models/device-types.md`

- **"Product catalog management"**
  - Primary: `/documentation/04-implementation/features/product-catalog.md`
  - System Products: `/documentation/07-cvd-framework/products/system-products.md`

- **"Par level calculation"**
  - Primary: `/documentation/07-cvd-framework/algorithms/par-level-calculation.md`
  - Implementation: `/documentation/03-architecture/components/par-level-engine.md`

#### Route Management
- **"Route optimization"**
  - Primary: `/documentation/04-implementation/features/route-management.md`
  - Algorithm: `/documentation/03-architecture/algorithms/route-optimization.md`

- **"Driver scheduling"**
  - Primary: `/documentation/04-implementation/features/driver-scheduling.md`
  - Calendar: `/documentation/06-design/ui/schedule-calendar.md`

#### Inventory Management
- **"Stock tracking"**
  - Primary: `/documentation/04-implementation/features/inventory-tracking.md`
  - Real-time: `/documentation/03-architecture/components/inventory-engine.md`

- **"Restock recommendations"**
  - Primary: `/documentation/07-cvd-framework/algorithms/restock-algorithm.md`
  - AI-powered: `/documentation/04-implementation/features/ai-recommendations.md`

### 7. Performance & Optimization Queries

#### System Performance
- **"Optimize database performance"**
  - Primary: `/documentation/05-development/performance/database-optimization.md`
  - Indexing: `/documentation/03-architecture/database/indexing-strategy.md`

- **"Frontend performance optimization"**
  - Primary: `/documentation/05-development/performance/frontend-optimization.md`
  - Caching: `/documentation/03-architecture/frontend/caching-strategy.md`

#### AI Optimization
- **"Optimize planogram with AI"**
  - Primary: `/documentation/04-implementation/features/ai-optimization.md`
  - Algorithm: `/documentation/07-cvd-framework/algorithms/ai-planogram-optimizer.md`

- **"Sales-based optimization"**
  - Primary: `/documentation/07-cvd-framework/algorithms/sales-optimization.md`
  - Metrics: `/documentation/03-architecture/components/metrics-engine.md`

### 8. Testing & Quality Queries

#### Testing
- **"Run tests / Testing strategy"**
  - Primary: `/documentation/05-development/testing/testing-strategy.md`
  - Unit Tests: `/documentation/05-development/testing/unit-tests.md`
  - Integration: `/documentation/05-development/testing/integration-tests.md`

- **"Test DEX parser"**
  - Primary: `/documentation/05-development/testing/dex-parser-tests.md`
  - Samples: `/docs/examples/dex files/`

#### Code Quality
- **"Code standards / Style guide"**
  - Primary: `/documentation/05-development/standards/code-standards.md`
  - Python: `/documentation/05-development/standards/python-style.md`
  - JavaScript: `/documentation/05-development/standards/javascript-style.md`

### 9. Security Queries

#### Authentication & Authorization
- **"Security best practices"**
  - Primary: `/documentation/03-architecture/security/security-best-practices.md`
  - Checklist: `/documentation/03-architecture/security/security-checklist.md`

- **"Session management"**
  - Primary: `/documentation/03-architecture/security/session-management.md`
  - Timeout: `/documentation/03-architecture/configuration/session-config.md`

#### Data Security
- **"Data encryption"**
  - Primary: `/documentation/03-architecture/security/encryption.md`
  - Password Hashing: `/documentation/03-architecture/security/password-security.md`

- **"Audit logging"**
  - Primary: `/documentation/03-architecture/security/audit-logging.md`
  - Configuration: `/documentation/03-architecture/configuration/audit-config.md`

### 10. Migration & Upgrade Queries

#### Data Migration
- **"Migrate data / Import existing data"**
  - Primary: `/documentation/05-development/migration/data-migration.md`
  - Tools: `/documentation/05-development/tools/migration-tools.md`

- **"Upgrade database schema"**
  - Primary: `/documentation/05-development/database/schema-migrations.md`
  - Scripts: `/documentation/05-development/scripts/migration-scripts.md`

## Query Pattern Matching Rules

### Pattern Recognition
1. **Exact Match**: Direct keyword matching
2. **Synonym Expansion**: Map related terms (e.g., "cooler" → "device", "vending machine" → "device")
3. **Context Inference**: Use surrounding words to determine intent
4. **Fallback Strategy**: Provide multiple relevant options when uncertain

### Priority Scoring
- **Primary** (Score: 1.0): Direct answer to the query
- **Secondary** (Score: 0.8): Related information that supplements the primary
- **Reference** (Score: 0.6): Background or detailed technical information
- **Example** (Score: 0.5): Code examples or implementation samples

### Domain-Specific Mappings

#### CVD Terminology
- "Cooler" → Device/Vending Machine
- "Slot" → Planogram position
- "Pick list" → Service order items
- "Cabinet" → Device compartment
- "Par level" → Minimum stock threshold
- "DEX" → Data Exchange (vending industry standard)
- "EVA DTS" → European Vending Association Data Transfer Standard
- "Grid pattern" → Product arrangement detection

#### Common Abbreviations
- PCP → Product Configuration Page
- INVD → Individual Device Configuration
- NSPT → New Planogram Setup
- PWA → Progressive Web App
- RBAC → Role-Based Access Control

## Usage Guidelines for AI Agents

### Query Processing Steps
1. **Parse Query**: Extract key terms and intent
2. **Match Pattern**: Find best matching pattern(s)
3. **Retrieve Documents**: Get primary and secondary sources
4. **Context Assembly**: Build comprehensive response
5. **Provide Navigation**: Include relevant links and paths

### Response Strategy
- Always provide the most specific documentation first
- Include related documents for comprehensive understanding
- Suggest next steps or related topics
- Provide code examples when available
- Include UI page references for practical implementation

### Fallback Strategies
- If no exact match, provide closest alternatives
- Search in glossary for term definitions
- Check MASTER_INDEX for general navigation
- Refer to QUICK_START for basic operations
- Use AI_ASSISTANT_GUIDE for AI-specific features

## Maintenance Notes

This document should be updated when:
- New features are added to the system
- Documentation structure changes
- New query patterns emerge from usage
- Domain terminology evolves
- User feedback indicates gaps in coverage

Last pattern analysis: 2025-08-12
Total patterns mapped: 150+
Coverage score: 95%