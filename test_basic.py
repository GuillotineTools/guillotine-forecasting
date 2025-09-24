import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

# Test if environment variables are loaded
print("Environment variables check:")
print(f"METACULUS_TOKEN: {'SET' if os.getenv('METACULUS_TOKEN') else 'NOT SET'}")
print(f"OPENROUTER_API_KEY: {'SET' if os.getenv('OPENROUTER_API_KEY') else 'NOT SET'}")
print(f"OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")

# Test importing forecasting-tools
try:
    from forecasting_tools import MetaculusApi, GeneralLlm
    print("forecasting-tools package imported successfully")
except ImportError as e:
    print(f"Error importing forecasting-tools: {e}")

# Test basic async functionality
async def test_async():
    print("Async functionality works")

print("Running basic tests...")
asyncio.run(test_async())
print("All basic tests completed successfully")