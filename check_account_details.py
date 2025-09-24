import os
from dotenv import load_dotenv
load_dotenv()

import asyncio
import httpx

async def check_openrouter_account():
    print("Checking OpenRouter account details...")
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("[FAIL] No API key found")
        print(f"Available env vars: {[k for k in os.environ.keys() if 'OPENROUTER' in k]}")
        return
    
    print(f"[PASS] API key found: {api_key[:10]}...")
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Get account info
            response = await client.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print("[PASS] Retrieved account info")
                account_data = data.get('data', {})
                
                print(f"Label: {account_data.get('label', 'N/A')}")
                print(f"Is Free Tier: {account_data.get('is_free_tier', 'N/A')}")
                print(f"Usage: {account_data.get('usage', 'N/A')}")
                print(f"Limit: {account_data.get('limit', 'N/A')}")
                print(f"Limit Remaining: {account_data.get('limit_remaining', 'N/A')}")
                
                # Check if this is a provisioning key
                if account_data.get('is_provisioning_key', False):
                    print("WARNING: This is a provisioning key, which may have limited model access")
                    
            else:
                print(f"[FAIL] Status {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"[FAIL] Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_openrouter_account())