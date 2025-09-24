import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi, GeneralLlm

async def test_basic_forecasting():
    try:
        print("Testing basic forecasting functionality...")
        
        # Test LLM functionality
        print("Testing LLM functionality...")
        llm = GeneralLlm(
            model="openrouter/openai/gpt-4o-mini",
            temperature=0.3,
            timeout=30,
            allowed_tries=2,
        )
        
        test_prompt = "What is 2+2? Just give the answer as a number."
        try:
            response = await llm.invoke(test_prompt)
            print(f"LLM response: {response}")
        except Exception as e:
            print(f"LLM test failed: {e}")
            
        # Test question fetching
        print("Testing question fetching...")
        test_url = MetaculusApi.TEST_QUESTION_URLS[0]  # Human extinction question
        question = MetaculusApi.get_question_by_url(test_url)
        print(f"Successfully fetched question: {question.question_text}")
        
        print("Basic forecasting test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error in basic forecasting test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_basic_forecasting())
    if result:
        print("\n[PASS] All tests passed! The bot is ready to run.")
    else:
        print("\n[FAIL] Some tests failed. Please check the errors above.")