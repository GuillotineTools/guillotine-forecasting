import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

# Test to find correct model IDs
import httpx

async def find_correct_model_ids():
    print("Finding correct model IDs...")
    
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
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                
                # Look for the exact models we want and their correct IDs
                target_models = {
                    'kimi': [],
                    'deepseek': [],
                    'qwen': [],
                    'mistral': [],
                    'bytedance': [],
                    'wizardlm': [],
                    'gpt-4o': []
                }
                
                for model in models:
                    model_id = model.get('id', '')
                    model_name = model_id.lower()
                    
                    for target in target_models:
                        if target in model_name:
                            target_models[target].append(model_id)
                
                print("Found model IDs:")
                for target, model_list in target_models.items():
                    if model_list:
                        print(f"\n{target.upper()} models:")
                        for model in sorted(model_list)[:5]:  # Show first 5
                            print(f"  - {model}")
                            
                # Let's also check what models work by trying a few
                print("\nTesting a few models to see what actually works:")
                test_models = []
                for target in ['gpt-4o-mini', 'gpt-4o']:
                    matches = [m for m in models if target in m.get('id', '')]
                    test_models.extend([m.get('id') for m in matches[:2]])  # Test first 2 matches
                
                # Also test some of the target models
                for target in ['kimi', 'deepseek', 'qwen']:
                    matches = [m for m in models if target in m.get('id', '')]
                    test_models.extend([m.get('id') for m in matches[:1]])  # Test first match
                
                test_prompt = {"messages": [{"role": "user", "content": "2+2="}]}
                
                for model in test_models[:10]:  # Test first 10 models
                    try:
                        response = await client.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers=headers,
                            json={
                                "model": model,
                                "messages": [{"role": "user", "content": "2+2="}],
                                "max_tokens": 10
                            },
                            timeout=15.0
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            answer = result['choices'][0]['message']['content'].strip()
                            print(f"  [WORKS] {model}: {answer}")
                        else:
                            print(f"  [FAIL] {model}: {response.status_code}")
                            
                    except Exception as e:
                        print(f"  [ERROR] {model}: {type(e).__name__}")
                        
            else:
                print(f"[FAIL] Status {response.status_code}")
                
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(find_correct_model_ids())