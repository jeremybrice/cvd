---
title: "Contributing to the CVD Knowledge Base"
author: "Documentation Team"
category: "System Administration"
tags: ["documentation", "content-creation", "knowledge-base", "contributing"]
difficulty: "Intermediate"
last_updated: "2025-08-06T10:00:00Z"
description: "Complete guide for adding new articles and managing content in the CVD Knowledge Base system"
---

# Contributing to the CVD Knowledge Base

This guide provides comprehensive instructions for adding new articles and managing content within the CVD Knowledge Base system. Whether you're a team member creating documentation or a system administrator managing the knowledge base, this guide will help you understand the complete workflow.

## Table of Contents

1. [File Structure and Organization](#file-structure-and-organization)
2. [Article Creation Process](#article-creation-process)
3. [Category Management](#category-management)
4. [Content Standards](#content-standards)
5. [Deployment Process](#deployment-process)
6. [Technical Implementation](#technical-implementation)

## File Structure and Organization

### Directory Structure

The knowledge base content is stored in the `/knowledge-base/` directory with the following structure:

```
knowledge-base/
├── getting-started/
│   ├── getting-started-overview.md
│   ├── first-login-guide.md
│   └── ...
├── feature-tutorials/
│   ├── planogram-creation-tutorial.md
│   └── ...
├── troubleshooting/
│   ├── login-issues.md
│   └── ...
├── system-administration/
│   ├── user-management-guide.md
│   ├── contributing-to-knowledge-base.md
│   └── ...
└── best-practices/
    ├── planogram-optimization-tips.md
    └── ...
```

### File Naming Conventions

- **File Format**: All articles must be in Markdown (`.md`) format
- **Naming Pattern**: Use lowercase with hyphens for spaces (e.g., `user-management-guide.md`)
- **Unique IDs**: The filename (without extension) becomes the article ID
- **Descriptive Names**: Choose names that clearly describe the article content

### Supported Categories

The system recognizes these predefined categories:

| Category | Description | Icon | Color |
|----------|-------------|------|-------|
| **Getting Started** | Essential information for new users | 📚 | Blue (#4F46E5) |
| **Feature Tutorials** | Step-by-step guides for CVD features | 🎯 | Green (#059669) |
| **Troubleshooting** | Solutions to common problems | 🔧 | Red (#DC2626) |
| **System Administration** | Advanced configuration and management | ⚙️ | Brown (#7C2D12) |
| **Best Practices** | Recommended workflows and tips | ⭐ | Purple (#9333EA) |

## Article Creation Process

### Step 1: Create the Article File

1. **Choose the appropriate category directory** based on your content
2. **Create a new `.md` file** with a descriptive name
3. **Start with the required YAML frontmatter** (see template below)

### Step 2: YAML Frontmatter Template

Every article must begin with YAML frontmatter enclosed by `---`:

```yaml
---
title: "Your Article Title Here"
author: "Your Name"
category: "Getting Started"
tags: ["tag1", "tag2", "tag3"]
difficulty: "Beginner"
last_updated: "2025-08-06T10:00:00Z"
description: "Brief description of what this article covers (max 200 characters)"
---
```

#### Required Fields

- **title**: The article title as it appears in the interface
- **author**: Your name or team name
- **category**: Must match one of the predefined categories exactly
- **tags**: Array of relevant keywords for search functionality
- **difficulty**: One of "Beginner", "Intermediate", or "Advanced"
- **last_updated**: ISO 8601 timestamp format
- **description**: Brief summary for search results and article listings

### Step 3: Content Structure

After the frontmatter, structure your content using standard Markdown:

```markdown
# Article Title

Brief introduction paragraph explaining what the article covers.

## Major Section

Content for the major section...

### Subsection

More detailed content...

## Another Major Section

Additional content...

## Next Steps

- Link to related articles
- Suggest follow-up actions
```

### Step 4: Content Guidelines

#### Writing Style
- Use clear, concise language
- Write for your target difficulty level
- Include practical examples
- Use active voice when possible

#### Formatting
- Use consistent heading hierarchy (H1 for title, H2 for major sections, H3 for subsections)
- Include code blocks with proper language syntax highlighting
- Use bullet points and numbered lists for clarity
- Add tables for structured information

#### Links and References
- Link to related knowledge base articles using relative paths
- Use descriptive link text (not "click here")
- Include external links where relevant
- Test all links before publishing

## Category Management

### Adding New Categories

To add a new category to the system:

1. **Create the directory** in `/knowledge-base/`
2. **Update the category configuration** in `/services/knowledge_base_service.py`
3. **Add the category details** in the `category_configs` dictionary:

```python
'Your New Category': {
    'description': 'Description of the category',
    'icon': '📋',  # Choose appropriate emoji
    'color': '#6366F1',  # Hex color code
    'sort_order': 6  # Display order
}
```

### Category Configuration

Each category has these properties:
- **name**: Display name (matches directory name)
- **description**: Brief explanation shown on category cards
- **icon**: Emoji icon displayed on category cards
- **color**: Hex color code for visual distinction
- **sort_order**: Numeric order for category display
- **article_count**: Automatically calculated

## Content Standards

### Accessibility Requirements

- **Alt Text**: Provide descriptive alt text for all images
- **Heading Structure**: Use proper heading hierarchy (don't skip levels)
- **Link Context**: Ensure link text is descriptive and meaningful
- **Color Independence**: Don't rely solely on color to convey information

### SEO Optimization

- **Descriptive Titles**: Use clear, keyword-rich titles
- **Meta Descriptions**: Write compelling descriptions under 200 characters
- **Tag Strategy**: Include relevant tags that users might search for
- **Internal Linking**: Link to related articles within the knowledge base

### Code Examples

When including code, use proper syntax highlighting:

````markdown
```javascript
// JavaScript example
const api = new CVDApi();
const devices = await api.getDevices();
```

```python
# Python example
from services.knowledge_base_service import KnowledgeBaseService
kb_service = KnowledgeBaseService()
```
````

### Images and Media

- **File Location**: Store images in `/knowledge-base/assets/images/`
- **Supported Formats**: PNG, JPG, GIF, SVG
- **Naming**: Use descriptive filenames with hyphens
- **Size**: Optimize images for web (under 500KB recommended)
- **Markup**: Use standard Markdown image syntax with alt text

```markdown
![Screenshot of the login page](assets/images/login-page-screenshot.png)
```

## Deployment Process

### Testing and Validation

Before publishing new content:

1. **Verify Frontmatter**: Ensure all required fields are present and correctly formatted
2. **Check Links**: Test all internal and external links
3. **Review Content**: Proofread for grammar, spelling, and clarity
4. **Test Rendering**: Preview the article in the knowledge base interface

### Publication Workflow

The knowledge base uses automatic content detection:

1. **File Creation**: When you save a new `.md` file in the knowledge base directory
2. **Automatic Scanning**: The system scans for new content every 5 minutes
3. **Content Processing**: Articles are parsed and metadata extracted
4. **Database Update**: Article information is cached in the database
5. **Immediate Availability**: New articles appear in the interface within minutes

### Content Review Process

For quality control:

1. **Draft Review**: Have a colleague review content before publishing
2. **Technical Accuracy**: Verify all procedures and code examples
3. **User Testing**: Test instructions with someone unfamiliar with the process
4. **Regular Updates**: Review articles quarterly for accuracy and relevance

### Version Control (Recommended)

While the system works without version control, we recommend:

1. **Git Integration**: Track changes to knowledge base content
2. **Branch Strategy**: Use feature branches for major content updates
3. **Commit Messages**: Use descriptive messages for content changes
4. **Collaboration**: Use pull requests for content review

## Technical Implementation Details

### API Endpoints

The knowledge base uses these API endpoints:

- **GET** `/api/knowledge-base/articles` - List all articles
- **GET** `/api/knowledge-base/articles/{id}` - Get specific article
- **GET** `/api/knowledge-base/categories` - List all categories
- **GET** `/api/knowledge-base/search?q={query}` - Search articles

### Search Functionality

The search system indexes:
- Article titles (highest weight)
- Article descriptions
- Content text
- Tags
- Category names

Search results are ranked by relevance score based on match type and frequency.

### Content Processing

The `KnowledgeBaseService` handles:

1. **File Scanning**: Recursively scans the knowledge-base directory
2. **Markdown Parsing**: Extracts frontmatter and content
3. **Metadata Generation**: Calculates word count, reading time, and content hash
4. **Search Indexing**: Creates searchable content without markdown formatting
5. **Caching**: Stores processed content in SQLite database

### Performance Considerations

- **Caching**: Articles are cached for 5 minutes to reduce file system access
- **Lazy Loading**: Content is only processed when requested
- **Database Storage**: Metadata is stored in SQLite for fast queries
- **Content Hashing**: Files are re-processed only when content changes

### File Watching (Future Enhancement)

Consider implementing file system watching for instant updates:

```python
# Example using watchdog library
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class KnowledgeBaseHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.md'):
            self.knowledge_base.scan_articles(force_refresh=True)
```

## Troubleshooting Common Issues

### Article Not Appearing

**Problem**: New article doesn't show in the interface

**Solutions**:
1. Check YAML frontmatter syntax (use a YAML validator)
2. Verify category name matches exactly (case-sensitive)
3. Ensure file is saved with `.md` extension
4. Wait up to 5 minutes for automatic refresh
5. Check server logs for parsing errors

### Search Not Working

**Problem**: Article doesn't appear in search results

**Solutions**:
1. Verify tags are formatted as an array: `["tag1", "tag2"]`
2. Check that title and description contain searchable keywords
3. Ensure content has adequate text (not just images)
4. Confirm article is in a recognized category

### Formatting Issues

**Problem**: Content doesn't render correctly

**Solutions**:
1. Use standard Markdown syntax
2. Check heading hierarchy (don't skip levels)
3. Ensure code blocks use triple backticks
4. Validate YAML frontmatter indentation
5. Test with a Markdown preview tool

### Performance Issues

**Problem**: Knowledge base loads slowly

**Solutions**:
1. Optimize image file sizes
2. Break long articles into smaller pieces
3. Remove unused media files
4. Check for infinite loops in cross-references

## Best Practices Summary

### For Content Creators

1. **Plan Before Writing**: Outline your article structure first
2. **Know Your Audience**: Write for the specified difficulty level
3. **Use Examples**: Include practical, real-world examples
4. **Link Strategically**: Connect to related articles
5. **Update Regularly**: Keep content current and accurate

### For System Administrators

1. **Monitor Performance**: Watch for slow loading times
2. **Backup Content**: Regularly backup the knowledge-base directory
3. **Review Analytics**: Track which articles are most popular
4. **Manage Categories**: Don't let categories proliferate unnecessarily
5. **Quality Control**: Implement content review processes

### For Teams

1. **Style Guide**: Maintain consistent writing style across articles
2. **Responsibility Matrix**: Assign article ownership and maintenance
3. **Review Schedule**: Regular content audits for accuracy
4. **Feedback Loop**: Gather user feedback on article usefulness
5. **Continuous Improvement**: Iterate based on user needs

## Getting Help

If you encounter issues while contributing to the knowledge base:

1. **Check the Logs**: Server logs contain detailed error messages
2. **Validate YAML**: Use online YAML validators for frontmatter
3. **Test Markdown**: Preview content with a Markdown editor
4. **Ask for Review**: Have colleagues check your content
5. **Contact Support**: Reach out to the development team for technical issues

Remember, good documentation is an investment in your team's productivity and user experience. Take time to create clear, helpful content that will serve users well over time.