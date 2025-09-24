import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Environment variable check:")
print(f"OPENROUTER_API_KEY: {'SET' if os.getenv('OPENROUTER_API_KEY') else 'NOT SET'}")
if os.getenv('OPENROUTER_API_KEY'):
    print(f"API Key length: {len(os.getenv('OPENROUTER_API_KEY'))} characters")

# Also check from the .env file directly
import pathlib
env_path = pathlib.Path('.') / '.env'
if env_path.exists():
    print(".env file exists")
    with open(env_path, 'r') as f:
        content = f.read()
        if 'OPENROUTER_API_KEY' in content:
            print("OPENROUTER_API_KEY found in .env file")
        else:
            print("OPENROUTER_API_KEY NOT found in .env file")
else:
    print(".env file does not exist")