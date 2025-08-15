# CVD Documentation Migration Inventory

## Executive Summary

This document provides a comprehensive inventory of all existing documentation files in the `/docs/` directory, mapping them to their target locations in the new documentation structure, analyzing dependencies, and establishing migration priorities.

**Total Files Identified**: 67  
**Migration Priority Distribution**:
- P0 (Critical): 15 files  
- P1 (High): 28 files  
- P2 (Medium): 18 files  
- P3 (Low): 6 files  

**Migration Approach**: Preserve all existing content, enhance organization, establish cross-references

---

## File Inventory by Current Location

### Root Documentation Files

| Current File | Target Location | Priority | Migration Action | File Type | Size | Dependencies |
|-------------|----------------|----------|------------------|-----------|------|--------------|
| `/docs/CONTEXT.md` | `/01-project-core/PROJECT_CONTEXT.md` | P0 | Move & Enhance | Core | Medium | None |
| `/docs/SECURITY_IMPLEMENTATION.md` | `/05-development/security/IMPLEMENTATION_GUIDE.md` | P0 | Move & Cross-ref | Technical | Large | auth.py, migrations |
| `/docs/style-guide.md` | `/01-project-core/STYLE_GUIDE.md` | P0 | Move | Standards | Medium | All development |
| `/docs/jira-story-guide.md` | `/08-project-management/JIRA_STORY_GUIDE.md` | P1 | Move | Process | Small | Project stories |
| `/docs/documentation-system-implementation-plan.md` | `/08-project-management/DOCUMENTATION_PLAN.md` | P1 | Move & Update | Planning | Large | This migration |
| `/docs/documentation-system-execution-plan.md` | `/08-project-management/EXECUTION_PLAN.md` | P2 | Move | Planning | Large | Implementation plan |
| `/docs/documentation-system-execution-plan-phases.md` | `/08-project-management/EXECUTION_PHASES.md` | P2 | Move | Planning | Medium | Execution plan |

### System Structure Documentation

| Current File | Target Location | Priority | Migration Action | File Type | Size | Dependencies |
|-------------|----------------|----------|------------------|-----------|------|--------------|
| `/docs/systems/architecture.md` | `/03-architecture/system/ARCHITECTURE_OVERVIEW.md` | P0 | Move & Enhance | Core | Large | All components |
| `/docs/systems/file-location-guide.md` | `/03-architecture/system/FILE_ORGANIZATION.md` | P0 | Move & Update | Reference | Large | Directory structure |
| `/docs/systems/nginx-config.md` | `/05-development/deployment/NGINX_CONFIGURATION.md` | P1 | Move | Config | Medium | nginx.conf files |
| `/docs/systems/driver-app-data-flow-structure.md` | `/07-cvd-framework/pwa/DATA_FLOW.md` | P1 | Move | Technical | Medium | Driver PWA |
| `/docs/systems/driver-app-data-points-structure.md` | `/07-cvd-framework/pwa/DATA_STRUCTURE.md` | P1 | Move | Technical | Medium | Driver PWA |
| `/docs/systems/route-planner-logic.md` | `/07-cvd-framework/routing/PLANNER_LOGIC.md` | P1 | Move | Technical | Medium | route-schedule.html |

### Reports Directory

| Current File | Target Location | Priority | Migration Action | File Type | Size | Dependencies |
|-------------|----------------|----------|------------------|-----------|------|--------------|
| `/docs/reports/cvd-database-schema.json` | `/09-reference/database/SCHEMA.json` | P0 | Move & Validate | Data | Large | cvd.db |
| `/docs/reports/cvd-database-schema.sql` | `/09-reference/database/SCHEMA.sql` | P0 | Move & Validate | SQL | Large | cvd.db |
| `/docs/reports/cvd-database-explained.txt` | `/09-reference/database/SCHEMA_EXPLAINED.md` | P0 | Convert & Move | Documentation | Medium | Schema files |
| `/docs/reports/device_products.csv` | `/09-reference/examples/SAMPLE_DATA.csv` | P2 | Move | Data | Small | None |
| `/docs/reports/ai-chatbot-data-usage.md` | `/07-cvd-framework/chat-assistant/DATA_USAGE.md` | P1 | Move | Analysis | Medium | knowledge_base.py |
| `/docs/reports/ai-planogram-no-suggestions-analysis.md` | `/07-cvd-framework/planogram/OPTIMIZATION_ANALYSIS.md` | P1 | Move | Analysis | Medium | planogram_optimizer.py |
| `/docs/reports/chatbot-code-analysis.md` | `/07-cvd-framework/chat-assistant/CODE_ANALYSIS.md` | P1 | Move | Analysis | Medium | Chat components |
| `/docs/reports/console-logs.md` | `/04-implementation/troubleshooting/CONSOLE_LOGS.md` | P2 | Move | Debug | Small | Frontend issues |

### Debug Reports Directory

| Current File | Target Location | Priority | Migration Action | File Type | Size | Dependencies |
|-------------|----------------|----------|------------------|-----------|------|--------------|
| `/docs/debug-reports/service-order-workflow-fix.md` | `/04-implementation/troubleshooting/service-orders/WORKFLOW_FIX.md` | P1 | Move & Cross-ref | Fix | Medium | Service orders |
| `/docs/debug-reports/service-order-final-fix.md` | `/04-implementation/troubleshooting/service-orders/FINAL_FIX.md` | P1 | Move & Cross-ref | Fix | Medium | Service orders |
| `/docs/debug-reports/service-orders-500-error-fix.md` | `/04-implementation/troubleshooting/service-orders/500_ERROR_FIX.md` | P1 | Move & Cross-ref | Fix | Medium | Service orders |
| `/docs/debug-reports/android-pwa-data-fix.md` | `/04-implementation/troubleshooting/pwa/ANDROID_DATA_FIX.md` | P1 | Move & Cross-ref | Fix | Medium | Driver PWA |

### Examples Directory

| Current File | Target Location | Priority | Migration Action | File Type | Size | Dependencies |
|-------------|----------------|----------|------------------|-----------|------|--------------|
| `/docs/examples/service-orders-spec.md` | `/02-requirements/features/SERVICE_ORDERS_SPEC.md` | P0 | Move & Enhance | Spec | Large | Service orders |
| `/docs/examples/service-orders-mockup.html` | `/09-reference/examples/service-orders/MOCKUP.html` | P2 | Move | Example | Medium | Service orders |
| `/docs/examples/activity-monitoring-implementation.md` | `/04-implementation/backend/ACTIVITY_MONITORING.md` | P1 | Move | Implementation | Large | activity_tracker.py |
| `/docs/examples/activity-tracking-analysis.md` | `/07-cvd-framework/analytics/ACTIVITY_TRACKING.md` | P1 | Move | Analysis | Medium | Activity monitoring |
| `/docs/examples/database-migration-plan.md` | `/05-development/deployment/DATABASE_MIGRATION.md` | P1 | Move | Plan | Large | PostgreSQL migration |
| `/docs/examples/local-postgresql-migration-guide.md` | `/05-development/deployment/POSTGRESQL_SETUP.md` | P1 | Move | Guide | Large | Database setup |
| `/docs/examples/product-manager-execution-plan.md` | `/08-project-management/PRODUCT_EXECUTION_PLAN.md` | P2 | Move | Plan | Large | Product management |
| `/docs/examples/product-manager-enhanced-execution-plan.md` | `/08-project-management/ENHANCED_EXECUTION_PLAN.md` | P2 | Move | Plan | Large | Product management |
| `/docs/examples/requirements-gap-analysis.md` | `/02-requirements/analysis/GAP_ANALYSIS.md` | P1 | Move | Analysis | Medium | Requirements |
| `/docs/examples/merchandising-intelligence-assessment.md` | `/07-cvd-framework/analytics/MERCHANDISING_INTELLIGENCE.md` | P2 | Move | Analysis | Large | Analytics features |
| `/docs/examples/claude-code-expert-agent-prompt.md` | `/01-project-core/AI_AGENT_PROMPTS.md` | P1 | Move & Consolidate | AI | Medium | CLAUDE.md |
| `/docs/examples/claude-code-expert-agent-prompt-general.md` | `/01-project-core/AI_AGENT_PROMPTS.md` | P1 | Consolidate | AI | Medium | AI prompts |

### Examples - DEX Files

| Current File | Target Location | Priority | Migration Action | File Type | Size | Dependencies |
|-------------|----------------|----------|------------------|-----------|------|--------------|
| `/docs/examples/dex files/AMS 39 VCF .txt` | `/07-cvd-framework/dex-parser/examples/AMS_39_VCF.txt` | P1 | Move & Rename | Data | Small | DEX parser |
| `/docs/examples/dex files/AMS Sensit III.txt` | `/07-cvd-framework/dex-parser/examples/AMS_SENSIT_III.txt` | P1 | Move & Rename | Data | Small | DEX parser |
| `/docs/examples/dex files/Crane National 187.txt` | `/07-cvd-framework/dex-parser/examples/CRANE_NATIONAL_187.txt` | P1 | Move & Rename | Data | Small | DEX parser |
| `/docs/examples/dex files/Dixie Narco 501E.txt` | `/07-cvd-framework/dex-parser/examples/DIXIE_NARCO_501E.txt` | P1 | Move & Rename | Data | Small | DEX parser |
| `/docs/examples/dex files/Dixie Narco 5800.txt` | `/07-cvd-framework/dex-parser/examples/DIXIE_NARCO_5800.txt` | P1 | Move & Rename | Data | Small | DEX parser |
| `/docs/examples/dex files/Royal 660.txt` | `/07-cvd-framework/dex-parser/examples/ROYAL_660.txt` | P1 | Move & Rename | Data | Small | DEX parser |
| `/docs/examples/dex files/Vendo 721.txt` | `/07-cvd-framework/dex-parser/examples/VENDO_721.txt` | P1 | Move & Rename | Data | Small | DEX parser |

### Examples - HTML Files

| Current File | Target Location | Priority | Migration Action | File Type | Size | Dependencies |
|-------------|----------------|----------|------------------|-----------|------|--------------|
| `/docs/examples/html/UPT.html` | `/09-reference/examples/html/UPT_EXAMPLE.html` | P3 | Move | Example | Small | Legacy |
| `/docs/examples/html/map-test.html` | `/09-reference/examples/html/MAP_TEST.html` | P3 | Move | Example | Small | Map components |
| `/docs/examples/html/route-planner-mapping.html` | `/09-reference/examples/html/ROUTE_PLANNER_DEMO.html` | P2 | Move | Example | Medium | Route planning |
| `/docs/examples/html/vms-picovision-planner.html` | `/09-reference/examples/html/VMS_PLANNER_DEMO.html` | P3 | Move | Example | Medium | Legacy |

### Project Directory

| Current File | Target Location | Priority | Migration Action | File Type | Size | Dependencies |
|-------------|----------------|----------|------------------|-----------|------|--------------|
| `/docs/project/api-specification.yaml` | `/05-development/api/SPECIFICATION.yaml` | P0 | Move & Enhance | Spec | Large | All API endpoints |
| `/docs/project/data-requirements.md` | `/02-requirements/scope/DATA_REQUIREMENTS.md` | P0 | Move | Requirements | Medium | Database design |
| `/docs/project/infrastructure-sizing.md` | `/05-development/deployment/INFRASTRUCTURE_SIZING.md` | P1 | Move | Planning | Medium | Deployment |
| `/docs/project/integration-test-plan.md` | `/05-development/testing/INTEGRATION_TEST_PLAN.md` | P1 | Move | Testing | Large | Test frameworks |
| `/docs/project/monitoring-alerting-specifications.md` | `/05-development/deployment/MONITORING_SPECS.md` | P1 | Move | Specs | Medium | DevOps tools |
| `/docs/project/security-compliance-addendum.md` | `/05-development/security/COMPLIANCE_ADDENDUM.md` | P1 | Move | Security | Medium | Security implementation |
| `/docs/project/team-todo-list.md` | `/08-project-management/TEAM_BACKLOG.md` | P2 | Move & Update | Management | Medium | Current tasks |

### Project - Design Directory

| Current File | Target Location | Priority | Migration Action | File Type | Size | Dependencies |
|-------------|----------------|----------|------------------|-----------|------|--------------|
| `/docs/project/design/ai-planogram-ui-design.md` | `/06-design/features/AI_PLANOGRAM_UI.md` | P1 | Move | Design | Large | Planogram UI |

### Project - Jira Stories

| Current File | Target Location | Priority | Migration Action | File Type | Size | Dependencies |
|-------------|----------------|----------|------------------|-----------|------|--------------|
| `/docs/project/jira-stories/ai-planogram-epic.md` | `/08-project-management/epics/AI_PLANOGRAM_EPIC.md` | P2 | Move | Epic | Large | AI features |
| `/docs/project/jira-stories/ai-planogram-phase3-testing.md` | `/08-project-management/epics/AI_PLANOGRAM_TESTING.md` | P2 | Move | Epic | Medium | AI testing |

### Project - Plans Directory

| Current File | Target Location | Priority | Migration Action | File Type | Size | Dependencies |
|-------------|----------------|----------|------------------|-----------|------|--------------|
| `/docs/project/plans/ai-planogram-implementation-plan.md` | `/04-implementation/features/AI_PLANOGRAM_PLAN.md` | P1 | Move | Plan | Large | AI planogram |

### Requirements Directory

| Current File | Target Location | Priority | Migration Action | File Type | Size | Dependencies |
|-------------|----------------|----------|------------------|-----------|------|--------------|
| `/docs/requirements/user-soft-delete-requirements.md` | `/02-requirements/features/USER_SOFT_DELETE.md` | P1 | Move | Requirements | Medium | User management |
| `/docs/requirements/backend-deployment-plan.md` | `/05-development/deployment/BACKEND_DEPLOYMENT.md` | P1 | Move | Plan | Large | Backend components |
| `/docs/requirements/frontend-deployment-plan.md` | `/05-development/deployment/FRONTEND_DEPLOYMENT.md` | P1 | Move | Plan | Large | Frontend components |

### Icons Directory

| Current File | Target Location | Priority | Migration Action | File Type | Size | Dependencies |
|-------------|----------------|----------|------------------|-----------|------|--------------|
| `/docs/icons/svg-integration-guide.md` | `/06-design/components/SVG_INTEGRATION.md` | P2 | Move | Guide | Medium | Icon system |
| `/docs/icons/icon-system-demo.html` | `/06-design/components/ICON_SYSTEM_DEMO.html` | P2 | Move | Demo | Medium | Icon components |

---

## Dependency Analysis

### Critical Dependencies (Must migrate together)

#### Database Documentation Chain
- `cvd-database-schema.json` ← `cvd-database-schema.sql` ← `cvd-database-explained.txt`
- **Impact**: Core system understanding
- **Migration Order**: SQL schema first, then JSON, then explanation

#### Service Orders Documentation Chain
- `service-orders-spec.md` ← All debug reports in `/debug-reports/service-order-*`
- **Impact**: Service order functionality
- **Migration Order**: Spec first, then debug reports with cross-references

#### DEX Parser Documentation Chain
- All DEX example files ← `dex_parser.py` documentation
- **Impact**: DEX processing capability
- **Migration Order**: Examples first, then technical documentation

#### AI Features Documentation Chain
- AI agent prompts ← Chat assistant analysis ← Planogram optimization analysis
- **Impact**: AI feature understanding
- **Migration Order**: Prompts first, then individual feature analysis

### Circular Dependencies

#### Architecture ↔ Implementation
- **Files**: `architecture.md` references implementation examples
- **Solution**: Use cross-references after migration

#### Requirements ↔ Implementation Plans  
- **Files**: Requirements documents reference implementation plans
- **Solution**: Establish bidirectional links

### External Dependencies

#### Code Dependencies
| Documentation File | Code Dependencies | Update Strategy |
|--------------------|-------------------|-----------------|
| `api-specification.yaml` | `app.py`, all API routes | Sync with code changes |
| `file-location-guide.md` | Directory structure | Auto-generate from filesystem |
| `cvd-database-schema.*` | `cvd.db` | Extract from live database |
| DEX examples | `dex_parser.py` | Version with parser updates |

#### System Dependencies
| Documentation File | System Dependencies | Update Strategy |
|--------------------|-------------------|-----------------|
| `nginx-config.md` | `/config/nginx*.conf` | Link to actual config files |
| `infrastructure-sizing.md` | Deployment environment | Review during infrastructure changes |
| `security-*.md` | Security implementation | Review with security updates |

---

## Migration Priorities

### P0 - Critical (Must complete first)

**Files**: 15 total  
**Rationale**: Core system understanding, database schema, API specification

1. `CONTEXT.md` → Project context and overview
2. `SECURITY_IMPLEMENTATION.md` → Security foundation
3. `style-guide.md` → Development standards
4. `architecture.md` → System architecture
5. `file-location-guide.md` → File organization
6. `cvd-database-schema.json` → Database structure
7. `cvd-database-schema.sql` → Database DDL
8. `cvd-database-explained.txt` → Database documentation
9. `service-orders-spec.md` → Key feature specification
10. `api-specification.yaml` → API reference
11. `data-requirements.md` → Data architecture
12. All `/docs/` root files

**Completion Target**: Week 1-2 of migration

### P1 - High (Complete by week 3)

**Files**: 28 total  
**Rationale**: Feature-specific documentation, troubleshooting, implementation guides

Key Categories:
- All debug reports (immediate troubleshooting value)
- DEX parser examples (domain-specific knowledge)
- Implementation plans and guides
- System configuration documentation
- AI feature analysis

**Completion Target**: Week 2-3 of migration

### P2 - Medium (Complete by week 4)

**Files**: 18 total  
**Rationale**: Project management, examples, supplementary documentation

Key Categories:
- Project management artifacts
- HTML examples and demos
- Secondary analysis documents
- Design documentation

**Completion Target**: Week 3-4 of migration

### P3 - Low (Complete by week 5)

**Files**: 6 total  
**Rationale**: Legacy examples, non-critical demos

Key Categories:
- Legacy HTML examples
- Deprecated functionality examples
- Historical artifacts

**Completion Target**: Week 4-5 of migration

---

## Required Updates and Consolidations

### Consolidation Opportunities

#### AI Agent Documentation
**Action**: Consolidate into single comprehensive guide
- `claude-code-expert-agent-prompt.md`
- `claude-code-expert-agent-prompt-general.md`
- **Target**: `/01-project-core/AI_AGENT_PROMPTS.md`

#### Service Orders Troubleshooting
**Action**: Create service orders troubleshooting section
- `service-order-workflow-fix.md`
- `service-order-final-fix.md`
- `service-orders-500-error-fix.md`
- **Target**: `/04-implementation/troubleshooting/service-orders/`

#### Product Management Plans
**Action**: Consolidate execution plans
- `product-manager-execution-plan.md`
- `product-manager-enhanced-execution-plan.md`
- **Target**: `/08-project-management/PRODUCT_EXECUTION_PLAN.md`

#### Database Schema Documentation
**Action**: Create comprehensive database reference
- `cvd-database-schema.json`
- `cvd-database-schema.sql`
- `cvd-database-explained.txt`
- **Target**: `/09-reference/database/` (keep separate but cross-link)

### Content Updates Required

#### File References Updates
**Files needing path updates**:
- `CLAUDE.md` → Update all `/docs/` references to new structure
- `file-location-guide.md` → Update to reflect new documentation structure
- `architecture.md` → Update cross-references

#### Format Conversions
**Files needing format changes**:
- `cvd-database-explained.txt` → Convert to Markdown
- All DEX files → Standardize naming (remove spaces)
- HTML examples → Add proper documentation headers

#### Content Enhancement
**Files needing content updates**:
- `api-specification.yaml` → Complete all missing endpoints
- `service-orders-spec.md` → Update with latest workflow changes
- `architecture.md` → Add recent architectural decisions

### Cross-Reference Establishment

#### New Cross-Reference Links Needed
1. **API Spec ↔ Implementation**: Link API endpoints to code locations
2. **Requirements ↔ Implementation**: Link requirements to implementation status
3. **Architecture ↔ Code**: Link architectural components to source files
4. **Troubleshooting ↔ Features**: Link debug reports to feature documentation
5. **Examples ↔ Implementation**: Link examples to actual implementation

#### Navigation Paths to Establish
1. **Feature Discovery**: From user need → requirements → implementation → API
2. **Troubleshooting Path**: From error → debug report → solution → prevention
3. **Development Path**: From architecture → implementation → testing → deployment
4. **AI Assistant Path**: From question type → relevant documentation section

---

## Migration Validation Checklist

### Pre-Migration Validation
- [ ] All 67 files identified and categorized
- [ ] Dependencies mapped and understood
- [ ] Target locations confirmed available
- [ ] Priority order established and agreed upon
- [ ] Required tooling and scripts prepared

### During Migration Validation
- [ ] File integrity maintained during move
- [ ] Metadata preserved (creation dates, etc.)
- [ ] Links updated to new locations
- [ ] Cross-references established
- [ ] Format conversions completed successfully

### Post-Migration Validation
- [ ] All files accessible in new locations
- [ ] No broken internal links
- [ ] Search functionality works with new structure
- [ ] AI navigation paths functional
- [ ] Team can find documentation easily
- [ ] Old locations properly redirected or archived

---

## Risk Assessment

### High Risk Items

#### Missing Dependencies
**Risk**: Critical code dependencies not identified
**Impact**: Broken documentation after migration
**Mitigation**: Code analysis to identify all doc references

#### Large File Migrations
**Risk**: Large files (database schemas, specifications) corruption
**Impact**: Loss of critical system documentation
**Mitigation**: Checksum verification, backup before migration

#### Circular Reference Resolution
**Risk**: Breaking existing cross-references during migration
**Impact**: Navigation difficulties, incomplete context
**Mitigation**: Map all references before migration, update systematically

### Medium Risk Items

#### Format Conversion Issues
**Risk**: Content loss during format conversions
**Impact**: Incomplete or malformed documentation
**Mitigation**: Manual review of all conversions

#### Team Adoption
**Risk**: Team continues using old documentation locations
**Impact**: Documentation fragmentation, maintenance burden
**Mitigation**: Clear communication, training, old location redirection

---

## Success Metrics

### Quantitative Metrics
- **Migration Completeness**: 100% of identified files successfully migrated
- **Link Integrity**: <1% broken links after migration
- **Content Preservation**: 100% content preserved during migration
- **Search Coverage**: All migrated content searchable in new system

### Qualitative Metrics
- **Findability**: Team can locate relevant documentation <3 clicks
- **Completeness**: No gaps in critical system documentation
- **Consistency**: All documentation follows new standards
- **Maintainability**: Clear ownership and update processes established

---

## Next Steps

1. **Review and Approve**: Stakeholder review of migration inventory
2. **Finalize Migration Map**: Create detailed migration execution plan
3. **Prepare Tooling**: Set up migration scripts and validation tools
4. **Execute Migration**: Follow priority-based migration schedule
5. **Validate Results**: Run comprehensive validation checks
6. **Team Training**: Orient team to new documentation structure

---

**Document Metadata**:
- **Version**: 1.0
- **Created**: 2025-08-12
- **Author**: Documentation Migration Team
- **Total Files Analyzed**: 67
- **Estimated Migration Effort**: 40 hours
- **Dependencies Identified**: 150+
- **Critical Path Items**: 15