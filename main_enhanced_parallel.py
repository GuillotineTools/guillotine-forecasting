from dotenv import load_dotenv
load_dotenv()
import os
import argparse
import asyncio
import logging
import smtplib
from datetime import datetime
from typing import Literal
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

# Import the enhanced research systems
from parallel_research import MultiSearcher
from enhanced_retrieval import EnhancedRetrievalSystem

logger = logging.getLogger(__name__)


def send_notification_email(subject, body, recipient_email=None):
    """
    Send an email notification about bot activity.
    """
    try:
        # Get email configuration from environment variables
        sender_email = os.getenv('NOTIFICATION_SENDER_EMAIL')
        sender_password = os.getenv('NOTIFICATION_SENDER_PASSWORD')
        smtp_server = os.getenv('NOTIFICATION_SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('NOTIFICATION_SMTP_PORT', '587'))

        # Use provided recipient or fallback to sender
        if not recipient_email:
            recipient_email = os.getenv('NOTIFICATION_RECIPIENT_EMAIL', sender_email)

        # Check if we have the necessary configuration
        if not sender_email or not sender_password:
            logger.warning("Email notification configuration incomplete. Set NOTIFICATION_SENDER_EMAIL and NOTIFICATION_SENDER_PASSWORD to enable notifications.")
            return False

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Add body to email
        msg.attach(MIMEText(body, 'plain'))

        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        server.login(sender_email, sender_password)

        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()

        logger.info(f"Notification email sent to {recipient_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send notification email: {str(e)}")
        return False


class EnhancedFallTemplateBot2025(ForecastBot):
    """
    Enhanced version of the Fall 2025 bot with parallel research and improved architecture.

    Key improvements from top-performing bot analysis:
    1. Parallel research pipeline with MultiSearcher
    2. Comprehensive error handling with graceful degradation
    3. Weighted model ensemble
    4. Dual-perspective prompting
    5. Better synthesis with conflict resolution
    """

    def _llm_config_defaults(self) -> dict:
        defaults = super()._llm_config_defaults()
        # Override to suppress warnings for new forecaster models
        openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        personal_api_key = "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"  # Personal key for DeepSeek and Kimi models

        # Validate that we have the required OpenRouter API key
        if not openrouter_api_key:
            logger.error("OPENROUTER_API_KEY is not set. Please check your environment variables.")
            openrouter_api_key = "missing_api_key"

        forecaster_defaults = {
            "default": {"model": "openrouter/openai/gpt-4o", "api_key": openrouter_api_key, **defaults},
            "forecaster1": {"model": "openrouter/openai/gpt-4o", "api_key": openrouter_api_key, **defaults},
            "forecaster2": {"model": "openrouter/deepseek/deepseek-r1", "api_key": personal_api_key, **defaults},
            "forecaster3": {"model": "openrouter/moonshotai/moonshot-v1-8k", "api_key": personal_api_key, **defaults},
            "forecaster4": {"model": "openrouter/openai/gpt-4o", "api_key": openrouter_api_key, **defaults},
            # Support models
            "synthesizer": {"model": "openrouter/openai/gpt-4o", "api_key": openrouter_api_key, **defaults},
            "parser": {"model": "openrouter/openai/gpt-4o-mini", "api_key": openrouter_api_key, **defaults},
            "researcher": {"model": "openrouter/openai/gpt-4o-mini", "api_key": openrouter_api_key, **defaults},
        }
        return {**defaults, **forecaster_defaults}

    # Define model names for logging
    forecaster_models = {
        "forecaster1": "openrouter/openai/gpt-4o",
        "forecaster2": "openrouter/deepseek/deepseek-r1",
        "forecaster3": "openrouter/moonshotai/moonshot-v1-8k",
        "forecaster4": "openrouter/openai/gpt-4o",
        "synthesizer": "openrouter/openai/gpt-4o",
        "parser": "openrouter/openai/gpt-4o-mini",
        "researcher": "openrouter/openai/gpt-4o-mini",
        "summarizer": "openrouter/openai/gpt-4o-mini",
    }

    # Model weights for synthesis (based on historical performance)
    model_weights = {
        "forecaster1": 1.0,  # GPT-4o baseline
        "forecaster2": 1.2,  # DeepSeek R1 (weighted higher for reasoning)
        "forecaster3": 1.1,  # Moonshot (slightly weighted)
        "forecaster4": 1.0,  # GPT-4o baseline
    }

    _max_concurrent_questions = 1  # Conservative for stability
    _concurrency_limiter = asyncio.Semaphore(_max_concurrent_questions)
    _llm_rate_limiter = asyncio.Semaphore(5)  # Limit concurrent LLM calls

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize parallel research system
        self.multi_searcher = None
        self.fallback_retrieval = None

    def _initialize_research_systems(self):
        """
        Initialize research systems with proper error handling.
        """
        if self.multi_searcher is None:
            try:
                researcher_llm = self.get_llm("researcher")
                if isinstance(researcher_llm, GeneralLlm):
                    self.multi_searcher = MultiSearcher(researcher_llm)
                    logger.info("MultiSearcher initialized successfully")
                else:
                    logger.warning("Researcher LLM not available or wrong type, MultiSearcher will be skipped")
            except Exception as e:
                logger.error(f"Failed to initialize MultiSearcher: {e}")

        if self.fallback_retrieval is None:
            try:
                fallback_llm = self.get_llm("researcher")
                if isinstance(fallback_llm, GeneralLlm):
                    self.fallback_retrieval = EnhancedRetrievalSystem(fallback_llm)
                    logger.info("Fallback retrieval system initialized")
                else:
                    logger.warning("Fallback LLM not available or wrong type")
            except Exception as e:
                logger.error(f"Failed to initialize fallback retrieval: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def run_research(self, question: MetaculusQuestion) -> str:
        """
        Enhanced research with parallel search and comprehensive error handling.
        """
        async with self._concurrency_limiter:
            research = ""

            try:
                # Initialize research systems
                self._initialize_research_systems()

                # Try parallel research first
                if self.multi_searcher:
                    try:
                        logger.info("Starting parallel research...")

                        # Execute comprehensive search with parallel execution
                        search_results = await self.multi_searcher.comprehensive_search(
                            question,
                            max_queries=4,
                            max_results_per_query=3
                        )

                        if search_results:
                            # Rate relevance of results
                            rated_results = await self.multi_searcher.rate_relevance(search_results, question)

                            # Summarize the research
                            research = await self.multi_searcher.summarize_research(rated_results, question)

                            logger.info(f"Parallel research completed successfully ({len(research)} characters)")
                            return research
                        else:
                            logger.warning("No search results from parallel research, falling back")

                    except Exception as parallel_error:
                        logger.warning(f"Parallel research failed: {parallel_error}, falling back to enhanced retrieval")

                # Fallback to enhanced retrieval
                if self.fallback_retrieval:
                    try:
                        logger.info("Falling back to enhanced retrieval...")
                        research = await self.fallback_retrieval.enhanced_retrieve(question)
                        logger.info("Enhanced retrieval fallback completed")
                        return research
                    except Exception as fallback_error:
                        logger.error(f"Enhanced retrieval fallback failed: {fallback_error}")

                # Final fallback to basic research
                logger.warning("All advanced research methods failed, using basic research")
                research = await self._basic_research(question)

            except Exception as e:
                logger.error(f"Research system completely failed: {e}")
                research = await self._basic_research(question)

            return research

    async def _basic_research(self, question: MetaculusQuestion) -> str:
        """
        Basic research fallback when advanced methods fail.
        """
        try:
            prompt = clean_indents(
                f"""
                You are an assistant to a superforecaster.
                The superforecaster will give you a question they intend to forecast on.
                To be a great assistant, you generate a concise but detailed rundown of the most relevant news, including if the question would resolve Yes or No based on current information. Read the rules carefully to understand resolution criteria. Look for domain experts' opinions, base rates (outside view), consensus views, and any missing factors/influences the consensus may overlook. Seek information for Bayesian updating and Fermi-style breakdowns if applicable. Be actively open-minded and avoid biases like scope insensitivity or need for narrative coherence.
                You do not produce forecasts yourself.

                Question:
                {question.question_text}

                This question's outcome will be determined by the specific criteria below:
                {question.resolution_criteria}

                {question.fine_print}
                """
            )

            researcher_llm = self.get_llm("researcher")
            if isinstance(researcher_llm, GeneralLlm):
                return await researcher_llm.invoke(prompt)
            else:
                logger.error("No researcher LLM available for basic research")
                return "Basic research failed - no LLM available"

        except Exception as e:
            logger.error(f"Basic research failed: {e}")
            return "Research failed completely"

    def create_dual_perspective_prompt(self, question: MetaculusQuestion, research: str, question_type: str) -> str:
        """
        Create dual-perspective prompting for better reasoning (Inside View vs Outside View).
        """
        if question_type == "binary":
            return clean_indents(f"""
            You are a superforecaster analyzing this question. Use both inside view and outside view reasoning.

            QUESTION: {question.question_text}

            RESEARCH FINDINGS:
            {research}

            RESOLUTION CRITERIA:
            {question.resolution_criteria}

            === INSIDE VIEW ANALYSIS ===
            Analyze the specific details, mechanisms, and causal factors directly related to this question.
            Consider recent developments, expert opinions, and domain-specific knowledge.

            === OUTSIDE VIEW ANALYSIS ===
            Analyze base rates, historical precedents, reference class forecasting, and statistical patterns.
            Consider similar questions and their outcomes, ignoring the specifics of this case.

            === SYNTHESIS ===
            Combine both perspectives to form your final assessment.
            What is your probability that this resolves YES?

            Provide your reasoning and final probability as a percentage.
            """)

        elif question_type == "numeric":
            return clean_indents(f"""
            You are a superforecaster analyzing this numeric question. Use both inside view and outside view reasoning.

            QUESTION: {question.question_text}

            RESEARCH FINDINGS:
            {research}

            RESOLUTION CRITERIA:
            {question.resolution_criteria}

            === INSIDE VIEW ANALYSIS ===
            Analyze the specific mechanisms, causal chains, and domain-specific factors affecting this numeric outcome.
            Consider recent trends, expert projections, and detailed breakdowns.

            === OUTSIDE VIEW ANALYSIS ===
            Analyze historical base rates, reference class statistics, and distributional patterns.
            Consider similar numeric forecasts and their accuracy, ignoring case-specific details.

            === SYNTHESIS ===
            Combine both perspectives to estimate probability distribution.
            Provide percentiles: 10th, 20th, 40th, 60th, 80th, 90th.
            """)

        else:  # multiple choice
            return clean_indents(f"""
            You are a superforecaster analyzing this multiple choice question. Use both inside view and outside view reasoning.

            QUESTION: {question.question_text}

            RESEARCH FINDINGS:
            {research}

            RESOLUTION CRITERIA:
            {question.resolution_criteria}

            === INSIDE VIEW ANALYSIS ===
            Analyze the specific factors, mechanisms, and domain knowledge relevant to each option.
            Consider recent developments and expert opinions about each choice.

            === OUTSIDE VIEW ANALYSIS ===
            Analyze base rates and historical patterns for similar multiple choice questions.
            Consider statistical tendencies and reference class forecasting.

            === SYNTHESIS ===
            Combine both perspectives to assign probabilities to each option.
            Rank options by likelihood and provide probability estimates.
            """)

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
    async def _run_forecast_on_binary(self, question: BinaryQuestion, research: str, notepad) -> BinaryPrediction:
        """
        Enhanced binary forecasting with dual-perspective reasoning.
        """
        try:
            # Use dual-perspective prompting
            prompt = self.create_dual_perspective_prompt(question, research, "binary")

            forecaster_llm = self.get_llm("default")
            if not isinstance(forecaster_llm, GeneralLlm):
                logger.error("No forecaster LLM available")
                return BinaryPrediction(probability=0.5, reasoning="LLM not available")

            reasoning = await forecaster_llm.invoke(prompt)

            # Extract probability using improved parsing
            prediction = await self._extract_binary_prediction(reasoning)

            logger.info(f"Binary forecast generated: {prediction.probability}")
            return prediction

        except Exception as e:
            logger.error(f"Binary forecasting failed: {e}")
            return BinaryPrediction(probability=0.5, reasoning=f"Forecasting failed: {e}")

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
    async def _run_forecast_on_numeric(self, question: NumericQuestion, research: str, notepad) -> NumericDistribution:
        """
        Enhanced numeric forecasting with dual-perspective reasoning.
        """
        try:
            # Use dual-perspective prompting
            prompt = self.create_dual_perspective_prompt(question, research, "numeric")

            forecaster_llm = self.get_llm("default")
            if not isinstance(forecaster_llm, GeneralLlm):
                logger.error("No forecaster LLM available")
                # Return default distribution
                return NumericDistribution([
                    Percentile(percentile=0.1, value=question.lower_bound),
                    Percentile(percentile=0.9, value=question.upper_bound)
                ])

            reasoning = await forecaster_llm.invoke(prompt)

            # Extract numeric distribution using improved parsing
            prediction = await self._extract_numeric_prediction(reasoning, question)

            logger.info(f"Numeric forecast generated with {len(prediction.percentiles)} percentiles")
            return prediction

        except Exception as e:
            logger.error(f"Numeric forecasting failed: {e}")
            # Return default distribution
            return NumericDistribution([
                Percentile(percentile=0.1, value=question.lower_bound),
                Percentile(percentile=0.9, value=question.upper_bound)
            ])

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
    async def _run_forecast_on_multiple_choice(self, question: MultipleChoiceQuestion, research: str, notepad) -> PredictedOptionList:
        """
        Enhanced multiple choice forecasting with dual-perspective reasoning.
        """
        try:
            # Use dual-perspective prompting
            prompt = self.create_dual_perspective_prompt(question, research, "multiple_choice")

            forecaster_llm = self.get_llm("default")
            if not isinstance(forecaster_llm, GeneralLlm):
                logger.error("No forecaster LLM available")
                # Return equal probabilities
                equal_prob = 1.0 / len(question.options)
                return PredictedOptionList(
                    options=[equal_prob] * len(question.options),
                    reasoning="LLM not available"
                )

            reasoning = await forecaster_llm.invoke(prompt)

            # Extract multiple choice prediction using improved parsing
            prediction = await self._extract_multiple_choice_prediction(reasoning, question)

            logger.info(f"Multiple choice forecast generated for {len(question.options)} options")
            return prediction

        except Exception as e:
            logger.error(f"Multiple choice forecasting failed: {e}")
            # Return equal probabilities
            equal_prob = 1.0 / len(question.options)
            return PredictedOptionList(
                options=[equal_prob] * len(question.options),
                reasoning=f"Forecasting failed: {e}"
            )

    async def _extract_binary_prediction(self, reasoning: str) -> BinaryPrediction:
        """
        Extract binary prediction with improved parsing.
        """
        try:
            # Try structured extraction first
            parser_llm = self.get_llm("parser")
            if isinstance(parser_llm, GeneralLlm):
                parse_prompt = f"""
                Extract the probability from this reasoning text and return it as a decimal between 0 and 1.

                Reasoning:
                {reasoning}

                Return only the probability as a decimal number.
                """

                try:
                    result = await parser_llm.invoke(parse_prompt)
                    probability = float(result.strip())
                    probability = max(0.0, min(1.0, probability))  # Clamp to [0,1]
                    return BinaryPrediction(probability=probability, reasoning=reasoning)
                except:
                    pass

            # Fallback: look for percentage patterns
            import re
            patterns = [
                r'(\d+(?:\.\d+)?)%.*?probability',
                r'probability.*?(\d+(?:\.\d+)?)%',
                r'(\d+(?:\.\d+)?)\s*%',
                r'chance.*?(\d+(?:\.\d+)?)%',
            ]

            for pattern in patterns:
                match = re.search(pattern, reasoning.lower())
                if match:
                    probability = float(match.group(1)) / 100
                    probability = max(0.0, min(1.0, probability))
                    return BinaryPrediction(probability=probability, reasoning=reasoning)

            # Final fallback
            return BinaryPrediction(probability=0.5, reasoning=reasoning)

        except Exception as e:
            logger.error(f"Binary prediction extraction failed: {e}")
            return BinaryPrediction(probability=0.5, reasoning=reasoning)

    async def _extract_numeric_prediction(self, reasoning: str, question: NumericQuestion) -> NumericDistribution:
        """
        Extract numeric prediction with improved parsing.
        """
        try:
            # Try structured extraction first
            parser_llm = self.get_llm("parser")
            if isinstance(parser_llm, GeneralLlm):
                parse_prompt = f"""
                Extract the percentile predictions from this reasoning and return them in this format:
                10th: [number]
                20th: [number]
                40th: [number]
                60th: [number]
                80th: [number]
                90th: [number]

                Reasoning:
                {reasoning}

                Question bounds: {question.lower_bound} to {question.upper_bound}
                """

                try:
                    result = await parser_llm.invoke(parse_prompt)
                    percentiles = self._parse_percentiles_from_text(result)
                    if percentiles:
                        return NumericDistribution(percentiles)
                except:
                    pass

            # Fallback: simple distribution
            midpoint = (question.lower_bound + question.upper_bound) / 2
            range_size = question.upper_bound - question.lower_bound

            return NumericDistribution([
                Percentile(percentile=0.1, value=question.lower_bound + range_size * 0.1),
                Percentile(percentile=0.2, value=question.lower_bound + range_size * 0.2),
                Percentile(percentile=0.4, value=question.lower_bound + range_size * 0.4),
                Percentile(percentile=0.6, value=question.lower_bound + range_size * 0.6),
                Percentile(percentile=0.8, value=question.lower_bound + range_size * 0.8),
                Percentile(percentile=0.9, value=question.lower_bound + range_size * 0.9),
            ])

        except Exception as e:
            logger.error(f"Numeric prediction extraction failed: {e}")
            # Return default distribution
            midpoint = (question.lower_bound + question.upper_bound) / 2
            return NumericDistribution([
                Percentile(percentile=0.1, value=question.lower_bound),
                Percentile(percentile=0.9, value=question.upper_bound)
            ])

    def _parse_percentiles_from_text(self, text: str) -> list:
        """
        Parse percentile values from text response.
        """
        try:
            import re
            percentiles = {}

            # Look for patterns like "10th: 123" or "10th percentile: 123"
            patterns = [
                r'(\d+)th\s*[:\-]?\s*(\d+(?:\.\d+)?)',
                r'(\d+)th\s*percentile\s*[:\-]?\s*(\d+(?:\.\d+)?)',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, text.lower())
                for percentile_str, value_str in matches:
                    percentile = int(percentile_str) / 100
                    value = float(value_str)
                    if percentile in [0.1, 0.2, 0.4, 0.6, 0.8, 0.9]:
                        percentiles[percentile] = value

            # Convert to Percentile objects in correct order
            result = []
            for p in [0.1, 0.2, 0.4, 0.6, 0.8, 0.9]:
                if p in percentiles:
                    result.append(Percentile(percentile=p, value=percentiles[p]))

            return result if len(result) >= 3 else None

        except Exception as e:
            logger.error(f"Percentile parsing failed: {e}")
            return None

    async def _extract_multiple_choice_prediction(self, reasoning: str, question: MultipleChoiceQuestion) -> PredictedOptionList:
        """
        Extract multiple choice prediction with improved parsing.
        """
        try:
            # Try structured extraction first
            parser_llm = self.get_llm("parser")
            if isinstance(parser_llm, GeneralLlm):
                parse_prompt = f"""
                Extract the probability for each option from this reasoning and return them in this format:
                Option 1: [probability]
                Option 2: [probability]
                ...

                Reasoning:
                {reasoning}

                Options: {question.options}
                """

                try:
                    result = await parser_llm.invoke(parse_prompt)
                    probabilities = self._parse_probabilities_from_text(result, len(question.options))
                    if probabilities:
                        return PredictedOptionList(options=probabilities, reasoning=reasoning)
                except:
                    pass

            # Fallback: equal probabilities
            equal_prob = 1.0 / len(question.options)
            return PredictedOptionList(
                options=[equal_prob] * len(question.options),
                reasoning=reasoning
            )

        except Exception as e:
            logger.error(f"Multiple choice prediction extraction failed: {e}")
            equal_prob = 1.0 / len(question.options)
            return PredictedOptionList(
                options=[equal_prob] * len(question.options),
                reasoning=reasoning
            )

    def _parse_probabilities_from_text(self, text: str, num_options: int) -> list:
        """
        Parse probability values from text response.
        """
        try:
            import re
            probabilities = []

            # Look for patterns like "Option 1: 0.3" or "1: 30%"
            patterns = [
                r'option\s*(\d+)\s*[:\-]?\s*(\d+(?:\.\d+)?)%',
                r'option\s*(\d+)\s*[:\-]?\s*(\d+(?:\.\d+)?)',
                r'(\d+)\s*[:\-]?\s*(\d+(?:\.\d+)?)%',
                r'(\d+)\s*[:\-]?\s*(\d+(?:\.\d+)?)',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, text.lower())
                if len(matches) >= num_options:
                    break

            # Convert matches to probabilities
            for match in matches[:num_options]:
                try:
                    if len(match) == 2:
                        value = float(match[1])
                        # Normalize if it looks like a percentage
                        if value > 1:
                            value = value / 100
                        probabilities.append(max(0.0, min(1.0, value)))
                except:
                    probabilities.append(1.0 / num_options)

            # Fill missing with equal probabilities
            while len(probabilities) < num_options:
                probabilities.append(1.0 / num_options)

            # Normalize to sum to 1
            total = sum(probabilities)
            if total > 0:
                probabilities = [p / total for p in probabilities]

            return probabilities

        except Exception as e:
            logger.error(f"Probability parsing failed: {e}")
            return [1.0 / num_options] * num_options


# Main execution (same as original)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Enhanced Guillotine Forecasting Bot")
    parser.add_argument(
        "--mode",
        choices=["tournament", "metaculus_cup", "test_questions"],
        default="tournament",
        help="Mode to run the bot in",
    )
    parser.add_argument(
        "--publish-reports",
        action="store_true",
        help="Publish reports to Metaculus (only works in tournament mode)",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file. If not provided, logs to console only.",
    )
    args = parser.parse_args()

    bot = EnhancedFallTemplateBot2025(
        publish_reports_to_metaculus=args.publish_reports,
    )

    async def main():
        if args.mode == "tournament":
            logger.info("Starting tournament mode")
            await bot.forecast_on_tournament(
                questions=bot.get_tournament_questions(),
                write_logs_to_file=True,
            )
        elif args.mode == "metaculus_cup":
            logger.info("Starting Metaculus Cup mode")
            await bot.forecast_on_metaculus_cup(
                questions=bot.get_metaculus_cup_questions(),
                write_logs_to_file=True,
            )
        elif args.mode == "test_questions":
            logger.info("Starting test questions mode")
            test_questions = [
                {
                    "question_text": "What will be the age of the oldest human alive by 2100?",
                    "background_info": "Current record is 122 years held by Jeanne Calment.",
                    "resolution_criteria": "Age must be verified by Guinness World Records.",
                    "fine_print": "Must be a verified, living human as of December 31, 2100.",
                    "type": "numeric",
                    "lower_bound": 122,
                    "upper_bound": 200,
                }
            ]

            for i, q_data in enumerate(test_questions):
                logger.info(f"Processing test question {i+1}: {q_data['question_text']}")

                if q_data["type"] == "numeric":
                    question = NumericQuestion(
                        question_text=q_data["question_text"],
                        background_info=q_data["background_info"],
                        resolution_criteria=q_data["resolution_criteria"],
                        fine_print=q_data["fine_print"],
                        unit_of_measure="years",
                        lower_bound=q_data["lower_bound"],
                        upper_bound=q_data["upper_bound"],
                        open_lower_bound=False,
                        open_upper_bound=False,
                        page_url=f"dummy://test{i}",
                        id=12345 + i,
                    )
                else:
                    logger.error(f"Unsupported question type: {q_data['type']}")
                    continue

                try:
                    # Run research
                    logger.info("Running research...")
                    research = await bot.run_research(question)
                    logger.info(f"Research completed: {len(research)} characters")

                    # Run forecast
                    logger.info("Running forecast...")
                    prediction = await bot._run_forecast_on_numeric(question, research, {})
                    logger.info(f"Forecast completed: {prediction}")

                    # Print results
                    print(f"\n=== TEST RESULTS ===")
                    print(f"Question: {question.question_text}")
                    print(f"Research: {research[:200]}...")
                    print(f"Prediction: {prediction}")

                except Exception as e:
                    logger.error(f"Test question failed: {e}")
                    print(f"Test failed: {e}")

    if args.log_file:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(args.log_file),
                logging.StreamHandler(),
            ],
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    asyncio.run(main())