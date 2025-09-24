#!/usr/bin/env python3
"""
Script to check what's available in MetaculusApi
"""
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

def check_available_classes():
    """Check what's available in MetaculusApi"""
    print("Checking available classes and methods...")
    
    # Check what's in the module
    import forecasting_tools.helpers.metaculus_api as api_module
    print("Available in metaculus_api module:")
    for name in dir(api_module):
        if not name.startswith('_'):
            print(f"  - {name}")
            
    # Check what's in MetaculusApi
    print("\nAvailable in MetaculusApi class:")
    for name in dir(MetaculusApi):
        if not name.startswith('_'):
            print(f"  - {name}")

if __name__ == "__main__":
    check_available_classes()