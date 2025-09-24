from dotenv import load_dotenv
load_dotenv()
import os
import argparse
import asyncio
import logging
from datetime import datetime
from typing import Literal

from forecasting_tools import (
    AskNewsSearcher,
    BinaryQuestion,
    ForecastBot,
    GeneralLlm,
    MetaculusApi,
    MetaculusQuestion,
    MultipleChoiceQuestion,
    NumericDistribution,
    NumericQuestion,
    Percentile,
    BinaryPrediction,
    PredictedOptionList,
    ReasonedPrediction,
    SmartSearcher,
    clean_indents,
    structure_output,
)
from tenacity import retry, stop_after_attempt, wait_fixed

# Import the enhanced retrieval system
from enhanced_retrieval import EnhancedRetrievalSystem

# Import the optimized reasoning system
from optimized_reasoning import OptimizedReasoningSystem

logger = logging.getLogger(__name__)


class EnhancedTemplateBot2025(ForecastBot):
    """
    Enhanced version of the template bot that combines working model configuration
    with enhanced retrieval and optimized reasoning systems from the research paper.
    """

    def _llm_config_defaults(self) -> dict:
        defaults = super()._llm_config_defaults()
        # Use only available models that work with our API keys
        forecaster_defaults = {
            "forecaster1": {"model": "openrouter/openai/gpt-4o-mini", "api_key": os.getenv('OPENROUTER_API_KEY'), **defaults},
            "forecaster2": {"model": "openrouter/openai/gpt-4o", "api_key": os.getenv('OPENROUTER_API_KEY'), **defaults},
            "forecaster3": {"model": "openrouter/deepseek/deepseek-chat-v3-0324", "api_key": "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", **defaults},
            "forecaster4": {"model": "openrouter/moonshotai/kimi-k2-0905", "api_key": "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", **defaults},
            "forecaster5": {"model": "openrouter/openai/gpt-4o-mini", "api_key": os.getenv('OPENROUTER_API_KEY'), **defaults},
            "forecaster6": {"model": "openrouter/openai/gpt-4o", "api_key": os.getenv('OPENROUTER_API_KEY'), **defaults},
            # Add support models
            "synthesizer": {"model": "openrouter/openai/gpt-4o", "api_key": os.getenv('OPENROUTER_API_KEY'), **defaults},
            "parser": {"model": "openrouter/openai/gpt-4o-mini", "api_key": os.getenv('OPENROUTER_API_KEY'), **defaults},
            "researcher": {"model": "openrouter/openai/gpt-4o-mini", "api_key": os.getenv('OPENROUTER_API_KEY'), **defaults},
        }
        return {**defaults, **forecaster_defaults}

    # Define model names for logging
    forecaster_models = {
        "forecaster1": "openrouter/openai/gpt-4o-mini",
        "forecaster2": "openrouter/openai/gpt-4o",
        "forecaster3": "openrouter/deepseek/deepseek-chat-v3-0324",
        "forecaster4": "openrouter/moonshotai/kimi-k2-0905",
        "forecaster5": "openrouter/openai/gpt-4o-mini",
        "forecaster6": "openrouter/openai/gpt-4o",
        "synthesizer": "openrouter/openai/gpt-4o",
        "parser": "openrouter/openai/gpt-4o-mini",
        "researcher": "openrouter/openai/gpt-4o-mini",
    }

    # Rate limiting configuration - increased for enhanced systems
    _max_concurrent_questions = 1
    _concurrency_limiter = asyncio.Semaphore(_max_concurrent_questions)
    _llm_rate_limiter = asyncio.Semaphore(5)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def run_research(self, question: MetaculusQuestion) -> str:
        async with self._concurrency_limiter:
            research = ""
            researcher = self.get_llm("researcher")

            # Always use enhanced retrieval system
            forecaster_model = self.forecaster_models.get("forecaster1", "openrouter/openai/gpt-4o-mini")
            enhanced_retrieval = EnhancedRetrievalSystem(GeneralLlm(model=forecaster_model))
            research = await enhanced_retrieval.enhanced_retrieve(question)

            logger.info(f"Found Research for URL {question.page_url}:\n{research}")
            return research

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def _run_forecast_on_binary(
        self, question: BinaryQuestion, research: str
    ) -> ReasonedPrediction[float]:
        # Use optimized reasoning system
        use_optimized_reasoning = os.getenv('USE_OPTIMIZED_REASONING', 'true').lower() == 'true'

        if use_optimized_reasoning:
            forecaster_model = self.forecaster_models.get("forecaster1", "openrouter/openai/gpt-4o-mini")
            optimized_reasoning = OptimizedReasoningSystem(GeneralLlm(model=forecaster_model))
            prompt = await optimized_reasoning.get_optimized_binary_reasoning_prompt(question, research)
        else:
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
                Question close date: {question.scheduled_close_time.strftime("%Y-%m-%d") if question.scheduled_close_time else "N/A"}

                Your research assistant says:
                {research}

                Please provide your probability estimate as a decimal number between 0 and 1.
                """
            )

        # Define forecaster models (use all 6 for ensemble)
        forecaster_keys = ["forecaster1", "forecaster2", "forecaster3", "forecaster4", "forecaster5", "forecaster6"]
        individual_reasonings = []
        individual_predictions = []

        # Generate individual forecasts
        for key in forecaster_keys:
            forecaster_model = self.forecaster_models.get(key, "openrouter/openai/gpt-4o-mini")
            llm = GeneralLlm(model=forecaster_model)
            reasoning = await llm.invoke(prompt)
            logger.info(f"Reasoning from {key} for URL {question.page_url}: {reasoning}")

            predicted_value: float = await structure_output(
                text_to_structure=reasoning,
                output_type=float,
                model=GeneralLlm(model=self.forecaster_models.get("parser", "openrouter/openai/gpt-4o-mini")),
            )
            individual_reasonings.append(reasoning)
            individual_predictions.append(predicted_value)
            model_name = self.forecaster_models.get(key, 'unknown')
            logger.info(f"Forecast from {key} ({model_name}) for URL {question.page_url}: {predicted_value}")

        # Synthesize final prediction
        synth_prompt = clean_indents(
            f"""
            You are a synthesizer comparing multiple forecaster outputs for a binary question.

            Question: {question.question_text}

            Individual forecasts:
            """
        )
        for i, (reason, pred) in enumerate(zip(individual_reasonings, individual_predictions), 1):
            synth_prompt += f"\nForecaster {i}: Reasoning: {reason}\nPrediction: {pred}\n"

        synth_prompt += clean_indents(
            f"""
            Compare these forecasts and synthesize a final probability. Consider:
            - Areas of agreement and disagreement
            - Strength of reasoning from each forecaster
            - Base rates and outside view considerations
            - Most likely outcome given all evidence

            Output your final synthesized probability as a single decimal number between 0 and 1.
            """
        )

        synthesizer = self.get_llm("synthesizer")
        synth_reasoning = await synthesizer.invoke(synth_prompt)
        final_pred: float = await structure_output(
            text_to_structure=synth_reasoning,
            output_type=float,
            model=GeneralLlm(model=self.forecaster_models.get("parser", "openrouter/openai/gpt-4o-mini")),
        )

        # Clamp to valid range
        final_pred = max(0.0, min(1.0, final_pred))

        # Create combined reasoning with model names
        combined_reasoning_parts = [
            f"Enhanced Research:\n{research}",
            f"\nSynthesizer Analysis ({self.forecaster_models['synthesizer']}):\n{synth_reasoning}",
            f"\nFinal Probability: {final_pred:.3f}",
            f"\nIndividual Forecaster Contributions:"
        ]

        for i, (reason, pred) in enumerate(zip(individual_reasonings, individual_predictions), 1):
            model_name = self.forecaster_models.get(f"forecaster{i}", 'unknown')
            combined_reasoning_parts.append(f"  {i}. {model_name}: {pred:.3f}")

        combined_reasoning = "\n".join(combined_reasoning_parts)
        return ReasonedPrediction(prediction_value=final_pred, reasoning=combined_reasoning)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def _run_forecast_on_multiple_choice(
        self, question: MultipleChoiceQuestion, research: str
    ) -> ReasonedPrediction[PredictedOptionList]:
        # Use optimized reasoning system
        use_optimized_reasoning = os.getenv('USE_OPTIMIZED_REASONING', 'true').lower() == 'true'

        if use_optimized_reasoning:
            forecaster_model = self.forecaster_models.get("forecaster1", "openrouter/openai/gpt-4o-mini")
            optimized_reasoning = OptimizedReasoningSystem(GeneralLlm(model=forecaster_model))
            prompt = await optimized_reasoning.get_optimized_multiple_choice_reasoning_prompt(question, research)
        else:
            prompt = clean_indents(
                f"""
                You are an expert superforecaster. Make probability estimates for each option in the multiple choice question. You MUST give probability estimates for ALL options that sum to 1.0 UNDER ALL CIRCUMSTANCES.

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
                Question close date: {question.scheduled_close_time.strftime("%Y-%m-%d") if question.scheduled_close_time else "N/A"}

                Your research assistant says:
                {research}

                Please provide your probability estimates for each option.
                """
            )

        parsing_instructions = clean_indents(
            f"""
            Make sure that all option names are one of the following:
            {question.options}
            The text you are parsing may prepend these options with some variation of "Option" which you should remove if not part of the option names I just gave you.
            """
        )

        # Define forecaster models (use 4 forecasters for multiple choice to save time)
        forecaster_keys = ["forecaster1", "forecaster2", "forecaster3", "forecaster4"]
        individual_reasonings = []
        individual_predictions = []

        # Generate individual forecasts
        for key in forecaster_keys:
            forecaster_model = self.forecaster_models.get(key, "openrouter/openai/gpt-4o-mini")
            llm = GeneralLlm(model=forecaster_model)
            reasoning = await llm.invoke(prompt)
            logger.info(f"Reasoning from {key} for URL {question.page_url}: {reasoning}")
            predicted_option_list: PredictedOptionList = await structure_output(
                text_to_structure=reasoning,
                output_type=PredictedOptionList,
                model=GeneralLlm(model=self.forecaster_models.get("parser", "openrouter/openai/gpt-4o-mini")),
                additional_instructions=parsing_instructions,
            )
            individual_reasonings.append(reasoning)
            individual_predictions.append(predicted_option_list)
            model_name = self.forecaster_models.get(key, 'unknown')
            logger.info(f"Forecast from {key} ({model_name}) for URL {question.page_url}: {predicted_option_list}")

        # Synthesize final prediction
        synth_prompt = clean_indents(
            f"""
            You are a synthesizer comparing multiple forecaster outputs for a multiple choice question.

            Question: {question.question_text}
            Options: {question.options}

            Individual forecasts:
            """
        )
        for i, (reason, pred) in enumerate(zip(individual_reasonings, individual_predictions), 1):
            synth_prompt += f"\nForecaster {i}: Reasoning: {reason}\nPrediction: {pred}\n"

        synth_prompt += clean_indents(
            f"""
            Compare these: Highlight agreements/disagreements, resolve via heuristics (base rates, Bayesian updates, Fermi, intangibles, qualitative elements, wide intervals, bias avoidance). Synthesize a final balanced probability distribution.

            Output only the final probabilities for the N options in this order {question.options} as:
            Option_A: Probability_A
            Option_B: Probability_B
            ...
            """
        )

        synthesizer = self.get_llm("synthesizer")
        synth_reasoning = await synthesizer.invoke(synth_prompt)

        final_predicted_option_list: PredictedOptionList = await structure_output(
            text_to_structure=synth_reasoning,
            output_type=PredictedOptionList,
            model=GeneralLlm(model=self.forecaster_models.get("parser", "openrouter/openai/gpt-4o-mini")),
            additional_instructions=parsing_instructions,
        )

        # Create combined reasoning with model names
        combined_reasoning_parts = [
            f"Enhanced Research:\n{research}",
            f"\nSynthesizer Analysis ({self.forecaster_models['synthesizer']}):\n{synth_reasoning}",
            f"\nFinal Predictions: {final_predicted_option_list}",
            f"\nIndividual Forecaster Contributions:"
        ]

        for i, (reason, pred) in enumerate(zip(individual_reasonings, individual_predictions), 1):
            model_name = self.forecaster_models.get(f"forecaster{i}", 'unknown')
            combined_reasoning_parts.append(f"  {i}. {model_name}: {pred}")

        combined_reasoning = "\n".join(combined_reasoning_parts)
        return ReasonedPrediction(
            prediction_value=final_predicted_option_list, reasoning=combined_reasoning
        )

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def _run_forecast_on_numeric(
        self, question: NumericQuestion, research: str
    ) -> ReasonedPrediction[NumericDistribution]:
        # Use optimized reasoning system
        use_optimized_reasoning = os.getenv('USE_OPTIMIZED_REASONING', 'true').lower() == 'true'

        if use_optimized_reasoning:
            forecaster_model = self.forecaster_models.get("forecaster1", "openrouter/openai/gpt-4o-mini")
            optimized_reasoning = OptimizedReasoningSystem(GeneralLlm(model=forecaster_model))
            prompt = await optimized_reasoning.get_optimized_numeric_reasoning_prompt(question, research)
        else:
            prompt = clean_indents(
                f"""
                You are an expert superforecaster. Estimate the numeric value for the question. You MUST provide a forecast under ALL CIRCUMSTANCES.

                Question:
                {question.question_text}

                Question Background:
                {question.background_info}

                Resolution Criteria:
                {question.resolution_criteria}

                {question.fine_print}

                Today's date: {datetime.now().strftime("%Y-%m-%d")}
                Question close date: {question.scheduled_close_time.strftime("%Y-%m-%d") if question.scheduled_close_time else "N/A"}

                Your research assistant says:
                {research}

                Upper Bound: {question.upper_bound}
                Lower Bound: {question.lower_bound}

                Please provide your estimate with percentiles.
                """
            )

        # Define forecaster models (use 4 forecasters for numeric to save time)
        forecaster_keys = ["forecaster1", "forecaster2", "forecaster3", "forecaster4"]
        individual_reasonings = []
        individual_predictions = []

        # Generate individual forecasts
        for key in forecaster_keys:
            forecaster_model = self.forecaster_models.get(key, "openrouter/openai/gpt-4o-mini")
            llm = GeneralLlm(model=forecaster_model)
            reasoning = await llm.invoke(prompt)
            logger.info(f"Reasoning from {key} for URL {question.page_url}: {reasoning}")

            predicted_distribution: NumericDistribution = await structure_output(
                text_to_structure=reasoning,
                output_type=NumericDistribution,
                model=GeneralLlm(model=self.forecaster_models.get("parser", "openrouter/openai/gpt-4o-mini")),
            )
            individual_reasonings.append(reasoning)
            individual_predictions.append(predicted_distribution)
            model_name = self.forecaster_models.get(key, 'unknown')
            logger.info(f"Forecast from {key} ({model_name}) for URL {question.page_url}: {predicted_distribution}")

        # Synthesize final prediction
        synth_prompt = clean_indents(
            f"""
            You are a synthesizer comparing multiple forecaster outputs for a numeric question.

            Question: {question.question_text}
            Range: [{question.lower_bound}, {question.upper_bound}]

            Individual forecasts:
            """
        )
        for i, (reason, pred) in enumerate(zip(individual_reasonings, individual_predictions), 1):
            synth_prompt += f"\nForecaster {i}: Reasoning: {reason}\nPrediction: {pred}\n"

        synth_prompt += clean_indents(
            f"""
            Synthesize these forecasts into a final distribution. Consider areas of agreement/disagreement and reasoning quality.

            Output your final forecast with percentiles.
            """
        )

        synthesizer = self.get_llm("synthesizer")
        synth_reasoning = await synthesizer.invoke(synth_prompt)

        final_predicted_distribution: NumericDistribution = await structure_output(
            text_to_structure=synth_reasoning,
            output_type=NumericDistribution,
            model=GeneralLlm(model=self.forecaster_models.get("parser", "openrouter/openai/gpt-4o-mini")),
        )

        # Create combined reasoning with model names
        combined_reasoning_parts = [
            f"Enhanced Research:\n{research}",
            f"\nSynthesizer Analysis ({self.forecaster_models['synthesizer']}):\n{synth_reasoning}",
            f"\nFinal Distribution: {final_predicted_distribution}",
            f"\nIndividual Forecaster Contributions:"
        ]

        for i, (reason, pred) in enumerate(zip(individual_reasonings, individual_predictions), 1):
            model_name = self.forecaster_models.get(f"forecaster{i}", 'unknown')
            combined_reasoning_parts.append(f"  {i}. {model_name}: {pred}")

        combined_reasoning = "\n".join(combined_reasoning_parts)
        return ReasonedPrediction(
            prediction_value=final_predicted_distribution, reasoning=combined_reasoning
        )


def main():
    """
    Main function to run the enhanced bot.
    """
    parser = argparse.ArgumentParser(description="Run Enhanced Forecasting Bot")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["test_questions", "tournament", "metaculus_cup"],
        default="tournament",
        help="Mode to run the bot in",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish forecasts to Metaculus (only works in tournament mode)",
    )
    run_mode = parser.parse_args().mode
    publish_reports_to_metaculus = parser.parse_args().publish

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Check environment variables
    logger.info("Environment variables check:")
    logger.info(f"METACULUS_TOKEN: {'SET' if os.getenv('METACULUS_TOKEN') else 'NOT SET'}")
    logger.info(f"OPENROUTER_API_KEY: {'SET' if os.getenv('OPENROUTER_API_KEY') else 'NOT SET'}")
    logger.info(f"OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
    logger.info(f"USE_OPTIMIZED_REASONING: {os.getenv('USE_OPTIMIZED_REASONING', 'true')}")

    # Initialize enhanced bot
    template_bot = EnhancedTemplateBot2025(
        research_reports_per_question=1,
        predictions_per_research_report=1,
        publish_reports_to_metaculus=publish_reports_to_metaculus,
    )

    if run_mode == "test_questions":
        logger.info("Starting test questions mode")
        # Create simple test questions
        example_questions = [
            BinaryQuestion(
                question_text="Will it rain tomorrow?",
                resolution_criteria="It will be considered resolved as yes if any measurable precipitation occurs at the location.",
                page_url="dummy://test1",
                scheduled_close_time=datetime(2025, 12, 31)
            ),
            MultipleChoiceQuestion(
                question_text="Which party will win the next election?",
                options=["Party A", "Party B", "Party C"],
                resolution_criteria="The party that wins the most seats will be considered the winner.",
                page_url="dummy://test2",
                scheduled_close_time=datetime(2025, 12, 31)
            ),
            NumericQuestion(
                question_text="What will be the temperature tomorrow?",
                resolution_criteria="The temperature at noon will be used.",
                lower_bound=0,
                upper_bound=50,
                open_lower_bound=False,
                open_upper_bound=False,
                page_url="dummy://test3",
                scheduled_close_time=datetime(2025, 12, 31)
            ),
        ]
        forecast_reports = asyncio.run(
            template_bot.forecast_questions(example_questions, return_exceptions=True)
        )
    elif run_mode == "tournament":
        logger.info("Starting tournament mode forecast")
        logger.info(f"Checking AI Competition Tournament ID: {MetaculusApi.CURRENT_AI_COMPETITION_ID}")
        logger.info(f"Checking MiniBench Tournament ID: {MetaculusApi.CURRENT_MINIBENCH_ID}")
        logger.info("Checking Fall AIB 2025 Tournament by slug: fall-aib-2025")

        seasonal_tournament_reports = asyncio.run(
            template_bot.forecast_on_tournament(
                MetaculusApi.CURRENT_AI_COMPETITION_ID, return_exceptions=True
            )
        )
        minibench_reports = asyncio.run(
            template_bot.forecast_on_tournament(
                MetaculusApi.CURRENT_MINIBENCH_ID, return_exceptions=True
            )
        )

        # Add the Fall AIB 2025 tournament by slug
        try:
            fall_aib_reports = asyncio.run(
                template_bot.forecast_on_tournament_by_slug(
                    "fall-aib-2025", return_exceptions=True
                )
            )
            forecast_reports = seasonal_tournament_reports + minibench_reports + fall_aib_reports
        except Exception as e:
            logger.warning(f"Could not fetch Fall AIB 2025 tournament: {e}")
            forecast_reports = seasonal_tournament_reports + minibench_reports

    elif run_mode == "metaculus_cup":
        # The permanent ID for the Metaculus Cup is now 32828
        logger.info("Starting Metaculus cup mode forecast")
        logger.info("Checking Metaculus Cup Tournament ID: 32828")
        template_bot.skip_previously_forecasted_questions = False
        forecast_reports = asyncio.run(
            template_bot.forecast_on_tournament(
                32828, return_exceptions=True  # Use the correct ID instead of the slug
            )
        )
    else:
        raise ValueError(f"Unknown mode: {run_mode}")

    logger.info("Forecasting completed successfully")
    template_bot.log_report_summary(forecast_reports)

    if run_mode == "test_questions":
        for i, report in enumerate(forecast_reports):
            if isinstance(report, Exception):
                logger.error(f"Error in example question {i}: {report}")
            else:
                logger.info(f"Example question {i} forecast: {report.prediction_value}")


if __name__ == "__main__":
    main()