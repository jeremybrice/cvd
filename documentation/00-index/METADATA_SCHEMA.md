---
title: "CVD Documentation Metadata Schema"
category: "Documentation Standards"
tags: ["metadata", "schema", "standards", "frontmatter"]
created: "2025-08-12"
updated: "2025-08-12"
version: "1.0"
author: "Documentation Team"
audience: "developers"
description: "Comprehensive metadata schema and validation rules for CVD documentation"
---

# CVD Documentation Metadata Schema

This document defines the comprehensive metadata schema for all CVD documentation. The metadata system enables search, discovery, categorization, and automated processing of documentation content.

## Table of Contents

1. [Schema Overview](#schema-overview)
2. [Required Fields](#required-fields)
3. [Optional Fields](#optional-fields)
4. [Field Specifications](#field-specifications)
5. [Category Taxonomy](#category-taxonomy)
6. [Tag Taxonomy](#tag-taxonomy)
7. [Audience Definitions](#audience-definitions)
8. [Validation Rules](#validation-rules)
9. [Usage Examples](#usage-examples)

## Schema Overview

All CVD documentation files must include YAML frontmatter with metadata conforming to this schema. The metadata system supports:

- **Content Discovery**: Search and filtering by tags, category, audience
- **Quality Management**: Version tracking, review scheduling, deprecation
- **User Experience**: Difficulty levels, time estimates, prerequisites
- **Automation**: Build processes, link validation, content auditing

### Schema Structure

```yaml
---
# REQUIRED FIELDS
title: "Document Title"
category: "Primary Category"
tags: ["tag1", "tag2", "tag3"]
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
version: "X.Y"

# OPTIONAL FIELDS
author: "Author Name"
contributors: ["Name 1", "Name 2"]
audience: "target-audience"
difficulty: "skill-level"
prerequisites: ["Requirement 1", "Requirement 2"]
related_docs: ["../path/doc1.md", "../path/doc2.md"]
estimated_time: "15 minutes"
description: "Brief description"
deprecated: false
review_date: "YYYY-MM-DD"
changelog: ["Version: Description"]
---
```

## Required Fields

These fields must be present in all documentation:

### title

**Type**: String  
**Length**: 10-80 characters  
**Description**: Human-readable document title  
**Format**: Title case, descriptive  

```yaml
title: "Device Configuration Guide"
title: "API Authentication Reference"
title: "Troubleshooting Service Order Issues"
```

### category

**Type**: String  
**Description**: Primary document category from taxonomy  
**Validation**: Must match predefined category list  

```yaml
category: "User Guides"
category: "API Reference"
category: "Troubleshooting"
```

### tags

**Type**: Array of strings  
**Length**: 2-5 tags  
**Format**: Lowercase, kebab-case  
**Description**: Searchable keywords describing content  

```yaml
tags: ["authentication", "security", "api"]
tags: ["planogram", "device-management", "configuration"]
tags: ["troubleshooting", "service-orders", "workflow"]
```

### created

**Type**: String  
**Format**: ISO date (YYYY-MM-DD)  
**Description**: Initial creation date  

```yaml
created: "2025-08-12"
```

### updated

**Type**: String  
**Format**: ISO date (YYYY-MM-DD)  
**Description**: Last modification date  

```yaml
updated: "2025-08-12"
```

### version

**Type**: String  
**Format**: Semantic versioning (minimum X.Y)  
**Description**: Document version for change tracking  

```yaml
version: "1.0"    # Initial version
version: "1.1"    # Minor updates
version: "2.0"    # Major revisions
```

## Optional Fields

These fields enhance discoverability and user experience:

### author

**Type**: String  
**Description**: Primary author name  

```yaml
author: "Technical Writing Team"
author: "Jane Smith"
```

### contributors

**Type**: Array of strings  
**Description**: Additional contributors  

```yaml
contributors: ["John Doe", "Maria Garcia", "Alex Chen"]
```

### audience

**Type**: String  
**Values**: `developers` | `end-users` | `admins` | `all`  
**Description**: Target audience for content  

```yaml
audience: "developers"    # Technical documentation
audience: "end-users"     # User-facing guides
audience: "admins"        # System administration
audience: "all"           # General audience
```

### difficulty

**Type**: String  
**Values**: `beginner` | `intermediate` | `advanced`  
**Description**: Required skill level  

```yaml
difficulty: "beginner"      # No prior knowledge needed
difficulty: "intermediate"  # Some experience required
difficulty: "advanced"      # Expert-level content
```

### prerequisites

**Type**: Array of strings  
**Description**: Required knowledge or setup  

```yaml
prerequisites:
  - "Basic Python knowledge"
  - "CVD system access"
  - "Completed initial setup"
```

### related_docs

**Type**: Array of strings  
**Description**: Relative paths to related documents  

```yaml
related_docs:
  - "../api/authentication-guide.md"
  - "../user-guides/device-management.md"
  - "./troubleshooting-common-issues.md"
```

### estimated_time

**Type**: String  
**Format**: "[number] [unit]"  
**Description**: Expected reading/completion time  

```yaml
estimated_time: "5 minutes"    # Quick reference
estimated_time: "15 minutes"   # Standard guide
estimated_time: "30 minutes"   # Comprehensive tutorial
estimated_time: "1 hour"       # In-depth documentation
```

### description

**Type**: String  
**Length**: 50-200 characters  
**Description**: Brief content summary for search results  

```yaml
description: "Step-by-step guide for configuring vending machine devices in the CVD system"
```

### deprecated

**Type**: Boolean  
**Default**: false  
**Description**: Marks document as deprecated  

```yaml
deprecated: false        # Active document
deprecated: true         # Deprecated content
```

### review_date

**Type**: String  
**Format**: ISO date (YYYY-MM-DD)  
**Description**: Scheduled review date  

```yaml
review_date: "2025-12-01"
```

### changelog

**Type**: Array of strings  
**Description**: Version history and changes  

```yaml
changelog:
  - "2.0: Complete rewrite for new API"
  - "1.2: Added troubleshooting section"
  - "1.1: Fixed broken examples"
  - "1.0: Initial version"
```

## Field Specifications

### String Length Limits

| Field | Minimum | Maximum | Notes |
|-------|---------|---------|-------|
| title | 10 | 80 | Descriptive but concise |
| description | 50 | 200 | Search result snippet |
| author | 2 | 50 | Name or team identifier |
| estimated_time | 5 | 20 | Include units |

### Date Format

All dates must use ISO 8601 format (YYYY-MM-DD):

```yaml
created: "2025-08-12"      # ✅ Correct
updated: "2025-12-31"      # ✅ Correct

created: "08/12/2025"      # ❌ US format
updated: "12-Aug-2025"     # ❌ Text month
created: "2025/08/12"      # ❌ Wrong separators
```

### Version Format

Use semantic versioning principles:

```yaml
version: "1.0"      # ✅ Major.Minor
version: "1.2"      # ✅ Minor update
version: "2.0"      # ✅ Major revision
version: "1.2.1"    # ✅ Patch (optional)

version: "v1.0"     # ❌ Prefix
version: "1"        # ❌ Missing minor
version: "latest"   # ❌ Non-numeric
```

## Category Taxonomy

All documents must use one of these predefined categories:

### Primary Categories

#### Getting Started
For introductory and onboarding content:
- System overviews
- First-time user guides
- Quick start tutorials
- Initial setup procedures

#### User Guides
For end-user documentation:
- Feature-specific guides
- Step-by-step procedures
- Workflow documentation
- Best practices

#### API Reference
For technical API documentation:
- Endpoint documentation
- Authentication guides
- SDK references
- Integration examples

#### Development
For developer-focused content:
- Setup and installation
- Development workflows
- Code examples
- Architecture guides

#### Troubleshooting
For problem resolution:
- Common issues and solutions
- Diagnostic procedures
- Error message references
- FAQ sections

#### Operations
For deployment and maintenance:
- Deployment guides
- Configuration management
- Monitoring and alerting
- Backup and recovery

#### Reference
For quick lookup information:
- Glossaries and terminology
- Configuration references
- Keyboard shortcuts
- Command references

### Category Usage Guidelines

Choose the most specific applicable category:

```yaml
# ✅ Good category choices
category: "API Reference"        # For /api/auth/login endpoint docs
category: "User Guides"          # For planogram creation tutorial
category: "Troubleshooting"      # For service order error solutions
category: "Getting Started"      # For new user onboarding

# ❌ Poor category choices
category: "Documentation"        # Too generic
category: "General"             # Not descriptive
category: "Miscellaneous"       # Catch-all category
```

## Tag Taxonomy

Tags enable cross-category content discovery. Use 2-5 tags per document.

### Core Business Tags

**Device Management**:
- `device-management`
- `device-configuration`
- `cabinet-setup`
- `device-monitoring`

**Operations**:
- `service-orders`
- `route-planning`
- `driver-app`
- `field-operations`

**Analytics & Reporting**:
- `analytics`
- `reporting`
- `dashboards`
- `metrics`

**Product Management**:
- `planogram`
- `product-catalog`
- `inventory`
- `pricing`

### Technical Tags

**Development**:
- `api`
- `authentication`
- `integration`
- `sdk`
- `webhooks`

**System**:
- `database`
- `backup`
- `security`
- `performance`
- `configuration`

**User Interface**:
- `ui`
- `frontend`
- `mobile`
- `responsive`

### Process Tags

**Documentation Types**:
- `tutorial`
- `reference`
- `guide`
- `quickstart`
- `troubleshooting`

**Skill Levels**:
- `beginner`
- `intermediate`
- `advanced`
- `expert`

**Workflows**:
- `setup`
- `configuration`
- `maintenance`
- `upgrade`

### Tag Formatting Rules

- Use lowercase only
- Use hyphens for multi-word tags
- Be specific but not overly narrow
- Avoid redundancy with category

```yaml
# ✅ Good tag usage
tags: ["device-configuration", "cabinet-setup", "tutorial", "beginner"]
tags: ["api", "authentication", "security", "integration"]
tags: ["troubleshooting", "service-orders", "workflow", "errors"]

# ❌ Poor tag usage
tags: ["Device", "Configuration"]        # Wrong case
tags: ["device_configuration"]           # Wrong separator
tags: ["devices", "device-mgmt"]         # Inconsistent terminology
tags: ["guide"]                          # Too generic, only 1 tag
```

## Audience Definitions

### developers

**Target**: Software developers, integrators, technical implementers  
**Content**: API documentation, code examples, technical guides  
**Assumes**: Programming knowledge, technical background  

**Example Topics**:
- REST API integration
- Database schema documentation
- Custom development guides
- SDK references

### end-users

**Target**: CVD system users (operators, managers, drivers)  
**Content**: User interface guides, feature tutorials, workflows  
**Assumes**: Business context, no technical background  

**Example Topics**:
- Creating planograms
- Managing service orders
- Using analytics dashboards
- Mobile app guides

### admins

**Target**: System administrators, IT personnel  
**Content**: Installation, configuration, maintenance procedures  
**Assumes**: System administration knowledge  

**Example Topics**:
- System installation
- User management
- Security configuration
- Backup procedures

### all

**Target**: Mixed or general audience  
**Content**: Overviews, getting started, general information  
**Assumes**: No specific technical knowledge  

**Example Topics**:
- System overviews
- Getting started guides
- General best practices
- FAQ sections

## Validation Rules

### Required Field Validation

All required fields must be present and valid:

```yaml
# ✅ Complete required metadata
---
title: "Device Configuration Guide"
category: "User Guides"
tags: ["device-management", "configuration", "tutorial"]
created: "2025-08-12"
updated: "2025-08-12"
version: "1.0"
---

# ❌ Missing required fields
---
title: "Device Configuration Guide"
# Missing: category, tags, created, updated, version
---
```

### Field Format Validation

Each field must conform to its specified format:

```yaml
# ✅ Valid formats
title: "Complete User Management Guide"        # 10-80 chars
tags: ["user-mgmt", "admin", "guide"]         # 2-5 kebab-case tags
created: "2025-08-12"                          # ISO date
version: "1.0"                                 # Semantic version

# ❌ Invalid formats
title: "Guide"                                 # Too short (<10 chars)
title: "This is an extremely long title that exceeds the maximum character limit" # Too long
tags: ["UserManagement"]                       # Wrong case
created: "08/12/2025"                         # Wrong date format
version: "v1"                                 # Wrong version format
```

### Cross-Field Validation

Some fields must be consistent with others:

```yaml
# ✅ Consistent metadata
category: "API Reference"
tags: ["api", "authentication", "reference"]  # Tags align with category
audience: "developers"                         # Appropriate for API docs

# ❌ Inconsistent metadata
category: "User Guides"
tags: ["api", "technical", "development"]     # Tags don't match category
audience: "end-users"                          # Wrong audience for technical content
```

## Usage Examples

### User Guide Document

```yaml
---
title: "Creating Your First Planogram"
category: "User Guides"
tags: ["planogram", "device-configuration", "tutorial", "beginner"]
created: "2025-08-12"
updated: "2025-08-12"
version: "1.0"
author: "User Experience Team"
audience: "end-users"
difficulty: "beginner"
prerequisites: ["CVD system access", "Basic device setup completed"]
estimated_time: "20 minutes"
description: "Step-by-step tutorial for creating and configuring your first planogram in the CVD system"
review_date: "2025-11-12"
related_docs:
  - "../getting-started/device-setup-guide.md"
  - "./advanced-planogram-features.md"
---
```

### API Reference Document

```yaml
---
title: "Authentication API Reference"
category: "API Reference"
tags: ["api", "authentication", "security", "reference"]
created: "2025-08-12"
updated: "2025-08-12"
version: "2.0"
author: "Development Team"
contributors: ["API Team", "Security Team"]
audience: "developers"
difficulty: "intermediate"
prerequisites: ["REST API knowledge", "OAuth2 understanding"]
estimated_time: "10 minutes"
description: "Complete API reference for CVD authentication endpoints including OAuth2 flow"
changelog:
  - "2.0: Updated for OAuth2 implementation"
  - "1.1: Added refresh token endpoint"
  - "1.0: Initial API documentation"
related_docs:
  - "./api-getting-started.md"
  - "../development/sdk-integration-guide.md"
---
```

### Troubleshooting Document

```yaml
---
title: "Service Order Workflow Issues"
category: "Troubleshooting"
tags: ["troubleshooting", "service-orders", "workflow", "errors"]
created: "2025-08-12"
updated: "2025-08-12"
version: "1.1"
audience: "all"
difficulty: "beginner"
estimated_time: "5 minutes"
description: "Common service order workflow issues and their solutions"
related_docs:
  - "../user-guides/service-order-management.md"
  - "./general-troubleshooting.md"
changelog:
  - "1.1: Added mobile app specific issues"
  - "1.0: Initial troubleshooting guide"
---
```

### Development Guide

```yaml
---
title: "Setting Up Local Development Environment"
category: "Development"
tags: ["setup", "development", "environment", "installation"]
created: "2025-08-12"
updated: "2025-08-12"
version: "1.0"
author: "Development Team"
audience: "developers"
difficulty: "intermediate"
prerequisites: ["Python 3.8+", "Git", "Code editor"]
estimated_time: "45 minutes"
description: "Complete guide for setting up CVD development environment locally"
related_docs:
  - "./coding-standards.md"
  - "./testing-guidelines.md"
  - "../api/development-api-access.md"
---
```

---

## Validation Checklist

Before publishing documentation, verify:

### Required Fields ✓
- [ ] title (10-80 characters, descriptive)
- [ ] category (from approved taxonomy)
- [ ] tags (2-5 tags, kebab-case, relevant)
- [ ] created (ISO date format)
- [ ] updated (ISO date format)
- [ ] version (semantic versioning)

### Optional Fields (if used) ✓
- [ ] author/contributors (meaningful names)
- [ ] audience (matches content target)
- [ ] difficulty (matches content complexity)
- [ ] prerequisites (accurate requirements)
- [ ] estimated_time (realistic estimate)
- [ ] description (50-200 characters)
- [ ] related_docs (valid relative paths)

### Content Consistency ✓
- [ ] Tags align with category
- [ ] Audience matches content type
- [ ] Difficulty matches prerequisites
- [ ] Version reflects document maturity

### Format Validation ✓
- [ ] YAML syntax is valid
- [ ] All dates use YYYY-MM-DD format
- [ ] Tags use lowercase kebab-case
- [ ] Version follows semantic versioning

---

**Last Updated**: 2025-08-12  
**Version**: 1.0  
**Next Review**: 2025-11-12