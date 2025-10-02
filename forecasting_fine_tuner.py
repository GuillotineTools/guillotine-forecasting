"""
Self-supervised fine-tuning for forecasting models based on the paper
"Approaching Human-Level Forecasting with Language Models"

This module implements the fine-tuning approach described in Section 5.1 of the paper,
where we generate multiple candidate forecasts, select those that outperform the crowd,
and fine-tune a model on the successful reasonings.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import datetime

from fallback_llm import FallbackLLM, create_default_fallback_llm
import main  # For accessing question data and evaluation

logger = logging.getLogger(__name__)

@dataclass
class FineTuningExample:
    """A single fine-tuning example"""
    question: str
    background: str
    resolution_criteria: str
    retrieved_info: str
    reasoning: str
    prediction: float
    crowd_prediction: float
    brier_score: float

class ForecastingFineTuner:
    """
    Implements self-supervised fine-tuning for forecasting models.

    Based on the paper's approach:
    1. Generate multiple candidate forecasts per question
    2. Select those that outperform the human crowd
    3. Fine-tune on successful reasonings
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_llm = create_default_fallback_llm(api_key)

    async def generate_candidate_forecasts(
        self,
        question: Dict[str, Any],
        num_candidates: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple candidate forecasts for a single question using different approaches.

        Args:
            question: Question data with background, resolution criteria, etc.
            num_candidates: Number of different forecast attempts

        Returns:
            List of forecast results with reasoning and predictions
        """
        candidates = []

        # Different prompt variations for diversity
        prompt_templates = [
            self._get_standard_prompt(),
            self._get_conservative_prompt(),
            self._get_optimistic_prompt(),
            self._get_detailed_analysis_prompt(),
        ]

        # Generate candidates with different prompts and slight variations
        for i in range(num_candidates):
            prompt_template = prompt_templates[i % len(prompt_templates)]

            # Add some variation to temperature for diversity
            temperature = 0.3 + (i % 3) * 0.2  # 0.3, 0.5, 0.7 cycling

            try:
                forecast_result = await self._generate_single_forecast(
                    question, prompt_template, temperature
                )
                candidates.append(forecast_result)
            except Exception as e:
                logger.warning(f"Failed to generate candidate {i}: {e}")
                continue

        return candidates

    def _get_standard_prompt(self) -> str:
        """Standard forecasting prompt based on our current system"""
        return """
You are an expert superforecaster. Make a prediction about this question.

Question: {question}
Background: {background}
Resolution Criteria: {resolution_criteria}

Retrieved Information:
{retrieved_info}

Follow this 4-step reasoning process:

=== STEP 1: QUESTION UNDERSTANDING ===
Rephrase and expand the question to ensure complete understanding.

=== STEP 2: DUAL ARGUMENT ANALYSIS ===
Provide balanced arguments for YES and NO outcomes, with strength assessments.

=== STEP 3: WEIGHTED AGGREGATION ===
Weigh the factors and aggregate into an initial probability estimate.

=== STEP 4: CALIBRATION AND FINAL ASSESSMENT ===
Check for biases and provide final calibrated probability.

Final Probability: [decimal between 0 and 1]
"""

    def _get_conservative_prompt(self) -> str:
        """More conservative forecasting approach"""
        return """
You are a cautious superforecaster who emphasizes base rates and historical precedents.

Question: {question}
Background: {background}
Resolution Criteria: {resolution_criteria}

Retrieved Information:
{retrieved_info}

Be conservative in your estimate. World events rarely change dramatically. Consider:
- Historical precedents for similar events
- Base rates of success/failure
- Status quo bias

Provide your reasoning and final probability.
Final Probability: [decimal between 0 and 1]
"""

    def _get_optimistic_prompt(self) -> str:
        """More optimistic forecasting approach"""
        return """
You are an optimistic superforecaster who looks for positive indicators and potential breakthroughs.

Question: {question}
Background: {background}
Resolution Criteria: {resolution_criteria}

Retrieved Information:
{retrieved_info}

Look for reasons why this could happen sooner or more successfully than expected. Consider:
- Recent positive developments
- Accelerating trends
- Potential catalysts

Provide your reasoning and final probability.
Final Probability: [decimal between 0 and 1]
"""

    def _get_detailed_analysis_prompt(self) -> str:
        """Detailed analytical approach"""
        return """
You are a systematic analyst. Break down this forecasting question methodically.

Question: {question}
Background: {background}
Resolution Criteria: {resolution_criteria}

Retrieved Information:
{retrieved_info}

Create a decision tree or probability tree analysis. Consider:
- Key uncertainties and their probabilities
- Conditional dependencies
- Sensitivity analysis

Provide detailed reasoning and final probability.
Final Probability: [decimal between 0 and 1]
"""

    async def _generate_single_forecast(
        self,
        question: Dict[str, Any],
        prompt_template: str,
        temperature: float = 0.5
    ) -> Dict[str, Any]:
        """Generate a single forecast using the given prompt template"""

        # Get retrieved information (simplified for now - in practice would use actual retrieval)
        retrieved_info = question.get('retrieved_info', 'No additional information available.')

        # Format the prompt
        prompt = prompt_template.format(
            question=question['title'],
            background=question.get('description', ''),
            resolution_criteria=question.get('resolution_criteria', ''),
            retrieved_info=retrieved_info
        )

        # Generate forecast
        response = await self.base_llm.invoke(prompt)

        # Parse the prediction from response
        prediction = self._extract_prediction(response)

        return {
            'question': question['title'],
            'response': response,
            'prediction': prediction,
            'temperature': temperature,
            'prompt_type': prompt_template.split('\n')[1].strip() if '\n' in prompt_template else 'standard'
        }

    def _extract_prediction(self, response: str) -> float:
        """Extract probability prediction from LLM response"""
        import re

        # Look for patterns like "Final Probability: 0.25" or "*0.75*"
        patterns = [
            r'Final Probability:\s*([0-9]*\.?[0-9]+)',
            r'\*([0-9]*\.?[0-9]+)\*',
            r'Probability:\s*([0-9]*\.?[0-9]+)',
            r'([0-9]*\.?[0-9]+)'  # Last resort - any number
        ]

        for pattern in patterns:
            matches = re.findall(pattern, response)
            if matches:
                try:
                    pred = float(matches[-1])  # Take the last match
                    if 0 <= pred <= 1:
                        return pred
                except ValueError:
                    continue

        # Default to 0.5 if no valid prediction found
        logger.warning(f"Could not extract valid prediction from response: {response[:200]}...")
        return 0.5

    def select_successful_forecasts(
        self,
        candidates: List[Dict[str, Any]],
        actual_outcome: float,
        crowd_prediction: float
    ) -> List[FineTuningExample]:
        """
        Select forecasts that outperform the crowd for fine-tuning.

        Args:
            candidates: List of forecast candidates
            actual_outcome: True outcome (0 or 1)
            crowd_prediction: Crowd's average prediction

        Returns:
            List of successful examples for fine-tuning
        """
        successful_examples = []

        crowd_brier = (crowd_prediction - actual_outcome) ** 2

        for candidate in candidates:
            candidate_brier = (candidate['prediction'] - actual_outcome) ** 2

            # Select if candidate outperforms crowd
            if candidate_brier < crowd_brier:
                # Additional filtering as per paper: avoid overconfidence
                prediction_diff = abs(candidate['prediction'] - crowd_prediction)
                if prediction_diff <= 0.15:  # Not too different from crowd
                    example = FineTuningExample(
                        question=candidate['question'],
                        background="",  # Would need to be populated
                        resolution_criteria="",
                        retrieved_info="",
                        reasoning=candidate['response'],
                        prediction=candidate['prediction'],
                        crowd_prediction=crowd_prediction,
                        brier_score=candidate_brier
                    )
                    successful_examples.append(example)

        return successful_examples

    def prepare_fine_tuning_data(
        self,
        successful_examples: List[FineTuningExample]
    ) -> List[Dict[str, str]]:
        """
        Prepare examples in the format expected for fine-tuning.

        Returns format suitable for OpenAI fine-tuning or similar.
        """
        fine_tuning_data = []

        for example in successful_examples:
            # Create input-output pair
            input_text = f"Question: {example.question}\nBackground: {example.background}\nResolution Criteria: {example.resolution_criteria}\nRetrieved Information: {example.retrieved_info}"

            # Mix candidate prediction with crowd prediction as per paper
            adjusted_prediction = (example.prediction + example.crowd_prediction) / 2

            output_text = f"{example.reasoning}\nFinal Probability: {adjusted_prediction}"

            fine_tuning_data.append({
                "messages": [
                    {"role": "user", "content": input_text},
                    {"role": "assistant", "content": output_text}
                ]
            })

        return fine_tuning_data

    async def run_fine_tuning_pipeline(
        self,
        questions: List[Dict[str, Any]],
        max_questions: int = 50
    ) -> List[Dict[str, str]]:
        """
        Run the complete fine-tuning pipeline on a set of questions.

        Args:
            questions: List of question data
            max_questions: Maximum questions to process

        Returns:
            Fine-tuning data ready for model training
        """
        all_successful_examples = []

        logger.info(f"Starting fine-tuning pipeline with {min(len(questions), max_questions)} questions")

        for i, question in enumerate(questions[:max_questions]):
            logger.info(f"Processing question {i+1}/{min(len(questions), max_questions)}: {question.get('title', '')[:50]}...")

            try:
                # Generate candidate forecasts
                candidates = await self.generate_candidate_forecasts(question)

                # For demo purposes, simulate crowd prediction and outcome
                # In practice, would use actual historical data
                crowd_prediction = 0.5  # Placeholder
                actual_outcome = 0.0 if "will" in question.get('title', '').lower() else 1.0  # Very simplistic

                # Select successful forecasts
                successful = self.select_successful_forecasts(
                    candidates, actual_outcome, crowd_prediction
                )

                all_successful_examples.extend(successful)
                logger.info(f"Generated {len(successful)} successful examples from {len(candidates)} candidates")

            except Exception as e:
                logger.error(f"Failed to process question {i+1}: {e}")
                continue

        # Prepare fine-tuning data
        fine_tuning_data = self.prepare_fine_tuning_data(all_successful_examples)

        logger.info(f"Generated {len(fine_tuning_data)} fine-tuning examples")

        return fine_tuning_data

# Utility functions for integration with main system

async def generate_fine_tuning_dataset(
    api_key: str,
    output_file: str = "forecasting_fine_tune_data.jsonl",
    max_questions: int = 100
) -> None:
    """
    Generate a fine-tuning dataset using the ForecastingFineTuner.

    Args:
        api_key: OpenRouter API key
        output_file: Output file for fine-tuning data
        max_questions: Maximum questions to process
    """
    tuner = ForecastingFineTuner(api_key)

    # In practice, would load actual question data
    # For demo, create sample questions
    sample_questions = [
        {
            "title": "Will the oldest human as of 2100 be over 130 years old?",
            "description": "The current record is 122 years. Advances in medicine may extend it.",
            "resolution_criteria": "Official Guinness record for oldest verified human age as of January 1, 2100.",
            "retrieved_info": "Recent research shows promising anti-aging therapies..."
        }
    ] * max_questions  # Duplicate for testing

    fine_tuning_data = await tuner.run_fine_tuning_pipeline(sample_questions, max_questions)

    # Save to JSONL format for OpenAI fine-tuning
    with open(output_file, 'w') as f:
        for example in fine_tuning_data:
            f.write(json.dumps(example) + '\n')

    logger.info(f"Saved {len(fine_tuning_data)} examples to {output_file}")

if __name__ == "__main__":
    # Example usage
    import os
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        asyncio.run(generate_fine_tuning_dataset(api_key))
    else:
        print("Please set OPENROUTER_API_KEY environment variable")