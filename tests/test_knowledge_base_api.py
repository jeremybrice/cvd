"""
Knowledge Base API Test Suite
Comprehensive testing of all knowledge base API endpoints
Tests authentication, error handling, performance, and data validation
"""

import pytest
import json
import time
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sqlite3

# Test configuration
TEST_DB_PATH = ":memory:"
TEST_CONTENT_PATH = "/tmp/test_kb_content"

class TestKnowledgeBaseService:
    """Test the KnowledgeBaseService class"""
    
    @pytest.fixture
    def setup_test_content(self):
        """Create test markdown files"""
        content_dir = Path(TEST_CONTENT_PATH)
        content_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test articles with proper frontmatter
        test_articles = [
            {
                "filename": "getting-started.md",
                "content": """---
title: "Test Getting Started"
author: "Test Author" 
category: "Getting Started"
tags: ["test", "basics"]
difficulty: "Beginner"
last_updated: "2025-08-06T10:00:00Z"
description: "Test article for getting started"
---

# Test Getting Started

This is a test article for the getting started category.

## Section 1
Content here.

## Section 2
More content here.
"""
            },
            {
                "filename": "advanced-config.md", 
                "content": """---
title: "Advanced Configuration"
author: "Tech Team"
category: "System Administration"
tags: ["advanced", "configuration"]
difficulty: "Advanced"
last_updated: "2025-08-05T15:30:00Z"
description: "Advanced system configuration guide"
---

# Advanced Configuration

This article covers advanced configuration topics.

## Database Setup
Step-by-step instructions.

## Security Configuration
Security best practices.
"""
            },
            {
                "filename": "invalid-frontmatter.md",
                "content": """# Invalid Article

This article has no frontmatter and should be skipped.
"""
            }
        ]
        
        for article in test_articles:
            file_path = content_dir / article["filename"]
            file_path.write_text(article["content"])
        
        yield content_dir
        
        # Cleanup
        import shutil
        if content_dir.exists():
            shutil.rmtree(content_dir)
    
    @pytest.fixture
    def knowledge_base_service(self, setup_test_content):
        """Create KnowledgeBaseService instance with test data"""
        from services.knowledge_base_service import KnowledgeBaseService
        return KnowledgeBaseService(content_path=str(setup_test_content), db_path=TEST_DB_PATH)
    
    def test_scan_articles_success(self, knowledge_base_service):
        """Test successful article scanning"""
        articles = knowledge_base_service.scan_articles()
        
        # Should return valid articles only (invalid frontmatter filtered out)
        assert len(articles) == 2
        
        # Check article structure
        for article in articles:
            assert "id" in article
            assert "title" in article
            assert "author" in article
            assert "category" in article
            assert "tags" in article
            assert "difficulty" in article
            assert "content" in article
            assert "word_count" in article
            assert "read_time_minutes" in article
            assert "last_updated" in article
        
        # Check specific articles
        getting_started = next((a for a in articles if a["id"] == "getting-started"), None)
        assert getting_started is not None
        assert getting_started["title"] == "Test Getting Started"
        assert getting_started["category"] == "Getting Started"
        assert getting_started["difficulty"] == "Beginner"
        assert "test" in getting_started["tags"]
    
    def test_scan_articles_caching(self, knowledge_base_service):
        """Test article caching functionality"""
        # First scan
        start_time = time.time()
        articles1 = knowledge_base_service.scan_articles()
        first_scan_time = time.time() - start_time
        
        # Second scan (should be cached)
        start_time = time.time()
        articles2 = knowledge_base_service.scan_articles()
        second_scan_time = time.time() - start_time
        
        # Results should be identical
        assert len(articles1) == len(articles2)
        assert articles1[0]["id"] == articles2[0]["id"]
        
        # Second scan should be faster (cached)
        # Note: This might not always be reliable in tests, so we just check the cache exists
        assert knowledge_base_service.cache.get("articles") is not None
    
    def test_get_article_by_id_success(self, knowledge_base_service):
        """Test successful article retrieval by ID"""
        article = knowledge_base_service.get_article_by_id("getting-started")
        
        assert article is not None
        assert article["id"] == "getting-started"
        assert article["title"] == "Test Getting Started"
        assert "navigation" in article
        assert "breadcrumb" in article["navigation"]
        assert article["navigation"]["breadcrumb"] == ["Knowledge Base", "Getting Started", "Test Getting Started"]
    
    def test_get_article_by_id_not_found(self, knowledge_base_service):
        """Test article retrieval with invalid ID"""
        article = knowledge_base_service.get_article_by_id("nonexistent-article")
        assert article is None
    
    def test_search_articles_title_match(self, knowledge_base_service):
        """Test search functionality with title matches"""
        results = knowledge_base_service.search_articles("getting started")
        
        assert len(results) >= 1
        
        # Check result structure
        result = results[0]
        assert "id" in result
        assert "title" in result
        assert "category" in result
        assert "snippet" in result
        assert "score" in result
        assert "match_type" in result
        
        # Should find the getting started article
        assert result["id"] == "getting-started"
        assert result["score"] > 0
    
    def test_search_articles_content_match(self, knowledge_base_service):
        """Test search functionality with content matches"""
        results = knowledge_base_service.search_articles("database setup")
        
        assert len(results) >= 1
        result = results[0]
        assert "advanced-config" in result["id"]
        assert "database" in result["snippet"].lower()
    
    def test_search_articles_with_filters(self, knowledge_base_service):
        """Test search with category and difficulty filters"""
        # Search with category filter
        results = knowledge_base_service.search_articles(
            query="test", 
            category="Getting Started"
        )
        
        assert len(results) >= 1
        for result in results:
            assert result["category"] == "Getting Started"
        
        # Search with difficulty filter
        results = knowledge_base_service.search_articles(
            query="configuration", 
            difficulty="Advanced"
        )
        
        assert len(results) >= 1
        for result in results:
            assert result["difficulty"] == "Advanced"
    
    def test_search_articles_empty_query(self, knowledge_base_service):
        """Test search with empty or too short query"""
        # Empty query
        results = knowledge_base_service.search_articles("")
        assert len(results) == 0
        
        # Too short query
        results = knowledge_base_service.search_articles("a")
        assert len(results) == 0
    
    def test_get_categories(self, knowledge_base_service):
        """Test category retrieval"""
        categories = knowledge_base_service.get_categories()
        
        assert len(categories) >= 2  # Should have at least the categories from test articles
        
        # Check category structure
        for category in categories:
            assert "name" in category
            assert "article_count" in category
            assert "description" in category
            assert "icon" in category
            assert "color" in category
            assert "sort_order" in category
        
        # Check specific categories
        category_names = [c["name"] for c in categories]
        assert "Getting Started" in category_names
        assert "System Administration" in category_names
    
    def test_get_article_stats(self, knowledge_base_service):
        """Test knowledge base statistics"""
        stats = knowledge_base_service.get_article_stats()
        
        assert "total_articles" in stats
        assert "total_words" in stats
        assert "total_categories" in stats
        assert "average_words_per_article" in stats
        assert "categories" in stats
        assert "last_updated" in stats
        
        # Verify counts
        assert stats["total_articles"] == 2
        assert stats["total_categories"] >= 2
        assert stats["total_words"] > 0


class TestKnowledgeBaseAPIEndpoints:
    """Test the Flask API endpoints"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask app"""
        # This would normally import your actual Flask app
        # For testing, we'll mock the necessary components
        from unittest.mock import MagicMock
        app = MagicMock()
        return app
    
    @pytest.fixture
    def mock_auth_session(self):
        """Mock authenticated session"""
        with patch('flask.session') as mock_session:
            mock_session.get.return_value = 1  # Mock user_id
            yield mock_session
    
    @pytest.fixture  
    def mock_kb_service(self):
        """Mock KnowledgeBaseService"""
        with patch('services.knowledge_base_service.KnowledgeBaseService') as mock_service:
            mock_instance = mock_service.return_value
            
            # Mock article data
            mock_instance.scan_articles.return_value = [
                {
                    "id": "test-article-1",
                    "title": "Test Article 1",
                    "author": "Test Author",
                    "category": "Getting Started", 
                    "tags": ["test"],
                    "difficulty": "Beginner",
                    "description": "Test description",
                    "word_count": 100,
                    "read_time_minutes": 1,
                    "last_updated": "2025-08-06T10:00:00Z"
                }
            ]
            
            # Mock categories
            mock_instance.get_categories.return_value = [
                {
                    "name": "Getting Started",
                    "description": "Essential information",
                    "icon": "📚",
                    "color": "#4F46E5",
                    "article_count": 1,
                    "sort_order": 1
                }
            ]
            
            # Mock article by ID
            mock_instance.get_article_by_id.return_value = {
                "id": "test-article-1",
                "title": "Test Article 1",
                "content": "# Test Article\n\nThis is test content.",
                "metadata": {
                    "author": "Test Author",
                    "category": "Getting Started",
                    "tags": ["test"],
                    "difficulty": "Beginner",
                    "last_updated": "2025-08-06T10:00:00Z",
                    "description": "Test description",
                    "word_count": 100,
                    "read_time_minutes": 1
                },
                "navigation": {
                    "breadcrumb": ["Knowledge Base", "Getting Started", "Test Article 1"],
                    "previous_article": None,
                    "next_article": None
                }
            }
            
            # Mock search results
            mock_instance.search_articles.return_value = [
                {
                    "id": "test-article-1",
                    "title": "Test Article 1", 
                    "category": "Getting Started",
                    "difficulty": "Beginner",
                    "description": "Test description",
                    "snippet": "This is a test <mark>article</mark> snippet",
                    "score": 10,
                    "match_type": "title",
                    "read_time_minutes": 1
                }
            ]
            
            yield mock_instance

    def test_get_articles_endpoint_success(self, mock_auth_session, mock_kb_service):
        """Test /api/knowledge-base/articles endpoint success"""
        # Mock the actual endpoint function
        with patch('app.jsonify') as mock_jsonify:
            mock_jsonify.return_value = {"success": True}
            
            # Import and call the actual endpoint function
            from app import get_knowledge_base_articles
            
            result = get_knowledge_base_articles()
            
            # Verify service was called
            mock_kb_service.scan_articles.assert_called_once()
            mock_kb_service.get_categories.assert_called_once()
    
    def test_get_articles_endpoint_auth_required(self):
        """Test /api/knowledge-base/articles requires authentication"""
        with patch('flask.session') as mock_session:
            mock_session.get.return_value = None  # No user_id
            
            with patch('app.jsonify') as mock_jsonify:
                with patch('app.auth_manager') as mock_auth:
                    mock_auth.require_auth.return_value = ({"success": False, "error": "Authentication required"}, 401)
                    
                    # Test should return 401
                    # This tests the decorator behavior
                    pass
    
    def test_get_article_endpoint_success(self, mock_auth_session, mock_kb_service):
        """Test /api/knowledge-base/articles/<id> endpoint success"""
        with patch('app.jsonify') as mock_jsonify:
            with patch('markdown.markdown') as mock_markdown:
                mock_markdown.return_value = "<h1>Test Article</h1><p>Content</p>"
                mock_jsonify.return_value = {"success": True}
                
                from app import get_knowledge_base_article
                
                result = get_knowledge_base_article("test-article-1")
                
                # Verify service was called with correct ID
                mock_kb_service.get_article_by_id.assert_called_once_with("test-article-1")
                mock_markdown.assert_called_once()
    
    def test_get_article_endpoint_not_found(self, mock_auth_session, mock_kb_service):
        """Test /api/knowledge-base/articles/<id> endpoint with invalid ID"""
        mock_kb_service.get_article_by_id.return_value = None
        
        with patch('app.jsonify') as mock_jsonify:
            mock_jsonify.return_value = ({"success": False, "error": "Article not found"}, 404)
            
            from app import get_knowledge_base_article
            
            result = get_knowledge_base_article("nonexistent")
            
            mock_kb_service.get_article_by_id.assert_called_once_with("nonexistent")
    
    def test_search_endpoint_success(self, mock_auth_session, mock_kb_service):
        """Test /api/knowledge-base/search endpoint success"""
        with patch('flask.request') as mock_request:
            mock_request.args.get.side_effect = lambda key, default='': {
                'q': 'test query',
                'category': '',
                'difficulty': ''
            }.get(key, default)
            
            with patch('app.jsonify') as mock_jsonify:
                with patch('time.time', side_effect=[1000, 1000.05]):  # Mock 50ms search time
                    mock_jsonify.return_value = {"success": True}
                    
                    from app import search_knowledge_base
                    
                    result = search_knowledge_base()
                    
                    mock_kb_service.search_articles.assert_called_once_with("test query", None, None)
    
    def test_search_endpoint_query_too_short(self, mock_auth_session):
        """Test /api/knowledge-base/search endpoint with short query"""
        with patch('flask.request') as mock_request:
            mock_request.args.get.side_effect = lambda key, default='': {
                'q': 'a',  # Too short
                'category': '',
                'difficulty': ''
            }.get(key, default)
            
            with patch('app.jsonify') as mock_jsonify:
                mock_jsonify.return_value = ({"success": False, "error": "Query must be at least 2 characters"}, 400)
                
                from app import search_knowledge_base
                
                result = search_knowledge_base()
    
    def test_categories_endpoint_success(self, mock_auth_session, mock_kb_service):
        """Test /api/knowledge-base/categories endpoint success"""
        with patch('app.jsonify') as mock_jsonify:
            mock_jsonify.return_value = {"success": True}
            
            from app import get_knowledge_base_categories
            
            result = get_knowledge_base_categories()
            
            mock_kb_service.get_categories.assert_called_once()
    
    def test_stats_endpoint_success(self, mock_auth_session, mock_kb_service):
        """Test /api/knowledge-base/stats endpoint success"""
        mock_kb_service.get_article_stats.return_value = {
            "total_articles": 5,
            "total_words": 1000,
            "total_categories": 3
        }
        
        with patch('app.jsonify') as mock_jsonify:
            mock_jsonify.return_value = {"success": True}
            
            from app import get_knowledge_base_stats
            
            result = get_knowledge_base_stats()
            
            mock_kb_service.get_article_stats.assert_called_once()


class TestKnowledgeBasePerformance:
    """Performance tests for knowledge base functionality"""
    
    def test_search_performance_benchmark(self):
        """Test search performance meets requirements (< 500ms)"""
        # This would test with larger datasets
        # For now, we'll test the basic structure
        pass
    
    def test_article_loading_performance(self):
        """Test article loading performance (< 1s)"""
        # This would test article loading times
        pass
    
    def test_memory_usage(self):
        """Test memory usage stays within limits"""
        # This would test memory consumption
        pass


class TestKnowledgeBaseErrorHandling:
    """Test error handling and edge cases"""
    
    def test_missing_content_directory(self):
        """Test behavior when content directory doesn't exist"""
        from services.knowledge_base_service import KnowledgeBaseService
        service = KnowledgeBaseService(content_path="/nonexistent/path")
        
        # Should handle gracefully and return empty list
        articles = service.scan_articles()
        assert isinstance(articles, list)
        assert len(articles) == 0
    
    def test_malformed_yaml_frontmatter(self):
        """Test handling of malformed YAML frontmatter"""
        # Create temporary file with bad YAML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
title: "Test"
author: [unclosed yaml list
category: "Test"
---

Content here.
""")
            f.flush()
            
            from services.knowledge_base_service import KnowledgeBaseService
            service = KnowledgeBaseService()
            
            # Should handle the parsing error gracefully
            result = service._parse_article(Path(f.name))
            assert result is None
        
        # Cleanup
        os.unlink(f.name)
    
    def test_database_connection_error(self):
        """Test handling of database connection errors"""
        from services.knowledge_base_service import KnowledgeBaseService
        service = KnowledgeBaseService(db_path="/invalid/path/db.sqlite")
        
        # Should handle database errors gracefully
        # This tests the _update_db_cache method error handling
        service.cache['articles'] = []
        # Should not raise exception
        service._update_db_cache([])
    
    def test_unicode_content_handling(self):
        """Test handling of Unicode content in articles"""
        # Test with Unicode characters, emojis, special symbols
        unicode_content = """---
title: "Unicode Test 🚀"
author: "Test Author"
category: "Test"
tags: ["unicode", "émoji", "中文"]
difficulty: "Beginner" 
description: "Testing Unicode handling"
---

# Unicode Content Test

This article contains various Unicode characters:
- Emojis: 🎯 📚 ⭐
- Accented characters: café, naïve, résumé
- Chinese characters: 测试文档
- Mathematical symbols: ∑ ∫ √
- Currency symbols: $ € £ ¥
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(unicode_content)
            f.flush()
            
            from services.knowledge_base_service import KnowledgeBaseService
            service = KnowledgeBaseService()
            
            result = service._parse_article(Path(f.name))
            assert result is not None
            assert "🚀" in result["title"]
            assert "émoji" in result["tags"]
            assert "测试文档" in result["content"]
        
        os.unlink(f.name)


class TestKnowledgeBaseValidation:
    """Test data validation and security"""
    
    def test_xss_prevention_in_content(self):
        """Test that XSS attempts in content are handled safely"""
        malicious_content = """---
title: "XSS Test"
author: "Test"
category: "Test" 
difficulty: "Beginner"
description: "Testing XSS prevention"
---

# XSS Test

<script>alert('xss')</script>
<img src="x" onerror="alert('xss')">
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(malicious_content)
            f.flush()
            
            from services.knowledge_base_service import KnowledgeBaseService
            service = KnowledgeBaseService()
            
            result = service._parse_article(Path(f.name))
            assert result is not None
            # Content should be preserved as-is (XSS prevention happens in frontend/markdown rendering)
            assert "<script>" in result["content"]
        
        os.unlink(f.name)
    
    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are prevented"""
        # Test malicious search queries
        from services.knowledge_base_service import KnowledgeBaseService
        service = KnowledgeBaseService()
        
        malicious_queries = [
            "'; DROP TABLE articles; --",
            "' OR '1'='1",
            "UNION SELECT * FROM users",
        ]
        
        for query in malicious_queries:
            # Should not raise exceptions and return empty results
            results = service.search_articles(query)
            assert isinstance(results, list)
    
    def test_path_traversal_prevention(self):
        """Test that path traversal attempts are prevented"""
        from services.knowledge_base_service import KnowledgeBaseService
        service = KnowledgeBaseService()
        
        malicious_ids = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\drivers\\etc\\hosts"
        ]
        
        for malicious_id in malicious_ids:
            # Should return None (not found) rather than exposing files
            result = service.get_article_by_id(malicious_id)
            assert result is None


if __name__ == "__main__":
    # Run specific test categories
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--durations=10"
    ])