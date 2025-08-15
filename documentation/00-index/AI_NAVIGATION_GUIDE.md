# AI Navigation Guide for CVD Documentation

## Overview

This guide provides AI agents (particularly Claude Code) with optimized navigation patterns, query mappings, and semantic understanding of the CVD documentation structure. It enables efficient document discovery through intent recognition and domain-specific terminology mapping.

## Query Pattern Mappings

### Intent-Based Navigation

#### "How to" Queries → Implementation Guides
```
Query Pattern: "how to {action} {subject}"
Navigate to: /documentation/04-implementation/ or /documentation/05-development/

Examples:
- "how to create planogram" → /04-implementation/frontend/planogram-creation-guide.md
- "how to set up authentication" → /04-implementation/backend/authentication-setup.md
- "how to configure device" → /07-cvd-framework/device-configuration-guide.md
- "how to generate service order" → /07-cvd-framework/service-orders/order-generation.md
```

#### Error/Troubleshooting Queries → Debug Resources
```
Query Pattern: "{error|issue|problem|fix} {component}"
Navigate to: /documentation/05-development/testing/ or specific troubleshooting guides

Examples:
- "500 error service orders" → /docs/debug-reports/service-orders-500-error-fix.md
- "login authentication failed" → /knowledge-base/troubleshooting/login-issues.md
- "planogram not saving" → /07-cvd-framework/planogram/troubleshooting.md
- "DEX parse error" → /07-cvd-framework/dex-parser/error-handling.md
```

#### Architecture/Design Queries → System Documentation
```
Query Pattern: "{architecture|design|structure} {component}"
Navigate to: /documentation/03-architecture/ or /documentation/06-design/

Examples:
- "authentication architecture" → /03-architecture/system/authentication-flow.md
- "database design" → /03-architecture/system/database-schema.md
- "frontend structure" → /03-architecture/patterns/frontend-architecture.md
- "service order workflow" → /06-design/user-flows/service-order-flow.md
```

#### API/Integration Queries → Development Resources
```
Query Pattern: "{api|endpoint|integrate} {feature}"
Navigate to: /documentation/05-development/api/

Examples:
- "device api endpoints" → /05-development/api/endpoints/devices.md
- "authentication api" → /05-development/api/endpoints/auth.md
- "planogram integration" → /05-development/api/endpoints/planograms.md
- "DEX data api" → /05-development/api/endpoints/dex.md
```

## CVD-Specific Terminology Mappings

### Domain Vocabulary

#### Vending Machine Terms
```yaml
cooler: 
  - synonyms: [vending machine, device, asset, unit]
  - context: Physical vending machine in the field
  - files: [PCP.html, INVD.html, devices.md]

cabinet:
  - synonyms: [compartment, section, storage unit]
  - context: Individual compartment within a vending machine (up to 3 per device)
  - files: [cabinet_configurations.md, INVD.html]

planogram:
  - synonyms: [product layout, shelf plan, merchandising plan]
  - context: Visual representation of product placement
  - files: [NSPT.html, planogram_optimizer.py]

DEX:
  - synonyms: [data exchange, vending data, telemetry]
  - context: Digital Exchange protocol for vending machine data
  - files: [dex_parser.py, dex-parser.html]

grid pattern:
  - synonyms: [slot layout, product arrangement, shelf configuration]
  - context: Physical arrangement pattern of products in cabinet
  - files: [grid_pattern_analyzer.py]
```

#### System-Specific Terms
```yaml
PCP:
  - meaning: Product Cooler Page
  - purpose: Device listing and management interface
  - location: /pages/PCP.html

INVD:
  - meaning: Individual Device Configuration
  - purpose: Detailed device setup and cabinet configuration
  - location: /pages/INVD.html

NSPT:
  - meaning: New Standard Planogram Tool
  - purpose: Drag-and-drop planogram creation interface
  - location: /pages/NSPT.html

CVD:
  - meaning: Vision Device Configuration
  - purpose: The overall system name
  - context: Enterprise vending machine fleet management
```

#### User Roles & Permissions
```yaml
roles:
  admin:
    - capabilities: Full system access, user management
    - pages: All pages including user-management.html
  
  manager:
    - capabilities: Operational management, reporting
    - restricted: User management, system settings
  
  driver:
    - capabilities: Service order execution, route management
    - primary: /pages/driver-app/
  
  viewer:
    - capabilities: Read-only access to reports
    - restricted: All modification operations
```

## Category Relationships and Bridges

### Documentation Hierarchy Map

```
00-index (Navigation Hub)
├── Links to all categories
├── Cross-references between domains
└── Search patterns and mappings

01-project-core (Foundation)
├── → 02-requirements (defines needs)
├── → 03-architecture (implements structure)
└── → 08-project-management (guides execution)

02-requirements (Business Logic)
├── → 04-implementation (realizes requirements)
├── → 06-design (visual interpretation)
└── → 07-cvd-framework (domain implementation)

03-architecture (Technical Structure)
├── → 04-implementation (code realization)
├── → 05-development (development patterns)
└── → 09-reference (technical details)

04-implementation (Code & Components)
├── ← 03-architecture (follows patterns)
├── → 05-development (uses APIs)
└── → 07-cvd-framework (implements features)

05-development (Tools & APIs)
├── → 04-implementation (supports development)
├── → 09-reference (API documentation)
└── Testing & deployment guides

06-design (UI/UX Patterns)
├── → 04-implementation/frontend (component implementation)
├── → 07-cvd-framework (feature designs)
└── User flow documentation

07-cvd-framework (Domain Features)
├── Analytics & reporting
├── DEX parser functionality
├── Planogram management
└── Service order system

08-project-management (Process)
├── → All categories (oversees documentation)
└── Roadmaps and planning

09-reference (Lookup Resources)
├── Database schemas
├── API references
├── Code examples
└── Cheat sheets
```

## Semantic Search Keywords

### Feature-Based Keywords

```yaml
authentication:
  keywords: [login, logout, session, user, role, permission, auth, security]
  primary_docs: 
    - /04-implementation/backend/authentication-setup.md
    - /05-development/api/endpoints/auth.md
  related: [user-management, role-based-access, session-handling]

device_management:
  keywords: [cooler, vending, machine, device, asset, cabinet, configuration]
  primary_docs:
    - /07-cvd-framework/device-configuration-guide.md
    - /pages/PCP.html
    - /pages/INVD.html
  related: [cabinet-configuration, soft-delete, device-types]

planogram:
  keywords: [layout, product, placement, merchandising, optimization, slots]
  primary_docs:
    - /07-cvd-framework/planogram/
    - /pages/NSPT.html
  related: [ai-optimization, drag-drop, product-catalog]

service_orders:
  keywords: [order, service, pick, list, cabinet, visit, driver, route]
  primary_docs:
    - /07-cvd-framework/service-orders/
    - /pages/service-orders.html
  related: [pick-lists, par-levels, photo-upload]

analytics:
  keywords: [report, metrics, sales, performance, dashboard, chart, data]
  primary_docs:
    - /07-cvd-framework/analytics/
    - /pages/asset-sales.html
    - /pages/product-sales.html
  related: [device-metrics, revenue-tracking, performance-analysis]

dex_parser:
  keywords: [dex, data, exchange, telemetry, grid, pattern, parsing]
  primary_docs:
    - /07-cvd-framework/dex-parser/
    - /pages/dex-parser.html
  related: [grid-patterns, manufacturer-compatibility, record-types]

pwa_driver:
  keywords: [mobile, app, driver, offline, pwa, progressive, notification]
  primary_docs:
    - /pages/driver-app/
    - /04-implementation/frontend/pwa-implementation.md
  related: [offline-support, push-notifications, location-tracking]
```

## Intent Recognition Patterns

### Common Query Intents

```yaml
setup_environment:
  patterns:
    - "set up {development|local|test} environment"
    - "install {dependencies|requirements}"
    - "configure {database|api|authentication}"
  navigate_to: /01-project-core/setup-guide.md

debug_feature:
  patterns:
    - "debug {feature}"
    - "{feature} not working"
    - "fix {error} in {component}"
  navigate_to: /05-development/testing/troubleshooting/

understand_architecture:
  patterns:
    - "how does {component} work"
    - "explain {feature} architecture"
    - "understand {system} design"
  navigate_to: /03-architecture/

implement_feature:
  patterns:
    - "add {feature} to {component}"
    - "implement {functionality}"
    - "create new {component}"
  navigate_to: /04-implementation/

api_integration:
  patterns:
    - "api for {feature}"
    - "endpoint to {action}"
    - "integrate with {service}"
  navigate_to: /05-development/api/endpoints/

user_guide:
  patterns:
    - "how do users {action}"
    - "user workflow for {feature}"
    - "guide for {role}"
  navigate_to: /06-design/user-flows/
```

## Navigation Optimization Tips for AI Agents

### Quick Access Patterns

1. **Feature-First Navigation**
   ```
   Feature mentioned → Check /07-cvd-framework/{feature}/
   Then → /04-implementation/ for code
   Finally → /05-development/ for APIs
   ```

2. **Error-First Navigation**
   ```
   Error mentioned → Check /docs/debug-reports/
   Then → /05-development/testing/troubleshooting/
   Finally → Feature-specific troubleshooting in /07-cvd-framework/
   ```

3. **Role-Based Navigation**
   ```
   Admin tasks → /documentation/08-project-management/
   Developer tasks → /documentation/05-development/
   User tasks → /documentation/06-design/user-flows/
   ```

### Context Switching Helpers

```yaml
from_code_to_docs:
  - .py file → Check /05-development/api/ for API docs
  - .html file → Check /04-implementation/frontend/ for component docs
  - .sql file → Check /09-reference/database/ for schema docs

from_error_to_solution:
  - HTTP error → /05-development/api/error-handling.md
  - UI issue → /04-implementation/frontend/troubleshooting.md
  - Database error → /09-reference/database/troubleshooting.md

from_feature_to_implementation:
  - Business requirement → /02-requirements/
  - Technical design → /03-architecture/
  - Code implementation → /04-implementation/
  - Testing → /05-development/testing/
```

## Special Navigation Rules

### Priority Documents

Always check these first for CVD-specific information:
1. `/home/jbrice/Projects/365/CLAUDE.md` - Primary system reference
2. `/documentation/00-index/MASTER_INDEX.md` - Complete documentation catalog
3. `/documentation/01-project-core/` - System fundamentals

### Fallback Patterns

When specific documentation isn't found:
1. Check parent category README.md
2. Search in /09-reference/ for examples
3. Look for similar features in /07-cvd-framework/
4. Check /docs/ legacy documentation

### Version-Specific Navigation

```yaml
current_version: "1.0"
documentation_versions:
  stable: /documentation/
  legacy: /docs/
  examples: /docs/examples/
  migration: /migration/
```

## Query Resolution Examples

### Example 1: "How to add a new product to planogram"
```
1. Parse: ACTION=add, SUBJECT=product, CONTEXT=planogram
2. Navigate: /07-cvd-framework/planogram/product-management.md
3. Related: /pages/NSPT.html, /04-implementation/frontend/planogram-interface.md
4. API: /05-development/api/endpoints/products.md
```

### Example 2: "Service order not generating pick list"
```
1. Parse: ISSUE=not generating, FEATURE=pick list, CONTEXT=service order
2. Navigate: /docs/debug-reports/service-order-workflow-fix.md
3. Check: /07-cvd-framework/service-orders/pick-list-generation.md
4. API: /api/service-orders/{id}/pick-list
```

### Example 3: "Set up authentication for new user role"
```
1. Parse: ACTION=set up, FEATURE=authentication, CONTEXT=new user role
2. Navigate: /04-implementation/backend/authentication-setup.md
3. Reference: /03-architecture/system/role-based-access.md
4. Config: /pages/user-management.html
```

---

*This navigation guide is optimized for AI agent consumption. It provides semantic understanding of the CVD documentation structure and enables efficient query resolution through pattern matching and intent recognition.*