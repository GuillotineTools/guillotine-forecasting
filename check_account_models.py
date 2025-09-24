import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

# Test if we can make a direct API call to OpenRouter to check account-specific models
import httpx

async def check_account_specific_models():
    print("Checking account-specific model availability...")
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("[FAIL] OPENROUTER_API_KEY not found")
        return
    
    print("[PASS] API key found")
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Try to get account information
            response = await client.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers=headers,
                timeout=30.0
            )
            
            print(f"Auth Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"[PASS] Retrieved account info")
                print(f"Account data: {data}")
            else:
                print(f"[INFO] Auth endpoint not available or requires different permissions")
                print(f"Status: {response.status_code}")
                
            # Try a simple test call to see what models work
            test_models = [
                "openrouter/openai/gpt-4o-mini",
                "openrouter/openai/gpt-4o",
                "openrouter/moonshotai/kimi-k2-0905",
                "openrouter/deepseek/deepseek-r1"
            ]
            
            test_prompt = {"messages": [{"role": "user", "content": "What is 2+2?"}]}
            
            print("\nTesting model availability via direct API calls:")
            for model in test_models:
                try:
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": "What is 2+2? Just give the number."}],
                            "max_tokens": 10
                        },
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        answer = result['choices'][0]['message']['content'].strip()
                        print(f"  [PASS] {model}: {answer}")
                    else:
                        error_data = response.json() if response.content else {"error": "No response"}
                        print(f"  [FAIL] {model}: {response.status_code} - {error_data}")
                        
                except Exception as e:
                    print(f"  [FAIL] {model}: Exception - {e}")
                
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_account_specific_models())