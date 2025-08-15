#!/usr/bin/env python3
"""
Quick test script for Knowledge Base functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.knowledge_base_service import KnowledgeBaseService

def test_knowledge_base():
    """Test the knowledge base service"""
    print("Testing Knowledge Base Service...")
    
    # Initialize service
    kb = KnowledgeBaseService()
    
    # Test article scanning
    print("\n1. Testing article scanning:")
    articles = kb.scan_articles()
    print(f"   Found {len(articles)} articles")
    
    for article in articles:
        print(f"   - {article['title']} ({article['category']}, {article['difficulty']})")
    
    # Test categories
    print("\n2. Testing categories:")
    categories = kb.get_categories()
    print(f"   Found {len(categories)} categories")
    
    for category in categories:
        print(f"   - {category['name']}: {category['article_count']} articles")
    
    # Test search
    print("\n3. Testing search:")
    search_terms = ["planogram", "login", "device", "troubleshooting"]
    
    for term in search_terms:
        results = kb.search_articles(term)
        print(f"   Search for '{term}': {len(results)} results")
        for result in results[:2]:  # Show top 2 results
            print(f"     - {result['title']} (score: {result['score']})")
    
    # Test specific article
    print("\n4. Testing specific article retrieval:")
    if articles:
        article_id = articles[0]['id']
        article = kb.get_article_by_id(article_id)
        if article:
            print(f"   Retrieved: {article['title']}")
            print(f"   Navigation: {article.get('navigation', {})}")
        else:
            print(f"   Failed to retrieve article: {article_id}")
    
    # Test stats
    print("\n5. Testing statistics:")
    stats = kb.get_article_stats()
    print(f"   Total articles: {stats['total_articles']}")
    print(f"   Total words: {stats['total_words']}")
    print(f"   Categories: {stats['total_categories']}")
    print(f"   Avg words per article: {stats['average_words_per_article']}")
    
    print("\n✅ Knowledge Base Service test completed successfully!")

if __name__ == "__main__":
    test_knowledge_base()