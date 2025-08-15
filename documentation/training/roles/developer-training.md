# CVD Documentation System - Developer Training

## Overview

This training is specifically designed for developers working on the CVD (Vision Device Configuration) project. It focuses on development workflow integration, API documentation usage, coding standards, and technical implementation guidance within the new documentation system.

**Target Audience**: Software developers, technical leads, DevOps engineers  
**Training Duration**: 90-120 minutes  
**Prerequisites**: Basic CVD project familiarity, completed main GUIDE.md training

---

## Developer-Specific Documentation Structure

### Core Developer Categories

```
📁 03-architecture/        ← Technical decisions, patterns, system design
📁 04-implementation/      ← Development guides, component implementations  
📁 05-development/         ← APIs, testing, deployment, tools
📁 09-reference/          ← Quick references, code examples, cheat sheets
```

### Developer Workflow Integration

#### Daily Development Workflow

**1. Feature Development Workflow**:
```bash
# Starting a new feature
1. Requirements research:
   cvd-search "feature-name" --categories "Requirements" --max-results 10

2. Architecture review:
   cvd-search "feature-name patterns" --categories "Architecture"

3. API documentation:  
   cat /documentation/05-development/api/endpoints/{feature}.md

4. Implementation patterns:
   cvd-search "implementation patterns" --categories "Implementation"

5. Testing guidance:
   cat /documentation/05-development/testing/STRATEGY.md
```

**2. API Development Workflow**:
```bash
# API endpoint development  
1. Review API patterns:
   cat /documentation/03-architecture/patterns/API_PATTERNS.md

2. Check existing endpoints:
   ls /documentation/05-development/api/endpoints/

3. Follow endpoint template:
   cp /documentation/00-index/templates/api-endpoint-template.md \
      /documentation/05-development/api/endpoints/new-endpoint.md

4. Implement following coding standards:
   cat /documentation/05-development/CODING_STANDARDS.md

5. Add tests using examples:
   cat /documentation/05-development/testing/examples/API_ENDPOINT_TESTS.py
```

**3. Bug Investigation Workflow**:
```bash  
# Troubleshooting approach
1. Error documentation search:
   cvd-search "error message keywords" --tags "troubleshooting"

2. Check runbooks:
   ls /documentation/05-development/deployment/runbooks/

3. Review architectural constraints:
   cvd-search "constraint limitation" --categories "Architecture"

4. Check implementation patterns for alternatives:
   cat /documentation/03-architecture/patterns/ANTI_PATTERNS.md
```

#### Code Review Integration

**Pre-Review Documentation Checklist**:
```bash
# Before submitting PR
1. Update API documentation if endpoints changed:
   vim /documentation/05-development/api/endpoints/{modified-endpoint}.md

2. Add/update tests documentation:
   # Reference examples in /documentation/05-development/testing/examples/

3. Update architecture decisions if needed:
   # Create new ADR in /documentation/03-architecture/decisions/

4. Check coding standards compliance:
   grep -n "TODO\|FIXME\|HACK" {your-files}
   # Document any intentional exceptions
```

---

## API Documentation Usage

### Comprehensive API Reference System

#### API Documentation Structure
```
05-development/api/
├── OVERVIEW.md              ← API architecture and conventions
├── endpoints/
│   ├── auth.md             ← Authentication endpoints  
│   ├── devices.md          ← Device management APIs
│   ├── service-orders.md   ← Service order APIs
│   └── {feature}.md        ← Feature-specific endpoints
└── README.md               ← API navigation guide
```

#### Finding API Information

**1. Endpoint Discovery**:
```bash
# Find all endpoints for a feature
cvd-search "planogram API endpoint" --categories "Development" --tags "api"

# List available endpoint docs
ls /documentation/05-development/api/endpoints/

# Search within endpoint docs
cvd-search "POST /api/planograms" --phrase
```

**2. API Pattern Understanding**:
```bash
# Review API design patterns
cat /documentation/03-architecture/patterns/API_PATTERNS.md

# Check authentication patterns
cat /documentation/05-development/api/endpoints/auth.md

# Study error handling conventions
cvd-search "error handling API" --categories "Architecture" "Development"
```

**3. Implementation Examples**:
```bash
# Find code examples for API usage
cvd-search "API example" --categories "Reference" --tags "examples"

# Check test examples
cat /documentation/05-development/testing/examples/API_ENDPOINT_TESTS.py

# Review integration patterns  
cat /documentation/03-architecture/patterns/INTEGRATION_PATTERNS.md
```

### API Documentation Standards for Developers

#### When to Update API Documentation

**Always Update When**:
- Adding new endpoints
- Changing request/response schemas
- Modifying authentication requirements
- Adding new error codes
- Changing rate limits or constraints

**Documentation Template Usage**:
```bash
# Create new endpoint documentation
cp /documentation/00-index/templates/api-endpoint-template.md \
   /documentation/05-development/api/endpoints/your-endpoint.md

# Follow the template structure:
# 1. Endpoint overview and purpose
# 2. Request format and parameters  
# 3. Response format and examples
# 4. Error handling and codes
# 5. Usage examples and integration notes
```

#### API Documentation Best Practices

**Code Examples Standards**:
```bash
# Always include curl examples
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"key": "value"}' \
  http://localhost:5000/api/endpoint

# Include Python client examples  
from api_client import CVDApi
api = CVDApi()
result = api.create_resource(data)

# Include JavaScript frontend examples
const response = await api.post('/api/endpoint', data);
```

**Error Documentation Requirements**:
```markdown
## Error Responses

| Status | Code | Description | Resolution |
|--------|------|-------------|------------|
| 400 | INVALID_DATA | Request data validation failed | Check required fields |
| 401 | UNAUTHORIZED | Authentication required | Include valid token |
| 403 | FORBIDDEN | Insufficient permissions | Check user role |
| 404 | NOT_FOUND | Resource does not exist | Verify resource ID |
```

---

## Coding Standards Integration

### CVD Coding Standards Overview

#### Python/Flask Backend Standards

**Code Organization**:
```python
# File structure standards
app.py                 # Main application entry
auth.py               # Authentication module
{feature}_service.py  # Feature-specific services
models/              # Data models
utils/               # Utility functions
tests/               # Test modules

# Import organization  
# 1. Standard library imports
import os
from datetime import datetime

# 2. Third-party imports
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash

# 3. Local imports
from auth import require_auth
from models.device import Device
```

**Function Documentation Standards**:
```python
def create_service_order(device_id: int, order_data: dict) -> dict:
    """
    Create a new service order for a device.
    
    Args:
        device_id (int): Target device ID
        order_data (dict): Service order details
            - description (str): Order description
            - priority (str): Order priority level
            - scheduled_date (str): ISO format date
    
    Returns:
        dict: Created service order with ID and status
        
    Raises:
        ValueError: If device_id is invalid
        AuthenticationError: If user lacks permissions
        
    Example:
        order = create_service_order(123, {
            "description": "Restock beverages", 
            "priority": "normal",
            "scheduled_date": "2025-08-15T10:00:00Z"
        })
    """
```

**Error Handling Standards**:
```python
# Consistent error response format
def handle_api_error(error_code: str, message: str, status_code: int = 400):
    return jsonify({
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    }), status_code

# Usage in endpoints
@app.route('/api/devices', methods=['POST'])
@require_auth
def create_device():
    try:
        # Implementation
        pass
    except ValueError as e:
        return handle_api_error("INVALID_DATA", str(e), 400)
    except PermissionError as e:
        return handle_api_error("FORBIDDEN", str(e), 403)
```

#### Frontend JavaScript Standards

**Module Organization**:
```javascript
// api.js - API client class
class CVDApi {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }
    
    async request(endpoint, options = {}) {
        // Standard request handling with retry logic
    }
}

// Component organization
components/
├── auth/           # Authentication components
├── devices/        # Device management components  
├── planogram/      # Planogram components
└── shared/         # Shared UI components
```

**API Integration Standards**:
```javascript
// Consistent error handling
async function handleApiCall(apiCall) {
    try {
        const result = await apiCall();
        return { success: true, data: result };
    } catch (error) {
        console.error('API Error:', error);
        return { 
            success: false, 
            error: error.message,
            code: error.code 
        };
    }
}

// Usage pattern
const result = await handleApiCall(() => 
    api.createDevice(deviceData)
);

if (result.success) {
    updateUI(result.data);
} else {
    showError(result.error);
}
```

### Documentation Requirements for Code Changes

**Code Documentation Checklist**:
```bash
# For each code change, ensure:
1. [ ] Inline comments explain complex logic
2. [ ] Function/method docstrings are complete
3. [ ] API changes are documented in endpoint docs
4. [ ] Examples are updated in documentation
5. [ ] Error handling is documented
6. [ ] Integration patterns are noted
7. [ ] Testing approach is documented
```

**Architecture Decision Documentation**:
```bash
# When making significant architectural changes:
1. Create ADR (Architecture Decision Record):
   cp /documentation/00-index/templates/adr-template.md \
      /documentation/03-architecture/decisions/ADR-{number}-{title}.md

2. Update architecture patterns if needed:
   vim /documentation/03-architecture/patterns/{relevant-pattern}.md

3. Update implementation guides:
   vim /documentation/04-implementation/{component}/README.md
```

---

## Technical Implementation Guidance

### Component Development Workflow

#### Frontend Component Development

**1. Component Planning**:
```bash
# Research existing components
cvd-search "component implementation" --categories "Implementation" "Design"

# Check design system
cat /documentation/06-design/DESIGN_SYSTEM.md

# Review UI patterns
cat /documentation/06-design/patterns/README.md
```

**2. Component Implementation**:
```javascript  
// Follow CVD component structure
class PlanogramEditor {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.api = new CVDApi();
        this.init();
    }
    
    async init() {
        await this.loadData();
        this.setupEventHandlers();
        this.render();
    }
    
    // Consistent error handling
    async handleAction(action) {
        try {
            const result = await action();
            this.handleSuccess(result);
        } catch (error) {
            this.handleError(error);
        }
    }
}
```

**3. Component Documentation**:
```bash
# Document component usage
cp /documentation/00-index/templates/component-guide-template.md \
   /documentation/04-implementation/components/your-component.md

# Include in design system if reusable
echo "- [Your Component](../implementation/components/your-component.md)" >> \
     /documentation/06-design/components/README.md
```

#### Backend Service Development

**1. Service Planning**:
```bash
# Check service patterns
cat /documentation/03-architecture/patterns/DATABASE_PATTERNS.md

# Review existing services
ls /documentation/04-implementation/backend/

# Check integration requirements
cvd-search "integration pattern" --categories "Architecture"
```

**2. Service Implementation**:
```python
# Follow CVD service structure
class PlanogramService:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def create_planogram(self, device_id: int, planogram_data: dict) -> dict:
        """Create new planogram with validation and audit logging."""
        try:
            # Validate input
            self._validate_planogram_data(planogram_data)
            
            # Check permissions
            self._check_user_permissions(device_id)
            
            # Create planogram
            planogram = self._insert_planogram(device_id, planogram_data)
            
            # Log activity
            self._audit_log("PLANOGRAM_CREATED", planogram['id'])
            
            return planogram
            
        except ValidationError as e:
            raise ServiceError(f"Invalid planogram data: {e}")
        except PermissionError as e:
            raise ServiceError(f"Access denied: {e}")
```

**3. Service Documentation**:
```bash
# Document service API
cp /documentation/00-index/templates/api-endpoint-template.md \
   /documentation/05-development/api/endpoints/your-service.md

# Update implementation guide
vim /documentation/04-implementation/backend/your-service.md
```

### Database Development Patterns

#### Schema Changes

**1. Schema Change Process**:
```bash
# Review existing schema
cat /documentation/09-reference/database/cvd-database-schema.sql

# Check database patterns
cat /documentation/03-architecture/patterns/DATABASE_PATTERNS.md

# Plan migration strategy
cvd-search "database migration" --tags "database"
```

**2. Migration Implementation**:
```python
# Follow migration standards
def migrate_add_planogram_optimization():
    """
    Add planogram optimization tables and indexes.
    
    Migration: Add support for AI-powered planogram optimization
    Version: 1.5.0
    Date: 2025-08-12
    """
    cursor.execute("""
        CREATE TABLE planogram_optimizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            planogram_id INTEGER NOT NULL,
            optimization_data JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (planogram_id) REFERENCES planograms(id)
        )
    """)
    
    # Add indexes for performance
    cursor.execute("""
        CREATE INDEX idx_planogram_optimizations_planogram_id 
        ON planogram_optimizations(planogram_id)
    """)
```

**3. Migration Documentation**:
```bash
# Update schema documentation
vim /documentation/09-reference/database/cvd-database-schema.sql

# Document migration in ADR if significant
cp /documentation/03-architecture/decisions/ADR-template.md \
   /documentation/03-architecture/decisions/ADR-{number}-schema-change.md
```

### Testing Integration

#### Test Development Workflow

**1. Test Planning**:
```bash
# Review testing strategy  
cat /documentation/05-development/testing/STRATEGY.md

# Check test patterns
cat /documentation/05-development/testing/PATTERNS.md

# Review examples
ls /documentation/05-development/testing/examples/
```

**2. Test Implementation**:
```python
# Follow CVD testing patterns
import unittest
from unittest.mock import Mock, patch
from app import app, db
from planogram_service import PlanogramService

class TestPlanogramService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures and test database."""
        self.app = app.test_client()
        self.service = PlanogramService(db)
        
    def test_create_planogram_success(self):
        """Test successful planogram creation with valid data."""
        # Arrange
        device_id = 123
        planogram_data = {
            "name": "Test Planogram",
            "slots": [{"position": 1, "product_id": 1}]
        }
        
        # Act  
        result = self.service.create_planogram(device_id, planogram_data)
        
        # Assert
        self.assertIsNotNone(result['id'])
        self.assertEqual(result['name'], "Test Planogram")
        
    def test_create_planogram_invalid_data(self):
        """Test planogram creation with invalid data raises error."""
        with self.assertRaises(ServiceError):
            self.service.create_planogram(123, {})
```

**3. Test Documentation**:
```bash
# Update test documentation
vim /documentation/05-development/testing/GUIDE.md

# Add test examples if novel patterns
cp your_test.py /documentation/05-development/testing/examples/
```

---

## Development Environment Integration

### IDE and Editor Setup

#### Visual Studio Code Integration

**Recommended Extensions**:
```json
// .vscode/extensions.json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.flake8", 
        "ms-vscode.vscode-json",
        "bradlc.vscode-tailwindcss",
        "formulahendry.auto-rename-tag"
    ]
}
```

**Workspace Settings**:
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "editor.rulers": [80, 120],
    "files.associations": {
        "*.md": "markdown"
    },
    "markdown.preview.breaks": true
}
```

**CVD Documentation Snippets**:
```json
// .vscode/cvd-docs.code-snippets
{
    "CVD API Endpoint Doc": {
        "scope": "markdown",
        "prefix": "cvd-api",
        "body": [
            "# ${1:Endpoint Name}",
            "",
            "## Overview",
            "${2:Brief description}",
            "",
            "## Endpoint Details",
            "- **URL**: `${3:HTTP_METHOD} ${4:/api/path}`",
            "- **Authentication**: Required",
            "- **Roles**: ${5:Admin, Manager}",
            "",
            "## Request Format",
            "```json",
            "${6:request_example}",
            "```",
            "",
            "## Response Format", 
            "```json",
            "${7:response_example}",
            "```"
        ]
    }
}
```

#### Command Line Integration

**Shell Aliases for Development**:
```bash
# Add to ~/.bashrc or ~/.zshrc

# CVD Documentation aliases
alias cvd-search='python /path/to/documentation/00-index/scripts/search.py --search'
alias cvd-api='cat /path/to/documentation/05-development/api/OVERVIEW.md'
alias cvd-patterns='ls /path/to/documentation/03-architecture/patterns/'
alias cvd-tests='cat /path/to/documentation/05-development/testing/STRATEGY.md'

# CVD Development workflow
alias cvd-dev-setup='cd /path/to/cvd && source venv/bin/activate'
alias cvd-run-tests='python -m pytest tests/ -v'
alias cvd-validate-docs='cd /path/to/documentation/00-index/scripts && ./validate-all.sh'

# Quick access to common documentation
alias cvd-coding-standards='cat /path/to/documentation/05-development/CODING_STANDARDS.md'
alias cvd-api-patterns='cat /path/to/documentation/03-architecture/patterns/API_PATTERNS.md'
```

**Development Workflow Scripts**:
```bash
#!/bin/bash
# Save as ~/bin/cvd-dev-workflow

case $1 in
  "feature")
    echo "=== Starting Feature Development ==="
    cvd-search "$2" --categories "Requirements" "Architecture"
    ;;
  "api")
    echo "=== API Development Resources ==="
    cat /path/to/documentation/03-architecture/patterns/API_PATTERNS.md
    ;;
  "test")
    echo "=== Running Tests and Validation ==="
    cd /path/to/cvd && python -m pytest tests/ -v
    cd /path/to/documentation/00-index/scripts && ./validate-all.sh
    ;;
  "docs")
    echo "=== Rebuilding Documentation ==="
    cd /path/to/documentation/00-index/scripts
    python search.py --build
    ./link-checker.sh
    ;;
  *)
    echo "Usage: cvd-dev-workflow [feature|api|test|docs] [feature-name]"
    ;;
esac
```

### Git Integration

#### Pre-Commit Hooks for Documentation

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate documentation changes
if git diff --cached --name-only | grep -q "documentation/"; then
    echo "Validating documentation changes..."
    
    cd documentation/00-index/scripts
    
    # Check for broken links
    ./link-checker.sh
    if [ $? -ne 0 ]; then
        echo "Documentation validation failed: broken links found"
        exit 1
    fi
    
    # Rebuild search index if content changed
    python search.py --build
    
    # Add updated search index to commit
    git add ../SEARCH_INDEX.json
    
    echo "Documentation validation passed"
fi
```

#### Commit Message Templates

```bash
# .gitmessage template for documentation changes
# feat(docs): add new API endpoint documentation
# fix(docs): correct broken cross-references  
# docs: update developer workflow guide
# 
# - Describe what documentation was changed
# - Mention any new cross-references added
# - Note if search index needs rebuilding
#
# Closes: #issue-number
```

---

## Advanced Development Topics

### Performance Considerations

#### Documentation System Performance

**Search Index Optimization**:
```bash
# Monitor search performance
python /documentation/00-index/scripts/search.py --stats

# Expected metrics:
# - Index size: < 5MB
# - Search response: < 100ms
# - Memory usage: < 10MB

# Optimize for large result sets
cvd-search "broad-term" --max-results 10 --categories "specific"
```

**Mobile Development Considerations**:
```bash
# Test mobile documentation access
# - Search functionality on 3G networks
# - Table responsiveness on small screens  
# - Code block formatting on mobile

# Known issues (being addressed):
# - Search index load time on 3G: 5.8 seconds
# - Table horizontal scroll on mobile
# - Code block overflow on small screens
```

#### Application Performance Integration

**Performance Documentation Standards**:
```python
def performance_critical_function():
    """
    Performance-critical function with documented constraints.
    
    Performance Requirements:
    - Response time: < 200ms for typical requests
    - Memory usage: < 50MB per request
    - Database queries: < 5 per request
    
    Monitoring:
    - Log execution time for requests > 100ms
    - Alert if memory usage exceeds 40MB
    - Database query count tracking enabled
    """
```

**Performance Testing Documentation**:
```bash
# Document performance test results
cp /documentation/00-index/templates/performance-test-template.md \
   /documentation/05-development/testing/performance/{feature}-performance.md

# Include baseline metrics and acceptance criteria
# Update after significant performance changes
```

### Security Integration

#### Security Documentation Requirements

**Security-Related Code Documentation**:
```python
@require_auth
@require_role(['admin', 'manager'])  
def sensitive_operation():
    """
    Sensitive operation requiring elevated permissions.
    
    Security Considerations:
    - Requires authentication and admin/manager role
    - Input validation applied to all parameters
    - Audit logging enabled for all operations
    - Rate limiting: 10 requests per minute per user
    
    Security Documentation:
    - See: /documentation/03-architecture/SECURITY.md
    - Patterns: /documentation/03-architecture/patterns/SECURITY_PATTERNS.md
    """
```

**Security Change Process**:
```bash
# For security-related changes:
1. Review security patterns:
   cat /documentation/03-architecture/patterns/SECURITY_PATTERNS.md

2. Update security documentation:
   vim /documentation/03-architecture/SECURITY.md

3. Document in ADR if architectural change:
   cp /documentation/03-architecture/decisions/ADR-template.md \
      /documentation/03-architecture/decisions/ADR-{n}-security-change.md

4. Update runbooks if operational impact:
   vim /documentation/05-development/deployment/runbooks/SECURITY_AUDIT.md
```

---

## Developer Training Completion

### Developer Skills Assessment

**Technical Documentation Skills** (Score: ___/10):
- [ ] Can navigate efficiently to relevant technical documentation
- [ ] Can find and use API documentation effectively  
- [ ] Can contribute technical documentation following standards
- [ ] Can integrate documentation workflow with development process
- [ ] Can troubleshoot using available technical resources

**Code Integration Skills** (Score: ___/10):
- [ ] Follows CVD coding standards consistently
- [ ] Documents code changes appropriately 
- [ ] Updates API documentation with code changes
- [ ] Creates appropriate tests and test documentation
- [ ] Integrates architecture decisions into implementation

**Development Workflow Skills** (Score: ___/10):
- [ ] Uses search effectively for development tasks
- [ ] Follows established patterns and anti-patterns
- [ ] Documents architectural decisions appropriately
- [ ] Maintains cross-references in documentation
- [ ] Validates documentation changes before commit

**Advanced Integration Skills** (Score: ___/10):
- [ ] Optimizes documentation for team workflow  
- [ ] Contributes to documentation system improvements
- [ ] Mentors other developers on documentation usage
- [ ] Identifies and addresses documentation gaps
- [ ] Maintains high documentation quality standards

**Total Developer Score**: ___/40

### Next Steps for Developers

**Score 32-40 (Expert Level)**:
- Lead documentation improvement initiatives
- Mentor new developers on documentation standards
- Contribute to documentation system architecture
- Champion best practices across development team

**Score 24-31 (Proficient Level)**:
- Use documentation system independently
- Contribute regularly to documentation updates
- Help maintain documentation quality
- Assist with developer onboarding

**Score 16-23 (Developing Level)**:  
- Focus on specific areas needing improvement
- Practice with hands-on exercises
- Pair with experienced developers for guidance
- Complete additional focused training

**Score Below 16 (Needs Support)**:
- Schedule one-on-one technical mentoring
- Complete basic training before advanced topics
- Focus on fundamental workflow integration
- Regular check-ins with tech lead

---

## Developer Resources Quick Reference

### Essential Commands
```bash
# Search and navigation
cvd-search "query" --categories "Development" "Architecture"
cvd-search "API endpoint" --tags "api"

# Documentation maintenance
cd /documentation/00-index/scripts/
python search.py --build
./validate-all.sh
./link-checker.sh

# Development workflow
cvd-dev-workflow feature "feature-name"
cvd-dev-workflow api
cvd-dev-workflow test
```

### Key Documentation Paths
```
📁 05-development/CODING_STANDARDS.md      ← Code quality standards
📁 05-development/api/OVERVIEW.md          ← API architecture guide
📁 03-architecture/patterns/API_PATTERNS.md ← API design patterns
📁 05-development/testing/STRATEGY.md      ← Testing approach
📁 09-reference/cheat-sheets/DEVELOPER_COMMANDS.md ← Quick commands
```

### Templates for Developers
```
📄 00-index/templates/api-endpoint-template.md
📄 00-index/templates/component-guide-template.md  
📄 00-index/templates/adr-template.md
📄 00-index/templates/troubleshooting-template.md
```

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-08-12  
**Target Audience**: Software developers, technical leads, DevOps engineers  
**Prerequisites**: Completed main CVD documentation training  
**Next Review**: 2025-11-12