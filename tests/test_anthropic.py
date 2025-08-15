#!/usr/bin/env python3
import os
import sys

# Check if API key is set
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print("❌ ANTHROPIC_API_KEY environment variable is NOT set")
    print("\nTo fix this, run:")
    print('export ANTHROPIC_API_KEY="your-actual-api-key-here"')
    sys.exit(1)
else:
    print(f"✓ ANTHROPIC_API_KEY is set (starts with: {api_key[:10]}...)")

# Try to import anthropic
try:
    import anthropic
    print("✓ anthropic package is installed")
    
    # Try to create a client
    try:
        client = anthropic.Anthropic(api_key=api_key)
        print("✓ Anthropic client created successfully")
        
        # Try a simple API call
        try:
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[
                    {"role": "user", "content": "Say 'API test successful' and nothing else"}
                ]
            )
            print(f"✓ API call successful: {response.content[0].text}")
        except Exception as e:
            print(f"❌ API call failed: {e}")
            
    except Exception as e:
        print(f"❌ Failed to create Anthropic client: {e}")
        
except ImportError:
    print("❌ anthropic package is NOT installed")
    print("\nTo fix this, run:")
    print("pip install anthropic==0.57.1")