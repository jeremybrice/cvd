# CVD Documentation Migration Map

## Executive Summary

This document provides the detailed execution plan for migrating CVD documentation from the current `/docs/` structure to the new organized documentation system. It includes specific file mappings, redirect strategies, update requirements, and a phase-by-phase execution timeline.

**Migration Scope**: 67 files across 10 categories  
**Estimated Duration**: 5 weeks  
**Risk Level**: Medium (manageable with proper validation)  
**Success Criteria**: 100% file migration, <1% broken links, seamless team transition

---

## Detailed Migration Mappings

### Phase 1: Critical Foundation (P0 - Week 1)

#### Core Project Files
```bash
# Primary System Documentation
/docs/CONTEXT.md
→ /documentation/01-project-core/PROJECT_CONTEXT.md
  • Action: Move + add metadata header
  • Update: Add cross-references to architecture
  • Dependencies: None
  • Validation: Content completeness check

/docs/style-guide.md  
→ /documentation/01-project-core/STYLE_GUIDE.md
  • Action: Move + enhance with new standards
  • Update: Add section on documentation standards
  • Dependencies: All development files reference this
  • Validation: Ensure all style rules documented

/docs/SECURITY_IMPLEMENTATION.md
→ /documentation/05-development/security/IMPLEMENTATION_GUIDE.md
  • Action: Move + create security index
  • Update: Cross-reference with auth.py and migrations
  • Dependencies: Authentication system, user management
  • Validation: Security checklist completeness
```

#### System Architecture
```bash
/docs/systems/architecture.md
→ /documentation/03-architecture/system/ARCHITECTURE_OVERVIEW.md
  • Action: Move + expand with recent changes
  • Update: Add component diagrams, data flow
  • Dependencies: All system components
  • Validation: Architecture accuracy with current system

/docs/systems/file-location-guide.md
→ /documentation/03-architecture/system/FILE_ORGANIZATION.md  
  • Action: Move + update for new structure
  • Update: Reflect new documentation paths
  • Dependencies: Directory structure, CLAUDE.md
  • Validation: Path accuracy validation
```

#### Database Documentation
```bash
/docs/reports/cvd-database-schema.json
→ /documentation/09-reference/database/SCHEMA.json
  • Action: Move + validate against current DB
  • Update: Add timestamp, version info
  • Dependencies: cvd.db structure
  • Validation: Schema accuracy check

/docs/reports/cvd-database-schema.sql  
→ /documentation/09-reference/database/SCHEMA.sql
  • Action: Move + add comments
  • Update: Include constraints, indexes
  • Dependencies: Database structure
  • Validation: SQL syntax validation

/docs/reports/cvd-database-explained.txt
→ /documentation/09-reference/database/SCHEMA_EXPLAINED.md
  • Action: Convert to Markdown + enhance
  • Update: Add table relationships, business logic
  • Dependencies: Schema files
  • Validation: Completeness against actual schema
```

#### API Documentation  
```bash
/docs/project/api-specification.yaml
→ /documentation/05-development/api/SPECIFICATION.yaml
  • Action: Move + complete missing endpoints
  • Update: Add all 50+ endpoints, examples
  • Dependencies: app.py routes
  • Validation: API completeness audit

/docs/project/data-requirements.md
→ /documentation/02-requirements/scope/DATA_REQUIREMENTS.md
  • Action: Move + update with current data model
  • Update: Add data validation rules
  • Dependencies: Database design
  • Validation: Requirements vs implementation check
```

### Phase 2: Feature Documentation (P1 - Week 2)

#### Service Orders Suite
```bash
/docs/examples/service-orders-spec.md
→ /documentation/02-requirements/features/SERVICE_ORDERS_SPEC.md
  • Action: Move + enhance with workflow details
  • Update: Add recent cabinet-centric changes
  • Dependencies: service_order_service.py
  • Validation: Spec vs implementation alignment

/docs/debug-reports/service-order-workflow-fix.md
→ /documentation/04-implementation/troubleshooting/service-orders/WORKFLOW_FIX.md
  • Action: Move + cross-reference with spec
  • Update: Add prevention strategies
  • Dependencies: Service order spec
  • Validation: Fix still applicable

/docs/debug-reports/service-order-final-fix.md  
→ /documentation/04-implementation/troubleshooting/service-orders/FINAL_FIX.md
  • Action: Move + link to related fixes
  • Update: Add root cause analysis
  • Dependencies: Other service order fixes
  • Validation: Solution completeness

/docs/debug-reports/service-orders-500-error-fix.md
→ /documentation/04-implementation/troubleshooting/service-orders/500_ERROR_FIX.md
  • Action: Move + add error prevention
  • Update: Include monitoring recommendations
  • Dependencies: Error handling code
  • Validation: Fix effectiveness
```

#### DEX Parser Documentation
```bash
/docs/examples/dex files/AMS 39 VCF .txt
→ /documentation/07-cvd-framework/dex-parser/examples/AMS_39_VCF.txt
  • Action: Move + standardize filename
  • Update: Add format documentation header
  • Dependencies: dex_parser.py
  • Validation: Parser compatibility

/docs/examples/dex files/AMS Sensit III.txt
→ /documentation/07-cvd-framework/dex-parser/examples/AMS_SENSIT_III.txt
  • Action: Move + standardize filename
  • Update: Document format specifics
  • Dependencies: DEX parser
  • Validation: Parse success

/docs/examples/dex files/Crane National 187.txt
→ /documentation/07-cvd-framework/dex-parser/examples/CRANE_NATIONAL_187.txt
  • Action: Move + standardize filename
  • Update: Add manufacturer notes
  • Dependencies: Grid pattern analyzer
  • Validation: Grid detection accuracy

/docs/examples/dex files/Dixie Narco 501E.txt
→ /documentation/07-cvd-framework/dex-parser/examples/DIXIE_NARCO_501E.txt
  • Action: Move + standardize filename
  • Update: Document unique features
  • Dependencies: DEX record types
  • Validation: Record parsing

/docs/examples/dex files/Dixie Narco 5800.txt
→ /documentation/07-cvd-framework/dex-parser/examples/DIXIE_NARCO_5800.txt
  • Action: Move + standardize filename
  • Update: Add model specifications
  • Dependencies: Device types
  • Validation: Device compatibility

/docs/examples/dex files/Royal 660.txt
→ /documentation/07-cvd-framework/dex-parser/examples/ROYAL_660.txt
  • Action: Move + standardize filename
  • Update: Document format variations
  • Dependencies: Parser flexibility
  • Validation: Edge case handling

/docs/examples/dex files/Vendo 721.txt
→ /documentation/07-cvd-framework/dex-parser/examples/VENDO_721.txt
  • Action: Move + standardize filename
  • Update: Add troubleshooting notes
  • Dependencies: Error handling
  • Validation: Error recovery
```

#### PWA Documentation
```bash
/docs/systems/driver-app-data-flow-structure.md
→ /documentation/07-cvd-framework/pwa/DATA_FLOW.md
  • Action: Move + update with offline sync
  • Update: Add IndexedDB schema
  • Dependencies: Driver app components
  • Validation: Data flow accuracy

/docs/systems/driver-app-data-points-structure.md
→ /documentation/07-cvd-framework/pwa/DATA_STRUCTURE.md
  • Action: Move + expand data model
  • Update: Include sync conflict resolution
  • Dependencies: PWA data layer
  • Validation: Structure completeness

/docs/debug-reports/android-pwa-data-fix.md
→ /documentation/04-implementation/troubleshooting/pwa/ANDROID_DATA_FIX.md
  • Action: Move + add prevention strategies
  • Update: Include testing procedures
  • Dependencies: Android PWA code
  • Validation: Fix applicability
```

### Phase 3: Implementation & Analysis (P1 - Week 3)

#### Implementation Documentation
```bash
/docs/examples/activity-monitoring-implementation.md
→ /documentation/04-implementation/backend/ACTIVITY_MONITORING.md
  • Action: Move + update with current implementation
  • Update: Add performance considerations
  • Dependencies: activity_tracker.py
  • Validation: Implementation accuracy

/docs/examples/database-migration-plan.md
→ /documentation/05-development/deployment/DATABASE_MIGRATION.md
  • Action: Move + generalize for future migrations
  • Update: Add rollback procedures
  • Dependencies: Migration scripts
  • Validation: Migration process completeness

/docs/examples/local-postgresql-migration-guide.md
→ /documentation/05-development/deployment/POSTGRESQL_SETUP.md
  • Action: Move + make environment-agnostic
  • Update: Add troubleshooting section
  • Dependencies: Database configuration
  • Validation: Setup procedure accuracy
```

#### AI Features Analysis
```bash
/docs/reports/ai-chatbot-data-usage.md
→ /documentation/07-cvd-framework/chat-assistant/DATA_USAGE.md
  • Action: Move + update with current usage
  • Update: Add privacy considerations
  • Dependencies: knowledge_base.py
  • Validation: Usage pattern accuracy

/docs/reports/ai-planogram-no-suggestions-analysis.md
→ /documentation/07-cvd-framework/planogram/OPTIMIZATION_ANALYSIS.md
  • Action: Move + expand analysis
  • Update: Add improvement recommendations
  • Dependencies: planogram_optimizer.py
  • Validation: Analysis relevance

/docs/examples/claude-code-expert-agent-prompt.md + 
/docs/examples/claude-code-expert-agent-prompt-general.md
→ /documentation/01-project-core/AI_AGENT_PROMPTS.md
  • Action: Consolidate into single comprehensive guide
  • Update: Add usage examples, best practices
  • Dependencies: CLAUDE.md integration
  • Validation: Prompt effectiveness
```

#### System Configuration
```bash
/docs/systems/nginx-config.md
→ /documentation/05-development/deployment/NGINX_CONFIGURATION.md
  • Action: Move + update with current configs
  • Update: Add security hardening notes
  • Dependencies: nginx.conf files
  • Validation: Configuration accuracy

/docs/requirements/backend-deployment-plan.md
→ /documentation/05-development/deployment/BACKEND_DEPLOYMENT.md
  • Action: Move + update deployment steps
  • Update: Add monitoring setup
  • Dependencies: Backend components
  • Validation: Deployment completeness

/docs/requirements/frontend-deployment-plan.md
→ /documentation/05-development/deployment/FRONTEND_DEPLOYMENT.md
  • Action: Move + update with PWA considerations
  • Update: Add CDN configuration
  • Dependencies: Frontend components
  • Validation: Deployment accuracy
```

### Phase 4: Project Management & Design (P2 - Week 4)

#### Project Management
```bash
/docs/jira-story-guide.md
→ /documentation/08-project-management/JIRA_STORY_GUIDE.md
  • Action: Move + update with current processes
  • Update: Add story template examples
  • Dependencies: Project workflow
  • Validation: Process accuracy

/docs/project/team-todo-list.md
→ /documentation/08-project-management/TEAM_BACKLOG.md
  • Action: Move + archive completed items
  • Update: Restructure as living document
  • Dependencies: Current project status
  • Validation: Relevance of items

/docs/documentation-system-implementation-plan.md
→ /documentation/08-project-management/DOCUMENTATION_PLAN.md
  • Action: Move + mark as historical
  • Update: Add lessons learned
  • Dependencies: This migration
  • Validation: Plan vs actual comparison
```

#### Design Documentation
```bash
/docs/project/design/ai-planogram-ui-design.md
→ /documentation/06-design/features/AI_PLANOGRAM_UI.md
  • Action: Move + update with implemented design
  • Update: Add usability testing results
  • Dependencies: Planogram UI components
  • Validation: Design vs implementation

/docs/icons/svg-integration-guide.md
→ /documentation/06-design/components/SVG_INTEGRATION.md
  • Action: Move + expand with current icon system
  • Update: Add accessibility guidelines
  • Dependencies: Icon generation tools
  • Validation: Integration process accuracy

/docs/icons/icon-system-demo.html
→ /documentation/06-design/components/ICON_SYSTEM_DEMO.html
  • Action: Move + update with current icons
  • Update: Make responsive, add documentation
  • Dependencies: Icon assets
  • Validation: Demo functionality
```

### Phase 5: Examples & References (P3 - Week 5)

#### HTML Examples
```bash
/docs/examples/html/route-planner-mapping.html
→ /documentation/09-reference/examples/html/ROUTE_PLANNER_DEMO.html
  • Action: Move + add documentation header
  • Update: Make standalone, add comments
  • Dependencies: Route planning components
  • Validation: Demo functionality

/docs/examples/html/map-test.html
→ /documentation/09-reference/examples/html/MAP_TEST.html
  • Action: Move + document test scenarios
  • Update: Add test case descriptions
  • Dependencies: Map components
  • Validation: Test coverage

/docs/examples/html/UPT.html
→ /documentation/09-reference/examples/html/UPT_EXAMPLE.html
  • Action: Move + mark as legacy
  • Update: Add historical context
  • Dependencies: Legacy systems
  • Validation: Historical accuracy
```

#### Data Examples
```bash
/docs/reports/device_products.csv
→ /documentation/09-reference/examples/SAMPLE_DATA.csv
  • Action: Move + anonymize if needed
  • Update: Add data dictionary
  • Dependencies: Database structure
  • Validation: Data format accuracy
```

---

## CLAUDE.md Integration Updates

The main CLAUDE.md file needs critical updates to reference the new documentation structure:

### Required CLAUDE.md Updates

```markdown
# Current References → New References

## File Organization Section (Line 49)
CURRENT: See `/docs/system-structure/file-location-guide.md`
NEW: See `/documentation/03-architecture/system/FILE_ORGANIZATION.md`

## Documentation Reference (Line 54)  
CURRENT: - Documentation: `/docs/`
NEW: - Documentation: `/documentation/`

## Testing Section (Line 222)
CURRENT: - DEX samples: `/docs/examples/dex files/`
NEW: - DEX samples: `/documentation/07-cvd-framework/dex-parser/examples/`

## General Reference (Line 259)
CURRENT: For detailed information on specific features, refer to documentation in `/docs/`.
NEW: For detailed information on specific features, refer to documentation in `/documentation/`.
```

### New CLAUDE.md Sections to Add

```markdown
## Documentation Navigation

### Quick Access Paths
- **Getting Started**: `/documentation/01-project-core/QUICK_START.md`
- **API Reference**: `/documentation/05-development/api/`
- **Troubleshooting**: `/documentation/04-implementation/troubleshooting/`
- **Architecture**: `/documentation/03-architecture/system/`
- **CVD Framework**: `/documentation/07-cvd-framework/`

### AI Assistant Navigation
See `/documentation/00-index/AI_NAVIGATION_GUIDE.md` for agent-specific documentation paths.

### Documentation Standards
All documentation follows standards defined in `/documentation/00-index/DOCUMENTATION_STANDARDS.md`
```

---

## Redirect Strategy

### Internal Link Redirects

Create redirect mappings for internal references:

```bash
# Create redirect map file
/documentation/00-index/REDIRECT_MAP.json
{
  "/docs/CONTEXT.md": "/documentation/01-project-core/PROJECT_CONTEXT.md",
  "/docs/systems/architecture.md": "/documentation/03-architecture/system/ARCHITECTURE_OVERVIEW.md",
  "/docs/examples/dex files/": "/documentation/07-cvd-framework/dex-parser/examples/",
  // ... all mappings
}
```

### Code Reference Updates

Files that reference documentation paths need updates:

```python
# knowledge_base.py - Update documentation paths
OLD: "/docs/examples/"
NEW: "/documentation/09-reference/examples/"

# Any import or reference statements
OLD: "../docs/reports/schema.json"  
NEW: "../documentation/09-reference/database/SCHEMA.json"
```

### Search Index Updates

Update any search functionality to use new paths:

```javascript
// Search configuration
const DOC_PATHS = [
  "/documentation/01-project-core/",
  "/documentation/02-requirements/",
  "/documentation/03-architecture/",
  // ... all new paths
];
```

---

## Migration Scripts

### Automated Migration Script

```bash
#!/bin/bash
# migrate-docs.sh - Automated documentation migration

# Phase 1: Critical files
echo "Phase 1: Migrating critical documentation..."
migrate_file() {
  local source="$1"
  local target="$2" 
  local action="$3"
  
  echo "Migrating: $source → $target"
  
  # Create target directory
  mkdir -p "$(dirname "$target")"
  
  # Copy file with metadata preservation
  cp -p "$source" "$target"
  
  # Apply any transformations
  case "$action" in
    "convert_md")
      # Convert .txt to .md with header
      add_markdown_header "$target"
      ;;
    "standardize_name")
      # Clean up filename spaces/chars
      standardize_filename "$target"
      ;;
    "add_metadata")
      # Add YAML front matter
      add_yaml_header "$target"
      ;;
  esac
  
  echo "✓ Completed: $target"
}

# Execute migrations by phase
source migration-phase-1.sh
source migration-phase-2.sh
source migration-phase-3.sh
source migration-phase-4.sh
source migration-phase-5.sh

echo "Migration completed. Running validation..."
validate_migration.sh
```

### Validation Script

```bash
#!/bin/bash
# validate_migration.sh - Validate migration completeness

echo "Validating migration results..."

# Check file count
EXPECTED_FILES=67
ACTUAL_FILES=$(find /documentation -name "*.md" -o -name "*.html" -o -name "*.json" -o -name "*.sql" -o -name "*.yaml" -o -name "*.csv" -o -name "*.txt" | wc -l)

if [ "$ACTUAL_FILES" -eq "$EXPECTED_FILES" ]; then
  echo "✓ File count validation passed: $ACTUAL_FILES files"
else
  echo "✗ File count mismatch: expected $EXPECTED_FILES, found $ACTUAL_FILES"
  exit 1
fi

# Check for broken links
echo "Checking for broken internal links..."
broken_links=0
for file in $(find /documentation -name "*.md"); do
  # Check for old /docs/ references
  if grep -q "/docs/" "$file"; then
    echo "⚠ Found old path reference in: $file"
    ((broken_links++))
  fi
done

if [ "$broken_links" -eq 0 ]; then
  echo "✓ No broken internal links found"
else
  echo "✗ Found $broken_links files with old path references"
fi

# Validate file accessibility
echo "Validating file accessibility..."
for file in $(find /documentation -name "*.md"); do
  if [ ! -r "$file" ]; then
    echo "✗ File not readable: $file"
    exit 1
  fi
done
echo "✓ All files accessible"

echo "Migration validation completed successfully!"
```

### Link Update Script

```bash
#!/bin/bash
# update_links.sh - Update all internal documentation links

echo "Updating internal documentation links..."

# Load redirect mappings
REDIRECT_MAP="/documentation/00-index/REDIRECT_MAP.json"

# Update CLAUDE.md
echo "Updating CLAUDE.md..."
sed -i 's|/docs/system-structure/file-location-guide.md|/documentation/03-architecture/system/FILE_ORGANIZATION.md|g' CLAUDE.md
sed -i 's|/docs/examples/dex files/|/documentation/07-cvd-framework/dex-parser/examples/|g' CLAUDE.md
sed -i 's|documentation in `/docs/`|documentation in `/documentation/`|g' CLAUDE.md

# Update all markdown files in new documentation
find /documentation -name "*.md" -exec sed -i 's|/docs/|/documentation/|g' {} \;

# Update specific path patterns
find /documentation -name "*.md" -exec sed -i 's|docs/systems/|documentation/03-architecture/system/|g' {} \;
find /documentation -name "*.md" -exec sed -i 's|docs/examples/|documentation/09-reference/examples/|g' {} \;

echo "Link updates completed!"
```

---

## Execution Timeline

### Week 1: Foundation & Critical Files
**Days 1-2**: Set up new structure, create scripts
- Create all directory structures
- Set up migration and validation scripts
- Prepare redirect mappings

**Days 3-5**: Migrate P0 files
- Core project documentation
- Database schemas
- System architecture
- API specifications

**Validation**: Daily file integrity checks

### Week 2: Feature Documentation  
**Days 1-2**: Service orders and troubleshooting
- Service order specifications
- All debug reports
- Cross-reference establishment

**Days 3-5**: DEX parser and examples
- All DEX example files
- Technical documentation
- AI feature analysis

**Validation**: Feature completeness audit

### Week 3: Implementation & Configuration
**Days 1-3**: Implementation guides
- Activity monitoring
- Database migrations
- PWA documentation

**Days 4-5**: System configuration
- Nginx configuration
- Deployment procedures
- Security documentation

**Validation**: Technical accuracy review

### Week 4: Project Management & Design
**Days 1-3**: Project documentation
- Jira processes
- Team backlogs
- Planning documents

**Days 4-5**: Design documentation
- UI specifications
- Component guides
- Icon system

**Validation**: Process documentation review

### Week 5: Examples & Final Validation
**Days 1-2**: Examples and references
- HTML examples
- Data samples
- Legacy documentation

**Days 3-5**: Comprehensive validation
- Link checking
- Search functionality
- Team training preparation

**Final Validation**: Complete system test

---

## Risk Mitigation

### Identified Risks & Mitigation Strategies

#### File Corruption During Migration
**Risk**: Large files corrupted during move
**Mitigation**: 
- Use checksums for validation
- Create backups before migration
- Test with small files first

#### Broken Cross-References
**Risk**: Internal links broken after migration
**Mitigation**:
- Map all references before migration
- Use automated link checking
- Staged link updates

#### Team Disruption
**Risk**: Team unable to find documentation during migration
**Mitigation**:
- Migrate in phases (most critical first)
- Maintain old structure until complete
- Provide transition documentation

#### Search Index Issues
**Risk**: Search functionality broken after migration
**Mitigation**:
- Update search configuration early
- Test search with sample queries
- Maintain search index during transition

---

## Success Validation

### Completion Checklist
- [ ] All 67 files successfully migrated
- [ ] No broken internal links (<1% target)
- [ ] All cross-references established
- [ ] Search functionality operational
- [ ] CLAUDE.md updated with new paths
- [ ] Redirect mappings functional
- [ ] Team can navigate new structure
- [ ] Documentation standards applied
- [ ] Backup of old structure maintained
- [ ] Migration scripts documented

### Team Acceptance Criteria
- [ ] Developers can find API documentation <30 seconds
- [ ] Troubleshooting guides immediately accessible
- [ ] New documentation structure intuitive
- [ ] AI assistant navigation functional
- [ ] All role-based documentation accessible
- [ ] Mobile/responsive documentation access
- [ ] Offline documentation availability (PWA context)

---

## Post-Migration Tasks

### Immediate (Week 6)
1. **Archive Old Structure**: Move `/docs/` to `/docs-archived/`
2. **Update External References**: Check external tools/scripts
3. **Team Training**: Conduct navigation training sessions
4. **Monitor Usage**: Track documentation access patterns

### Short-term (Month 1)
1. **Gather Feedback**: Collect team feedback on new structure
2. **Optimize Navigation**: Improve based on usage patterns
3. **Complete Cross-References**: Fill any missing links
4. **Update Automation**: Modify any automated tools

### Long-term (Ongoing)
1. **Maintain Currency**: Keep documentation updated with code changes
2. **Process Refinement**: Improve documentation processes
3. **Team Onboarding**: Update onboarding with new structure
4. **Continuous Improvement**: Regular reviews and updates

---

**Document Metadata**:
- **Version**: 1.0  
- **Created**: 2025-08-12
- **Migration Target**: 67 files
- **Estimated Execution Time**: 5 weeks
- **Risk Assessment**: Medium
- **Dependencies**: Team availability, system stability
- **Success Criteria**: 100% migration, <1% broken links