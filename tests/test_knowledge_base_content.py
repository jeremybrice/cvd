"""
Knowledge Base Content Validation Test Suite
Tests markdown processing, article structure validation, and content quality
Validates content against planning document specifications
"""

import pytest
import yaml
import markdown
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class TestKnowledgeBaseContent:
    """Content validation and markdown processing tests"""
    
    @pytest.fixture
    def knowledge_base_path(self):
        """Get path to knowledge base content directory"""
        return Path("/home/jbrice/Projects/365/knowledge-base")
    
    @pytest.fixture
    def sample_articles(self, knowledge_base_path):
        """Get list of all markdown articles"""
        if knowledge_base_path.exists():
            return list(knowledge_base_path.rglob("*.md"))
        else:
            return []
    
    def test_article_frontmatter_validation(self, sample_articles):
        """Test: All articles have valid YAML frontmatter with required fields"""
        required_fields = ['title', 'author', 'category', 'difficulty', 'description']
        optional_fields = ['tags', 'last_updated']
        valid_difficulties = ['Beginner', 'Intermediate', 'Advanced']
        valid_categories = [
            'Getting Started',
            'Feature Tutorials', 
            'Troubleshooting',
            'System Administration',
            'Best Practices'
        ]
        
        validation_results = []
        
        for article_path in sample_articles:
            result = {
                'file': str(article_path),
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            try:
                content = article_path.read_text(encoding='utf-8')
                
                # Check for frontmatter
                if not content.startswith('---'):
                    result['valid'] = False
                    result['errors'].append("Missing YAML frontmatter delimiter")
                    validation_results.append(result)
                    continue
                
                # Extract and parse frontmatter
                parts = content.split('---', 2)
                if len(parts) < 3:
                    result['valid'] = False
                    result['errors'].append("Invalid frontmatter structure")
                    validation_results.append(result)
                    continue
                
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    if not isinstance(frontmatter, dict):
                        result['valid'] = False
                        result['errors'].append("Frontmatter is not a valid YAML object")
                        continue
                        
                except yaml.YAMLError as e:
                    result['valid'] = False
                    result['errors'].append(f"YAML parsing error: {e}")
                    validation_results.append(result)
                    continue
                
                # Validate required fields
                for field in required_fields:
                    if field not in frontmatter:
                        result['valid'] = False
                        result['errors'].append(f"Missing required field: {field}")
                    elif not frontmatter[field] or not str(frontmatter[field]).strip():
                        result['valid'] = False
                        result['errors'].append(f"Empty required field: {field}")
                
                # Validate field values
                if 'difficulty' in frontmatter:
                    if frontmatter['difficulty'] not in valid_difficulties:
                        result['valid'] = False
                        result['errors'].append(f"Invalid difficulty: {frontmatter['difficulty']}. Must be one of: {valid_difficulties}")
                
                if 'category' in frontmatter:
                    if frontmatter['category'] not in valid_categories:
                        result['warnings'].append(f"Category '{frontmatter['category']}' not in predefined list: {valid_categories}")
                
                # Validate optional fields format
                if 'tags' in frontmatter:
                    if not isinstance(frontmatter['tags'], list):
                        result['valid'] = False
                        result['errors'].append("Tags must be a list")
                    elif not all(isinstance(tag, str) for tag in frontmatter['tags']):
                        result['valid'] = False
                        result['errors'].append("All tags must be strings")
                
                if 'last_updated' in frontmatter:
                    try:
                        # Try to parse as ISO datetime
                        if isinstance(frontmatter['last_updated'], str):
                            datetime.fromisoformat(frontmatter['last_updated'].replace('Z', '+00:00'))
                    except ValueError:
                        result['warnings'].append("last_updated should be in ISO datetime format")
                
                # Validate content exists after frontmatter
                markdown_content = parts[2].strip()
                if not markdown_content:
                    result['valid'] = False
                    result['errors'].append("Article has no content after frontmatter")
                elif len(markdown_content) < 100:
                    result['warnings'].append("Article content is very short (< 100 characters)")
                
            except Exception as e:
                result['valid'] = False
                result['errors'].append(f"Error reading file: {e}")
            
            validation_results.append(result)
        
        # Report results
        valid_articles = [r for r in validation_results if r['valid']]
        invalid_articles = [r for r in validation_results if not r['valid']]
        articles_with_warnings = [r for r in validation_results if r['warnings']]
        
        print(f"\nArticle Frontmatter Validation Results:")
        print(f"  Total articles: {len(validation_results)}")
        print(f"  Valid articles: {len(valid_articles)}")
        print(f"  Invalid articles: {len(invalid_articles)}")
        print(f"  Articles with warnings: {len(articles_with_warnings)}")
        
        if invalid_articles:
            print(f"\nInvalid articles:")
            for article in invalid_articles:
                print(f"  - {Path(article['file']).name}:")
                for error in article['errors']:
                    print(f"    • {error}")
        
        if articles_with_warnings:
            print(f"\nWarnings:")
            for article in articles_with_warnings:
                print(f"  - {Path(article['file']).name}:")
                for warning in article['warnings']:
                    print(f"    • {warning}")
        
        # Assert all articles are valid
        assert len(invalid_articles) == 0, f"{len(invalid_articles)} articles have invalid frontmatter"
        
        return validation_results
    
    def test_markdown_content_structure(self, sample_articles):
        """Test: Markdown content follows proper structure and formatting"""
        structure_results = []
        
        for article_path in sample_articles:
            result = {
                'file': str(article_path),
                'valid': True,
                'errors': [],
                'warnings': [],
                'structure_score': 0
            }
            
            try:
                content = article_path.read_text(encoding='utf-8')
                
                # Extract markdown content (skip frontmatter)
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        markdown_content = parts[2].strip()
                    else:
                        markdown_content = content
                else:
                    markdown_content = content
                
                # Test heading structure
                headings = re.findall(r'^(#{1,6})\s+(.+)$', markdown_content, re.MULTILINE)
                
                if not headings:
                    result['warnings'].append("No headings found")
                else:
                    # Check for H1 (main title)
                    h1_headings = [h for h in headings if len(h[0]) == 1]
                    if not h1_headings:
                        result['warnings'].append("No H1 heading found")
                    elif len(h1_headings) > 1:
                        result['warnings'].append("Multiple H1 headings found")
                    else:
                        result['structure_score'] += 2
                    
                    # Check heading hierarchy
                    heading_levels = [len(h[0]) for h in headings]
                    for i in range(1, len(heading_levels)):
                        if heading_levels[i] - heading_levels[i-1] > 1:
                            result['warnings'].append("Heading hierarchy skips levels")
                            break
                    else:
                        result['structure_score'] += 1
                
                # Test paragraph structure
                paragraphs = markdown_content.split('\n\n')
                non_empty_paragraphs = [p.strip() for p in paragraphs if p.strip()]
                
                if len(non_empty_paragraphs) < 3:
                    result['warnings'].append("Article has fewer than 3 paragraphs")
                else:
                    result['structure_score'] += 1
                
                # Test for code blocks (should be properly formatted)
                code_blocks = re.findall(r'```[\s\S]*?```', markdown_content)
                inline_code = re.findall(r'`[^`]+`', markdown_content)
                
                if code_blocks or inline_code:
                    result['structure_score'] += 1
                
                # Test for lists
                unordered_lists = re.findall(r'^\s*[-*+]\s+.+$', markdown_content, re.MULTILINE)
                ordered_lists = re.findall(r'^\s*\d+\.\s+.+$', markdown_content, re.MULTILINE)
                
                if unordered_lists or ordered_lists:
                    result['structure_score'] += 1
                
                # Test for links
                links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', markdown_content)
                if links:
                    result['structure_score'] += 1
                    
                    # Validate internal links
                    for link_text, link_url in links:
                        if not link_url.startswith(('http', 'https', 'mailto')):
                            # Internal link - should be valid
                            if link_url.startswith('#'):
                                # Anchor link - check if anchor exists
                                anchor = link_url[1:]
                                # Simplified check - would need more sophisticated validation
                                pass
                            else:
                                result['warnings'].append(f"Internal link may be broken: {link_url}")
                
                # Test content length and readability
                word_count = len(markdown_content.split())
                if word_count < 100:
                    result['warnings'].append(f"Article is very short ({word_count} words)")
                elif word_count > 5000:
                    result['warnings'].append(f"Article is very long ({word_count} words)")
                else:
                    result['structure_score'] += 1
                
                # Check for common markdown issues
                if ']((' in markdown_content:
                    result['errors'].append("Double parentheses in link syntax")
                    result['valid'] = False
                
                if re.search(r'\[([^\]]+)\]\(\)', markdown_content):
                    result['errors'].append("Empty link URL")
                    result['valid'] = False
                
                # Score-based validation (max score is 7)
                if result['structure_score'] < 3:
                    result['warnings'].append(f"Low structure score ({result['structure_score']}/7)")
                
            except Exception as e:
                result['valid'] = False
                result['errors'].append(f"Error processing content: {e}")
            
            structure_results.append(result)
        
        # Report results
        valid_structure = [r for r in structure_results if r['valid']]
        invalid_structure = [r for r in structure_results if not r['valid']]
        avg_score = sum(r['structure_score'] for r in valid_structure) / len(valid_structure) if valid_structure else 0
        
        print(f"\nMarkdown Structure Validation Results:")
        print(f"  Total articles: {len(structure_results)}")
        print(f"  Valid structure: {len(valid_structure)}")
        print(f"  Invalid structure: {len(invalid_structure)}")
        print(f"  Average structure score: {avg_score:.1f}/7")
        
        if invalid_structure:
            print(f"\nStructure errors:")
            for article in invalid_structure:
                print(f"  - {Path(article['file']).name}:")
                for error in article['errors']:
                    print(f"    • {error}")
        
        # Assert structure is valid
        assert len(invalid_structure) == 0, f"{len(invalid_structure)} articles have invalid structure"
        assert avg_score >= 3.0, f"Average structure score {avg_score:.1f} below minimum 3.0"
        
        return structure_results
    
    def test_markdown_rendering_quality(self, sample_articles):
        """Test: Markdown renders correctly to HTML without errors"""
        rendering_results = []
        
        # Configure markdown with extensions
        md = markdown.Markdown(extensions=[
            'codehilite',
            'fenced_code',
            'tables',
            'toc'
        ])
        
        for article_path in sample_articles[:10]:  # Test first 10 articles for performance
            result = {
                'file': str(article_path),
                'valid': True,
                'errors': [],
                'warnings': [],
                'html_length': 0,
                'rendering_issues': []
            }
            
            try:
                content = article_path.read_text(encoding='utf-8')
                
                # Extract markdown content
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        markdown_content = parts[2].strip()
                    else:
                        markdown_content = content
                else:
                    markdown_content = content
                
                # Render to HTML
                try:
                    html_output = md.convert(markdown_content)
                    result['html_length'] = len(html_output)
                    
                    # Reset for next conversion
                    md.reset()
                    
                except Exception as e:
                    result['valid'] = False
                    result['errors'].append(f"Markdown rendering failed: {e}")
                    continue
                
                # Validate HTML output quality
                if len(html_output) < 100:
                    result['warnings'].append("Rendered HTML is very short")
                
                # Check for common rendering issues
                if '<p></p>' in html_output:
                    result['rendering_issues'].append("Empty paragraphs in output")
                
                if html_output.count('<h1>') > 1:
                    result['rendering_issues'].append("Multiple H1 elements in output")
                
                # Check for unclosed tags (basic validation)
                tag_pattern = r'<(\w+)[^>]*>'
                closing_tag_pattern = r'</(\w+)>'
                
                opening_tags = re.findall(tag_pattern, html_output)
                closing_tags = re.findall(closing_tag_pattern, html_output)
                
                # Filter out self-closing tags
                self_closing_tags = ['img', 'br', 'hr', 'input', 'meta', 'link']
                opening_tags = [tag for tag in opening_tags if tag not in self_closing_tags]
                
                if len(opening_tags) != len(closing_tags):
                    result['rendering_issues'].append("Possible unclosed HTML tags")
                
                # Check for code syntax highlighting
                if '```' in markdown_content:
                    if 'class="codehilite"' not in html_output and 'class="highlight"' not in html_output:
                        result['warnings'].append("Code blocks may not have syntax highlighting")
                
                # Check for table rendering
                if '|' in markdown_content and 'table' not in html_output.lower():
                    result['warnings'].append("Tables may not have rendered correctly")
                
            except Exception as e:
                result['valid'] = False
                result['errors'].append(f"Error during rendering test: {e}")
            
            rendering_results.append(result)
        
        # Report results
        valid_rendering = [r for r in rendering_results if r['valid']]
        invalid_rendering = [r for r in rendering_results if not r['valid']]
        avg_html_length = sum(r['html_length'] for r in valid_rendering) / len(valid_rendering) if valid_rendering else 0
        
        print(f"\nMarkdown Rendering Quality Results:")
        print(f"  Total articles tested: {len(rendering_results)}")
        print(f"  Valid rendering: {len(valid_rendering)}")
        print(f"  Invalid rendering: {len(invalid_rendering)}")
        print(f"  Average HTML length: {avg_html_length:.0f} characters")
        
        if invalid_rendering:
            print(f"\nRendering errors:")
            for article in invalid_rendering:
                print(f"  - {Path(article['file']).name}:")
                for error in article['errors']:
                    print(f"    • {error}")
        
        # Assert rendering quality
        assert len(invalid_rendering) == 0, f"{len(invalid_rendering)} articles failed to render properly"
        
        return rendering_results
    
    def test_content_accessibility(self, sample_articles):
        """Test: Content follows accessibility best practices"""
        accessibility_results = []
        
        for article_path in sample_articles:
            result = {
                'file': str(article_path),
                'valid': True,
                'errors': [],
                'warnings': [],
                'accessibility_score': 0
            }
            
            try:
                content = article_path.read_text(encoding='utf-8')
                
                # Extract markdown content
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        markdown_content = parts[2].strip()
                    else:
                        markdown_content = content
                else:
                    markdown_content = content
                
                # Test for descriptive link text
                links = re.findall(r'\[([^\]]+)\]\([^)]+\)', markdown_content)
                generic_link_texts = ['click here', 'here', 'read more', 'this', 'link']
                
                for link_text, link_url in [(m, '') for m in links]:
                    if link_text.lower().strip() in generic_link_texts:
                        result['warnings'].append(f"Generic link text: '{link_text}'")
                    else:
                        result['accessibility_score'] += 0.5
                
                # Test for alt text on images
                images = re.findall(r'!\[([^\]]*)\]\([^)]+\)', markdown_content)
                for alt_text in images:
                    if not alt_text.strip():
                        result['warnings'].append("Image without alt text")
                    elif len(alt_text.strip()) < 10:
                        result['warnings'].append(f"Short alt text: '{alt_text}'")
                    else:
                        result['accessibility_score'] += 1
                
                # Test heading structure for screen readers
                headings = re.findall(r'^(#{1,6})\s+(.+)$', markdown_content, re.MULTILINE)
                heading_levels = [len(h[0]) for h in headings]
                
                if heading_levels:
                    # Check for logical progression
                    proper_hierarchy = True
                    for i in range(1, len(heading_levels)):
                        if heading_levels[i] - heading_levels[i-1] > 1:
                            proper_hierarchy = False
                            break
                    
                    if proper_hierarchy:
                        result['accessibility_score'] += 2
                    else:
                        result['warnings'].append("Heading hierarchy not accessible")
                
                # Test for descriptive section headings
                for level, heading_text in headings:
                    if len(heading_text.strip()) < 3:
                        result['warnings'].append(f"Very short heading: '{heading_text}'")
                    elif heading_text.strip().lower() in ['introduction', 'conclusion', 'summary']:
                        result['warnings'].append(f"Generic heading: '{heading_text}'")
                    else:
                        result['accessibility_score'] += 0.2
                
                # Test for list structure
                list_items = re.findall(r'^\s*[-*+\d\.]\s+.+$', markdown_content, re.MULTILINE)
                if list_items:
                    result['accessibility_score'] += 1
                
                # Test for table headers
                tables = re.findall(r'\|.+\|\n\|[-\s|]+\|', markdown_content)
                for table in tables:
                    if table.count('|') >= 4:  # Has header row
                        result['accessibility_score'] += 1
                    else:
                        result['warnings'].append("Table may be missing headers")
                
                # Test content length for readability
                word_count = len(markdown_content.split())
                if 200 <= word_count <= 2000:  # Good length for accessibility
                    result['accessibility_score'] += 1
                elif word_count > 3000:
                    result['warnings'].append("Very long article may be hard to read")
                
                # Test for code accessibility
                code_blocks = re.findall(r'```(\w+)?\n(.*?)```', markdown_content, re.DOTALL)
                for lang, code in code_blocks:
                    if not lang:
                        result['warnings'].append("Code block without language specification")
                    else:
                        result['accessibility_score'] += 0.5
                
            except Exception as e:
                result['valid'] = False
                result['errors'].append(f"Error during accessibility test: {e}")
            
            accessibility_results.append(result)
        
        # Report results
        valid_accessibility = [r for r in accessibility_results if r['valid']]
        invalid_accessibility = [r for r in accessibility_results if not r['valid']]
        avg_score = sum(r['accessibility_score'] for r in valid_accessibility) / len(valid_accessibility) if valid_accessibility else 0
        
        print(f"\nContent Accessibility Results:")
        print(f"  Total articles: {len(accessibility_results)}")
        print(f"  Valid accessibility: {len(valid_accessibility)}")
        print(f"  Invalid accessibility: {len(invalid_accessibility)}")
        print(f"  Average accessibility score: {avg_score:.1f}")
        
        # Assert accessibility standards
        assert len(invalid_accessibility) == 0, f"{len(invalid_accessibility)} articles have accessibility errors"
        
        return accessibility_results
    
    def test_content_quality_metrics(self, sample_articles):
        """Test: Content meets quality standards for readability and completeness"""
        quality_results = []
        
        for article_path in sample_articles:
            result = {
                'file': str(article_path),
                'valid': True,
                'errors': [],
                'warnings': [],
                'metrics': {}
            }
            
            try:
                content = article_path.read_text(encoding='utf-8')
                
                # Parse frontmatter and content
                frontmatter = {}
                markdown_content = content
                
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        markdown_content = parts[2].strip()
                
                # Calculate metrics
                word_count = len(markdown_content.split())
                char_count = len(markdown_content)
                sentence_count = len(re.findall(r'[.!?]+', markdown_content))
                paragraph_count = len([p for p in markdown_content.split('\n\n') if p.strip()])
                
                result['metrics'] = {
                    'word_count': word_count,
                    'char_count': char_count,
                    'sentence_count': sentence_count,
                    'paragraph_count': paragraph_count,
                    'avg_words_per_sentence': word_count / max(sentence_count, 1),
                    'avg_words_per_paragraph': word_count / max(paragraph_count, 1)
                }
                
                # Reading time calculation (250 words per minute)
                calculated_reading_time = max(1, round(word_count / 250))
                result['metrics']['calculated_reading_time'] = calculated_reading_time
                
                # Validate against frontmatter if present
                if 'read_time_minutes' in frontmatter:
                    declared_reading_time = frontmatter['read_time_minutes']
                    if abs(calculated_reading_time - declared_reading_time) > 2:
                        result['warnings'].append(f"Reading time mismatch: declared {declared_reading_time}, calculated {calculated_reading_time}")
                
                # Quality checks
                if word_count < 200:
                    result['warnings'].append(f"Article is quite short ({word_count} words)")
                elif word_count > 5000:
                    result['warnings'].append(f"Article is very long ({word_count} words)")
                
                # Readability checks
                avg_words_per_sentence = result['metrics']['avg_words_per_sentence']
                if avg_words_per_sentence > 25:
                    result['warnings'].append(f"Sentences may be too long (avg {avg_words_per_sentence:.1f} words)")
                
                avg_words_per_paragraph = result['metrics']['avg_words_per_paragraph']
                if avg_words_per_paragraph > 150:
                    result['warnings'].append(f"Paragraphs may be too long (avg {avg_words_per_paragraph:.1f} words)")
                
                # Check for step-by-step content (good for tutorials)
                step_indicators = re.findall(r'\b(?:step|stage|phase)\s*\d+\b', markdown_content, re.IGNORECASE)
                numbered_lists = re.findall(r'^\s*\d+\.\s+', markdown_content, re.MULTILINE)
                
                if len(step_indicators) > 2 or len(numbered_lists) > 5:
                    result['metrics']['has_structured_steps'] = True
                else:
                    result['metrics']['has_structured_steps'] = False
                
                # Check for examples
                example_indicators = re.findall(r'\b(?:example|for instance|such as|like)\b', markdown_content, re.IGNORECASE)
                code_blocks = re.findall(r'```[\s\S]*?```', markdown_content)
                
                result['metrics']['has_examples'] = len(example_indicators) > 2 or len(code_blocks) > 0
                
                # Check for troubleshooting content
                troubleshooting_indicators = re.findall(r'\b(?:error|issue|problem|troubleshoot|fix|solution)\b', markdown_content, re.IGNORECASE)
                result['metrics']['has_troubleshooting'] = len(troubleshooting_indicators) > 3
                
            except Exception as e:
                result['valid'] = False
                result['errors'].append(f"Error during quality analysis: {e}")
            
            quality_results.append(result)
        
        # Aggregate metrics
        valid_results = [r for r in quality_results if r['valid']]
        
        if valid_results:
            avg_word_count = sum(r['metrics']['word_count'] for r in valid_results) / len(valid_results)
            avg_reading_time = sum(r['metrics']['calculated_reading_time'] for r in valid_results) / len(valid_results)
            structured_articles = sum(1 for r in valid_results if r['metrics'].get('has_structured_steps'))
            articles_with_examples = sum(1 for r in valid_results if r['metrics'].get('has_examples'))
            troubleshooting_articles = sum(1 for r in valid_results if r['metrics'].get('has_troubleshooting'))
            
            print(f"\nContent Quality Metrics:")
            print(f"  Total articles analyzed: {len(valid_results)}")
            print(f"  Average word count: {avg_word_count:.0f}")
            print(f"  Average reading time: {avg_reading_time:.1f} minutes")
            print(f"  Structured articles: {structured_articles}/{len(valid_results)} ({structured_articles/len(valid_results)*100:.1f}%)")
            print(f"  Articles with examples: {articles_with_examples}/{len(valid_results)} ({articles_with_examples/len(valid_results)*100:.1f}%)")
            print(f"  Troubleshooting articles: {troubleshooting_articles}/{len(valid_results)} ({troubleshooting_articles/len(valid_results)*100:.1f}%)")
            
            # Quality assertions
            assert avg_word_count >= 300, f"Average word count {avg_word_count:.0f} below minimum 300"
            assert structured_articles / len(valid_results) >= 0.3, "At least 30% of articles should have structured steps"
        
        return quality_results
    
    def test_cross_reference_validation(self, sample_articles):
        """Test: Internal links and cross-references are valid"""
        cross_ref_results = []
        
        # Build map of available articles
        article_map = {}
        for article_path in sample_articles:
            try:
                content = article_path.read_text(encoding='utf-8')
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        title = frontmatter.get('title', '')
                        article_id = article_path.stem
                        article_map[article_id] = {
                            'title': title,
                            'path': str(article_path),
                            'category': frontmatter.get('category', '')
                        }
            except:
                continue
        
        for article_path in sample_articles:
            result = {
                'file': str(article_path),
                'valid': True,
                'errors': [],
                'warnings': [],
                'internal_links': [],
                'broken_links': []
            }
            
            try:
                content = article_path.read_text(encoding='utf-8')
                
                # Extract markdown content
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        markdown_content = parts[2].strip()
                    else:
                        markdown_content = content
                else:
                    markdown_content = content
                
                # Find all links
                links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', markdown_content)
                
                for link_text, link_url in links:
                    if not link_url.startswith(('http', 'https', 'mailto')):
                        # Internal link
                        result['internal_links'].append({
                            'text': link_text,
                            'url': link_url
                        })
                        
                        # Validate internal link
                        if link_url.startswith('#'):
                            # Anchor link - check if heading exists
                            anchor = link_url[1:].lower().replace('-', ' ')
                            headings = re.findall(r'^#+\s+(.+)$', markdown_content, re.MULTILINE)
                            heading_anchors = [h.lower().strip() for h in headings]
                            
                            if anchor not in heading_anchors:
                                result['broken_links'].append({
                                    'text': link_text,
                                    'url': link_url,
                                    'reason': 'Anchor not found'
                                })
                        else:
                            # File reference
                            referenced_id = link_url.replace('.md', '').replace('.html', '')
                            if referenced_id not in article_map:
                                result['broken_links'].append({
                                    'text': link_text,
                                    'url': link_url,
                                    'reason': 'Referenced article not found'
                                })
                
                if result['broken_links']:
                    result['valid'] = False
                    for broken_link in result['broken_links']:
                        result['errors'].append(f"Broken link: '{broken_link['text']}' -> {broken_link['url']} ({broken_link['reason']})")
                
            except Exception as e:
                result['valid'] = False
                result['errors'].append(f"Error validating cross-references: {e}")
            
            cross_ref_results.append(result)
        
        # Report results
        valid_refs = [r for r in cross_ref_results if r['valid']]
        invalid_refs = [r for r in cross_ref_results if not r['valid']]
        total_internal_links = sum(len(r['internal_links']) for r in cross_ref_results)
        total_broken_links = sum(len(r['broken_links']) for r in cross_ref_results)
        
        print(f"\nCross-Reference Validation Results:")
        print(f"  Total articles: {len(cross_ref_results)}")
        print(f"  Valid references: {len(valid_refs)}")
        print(f"  Invalid references: {len(invalid_refs)}")
        print(f"  Total internal links: {total_internal_links}")
        print(f"  Total broken links: {total_broken_links}")
        
        if invalid_refs:
            print(f"\nBroken references:")
            for article in invalid_refs:
                print(f"  - {Path(article['file']).name}:")
                for error in article['errors']:
                    print(f"    • {error}")
        
        # Assert reference validity
        assert len(invalid_refs) == 0, f"{len(invalid_refs)} articles have broken internal references"
        
        return cross_ref_results


class TestKnowledgeBaseServiceIntegration:
    """Integration tests for KnowledgeBaseService with real content"""
    
    def test_service_with_real_content(self):
        """Test KnowledgeBaseService processes real content correctly"""
        try:
            from services.knowledge_base_service import KnowledgeBaseService
            
            kb_path = "/home/jbrice/Projects/365/knowledge-base"
            if not Path(kb_path).exists():
                pytest.skip("Knowledge base content directory not found")
            
            service = KnowledgeBaseService(content_path=kb_path)
            
            # Test article scanning
            articles = service.scan_articles()
            assert len(articles) > 0, "Should find at least one article"
            
            print(f"\nKnowledge Base Service Integration Test:")
            print(f"  Articles found: {len(articles)}")
            
            # Test article structure
            for article in articles[:5]:  # Test first 5 articles
                assert 'id' in article, "Article should have ID"
                assert 'title' in article, "Article should have title"
                assert 'category' in article, "Article should have category"
                assert 'content' in article, "Article should have content"
                assert article['word_count'] > 0, "Article should have word count"
                assert article['read_time_minutes'] > 0, "Article should have reading time"
                
                print(f"    {article['id']}: {article['word_count']} words, {article['read_time_minutes']} min")
            
            # Test categories
            categories = service.get_categories()
            assert len(categories) > 0, "Should have at least one category"
            
            print(f"  Categories found: {len(categories)}")
            for category in categories:
                assert 'name' in category, "Category should have name"
                assert 'article_count' in category, "Category should have article count"
                print(f"    {category['name']}: {category['article_count']} articles")
            
            # Test search functionality
            search_results = service.search_articles("getting started")
            print(f"  Search results for 'getting started': {len(search_results)}")
            
            # Test individual article retrieval
            if articles:
                first_article = service.get_article_by_id(articles[0]['id'])
                assert first_article is not None, "Should retrieve article by ID"
                assert 'navigation' in first_article, "Article should have navigation info"
                print(f"    Retrieved article: {first_article['title']}")
            
            # Test statistics
            stats = service.get_article_stats()
            assert 'total_articles' in stats, "Stats should include total articles"
            assert 'total_words' in stats, "Stats should include total words"
            assert stats['total_articles'] == len(articles), "Stats should match article count"
            
            print(f"  Total words in knowledge base: {stats['total_words']}")
            
        except ImportError:
            pytest.skip("KnowledgeBaseService not available for testing")


if __name__ == "__main__":
    # Run content validation tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--durations=10"
    ])