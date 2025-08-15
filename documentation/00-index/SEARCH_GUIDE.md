# CVD Documentation Search Guide

## Overview

The CVD Documentation Search System provides comprehensive search functionality across the entire documentation corpus. This guide covers search syntax, operators, filters, and advanced features to help you find exactly what you're looking for.

**Last Updated**: 2025-08-12  
**Search Engine Version**: 1.0  
**Total Indexed Documents**: 119  
**Total Search Terms**: 4,511

## Quick Start

### Basic Search
```bash
# Simple text search
python documentation/00-index/scripts/search.py --search "planogram"

# Multiple terms (AND operation by default)
python documentation/00-index/scripts/search.py --search "device management API"
```

### Command Line Interface
```bash
# Build or rebuild the search index
python documentation/00-index/scripts/search.py --build

# Search with filters
python documentation/00-index/scripts/search.py --search "authentication" --categories "Architecture" "Implementation"

# Get search suggestions
python documentation/00-index/scripts/search.py --suggestions "plano"

# Show index statistics
python documentation/00-index/scripts/search.py --stats
```

## Search Syntax and Operators

### Basic Text Search
- **Simple terms**: `planogram`, `device`, `authentication`
- **Multiple terms**: `service order management` (searches for documents containing all terms)
- **Case insensitive**: `API` and `api` return the same results

### Phrase Matching
Use the `--phrase` flag for exact phrase searches:
```bash
# Find exact phrase
python search.py --search "service order workflow" --phrase

# Versus word search (default)
python search.py --search "service order workflow"
```

### Fuzzy Search (Default)
The search engine automatically includes fuzzy matching for typos and variations:
- `plonogram` → matches `planogram`
- `authetication` → matches `authentication`
- `databse` → matches `database`

Disable fuzzy search:
```bash
python search.py --search "planogram" --no-fuzzy
```

### Boolean Operators (Simplified)
When using `--boolean` mode:
- **AND** (default): `device management` (both terms required)
- **OR**: Use separate searches or multiple categories/tags
- **Exclude**: Prefix with `-` (basic implementation)

```bash
# Boolean mode example
python search.py --search "API endpoint" --boolean
```

## Filter Options

### Category Filtering
Filter results by documentation categories:

```bash
# Single category
python search.py --search "authentication" --categories "Architecture"

# Multiple categories
python search.py --search "API" --categories "Development" "Implementation" "Reference"
```

**Available Categories**:
- `Navigation` (00-index)
- `Project Core` (01-project-core)  
- `Requirements` (02-requirements)
- `Architecture` (03-architecture)
- `Implementation` (04-implementation)
- `Development` (05-development)
- `Design` (06-design)
- `CVD Framework` (07-cvd-framework)
- `Project Management` (08-project-management)
- `Reference` (09-reference)

### Tag-Based Filtering
Filter by content tags automatically extracted from documents:

```bash
# Single tag
python search.py --search "database" --tags "sqlite"

# Multiple tags
python search.py --search "frontend" --tags "javascript" "html" "css"
```

**Common Tags**:
- Technical: `api`, `database`, `sqlite`, `flask`, `javascript`, `html`, `css`, `python`
- Functional: `planogram`, `device`, `service-order`, `route`, `analytics`, `authentication`
- Framework: `pwa`, `cabinet`, `vending`, `dex`

### Result Limits
Control the number of results returned:
```bash
# Limit to 10 results
python search.py --search "API" --max-results 10

# Get more comprehensive results
python search.py --search "planogram" --max-results 50
```

## Advanced Query Examples

### Finding Specific Features
```bash
# Planogram-related documentation
python search.py --search "planogram" --categories "CVD Framework" "Requirements"

# Authentication implementation
python search.py --search "authentication" --tags "security" "api"

# Database design
python search.py --search "database" --categories "Architecture" "Reference"
```

### Development-Focused Searches
```bash
# API documentation
python search.py --search "API endpoint" --categories "Development" --tags "api"

# Frontend components
python search.py --search "component" --categories "Implementation" "Design" --tags "frontend"

# Testing guidance
python search.py --search "testing" --categories "Development" --max-results 20
```

### Architecture and Design Searches
```bash
# Architecture decisions
python search.py --search "ADR" --categories "Architecture"

# Design patterns
python search.py --search "pattern" --categories "Architecture" "Design"

# System overview
python search.py --search "system architecture" --phrase --categories "Architecture"
```

### Business Domain Searches
```bash
# Service order management
python search.py --search "service order" --categories "CVD Framework" "Requirements"

# Device management
python search.py --search "device management" --tags "device" "vending"

# Analytics and reporting
python search.py --search "analytics" --categories "CVD Framework" --tags "reporting"
```

## Search Tips and Best Practices

### Effective Search Strategies

1. **Start Broad, Then Narrow**:
   ```bash
   # Step 1: Broad search
   python search.py --search "authentication"
   
   # Step 2: Narrow down
   python search.py --search "authentication" --categories "Implementation"
   
   # Step 3: Specific search
   python search.py --search "authentication API" --tags "security"
   ```

2. **Use Domain Terminology**:
   - CVD-specific terms: `planogram`, `DEX`, `service order`, `route optimization`
   - Technical terms: `Flask`, `SQLite`, `PWA`, `iframe`
   - Business terms: `vending machine`, `cabinet`, `product placement`

3. **Leverage Synonyms**:
   The search engine includes CVD-specific synonyms:
   - `device` → `machine`, `vending machine`, `cooler`, `equipment`
   - `planogram` → `product placement`, `slot assignment`, `layout`
   - `service order` → `work order`, `maintenance`, `task`

4. **Combine Filters Effectively**:
   ```bash
   # Find implementation guides for specific features
   python search.py --search "planogram" --categories "Implementation" --tags "frontend"
   ```

### Common Search Patterns

#### Finding Getting Started Information
```bash
# Quick start guides
python search.py --search "quick start setup" --categories "Project Core"

# Installation instructions  
python search.py --search "installation setup" --tags "setup"
```

#### Troubleshooting Issues
```bash
# Error handling
python search.py --search "error handling" --categories "Development" "Implementation"

# Common problems
python search.py --search "troubleshooting" --max-results 15
```

#### API Reference Lookup
```bash
# Specific endpoints
python search.py --search "auth endpoint" --categories "Development"

# API patterns
python search.py --search "REST API" --tags "api" --categories "Architecture"
```

#### Configuration and Setup
```bash
# Configuration files
python search.py --search "configuration" --tags "setup"

# Environment setup
python search.py --search "environment" --categories "Development"
```

## Search Result Interpretation

### Understanding Scores
Search results are ranked by relevance score based on:
- **Title matches** (weight: 3.0) - Highest priority
- **Heading matches** (weight: 2.5) - High priority  
- **Filename matches** (weight: 2.0) - Medium-high priority
- **Content matches** (weight: 1.0) - Base priority
- **Code block matches** (weight: 1.5) - Medium priority
- **Phrase matches** - Bonus scoring
- **Document length** - Focused content gets higher scores

### Result Components
Each search result includes:
- **Title**: Document title or derived from filename
- **Path**: Relative path within documentation structure
- **Category**: Primary documentation category
- **Score**: Relevance score (higher = more relevant)
- **Tags**: Automatically extracted content tags
- **Snippets**: Contextual excerpts with search terms highlighted

### Using Snippets
Snippets show search terms in context:
```
Snippet: The **planogram** management system provides drag-and-drop interface for **product** placement...
```
- `**term**` indicates matched search terms
- `...` indicates truncated content
- Multiple snippets may be shown for comprehensive matches

## Troubleshooting Search Issues

### No Results Found

**Possible Causes**:
1. **Typo in search term** - Use fuzzy search (enabled by default)
2. **Too restrictive filters** - Remove category/tag filters
3. **Term not indexed** - Try synonyms or broader terms
4. **Index needs rebuilding** - Run `--build` command

**Solutions**:
```bash
# Check for typos with suggestions
python search.py --suggestions "plano"

# Remove filters
python search.py --search "planogram"

# Try synonyms
python search.py --search "product placement"

# Rebuild index
python search.py --build
```

### Too Many Results

**Solutions**:
1. **Add category filters**:
   ```bash
   python search.py --search "API" --categories "Development"
   ```

2. **Add tag filters**:
   ```bash
   python search.py --search "component" --tags "frontend"
   ```

3. **Use phrase matching**:
   ```bash
   python search.py --search "service order workflow" --phrase
   ```

4. **Limit results**:
   ```bash
   python search.py --search "documentation" --max-results 10
   ```

### Poor Result Quality

**Improvements**:
1. **Use more specific terms**:
   ```bash
   # Instead of: "data"
   python search.py --search "database schema"
   ```

2. **Combine multiple filters**:
   ```bash
   python search.py --search "authentication" --categories "Implementation" --tags "security"
   ```

3. **Try phrase matching for exact concepts**:
   ```bash
   python search.py --search "planogram optimization" --phrase
   ```

### Index Issues

**Rebuilding the Index**:
```bash
# Full rebuild (recommended after documentation changes)
python search.py --build

# Check index health
python search.py --stats
```

**Index Statistics to Monitor**:
- Total documents should match expected documentation files
- Total terms should be reasonable (3,000-5,000 for full docs)
- Index size should be manageable (< 10MB)

## Integration Examples

### From Python Scripts
```python
from documentation.scripts.search import DocumentationSearchEngine, SearchQuery

# Initialize engine
engine = DocumentationSearchEngine()

# Create search query
query = SearchQuery(
    query="planogram optimization",
    categories=["CVD Framework"],
    fuzzy=True,
    max_results=10
)

# Perform search
results = engine.search(query)

# Process results
for result in results:
    print(f"Title: {result.title}")
    print(f"Score: {result.score}")
    print(f"Snippets: {result.snippets}")
```

### From Shell Scripts
```bash
#!/bin/bash
# Search script example

SEARCH_SCRIPT="documentation/00-index/scripts/search.py"

# Search for authentication docs
echo "=== Authentication Documentation ==="
python $SEARCH_SCRIPT --search "authentication" --categories "Implementation" --max-results 5

# Search for API endpoints  
echo "=== API Endpoints ==="
python $SEARCH_SCRIPT --search "API endpoint" --tags "api" --max-results 10
```

## Performance Considerations

### Index Size and Performance
- **Total indexed documents**: 119
- **Index file size**: ~5MB  
- **Search response time**: < 100ms for typical queries
- **Memory usage**: ~10MB for loaded index

### Optimization Tips
1. **Rebuild index periodically** to maintain performance
2. **Use specific terms** to reduce candidate document set
3. **Apply filters early** to narrow search scope
4. **Limit results** for faster response times

### Scaling Considerations
The current implementation handles the CVD documentation corpus efficiently. For significantly larger document sets (>1,000 files), consider:
- Index partitioning by category
- Caching frequently accessed results  
- Background index updates
- Search result pagination

## Maintenance and Updates

### Regular Maintenance
```bash
# Weekly: Rebuild index to include new documentation
python search.py --build

# Monthly: Check index statistics
python search.py --stats

# As needed: Clear and rebuild if issues arise
rm documentation/00-index/SEARCH_INDEX.json
python search.py --build
```

### Adding New Content
When adding new documentation:
1. Add files following documentation standards
2. Rebuild search index: `python search.py --build`
3. Test search functionality with new content
4. Update this guide if new search patterns emerge

### Search Guide Updates
This guide should be updated when:
- New search features are added
- Documentation structure changes significantly  
- New categories or tags are introduced
- User feedback identifies missing guidance

---

## Quick Reference Commands

```bash
# Essential Commands
python search.py --build                    # Build/rebuild index
python search.py --search "query"          # Basic search
python search.py --stats                   # Show statistics
python search.py --suggestions "partial"   # Get suggestions

# Filtered Searches
python search.py --search "query" --categories "Category1" "Category2"
python search.py --search "query" --tags "tag1" "tag2"
python search.py --search "query" --max-results 20

# Advanced Options
python search.py --search "exact phrase" --phrase
python search.py --search "query" --boolean --no-fuzzy
```

## Getting Help

- **Command help**: `python search.py --help`
- **Search issues**: Check troubleshooting section above
- **Feature requests**: Add to documentation backlog
- **Bug reports**: Include search query and expected vs actual results

---

*This search guide is maintained alongside the CVD documentation system. For the most current version, always refer to this file in the documentation repository.*