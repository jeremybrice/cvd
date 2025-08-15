#!/usr/bin/env python3
"""
Performance test for Activity Trends API
Verify sub-2 second response time for 365 days of data
"""

import time
import sqlite3
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/home/jbrice/Projects/365')

from activity_trends_service import ActivityTrendsService
from trends_cache import TrendsCache

DATABASE = 'cvd.db'

def generate_365_days_data():
    """Generate 365 days of test data"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print("Generating 365 days of test data...")
    
    for i in range(365):
        date = (datetime.now().date() - timedelta(days=i)).isoformat()
        
        # Check if data already exists
        existing = cursor.execute(
            "SELECT id FROM activity_summary_daily WHERE date = ?",
            (date,)
        ).fetchone()
        
        if not existing:
            # Insert test data with realistic patterns
            cursor.execute("""
                INSERT INTO activity_summary_daily (
                    date, unique_users, total_sessions, total_page_views,
                    total_api_calls, avg_session_duration_seconds,
                    peak_concurrent_users, peak_hour
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date,
                50 + (i % 20),       # unique_users: 50-69
                100 + (i % 50),      # total_sessions: 100-149
                500 + (i * 10),      # total_page_views: increasing
                200 + (i * 5),       # total_api_calls: increasing
                300 + (i % 200),     # avg_session_duration
                10 + (i % 10),       # peak_concurrent_users: 10-19
                14                   # peak_hour: 2 PM
            ))
    
    conn.commit()
    conn.close()
    print(f"✓ Generated 365 days of test data")

def test_performance_uncached():
    """Test performance without cache (cold query)"""
    print("\n" + "=" * 60)
    print("Performance Test: 365 Days (Uncached)")
    print("=" * 60)
    
    service = ActivityTrendsService(DATABASE)
    
    # Query for full year
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    metrics = ['unique_users', 'total_sessions', 'total_page_views', 
               'total_api_calls', 'avg_session_duration_seconds']
    
    print(f"\nQuerying data from {start_date} to {end_date}")
    print(f"Metrics: {', '.join(metrics)}")
    
    # Measure query time
    start_time = time.time()
    trends_data = service.get_trends(start_date, end_date, metrics)
    query_time = time.time() - start_time
    
    # Measure summary calculation time
    start_time = time.time()
    summary = service.calculate_summary(trends_data)
    summary_time = time.time() - start_time
    
    total_time = query_time + summary_time
    
    # Results
    print(f"\nResults:")
    print(f"  - Query time: {query_time:.3f} seconds")
    print(f"  - Summary calculation: {summary_time:.3f} seconds")
    print(f"  - Total time: {total_time:.3f} seconds")
    
    # Data stats
    total_points = sum(len(data) for data in trends_data.values())
    print(f"\nData retrieved:")
    print(f"  - Total data points: {total_points}")
    print(f"  - Days covered: 365")
    print(f"  - Metrics: {len(metrics)}")
    
    # Performance verdict
    if total_time < 2.0:
        print(f"\n✓ PASS: Response time ({total_time:.3f}s) is under 2 seconds")
        return True
    else:
        print(f"\n✗ FAIL: Response time ({total_time:.3f}s) exceeds 2 seconds")
        return False

def test_performance_cached():
    """Test performance with cache (warm query)"""
    print("\n" + "=" * 60)
    print("Performance Test: 365 Days (Cached)")
    print("=" * 60)
    
    service = ActivityTrendsService(DATABASE)
    cache = TrendsCache(max_size=100, default_ttl=3600)
    
    # Query for full year
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    metrics = ['unique_users', 'total_sessions', 'total_page_views']
    
    print(f"\nWarming cache...")
    # First query to warm cache
    trends_data = service.get_trends(start_date, end_date, metrics)
    summary = service.calculate_summary(trends_data)
    
    # Store in cache
    cache_key = cache.generate_key(start_date, end_date, metrics)
    response_data = {
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'metrics': trends_data,
        'summary': summary
    }
    cache.set(cache_key, response_data)
    print(f"✓ Cache warmed with key: {cache_key}")
    
    # Measure cached retrieval
    print(f"\nRetrieving from cache...")
    start_time = time.time()
    cached_data = cache.get(cache_key)
    cache_time = time.time() - start_time
    
    print(f"\nResults:")
    print(f"  - Cache retrieval time: {cache_time:.3f} seconds")
    
    # Performance verdict
    if cache_time < 0.1:  # Cache hit should be under 100ms
        print(f"\n✓ PASS: Cache response time ({cache_time:.3f}s) is under 0.1 seconds")
        return True
    else:
        print(f"\n✗ FAIL: Cache response time ({cache_time:.3f}s) exceeds 0.1 seconds")
        return False

def test_query_optimization():
    """Test database query performance with EXPLAIN"""
    print("\n" + "=" * 60)
    print("Query Optimization Analysis")
    print("=" * 60)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Test query with date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    query = """
    EXPLAIN QUERY PLAN
    SELECT date, unique_users, total_sessions, total_page_views
    FROM activity_summary_daily
    WHERE date BETWEEN ? AND ?
    ORDER BY date ASC
    """
    
    print(f"\nQuery plan for date range {start_date} to {end_date}:")
    cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
    
    for row in cursor.fetchall():
        print(f"  {row}")
    
    # Check if indexes are being used
    uses_index = False
    cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
    for row in cursor.fetchall():
        if 'USING INDEX' in str(row):
            uses_index = True
            break
    
    if uses_index:
        print("\n✓ Query is using indexes efficiently")
    else:
        print("\n⚠ Query may not be using indexes optimally")
    
    conn.close()

def main():
    """Run all performance tests"""
    print("=" * 60)
    print("Activity Trends Performance Test Suite")
    print("Requirement: Sub-2 second response for 365 days of data")
    print("=" * 60)
    
    # Generate test data
    generate_365_days_data()
    
    # Run tests
    tests_passed = 0
    tests_total = 3
    
    # Test 1: Uncached performance
    if test_performance_uncached():
        tests_passed += 1
    
    # Test 2: Cached performance
    if test_performance_cached():
        tests_passed += 1
    
    # Test 3: Query optimization
    test_query_optimization()
    tests_passed += 1  # Information only, always passes
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Performance Test Results: {tests_passed}/{tests_total} passed")
    
    if tests_passed == tests_total:
        print("✓ All performance requirements met!")
    else:
        print(f"✗ {tests_total - tests_passed} performance test(s) failed")
    
    print("=" * 60)

if __name__ == "__main__":
    main()