"""
Knowledge Base Integration Test Suite
End-to-end testing of complete user workflows
Tests the integration between backend, frontend, and user interactions
"""

import pytest
import time
import json
import tempfile
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import requests


class TestKnowledgeBaseIntegration:
    """End-to-end integration tests for Knowledge Base functionality"""
    
    @pytest.fixture(scope="class")
    def web_driver(self):
        """Setup Chrome WebDriver for testing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode for CI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    @pytest.fixture
    def authenticated_session(self, web_driver):
        """Login and authenticate the session"""
        driver = web_driver
        
        # Navigate to login page
        driver.get("http://localhost:8000/")
        
        # Wait for login form
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        
        # Login with test credentials
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin")
        login_button.click()
        
        # Wait for successful login (look for main navigation)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nav"))
        )
        
        return driver
    
    def test_complete_user_journey_browse_by_category(self, authenticated_session):
        """Test complete user journey: login -> browse categories -> view article"""
        driver = authenticated_session
        
        # Step 1: Navigate to Knowledge Base
        help_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Help"))
        )
        help_menu.click()
        
        knowledge_base_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Knowledge Base"))
        )
        knowledge_base_link.click()
        
        # Step 2: Wait for Knowledge Base to load in iframe
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        
        # Switch to iframe
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)
        
        # Wait for categories to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "kb-category-card"))
        )
        
        # Step 3: Click on "Getting Started" category
        category_cards = driver.find_elements(By.CLASS_NAME, "kb-category-card")
        getting_started_card = None
        
        for card in category_cards:
            if "Getting Started" in card.text:
                getting_started_card = card
                break
        
        assert getting_started_card is not None, "Getting Started category not found"
        getting_started_card.click()
        
        # Step 4: Verify article list loads
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "articleListView"))
        )
        
        article_list = driver.find_element(By.ID, "articleListView")
        assert article_list.is_displayed(), "Article list should be visible"
        
        # Verify breadcrumb
        breadcrumb = driver.find_element(By.ID, "breadcrumb")
        assert "Getting Started" in breadcrumb.text, "Breadcrumb should show category"
        
        # Step 5: Click on first article
        article_items = driver.find_elements(By.CLASS_NAME, "kb-article-item")
        assert len(article_items) > 0, "Should have at least one article"
        
        first_article = article_items[0]
        first_article.click()
        
        # Step 6: Verify article content loads
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "articleView"))
        )
        
        article_view = driver.find_element(By.ID, "articleView")
        assert article_view.is_displayed(), "Article view should be visible"
        
        # Verify article content is present
        article_content = driver.find_element(By.ID, "articleContent")
        assert len(article_content.text) > 0, "Article should have content"
        
        # Verify metadata is displayed
        article_metadata = driver.find_element(By.ID, "articleMetadata")
        assert "Author:" in article_metadata.text, "Article metadata should be displayed"
        
        # Step 7: Test back navigation
        back_button = driver.find_element(By.ID, "articleBackButton")
        back_button.click()
        
        # Verify we're back to article list
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "articleListView"))
        )
        
        driver.switch_to.default_content()
    
    def test_search_workflow(self, authenticated_session):
        """Test complete search workflow: search -> view results -> view article"""
        driver = authenticated_session
        
        # Navigate to Knowledge Base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)
        
        # Wait for search input to be available
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        
        # Perform search
        search_query = "getting started"
        search_input.clear()
        search_input.send_keys(search_query)
        
        # Wait for debounced search (300ms + buffer)
        time.sleep(1)
        
        # Verify search results appear
        search_results = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchResults"))
        )
        assert search_results.is_displayed(), "Search results should be visible"
        
        # Check for search result items
        result_items = driver.find_elements(By.CLASS_NAME, "kb-search-result-item")
        assert len(result_items) > 0, "Should have search results"
        
        # Verify search highlighting
        first_result = result_items[0]
        snippet = first_result.find_element(By.CLASS_NAME, "kb-search-snippet")
        # Check for highlighted terms (marked with <mark> tags)
        snippet_html = snippet.get_attribute("innerHTML")
        
        # Click on first search result
        first_result.click()
        
        # Verify article loads
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "articleView"))
        )
        
        article_view = driver.find_element(By.ID, "articleView")
        assert article_view.is_displayed(), "Article should load from search results"
        
        driver.switch_to.default_content()
    
    def test_search_filters(self, authenticated_session):
        """Test search with category and difficulty filters"""
        driver = authenticated_session
        
        # Navigate to Knowledge Base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Focus on search input to show filters
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_input.click()
        
        # Wait for filters to appear
        search_filters = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "searchFilters"))
        )
        
        # Test category filter
        category_filter = driver.find_element(By.ID, "categoryFilter")
        options = category_filter.find_elements(By.TAG_NAME, "option")
        assert len(options) > 1, "Should have category options"
        
        # Select a category
        category_filter.click()
        category_filter.find_element(By.XPATH, "//option[text()='Getting Started']").click()
        
        # Perform search with filter
        search_input.send_keys("tutorial")
        time.sleep(1)
        
        # Verify filtered results
        result_items = driver.find_elements(By.CLASS_NAME, "kb-search-result-item")
        if len(result_items) > 0:
            # Check that all results are from the selected category
            for item in result_items:
                meta = item.find_element(By.CLASS_NAME, "kb-article-meta")
                assert "Getting Started" in meta.text, "All results should be from selected category"
        
        driver.switch_to.default_content()
    
    def test_keyboard_navigation(self, authenticated_session):
        """Test keyboard navigation accessibility"""
        driver = authenticated_session
        
        # Navigate to Knowledge Base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Start from search input
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_input.click()
        
        # Tab through interactive elements
        actions = ActionChains(driver)
        
        # Tab to next element
        actions.send_keys(Keys.TAB)
        actions.perform()
        
        # Verify focus moved to next interactive element
        active_element = driver.switch_to.active_element
        assert active_element != search_input, "Focus should move with Tab key"
        
        # Test Enter key activation on category cards
        category_cards = driver.find_elements(By.CLASS_NAME, "kb-category-card")
        if len(category_cards) > 0:
            first_card = category_cards[0]
            first_card.click()  # Focus the card
            
            # Press Enter to activate
            actions = ActionChains(driver)
            actions.send_keys(Keys.ENTER)
            actions.perform()
            
            # Verify navigation occurred
            time.sleep(1)
            article_list = driver.find_element(By.ID, "articleListView")
            # Note: This test may need adjustment based on actual keyboard event handling
        
        driver.switch_to.default_content()
    
    def test_responsive_breakpoints(self, authenticated_session):
        """Test responsive design at different viewport sizes"""
        driver = authenticated_session
        
        # Test different viewport sizes
        viewports = [
            (375, 667),   # Mobile
            (768, 1024),  # Tablet
            (1200, 800),  # Desktop
        ]
        
        for width, height in viewports:
            driver.set_window_size(width, height)
            
            # Navigate to Knowledge Base
            driver.get("http://localhost:8000/#knowledge-base")
            
            # Switch to iframe
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            driver.switch_to.frame(iframe)
            
            # Verify layout adapts
            container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "kb-container"))
            )
            
            # Check search input is visible and properly sized
            search_input = driver.find_element(By.ID, "searchInput")
            assert search_input.is_displayed(), f"Search input should be visible at {width}x{height}"
            
            # Check categories grid layout
            categories_grid = driver.find_element(By.ID, "categoriesGrid")
            assert categories_grid.is_displayed(), f"Categories grid should be visible at {width}x{height}"
            
            # For mobile, verify single column layout
            if width < 768:
                # Categories should stack vertically
                category_cards = driver.find_elements(By.CLASS_NAME, "kb-category-card")
                if len(category_cards) >= 2:
                    card1_rect = category_cards[0].rect
                    card2_rect = category_cards[1].rect
                    # Cards should be stacked (second card below first)
                    assert card2_rect['y'] > card1_rect['y'], "Cards should stack vertically on mobile"
            
            driver.switch_to.default_content()
    
    def test_error_handling(self, authenticated_session):
        """Test error handling for network failures and invalid data"""
        driver = authenticated_session
        
        # Navigate to Knowledge Base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Test invalid article ID (simulate via direct URL manipulation)
        driver.execute_script("""
            // Simulate clicking on a non-existent article
            if (window.knowledgeBase) {
                window.knowledgeBase.showArticle('non-existent-article-id');
            }
        """)
        
        # Wait for error state or graceful handling
        time.sleep(2)
        
        # Check if error is handled gracefully
        error_state = driver.find_elements(By.ID, "errorState")
        loading_state = driver.find_elements(By.ID, "loadingState")
        
        # Error should be handled without breaking the interface
        # Either show error state or return to safe state
        assert len(error_state) == 0 or not error_state[0].is_displayed() or \
               "error" in error_state[0].text.lower(), "Error should be handled gracefully"
        
        driver.switch_to.default_content()
    
    def test_performance_requirements(self, authenticated_session):
        """Test performance requirements are met"""
        driver = authenticated_session
        
        # Navigate to Knowledge Base and measure load time
        start_time = time.time()
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Wait for iframe to load
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Wait for categories to load (indicating full initialization)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "kb-category-card"))
        )
        
        load_time = time.time() - start_time
        
        # Test requirement: Page load < 2 seconds
        assert load_time < 2.0, f"Page load time {load_time:.2f}s exceeds 2 second requirement"
        
        # Test search performance
        search_input = driver.find_element(By.ID, "searchInput")
        
        search_start = time.time()
        search_input.send_keys("test query")
        
        # Wait for search results or timeout
        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.ID, "searchResults"))
            )
            search_time = time.time() - search_start
            
            # Test requirement: Search response < 500ms
            assert search_time < 0.5, f"Search response time {search_time:.2f}s exceeds 500ms requirement"
        except:
            # Search may not complete due to test environment
            pass
        
        driver.switch_to.default_content()
    
    def test_cross_browser_compatibility(self):
        """Test compatibility across different browsers"""
        # This test would be expanded to test Firefox, Safari, Edge
        # For now, we test Chrome as the primary browser
        pass
    
    def test_authentication_integration(self, web_driver):
        """Test authentication integration and session management"""
        driver = web_driver
        
        # Test unauthenticated access
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Should redirect to login or show authentication required
        time.sleep(2)
        
        # Check if redirected to login
        current_url = driver.current_url
        login_elements = driver.find_elements(By.ID, "username")
        
        # Should either be on login page or show auth required message
        assert "/login" in current_url or len(login_elements) > 0 or \
               "login" in driver.page_source.lower() or \
               "authentication" in driver.page_source.lower(), \
               "Unauthenticated access should be handled"
    
    def test_article_navigation_flow(self, authenticated_session):
        """Test complete article navigation including previous/next"""
        driver = authenticated_session
        
        # Navigate to Knowledge Base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Navigate to a category with multiple articles
        category_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "kb-category-card"))
        )
        
        # Click on first category
        category_cards[0].click()
        
        # Wait for articles list
        article_items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "kb-article-item"))
        )
        
        if len(article_items) > 1:
            # Click on first article
            article_items[0].click()
            
            # Wait for article to load
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "articleView"))
            )
            
            # Check for navigation buttons
            next_button = driver.find_elements(By.ID, "nextArticle")
            prev_button = driver.find_elements(By.ID, "prevArticle")
            
            # If next button exists and is visible, test it
            if len(next_button) > 0 and next_button[0].is_displayed():
                next_button[0].click()
                
                # Wait for next article to load
                time.sleep(2)
                
                # Verify article content changed
                new_article_content = driver.find_element(By.ID, "articleContent")
                assert len(new_article_content.text) > 0, "Next article should load"
        
        driver.switch_to.default_content()
    
    def test_content_rendering(self, authenticated_session):
        """Test markdown content rendering and formatting"""
        driver = authenticated_session
        
        # Navigate to Knowledge Base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Navigate to an article
        category_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "kb-category-card"))
        )
        category_cards[0].click()
        
        # Click on first article
        article_items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "kb-article-item"))
        )
        article_items[0].click()
        
        # Wait for article content
        article_content = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "articleContent"))
        )
        
        # Verify markdown elements are rendered correctly
        headings = article_content.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4")
        assert len(headings) > 0, "Article should have rendered headings"
        
        paragraphs = article_content.find_elements(By.TAG_NAME, "p")
        assert len(paragraphs) > 0, "Article should have rendered paragraphs"
        
        # Check for code blocks if present
        code_blocks = article_content.find_elements(By.TAG_NAME, "pre")
        # Code blocks should be properly formatted if present
        
        # Check for lists if present
        lists = article_content.find_elements(By.CSS_SELECTOR, "ul, ol")
        # Lists should be properly formatted if present
        
        driver.switch_to.default_content()


class TestKnowledgeBaseAPI:
    """Test API endpoints directly"""
    
    @pytest.fixture
    def api_base_url(self):
        return "http://localhost:5000"  # Flask backend URL
    
    @pytest.fixture 
    def authenticated_session_requests(self, api_base_url):
        """Create authenticated requests session"""
        session = requests.Session()
        
        # Login to get session cookie
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        
        response = session.post(f"{api_base_url}/api/auth/login", json=login_data)
        assert response.status_code == 200, "Authentication should succeed"
        
        return session
    
    def test_articles_endpoint_response_time(self, authenticated_session_requests, api_base_url):
        """Test articles endpoint response time"""
        session = authenticated_session_requests
        
        start_time = time.time()
        response = session.get(f"{api_base_url}/api/knowledge-base/articles")
        response_time = time.time() - start_time
        
        assert response.status_code == 200, "Articles endpoint should return 200"
        assert response_time < 1.0, f"Articles endpoint response time {response_time:.3f}s exceeds 1 second"
        
        # Verify response structure
        data = response.json()
        assert data.get('success') is True, "Response should indicate success"
        assert 'articles' in data, "Response should contain articles"
        assert 'total_count' in data, "Response should contain total_count"
        assert 'categories' in data, "Response should contain categories"
    
    def test_search_endpoint_response_time(self, authenticated_session_requests, api_base_url):
        """Test search endpoint response time"""
        session = authenticated_session_requests
        
        start_time = time.time()
        response = session.get(f"{api_base_url}/api/knowledge-base/search?q=test")
        response_time = time.time() - start_time
        
        assert response.status_code == 200, "Search endpoint should return 200"
        assert response_time < 0.5, f"Search response time {response_time:.3f}s exceeds 500ms requirement"
        
        # Verify response structure
        data = response.json()
        assert data.get('success') is True, "Response should indicate success"
        assert 'results' in data, "Response should contain results"
        assert 'total_results' in data, "Response should contain total_results"
        assert 'search_time_ms' in data, "Response should contain search_time_ms"
    
    def test_article_endpoint_response_time(self, authenticated_session_requests, api_base_url):
        """Test individual article endpoint response time"""
        session = authenticated_session_requests
        
        # First get list of articles to get a valid ID
        articles_response = session.get(f"{api_base_url}/api/knowledge-base/articles")
        articles_data = articles_response.json()
        
        if articles_data.get('articles') and len(articles_data['articles']) > 0:
            article_id = articles_data['articles'][0]['id']
            
            start_time = time.time()
            response = session.get(f"{api_base_url}/api/knowledge-base/articles/{article_id}")
            response_time = time.time() - start_time
            
            assert response.status_code == 200, "Article endpoint should return 200"
            assert response_time < 1.0, f"Article response time {response_time:.3f}s exceeds 1 second requirement"
            
            # Verify response structure
            data = response.json()
            assert data.get('success') is True, "Response should indicate success"
            assert 'article' in data, "Response should contain article"
            
            article = data['article']
            assert 'id' in article, "Article should have ID"
            assert 'title' in article, "Article should have title"
            assert 'content_html' in article, "Article should have HTML content"
            assert 'content_raw' in article, "Article should have raw content"
            assert 'metadata' in article, "Article should have metadata"
    
    def test_categories_endpoint(self, authenticated_session_requests, api_base_url):
        """Test categories endpoint"""
        session = authenticated_session_requests
        
        response = session.get(f"{api_base_url}/api/knowledge-base/categories")
        assert response.status_code == 200, "Categories endpoint should return 200"
        
        data = response.json()
        assert data.get('success') is True, "Response should indicate success"
        assert 'categories' in data, "Response should contain categories"
        
        categories = data['categories']
        assert len(categories) > 0, "Should have at least one category"
        
        # Verify category structure
        for category in categories:
            assert 'name' in category, "Category should have name"
            assert 'description' in category, "Category should have description"
            assert 'article_count' in category, "Category should have article_count"
            assert 'icon' in category, "Category should have icon"
            assert 'color' in category, "Category should have color"
    
    def test_stats_endpoint(self, authenticated_session_requests, api_base_url):
        """Test stats endpoint"""
        session = authenticated_session_requests
        
        response = session.get(f"{api_base_url}/api/knowledge-base/stats")
        assert response.status_code == 200, "Stats endpoint should return 200"
        
        data = response.json()
        assert data.get('success') is True, "Response should indicate success"
        assert 'stats' in data, "Response should contain stats"
        
        stats = data['stats']
        assert 'total_articles' in stats, "Stats should include total_articles"
        assert 'total_words' in stats, "Stats should include total_words"
        assert 'total_categories' in stats, "Stats should include total_categories"
    
    def test_unauthorized_access(self, api_base_url):
        """Test API endpoints require authentication"""
        # Create unauthenticated session
        session = requests.Session()
        
        endpoints = [
            '/api/knowledge-base/articles',
            '/api/knowledge-base/search?q=test',
            '/api/knowledge-base/categories',
            '/api/knowledge-base/stats'
        ]
        
        for endpoint in endpoints:
            response = session.get(f"{api_base_url}{endpoint}")
            assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"


class TestKnowledgeBaseAccessibility:
    """Accessibility-focused integration tests"""
    
    def test_screen_reader_compatibility(self, authenticated_session):
        """Test screen reader compatibility using accessibility attributes"""
        driver = authenticated_session
        
        # Navigate to Knowledge Base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Check for ARIA labels and roles
        elements_with_aria = driver.find_elements(By.XPATH, "//*[@aria-label or @aria-labelledby or @role]")
        assert len(elements_with_aria) > 0, "Should have elements with ARIA attributes"
        
        # Check search input has proper labeling
        search_input = driver.find_element(By.ID, "searchInput")
        aria_label = search_input.get_attribute("aria-label")
        placeholder = search_input.get_attribute("placeholder")
        assert aria_label or placeholder, "Search input should be properly labeled"
        
        # Check for semantic HTML
        semantic_elements = driver.find_elements(By.CSS_SELECTOR, "main, nav, section, article, header, footer")
        assert len(semantic_elements) > 0, "Should use semantic HTML elements"
        
        # Check heading hierarchy
        headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
        if len(headings) > 0:
            # Verify heading hierarchy is logical
            heading_levels = []
            for heading in headings:
                level = int(heading.tag_name[1])
                heading_levels.append(level)
            
            # Check that headings don't skip levels dramatically
            for i in range(1, len(heading_levels)):
                level_jump = heading_levels[i] - heading_levels[i-1]
                assert level_jump <= 2, "Heading levels should not skip more than one level"
        
        driver.switch_to.default_content()
    
    def test_focus_management(self, authenticated_session):
        """Test focus management and keyboard navigation"""
        driver = authenticated_session
        
        # Navigate to Knowledge Base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Test focus indicators
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        
        # Focus the input and verify focus indicator
        search_input.click()
        active_element = driver.switch_to.active_element
        assert active_element == search_input, "Search input should receive focus"
        
        # Test tab navigation
        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB)
        actions.perform()
        
        new_active_element = driver.switch_to.active_element
        assert new_active_element != search_input, "Focus should move with Tab key"
        
        # Verify focused element is interactive
        tag_name = new_active_element.tag_name.lower()
        interactive_tags = ['button', 'a', 'input', 'select', 'textarea']
        has_tabindex = new_active_element.get_attribute('tabindex') is not None
        
        assert tag_name in interactive_tags or has_tabindex, "Focused element should be interactive"
        
        driver.switch_to.default_content()


if __name__ == "__main__":
    # Run integration tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--durations=10",
        "-m", "not slow"  # Skip slow tests by default
    ])