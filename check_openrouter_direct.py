import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

# Test if we can make a direct API call to OpenRouter
import httpx

async def check_openrouter_models_direct():
    print("Checking OpenRouter models via direct API call...")
    
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
            
            response = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers=headers,
                timeout=30.0
            )
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"[PASS] Retrieved {len(data.get('data', []))} models")
                
                # Look for specific models
                models = data.get('data', [])
                target_providers = ['moonshot', 'deepseek', 'qwen', 'mistral', 'bytedance', 'wizardlm']
                
                found_models = []
                for model in models:
                    model_id = model.get('id', '').lower()
                    for provider in target_providers:
                        if provider in model_id:
                            found_models.append(model_id)
                            break
                
                print(f"Found {len(found_models)} potentially relevant models:")
                for model in sorted(set(found_models))[:10]:
                    print(f"  - {model}")
                    
                # Check for the specific models we want
                specific_models = [
                    "moonshotai/kimi-k2-0905",
                    "deepseek/deepseek-r1",
                    "qwen/qwen3-max",
                    "mistralai/mistral-large",
                    "bytedance/seed-oss-36b-instruct",
                    "microsoft/wizardlm-2-8x22b"
                ]
                
                print("\nChecking for specific models:")
                for model in specific_models:
                    matching = [m for m in models if model in m.get('id', '')]
                    if matching:
                        print(f"  [FOUND] {model}: {len(matching)} variants")
                        for m in matching[:3]:  # Show first 3 variants
                            print(f"    - {m.get('id')}")
                    else:
                        print(f"  [NOT FOUND] {model}")
                        
            else:
                print(f"[FAIL] Status {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_openrouter_models_direct())