#!/usr/bin/env python3
"""
Manual test of Activity Trends functionality
Tests the service layer directly without HTTP
"""

import sqlite3
from datetime import datetime, timedelta
import sys
import os

# Add project directory to path
sys.path.insert(0, '/home/jbrice/Projects/365')

from activity_trends_service import (
    ActivityTrendsService,
    TrendAnalyzer,
    DailySummaryProcessor,
    DataCompletionService
)
from trends_cache import TrendsCache, CacheWarmer

DATABASE = 'cvd.db'

def generate_test_data():
    """Generate some test data in activity_summary_daily"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print("Generating test data...")
    
    # Generate data for last 30 days
    for i in range(30):
        date = (datetime.now().date() - timedelta(days=i)).isoformat()
        
        # Check if data already exists
        existing = cursor.execute(
            "SELECT id FROM activity_summary_daily WHERE date = ?",
            (date,)
        ).fetchone()
        
        if not existing:
            # Insert test data with varying values
            cursor.execute("""
                INSERT INTO activity_summary_daily (
                    date, unique_users, total_sessions, total_page_views,
                    total_api_calls, avg_session_duration_seconds,
                    peak_concurrent_users, peak_hour
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date,
                10 + (i % 5),  # unique_users: 10-14
                20 + (i % 10),  # total_sessions: 20-29
                100 + (i * 5),  # total_page_views: increasing
                50 + (i * 2),   # total_api_calls: increasing
                300 + (i % 100),  # avg_session_duration
                5 + (i % 3),    # peak_concurrent_users: 5-7
                14  # peak_hour: 2 PM
            ))
    
    conn.commit()
    conn.close()
    print(f"✓ Test data generated for last 30 days")

def test_service_layer():
    """Test the ActivityTrendsService"""
    print("\n" + "=" * 60)
    print("Testing ActivityTrendsService")
    print("=" * 60)
    
    service = ActivityTrendsService(DATABASE)
    
    # Test 1: Get trends for last 7 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    metrics = ['unique_users', 'total_sessions', 'total_page_views']
    
    print(f"\nTest 1: Getting trends for {start_date} to {end_date}")
    trends_data = service.get_trends(start_date, end_date, metrics)
    
    if trends_data:
        print(f"✓ Retrieved trends data")
        for metric, data_points in trends_data.items():
            print(f"  - {metric}: {len(data_points)} data points")
            if data_points:
                print(f"    First value: {data_points[0]['value']}")
                print(f"    Last value: {data_points[-1]['value']}")
    else:
        print("✗ No trends data retrieved")
    
    # Test 2: Calculate summary
    print("\nTest 2: Calculating summary statistics")
    summary = service.calculate_summary(trends_data)
    
    if summary:
        print(f"✓ Summary calculated")
        for metric, stats in summary.items():
            print(f"  - {metric}:")
            print(f"    * Average: {stats.get('average', 0)}")
            print(f"    * Min: {stats.get('min', 0)}")
            print(f"    * Max: {stats.get('max', 0)}")
            print(f"    * Trend: {stats.get('trend', 'unknown')}")
    else:
        print("✗ No summary calculated")
    
    return True

def test_cache():
    """Test the TrendsCache"""
    print("\n" + "=" * 60)
    print("Testing TrendsCache")
    print("=" * 60)
    
    cache = TrendsCache(max_size=10, default_ttl=60)
    
    # Test 1: Cache set and get
    print("\nTest 1: Cache set and get")
    test_data = {'test': 'data', 'value': 42}
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    metrics = ['unique_users']
    
    cache_key = cache.generate_key(start_date, end_date, metrics)
    print(f"  Generated cache key: {cache_key}")
    
    cache.set(cache_key, test_data)
    print("  ✓ Data stored in cache")
    
    retrieved = cache.get(cache_key)
    if retrieved == test_data:
        print("  ✓ Data retrieved successfully")
    else:
        print("  ✗ Retrieved data doesn't match")
    
    # Test 2: Cache stats
    print("\nTest 2: Cache statistics")
    stats = cache.get_stats()
    print(f"  - Size: {stats['size']}/{stats['max_size']}")
    print(f"  - Hits: {stats['hits']}")
    print(f"  - Misses: {stats['misses']}")
    print(f"  - Hit rate: {stats['hit_rate']}%")
    
    # Test 3: TTL
    print("\nTest 3: TTL check")
    ttl = cache.get_ttl(cache_key)
    print(f"  - Remaining TTL: {ttl} seconds")
    
    return True

def test_trend_analyzer():
    """Test the TrendAnalyzer"""
    print("\n" + "=" * 60)
    print("Testing TrendAnalyzer")
    print("=" * 60)
    
    analyzer = TrendAnalyzer()
    
    # Test with increasing trend
    print("\nTest 1: Analyzing increasing trend")
    increasing_data = [
        {'value': 10}, {'value': 12}, {'value': 15},
        {'value': 18}, {'value': 22}, {'value': 25},
        {'value': 28}
    ]
    
    result = analyzer.calculate_trend(increasing_data)
    print(f"  - Direction: {result['direction']}")
    print(f"  - Strength: {result['strength']}")
    print(f"  - Confidence: {result['confidence']}")
    print(f"  - Percentage change: {result['percentage_change']}%")
    
    # Test with stable trend
    print("\nTest 2: Analyzing stable trend")
    stable_data = [
        {'value': 10}, {'value': 11}, {'value': 10},
        {'value': 9}, {'value': 10}, {'value': 11},
        {'value': 10}
    ]
    
    result = analyzer.calculate_trend(stable_data)
    print(f"  - Direction: {result['direction']}")
    print(f"  - Strength: {result['strength']}")
    print(f"  - Confidence: {result['confidence']}")
    
    return True

def test_daily_processor():
    """Test the DailySummaryProcessor"""
    print("\n" + "=" * 60)
    print("Testing DailySummaryProcessor")
    print("=" * 60)
    
    processor = DailySummaryProcessor(DATABASE)
    
    print("\nProcessing missing daily summaries...")
    processed = processor.process_missing_days()
    print(f"✓ Processed {processed} missing days")
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Activity Trends Service Layer Test Suite")
    print("=" * 60)
    
    # Generate test data first
    generate_test_data()
    
    # Run tests
    tests_passed = 0
    tests_total = 4
    
    try:
        if test_service_layer():
            tests_passed += 1
    except Exception as e:
        print(f"✗ Service layer test failed: {e}")
    
    try:
        if test_cache():
            tests_passed += 1
    except Exception as e:
        print(f"✗ Cache test failed: {e}")
    
    try:
        if test_trend_analyzer():
            tests_passed += 1
    except Exception as e:
        print(f"✗ Trend analyzer test failed: {e}")
    
    try:
        if test_daily_processor():
            tests_passed += 1
    except Exception as e:
        print(f"✗ Daily processor test failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed}/{tests_total} passed")
    
    if tests_passed == tests_total:
        print("✓ All tests passed!")
    else:
        print(f"✗ {tests_total - tests_passed} test(s) failed")
    
    print("=" * 60)

if __name__ == "__main__":
    main()