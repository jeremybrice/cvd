"""
Knowledge Base Performance Test Suite
Tests performance requirements and benchmarks
Validates load times, search performance, and resource usage
"""

import pytest
import time
import threading
import concurrent.futures
import psutil
import json
import tempfile
from pathlib import Path
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class TestKnowledgeBasePerformance:
    """Performance tests for Knowledge Base functionality"""
    
    @pytest.fixture(scope="class")
    def headless_driver(self):
        """Setup headless Chrome for performance testing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-images")  # Disable images for performance testing
        chrome_options.add_argument("--disable-javascript")  # Test with JS disabled first
        
        driver = webdriver.Chrome(options=chrome_options)
        yield driver
        driver.quit()
    
    @pytest.fixture
    def performance_driver(self):
        """Setup Chrome with performance logging"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Enable performance logging
        chrome_options.add_experimental_option('perfLoggingPrefs', {
            'enableNetwork': True,
            'enablePage': True,
            'enableTimeline': True
        })
        chrome_options.add_experimental_option('loggingPrefs', {
            'performance': 'ALL'
        })
        
        driver = webdriver.Chrome(options=chrome_options)
        yield driver
        driver.quit()
    
    @pytest.fixture
    def authenticated_performance_session(self, performance_driver):
        """Create authenticated session for performance testing"""
        driver = performance_driver
        
        # Login
        driver.get("http://localhost:8000/")
        
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            username_field = driver.find_element(By.ID, "username")
            password_field = driver.find_element(By.ID, "password")
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            username_field.send_keys("admin")
            password_field.send_keys("admin")
            login_button.click()
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "nav"))
            )
        except:
            pass  # May already be logged in or login not required
        
        return driver
    
    def test_page_load_performance_requirement(self, authenticated_performance_session):
        """Test: Page load time must be < 2 seconds (Technical Plan requirement)"""
        driver = authenticated_performance_session
        
        # Clear any existing performance logs
        driver.get_log('performance')
        
        # Measure knowledge base load time
        start_time = time.time()
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Wait for iframe to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        
        # Switch to iframe and wait for content to load
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)
        
        # Wait for categories to load (indicating full initialization)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "kb-category-card"))
        )
        
        load_time = time.time() - start_time
        
        # Technical Plan requirement: < 2 seconds
        assert load_time < 2.0, f"Page load time {load_time:.2f}s exceeds 2 second requirement"
        
        # Get performance metrics from browser
        logs = driver.get_log('performance')
        navigation_times = self.extract_navigation_timing(logs)
        
        if navigation_times:
            dom_complete = navigation_times.get('domComplete', 0)
            load_event_end = navigation_times.get('loadEventEnd', 0)
            
            print(f"Performance Metrics:")
            print(f"  Total Load Time: {load_time:.2f}s")
            print(f"  DOM Complete: {dom_complete:.2f}ms")
            print(f"  Load Event End: {load_event_end:.2f}ms")
        
        driver.switch_to.default_content()
        return load_time
    
    def test_search_performance_requirement(self, authenticated_performance_session):
        """Test: Search response time must be < 500ms (Technical Plan requirement)"""
        driver = authenticated_performance_session
        
        # Navigate to knowledge base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Wait for page to fully load
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        
        # Test multiple search queries for average performance
        search_queries = [
            "getting started",
            "planogram",
            "troubleshooting",
            "device configuration",
            "user management"
        ]
        
        search_times = []
        
        for query in search_queries:
            search_input.clear()
            
            # Measure search response time
            start_time = time.time()
            search_input.send_keys(query)
            
            # Wait for search results or timeout
            try:
                WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located((By.ID, "searchResults"))
                )
                search_time = time.time() - start_time
                search_times.append(search_time)
            except:
                # Search may not complete in test environment
                search_time = time.time() - start_time
                search_times.append(search_time)
            
            # Clear search for next test
            search_input.clear()
            time.sleep(0.5)
        
        if search_times:
            avg_search_time = sum(search_times) / len(search_times)
            max_search_time = max(search_times)
            
            print(f"Search Performance:")
            print(f"  Average: {avg_search_time:.3f}s")
            print(f"  Maximum: {max_search_time:.3f}s")
            print(f"  Individual times: {[f'{t:.3f}s' for t in search_times]}")
            
            # Technical Plan requirement: < 500ms
            assert avg_search_time < 0.5, f"Average search time {avg_search_time:.3f}s exceeds 500ms requirement"
            assert max_search_time < 1.0, f"Maximum search time {max_search_time:.3f}s exceeds reasonable limit"
        
        driver.switch_to.default_content()
        return search_times
    
    def test_article_loading_performance(self, authenticated_performance_session):
        """Test: Article loading time must be < 1 second (Technical Plan requirement)"""
        driver = authenticated_performance_session
        
        # Navigate to knowledge base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Switch to iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # Navigate to a category
        category_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "kb-category-card"))
        )
        
        if len(category_cards) > 0:
            category_cards[0].click()
            
            # Wait for articles list
            article_items = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "kb-article-item"))
            )
            
            article_load_times = []
            
            # Test loading first few articles
            for i, article_item in enumerate(article_items[:3]):  # Test first 3 articles
                start_time = time.time()
                article_item.click()
                
                # Wait for article content to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "articleContent"))
                )
                
                # Wait for content to be populated
                article_content = driver.find_element(By.ID, "articleContent")
                WebDriverWait(driver, 10).until(
                    lambda d: len(article_content.text) > 0
                )
                
                load_time = time.time() - start_time
                article_load_times.append(load_time)
                
                print(f"Article {i+1} load time: {load_time:.3f}s")
                
                # Navigate back to articles list
                back_button = driver.find_element(By.ID, "articleBackButton")
                back_button.click()
                
                # Wait for articles list to reappear
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "articleListView"))
                )
                
                time.sleep(0.5)  # Brief pause between tests
            
            if article_load_times:
                avg_load_time = sum(article_load_times) / len(article_load_times)
                max_load_time = max(article_load_times)
                
                print(f"Article Loading Performance:")
                print(f"  Average: {avg_load_time:.3f}s")
                print(f"  Maximum: {max_load_time:.3f}s")
                
                # Technical Plan requirement: < 1 second
                assert avg_load_time < 1.0, f"Average article load time {avg_load_time:.3f}s exceeds 1 second requirement"
                assert max_load_time < 2.0, f"Maximum article load time {max_load_time:.3f}s exceeds reasonable limit"
        
        driver.switch_to.default_content()
    
    def test_memory_usage_requirement(self, authenticated_performance_session):
        """Test: Memory usage should be < 50MB additional (Technical Plan requirement)"""
        driver = authenticated_performance_session
        
        # Get baseline memory usage
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Navigate to knowledge base multiple times to test memory leaks
        for i in range(5):
            driver.get("http://localhost:8000/#knowledge-base")
            
            # Switch to iframe
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            driver.switch_to.frame(iframe)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "kb-category-card"))
            )
            
            # Perform some interactions
            search_input = driver.find_element(By.ID, "searchInput")
            search_input.send_keys(f"test query {i}")
            time.sleep(1)
            search_input.clear()
            
            driver.switch_to.default_content()
            time.sleep(1)
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - baseline_memory
        
        print(f"Memory Usage:")
        print(f"  Baseline: {baseline_memory:.1f}MB")
        print(f"  Final: {final_memory:.1f}MB") 
        print(f"  Increase: {memory_increase:.1f}MB")
        
        # Technical Plan requirement: < 50MB additional
        assert memory_increase < 50.0, f"Memory usage increase {memory_increase:.1f}MB exceeds 50MB limit"
        
        # Check for potential memory leaks (should not increase significantly with repeated use)
        assert memory_increase < 100.0, f"Potential memory leak detected: {memory_increase:.1f}MB increase"
    
    def test_concurrent_user_performance(self):
        """Test performance under concurrent user load"""
        api_base_url = "http://localhost:5000"
        
        # Create multiple concurrent requests to simulate load
        def make_request(endpoint):
            session = requests.Session()
            # Login first
            login_data = {'username': 'admin', 'password': 'admin'}
            try:
                session.post(f"{api_base_url}/api/auth/login", json=login_data, timeout=5)
                
                start_time = time.time()
                response = session.get(f"{api_base_url}{endpoint}", timeout=5)
                response_time = time.time() - start_time
                
                return {
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'endpoint': endpoint,
                    'status_code': 0,
                    'response_time': 5.0,  # Timeout
                    'success': False,
                    'error': str(e)
                }
        
        endpoints = [
            '/api/knowledge-base/articles',
            '/api/knowledge-base/categories',
            '/api/knowledge-base/search?q=test',
            '/api/knowledge-base/stats'
        ]
        
        # Test with 10 concurrent requests per endpoint
        concurrent_requests = []
        for endpoint in endpoints:
            for i in range(10):
                concurrent_requests.append(endpoint)
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_endpoint = {
                executor.submit(make_request, endpoint): endpoint 
                for endpoint in concurrent_requests
            }
            
            for future in concurrent.futures.as_completed(future_to_endpoint):
                result = future.result()
                results.append(result)
        
        # Analyze results
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        if successful_requests:
            avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
            max_response_time = max(r['response_time'] for r in successful_requests)
            
            print(f"Concurrent Load Test Results:")
            print(f"  Total Requests: {len(results)}")
            print(f"  Successful: {len(successful_requests)}")
            print(f"  Failed: {len(failed_requests)}")
            print(f"  Success Rate: {len(successful_requests)/len(results)*100:.1f}%")
            print(f"  Average Response Time: {avg_response_time:.3f}s")
            print(f"  Maximum Response Time: {max_response_time:.3f}s")
            
            # Performance requirements under load
            success_rate = len(successful_requests) / len(results)
            assert success_rate >= 0.95, f"Success rate {success_rate:.2%} below 95% requirement"
            assert avg_response_time < 2.0, f"Average response time {avg_response_time:.3f}s exceeds 2s under load"
        else:
            pytest.skip("No successful requests - server may not be running")
    
    def test_large_dataset_performance(self):
        """Test performance with large knowledge base content"""
        # This would test with a large number of articles
        # For now, we'll simulate by testing search performance with complex queries
        
        # Create temporary large content for testing
        large_content_dir = Path("/tmp/large_kb_test")
        large_content_dir.mkdir(exist_ok=True)
        
        try:
            # Create 100 test articles
            for i in range(100):
                article_content = f"""---
title: "Test Article {i+1}"
author: "Test Author"
category: "Test Category {(i % 5) + 1}"
tags: ["test", "performance", "article{i+1}"]
difficulty: "{'Beginner' if i % 3 == 0 else 'Intermediate' if i % 3 == 1 else 'Advanced'}"
description: "Performance test article {i+1}"
---

# Test Article {i+1}

This is a performance test article with substantial content to test search and loading performance.

## Section 1
{'Lorem ipsum dolor sit amet, consectetur adipiscing elit. ' * 20}

## Section 2
{'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ' * 15}

## Section 3
{'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris. ' * 10}

## Performance Testing Content
This article contains keyword: performance_test_keyword_{i+1}
Search relevance testing with specific terms.
"""
                
                article_file = large_content_dir / f"test-article-{i+1}.md"
                article_file.write_text(article_content)
            
            # Test the knowledge base service with large dataset
            from services.knowledge_base_service import KnowledgeBaseService
            
            service = KnowledgeBaseService(content_path=str(large_content_dir))
            
            # Test article scanning performance
            start_time = time.time()
            articles = service.scan_articles()
            scan_time = time.time() - start_time
            
            assert len(articles) == 100, "Should load all 100 test articles"
            assert scan_time < 5.0, f"Article scanning took {scan_time:.3f}s, should be under 5 seconds"
            
            # Test search performance with large dataset
            search_queries = [
                "performance",
                "test article",
                "lorem ipsum",
                "performance_test_keyword_50"
            ]
            
            search_times = []
            for query in search_queries:
                start_time = time.time()
                results = service.search_articles(query)
                search_time = time.time() - start_time
                search_times.append(search_time)
                
                print(f"Search '{query}': {len(results)} results in {search_time:.3f}s")
            
            avg_search_time = sum(search_times) / len(search_times)
            max_search_time = max(search_times)
            
            print(f"Large Dataset Search Performance:")
            print(f"  Dataset Size: {len(articles)} articles")
            print(f"  Average Search Time: {avg_search_time:.3f}s")
            print(f"  Maximum Search Time: {max_search_time:.3f}s")
            
            # Should maintain performance with large dataset
            assert avg_search_time < 1.0, f"Average search time {avg_search_time:.3f}s too slow for large dataset"
            assert max_search_time < 2.0, f"Maximum search time {max_search_time:.3f}s too slow for large dataset"
            
        finally:
            # Cleanup
            import shutil
            if large_content_dir.exists():
                shutil.rmtree(large_content_dir)
    
    def test_browser_performance_metrics(self, authenticated_performance_session):
        """Test Core Web Vitals and browser performance metrics"""
        driver = authenticated_performance_session
        
        # Navigate to knowledge base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Wait for page to load completely
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        
        # Get performance timing data
        performance_script = """
        return {
            navigation: performance.getEntriesByType('navigation')[0],
            paint: performance.getEntriesByType('paint'),
            memory: performance.memory ? {
                usedJSHeapSize: performance.memory.usedJSHeapSize,
                totalJSHeapSize: performance.memory.totalJSHeapSize,
                jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
            } : null,
            timing: performance.timing
        };
        """
        
        perf_data = driver.execute_script(performance_script)
        
        if perf_data['navigation']:
            nav = perf_data['navigation']
            dom_content_loaded = nav.get('domContentLoadedEventEnd', 0) - nav.get('domContentLoadedEventStart', 0)
            load_complete = nav.get('loadEventEnd', 0) - nav.get('loadEventStart', 0)
            
            print(f"Browser Performance Metrics:")
            print(f"  DOM Content Loaded: {dom_content_loaded:.0f}ms")
            print(f"  Load Complete: {load_complete:.0f}ms")
            
            # Core Web Vitals targets
            assert dom_content_loaded < 1500, f"DOM Content Loaded {dom_content_loaded:.0f}ms exceeds 1.5s target"
        
        if perf_data['paint']:
            paint_times = {entry['name']: entry['startTime'] for entry in perf_data['paint']}
            
            if 'first-paint' in paint_times:
                fp = paint_times['first-paint']
                print(f"  First Paint: {fp:.0f}ms")
                assert fp < 1000, f"First Paint {fp:.0f}ms exceeds 1s target"
            
            if 'first-contentful-paint' in paint_times:
                fcp = paint_times['first-contentful-paint']
                print(f"  First Contentful Paint: {fcp:.0f}ms")
                assert fcp < 1500, f"First Contentful Paint {fcp:.0f}ms exceeds 1.5s target"
        
        if perf_data['memory']:
            memory = perf_data['memory']
            used_mb = memory['usedJSHeapSize'] / 1024 / 1024
            total_mb = memory['totalJSHeapSize'] / 1024 / 1024
            
            print(f"  JS Heap Used: {used_mb:.1f}MB")
            print(f"  JS Heap Total: {total_mb:.1f}MB")
            
            assert used_mb < 50, f"JS Heap usage {used_mb:.1f}MB exceeds 50MB limit"
    
    def test_network_performance(self, authenticated_performance_session):
        """Test network request performance and efficiency"""
        driver = authenticated_performance_session
        
        # Clear performance logs
        driver.get_log('performance')
        
        # Navigate to knowledge base
        driver.get("http://localhost:8000/#knowledge-base")
        
        # Wait for page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        
        # Get network performance logs
        logs = driver.get_log('performance')
        
        network_events = []
        for log in logs:
            message = json.loads(log['message'])
            if message['message']['method'] in ['Network.requestWillBeSent', 'Network.responseReceived']:
                network_events.append(message['message'])
        
        # Analyze network requests
        requests_by_type = {}
        total_size = 0
        
        for event in network_events:
            if event['method'] == 'Network.responseReceived':
                response = event['params']['response']
                url = response['url']
                mime_type = response.get('mimeType', 'unknown')
                
                # Categorize requests
                if mime_type.startswith('text/html'):
                    req_type = 'HTML'
                elif mime_type.startswith('text/css'):
                    req_type = 'CSS'
                elif mime_type.startswith('application/javascript') or mime_type.startswith('text/javascript'):
                    req_type = 'JavaScript'
                elif mime_type.startswith('image/'):
                    req_type = 'Image'
                elif 'api' in url:
                    req_type = 'API'
                else:
                    req_type = 'Other'
                
                requests_by_type[req_type] = requests_by_type.get(req_type, 0) + 1
                
                # Track response size if available
                if 'encodedDataLength' in response:
                    total_size += response['encodedDataLength']
        
        print(f"Network Performance:")
        print(f"  Total Requests: {sum(requests_by_type.values())}")
        for req_type, count in requests_by_type.items():
            print(f"  {req_type}: {count} requests")
        
        if total_size > 0:
            print(f"  Total Transfer Size: {total_size / 1024:.1f}KB")
            
            # Performance requirements
            assert total_size < 2 * 1024 * 1024, f"Total transfer size {total_size / 1024:.1f}KB exceeds 2MB"
        
        # API requests should be minimal for initial load
        api_requests = requests_by_type.get('API', 0)
        assert api_requests <= 5, f"Too many API requests ({api_requests}) for initial load"
    
    def extract_navigation_timing(self, performance_logs):
        """Extract navigation timing from performance logs"""
        for log in performance_logs:
            message = json.loads(log['message'])
            if (message['message']['method'] == 'Runtime.evaluate' and 
                'navigationStart' in str(message)):
                # Extract timing data
                return {}  # Simplified for now
        return {}


class TestKnowledgeBaseScalability:
    """Test scalability with various content sizes"""
    
    def test_scalability_benchmarks(self):
        """Test performance scaling with different content volumes"""
        from services.knowledge_base_service import KnowledgeBaseService
        
        # Test with different article counts
        article_counts = [10, 50, 100, 500]
        results = {}
        
        for count in article_counts:
            # Create temporary content directory
            temp_dir = Path(f"/tmp/kb_scale_test_{count}")
            temp_dir.mkdir(exist_ok=True)
            
            try:
                # Generate test articles
                for i in range(count):
                    content = f"""---
title: "Scale Test Article {i+1}"
author: "Test Author"
category: "Category {(i % 10) + 1}"
tags: ["scale", "test", "article{i}"]
difficulty: "{'Beginner' if i % 3 == 0 else 'Intermediate' if i % 3 == 1 else 'Advanced'}"
description: "Scale test article {i+1}"
---

# Scale Test Article {i+1}

Content for scaling test with keyword: scale_test_{i}

{'Lorem ipsum content. ' * (50 + i % 100)}
"""
                    
                    article_file = temp_dir / f"scale-test-{i+1}.md"
                    article_file.write_text(content)
                
                # Test service performance
                service = KnowledgeBaseService(content_path=str(temp_dir))
                
                # Measure scan time
                start_time = time.time()
                articles = service.scan_articles()
                scan_time = time.time() - start_time
                
                # Measure search time
                start_time = time.time()
                search_results = service.search_articles("scale test")
                search_time = time.time() - start_time
                
                results[count] = {
                    'scan_time': scan_time,
                    'search_time': search_time,
                    'articles_found': len(articles),
                    'search_results': len(search_results)
                }
                
                print(f"Scale Test - {count} articles:")
                print(f"  Scan Time: {scan_time:.3f}s")
                print(f"  Search Time: {search_time:.3f}s")
                print(f"  Articles Found: {len(articles)}")
                print(f"  Search Results: {len(search_results)}")
                
            finally:
                # Cleanup
                import shutil
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
        
        # Verify scaling is reasonable
        for count in article_counts:
            if count > 10:
                prev_count = max([c for c in article_counts if c < count])
                
                scan_ratio = results[count]['scan_time'] / results[prev_count]['scan_time']
                count_ratio = count / prev_count
                
                # Scan time should scale reasonably (not exponentially)
                assert scan_ratio <= count_ratio * 2, f"Scan time scaling too steep: {scan_ratio:.2f}x for {count_ratio:.2f}x content"
                
                search_ratio = results[count]['search_time'] / results[prev_count]['search_time']
                
                # Search time should scale reasonably
                assert search_ratio <= count_ratio * 1.5, f"Search time scaling too steep: {search_ratio:.2f}x for {count_ratio:.2f}x content"
        
        return results


if __name__ == "__main__":
    # Run performance tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure for performance tests
        "--durations=0"  # Show all test durations
    ])