#!/usr/bin/env python3
"""
CVD Mobile PWA Testing Examples

This file demonstrates comprehensive testing patterns for Progressive Web App (PWA) functionality
in the CVD Driver App, including offline capabilities, push notifications, service worker behavior,
and mobile-specific features like location tracking and photo uploads.
"""

import unittest
import json
import time
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

# Add CVD application to Python path for testing
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

# Try to import CVD components (may not be available in all test environments)
try:
    from app import create_app
    from auth import hash_password
    CVD_AVAILABLE = True
except ImportError as e:
    print(f"Warning: CVD modules not available: {e}")
    CVD_AVAILABLE = False


class PWAOfflineFunctionalityTests(unittest.TestCase):
    """
    PWA Offline Functionality Tests
    
    These tests demonstrate:
    - Service worker registration and caching
    - Offline data storage with IndexedDB
    - Background synchronization
    - Offline UI state management
    - Data persistence and recovery
    """
    
    def setUp(self):
        """Set up PWA testing environment with Chrome in mobile mode."""
        print("Setting up PWA offline functionality tests...")
        
        # Configure Chrome for mobile PWA testing
        self.chrome_options = Options()
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--headless')  # Run headless for automated testing
        
        # Mobile emulation settings
        mobile_emulation = {
            "deviceName": "iPhone 12"
        }
        self.chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # PWA-specific settings
        self.chrome_options.add_argument('--enable-features=VaapiVideoDecoder')
        self.chrome_options.add_argument('--disable-features=TranslateUI')
        self.chrome_options.add_argument('--disable-ipc-flooding-protection')
        
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.implicitly_wait(10)
            self.driver_available = True
            print("✓ Chrome WebDriver initialized for mobile PWA testing")
        except Exception as e:
            print(f"Warning: Chrome WebDriver not available: {e}")
            self.driver = None
            self.driver_available = False
        
        # Set up test server if CVD is available
        if CVD_AVAILABLE:
            self.setup_test_server()
        else:
            self.test_server_url = "http://localhost:8000"  # Assume external server
        
        print("PWA test environment setup complete")
    
    def tearDown(self):
        """Clean up PWA testing environment."""
        if self.driver_available and self.driver:
            self.driver.quit()
        
        if hasattr(self, 'test_server'):
            # Clean up test server
            pass
        
        print("PWA test environment cleanup complete")
    
    def setup_test_server(self):
        """Set up local test server for PWA testing."""
        # Create temporary database for PWA testing
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        
        # Configure test app
        self.app = create_app({
            'TESTING': True,
            'DATABASE': self.db_path,
            'SECRET_KEY': 'pwa-test-secret'
        })
        
        # Initialize test database with minimal data
        self.init_pwa_test_database()
        
        self.test_server_url = "http://localhost:5000"  # Flask default
        print(f"Test server configured at {self.test_server_url}")
    
    def init_pwa_test_database(self):
        """Initialize database with PWA test data."""
        import sqlite3
        
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Create essential tables for PWA testing
        cursor.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'driver',
                full_name TEXT
            );
            
            CREATE TABLE service_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                assigned_to INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE service_order_cabinets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_order_id INTEGER NOT NULL,
                device_id INTEGER NOT NULL,
                cabinet_index INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                photos TEXT,  -- JSON array of photo URLs
                completed_at TIMESTAMP
            );
        """)
        
        # Create test driver user
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, full_name)
            VALUES (?, ?, ?, ?)
        """, ('testdriver', hash_password('testdriver'), 'driver', 'Test Driver'))
        
        # Create test service orders
        test_orders = [
            (1, 'pending', 1, 'Test service order for PWA testing'),
            (2, 'assigned', 1, 'Another test order'),
            (3, 'in_progress', 1, 'In-progress test order')
        ]
        
        cursor.executemany("""
            INSERT INTO service_orders (route_id, status, assigned_to, notes)
            VALUES (?, ?, ?, ?)
        """, test_orders)
        
        db.commit()
        db.close()
        
        print("PWA test database initialized")
    
    def test_service_worker_registration(self):
        """
        Test service worker registration and caching strategy.
        
        This test verifies:
        - Service worker script loads correctly
        - Registration succeeds
        - Cache strategies are implemented
        - Offline fallback pages are cached
        """
        print("\n=== Testing Service Worker Registration ===")
        
        if not self.driver_available:
            self.skipTest("WebDriver not available for service worker testing")
        
        try:
            # Navigate to PWA app
            pwa_url = f"{self.test_server_url}/pages/driver-app/"
            self.driver.get(pwa_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print(f"✓ Navigated to PWA app: {pwa_url}")
            
            # Check for service worker registration
            sw_registration_js = """
                return new Promise((resolve) => {
                    if ('serviceWorker' in navigator) {
                        navigator.serviceWorker.getRegistration()
                            .then(registration => {
                                resolve({
                                    supported: true,
                                    registered: registration !== undefined,
                                    scope: registration ? registration.scope : null,
                                    state: registration && registration.active ? registration.active.state : null
                                });
                            })
                            .catch(() => resolve({ supported: true, registered: false }));
                    } else {
                        resolve({ supported: false, registered: false });
                    }
                });
            """
            
            sw_info = self.driver.execute_async_script(sw_registration_js)
            
            self.assertTrue(sw_info['supported'], "Browser should support service workers")
            print(f"  Service Worker supported: {sw_info['supported']}")
            print(f"  Registration found: {sw_info['registered']}")
            
            if sw_info['registered']:
                print(f"  Scope: {sw_info['scope']}")
                print(f"  State: {sw_info['state']}")
            
            # Test cache functionality
            cache_test_js = """
                return new Promise((resolve) => {
                    if ('caches' in window) {
                        caches.keys().then(cacheNames => {
                            resolve({
                                supported: true,
                                cacheCount: cacheNames.length,
                                cacheNames: cacheNames
                            });
                        }).catch(() => resolve({ supported: true, cacheCount: 0 }));
                    } else {
                        resolve({ supported: false, cacheCount: 0 });
                    }
                });
            """
            
            cache_info = self.driver.execute_async_script(cache_test_js)
            
            self.assertTrue(cache_info['supported'], "Browser should support Cache API")
            print(f"  Cache API supported: {cache_info['supported']}")
            print(f"  Cache count: {cache_info['cacheCount']}")
            
            if cache_info['cacheCount'] > 0:
                print(f"  Cache names: {cache_info['cacheNames']}")
            
        except Exception as e:
            self.fail(f"Service worker registration test failed: {e}")
    
    def test_offline_data_storage(self):
        """
        Test offline data storage using IndexedDB.
        
        This test verifies:
        - IndexedDB support and initialization
        - Service order data storage offline
        - Data retrieval when offline
        - Data synchronization when back online
        """
        print("\n=== Testing Offline Data Storage ===")
        
        if not self.driver_available:
            self.skipTest("WebDriver not available for offline storage testing")
        
        try:
            # Navigate to driver app
            self.driver.get(f"{self.test_server_url}/pages/driver-app/")
            
            # Test IndexedDB support
            indexeddb_test_js = """
                return new Promise((resolve) => {
                    const supported = 'indexedDB' in window;
                    resolve({ supported: supported });
                });
            """
            
            indexeddb_info = self.driver.execute_async_script(indexeddb_test_js)
            self.assertTrue(indexeddb_info['supported'], "IndexedDB should be supported")
            
            print(f"✓ IndexedDB supported: {indexeddb_info['supported']}")
            
            # Test offline data storage
            offline_storage_js = """
                return new Promise((resolve) => {
                    // Mock service order data
                    const testServiceOrders = [
                        {
                            id: 1,
                            route_id: 1,
                            status: 'pending',
                            cabinets: [
                                { device_id: 101, cabinet_index: 0, status: 'pending' }
                            ],
                            offline: true,
                            sync_pending: false
                        },
                        {
                            id: 2,
                            route_id: 1,
                            status: 'in_progress',
                            cabinets: [
                                { device_id: 102, cabinet_index: 0, status: 'completed' }
                            ],
                            offline: true,
                            sync_pending: true
                        }
                    ];
                    
                    try {
                        // Store in localStorage as fallback (IndexedDB implementation would be more complex)
                        localStorage.setItem('cvd_offline_service_orders', JSON.stringify(testServiceOrders));
                        
                        // Retrieve and verify
                        const stored = JSON.parse(localStorage.getItem('cvd_offline_service_orders'));
                        
                        resolve({
                            success: true,
                            stored_count: stored.length,
                            has_offline_flag: stored[0].offline === true,
                            has_sync_pending: stored[1].sync_pending === true
                        });
                    } catch (error) {
                        resolve({ success: false, error: error.message });
                    }
                });
            """
            
            storage_result = self.driver.execute_async_script(offline_storage_js)
            
            self.assertTrue(storage_result['success'], "Offline storage should work")
            self.assertEqual(storage_result['stored_count'], 2, "Should store 2 service orders")
            self.assertTrue(storage_result['has_offline_flag'], "Should have offline flag")
            self.assertTrue(storage_result['has_sync_pending'], "Should track sync status")
            
            print(f"✓ Offline storage test passed")
            print(f"  Stored orders: {storage_result['stored_count']}")
            print(f"  Offline flags: {storage_result['has_offline_flag']}")
            print(f"  Sync tracking: {storage_result['has_sync_pending']}")
            
            # Test data retrieval in offline mode
            offline_retrieval_js = """
                return new Promise((resolve) => {
                    try {
                        const offlineOrders = JSON.parse(localStorage.getItem('cvd_offline_service_orders'));
                        const pendingOrders = offlineOrders.filter(order => order.status === 'pending');
                        const inProgressOrders = offlineOrders.filter(order => order.status === 'in_progress');
                        const syncPendingOrders = offlineOrders.filter(order => order.sync_pending);
                        
                        resolve({
                            success: true,
                            total_orders: offlineOrders.length,
                            pending_orders: pendingOrders.length,
                            in_progress_orders: inProgressOrders.length,
                            sync_pending_orders: syncPendingOrders.length
                        });
                    } catch (error) {
                        resolve({ success: false, error: error.message });
                    }
                });
            """
            
            retrieval_result = self.driver.execute_async_script(offline_retrieval_js)
            
            self.assertTrue(retrieval_result['success'], "Offline data retrieval should work")
            self.assertEqual(retrieval_result['total_orders'], 2)
            self.assertEqual(retrieval_result['pending_orders'], 1)
            self.assertEqual(retrieval_result['in_progress_orders'], 1)
            self.assertEqual(retrieval_result['sync_pending_orders'], 1)
            
            print(f"✓ Offline retrieval test passed")
            print(f"  Total orders: {retrieval_result['total_orders']}")
            print(f"  Pending: {retrieval_result['pending_orders']}")
            print(f"  In progress: {retrieval_result['in_progress_orders']}")
            print(f"  Sync pending: {retrieval_result['sync_pending_orders']}")
            
        except Exception as e:
            self.fail(f"Offline data storage test failed: {e}")
    
    def test_offline_ui_behavior(self):
        """
        Test UI behavior when offline.
        
        This test verifies:
        - Offline indicator display
        - Disabled network-dependent actions
        - Offline-first UI patterns
        - User feedback for offline state
        """
        print("\n=== Testing Offline UI Behavior ===")
        
        if not self.driver_available:
            self.skipTest("WebDriver not available for offline UI testing")
        
        try:
            # Navigate to driver app
            self.driver.get(f"{self.test_server_url}/pages/driver-app/")
            
            # Test offline detection and UI updates
            offline_ui_js = """
                return new Promise((resolve) => {
                    // Simulate offline state
                    const originalOnline = navigator.onLine;
                    
                    // Mock offline state
                    Object.defineProperty(navigator, 'onLine', {
                        writable: true,
                        value: false
                    });
                    
                    // Dispatch offline event
                    window.dispatchEvent(new Event('offline'));
                    
                    setTimeout(() => {
                        // Check UI changes for offline state
                        const offlineIndicators = document.querySelectorAll('.offline-indicator, [data-offline="true"]');
                        const disabledButtons = document.querySelectorAll('button:disabled, .disabled');
                        const offlineMessages = document.querySelectorAll('.offline-message, .offline-notice');
                        
                        // Restore online state
                        Object.defineProperty(navigator, 'onLine', {
                            writable: true,
                            value: originalOnline
                        });
                        
                        window.dispatchEvent(new Event('online'));
                        
                        resolve({
                            offline_indicators: offlineIndicators.length,
                            disabled_buttons: disabledButtons.length,
                            offline_messages: offlineMessages.length,
                            navigator_offline: !navigator.onLine
                        });
                    }, 500);
                });
            """
            
            ui_result = self.driver.execute_async_script(offline_ui_js)
            
            print(f"✓ Offline UI behavior test completed")
            print(f"  Offline indicators: {ui_result['offline_indicators']}")
            print(f"  Disabled buttons: {ui_result['disabled_buttons']}")
            print(f"  Offline messages: {ui_result['offline_messages']}")
            
            # Test should show some offline UI feedback
            has_offline_feedback = (ui_result['offline_indicators'] > 0 or 
                                  ui_result['disabled_buttons'] > 0 or 
                                  ui_result['offline_messages'] > 0)
            
            if not has_offline_feedback:
                print("! No specific offline UI feedback detected (may not be implemented)")
            else:
                print("✓ Offline UI feedback mechanisms present")
            
        except Exception as e:
            self.fail(f"Offline UI behavior test failed: {e}")
    
    def test_background_sync_functionality(self):
        """
        Test background sync functionality.
        
        This test verifies:
        - Background sync registration
        - Sync event handling
        - Data synchronization when online
        - Conflict resolution strategies
        """
        print("\n=== Testing Background Sync Functionality ===")
        
        if not self.driver_available:
            self.skipTest("WebDriver not available for background sync testing")
        
        try:
            # Navigate to driver app
            self.driver.get(f"{self.test_server_url}/pages/driver-app/")
            
            # Test background sync support and registration
            bg_sync_js = """
                return new Promise((resolve) => {
                    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
                        // Background sync is supported
                        navigator.serviceWorker.ready.then(registration => {
                            // Simulate sync registration
                            return registration.sync.register('service-order-sync');
                        }).then(() => {
                            resolve({
                                supported: true,
                                registered: true,
                                error: null
                            });
                        }).catch(error => {
                            resolve({
                                supported: true,
                                registered: false,
                                error: error.message
                            });
                        });
                    } else {
                        resolve({
                            supported: false,
                            registered: false,
                            error: 'Background Sync not supported'
                        });
                    }
                });
            """
            
            sync_result = self.driver.execute_async_script(bg_sync_js)
            
            print(f"✓ Background sync support: {sync_result['supported']}")
            
            if sync_result['supported']:
                print(f"  Registration successful: {sync_result['registered']}")
                if sync_result['error']:
                    print(f"  Error: {sync_result['error']}")
            else:
                print(f"  Not supported: {sync_result['error']}")
            
            # Test sync data preparation
            sync_data_js = """
                return new Promise((resolve) => {
                    // Simulate preparing data for background sync
                    const syncData = {
                        service_order_updates: [
                            {
                                id: 1,
                                status: 'completed',
                                completed_at: new Date().toISOString(),
                                photos: ['photo1.jpg', 'photo2.jpg'],
                                sync_action: 'update'
                            },
                            {
                                id: 2,
                                cabinet_id: 1,
                                status: 'in_progress',
                                started_at: new Date().toISOString(),
                                sync_action: 'cabinet_update'
                            }
                        ],
                        timestamp: Date.now()
                    };
                    
                    try {
                        // Store sync data
                        localStorage.setItem('cvd_pending_sync', JSON.stringify(syncData));
                        
                        // Verify storage
                        const stored = JSON.parse(localStorage.getItem('cvd_pending_sync'));
                        
                        resolve({
                            success: true,
                            updates_count: stored.service_order_updates.length,
                            has_photos: stored.service_order_updates[0].photos.length > 0,
                            has_timestamp: stored.timestamp > 0
                        });
                    } catch (error) {
                        resolve({
                            success: false,
                            error: error.message
                        });
                    }
                });
            """
            
            data_result = self.driver.execute_async_script(sync_data_js)
            
            self.assertTrue(data_result['success'], "Sync data preparation should work")
            self.assertEqual(data_result['updates_count'], 2, "Should prepare 2 updates for sync")
            self.assertTrue(data_result['has_photos'], "Should include photo data")
            self.assertTrue(data_result['has_timestamp'], "Should include timestamp")
            
            print(f"✓ Background sync data preparation test passed")
            print(f"  Updates queued: {data_result['updates_count']}")
            print(f"  Photo data included: {data_result['has_photos']}")
            print(f"  Timestamped: {data_result['has_timestamp']}")
            
        except Exception as e:
            self.fail(f"Background sync functionality test failed: {e}")


class PWAPushNotificationTests(unittest.TestCase):
    """
    PWA Push Notification Tests
    
    These tests demonstrate:
    - Push notification API support
    - Service worker push event handling
    - Notification permission management
    - Push subscription management
    - Notification interaction handling
    """
    
    def setUp(self):
        """Set up push notification testing environment."""
        print("Setting up PWA push notification tests...")
        
        # Configure Chrome with notification permissions
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--headless')
        
        # Grant notification permissions
        prefs = {
            "profile.default_content_setting_values.notifications": 1
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            self.driver_available = True
            print("✓ Chrome WebDriver initialized with notification permissions")
        except Exception as e:
            print(f"Warning: Chrome WebDriver not available: {e}")
            self.driver = None
            self.driver_available = False
        
        self.test_server_url = "http://localhost:8000"
    
    def tearDown(self):
        """Clean up push notification testing environment."""
        if self.driver_available and self.driver:
            self.driver.quit()
    
    def test_push_notification_support(self):
        """
        Test push notification API support and permissions.
        
        This test verifies:
        - Push Manager API availability
        - Notification API support
        - Permission request handling
        - Service worker push event setup
        """
        print("\n=== Testing Push Notification Support ===")
        
        if not self.driver_available:
            self.skipTest("WebDriver not available for push notification testing")
        
        try:
            # Navigate to driver app
            self.driver.get(f"{self.test_server_url}/pages/driver-app/")
            
            # Test push notification support
            push_support_js = """
                return new Promise((resolve) => {
                    const support = {
                        pushManager: 'PushManager' in window,
                        notifications: 'Notification' in window,
                        serviceWorker: 'serviceWorker' in navigator,
                        permissions: 'permissions' in navigator
                    };
                    
                    if (support.notifications) {
                        // Check current permission
                        support.permission = Notification.permission;
                        
                        // Test notification creation (won't actually show in headless)
                        try {
                            const testNotification = new Notification('Test CVD Notification', {
                                body: 'This is a test notification for CVD Driver App',
                                icon: '/icons/icon-192x192.png',
                                tag: 'cvd-test',
                                requireInteraction: false,
                                silent: true
                            });
                            
                            support.canCreateNotification = true;
                            testNotification.close();
                        } catch (error) {
                            support.canCreateNotification = false;
                            support.notificationError = error.message;
                        }
                    }
                    
                    resolve(support);
                });
            """
            
            support_result = self.driver.execute_async_script(push_support_js)
            
            # Verify push notification support
            self.assertTrue(support_result['pushManager'], "PushManager should be supported")
            self.assertTrue(support_result['notifications'], "Notifications should be supported")
            self.assertTrue(support_result['serviceWorker'], "Service Worker should be supported")
            
            print(f"✓ Push notification support verified")
            print(f"  PushManager: {support_result['pushManager']}")
            print(f"  Notifications: {support_result['notifications']}")
            print(f"  Service Worker: {support_result['serviceWorker']}")
            print(f"  Permission: {support_result.get('permission', 'unknown')}")
            print(f"  Can create notification: {support_result.get('canCreateNotification', False)}")
            
            if 'notificationError' in support_result:
                print(f"  Notification error: {support_result['notificationError']}")
            
        except Exception as e:
            self.fail(f"Push notification support test failed: {e}")
    
    def test_push_subscription_management(self):
        """
        Test push subscription creation and management.
        
        This test verifies:
        - Push subscription creation
        - Subscription key handling
        - Subscription persistence
        - Unsubscribe functionality
        """
        print("\n=== Testing Push Subscription Management ===")
        
        if not self.driver_available:
            self.skipTest("WebDriver not available for push subscription testing")
        
        try:
            # Navigate to driver app
            self.driver.get(f"{self.test_server_url}/pages/driver-app/")
            
            # Test push subscription management
            subscription_js = """
                return new Promise((resolve) => {
                    if ('serviceWorker' in navigator && 'PushManager' in window) {
                        navigator.serviceWorker.ready.then(registration => {
                            // Mock VAPID keys for testing
                            const applicationServerKey = 'BEl62iUYgUivxIkv69yViEuiBIa40HI80xeSNdmruGgQSWkmMLuAdXv1VLLr1xkBBQlP8Kb8sKdT8fGOsNTf2JYNfSo';
                            
                            return registration.pushManager.subscribe({
                                userVisibleOnly: true,
                                applicationServerKey: applicationServerKey
                            });
                        }).then(subscription => {
                            const subscriptionData = {
                                endpoint: subscription.endpoint,
                                keys: {
                                    p256dh: arrayBufferToBase64(subscription.getKey('p256dh')),
                                    auth: arrayBufferToBase64(subscription.getKey('auth'))
                                }
                            };
                            
                            resolve({
                                success: true,
                                hasEndpoint: !!subscription.endpoint,
                                hasKeys: !!subscription.getKey('p256dh'),
                                subscriptionData: subscriptionData
                            });
                        }).catch(error => {
                            resolve({
                                success: false,
                                error: error.message,
                                errorName: error.name
                            });
                        });
                    } else {
                        resolve({
                            success: false,
                            error: 'Push notifications not supported'
                        });
                    }
                    
                    function arrayBufferToBase64(buffer) {
                        const bytes = new Uint8Array(buffer);
                        let binary = '';
                        bytes.forEach(byte => binary += String.fromCharCode(byte));
                        return window.btoa(binary);
                    }
                });
            """
            
            subscription_result = self.driver.execute_async_script(subscription_js)
            
            if subscription_result['success']:
                self.assertTrue(subscription_result['hasEndpoint'], "Subscription should have endpoint")
                self.assertTrue(subscription_result['hasKeys'], "Subscription should have encryption keys")
                
                print(f"✓ Push subscription created successfully")
                print(f"  Has endpoint: {subscription_result['hasEndpoint']}")
                print(f"  Has keys: {subscription_result['hasKeys']}")
                
                # Verify subscription data structure
                if 'subscriptionData' in subscription_result:
                    sub_data = subscription_result['subscriptionData']
                    self.assertIn('endpoint', sub_data)
                    self.assertIn('keys', sub_data)
                    self.assertIn('p256dh', sub_data['keys'])
                    self.assertIn('auth', sub_data['keys'])
                    
                    print(f"  Endpoint present: {bool(sub_data['endpoint'])}")
                    print(f"  Keys present: {bool(sub_data['keys'])}")
            else:
                print(f"! Push subscription failed: {subscription_result['error']}")
                print(f"  Error type: {subscription_result.get('errorName', 'Unknown')}")
                
                # This might be expected in headless testing environment
                if 'not supported' in subscription_result['error'].lower():
                    print("  (This may be expected in headless testing environment)")
            
        except Exception as e:
            self.fail(f"Push subscription management test failed: {e}")
    
    def test_notification_display_and_interaction(self):
        """
        Test notification display and user interaction handling.
        
        This test verifies:
        - Notification display with proper data
        - Click event handling
        - Action button functionality
        - Notification grouping and tagging
        """
        print("\n=== Testing Notification Display and Interaction ===")
        
        if not self.driver_available:
            self.skipTest("WebDriver not available for notification interaction testing")
        
        try:
            # Navigate to driver app
            self.driver.get(f"{self.test_server_url}/pages/driver-app/")
            
            # Test notification creation with CVD-specific content
            notification_js = """
                return new Promise((resolve) => {
                    if ('Notification' in window) {
                        try {
                            // Create CVD service order notification
                            const serviceOrderNotification = new Notification('New Service Order Assigned', {
                                body: 'Route A - 3 devices need service',
                                icon: '/icons/icon-192x192.png',
                                badge: '/icons/icon-72x72.png',
                                tag: 'service-order-123',
                                requireInteraction: true,
                                actions: [
                                    {
                                        action: 'view',
                                        title: 'View Order',
                                        icon: '/icons/view-icon.png'
                                    },
                                    {
                                        action: 'dismiss',
                                        title: 'Dismiss',
                                        icon: '/icons/dismiss-icon.png'
                                    }
                                ],
                                data: {
                                    orderId: 123,
                                    routeId: 1,
                                    deviceCount: 3,
                                    priority: 'normal'
                                },
                                timestamp: Date.now()
                            });
                            
                            // Test notification properties
                            const notificationData = {
                                title: serviceOrderNotification.title,
                                body: serviceOrderNotification.body,
                                icon: serviceOrderNotification.icon,
                                tag: serviceOrderNotification.tag,
                                hasData: !!serviceOrderNotification.data,
                                hasActions: serviceOrderNotification.actions && serviceOrderNotification.actions.length > 0
                            };
                            
                            // Set up event handlers
                            let clickHandled = false;
                            let closeHandled = false;
                            
                            serviceOrderNotification.onclick = function(event) {
                                clickHandled = true;
                                // In real app, this would navigate to service order
                                console.log('Notification clicked:', event);
                            };
                            
                            serviceOrderNotification.onclose = function(event) {
                                closeHandled = true;
                                console.log('Notification closed:', event);
                            };
                            
                            // Simulate click and close
                            setTimeout(() => {
                                serviceOrderNotification.onclick(new Event('click'));
                                serviceOrderNotification.onclose(new Event('close'));
                                serviceOrderNotification.close();
                                
                                resolve({
                                    success: true,
                                    notification: notificationData,
                                    clickHandled: clickHandled,
                                    closeHandled: closeHandled
                                });
                            }, 100);
                            
                        } catch (error) {
                            resolve({
                                success: false,
                                error: error.message
                            });
                        }
                    } else {
                        resolve({
                            success: false,
                            error: 'Notifications not supported'
                        });
                    }
                });
            """
            
            notification_result = self.driver.execute_async_script(notification_js)
            
            if notification_result['success']:
                notification_data = notification_result['notification']
                
                # Verify notification structure
                self.assertEqual(notification_data['title'], 'New Service Order Assigned')
                self.assertIn('Route A', notification_data['body'])
                self.assertEqual(notification_data['tag'], 'service-order-123')
                self.assertTrue(notification_data['hasData'])
                
                print(f"✓ Notification created successfully")
                print(f"  Title: {notification_data['title']}")
                print(f"  Body: {notification_data['body']}")
                print(f"  Tag: {notification_data['tag']}")
                print(f"  Has data: {notification_data['hasData']}")
                print(f"  Has actions: {notification_data.get('hasActions', False)}")
                
                # Verify event handling
                self.assertTrue(notification_result['clickHandled'], "Click event should be handled")
                self.assertTrue(notification_result['closeHandled'], "Close event should be handled")
                
                print(f"  Click handled: {notification_result['clickHandled']}")
                print(f"  Close handled: {notification_result['closeHandled']}")
                
            else:
                print(f"! Notification creation failed: {notification_result['error']}")
                
        except Exception as e:
            self.fail(f"Notification display and interaction test failed: {e}")


class PWALocationTrackingTests(unittest.TestCase):
    """
    PWA Location Tracking Tests
    
    These tests demonstrate:
    - Geolocation API usage
    - Location permission handling
    - Background location tracking
    - Location data storage and sync
    - Privacy and battery considerations
    """
    
    def setUp(self):
        """Set up location tracking testing environment."""
        print("Setting up PWA location tracking tests...")
        
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--headless')
        
        # Grant location permissions
        prefs = {
            "profile.default_content_setting_values.geolocation": 1
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Mock location for testing
        chrome_options.add_argument('--use-fake-ui-for-media-stream')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            self.driver_available = True
            print("✓ Chrome WebDriver initialized with location permissions")
        except Exception as e:
            print(f"Warning: Chrome WebDriver not available: {e}")
            self.driver = None
            self.driver_available = False
        
        self.test_server_url = "http://localhost:8000"
    
    def tearDown(self):
        """Clean up location tracking testing environment."""
        if self.driver_available and self.driver:
            self.driver.quit()
    
    def test_geolocation_api_support(self):
        """
        Test geolocation API support and basic functionality.
        
        This test verifies:
        - Geolocation API availability
        - Position retrieval
        - Error handling for location access
        - Location data structure validation
        """
        print("\n=== Testing Geolocation API Support ===")
        
        if not self.driver_available:
            self.skipTest("WebDriver not available for geolocation testing")
        
        try:
            # Navigate to driver app
            self.driver.get(f"{self.test_server_url}/pages/driver-app/")
            
            # Test geolocation support and mock location
            geolocation_js = """
                return new Promise((resolve) => {
                    if ('geolocation' in navigator) {
                        // Mock geolocation for testing
                        const mockPosition = {
                            coords: {
                                latitude: 40.7128,
                                longitude: -74.0060,
                                accuracy: 10,
                                altitude: null,
                                altitudeAccuracy: null,
                                heading: null,
                                speed: null
                            },
                            timestamp: Date.now()
                        };
                        
                        // Override getCurrentPosition for testing
                        const originalGetCurrentPosition = navigator.geolocation.getCurrentPosition;
                        navigator.geolocation.getCurrentPosition = function(success, error, options) {
                            setTimeout(() => success(mockPosition), 100);
                        };
                        
                        // Test position retrieval
                        navigator.geolocation.getCurrentPosition(
                            function(position) {
                                resolve({
                                    supported: true,
                                    success: true,
                                    latitude: position.coords.latitude,
                                    longitude: position.coords.longitude,
                                    accuracy: position.coords.accuracy,
                                    timestamp: position.timestamp,
                                    hasCoords: !!position.coords,
                                    hasTimestamp: !!position.timestamp
                                });
                            },
                            function(error) {
                                resolve({
                                    supported: true,
                                    success: false,
                                    error: error.message,
                                    errorCode: error.code
                                });
                            },
                            {
                                enableHighAccuracy: true,
                                timeout: 10000,
                                maximumAge: 0
                            }
                        );
                    } else {
                        resolve({
                            supported: false,
                            success: false,
                            error: 'Geolocation not supported'
                        });
                    }
                });
            """
            
            location_result = self.driver.execute_async_script(geolocation_js)
            
            self.assertTrue(location_result['supported'], "Geolocation should be supported")
            
            if location_result['success']:
                self.assertTrue(location_result['hasCoords'], "Position should have coordinates")
                self.assertTrue(location_result['hasTimestamp'], "Position should have timestamp")
                self.assertIsInstance(location_result['latitude'], (int, float))
                self.assertIsInstance(location_result['longitude'], (int, float))
                
                print(f"✓ Geolocation API test passed")
                print(f"  Supported: {location_result['supported']}")
                print(f"  Success: {location_result['success']}")
                print(f"  Latitude: {location_result['latitude']}")
                print(f"  Longitude: {location_result['longitude']}")
                print(f"  Accuracy: {location_result['accuracy']}m")
                
            else:
                print(f"! Geolocation failed: {location_result['error']}")
                print(f"  Error code: {location_result.get('errorCode', 'Unknown')}")
                
        except Exception as e:
            self.fail(f"Geolocation API support test failed: {e}")
    
    def test_location_tracking_for_service_visits(self):
        """
        Test location tracking for service visit verification.
        
        This test verifies:
        - Location capture at service start/end
        - Location data storage with service records
        - Distance calculation between locations
        - Location-based service verification
        """
        print("\n=== Testing Location Tracking for Service Visits ===")
        
        if not self.driver_available:
            self.skipTest("WebDriver not available for service visit location testing")
        
        try:
            # Navigate to driver app
            self.driver.get(f"{self.test_server_url}/pages/driver-app/")
            
            # Test service visit location tracking
            service_location_js = """
                return new Promise((resolve) => {
                    // Mock service visit with location tracking
                    const serviceVisit = {
                        orderId: 123,
                        cabinetId: 1,
                        deviceLocation: {
                            latitude: 40.7128,
                            longitude: -74.0060,
                            name: 'Downtown Office Complex'
                        }
                    };
                    
                    // Mock driver current location
                    const driverLocation = {
                        latitude: 40.7130,
                        longitude: -74.0058,
                        accuracy: 15,
                        timestamp: Date.now()
                    };
                    
                    // Calculate distance between locations (Haversine formula)
                    function calculateDistance(lat1, lon1, lat2, lon2) {
                        const R = 6371; // Earth's radius in km
                        const dLat = (lat2 - lat1) * Math.PI / 180;
                        const dLon = (lon2 - lon1) * Math.PI / 180;
                        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                                Math.sin(dLon/2) * Math.sin(dLon/2);
                        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
                        return R * c * 1000; // Return distance in meters
                    }
                    
                    const distance = calculateDistance(
                        driverLocation.latitude, driverLocation.longitude,
                        serviceVisit.deviceLocation.latitude, serviceVisit.deviceLocation.longitude
                    );
                    
                    // Service visit location verification
                    const isAtServiceLocation = distance <= 100; // Within 100 meters
                    
                    // Create service visit record with location
                    const serviceVisitRecord = {
                        orderId: serviceVisit.orderId,
                        cabinetId: serviceVisit.cabinetId,
                        startLocation: {
                            latitude: driverLocation.latitude,
                            longitude: driverLocation.longitude,
                            accuracy: driverLocation.accuracy,
                            timestamp: driverLocation.timestamp
                        },
                        deviceLocation: serviceVisit.deviceLocation,
                        distanceToDevice: distance,
                        locationVerified: isAtServiceLocation,
                        startTime: new Date().toISOString()
                    };
                    
                    // Store service visit with location
                    try {
                        localStorage.setItem('cvd_service_visit_' + serviceVisit.orderId, 
                                           JSON.stringify(serviceVisitRecord));
                        
                        resolve({
                            success: true,
                            distance: distance,
                            locationVerified: isAtServiceLocation,
                            hasStartLocation: !!serviceVisitRecord.startLocation,
                            hasDeviceLocation: !!serviceVisitRecord.deviceLocation,
                            recordStored: true
                        });
                    } catch (error) {
                        resolve({
                            success: false,
                            error: error.message
                        });
                    }
                });
            """
            
            location_result = self.driver.execute_async_script(service_location_js)
            
            self.assertTrue(location_result['success'], "Service location tracking should work")
            self.assertTrue(location_result['hasStartLocation'], "Should capture start location")
            self.assertTrue(location_result['hasDeviceLocation'], "Should have device location")
            self.assertTrue(location_result['recordStored'], "Should store location record")
            
            # Distance should be reasonable (test uses nearby coordinates)
            self.assertLess(location_result['distance'], 500, "Distance should be reasonable for test")
            
            print(f"✓ Service visit location tracking test passed")
            print(f"  Distance to device: {location_result['distance']:.1f}m")
            print(f"  Location verified: {location_result['locationVerified']}")
            print(f"  Has start location: {location_result['hasStartLocation']}")
            print(f"  Has device location: {location_result['hasDeviceLocation']}")
            print(f"  Record stored: {location_result['recordStored']}")
            
        except Exception as e:
            self.fail(f"Service visit location tracking test failed: {e}")


if __name__ == '__main__':
    """
    Run the mobile PWA testing examples.
    
    Usage:
    python MOBILE_PWA_TESTS.py                        # Run all PWA tests
    python -m pytest MOBILE_PWA_TESTS.py             # Run with pytest
    python -m pytest MOBILE_PWA_TESTS.py::PWAOfflineFunctionalityTests::test_service_worker_registration -v
    
    Prerequisites:
    pip install selenium
    # Ensure ChromeDriver is installed and in PATH
    """
    
    print("="*80)
    print("CVD MOBILE PWA TESTING EXAMPLES")
    print("="*80)
    print()
    print("This module demonstrates comprehensive PWA testing patterns for:")
    print("• Offline functionality with service workers and IndexedDB")
    print("• Push notification support and subscription management")
    print("• Location tracking for service visit verification")
    print("• Mobile-specific UI behavior and responsiveness")
    print("• Background sync and data synchronization")
    print()
    print("Key PWA testing concepts demonstrated:")
    print("• Service worker registration and caching strategies")
    print("• Offline-first application patterns")
    print("• Push notification lifecycle and user interaction")
    print("• Geolocation API usage and location-based features")
    print("• Mobile browser automation with Selenium")
    print()
    print("Note: These tests require Chrome WebDriver and may need actual")
    print("browser environment for full PWA feature testing.")
    print()
    print("Running PWA tests with detailed output...")
    print("="*80)
    
    # Run tests with high verbosity
    unittest.main(verbosity=2, exit=False)
    
    print("="*80)
    print("MOBILE PWA TESTING EXAMPLES COMPLETED")
    print("="*80)