#!/usr/bin/env python3
"""
Test script to diagnose why the Anthropic API chatbot is in fallback mode
"""
import os
import sys
import requests
import json

def print_section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)

# 1. Check environment variable
print_section("1. Environment Variable Check")
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print("❌ ANTHROPIC_API_KEY is NOT set in environment")
    print("\nTo fix: Before starting the Flask server, run:")
    print('export ANTHROPIC_API_KEY="your-actual-api-key-here"')
else:
    print(f"✓ ANTHROPIC_API_KEY is set (starts with: {api_key[:10]}...)")

# 2. Check if anthropic package is installed
print_section("2. Python Package Check")
try:
    import anthropic
    print(f"✓ anthropic package is installed (version: {anthropic.__version__})")
except ImportError:
    print("❌ anthropic package is NOT installed")
    print("\nTo fix: Activate your virtual environment and run:")
    print("pip install anthropic==0.57.1")
    sys.exit(1)

# 3. Check if Flask server is running
print_section("3. Flask Server Check")
try:
    response = requests.get('http://localhost:5000/api/health', timeout=2)
    if response.status_code == 200:
        print("✓ Flask server is running on port 5000")
    else:
        print(f"⚠️  Flask server responded with status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Flask server is NOT running")
    print("\nTo fix: In a terminal, run:")
    print("source venv/bin/activate")
    print("python app.py")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error checking Flask server: {e}")

# 4. Test the chat endpoint
print_section("4. Chat Endpoint Test")
try:
    test_message = {
        "message": "Hello, testing API connection",
        "context": {
            "pageContext": {"currentPage": "test"},
            "devices": [],
            "weekly": {},
            "achievements": {}
        }
    }
    
    print(f"Sending test message to /api/chat...")
    response = requests.post(
        'http://localhost:5000/api/chat',
        json=test_message,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        if 'response' in data:
            if 'AI chat is not configured' in data['response']:
                print("❌ API returned fallback message - API key not available to Flask")
                print("\nThe Flask server is not seeing the ANTHROPIC_API_KEY")
                print("Make sure you:")
                print("1. Set the environment variable: export ANTHROPIC_API_KEY='your-key'")
                print("2. Restart the Flask server after setting the variable")
            else:
                print("✓ Chat endpoint responded successfully")
                print(f"Response preview: {data['response'][:100]}...")
        else:
            print(f"⚠️  Unexpected response format: {data}")
    else:
        print(f"❌ Chat endpoint returned error status: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error testing chat endpoint: {e}")

# 5. Direct API test (if key is available)
if api_key:
    print_section("5. Direct Anthropic API Test")
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[{"role": "user", "content": "Say 'API working' and nothing else"}]
        )
        print(f"✓ Direct API call successful: {response.content[0].text}")
    except Exception as e:
        print(f"❌ Direct API call failed: {e}")
        print("\nThis could mean:")
        print("- Invalid API key")
        print("- Network connectivity issues")
        print("- API rate limits or restrictions")

print_section("Summary")
print("\nTo ensure the chatbot works properly:")
print("1. Set ANTHROPIC_API_KEY environment variable")
print("2. Restart the Flask server with the environment variable set")
print("3. The server should pick up the API key and use Anthropic instead of fallback")
print("\nExample commands:")
print("export ANTHROPIC_API_KEY='sk-ant-...'")
print("source venv/bin/activate")
print("python app.py")