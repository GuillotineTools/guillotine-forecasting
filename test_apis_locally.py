#!/usr/bin/env python3
"""
Test both APIs with the current environment variables.
This will help verify if the GitHub Actions environment is working.
"""

import os
import asyncio
from datetime import datetime

os.environ['GITHUB_ACTIONS'] = 'true'

async def test_apis_locally():
    print("🧪 TESTING APIs WITH CURRENT ENVIRONMENT")
    print("=" * 60)
    print(f"Testing at: {datetime.now()}")
    print(f"GITHUB_ACTIONS: {os.environ.get('GITHUB_ACTIONS', 'NOT SET')}")
    print()

    # Check API keys
    metaculus_token = os.getenv('METACULUS_TOKEN')
    openrouter_key = os.getenv('OPENROUTER_API_KEY')

    print(f"🔑 METACULUS_TOKEN:")
    print(f"   Exists: {'✅' if metaculus_token else '❌'}")
    print(f"   Length: {len(metaculus_token) if metaculus_token else 0}")

    print(f"\n🔑 OPENROUTER_API_KEY:")
    print(f"   Exists: {'✅' if openrouter_key else '❌'}")
    print(f"   Length: {len(openrouter_key) if openrouter_key else 0}")
    print(f"   Format: {openrouter_key[:15]}...{openrouter_key[-10:] if openrouter_key and len(openrouter_key) > 25 else openrouter_key}")

    # Test Metaculus API
    print(f"\n📊 TESTING METACULUS API:")
    if metaculus_token and len(metaculus_token) > 20:
        try:
            import requests
            headers = {
                'Authorization': f'Token {metaculus_token}',
                'Content-Type': 'application/json'
            }

            response = requests.get('https://www.metaculus.com/api/posts/39988/', headers=headers)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS: {data.get('title', 'No title')[:60]}...")
                print(f"   Status: {data.get('status', 'Unknown')}")
                print(f"   Type: {data.get('type', 'Unknown')}")

                # Test submission
                print(f"\n🚀 TESTING SUBMISSION:")
                submission_data = [{
                    'question': 39988,
                    'prediction': 0.25  # 25%
                }]

                sub_response = requests.post('https://www.metaculus.com/api/questions/forecast/',
                                           headers=headers, json=submission_data)
                print(f"   Submission Status: {sub_response.status_code}")

                if sub_response.status_code == 200:
                    print(f"   ✅ SUBMISSION SUCCESSFUL!")
                    print(f"   🎯 FORECAST SUBMITTED TO METACULUS")
                    return True
                else:
                    print(f"   ❌ Submission failed: {sub_response.text}")
            else:
                print(f"   ❌ API access failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Metaculus API error: {e}")
    else:
        print(f"   ❌ Invalid or missing Metaculus token")

    # Test OpenRouter API
    print(f"\n🤖 TESTING OPENROUTER API:")
    if openrouter_key and len(openrouter_key) > 20:
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": "Say 'API test successful'"}]
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                message = result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')
                print(f"   ✅ SUCCESS: {message}")
            else:
                print(f"   ❌ API failed: {response.text}")
        except Exception as e:
            print(f"   ❌ OpenRouter API error: {e}")
    else:
        print(f"   ❌ Invalid or missing OpenRouter key")

    return False

if __name__ == "__main__":
    success = asyncio.run(test_apis_locally())

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"api_test_results_{timestamp}.txt", "w") as f:
        f.write(f"API Test Results - {datetime.now()}\n")
        f.write(f"Success: {success}\n")
        f.write(f"GITHUB_ACTIONS: {os.environ.get('GITHUB_ACTIONS', 'NOT SET')}\n")
        f.write(f"METACULUS_TOKEN: {'SET' if os.getenv('METACULUS_TOKEN') else 'NOT SET'}\n")
        f.write(f"OPENROUTER_API_KEY: {'SET' if os.getenv('OPENROUTER_API_KEY') else 'NOT SET'}\n")

    print(f"\n📄 Results saved to: api_test_results_{timestamp}.txt")
    print(f"\n🎯 FINAL RESULT: {'✅ APIs WORKING - SUBMISSION MADE!' if success else '❌ ISSUES DETECTED'}")