import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

def test_metaculus_api():
    try:
        print("Testing Metaculus API connection...")
        print(f"API Base URL: {MetaculusApi.API_BASE_URL}")
        print(f"Current AI Competition ID: {MetaculusApi.CURRENT_AI_COMPETITION_ID}")
        
        # Test getting a question by URL
        test_url = MetaculusApi.TEST_QUESTION_URLS[0]  # Human extinction question
        print(f"Testing with URL: {test_url}")
        
        try:
            question = MetaculusApi.get_question_by_url(test_url)
            print(f"Successfully fetched question: {question.question_text}")
            print(f"Question type: {type(question).__name__}")
            print(f"Question page URL: {question.page_url}")
            
            # Check available attributes
            print("Available attributes:")
            attributes = [attr for attr in dir(question) if not attr.startswith('_')]
            for attr in attributes[:20]:  # Show first 20 attributes
                try:
                    value = getattr(question, attr)
                    if not callable(value):
                        print(f"  - {attr}: {value}")
                except:
                    print(f"  - {attr}: <could not retrieve>")
            
            # Check callable methods
            print("Available methods:")
            methods = [attr for attr in attributes if callable(getattr(question, attr))]
            for method in methods[:10]:  # Show first 10 methods
                print(f"  - {method}")
                
        except Exception as e:
            print(f"Could not fetch question by URL: {e}")
            import traceback
            traceback.print_exc()
        
        print("Metaculus API test completed")
    except Exception as e:
        print(f"Error testing Metaculus API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_metaculus_api()