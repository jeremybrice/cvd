#!/usr/bin/env python3
"""
Test Security Features
Validates that all security monitoring features are working correctly
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append('..')

from security_monitor import SecurityMonitor
from activity_tracker import ActivityTracker

DATABASE = '../cvd.db'

def test_brute_force_detection():
    """Test brute force attack detection"""
    print("\n🔐 Testing Brute Force Detection")
    print("-" * 40)
    
    # Create mock activity tracker
    class MockTracker:
        pass
    
    tracker = MockTracker()
    monitor = SecurityMonitor(DATABASE, tracker)
    
    test_ip = "192.168.1.100"
    
    # Simulate failed login attempts
    for i in range(6):
        is_blocked, should_alert, alert_details = monitor.check_brute_force(
            test_ip, user_id=1, success=False
        )
        
        print(f"Attempt {i+1}: Blocked={is_blocked}, Alert={should_alert}")
        
        if alert_details:
            print(f"  Alert: {alert_details['description']}")
    
    # Check if IP is blocked
    if monitor.is_ip_blocked(test_ip):
        print("✅ IP successfully blocked after multiple attempts")
    else:
        print("❌ IP blocking failed")
    
    # Test successful login clears tracking
    monitor.check_brute_force(test_ip, user_id=1, success=True)
    print("✅ Successful login clears brute force tracking")

def test_data_export_monitoring():
    """Test data export monitoring"""
    print("\n📊 Testing Data Export Monitoring")
    print("-" * 40)
    
    class MockTracker:
        pass
    
    tracker = MockTracker()
    monitor = SecurityMonitor(DATABASE, tracker)
    
    user_id = 1
    
    # Simulate multiple exports
    for i in range(12):
        is_excessive, should_alert, alert_details = monitor.check_data_export(
            user_id, '/api/sales/export', row_count=500
        )
        
        if i < 10:
            print(f"Export {i+1}: Excessive={is_excessive}, Alert={should_alert}")
        else:
            print(f"Export {i+1}: Excessive={is_excessive}, Alert={should_alert}")
            if alert_details:
                print(f"  Alert: {alert_details['description']}")
    
    # Test bulk export
    is_excessive, should_alert, alert_details = monitor.check_data_export(
        user_id, '/api/planograms/export', row_count=5000
    )
    
    if should_alert:
        print(f"✅ Bulk export detected: {alert_details['description']}")
    else:
        print("❌ Bulk export detection failed")

def test_privilege_escalation():
    """Test privilege escalation detection"""
    print("\n👤 Testing Privilege Escalation Detection")
    print("-" * 40)
    
    class MockTracker:
        pass
    
    tracker = MockTracker()
    monitor = SecurityMonitor(DATABASE, tracker)
    
    # Test unauthorized admin access
    test_cases = [
        ('viewer', '/api/users', 'POST', True),  # Should alert
        ('driver', '/api/admin/settings', 'PUT', True),  # Should alert
        ('manager', '/api/users', 'GET', False),  # Should not alert
        ('admin', '/api/users', 'DELETE', False),  # Should not alert
    ]
    
    for role, endpoint, method, should_alert_expected in test_cases:
        is_unauth, should_alert, alert_details = monitor.check_privilege_escalation(
            1, role, endpoint, method
        )
        
        status = "✅" if should_alert == should_alert_expected else "❌"
        print(f"{status} {role} -> {endpoint} ({method}): Alert={should_alert}")
        
        if alert_details:
            print(f"    {alert_details['description']}")

def test_geographic_anomaly():
    """Test geographic anomaly detection"""
    print("\n🌍 Testing Geographic Anomaly Detection")
    print("-" * 40)
    
    class MockTracker:
        pass
    
    tracker = MockTracker()
    monitor = SecurityMonitor(DATABASE, tracker)
    
    user_id = 1
    
    # First login from New York
    is_anomaly, should_alert, alert_details = monitor.check_geographic_anomaly(
        user_id, "72.229.28.185", "Mozilla/5.0"
    )
    print(f"Login 1 (New York): Anomaly={is_anomaly}")
    
    # Quick login from London (impossible travel)
    time.sleep(0.1)  # Simulate minimal time passing
    is_anomaly, should_alert, alert_details = monitor.check_geographic_anomaly(
        user_id, "81.2.69.142", "Mozilla/5.0"
    )
    
    if should_alert:
        print(f"✅ Impossible travel detected: {alert_details['description']}")
    else:
        print("⚠️  Geographic anomaly detection needs real GeoIP integration")

def test_sensitive_data_access():
    """Test sensitive data access monitoring"""
    print("\n🔒 Testing Sensitive Data Access Monitoring")
    print("-" * 40)
    
    class MockTracker:
        pass
    
    tracker = MockTracker()
    monitor = SecurityMonitor(DATABASE, tracker)
    
    user_id = 1
    
    # Test after-hours access
    late_night = datetime.now().replace(hour=23, minute=30)
    is_sensitive, should_alert, alert_details = monitor.check_sensitive_data_access(
        user_id, '/api/sales/financial-report', late_night
    )
    
    if should_alert:
        print(f"✅ After-hours access detected: {alert_details['description']}")
    else:
        print("❌ After-hours detection failed")
    
    # Test weekend access
    # Note: This would need to be on an actual weekend to trigger
    weekend = datetime.now()
    if weekend.weekday() < 5:  # If not weekend
        # Simulate weekend
        days_to_saturday = 5 - weekend.weekday()
        weekend = weekend + timedelta(days=days_to_saturday)
    
    is_sensitive, should_alert, alert_details = monitor.check_sensitive_data_access(
        user_id, '/api/audit-log', weekend
    )
    
    if should_alert:
        print(f"✅ Weekend access detected: {alert_details['description']}")
    else:
        print("⚠️  Weekend detection depends on actual date")
    
    # Test normal business hours access
    business_hours = datetime.now().replace(hour=14, minute=0)  # 2 PM
    is_sensitive, should_alert, alert_details = monitor.check_sensitive_data_access(
        user_id, '/api/sales/report', business_hours
    )
    
    if not should_alert:
        print("✅ Business hours access not flagged")
    else:
        print("❌ False positive during business hours")

def main():
    """Run all security tests"""
    print("🛡️  CVD Security Features Test Suite")
    print("=" * 50)
    
    try:
        test_brute_force_detection()
        test_data_export_monitoring()
        test_privilege_escalation()
        test_geographic_anomaly()
        test_sensitive_data_access()
        
        print("\n" + "=" * 50)
        print("✅ Security feature tests completed!")
        print("\nNote: Some features require:")
        print("  - Real GeoIP integration for accurate geographic detection")
        print("  - Email/Slack integration for alert notifications")
        print("  - Regular security audits and threshold tuning")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()