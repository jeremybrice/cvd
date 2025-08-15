# CVD Documentation Standards

This document defines the comprehensive documentation standards for the CVD (Vision Device Configuration) project. All documentation must adhere to these standards to ensure consistency, accessibility, and maintainability across the entire documentation system.

## Table of Contents

1. [File Structure and Organization](#file-structure-and-organization)
2. [Markdown Standards](#markdown-standards)
3. [Metadata Requirements](#metadata-requirements)
4. [Content Standards](#content-standards)
5. [Code Documentation](#code-documentation)
6. [Cross-Reference System](#cross-reference-system)
7. [Version Control Practices](#version-control-practices)
8. [Review and Maintenance](#review-and-maintenance)

## File Structure and Organization

### Naming Conventions

All documentation files must follow **kebab-case** naming conventions:

**✅ Correct Examples:**
- `user-management-guide.md`
- `api-authentication-reference.md`
- `planogram-optimization-tips.md`
- `service-order-troubleshooting.md`

**❌ Incorrect Examples:**
- `UserManagementGuide.md` (PascalCase)
- `api_authentication_reference.md` (snake_case)
- `planogram optimization tips.md` (spaces)
- `Service-Order-Troubleshooting.MD` (incorrect extension case)

### Directory Structure

Follow the established CVD documentation hierarchy:

```
documentation/
├── 00-index/                    # Navigation and discovery
├── 01-project-core/             # Foundation documents
├── 02-requirements/             # Requirements and specifications
├── 03-architecture/             # System architecture
├── 04-development/              # Development guides
├── 05-api/                      # API documentation
├── 06-user-guides/              # End-user documentation
├── 07-operations/               # Deployment and operations
├── 08-troubleshooting/          # Problem resolution
└── 09-reference/                # Quick reference materials
```

### File Location Guidelines

- **API endpoints**: Place in `/05-api/endpoints/`
- **User guides**: Place in `/06-user-guides/[feature]/`
- **Troubleshooting**: Place in `/08-troubleshooting/[category]/`
- **Architecture docs**: Place in `/03-architecture/[system|decisions|patterns]/`
- **Development guides**: Place in `/04-development/[setup|guides|best-practices]/`

## Markdown Standards

### Document Structure

Every documentation file must follow this structure:

```markdown
---
[YAML frontmatter - see Metadata Requirements]
---

# Document Title

Brief description of the document's purpose (1-2 sentences).

## Table of Contents (for documents >500 words)

1. [Section One](#section-one)
2. [Section Two](#section-two)
3. [References](#references)

## Section One

Content...

## References

- [Related Document](../path/to/document.md)
- [External Link](https://example.com)
```

### Heading Guidelines

- Use **only one H1** per document (the main title)
- Follow logical hierarchy: H1 → H2 → H3 → H4 (maximum depth: H4)
- Use descriptive, action-oriented headings
- Include anchors for cross-referencing

**✅ Good Examples:**
```markdown
# Configuring Device Settings
## Adding a New Device
### Setting Cabinet Parameters
#### Defining Slot Configuration
```

**❌ Poor Examples:**
```markdown
# Setup
## Stuff
### More Things
```

### Code Block Standards

All code blocks must specify the language for proper syntax highlighting:

**✅ Correct:**
```markdown
```javascript
const api = new CVDApi();
const devices = await api.getDevices();
```

```sql
SELECT * FROM devices WHERE status = 'active';
```

```bash
python app.py --port 5000
```
```

**❌ Incorrect:**
```markdown
```
const api = new CVDApi();
```

    // Four-space indented code (avoid)
    const api = new CVDApi();
```

### List Formatting

Use consistent list formatting with proper spacing:

**✅ Correct:**
```markdown
## Setup Steps

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   - Set `ANTHROPIC_API_KEY` environment variable
   - Create `.env` file from template
   - Verify database connection

3. **Run the application**
   ```bash
   python app.py
   ```
```

### Table Standards

Use proper table formatting with headers and alignment:

```markdown
| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | integer | Yes | Device unique identifier |
| `name` | string | Yes | Device display name |
| `status` | string | No | Current operational status |
```

### Link Standards

- Use descriptive link text (never "click here")
- Prefer relative paths for internal documentation
- Include link descriptions for external resources

**✅ Correct:**
```markdown
See [User Management Guide](../06-user-guides/user-management-guide.md) for details.
Review the [Flask documentation](https://flask.palletsprojects.com/) for framework details.
```

**❌ Incorrect:**
```markdown
Click [here](../06-user-guides/user-management-guide.md) for details.
See [this link](https://flask.palletsprojects.com/).
```

### Emphasis and Formatting

- Use **bold** for UI elements, important terms, and emphasis
- Use *italics* for definitions and subtle emphasis
- Use `code` for variable names, file paths, and inline code
- Use > blockquotes for important notes and warnings

**Examples:**
```markdown
Click the **Save Changes** button to *confirm* your settings.
Set the `DATABASE_URL` environment variable in your `.env` file.

> **Warning**: Deleting a device will permanently remove all associated data.

> **Note**: This feature requires Admin or Manager role access.
```

## Metadata Requirements

Every documentation file must include YAML frontmatter with required metadata:

### Required Fields

```yaml
---
title: "Descriptive Document Title"
category: "Primary Category"
tags: ["tag1", "tag2", "tag3"]
created: "2025-08-12"
updated: "2025-08-12"
version: "1.0"
---
```

### Optional Fields

```yaml
---
# Optional metadata fields
author: "Author Name"
contributors: ["Name 1", "Name 2"]
audience: "developers" # or "end-users", "admins", "all"
difficulty: "beginner" # or "intermediate", "advanced"
prerequisites: ["Basic Python knowledge", "CVD system access"]
related_docs: 
  - "../api/authentication-guide.md"
  - "../user-guides/device-management.md"
estimated_time: "15 minutes"
description: "Brief description for search and discovery"
deprecated: false
review_date: "2025-12-01"
---
```

### Metadata Validation Rules

- **title**: Must be 10-80 characters, descriptive
- **category**: Must match existing category taxonomy
- **tags**: 2-5 relevant tags, lowercase, hyphenated
- **created/updated**: Use ISO date format (YYYY-MM-DD)
- **version**: Semantic versioning (X.Y format minimum)
- **audience**: One of "developers", "end-users", "admins", "all"
- **difficulty**: One of "beginner", "intermediate", "advanced"

## Content Standards

### Writing Style

#### Voice and Tone
- Use **active voice** whenever possible
- Write in **second person** ("you") for user-facing documentation
- Use **present tense** for current functionality
- Maintain a **professional, helpful tone**

**✅ Good Examples:**
```markdown
You can configure device settings through the Device Management page.
The system validates user input before saving changes.
Click the Save button to apply your configuration.
```

**❌ Poor Examples:**
```markdown
Device settings can be configured through the Device Management page. (passive)
One might configure device settings... (third person)
The system will validate user input... (future tense)
```

#### Clarity and Concision
- Use short, clear sentences (aim for 15-20 words maximum)
- Define technical terms on first use
- Use parallel structure in lists
- Avoid jargon and unnecessary complexity

#### Accessibility
- Use descriptive headings that make sense out of context
- Provide alt text descriptions for images
- Use clear, descriptive link text
- Structure content logically with proper heading hierarchy

### Step-by-Step Procedures

Format all procedures consistently:

```markdown
## Configuring Device Settings

To configure device settings:

1. **Navigate to Device Management**
   - Click **Devices** in the main navigation
   - Select **Device List** from the dropdown

2. **Select target device**
   - Find the device in the list
   - Click the **Edit** button (pencil icon)

3. **Update settings**
   ```javascript
   // Example configuration
   const config = {
     name: "Lobby Vending Machine",
     location: "Building A - Floor 1"
   };
   ```

4. **Save changes**
   - Click **Save Changes**
   - Wait for the confirmation message
   - Verify settings in the device list

**Expected Result**: The device settings are updated and visible in the device list with a "Last Updated" timestamp.
```

### Code Examples

All code examples must be:

- **Complete and functional** (not pseudocode)
- **Tested and verified** before documentation
- **Properly commented** when necessary
- **Formatted consistently**

```javascript
// CVD API Client Usage Example
const api = new CVDApi();

try {
  // Fetch all devices with error handling
  const devices = await api.getDevices();
  
  console.log(`Found ${devices.length} devices`);
  
  // Filter active devices
  const activeDevices = devices.filter(device => device.status === 'active');
  
  return activeDevices;
} catch (error) {
  console.error('Failed to fetch devices:', error);
  throw error;
}
```

### Error Handling Documentation

Always document error conditions and solutions:

```markdown
### Common Errors

#### Authentication Failed (401)

**Error Message**: "Invalid credentials provided"

**Cause**: The API key or session token is invalid or expired.

**Solution**:
1. Verify your API key in the environment variables
2. Check if your session has expired
3. Re-authenticate if necessary

**Prevention**: Implement proper token refresh logic in your application.
```

## Code Documentation

### API Documentation Standards

Document all API endpoints using this format:

```markdown
### POST /api/devices

Creates a new device in the CVD system.

#### Request

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <token>`

**Body:**
```json
{
  "name": "Device Name",
  "type": "snack_machine",
  "location_id": 123
}
```

#### Response

**Success (201 Created):**
```json
{
  "id": 456,
  "name": "Device Name",
  "type": "snack_machine",
  "location_id": 123,
  "created_at": "2025-08-12T10:30:00Z"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "validation_failed",
  "message": "Device name is required",
  "details": {
    "name": ["This field is required"]
  }
}
```

#### Usage Example

```javascript
const newDevice = await api.createDevice({
  name: "Lobby Vending Machine",
  type: "snack_machine",
  location_id: 123
});
```
```

### Function Documentation

Document functions with clear parameters and return values:

```markdown
### calculateProfitMargin(salesData, costs)

Calculates the profit margin for a given device or product.

**Parameters:**
- `salesData` (Object): Sales data containing revenue information
  - `revenue` (number): Total revenue in dollars
  - `period` (string): Time period for the data
- `costs` (Object): Cost breakdown
  - `inventory` (number): Inventory cost
  - `operations` (number): Operational costs

**Returns:**
- (number): Profit margin as a percentage (0-100)

**Example:**
```javascript
const margin = calculateProfitMargin(
  { revenue: 1000, period: "monthly" },
  { inventory: 600, operations: 200 }
);
// Returns: 20 (20% profit margin)
```

**Throws:**
- `TypeError`: If required parameters are missing
- `RangeError`: If revenue or costs are negative
```

## Cross-Reference System

### Internal Links

Use relative paths for internal documentation links:

```markdown
For detailed API information, see [Authentication Guide](../05-api/authentication-guide.md).

Related procedures:
- [Device Configuration](../06-user-guides/device-configuration.md)
- [Service Order Management](../06-user-guides/service-orders.md)
- [Troubleshooting Device Issues](../08-troubleshooting/device-issues.md)
```

### Link Anchors

Create meaningful anchors for section references:

```markdown
## User Authentication {#user-authentication}

For authentication details, see [User Authentication](#user-authentication).
```

### Document Relationships

Always include a "Related Documentation" section:

```markdown
## Related Documentation

### Prerequisites
- [System Requirements](../01-project-core/system-requirements.md)
- [Installation Guide](../04-development/installation-guide.md)

### Next Steps
- [Advanced Configuration](./advanced-configuration.md)
- [Performance Tuning](./performance-tuning.md)

### References
- [API Reference](../05-api/complete-reference.md)
- [Troubleshooting Guide](../08-troubleshooting/configuration-issues.md)
```

## Version Control Practices

### Commit Message Standards

Use conventional commits for documentation changes:

```
docs: add authentication guide for API access

- Document OAuth2 flow implementation
- Include code examples for token management
- Add troubleshooting section for auth issues

Resolves: #123
```

**Commit Types:**
- `docs:` - Documentation changes
- `docs(api):` - API documentation changes
- `docs(fix):` - Fix existing documentation
- `docs(update):` - Update existing content

### Branch Naming

Use descriptive branch names for documentation work:

```
docs/api-authentication-guide
docs/update-user-management
docs/fix-broken-links
docs/template-library-creation
```

### Change Tracking

#### Document Updates
Update the `updated` field in frontmatter for content changes:

```yaml
---
title: "User Management Guide"
updated: "2025-08-12"  # Changed from previous date
version: "1.1"         # Increment version
---
```

#### Breaking Changes
For significant structural changes, increment major version and document:

```yaml
---
version: "2.0"
changelog:
  - "2.0: Complete restructure of user management workflow"
  - "1.1: Added bulk operations section"
  - "1.0: Initial version"
---
```

### File History

Maintain a changelog section in major documents:

```markdown
## Document History

| Version | Date | Changes | Author |
|---------|------|---------|---------|
| 2.0 | 2025-08-12 | Complete rewrite for v2 system | J. Smith |
| 1.1 | 2025-07-15 | Added troubleshooting section | M. Johnson |
| 1.0 | 2025-06-01 | Initial version | J. Smith |
```

## Review and Maintenance

### Review Process

All documentation must undergo review before publication:

#### Self-Review Checklist
- [ ] Metadata is complete and accurate
- [ ] All links are functional
- [ ] Code examples are tested
- [ ] Spelling and grammar are correct
- [ ] Follows CVD documentation standards
- [ ] Includes proper cross-references

#### Peer Review Requirements
- Technical accuracy verification
- Clarity and comprehensibility review
- Standards compliance check
- Link validation

### Maintenance Schedule

#### Regular Maintenance
- **Weekly**: Check for broken internal links
- **Monthly**: Review and update version information
- **Quarterly**: Comprehensive content audit
- **Annually**: Major version updates and restructuring

#### Update Triggers
Update documentation when:
- API changes are implemented
- New features are released
- User workflows change
- System requirements change
- Feedback indicates confusion or errors

### Quality Assurance

#### Automated Checks
Implement automated validation for:
- Link integrity
- Metadata completeness
- Markdown formatting
- Spelling and grammar

#### Manual Reviews
Conduct manual reviews for:
- Technical accuracy
- Content clarity
- User experience
- Accessibility compliance

### Deprecation Process

When deprecating documentation:

1. **Mark as deprecated** in frontmatter:
   ```yaml
   deprecated: true
   replacement_doc: "../new-guide.md"
   deprecation_date: "2025-08-12"
   ```

2. **Add deprecation notice** at top of document:
   ```markdown
   > **⚠️ DEPRECATED**: This document is deprecated as of 2025-08-12. 
   > Please use [New Guide](../new-guide.md) instead.
   ```

3. **Maintain for 6 months** before removal
4. **Set up redirects** when possible

---

## Implementation Guidelines

### For Documentation Authors

1. **Use templates** from `/documentation/00-index/templates/`
2. **Follow the checklist** in each template
3. **Test all code examples** before publication
4. **Validate all links** before committing
5. **Request peer review** for technical content

### For Reviewers

1. **Verify technical accuracy**
2. **Test procedures step-by-step**
3. **Check standards compliance**
4. **Validate user experience**
5. **Provide constructive feedback**

### For Maintainers

1. **Monitor documentation metrics**
2. **Track user feedback and issues**
3. **Schedule regular reviews**
4. **Update templates as needed**
5. **Ensure standards evolution**

---

## Conclusion

These standards ensure that CVD documentation remains consistent, accessible, and maintainable. All contributors must follow these guidelines to maintain the quality and usability of the documentation system.

For questions about these standards or suggestions for improvements, please contact the Documentation Team or create an issue in the project repository.

**Last Updated**: 2025-08-12  
**Version**: 1.0  
**Next Review**: 2025-11-12