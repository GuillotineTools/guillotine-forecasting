import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

def test_metaculus_api_methods():
    try:
        print("Available methods in MetaculusApi:")
        methods = [method for method in dir(MetaculusApi) if not method.startswith('_')]
        for method in methods:
            print(f"  - {method}")
        
        print("\nChecking class attributes:")
        attributes = [attr for attr in dir(MetaculusApi) if not callable(getattr(MetaculusApi, attr)) and not attr.startswith('_')]
        for attr in attributes:
            print(f"  - {attr}: {getattr(MetaculusApi, attr)}")
            
        print("\nMetaculus API test completed")
    except Exception as e:
        print(f"Error testing Metaculus API: {e}")

if __name__ == "__main__":
    test_metaculus_api_methods()