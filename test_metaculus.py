import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

async def test_metaculus_api():
    try:
        print("Testing Metaculus API connection...")
        # Test if we can get a simple question
        # Using a known public question ID for testing
        question_id = 578  # Human extinction question
        try:
            question = await MetaculusApi.get_question_by_id(question_id)
            print(f"Successfully fetched question: {question.question_text}")
            print(f"Question type: {type(question).__name__}")
        except Exception as e:
            print(f"Could not fetch specific question: {e}")
            # Try to get any open questions
            try:
                questions = await MetaculusApi.get_questions_by_status("open", num_questions=1)
                if questions:
                    print(f"Successfully fetched {len(questions)} open question(s)")
                    print(f"First question: {questions[0].question_text}")
                else:
                    print("No open questions found")
            except Exception as e2:
                print(f"Could not fetch open questions: {e2}")
        
        print("Metaculus API test completed")
    except Exception as e:
        print(f"Error testing Metaculus API: {e}")

if __name__ == "__main__":
    asyncio.run(test_metaculus_api())