import os
from dotenv import load_dotenv
load_dotenv()

# Check the API key format
api_key = os.getenv('OPENROUTER_API_KEY')
if api_key:
    print(f"API Key prefix: {api_key[:10]}...")
    print(f"API Key length: {len(api_key)}")
    
    # Check if it's a v1 key
    if api_key.startswith('sk-or-v1'):
        print("This is a v1 OpenRouter key")
    elif api_key.startswith('sk-or'):
        print("This is an OpenRouter key")
    else:
        print("This is a different type of key")
        
    # Let's also check if there are any other OpenRouter-related environment variables
    env_vars = [key for key in os.environ.keys() if 'OPENROUTER' in key or 'LITELLM' in key]
    print(f"\\nRelated environment variables: {env_vars}")
    
    for var in env_vars:
        value = os.getenv(var)
        if value and len(value) > 10:
            print(f"{var}: {value[:10]}...{value[-4:]}")
        else:
            print(f"{var}: {value}")
else:
    print("No API key found")