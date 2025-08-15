#!/usr/bin/env python3
"""Test script to verify route schedule fixes"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_route_devices_api():
    """Test the route devices API endpoint"""
    print("Testing route devices API...")
    
    try:
        # Test route 1
        response = requests.get(f"{BASE_URL}/api/routes/1/devices")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Route Name: {data.get('routeName')}")
            print(f"✓ Number of devices: {len(data.get('devices', []))}")
            
            # Check device data structure
            devices = data.get('devices', [])
            if devices:
                first_device = devices[0]
                print(f"\n  First device structure:")
                print(f"    - id: {first_device.get('id')} (type: {type(first_device.get('id')).__name__})")
                print(f"    - asset: {first_device.get('asset')} (type: {type(first_device.get('asset')).__name__})")
                print(f"    - Has cabinets: {'cabinets' in first_device}")
                print(f"    - Has slotMetrics: {'slotMetrics' in first_device}")
                print(f"    - Has locationAddress: {'locationAddress' in first_device}")
                print(f"    - Has coordinates: {first_device.get('locationLatitude') is not None}")
                
                # Check cabinet structure
                if 'cabinets' in first_device and first_device['cabinets']:
                    first_cabinet = first_device['cabinets'][0]
                    print(f"\n  First cabinet structure:")
                    print(f"    - cabinetIndex: {first_cabinet.get('cabinetIndex')} (type: {type(first_cabinet.get('cabinetIndex')).__name__})")
                    print(f"    - Has metrics: {'metrics' in first_cabinet}")
                    
                # Verify ID consistency
                print(f"\n✓ ID type consistency check:")
                id_types = set()
                for device in devices:
                    id_types.add(type(device.get('id')).__name__)
                
                if len(id_types) == 1:
                    print(f"  ✓ All device IDs are type: {id_types.pop()}")
                else:
                    print(f"  ✗ Mixed ID types found: {id_types}")
                    
        else:
            print(f"✗ API returned status code: {response.status_code}")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Error testing route devices API: {e}")
        return False
    
    return True

def test_service_order_preview():
    """Test service order preview endpoint"""
    print("\n\nTesting service order preview API...")
    
    try:
        # First, get devices to build cabinet selections
        devices_response = requests.get(f"{BASE_URL}/api/routes/1/devices")
        if devices_response.status_code != 200:
            print("✗ Failed to get devices for route 1")
            return False
            
        devices_data = devices_response.json()
        devices = devices_data.get('devices', [])
        
        if not devices:
            print("✗ No devices found on route 1")
            return False
        
        # Build cabinet selections (select first cabinet of first device)
        cabinet_selections = []
        first_device = devices[0]
        if 'cabinets' in first_device and first_device['cabinets']:
            cabinet_selections.append({
                'deviceId': first_device['id'],
                'cabinetIndex': first_device['cabinets'][0]['cabinetIndex']
            })
        
        # Test service order preview
        tomorrow = (time.time() + 86400)
        service_date = time.strftime('%Y-%m-%d', time.localtime(tomorrow))
        
        preview_data = {
            'routeId': 1,
            'serviceDate': service_date,
            'cabinetSelections': cabinet_selections
        }
        
        response = requests.post(
            f"{BASE_URL}/api/service-orders/preview",
            json=preview_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Preview generated successfully")
            print(f"  - Service date: {data.get('serviceDate')}")
            print(f"  - Total units: {data.get('totalUnits')}")
            print(f"  - Total products: {data.get('totalProducts')}")
            print(f"  - Days until service: {data.get('daysUntilService')}")
        else:
            print(f"✗ Preview API returned status code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing service order preview: {e}")
        return False
        
    return True

def main():
    """Run all tests"""
    print("Route Schedule Fix Verification Tests")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/auth/current-user")
        if response.status_code == 401:
            print("✓ Server is running (authentication required)")
        elif response.status_code == 200:
            print("✓ Server is running (authenticated)")
        else:
            print(f"? Server returned unexpected status: {response.status_code}")
    except:
        print("✗ Cannot connect to server at", BASE_URL)
        print("  Make sure Flask server is running: python app.py")
        return
    
    # Run tests
    tests_passed = 0
    tests_total = 2
    
    if test_route_devices_api():
        tests_passed += 1
    
    if test_service_order_preview():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")

if __name__ == "__main__":
    main()