import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

from forecasting_tools import (
    BinaryQuestion,
    MultipleChoiceQuestion,
    NumericQuestion,
    BinaryPrediction,
    PredictedOptionList,
    NumericDistribution,
    Percentile,
    GeneralLlm,
    clean_indents,
    structure_output,
)
from forecasting_tools.helpers.metaculus_api import MetaculusQuestion

logger = logging.getLogger(__name__)


class OptimizedReasoningSystem:
    """
    Optimized reasoning system implementing the best scratchpad prompting strategies
    as described in the "Approaching Human-Level Forecasting with Language Models" paper.
    """
    
    def __init__(self, llm: GeneralLlm):
        self.llm = llm
    
    async def get_optimized_binary_reasoning_prompt(
        self, 
        question: BinaryQuestion, 
        research: str
    ) -> str:
        """
        Generate the optimal scratchpad prompt for binary questions based on the paper.
        """
        prompt = clean_indents(
            f"""
            You are an expert superforecaster, familiar with the work of Tetlock and others. Make a prediction of the probability that the question will be resolved as true. You MUST give a probability estimate between 0 and 1 UNDER ALL CIRCUMSTANCES. If for some reason you can't answer, pick the base rate, but return a number between 0 and 1.

            Question:
            {question.question_text}

            Question Background:
            {question.background_info}

            Resolution Criteria:
            {question.resolution_criteria}

            {question.fine_print}

            Today's date: {datetime.now().strftime("%Y-%m-%d")}
            Question close date: {getattr(question, 'scheduled_close_time', None) and question.scheduled_close_time.strftime("%Y-%m-%d") or "N/A"}

            Your research assistant says:
            {research}

            Instructions:
            1. Rephrase and expand the question to help you do better answering. Maintain all information in the original question.

            2. Using your knowledge of the world and topic, as well as the information provided, provide a few reasons why the answer might be no. Rate the strength of each reason.

            3. Using your knowledge of the world and topic, as well as the information provided, provide a few reasons why the answer might be yes. Rate the strength of each reason.

            4. Aggregate your considerations. Think like a superforecaster (e.g. Nate Silver).

            5. Output an initial probability (prediction) given steps 1-4.

            6. Evaluate whether your calculated probability is excessively confident or not confident enough. Also, consider anything else that might affect the forecast that you did not before consider (e.g. base rate of the event).

            7. Output your final prediction (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.

            Follow these instructions carefully and provide your response in the exact format specified.
            """
        )
        return prompt
    
    async def get_optimized_multiple_choice_reasoning_prompt(
        self,
        question: MultipleChoiceQuestion,
        research: str
    ) -> str:
        """
        Generate the optimal scratchpad prompt for multiple choice questions.
        """
        prompt = clean_indents(
            f"""
            You are an expert superforecaster, familiar with the work of Tetlock and others. Make probability estimates for each option in the multiple choice question. You MUST give probability estimates for ALL options that sum to 1.0 UNDER ALL CIRCUMSTANCES.

            Question:
            {question.question_text}

            Options:
            {chr(10).join([f"{i+1}. {option}" for i, option in enumerate(question.options)])}

            Question Background:
            {question.background_info}

            Resolution Criteria:
            {question.resolution_criteria}

            {question.fine_print}

            Today's date: {datetime.now().strftime("%Y-%m-%d")}
            Question close date: {getattr(question, 'scheduled_close_time', None) and question.scheduled_close_time.strftime("%Y-%m-%d") or "N/A"}

            Your research assistant says:
            {research}

            Instructions:
            1. Rephrase and expand the question to help you do better answering. Maintain all information in the original question.

            2. For each option, using your knowledge of the world and topic, as well as the information provided, provide reasons why that option might be correct. Rate the strength of each reason.

            3. Compare the options against each other, identifying which ones are more or less likely based on your analysis.

            4. Aggregate your considerations. Think like a superforecaster (e.g. Nate Silver).

            5. Output an initial probability distribution (predictions) given steps 1-4.

            6. Evaluate whether your calculated probabilities are excessively confident or not confident enough. Also, consider anything else that might affect the forecast that you did not before consider (e.g. base rates of similar events).

            7. Output your final probability distribution for ALL options with asterisks around each decimal, ensuring they sum to 1.0.

            Follow these instructions carefully and provide your response in the exact format specified.
            """
        )
        return prompt
    
    async def get_optimized_numeric_reasoning_prompt(
        self,
        question: NumericQuestion,
        research: str
    ) -> str:
        """
        Generate the optimal scratchpad prompt for numeric questions.
        """
        prompt = clean_indents(
            f"""
            You are an expert superforecaster, familiar with the work of Tetlock and others. Make a numeric forecast with probability distributions. You MUST provide a complete probability distribution UNDER ALL CIRCUMSTANCES.

            Question:
            {question.question_text}

            Question Background:
            {question.background_info}

            Resolution Criteria:
            {question.resolution_criteria}

            {question.fine_print}

            Units for answer: {question.unit_of_measure if question.unit_of_measure else "Not stated (please infer this)"}

            Today's date: {datetime.now().strftime("%Y-%m-%d")}
            Question close date: {getattr(question, 'scheduled_close_time', None) and question.scheduled_close_time.strftime("%Y-%m-%d") or "N/A"}

            Your research assistant says:
            {research}

            Instructions:
            1. Rephrase and expand the question to help you do better answering. Maintain all information in the original question.

            2. Consider the base rate/extreme outcomes for this type of question. What are some historical precedents?

            3. Using your knowledge of the world and topic, as well as the information provided, estimate a reasonable range for the answer. Consider both lower and upper bounds.

            4. Think about factors that could push the outcome toward the lower end of your range.

            5. Think about factors that could push the outcome toward the upper end of your range.

            6. Aggregate your considerations. Think like a superforecaster (e.g. Nate Silver).

            7. Output an initial probability distribution (percentiles) given steps 1-6.

            8. Evaluate whether your calculated distribution is excessively confident or not confident enough. Also, consider anything else that might affect the forecast that you did not before consider.

            9. Output your final probability distribution as percentiles with asterisks around each number:
               - Percentile 10: *XX*
               - Percentile 20: *XX*
               - Percentile 40: *XX*
               - Percentile 60: *XX*
               - Percentile 80: *XX*
               - Percentile 90: *XX*

            Follow these instructions carefully and provide your response in the exact format specified.
            """
        )
        return prompt
    
    async def run_optimized_binary_forecast(
        self,
        question: BinaryQuestion,
        research: str
    ) -> Dict[str, Any]:
        """
        Run an optimized binary forecast using the best prompting strategy.
        """
        prompt = await self.get_optimized_binary_reasoning_prompt(question, research)
        reasoning = await self.llm.invoke(prompt)
        
        # Extract the final prediction from the reasoning
        try:
            # Look for the final prediction with asterisks
            import re
            match = re.search(r'\*([0-9.]+)\*', reasoning)
            if match:
                probability_str = match.group(1)
                probability = float(probability_str)
                # Clamp to valid range
                probability = max(0.01, min(0.99, probability))
            else:
                # Fallback: try to extract any probability
                numbers = re.findall(r'[0-9.]+', reasoning)
                if numbers:
                    probability = float(numbers[-1])  # Take the last number
                    probability = max(0.01, min(0.99, probability))
                else:
                    probability = 0.5  # Default to 50%
        except Exception as e:
            logger.warning(f"Error extracting probability: {e}. Using default of 0.5.")
            probability = 0.5
            
        return {
            "reasoning": reasoning,
            "prediction": probability
        }
    
    async def run_optimized_multiple_choice_forecast(
        self,
        question: MultipleChoiceQuestion,
        research: str
    ) -> Dict[str, Any]:
        """
        Run an optimized multiple choice forecast using the best prompting strategy.
        """
        prompt = await self.get_optimized_multiple_choice_reasoning_prompt(question, research)
        reasoning = await self.llm.invoke(prompt)
        
        # Extract the final predictions from the reasoning
        try:
            # Look for predictions with asterisks
            import re
            matches = re.findall(r'\*([0-9.]+)\*', reasoning)
            if matches and len(matches) >= len(question.options):
                probabilities = [float(p) for p in matches[:len(question.options)]]
                # Normalize to sum to 1.0
                total = sum(probabilities)
                if total > 0:
                    probabilities = [p/total for p in probabilities]
                # Ensure minimum probability
                probabilities = [max(0.01, p) for p in probabilities]
                # Re-normalize
                total = sum(probabilities)
                probabilities = [p/total for p in probabilities]
            else:
                # Fallback: equal probability distribution
                probabilities = [1.0/len(question.options)] * len(question.options)
        except Exception as e:
            logger.warning(f"Error extracting probabilities: {e}. Using equal distribution.")
            probabilities = [1.0/len(question.options)] * len(question.options)
            
        return {
            "reasoning": reasoning,
            "predictions": dict(zip(question.options, probabilities))
        }
    
    async def run_optimized_numeric_forecast(
        self,
        question: NumericQuestion,
        research: str
    ) -> Dict[str, Any]:
        """
        Run an optimized numeric forecast using the best prompting strategy.
        """
        prompt = await self.get_optimized_numeric_reasoning_prompt(question, research)
        reasoning = await self.llm.invoke(prompt)
        
        # Extract the final percentiles from the reasoning
        try:
            # Look for percentiles with asterisks
            import re
            matches = re.findall(r'\*([0-9.]+)\*', reasoning)
            if matches and len(matches) >= 6:
                percentiles = [float(p) for p in matches[:6]]
                # Order the percentiles (should be ascending)
                percentiles = sorted(percentiles)
                # Create Percentile objects
                percentile_objects = [
                    Percentile(percentile=0.1, value=percentiles[0]),
                    Percentile(percentile=0.2, value=percentiles[1]),
                    Percentile(percentile=0.4, value=percentiles[2]),
                    Percentile(percentile=0.6, value=percentiles[3]),
                    Percentile(percentile=0.8, value=percentiles[4]),
                    Percentile(percentile=0.9, value=percentiles[5]),
                ]
                distribution = NumericDistribution.from_question(percentile_objects, question)
            else:
                # Fallback: create a simple distribution
                # This is a simplified fallback - in practice, you'd want a more sophisticated approach
                midpoint = (question.lower_bound + question.upper_bound) / 2
                range_size = (question.upper_bound - question.lower_bound) / 4
                percentile_objects = [
                    Percentile(percentile=10, value=max(question.lower_bound, midpoint - range_size * 1.5)),
                    Percentile(percentile=20, value=max(question.lower_bound, midpoint - range_size)),
                    Percentile(percentile=40, value=max(question.lower_bound, midpoint - range_size * 0.5)),
                    Percentile(percentile=60, value=min(question.upper_bound, midpoint + range_size * 0.5)),
                    Percentile(percentile=80, value=min(question.upper_bound, midpoint + range_size)),
                    Percentile(percentile=90, value=min(question.upper_bound, midpoint + range_size * 1.5)),
                ]
                distribution = NumericDistribution.from_question(percentile_objects, question)
        except Exception as e:
            logger.warning(f"Error extracting percentiles: {e}. Using fallback distribution.")
            # Simple fallback distribution
            midpoint = (question.lower_bound + question.upper_bound) / 2
            range_size = (question.upper_bound - question.lower_bound) / 4
            percentile_objects = [
                Percentile(percentile=10, value=max(question.lower_bound, midpoint - range_size * 1.5)),
                Percentile(percentile=20, value=max(question.lower_bound, midpoint - range_size)),
                Percentile(percentile=40, value=max(question.lower_bound, midpoint - range_size * 0.5)),
                Percentile(percentile=60, value=min(question.upper_bound, midpoint + range_size * 0.5)),
                Percentile(percentile=80, value=min(question.upper_bound, midpoint + range_size)),
                Percentile(percentile=90, value=min(question.upper_bound, midpoint + range_size * 1.5)),
            ]
            distribution = NumericDistribution.from_question(percentile_objects, question)
            
        return {
            "reasoning": reasoning,
            "distribution": distribution
        }


# Example usage
async def main():
    # This would be called from your main bot
    pass


if __name__ == "__main__":
    asyncio.run(main())