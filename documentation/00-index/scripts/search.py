#!/usr/bin/env python3
"""
CVD Documentation Search Engine
Provides full-text search functionality for the documentation system.

Features:
- Full-text search with fuzzy matching
- Tag-based filtering and category scoping
- Relevance ranking with multiple scoring factors
- Result highlighting and snippet extraction
- Boolean queries and phrase matching
- Integration with existing documentation structure
"""

import json
import re
import os
import sys
import argparse
import math
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import difflib

@dataclass
class SearchResult:
    """Represents a single search result"""
    file_path: str
    title: str
    content: str
    category: str
    tags: List[str]
    score: float
    matches: List[Dict[str, any]]
    snippets: List[str]
    
    def to_dict(self):
        return asdict(self)

@dataclass
class SearchQuery:
    """Represents a search query with filters"""
    query: str
    categories: List[str] = None
    tags: List[str] = None
    fuzzy: bool = True
    phrase_match: bool = False
    boolean_mode: bool = False
    max_results: int = 50
    snippet_length: int = 200

class DocumentationSearchEngine:
    """Main search engine for CVD documentation"""
    
    def __init__(self, documentation_root: str = None, index_path: str = None):
        """Initialize the search engine"""
        if documentation_root is None:
            documentation_root = Path(__file__).parent.parent.parent
        
        self.documentation_root = Path(documentation_root)
        
        if index_path is None:
            index_path = self.documentation_root / "00-index" / "SEARCH_INDEX.json"
        
        self.index_path = Path(index_path)
        self.search_index = {}
        self.inverted_index = defaultdict(set)
        self.category_index = defaultdict(set)
        self.tag_index = defaultdict(set)
        self.file_metadata = {}
        
        # CVD-specific synonyms and terminology
        self.synonyms = {
            'device': ['machine', 'vending machine', 'cooler', 'equipment'],
            'planogram': ['product placement', 'slot assignment', 'layout', 'configuration'],
            'dex': ['data exchange', 'audit data', 'machine data'],
            'service order': ['work order', 'maintenance', 'task', 'repair'],
            'route': ['delivery', 'schedule', 'path', 'itinerary'],
            'analytics': ['metrics', 'reporting', 'statistics', 'data', 'insights'],
            'authentication': ['login', 'auth', 'security', 'access'],
            'api': ['endpoint', 'rest', 'interface', 'service'],
            'database': ['db', 'storage', 'data', 'sqlite'],
            'pwa': ['progressive web app', 'mobile app', 'driver app'],
            'cabinet': ['compartment', 'section', 'drawer']
        }
        
        # Importance weights for different content types
        self.content_weights = {
            'title': 3.0,
            'heading': 2.5,
            'code': 1.5,
            'content': 1.0,
            'filename': 2.0
        }
        
        # Load existing index if available
        self.load_index()
    
    def load_index(self) -> bool:
        """Load the search index from disk"""
        try:
            if self.index_path.exists():
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.search_index = data.get('search_index', {})
                    self.inverted_index = defaultdict(set, {
                        k: set(v) for k, v in data.get('inverted_index', {}).items()
                    })
                    self.category_index = defaultdict(set, {
                        k: set(v) for k, v in data.get('category_index', {}).items()
                    })
                    self.tag_index = defaultdict(set, {
                        k: set(v) for k, v in data.get('tag_index', {}).items()
                    })
                    self.file_metadata = data.get('file_metadata', {})
                return True
        except Exception as e:
            print(f"Warning: Could not load search index: {e}")
        return False
    
    def save_index(self) -> bool:
        """Save the search index to disk"""
        try:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'search_index': self.search_index,
                'inverted_index': {k: list(v) for k, v in self.inverted_index.items()},
                'category_index': {k: list(v) for k, v in self.category_index.items()},
                'tag_index': {k: list(v) for k, v in self.tag_index.items()},
                'file_metadata': self.file_metadata,
                'metadata': {
                    'version': '1.0',
                    'total_documents': len(self.search_index),
                    'total_terms': len(self.inverted_index),
                    'build_timestamp': int(os.path.getmtime(self.index_path)) if self.index_path.exists() else 0
                }
            }
            
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error: Could not save search index: {e}")
            return False
    
    def build_index(self) -> int:
        """Build the search index from all documentation files"""
        print(f"Building search index from: {self.documentation_root}")
        
        # Find all markdown files
        md_files = list(self.documentation_root.rglob("*.md"))
        
        processed_count = 0
        for file_path in md_files:
            if self.process_file(file_path):
                processed_count += 1
                if processed_count % 10 == 0:
                    print(f"Processed {processed_count} files...")
        
        print(f"Index built successfully: {processed_count} files processed")
        return processed_count
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single markdown file and add to index"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata and content structure
            metadata = self.extract_metadata(file_path, content)
            
            # Store file metadata
            file_key = str(file_path.relative_to(self.documentation_root))
            self.file_metadata[file_key] = metadata
            
            # Process content for indexing
            text_content = self.extract_text_content(content)
            
            # Create search document
            search_doc = {
                'file_path': file_key,
                'title': metadata['title'],
                'content': text_content,
                'category': metadata['category'],
                'tags': metadata['tags'],
                'headings': metadata['headings'],
                'code_blocks': metadata['code_blocks'],
                'word_count': len(text_content.split())
            }
            
            # Store in main index
            self.search_index[file_key] = search_doc
            
            # Build inverted index
            self.index_document(file_key, search_doc)
            
            return True
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def extract_metadata(self, file_path: Path, content: str) -> Dict:
        """Extract metadata from a markdown file"""
        metadata = {
            'title': '',
            'category': '',
            'tags': [],
            'headings': [],
            'code_blocks': [],
            'links': [],
            'file_size': len(content),
            'relative_path': str(file_path.relative_to(self.documentation_root))
        }
        
        # Extract title (first H1 or filename)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        else:
            metadata['title'] = file_path.stem.replace('-', ' ').replace('_', ' ').title()
        
        # Determine category from path
        parts = file_path.parts
        if len(parts) > 1:
            category_part = parts[-2] if parts[-1].endswith('.md') else parts[-1]
            metadata['category'] = self.normalize_category(category_part)
        
        # Extract all headings
        headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        metadata['headings'] = [h.strip() for h in headings]
        
        # Extract code blocks
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
        metadata['code_blocks'] = [block.strip() for block in code_blocks]
        
        # Extract links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        metadata['links'] = [{'text': text, 'url': url} for text, url in links]
        
        # Generate tags based on content and path
        metadata['tags'] = self.generate_tags(file_path, content, metadata)
        
        return metadata
    
    def normalize_category(self, category_part: str) -> str:
        """Normalize category names for consistency"""
        category_mapping = {
            '00-index': 'Navigation',
            '01-project-core': 'Project Core',
            '02-requirements': 'Requirements',
            '03-architecture': 'Architecture',
            '04-implementation': 'Implementation',
            '05-development': 'Development',
            '06-design': 'Design',
            '07-cvd-framework': 'CVD Framework',
            '08-project-management': 'Project Management',
            '09-reference': 'Reference'
        }
        
        return category_mapping.get(category_part, category_part.replace('-', ' ').title())
    
    def generate_tags(self, file_path: Path, content: str, metadata: Dict) -> List[str]:
        """Generate tags based on file content and structure"""
        tags = set()
        
        # Tags from filename
        filename_parts = file_path.stem.lower().split('-')
        tags.update(part for part in filename_parts if len(part) > 2)
        
        # Tags from content keywords
        content_lower = content.lower()
        
        # CVD-specific keywords
        cvd_keywords = [
            'device', 'planogram', 'dex', 'service-order', 'route', 'analytics',
            'authentication', 'api', 'database', 'pwa', 'cabinet', 'vending',
            'flask', 'sqlite', 'javascript', 'python', 'html', 'css'
        ]
        
        for keyword in cvd_keywords:
            if keyword in content_lower:
                tags.add(keyword)
        
        # Tags from headings
        for heading in metadata['headings']:
            heading_words = re.findall(r'\b\w{3,}\b', heading.lower())
            tags.update(heading_words)
        
        # Limit and clean tags
        tags = {tag for tag in tags if len(tag) > 2 and tag.isalpha()}
        return sorted(list(tags))[:15]  # Limit to 15 most relevant tags
    
    def extract_text_content(self, content: str) -> str:
        """Extract plain text content from markdown"""
        # Remove code blocks but keep inline code
        content = re.sub(r'```.*?```', ' ', content, flags=re.DOTALL)
        
        # Remove markdown formatting
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*([^*]+)\*', r'\1', content)      # Italic
        content = re.sub(r'`([^`]+)`', r'\1', content)        # Inline code
        content = re.sub(r'#{1,6}\s+', '', content)           # Headers
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)  # Links
        
        # Clean up whitespace
        content = re.sub(r'\n+', ' ', content)
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def index_document(self, file_key: str, doc: Dict) -> None:
        """Add document to inverted index"""
        # Index title with high weight
        self.add_terms_to_index(file_key, doc['title'], 'title')
        
        # Index content
        self.add_terms_to_index(file_key, doc['content'], 'content')
        
        # Index headings
        for heading in doc.get('headings', []):
            self.add_terms_to_index(file_key, heading, 'heading')
        
        # Index filename
        filename = Path(file_key).stem.replace('-', ' ').replace('_', ' ')
        self.add_terms_to_index(file_key, filename, 'filename')
        
        # Update category and tag indexes
        self.category_index[doc['category']].add(file_key)
        for tag in doc['tags']:
            self.tag_index[tag].add(file_key)
    
    def add_terms_to_index(self, file_key: str, text: str, content_type: str) -> None:
        """Add terms from text to the inverted index"""
        # Tokenize and normalize
        terms = self.tokenize(text)
        
        for term in terms:
            # Add to inverted index with metadata
            self.inverted_index[term].add(file_key)
            
            # Also add synonyms
            for synonym in self.get_synonyms(term):
                self.inverted_index[synonym].add(file_key)
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable terms"""
        # Convert to lowercase and extract words
        words = re.findall(r'\b\w{2,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'under', 'over',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'shall', 'this', 'that', 'these',
            'those', 'a', 'an', 'as', 'if', 'it', 'its', 'you', 'your', 'we',
            'our', 'they', 'their', 'them', 'he', 'him', 'his', 'she', 'her',
            'hers', 'me', 'my', 'mine'
        }
        
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def get_synonyms(self, term: str) -> List[str]:
        """Get synonyms for a term"""
        synonyms = []
        for key, values in self.synonyms.items():
            if term == key:
                synonyms.extend(values)
            elif term in values:
                synonyms.append(key)
                synonyms.extend([v for v in values if v != term])
        return synonyms
    
    def search(self, query_obj: SearchQuery) -> List[SearchResult]:
        """Perform search and return ranked results"""
        # Parse query
        terms = self.parse_query(query_obj)
        
        if not terms:
            return []
        
        # Find candidate documents
        candidates = self.find_candidates(terms, query_obj)
        
        # Apply filters
        if query_obj.categories:
            candidates = self.filter_by_categories(candidates, query_obj.categories)
        
        if query_obj.tags:
            candidates = self.filter_by_tags(candidates, query_obj.tags)
        
        # Score and rank results
        scored_results = self.score_results(candidates, terms, query_obj)
        
        # Sort by score
        scored_results.sort(key=lambda x: x.score, reverse=True)
        
        # Limit results
        results = scored_results[:query_obj.max_results]
        
        # Generate snippets
        for result in results:
            result.snippets = self.generate_snippets(
                result.file_path, terms, query_obj.snippet_length
            )
        
        return results
    
    def parse_query(self, query_obj: SearchQuery) -> List[str]:
        """Parse search query into terms"""
        query = query_obj.query.strip()
        
        if query_obj.phrase_match:
            # Treat entire query as a phrase
            return [query.lower()]
        
        if query_obj.boolean_mode:
            # Parse boolean operators (simplified)
            # This is a basic implementation - could be expanded
            terms = []
            for term in re.findall(r'[+\-]?\b\w+\b', query):
                terms.append(term.lower().lstrip('+-'))
            return terms
        
        # Regular tokenization
        return self.tokenize(query)
    
    def find_candidates(self, terms: List[str], query_obj: SearchQuery) -> Set[str]:
        """Find candidate documents that match search terms"""
        if not terms:
            return set()
        
        candidates = set()
        
        for term in terms:
            # Exact matches
            if term in self.inverted_index:
                candidates.update(self.inverted_index[term])
            
            # Fuzzy matches if enabled
            if query_obj.fuzzy:
                for index_term in self.inverted_index:
                    # Simple fuzzy matching using difflib
                    if difflib.SequenceMatcher(None, term, index_term).ratio() > 0.8:
                        candidates.update(self.inverted_index[index_term])
        
        return candidates
    
    def filter_by_categories(self, candidates: Set[str], categories: List[str]) -> Set[str]:
        """Filter candidates by categories"""
        category_matches = set()
        for category in categories:
            if category in self.category_index:
                category_matches.update(self.category_index[category])
        
        return candidates.intersection(category_matches)
    
    def filter_by_tags(self, candidates: Set[str], tags: List[str]) -> Set[str]:
        """Filter candidates by tags"""
        tag_matches = set()
        for tag in tags:
            if tag in self.tag_index:
                tag_matches.update(self.tag_index[tag])
        
        return candidates.intersection(tag_matches)
    
    def score_results(self, candidates: Set[str], terms: List[str], query_obj: SearchQuery) -> List[SearchResult]:
        """Score and create result objects"""
        results = []
        
        for file_key in candidates:
            doc = self.search_index.get(file_key)
            if not doc:
                continue
            
            score = self.calculate_score(doc, terms, query_obj)
            matches = self.find_matches(doc, terms)
            
            result = SearchResult(
                file_path=file_key,
                title=doc['title'],
                content=doc['content'],
                category=doc['category'],
                tags=doc['tags'],
                score=score,
                matches=matches,
                snippets=[]  # Will be populated later
            )
            
            results.append(result)
        
        return results
    
    def calculate_score(self, doc: Dict, terms: List[str], query_obj: SearchQuery) -> float:
        """Calculate relevance score for a document"""
        score = 0.0
        
        # Count term frequencies in different parts
        title_lower = doc['title'].lower()
        content_lower = doc['content'].lower()
        
        for term in terms:
            # Title matches (highest weight)
            title_freq = title_lower.count(term)
            score += title_freq * self.content_weights['title']
            
            # Content matches
            content_freq = content_lower.count(term)
            score += content_freq * self.content_weights['content']
            
            # Heading matches
            for heading in doc.get('headings', []):
                heading_freq = heading.lower().count(term)
                score += heading_freq * self.content_weights['heading']
            
            # Filename matches
            filename = Path(doc['file_path']).stem.lower()
            filename_freq = filename.count(term)
            score += filename_freq * self.content_weights['filename']
        
        # Bonus for exact phrase matches
        if len(terms) > 1:
            phrase = ' '.join(terms)
            if phrase in content_lower:
                score += 5.0
            if phrase in title_lower:
                score += 10.0
        
        # Document length penalty (prefer focused content)
        if doc['word_count'] > 0:
            score = score * (1 + 1000 / doc['word_count'])
        
        return score
    
    def find_matches(self, doc: Dict, terms: List[str]) -> List[Dict[str, any]]:
        """Find specific matches within document"""
        matches = []
        content = doc['content']
        
        for term in terms:
            # Find all occurrences
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            for match in pattern.finditer(content):
                matches.append({
                    'term': term,
                    'start': match.start(),
                    'end': match.end(),
                    'context': self.get_match_context(content, match.start(), match.end())
                })
        
        return matches
    
    def get_match_context(self, content: str, start: int, end: int, context_size: int = 50) -> str:
        """Get context around a match"""
        context_start = max(0, start - context_size)
        context_end = min(len(content), end + context_size)
        
        context = content[context_start:context_end]
        
        # Clean up context
        context = re.sub(r'\s+', ' ', context).strip()
        
        return context
    
    def generate_snippets(self, file_path: str, terms: List[str], max_length: int = 200) -> List[str]:
        """Generate text snippets with highlighted matches"""
        doc = self.search_index.get(file_path)
        if not doc:
            return []
        
        content = doc['content']
        snippets = []
        
        # Find best snippets around matches
        for term in terms[:3]:  # Limit to first 3 terms
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            match = pattern.search(content)
            
            if match:
                # Get snippet around match
                start = max(0, match.start() - max_length // 2)
                end = min(len(content), match.start() + max_length // 2)
                
                snippet = content[start:end]
                snippet = re.sub(r'\s+', ' ', snippet).strip()
                
                # Add ellipsis if truncated
                if start > 0:
                    snippet = '...' + snippet
                if end < len(content):
                    snippet = snippet + '...'
                
                # Highlight the term
                highlighted = pattern.sub(f'**{term}**', snippet)
                snippets.append(highlighted)
        
        return snippets[:2]  # Return max 2 snippets
    
    def get_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """Get search suggestions for partial queries"""
        if len(partial_query) < 2:
            return []
        
        partial_lower = partial_query.lower()
        suggestions = []
        
        # Find matching terms from index
        for term in self.inverted_index:
            if term.startswith(partial_lower):
                suggestions.append(term)
                if len(suggestions) >= limit:
                    break
        
        # Add fuzzy matches if we need more
        if len(suggestions) < limit:
            for term in self.inverted_index:
                if partial_lower in term and term not in suggestions:
                    suggestions.append(term)
                    if len(suggestions) >= limit:
                        break
        
        return sorted(suggestions)
    
    def get_statistics(self) -> Dict:
        """Get search index statistics"""
        return {
            'total_documents': len(self.search_index),
            'total_terms': len(self.inverted_index),
            'total_categories': len(self.category_index),
            'total_tags': len(self.tag_index),
            'index_size_mb': round(self.index_path.stat().st_size / (1024 * 1024), 2) if self.index_path.exists() else 0
        }

def main():
    """Command line interface for the search engine"""
    parser = argparse.ArgumentParser(description='CVD Documentation Search Engine')
    parser.add_argument('--build', action='store_true', help='Build search index')
    parser.add_argument('--search', type=str, help='Search query')
    parser.add_argument('--categories', type=str, nargs='*', help='Filter by categories')
    parser.add_argument('--tags', type=str, nargs='*', help='Filter by tags')
    parser.add_argument('--fuzzy', action='store_true', default=True, help='Enable fuzzy search')
    parser.add_argument('--phrase', action='store_true', help='Phrase matching')
    parser.add_argument('--max-results', type=int, default=20, help='Maximum results')
    parser.add_argument('--stats', action='store_true', help='Show index statistics')
    parser.add_argument('--suggestions', type=str, help='Get search suggestions')
    
    args = parser.parse_args()
    
    # Initialize search engine
    engine = DocumentationSearchEngine()
    
    if args.build:
        print("Building search index...")
        count = engine.build_index()
        if engine.save_index():
            print(f"Index built successfully: {count} files indexed")
        else:
            print("Error saving index")
            return 1
    
    if args.stats:
        stats = engine.get_statistics()
        print("Search Index Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    if args.suggestions:
        suggestions = engine.get_suggestions(args.suggestions)
        print(f"Suggestions for '{args.suggestions}':")
        for suggestion in suggestions:
            print(f"  {suggestion}")
    
    if args.search:
        query = SearchQuery(
            query=args.search,
            categories=args.categories,
            tags=args.tags,
            fuzzy=args.fuzzy,
            phrase_match=args.phrase,
            max_results=args.max_results
        )
        
        print(f"Searching for: '{args.search}'")
        if args.categories:
            print(f"Categories: {', '.join(args.categories)}")
        if args.tags:
            print(f"Tags: {', '.join(args.tags)}")
        print()
        
        results = engine.search(query)
        
        if not results:
            print("No results found.")
            return 0
        
        print(f"Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.title}")
            print(f"   Path: {result.file_path}")
            print(f"   Category: {result.category}")
            print(f"   Score: {result.score:.2f}")
            
            if result.tags:
                print(f"   Tags: {', '.join(result.tags[:5])}")
            
            if result.snippets:
                for snippet in result.snippets:
                    print(f"   Snippet: {snippet}")
            
            print()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())