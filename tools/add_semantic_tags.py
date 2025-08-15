#!/usr/bin/env python3
"""
Add semantic tags and metadata to documentation files for AI optimization.
"""

import os
import re
from pathlib import Path
from datetime import datetime

# Base documentation directory
DOCS_DIR = Path("/home/jbrice/Projects/365/documentation")

# Tag mapping based on directory and content patterns
TAG_MAPPINGS = {
    "01-project-core": ["#project-overview", "#getting-started", "#core-concepts"],
    "02-requirements": ["#requirements", "#user-stories", "#specifications"],
    "03-architecture": ["#architecture", "#system-design", "#technical"],
    "04-implementation": ["#implementation", "#features", "#code"],
    "05-development": ["#development", "#coding", "#workflows"],
    "06-design": ["#ui-design", "#user-experience", "#interface"],
    "07-cvd-framework": ["#cvd-specific", "#vending", "#domain"],
    "08-project-management": ["#project-management", "#planning", "#tracking"],
    "09-reference": ["#reference", "#api", "#documentation"]
}

# Content-based tag patterns
CONTENT_TAGS = {
    r"device|vending machine|cooler": ["#device-management", "#vending-machine"],
    r"planogram|product placement|slot": ["#planogram", "#product-placement"],
    r"service order|pick list": ["#service-orders", "#operations"],
    r"DEX|EVA DTS|grid pattern": ["#dex-parser", "#data-exchange"],
    r"authentication|login|password": ["#authentication", "#security"],
    r"API|endpoint|REST": ["#api", "#integration"],
    r"database|SQLite|schema": ["#database", "#data-layer"],
    r"PWA|mobile|driver app": ["#pwa", "#mobile", "#driver-app"],
    r"AI|optimization|Claude": ["#ai", "#optimization", "#machine-learning"],
    r"analytics|reporting|metrics": ["#analytics", "#reporting", "#metrics"],
    r"route|scheduling|delivery": ["#route-management", "#logistics"],
    r"error|troubleshooting|debug": ["#troubleshooting", "#debugging"],
    r"test|testing|quality": ["#testing", "#quality-assurance"],
    r"deploy|deployment|production": ["#deployment", "#devops"],
    r"performance|optimization|speed": ["#performance", "#optimization"]
}

def extract_file_id(filepath):
    """Generate a unique ID from the file path."""
    relative_path = filepath.relative_to(DOCS_DIR)
    # Convert path to ID format: path/to/file.md -> PATH_TO_FILE
    id_str = str(relative_path.with_suffix('')).replace('/', '_').replace('-', '_').upper()
    return id_str

def extract_title(content):
    """Extract the main title from markdown content."""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return match.group(1) if match else "Untitled"

def determine_doc_type(filepath):
    """Determine document type based on path and content."""
    path_str = str(filepath)
    if "requirements" in path_str:
        return "Requirements"
    elif "api" in path_str or "endpoint" in path_str:
        return "API Documentation"
    elif "guide" in path_str or "tutorial" in path_str:
        return "User Guide"
    elif "architecture" in path_str:
        return "Architecture"
    elif "implementation" in path_str or "features" in path_str:
        return "Implementation"
    elif "troubleshooting" in path_str:
        return "Troubleshooting"
    elif "reference" in path_str:
        return "Reference"
    else:
        return "Documentation"

def extract_intent(content, filepath):
    """Extract the intent/purpose of the document."""
    title = extract_title(content)
    doc_type = determine_doc_type(filepath)
    
    # Look for executive summary or overview
    summary_match = re.search(r'(?:Executive Summary|Overview|Purpose)[:\n]+(.+?)(?:\n\n|\n#)', 
                              content, re.DOTALL | re.IGNORECASE)
    if summary_match:
        summary = summary_match.group(1).strip()
        # Get first sentence
        first_sentence = re.split(r'[.!?]', summary)[0].strip()
        if len(first_sentence) < 200:
            return first_sentence
    
    # Default based on type
    return f"{doc_type} for {title}"

def determine_audience(filepath, content):
    """Determine target audience based on content and path."""
    audiences = []
    
    path_str = str(filepath).lower()
    content_lower = content.lower()
    
    if "developer" in content_lower or "api" in path_str or "implementation" in path_str:
        audiences.append("developers")
    if "admin" in content_lower or "deployment" in path_str:
        audiences.append("system administrators")
    if "manager" in content_lower or "business" in content_lower:
        audiences.append("managers")
    if "user" in content_lower or "guide" in path_str:
        audiences.append("end users")
    if "architect" in content_lower or "architecture" in path_str:
        audiences.append("architects")
    
    return audiences if audiences else ["developers", "technical users"]

def collect_tags(filepath, content):
    """Collect all relevant tags for the document."""
    tags = set()
    
    # Add directory-based tags
    for dir_pattern, dir_tags in TAG_MAPPINGS.items():
        if dir_pattern in str(filepath):
            tags.update(dir_tags)
    
    # Add content-based tags
    for pattern, content_tags in CONTENT_TAGS.items():
        if re.search(pattern, content, re.IGNORECASE):
            tags.update(content_tags)
    
    # Add file-specific tags
    filename = filepath.stem.lower()
    if "readme" in filename:
        tags.add("#overview")
    if "quick" in filename and "start" in filename:
        tags.add("#quick-start")
    if "install" in filename:
        tags.add("#installation")
    
    return sorted(list(tags))

def find_related_docs(filepath, content):
    """Find related documentation files."""
    related = []
    filename = filepath.stem
    
    # Look for explicit references in content
    md_links = re.findall(r'\[.*?\]\(([^)]+\.md)\)', content)
    for link in md_links:
        if link and not link.startswith('http'):
            related.append(Path(link).stem + '.md')
    
    # Add common related patterns
    if "requirements" in filename:
        impl_name = filename.replace("-requirements", "-implementation")
        api_name = filename.replace("-requirements", "-api")
        related.extend([impl_name + ".md", api_name + ".md"])
    elif "implementation" in filename:
        req_name = filename.replace("-implementation", "-requirements")
        api_name = filename.replace("-implementation", "-api")
        related.extend([req_name + ".md", api_name + ".md"])
    
    # Remove duplicates and self-references
    related = [r for r in list(set(related)) if r != filepath.name]
    
    return related[:5]  # Limit to 5 related docs

def extract_search_keywords(content, title):
    """Extract search keywords from content."""
    keywords = set()
    
    # Add words from title
    title_words = re.findall(r'\b[a-z]+\b', title.lower())
    keywords.update(title_words)
    
    # Find emphasized terms (bold, italic, code)
    bold_terms = re.findall(r'\*\*([^*]+)\*\*', content)
    italic_terms = re.findall(r'\*([^*]+)\*', content)
    code_terms = re.findall(r'`([^`]+)`', content)
    
    for term in bold_terms + italic_terms + code_terms:
        if len(term) < 30:  # Avoid long code snippets
            keywords.update(term.lower().split())
    
    # CVD-specific terms
    cvd_terms = ["planogram", "dex", "cabinet", "vending", "cooler", "device", 
                 "service order", "pick list", "route", "driver", "pwa"]
    for term in cvd_terms:
        if term in content.lower():
            keywords.add(term)
    
    # Filter out common words
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                  "of", "with", "by", "from", "as", "is", "was", "are", "were"}
    keywords = [k for k in keywords if k not in stop_words and len(k) > 2]
    
    return ", ".join(sorted(list(set(keywords)))[:15])  # Limit to 15 keywords

def create_metadata_section(filepath, content):
    """Create a complete metadata section for the document."""
    doc_id = extract_file_id(filepath)
    title = extract_title(content)
    doc_type = determine_doc_type(filepath)
    tags = collect_tags(filepath, content)
    intent = extract_intent(content, filepath)
    audience = determine_audience(filepath, content)
    related = find_related_docs(filepath, content)
    keywords = extract_search_keywords(content, title)
    
    # Determine navigation info
    parent_dir = filepath.parent.relative_to(DOCS_DIR)
    category = parent_dir.name.replace('-', ' ').title() if parent_dir.name else "Root"
    
    metadata = f"""## Metadata
- **ID**: {doc_id}
- **Type**: {doc_type}
- **Version**: 1.0.0
- **Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
- **Tags**: {' '.join(tags) if tags else '#documentation'}
- **Intent**: {intent}
- **Audience**: {', '.join(audience)}"""
    
    if related:
        metadata += f"\n- **Related**: {', '.join(related)}"
    
    metadata += f"""
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/{parent_dir}/
- **Category**: {category}
- **Search Keywords**: {keywords}
"""
    
    return metadata

def has_metadata_section(content):
    """Check if the document already has a metadata section."""
    return "## Metadata" in content

def update_document(filepath):
    """Update a single document with metadata."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has metadata
        if has_metadata_section(content):
            return False
        
        # Skip certain files
        if filepath.name in ['README.md', 'DOCUMENTATION_STANDARDS.md', 'AI_QUERY_PATTERNS.md', 
                             'CONTEXT_BRIDGES.md', 'MASTER_INDEX.md']:
            return False
        
        # Create metadata section
        metadata = create_metadata_section(filepath, content)
        
        # Find where to insert metadata (after first heading)
        lines = content.split('\n')
        insert_index = 0
        
        for i, line in enumerate(lines):
            if line.startswith('# '):
                insert_index = i + 1
                # Skip any blank lines after title
                while insert_index < len(lines) and not lines[insert_index].strip():
                    insert_index += 1
                break
        
        # Insert metadata
        if insert_index > 0:
            lines.insert(insert_index, '')
            lines.insert(insert_index + 1, metadata)
            
            # Write back
            updated_content = '\n'.join(lines)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            return True
    
    except Exception as e:
        print(f"Error updating {filepath}: {e}")
        return False
    
    return False

def process_all_documents():
    """Process all documentation files."""
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    # Find all markdown files
    md_files = list(DOCS_DIR.rglob("*.md"))
    
    print(f"Found {len(md_files)} markdown files")
    print("Processing...")
    
    for filepath in md_files:
        # Skip index directory files (they're special)
        if "00-index" in str(filepath):
            skipped_count += 1
            continue
        
        result = update_document(filepath)
        if result:
            updated_count += 1
            print(f"✓ Updated: {filepath.relative_to(DOCS_DIR)}")
        elif result is False:
            skipped_count += 1
        else:
            error_count += 1
    
    print(f"\nSummary:")
    print(f"  Updated: {updated_count} files")
    print(f"  Skipped: {skipped_count} files (already have metadata or excluded)")
    print(f"  Errors: {error_count} files")

if __name__ == "__main__":
    process_all_documents()