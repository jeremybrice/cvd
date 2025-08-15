#!/usr/bin/env python3
"""Test script to check what the routes API is returning"""

import requests
import json

# Test the route devices endpoint
url = "http://localhost:5000/api/routes/1/devices"

try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(f"Route Name: {data.get('routeName')}")
        print(f"Number of devices: {len(data.get('devices', []))}")
        print("\nFirst 5 devices:")
        for i, device in enumerate(data.get('devices', [])[:5]):
            print(f"  Device {i+1}:")
            print(f"    id: {device.get('id')}")
            print(f"    asset: {device.get('asset')}")
            print(f"    cooler: {device.get('cooler')}")
            print(f"    location: {device.get('location')}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Failed to connect: {e}")
    print("Make sure the Flask server is running on port 5000")