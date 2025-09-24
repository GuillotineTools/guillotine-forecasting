import os
import requests
import json

def check_available_models():
    print("Checking available models through OpenRouter API...")
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("[FAIL] OPENROUTER_API_KEY not found in environment variables")
        return
    
    print("[PASS] OPENROUTER_API_KEY is set")
    
    # Try to get available models from OpenRouter
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Check if we can make a simple API call
        response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
        
        if response.status_code == 200:
            models_data = response.json()
            print(f"[PASS] Successfully retrieved models list")
            print(f"Total models available: {len(models_data.get('data', []))}")
            
            # Look for models that might be similar to the ones we want
            target_models = [
                "kimi", "moonshot", "deepseek", "qwen", "mistral", "bytedance", "wizardlm"
            ]
            
            available_models = []
            for model in models_data.get('data', []):
                model_id = model.get('id', '').lower()
                for target in target_models:
                    if target in model_id:
                        available_models.append(model_id)
                        break
            
            print(f"\nFound these potentially relevant models:")
            for model in sorted(set(available_models))[:10]:  # Show first 10
                print(f"  - {model}")
                
            # Check specifically for gpt models that we know work
            gpt_models = [model for model in models_data.get('data', []) 
                         if 'gpt' in model.get('id', '').lower()]
            print(f"\nAvailable GPT models:")
            for model in sorted([m.get('id') for m in gpt_models]):
                print(f"  - {model}")
                
        else:
            print(f"[FAIL] Failed to retrieve models list. Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"[FAIL] Error checking available models: {e}")

if __name__ == "__main__":
    check_available_models()