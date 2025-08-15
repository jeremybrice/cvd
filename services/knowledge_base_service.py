"""
Knowledge Base Service for CVD Vending Machine Management System
Handles markdown article processing, metadata extraction, and content management
"""

import os
import re
import yaml
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import hashlib
import logging

class KnowledgeBaseService:
    def __init__(self, content_path: str = "knowledge-base", db_path: str = "cvd.db"):
        """Initialize the knowledge base service"""
        self.content_path = Path(content_path)
        self.db_path = db_path
        self.cache = {}
        self.last_scan = None
        self.logger = logging.getLogger(__name__)
        
        # Ensure content directory exists
        self.content_path.mkdir(parents=True, exist_ok=True)
        
    def get_db_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def scan_articles(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Scan filesystem for markdown articles and cache metadata
        
        Args:
            force_refresh: Force refresh even if recently scanned
            
        Returns:
            List of article metadata dictionaries
        """
        # Check if we need to rescan (cache for 5 minutes)
        if (not force_refresh and self.last_scan and 
            (datetime.now() - self.last_scan).seconds < 300 and 
            'articles' in self.cache):
            return self.cache['articles']
            
        articles = []
        
        try:
            # Scan all markdown files recursively
            for md_file in self.content_path.rglob("*.md"):
                try:
                    article_data = self._parse_article(md_file)
                    if article_data:
                        articles.append(article_data)
                except Exception as e:
                    self.logger.error(f"Error processing {md_file}: {e}")
                    
            # Sort articles by category and title
            articles.sort(key=lambda x: (x['category'], x['title']))
            
            # Cache results
            self.cache['articles'] = articles
            self.cache['categories'] = self._build_categories(articles)
            self.last_scan = datetime.now()
            
            # Update database cache
            self._update_db_cache(articles)
            
        except Exception as e:
            self.logger.error(f"Error scanning articles: {e}")
            articles = []
            
        return articles
    
    def _parse_article(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse markdown file with YAML frontmatter
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            Article data dictionary or None if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Could not read file {file_path}: {e}")
            return None
            
        # Split frontmatter and content
        if not content.startswith('---'):
            self.logger.warning(f"Missing frontmatter in {file_path}")
            return None
            
        try:
            parts = content.split('---', 2)
            if len(parts) < 3:
                self.logger.error(f"Invalid frontmatter format in {file_path}")
                return None
                
            frontmatter_text = parts[1].strip()
            markdown_content = parts[2].strip()
            
            # Parse YAML frontmatter
            frontmatter = yaml.safe_load(frontmatter_text) or {}
            
        except yaml.YAMLError as e:
            self.logger.error(f"YAML parsing error in {file_path}: {e}")
            return None
            
        # Generate article ID from filename
        article_id = file_path.stem
        
        # Calculate reading time (250 words per minute average)
        word_count = len(markdown_content.split())
        read_time = max(1, round(word_count / 250))
        
        # Get file modification time
        file_stat = file_path.stat()
        file_modified = datetime.fromtimestamp(file_stat.st_mtime)
        
        # Use frontmatter last_updated or file modification time
        last_updated = frontmatter.get('last_updated')
        if isinstance(last_updated, str):
            try:
                last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            except ValueError:
                last_updated = file_modified
        else:
            last_updated = file_modified
            
        # Extract content preview (first 200 characters of content)
        content_preview = self._extract_preview(markdown_content)
        
        # Create search content (title + content without markdown)
        search_content = f"{frontmatter.get('title', '')} {self._strip_markdown(markdown_content)}"
        
        return {
            'id': article_id,
            'title': frontmatter.get('title', 'Untitled'),
            'author': frontmatter.get('author', 'Unknown'),
            'category': frontmatter.get('category', 'Uncategorized'),
            'tags': frontmatter.get('tags', []),
            'difficulty': frontmatter.get('difficulty', 'Beginner'),
            'description': frontmatter.get('description', ''),
            'last_updated': last_updated,
            'content': markdown_content,
            'word_count': word_count,
            'read_time_minutes': read_time,
            'file_path': str(file_path),
            'file_modified_time': file_modified,
            'content_preview': content_preview,
            'search_content': search_content,
            'content_hash': self._calculate_content_hash(content)
        }
    
    def _extract_preview(self, content: str, length: int = 200) -> str:
        """Extract preview text from markdown content"""
        # Remove markdown headers
        clean_content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
        # Remove markdown links but keep text
        clean_content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_content)
        # Remove bold/italic markers
        clean_content = re.sub(r'[*_`]+', '', clean_content)
        # Get first paragraph or specified length
        paragraphs = [p.strip() for p in clean_content.split('\n\n') if p.strip()]
        if paragraphs:
            preview = paragraphs[0]
            if len(preview) > length:
                preview = preview[:length].rsplit(' ', 1)[0] + '...'
            return preview
        return content[:length] + '...' if len(content) > length else content
    
    def _strip_markdown(self, content: str) -> str:
        """Remove markdown formatting for search content"""
        # Remove headers
        content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
        # Remove links but keep text
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        # Remove bold/italic/code markers
        content = re.sub(r'[*_`]+', '', content)
        # Remove list markers
        content = re.sub(r'^\s*[-*+]\s+', '', content, flags=re.MULTILINE)
        # Remove blockquote markers
        content = re.sub(r'^\s*>\s+', '', content, flags=re.MULTILINE)
        # Normalize whitespace
        content = ' '.join(content.split())
        return content
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate MD5 hash of content for change detection"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _build_categories(self, articles: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Build category information from articles"""
        categories = {}
        category_configs = {
            'Getting Started': {
                'description': 'Essential information for new users',
                'icon': '',
                'color': '#4F46E5',
                'sort_order': 1
            },
            'Feature Tutorials': {
                'description': 'Step-by-step guides for CVD features',
                'icon': '',
                'color': '#059669',
                'sort_order': 2
            },
            'Troubleshooting': {
                'description': 'Solutions to common problems',
                'icon': '',
                'color': '#DC2626',
                'sort_order': 3
            },
            'System Administration': {
                'description': 'Advanced configuration and management',
                'icon': '',
                'color': '#7C2D12',
                'sort_order': 4
            },
            'Best Practices': {
                'description': 'Recommended workflows and tips',
                'icon': '',
                'color': '#9333EA',
                'sort_order': 5
            }
        }
        
        # Count articles per category
        for article in articles:
            category_name = article['category']
            if category_name not in categories:
                config = category_configs.get(category_name, {
                    'description': f'Articles about {category_name}',
                    'icon': '',
                    'color': '#6B7280',
                    'sort_order': 99
                })
                categories[category_name] = {
                    'name': category_name,
                    'article_count': 0,
                    **config
                }
            categories[category_name]['article_count'] += 1
            
        return categories
    
    def get_article_by_id(self, article_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific article content by ID
        
        Args:
            article_id: Article identifier
            
        Returns:
            Article data with content and navigation info
        """
        # Ensure articles are loaded
        articles = self.scan_articles()
        
        # Find the article
        article = None
        for a in articles:
            if a['id'] == article_id:
                article = a
                break
                
        if not article:
            return None
            
        # Add navigation information
        article_index = articles.index(article)
        
        # Find previous and next articles in same category
        category_articles = [a for a in articles if a['category'] == article['category']]
        current_category_index = category_articles.index(article)
        
        prev_article = None
        next_article = None
        
        if current_category_index > 0:
            prev_article = category_articles[current_category_index - 1]['id']
        if current_category_index < len(category_articles) - 1:
            next_article = category_articles[current_category_index + 1]['id']
            
        # Build breadcrumb
        breadcrumb = ['Knowledge Base', article['category'], article['title']]
        
        # Add navigation info
        article['navigation'] = {
            'breadcrumb': breadcrumb,
            'previous_article': prev_article,
            'next_article': next_article
        }
        
        return article
    
    def search_articles(self, query: str, category: str = None, 
                       difficulty: str = None) -> List[Dict[str, Any]]:
        """
        Search articles by query with optional filters
        
        Args:
            query: Search query string
            category: Optional category filter
            difficulty: Optional difficulty filter
            
        Returns:
            List of matching articles with relevance scores
        """
        if not query or len(query.strip()) < 2:
            return []
            
        articles = self.scan_articles()
        query = query.lower().strip()
        results = []
        
        for article in articles:
            # Apply filters first
            if category and article['category'] != category:
                continue
            if difficulty and article['difficulty'] != difficulty:
                continue
                
            # Calculate relevance score
            score = 0
            match_types = []
            
            # Title match (highest weight)
            if query in article['title'].lower():
                score += 10
                match_types.append('title')
                
            # Description match
            if query in article.get('description', '').lower():
                score += 5
                match_types.append('description')
                
            # Tag match
            for tag in article.get('tags', []):
                if query in tag.lower():
                    score += 3
                    match_types.append('tags')
                    break
                    
            # Content match (lower weight due to volume)
            if query in article.get('search_content', '').lower():
                score += 1
                match_types.append('content')
                
            # Category match
            if query in article['category'].lower():
                score += 2
                match_types.append('category')
                
            if score > 0:
                # Create highlighted snippet
                snippet = self._create_search_snippet(article, query)
                
                results.append({
                    'id': article['id'],
                    'title': article['title'],
                    'category': article['category'],
                    'difficulty': article['difficulty'],
                    'description': article.get('description', ''),
                    'snippet': snippet,
                    'score': score,
                    'match_type': '_and_'.join(match_types),
                    'read_time_minutes': article['read_time_minutes']
                })
                
        # Sort by relevance score (descending)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def _create_search_snippet(self, article: Dict[str, Any], query: str) -> str:
        """Create highlighted search snippet"""
        content = article.get('search_content', '')
        query_lower = query.lower()
        
        # Find first occurrence of query in content
        content_lower = content.lower()
        query_pos = content_lower.find(query_lower)
        
        if query_pos == -1:
            # Use description or preview if no content match
            return article.get('description') or article.get('content_preview', '')
            
        # Extract context around the match (±100 characters)
        start = max(0, query_pos - 100)
        end = min(len(content), query_pos + len(query) + 100)
        
        snippet = content[start:end].strip()
        
        # Add ellipsis if we truncated
        if start > 0:
            snippet = '...' + snippet
        if end < len(content):
            snippet = snippet + '...'
            
        # Highlight the query term (case-insensitive)
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        snippet = pattern.sub(f'<mark>{query}</mark>', snippet)
        
        return snippet
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories with article counts"""
        articles = self.scan_articles()
        categories = self._build_categories(articles)
        
        # Convert to list and sort
        category_list = list(categories.values())
        category_list.sort(key=lambda x: x['sort_order'])
        
        return category_list
    
    def _update_db_cache(self, articles: List[Dict[str, Any]]) -> None:
        """Update database cache with article metadata"""
        try:
            with self.get_db_connection() as conn:
                # Clear existing cache
                conn.execute('DELETE FROM knowledge_base_articles')
                
                # Insert new articles
                for article in articles:
                    conn.execute('''
                        INSERT INTO knowledge_base_articles 
                        (id, title, author, category, tags, difficulty, word_count, 
                         read_time_minutes, file_path, file_modified_time, 
                         content_preview, search_content, content_hash, last_indexed)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        article['id'],
                        article['title'],
                        article['author'],
                        article['category'],
                        ','.join(article['tags']) if article['tags'] else '',
                        article['difficulty'],
                        article['word_count'],
                        article['read_time_minutes'],
                        article['file_path'],
                        article['file_modified_time'].isoformat(),
                        article['content_preview'],
                        article['search_content'],
                        article['content_hash'],
                        datetime.now().isoformat()
                    ))
                    
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error updating database cache: {e}")
    
    def get_article_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        articles = self.scan_articles()
        
        total_articles = len(articles)
        total_words = sum(a['word_count'] for a in articles)
        categories = self._build_categories(articles)
        
        return {
            'total_articles': total_articles,
            'total_words': total_words,
            'total_categories': len(categories),
            'average_words_per_article': total_words // total_articles if total_articles > 0 else 0,
            'categories': categories,
            'last_updated': self.last_scan.isoformat() if self.last_scan else None
        }