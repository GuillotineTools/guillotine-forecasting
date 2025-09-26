from dotenv import load_dotenv
load_dotenv()
import os
import argparse
import asyncio
import logging
import smtplib
from datetime import datetime, timedelta
from typing import Literal, List, Tuple, Dict, Any, Optional
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

# Import the enhanced retrieval system
from enhanced_retrieval import EnhancedRetrievalSystem

# Import the parallel research system
from parallel_research import MultiSearcher

# Import the optimized reasoning system
from optimized_reasoning import OptimizedReasoningSystem

# Import the redundant LLM system
from redundant_llm import create_redundant_llm

# Import the ntfy alert system
from ntfy_alerts import (
    NtfyAlerts,
    send_new_question_alert,
    send_bot_status_alert,
    send_forecast_alert,
    test_ntfy_connection
)

from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)
main_logger = logging.getLogger('__main__')

# Global ntfy instance
_ntfy_instance: Optional[NtfyAlerts] = None

def get_ntfy_instance() -> NtfyAlerts:
    """Get or create the global ntfy instance."""
    global _ntfy_instance
    if _ntfy_instance is None:
        try:
            _ntfy_instance = NtfyAlerts()
            logger.info("Ntfy alert system initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize ntfy alerts: {e}")
            _ntfy_instance = None
    return _ntfy_instance


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


class FallTemplateBot2025(ForecastBot):
    """
    This is a copy of the template bot for Fall 2025 Metaculus AI Tournament.
    This bot is what is used by Metaculus in our benchmark, but is also provided as a template for new bot makers.
    This template is given as-is, and though we have covered most test cases
    in forecasting-tools it may be worth double checking key components locally.

    Main changes since Q2:
    - An LLM now parses the final forecast output (rather than programmatic parsing)
    - Added resolution criteria and fine print explicitly to the research prompt
    - Previously in the prompt, nothing about upper/lower bound was shown when the bounds were open. Now a suggestion is made when this is the case.
    - Support for nominal bounds was added (i.e. when there are discrete questions and normal upper/lower bounds are not as intuitive)

    The main entry point of this bot is `forecast_on_tournament` in the parent class.
    See the script at the bottom of the file for more details on how to run the bot.
    Ignoring the finer details, the general flow is:
    - Load questions from Metaculus
    - For each question
        - Execute run_research a number of times equal to research_reports_per_question
        - Execute respective run_forecast function `predictions_per_research_report * research_reports_per_question` times
        - Aggregate the predictions
        - Submit prediction (if publish_reports_to_metaculus is True)
    - Return a list of ForecastReport objects

    Only the research and forecast functions need to be implemented in ForecastBot subclasses,
    though you may want to override other ones.
    In this example, you can change the prompts to be whatever you want since,
    structure_output uses an LLMto intelligently reformat the output into the needed structure.

    By default (i.e. 'tournament' mode), when you run this script, it will forecast on any open questions for the
    MiniBench and Seasonal AIB tournaments. If you want to forecast on only one or the other, you can remove one
    of them from the 'tournament' mode code at the bottom of the file.

    You can experiment with what models work best with your bot by using the `llms` parameter when initializing the bot.
    You can initialize the bot with any number of models. For example,
    ```python
    my_bot = MyBot(
        ...
        llms={  # choose your model names or GeneralLlm llms here, otherwise defaults will be chosen for you
            "default": GeneralLlm(
                model="openrouter/openai/gpt-4o", # "anthropic/claude-3-5-sonnet-20241022", etc (see docs for litellm)
                temperature=0.3,
                timeout=40,
                allowed_tries=2,
            ),
            "summarizer": "openai/gpt-4o-mini",
            "researcher": "asknews/deep-research/low",
            "parser": "openai/gpt-4o-mini",
        },
    )
    ```

    Then you can access the model in custom functions like this:
    ```python
    research_strategy = self.get_llm("researcher", "model_name"
    if research_strategy == "asknews/deep-research/low":
        ...
    # OR
    summarizer = await self.get_llm("summarizer", "model_name").invoke(prompt)
    # OR
    reasoning = await self.get_llm("default", "llm").invoke(prompt)
    ```

    If you end up having trouble with rate limits and want to try a more sophisticated rate limiter try:
    ```python
    from forecasting_tools import RefreshingBucketRateLimiter
    rate_limiter = RefreshingBucketRateLimiter(
        capacity=2,
        refresh_rate=1,
    ) # Allows 1 request per second on average with a burst of 2 requests initially. Set this as a class variable
    await self.rate_limiter.wait_till_able_to_acquire_resources(1) # 1 because it's consuming 1 request (use more if you are adding a token limit) 
    ```
    Additionally OpenRouter has large rate limits immediately on account creation
    """


    def _llm_config_defaults(self) -> dict:
        defaults = super()._llm_config_defaults()
        # Override to suppress warnings for new forecaster models

        # CRITICAL API KEY ASSIGNMENT - DO NOT CHANGE
        # The main OpenRouter API key (OPENROUTER_API_KEY from env vars) ONLY works for OpenAI models (GPT-4o, GPT-4o-mini)
        # The personal API key below ONLY works for DeepSeek and Moonshot/Kimi models
        # THESE CANNOT BE USED INTERCHANGEABLY OR MODELS WILL FAIL WITH "User not found" ERRORS
        # FOR DEEPSEEK MODELS, WE NOW USE REDUNDANT API: CHUTES FIRST, THEN OPENROUTER
        # FOR KIMI MODELS, WE USE OPENROUTER DIRECTLY (Kimi not available on Chutes)
        openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        personal_api_key = "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"  # Personal key for DeepSeek and Kimi models ONLY - FREE MODELS ONLY
        chutes_api_key = os.getenv('CHUTES_API_TOKEN', '')

        # Validate that we have the required OpenRouter API key
        if not openrouter_api_key:
            logger.error("OPENROUTER_API_KEY is not set. Please check your environment variables.")
            # Use a placeholder but this will cause issues
            openrouter_api_key = "missing_api_key"

        forecaster_defaults = {
            "default": {"model": "openrouter/openai/gpt-4o", "api_key": openrouter_api_key, **defaults},
            "forecaster1": {"model": "openrouter/openai/gpt-4o", "api_key": openrouter_api_key, **defaults},
            "forecaster2": {"model": "openrouter/deepseek/deepseek-r1", "api_key": personal_api_key, "redundant": True, "chutes_api_key": chutes_api_key, **defaults},
            "forecaster3": {"model": "openrouter/moonshotai/kimi-k2-0905", "api_key": personal_api_key, "redundant": True, "chutes_api_key": chutes_api_key, **defaults},
            "forecaster4": {"model": "openrouter/openai/gpt-4o", "api_key": openrouter_api_key, **defaults},
            # Add support models
            "synthesizer": {"model": "openrouter/openai/gpt-4o", "api_key": openrouter_api_key, **defaults},
            "parser": {"model": "openrouter/openai/gpt-4o-mini", "api_key": openrouter_api_key, **defaults},
            "researcher": {"model": "openrouter/openai/gpt-4o-mini", "api_key": openrouter_api_key, **defaults},
        }
        return {**defaults, **forecaster_defaults}

    # Define model names for logging
    forecaster_models = {
        "forecaster1": "openrouter/openai/gpt-4o",
        "forecaster2": "openrouter/deepseek/deepseek-r1",
        "forecaster3": "openrouter/moonshotai/kimi-k2-0905",
        "forecaster4": "openrouter/openai/gpt-4o",
        "synthesizer": "openrouter/openai/gpt-4o",
        "parser": "openrouter/openai/gpt-4o-mini",
        "researcher": "openrouter/openai/gpt-4o-mini",
        "summarizer": "openrouter/openai/gpt-4o-mini",
    }
    
    _max_concurrent_questions = (
        1  # Set this to whatever works for your search-provider/ai-model rate limits
    )
    _concurrency_limiter = asyncio.Semaphore(_max_concurrent_questions)

    # Add rate limiting for LLM calls
    _llm_rate_limiter = asyncio.Semaphore(5)  # Limit concurrent LLM calls

    # Parallel research system - initialized when needed
    _multi_searcher = None
    _fallback_retrieval = None

    # Multiple runs configuration for statistical aggregation
    _num_forecasting_runs = 5  # Number of runs per question for median selection

    def get_llm(self, purpose: str = "default", guarantee_type: str | None = None):
        """
        Override get_llm to properly handle dictionary configurations with API keys.
        This fixes the issue where DeepSeek and Moonshot models fail with authentication errors.
        """
        if purpose not in self._llms:
            raise ValueError(f"Unknown llm requested from llm dict for purpose: '{purpose}'")

        llm_config = self._llms[purpose]
        if llm_config is None:
            raise ValueError(f"LLM is undefined for purpose: {purpose}. It was probably not defined in defaults.")

        return_value = None

        if guarantee_type is None:
            return_value = llm_config
        elif guarantee_type == "llm":
            if isinstance(llm_config, GeneralLlm):
                return_value = llm_config
                logger.info(f"Using existing GeneralLlm for {purpose}: {llm_config.model}")
            elif isinstance(llm_config, dict):
                # Properly handle dictionary configuration by unpacking it
                model_name = llm_config.get('model', 'unknown')
                api_key = llm_config.get('api_key', 'missing')
                logger.info(f"Creating GeneralLlm from dict config for {purpose}: {model_name}")
                logger.info(f"API key length: {len(api_key) if api_key != 'missing' else 0}")
                logger.info(f"API key first 10 chars: {api_key[:10] if api_key != 'missing' else 'NONE'}")
                return_value = GeneralLlm(**llm_config)
                logger.info(f"Successfully created GeneralLlm for {purpose}")
                logger.info(f"Created model name: {return_value.model}")
            else:
                # Handle string model names
                logger.info(f"Creating GeneralLlm from string for {purpose}: {llm_config}")
                return_value = GeneralLlm(model=llm_config)
        elif guarantee_type == "string_name":
            if isinstance(llm_config, str):
                return_value = llm_config
            elif isinstance(llm_config, GeneralLlm):
                logger.warning(f"Converting GeneralLlm to string llm name: {llm_config.model} for purpose: {purpose}. This means any settings for the GeneralLlm will be ignored.")
                return_value = llm_config.model
            elif isinstance(llm_config, dict):
                return_value = llm_config.get('model', str(llm_config))
            else:
                return_value = str(llm_config)
        else:
            raise ValueError(f"Unknown guarantee_type: {guarantee_type}")

        return return_value

    def _initialize_parallel_research(self):
        """
        Initialize parallel research systems with proper error handling.
        """
        if self._multi_searcher is None:
            try:
                researcher_llm = self.get_llm("researcher")
                if not isinstance(researcher_llm, GeneralLlm):
                    # Create a proper GeneralLlm instance for MultiSearcher
                    researcher_llm = GeneralLlm(
                        model="openrouter/openai/gpt-4o-mini",
                        temperature=0,
                        allowed_tries=2,
                        timeout=40
                    )
                    logger.info("Created GeneralLlm instance for MultiSearcher")

                self._multi_searcher = MultiSearcher(researcher_llm)
                logger.info("MultiSearcher initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize MultiSearcher: {e}")

        if self._fallback_retrieval is None:
            try:
                fallback_llm = self.get_llm("researcher")
                if isinstance(fallback_llm, GeneralLlm):
                    self._fallback_retrieval = EnhancedRetrievalSystem(fallback_llm)
                    logger.info("Fallback retrieval system initialized")
                else:
                    logger.warning("Fallback LLM not available or wrong type")
            except Exception as e:
                logger.warning(f"Failed to initialize fallback retrieval: {e}")

        # Initialize reasoning session storage
        self._last_reasoning_session = None

    async def run_multiple_forecasting_runs(
        self,
        question: BinaryQuestion,
        research: str,
        forecaster_key: str,
        num_runs: int = None
    ) -> tuple[List[float], List[str]]:
        """
        Run multiple forecasting iterations for a single forecaster and return predictions with reasoning.

        Returns:
            tuple: (predictions_list, reasonings_list)
        """
        if num_runs is None:
            num_runs = self._num_forecasting_runs

        predictions = []
        reasonings = []

        logger.info(f"Running {num_runs} forecasting iterations for {forecaster_key}")

        for run_num in range(num_runs):
            try:
                async with self._llm_rate_limiter:  # Rate limit LLM calls
                    llm = self.get_llm(forecaster_key, "llm")
                    if llm is None:
                        logger.warning(f"LLM for {forecaster_key} is None, skipping run {run_num + 1}")
                        continue

                    # Check if this is a RedundantLlm and use appropriate method
                    if hasattr(llm, 'chutes_searcher'):  # It's a RedundantLlm
                        result = await self._run_redundant_llm_forecast(llm, question, research, run_num, num_runs)
                    else:
                        # Use optimized reasoning system for standard LLMs
                        optimized_system = OptimizedReasoningSystem(llm)
                        varied_research = research + f"\n\nRun {run_num + 1}/{num_runs} - Consider different aspects and perspectives."
                        result = await optimized_system.run_optimized_binary_forecast(question, varied_research)

                    reasoning = result["reasoning"]
                    decimal_pred = result["prediction"]

                    predictions.append(decimal_pred)
                    reasonings.append(reasoning)

                    logger.info(f"Run {run_num + 1} from {forecaster_key}: {decimal_pred}")

            except Exception as e:
                logger.warning(f"Run {run_num + 1} failed for {forecaster_key}: {str(e)}")
                continue

        return predictions, reasonings

    async def _run_redundant_llm_forecast(
        self,
        llm,
        question: BinaryQuestion,
        research: str,
        run_num: int,
        total_runs: int
    ) -> Dict[str, Any]:
        """
        Run a forecast using RedundantLlm without OptimizedReasoningSystem to avoid serialization issues.
        """
        # Add variation to research for diversity
        varied_research = research + f"\n\nRun {run_num + 1}/{total_runs} - Consider different aspects and perspectives."

        # Create a standard forecasting prompt
        prompt = clean_indents(
            f"""
            You are a professional forecaster making a prediction on a binary question.

            Question: {question.question_text}
            Background: {question.background_info}
            Resolution Criteria: {question.resolution_criteria}
            {question.fine_print}

            Research: {varied_research}

            Today is {datetime.now().strftime("%Y-%m-%d")}.

            Provide your reasoning and end with your final probability as a number between 0 and 1.
            Format your final answer as: "Probability: X.XX"
            """
        )

        # Get the forecast from the RedundantLlm
        reasoning = await llm.invoke(prompt)

        # Extract the probability from the reasoning
        try:
            import re
            # Look for probability in various formats
            patterns = [
                r'Probability:\s*([0-9.]+)',
                r'([0-9.]+)\s*%',
                r'([0-9.]+)\s*probability',
                r'([0-9.]+)\s*chance'
            ]

            decimal_pred = 0.5  # Default fallback
            for pattern in patterns:
                match = re.search(pattern, reasoning, re.IGNORECASE)
                if match:
                    pred_str = match.group(1)
                    decimal_pred = float(pred_str)
                    # If it looks like a percentage, convert to decimal
                    if decimal_pred > 1.0:
                        decimal_pred = decimal_pred / 100.0
                    # Ensure it's in valid range
                    decimal_pred = max(0.01, min(0.99, decimal_pred))
                    break
        except Exception as e:
            logger.warning(f"Failed to extract probability from reasoning: {e}")
            decimal_pred = 0.5

        return {
            "reasoning": reasoning,
            "prediction": decimal_pred
        }

    def calculate_median_prediction(self, predictions: List[float]) -> float:
        """
        Calculate median prediction from a list of predictions.
        """
        if not predictions:
            return 0.5  # Default fallback

        sorted_predictions = sorted(predictions)
        n = len(sorted_predictions)

        if n % 2 == 1:
            # Odd number of elements, return middle value
            median = sorted_predictions[n // 2]
        else:
            # Even number of elements, return average of two middle values
            median = (sorted_predictions[n // 2 - 1] + sorted_predictions[n // 2]) / 2

        return median

    def select_median_reasoning(self, predictions: List[float], reasonings: List[str]) -> str:
        """
        Select the reasoning closest to the median prediction.
        """
        if not predictions or not reasonings:
            return "No reasoning available"

        median_pred = self.calculate_median_prediction(predictions)

        # Find reasoning closest to median
        min_distance = float('inf')
        median_reasoning = reasonings[0]  # Default fallback

        for pred, reasoning in zip(predictions, reasonings):
            distance = abs(pred - median_pred)
            if distance < min_distance:
                min_distance = distance
                median_reasoning = reasoning

        return median_reasoning

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def run_research(self, question: MetaculusQuestion) -> str:
        """
        Enhanced research with parallel search and comprehensive error handling.
        Integrates parallel research system while maintaining original fallbacks.
        """
        async with self._concurrency_limiter:
            research = ""

            # Send ntfy alert for new question detection (Fall AIB tournament only)
            try:
                ntfy = get_ntfy_instance()
                if ntfy:
                    # Check if this is a Fall AIB tournament question
                    is_fall_aib = False
                    tournament = None

                    if hasattr(question, 'page_url'):
                        if 'fall-aib' in question.page_url.lower():
                            is_fall_aib = True
                            tournament = "Fall AIB 2025"
                        elif 'ai-competition' in question.page_url.lower():
                            tournament = "AI Competition"
                        elif 'minibench' in question.page_url.lower():
                            tournament = "MiniBench"

                    # Only send alert for Fall AIB tournament questions
                    if is_fall_aib:
                        # Determine question type
                        question_type = "unknown"
                        if hasattr(question, 'options'):
                            question_type = "multiple_choice"
                        elif hasattr(question, 'upper_bound') and hasattr(question, 'lower_bound'):
                            question_type = "numeric"
                        else:
                            question_type = "binary"

                        # Send new question alert for Fall AIB only
                        success = ntfy.send_new_question_alert(
                            question_title=question.question_text,
                            question_url=getattr(question, 'page_url', ''),
                            question_type=question_type,
                            tournament=tournament
                        )

                        if success:
                            logger.info(f"Sent ntfy alert for Fall AIB question: {question.question_text[:50]}...")
                    else:
                        logger.debug(f"Skipping ntfy alert - not a Fall AIB question: {question.question_text[:50]}...")
            except Exception as e:
                logger.debug(f"Could not send ntfy alert: {e}")

            try:
                # Initialize parallel research systems
                self._initialize_parallel_research()

                # Try parallel research first (new enhancement)
                if self._multi_searcher:
                    try:
                        logger.info("Starting parallel research...")

                        # Execute comprehensive search with multi-model reasoning
                        search_with_reasoning = await self._multi_searcher.comprehensive_search_with_reasoning(
                            question,
                            max_queries=4,
                            max_results_per_query=3,
                            enable_reasoning=True
                        )

                        if search_with_reasoning:
                            search_results = search_with_reasoning.get("search_results", [])
                            reasoning_session = search_with_reasoning.get("reasoning_session")
                            enhanced_forecast = search_with_reasoning.get("enhanced_forecast")

                            # Store reasoning session for later use in forecasting
                            if reasoning_session:
                                self._last_reasoning_session = reasoning_session
                                logger.info(f"Multi-model reasoning completed with {len(reasoning_session.get('reasoning_results', []))} agents")
                                main_logger.info(f"🧠 REASONING: Multi-model reasoning completed")

                                # Log reasoning insights
                                reasoning_summary = reasoning_session.get("reasoning_summary", {})
                                logger.info(f"Reasoning summary: {reasoning_summary}")
                                main_logger.info(f"🧠 REASONING: Summary - {reasoning_summary}")

                            if search_results:
                                # Rate relevance of results
                                rated_results = await self._multi_searcher.rate_relevance(search_results, question)

                                # Summarize the research (enhanced with reasoning insights)
                                research = await self._multi_searcher.summarize_research(rated_results, question)

                                # If available, append reasoning insights to research
                                if enhanced_forecast:
                                    research += f"\n\n## MULTI-MODEL REASONING INSIGHTS\n\n{enhanced_forecast}"

                                logger.info(f"Parallel research with reasoning completed successfully ({len(research)} characters)")
                                main_logger.info(f"🧠 REASONING: Enhanced research with reasoning completed")
                                return research
                        else:
                            logger.warning("No search results from parallel research, falling back to enhanced retrieval")

                    except Exception as parallel_error:
                        logger.warning(f"Parallel research failed: {parallel_error}, falling back to enhanced retrieval")

                # Fallback to enhanced retrieval (original logic)
                researcher = self.get_llm("researcher")
                if researcher is None:
                    logger.error(f"Researcher LLM is None for question {question.page_url}")
                    return ""

                # Use enhanced retrieval system by default
                if researcher == "enhanced-retrieval" or True:  # Always use enhanced retrieval
                    try:
                        default_llm = self.get_llm("default", "llm")
                        if default_llm is None:
                            logger.error(f"Default LLM is None for question {question.page_url}, trying to get directly")
                            # Try to instantiate a new LLM directly to avoid configuration issues
                            openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
                            if not openrouter_api_key:
                                logger.error("OPENROUTER_API_KEY not available")
                                return ""
                            
                            from forecasting_tools import GeneralLlm
                            temp_llm = GeneralLlm(
                                model="openrouter/openai/gpt-4o-mini",  # Use a reliable model
                                api_key=openrouter_api_key,
                                temperature=0.5,
                                timeout=60,
                                allowed_tries=2,
                            )
                            enhanced_retrieval = EnhancedRetrievalSystem(temp_llm)
                            research = await enhanced_retrieval.enhanced_retrieve(question)
                        else:
                            enhanced_retrieval = EnhancedRetrievalSystem(default_llm)
                            research = await enhanced_retrieval.enhanced_retrieve(question)
                    except Exception as e:
                        logger.warning(f"Enhanced retrieval failed: {str(e)}, falling back to basic research")
                        # Fallback to basic research
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
                        llm = self.get_llm("researcher", "llm")
                        if llm is None:
                            logger.error(f"Researcher LLM is None for question {question.page_url}")
                            return ""
                        try:
                            research = await llm.invoke(prompt)
                        except Exception as llm_error:
                            logger.error(f"Researcher LLM invoke failed: {str(llm_error)}. Question: {question.page_url}")
                            # Try with default LLM as a last resort
                            default_llm = self.get_llm("default", "llm")
                            if default_llm:
                                try:
                                    research = await default_llm.invoke(prompt)
                                except Exception as final_error:
                                    logger.error(f"Final fallback failed for question {question.page_url}: {str(final_error)}")
                                    return ""
                else:
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

                    if isinstance(researcher, GeneralLlm):
                        research = await researcher.invoke(prompt)
                    elif researcher == "asknews/news-summaries":
                        research = await AskNewsSearcher().get_formatted_news_async(
                            question.question_text
                        )
                    elif researcher == "asknews/deep-research/medium-depth":
                        research = await AskNewsSearcher().get_formatted_deep_research(
                            question.question_text,
                            sources=["asknews", "google"],
                            search_depth=2,
                            max_depth=4,
                        )
                    elif researcher == "asknews/deep-research/high-depth":
                        research = await AskNewsSearcher().get_formatted_deep_research(
                            question.question_text,
                            sources=["asknews", "google"],
                            search_depth=4,
                            max_depth=6,
                        )
                    elif researcher.startswith("smart-searcher"):
                        model_name = researcher.removeprefix("smart-searcher/")
                        searcher = SmartSearcher(
                            model=model_name,
                            temperature=0,
                            num_searches_to_run=2,
                            num_sites_per_search=10,
                            use_advanced_filters=False,
                        )
                        research = await searcher.invoke(prompt)
                    elif not researcher or researcher == "None":
                        research = ""
                    else:
                        research = await self.get_llm("researcher", "llm").invoke(prompt)
                        
                logger.info(f"Found Research for URL {question.page_url}:\\n{research if research else 'No research content'}")
                return research
                
            except Exception as e:
                logger.error(f"Primary researcher completely failed for URL {question.page_url}: {str(e)}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")

                # Final fallback: basic research
                logger.warning("All advanced research methods failed, using basic research fallback")
                try:
                    research = await self._basic_research_fallback(question)
                    if research:
                        logger.info("Basic research fallback succeeded")
                        return research
                except Exception as fallback_error:
                    logger.error(f"Basic research fallback also failed: {fallback_error}")

                # Return empty research rather than failing completely
                return ""

    async def _basic_research_fallback(self, question: MetaculusQuestion) -> str:
        """
        Basic research fallback when all advanced methods fail.
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
                logger.error("No researcher LLM available for basic research fallback")
                return ""

        except Exception as e:
            logger.error(f"Basic research fallback failed: {e}")
            return ""

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def _run_forecast_on_binary(
        self, question: BinaryQuestion, research: str
    ) -> ReasonedPrediction[float]:
        # Check if we should use the optimized reasoning system
        use_optimized_reasoning = os.getenv('USE_OPTIMIZED_REASONING', 'true').lower() == 'true'
        
        try:
            if use_optimized_reasoning:
                # Use the optimized reasoning system - RESTORE ORIGINAL WORKING LOGIC
                optimizer = OptimizedReasoningSystem(self.get_llm("default", "llm"))

                # Define forecaster models (only 4 forecasters)
                forecaster_keys = ["forecaster1", "forecaster2", "forecaster3", "forecaster4"]
                individual_reasonings = []
                individual_predictions = []
                successful_forecasters = []

                # Generate individual forecasts with multiple runs and median selection
                for key in forecaster_keys:
                    try:
                        logger.info(f"Running multiple forecasts for {key} with median selection")

                        # Use multiple runs with median selection
                        predictions, reasonings = await self.run_multiple_forecasting_runs(
                            question, research, key, self._num_forecasting_runs
                        )

                        if predictions:
                            # Calculate median prediction for this forecaster
                            median_pred = self.calculate_median_prediction(predictions)
                            median_reasoning = self.select_median_reasoning(predictions, reasonings)

                            logger.info(f"Median forecast from {key}: {median_pred} (from {len(predictions)} runs)")

                            individual_reasonings.append(f"Median of {len(predictions)} runs: {median_reasoning}")
                            individual_predictions.append(median_pred)
                            successful_forecasters.append(key)
                            model_name = self.forecaster_models.get(key, 'unknown')
                            logger.info(f"Median forecast from {key} ({model_name}) for URL {question.page_url}: {median_pred}")
                        else:
                            logger.warning(f"No successful runs for {key}, skipping")
                    except Exception as e:
                        logger.warning(f"Forecaster {key} failed for URL {question.page_url}: {str(e)}")
                        continue

                # Check if we have any successful forecasts
                if not successful_forecasters:
                    logger.error(f"All forecasters failed for binary question URL {question.page_url}")
                    # Return a default prediction
                    return ReasonedPrediction(prediction_value=0.5, reasoning="All forecasters failed, defaulting to 50% probability")

                # Synthesize final prediction with rate limiting
                async with self._llm_rate_limiter:  # Rate limit LLM calls
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
                        Compare these: Highlight agreements/disagreements, resolve via heuristics (base rates, Bayesian updates, Fermi, intangibles, qualitative elements, wide intervals, bias avoidance). Synthesize a final balanced probability.

                        Output only the final probability as: "Probability: ZZ%", 0-100
                        """
                    )

                    try:
                        synth_llm = self.get_llm("synthesizer", "llm")
                        if synth_llm is None:
                            # Fallback to default LLM
                            synth_llm = self.get_llm("default", "llm")

                        synth_model_name = self.forecaster_models.get('synthesizer', 'openai/gpt-4o')
                        synth_reasoning = await synth_llm.invoke(synth_prompt)
                        logger.info(f"Synthesized reasoning (using {synth_model_name}) for URL {question.page_url}: {synth_reasoning}")

                        try:
                            parser_llm = self.get_llm("parser", "llm")
                            if parser_llm is None:
                                # Fallback to default LLM
                                parser_llm = self.get_llm("default", "llm")

                            parser_model_name = self.forecaster_models.get('parser', 'openai/gpt-4o-mini')
                            final_binary_prediction: BinaryPrediction = await structure_output(
                                synth_reasoning, BinaryPrediction, model=parser_llm
                            )
                            final_decimal_pred = max(0.01, min(0.99, final_binary_prediction.prediction_in_decimal))
                            logger.info(f"Synthesized final prediction (parsed with {parser_model_name}) for URL {question.page_url}: {final_decimal_pred}")
                        except Exception as parser_e:
                            logger.warning(f"Parser failed for URL {question.page_url}, using fallback: {str(parser_e)}")
                            # Fallback: extract probability from synthesis reasoning
                            import re
                            match = re.search(r'(\d+)%', synth_reasoning)
                            if match:
                                final_decimal_pred = float(match.group(1)) / 100.0
                                final_decimal_pred = max(0.01, min(0.99, final_decimal_pred))
                            else:
                                final_decimal_pred = 0.5  # Default fallback
                    except Exception as synth_e:
                        logger.warning(f"Synthesizer failed for URL {question.page_url}, using average: {str(synth_e)}")
                        # Fallback: average all predictions
                        final_decimal_pred = sum(individual_predictions) / len(individual_predictions)
                        final_decimal_pred = max(0.01, min(0.99, final_decimal_pred))
                        synth_reasoning = "Synthesizer failed, used average of individual predictions"

                # Combined reasoning with model names
                combined_reasoning_parts = []
                for i, (key, reasoning) in enumerate(zip(successful_forecasters, individual_reasonings)):
                    model_name = self.forecaster_models.get(key, 'unknown')
                    combined_reasoning_parts.append(f"Forecaster {i+1} ({key}: {model_name}): {reasoning}")
                combined_reasoning_parts.append(f"Synthesis: {synth_reasoning}")
                combined_reasoning = "\n\n".join(combined_reasoning_parts)

                return ReasonedPrediction(prediction_value=final_decimal_pred, reasoning=combined_reasoning)
            else:
                # Use the original reasoning system
                prompt = clean_indents(
                    f"""
                    You are a professional forecaster interviewing for a job.

                    Your interview question is:
                    {question.question_text}

                    Question background:
                    {question.background_info}


                    This question's outcome will be determined by the specific criteria below. These criteria have not yet been satisfied:
                    {question.resolution_criteria}

                    {question.fine_print}


                    Your research assistant says:
                    {research}

                    Today is {datetime.now().strftime("%Y-%m-%d")}.

                    Before answering you write:
                    (a) The time left until the outcome to the question is known.
                    (b) The status quo outcome if nothing changed.
                    (c) A brief description of a scenario that results in a No outcome.
                    (d) A brief description of a scenario that results in a Yes outcome.

                    You write your rationale remembering that good forecasters put extra weight on the status quo outcome since the world changes slowly most of the time. Avoid overconfidence by assigning moderate probabilities and leaving room for uncertainty. Don't be contrarian for its own sake, but look for information, factors, and influences that the consensus may be missing. Use nuanced weighting: anchor with outside view base rate to avoid anchoring bias, then move to inside view. Accurately update based on new information (Bayesianism). Use Fermi estimates if applicable by breaking down into easier steps. Read the rules carefully. Utilize different points of view (teams of superforecasters) and incorporate feedback. Forecast changes should be gradual. Be actively open-minded and avoid biases like scope insensitivity or need for narrative coherence.

                    The last thing you write is your final answer as: "Probability: ZZ%", 0-100
                    """
                )
                
                # Define forecaster models (only 4 forecasters)
                forecaster_keys = ["forecaster1", "forecaster2", "forecaster3", "forecaster4"]
                individual_reasonings = []
                individual_predictions = []
                successful_forecasters = []

                # Generate individual forecasts with error handling
                for key in forecaster_keys:
                    try:
                        async with self._llm_rate_limiter:  # Rate limit LLM calls
                            llm = self.get_llm(key, "llm")
                            if llm is None:
                                logger.warning(f"LLM for {key} is None, skipping")
                                continue
                                
                            reasoning = await llm.invoke(prompt)
                            # Log full reasoning with proper formatting
                            logger.info(f"=== FORECASTER {key.upper()} REASONING ===")
                            main_logger.info(f"=== FORECASTER {key.upper()} REASONING ===")
                            logger.info(f"Model: {self.forecaster_models.get(key, 'unknown')}")
                            main_logger.info(f"Model: {self.forecaster_models.get(key, 'unknown')}")
                            logger.info(f"Question: {question.page_url}")
                            main_logger.info(f"Question: {question.page_url}")
                            logger.info(f"Full Reasoning:\n{reasoning}")
                            main_logger.info(f"Full Reasoning:\n{reasoning}")
                            logger.info(f"=== END {key.upper()} REASONING ===")
                            main_logger.info(f"=== END {key.upper()} REASONING ===")
                            binary_prediction: BinaryPrediction = await structure_output(
                                reasoning, BinaryPrediction, model=self.get_llm("parser", "llm")
                            )
                            decimal_pred = max(0.01, min(0.99, binary_prediction.prediction_in_decimal))
                            individual_reasonings.append(reasoning)
                            individual_predictions.append(decimal_pred)
                            successful_forecasters.append(key)
                            model_name = self.forecaster_models.get(key, 'unknown')
                            logger.info(f"Forecast from {key} ({model_name}) for URL {question.page_url}: {decimal_pred}")
                    except Exception as e:
                        logger.warning(f"Forecaster {key} failed for URL {question.page_url}: {str(e)}")
                        continue

                # Check if we have any successful forecasts
                if not successful_forecasters:
                    logger.error(f"All forecasters failed for binary question URL {question.page_url}")
                    # Return a default prediction
                    return ReasonedPrediction(prediction_value=0.5, reasoning="All forecasters failed, defaulting to 50% probability")

                # Synthesize final prediction with rate limiting
                async with self._llm_rate_limiter:  # Rate limit LLM calls
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
                        Compare these: Highlight agreements/disagreements, resolve via heuristics (base rates, Bayesian updates, Fermi, intangibles, qualitative elements, wide intervals, bias avoidance). Synthesize a final balanced probability.

                        Output only the final probability as: "Probability: ZZ%", 0-100
                        """
                    )

                    try:
                        synth_llm = self.get_llm("synthesizer", "llm")
                        if synth_llm is None:
                            # Fallback to default LLM
                            synth_llm = self.get_llm("default", "llm")
                            
                        synth_model_name = self.forecaster_models.get('synthesizer', 'openai/gpt-4o')
                        synth_reasoning = await synth_llm.invoke(synth_prompt)
                        logger.info(f"Synthesized reasoning (using {synth_model_name}) for URL {question.page_url}: {synth_reasoning}")
                        
                        try:
                            parser_llm = self.get_llm("parser", "llm")
                            if parser_llm is None:
                                # Fallback to default LLM
                                parser_llm = self.get_llm("default", "llm")
                                
                            parser_model_name = self.forecaster_models.get('parser', 'openai/gpt-4o-mini')
                            final_binary_prediction: BinaryPrediction = await structure_output(
                                synth_reasoning, BinaryPrediction, model=parser_llm
                            )
                            final_decimal_pred = max(0.01, min(0.99, final_binary_prediction.prediction_in_decimal))
                            logger.info(f"Synthesized final prediction (parsed with {parser_model_name}) for URL {question.page_url}: {final_decimal_pred}")
                        except Exception as parser_e:
                            logger.warning(f"Parser failed for URL {question.page_url}, using fallback: {str(parser_e)}")
                            # Fallback: extract probability from synthesis reasoning
                            import re
                            match = re.search(r'(\d+)%', synth_reasoning)
                            if match:
                                final_decimal_pred = float(match.group(1)) / 100.0
                                final_decimal_pred = max(0.01, min(0.99, final_decimal_pred))
                            else:
                                final_decimal_pred = 0.5  # Default fallback
                    except Exception as synth_e:
                        logger.warning(f"Synthesizer failed for URL {question.page_url}, using average: {str(synth_e)}")
                        # Fallback: average all predictions
                        final_decimal_pred = sum(individual_predictions) / len(individual_predictions)
                        final_decimal_pred = max(0.01, min(0.99, final_decimal_pred))
                        synth_reasoning = "Synthesizer failed, used average of individual predictions"

                # Combined reasoning with model names
                combined_reasoning_parts = []
                for i, (key, reasoning) in enumerate(zip(successful_forecasters, individual_reasonings)):
                    model_name = self.forecaster_models.get(key, 'unknown')
                    combined_reasoning_parts.append(f"Forecaster {i+1} ({key}: {model_name}): {reasoning}")
                combined_reasoning_parts.append(f"Synthesis: {synth_reasoning}")
                combined_reasoning = "\n\n".join(combined_reasoning_parts)

                return ReasonedPrediction(prediction_value=final_decimal_pred, reasoning=combined_reasoning)
        except Exception as e:
            logger.error(f"Error in binary forecasting for URL {question.page_url}: {str(e)}")
            # Return a default prediction with error reasoning
            return ReasonedPrediction(prediction_value=0.5, reasoning=f"Error in forecasting process: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def _run_forecast_on_multiple_choice(
        self, question: MultipleChoiceQuestion, research: str
    ) -> ReasonedPrediction[PredictedOptionList]:
        # Check if we should use the optimized reasoning system
        use_optimized_reasoning = os.getenv('USE_OPTIMIZED_REASONING', 'true').lower() == 'true'
        
        try:
            if use_optimized_reasoning:
                # Optimized reasoning system disabled - this should not be reached
                logger.warning("Optimized reasoning system is disabled")
                default_probs = {option: 1.0/len(question.options) for option in question.options}
                return ReasonedPrediction(
                    prediction_value=default_probs,
                    reasoning="Optimized reasoning system disabled"
                )
            else:
                # Use the original reasoning system
                prompt = clean_indents(
                    f"""
                    You are a professional forecaster interviewing for a job.

                    Your interview question is:
                    {question.question_text}

                    The options are: {question.options}


                    Background:
                    {question.background_info}

                    {question.resolution_criteria}

                    {question.fine_print}


                    Your research assistant says:
                    {research}

                    Today is {datetime.now().strftime("%Y-%m-%d")}.

                    Before answering you write:
                    (a) The time left until the outcome to the question is known.
                    (b) The status quo outcome if nothing changed.
                    (c) A description of an scenario that results in an unexpected outcome.

                    You write your rationale remembering that (1) good forecasters put extra weight on the status quo outcome since the world changes slowly most of the time, and (2) good forecasters leave some moderate probability on most options to account for unexpected outcomes. Avoid overconfidence by distributing probabilities moderately. Don't be contrarian for its own sake, but look for information, factors, and influences that the consensus may be missing. Use nuanced weighting: anchor with outside view base rate to avoid anchoring bias, then move to inside view. Accurately update based on new information (Bayesianism). Use Fermi estimates if applicable by breaking down into easier steps. Read the rules carefully. Utilize different points of view (teams of superforecasters) and incorporate feedback. Forecast changes should be gradual. Be actively open-minded and avoid biases like scope insensitivity or need for narrative coherence.

                    The last thing you write is your final probabilities for the N options in this order {question.options} as:
                    Option_A: Probability_A
                    Option_B: Probability_B
                    ... 
                    Option_N: Probability_N
                    """
                )
                parsing_instructions = clean_indents(
                    f"""
                    Make sure that all option names are one of the following:
                    {question.options}
                    The text you are parsing may prepend these options with some variation of "Option" which you should remove if not part of the option names I just gave you.
                    """
                )
                
                # Define forecaster models (only 4 forecasters)
                forecaster_keys = ["forecaster1", "forecaster2", "forecaster3", "forecaster4"]
                individual_reasonings = []
                individual_predictions = []
                successful_forecasters = []

                # Generate individual forecasts with error handling
                for key in forecaster_keys:
                    try:
                        async with self._llm_rate_limiter:  # Rate limit LLM calls
                            llm = self.get_llm(key, "llm")
                            if llm is None:
                                logger.warning(f"LLM for {key} is None, skipping")
                                continue
                                
                            reasoning = await llm.invoke(prompt)
                            # Log full reasoning with proper formatting
                            logger.info(f"=== FORECASTER {key.upper()} REASONING ===")
                            main_logger.info(f"=== FORECASTER {key.upper()} REASONING ===")
                            logger.info(f"Model: {self.forecaster_models.get(key, 'unknown')}")
                            main_logger.info(f"Model: {self.forecaster_models.get(key, 'unknown')}")
                            logger.info(f"Question: {question.page_url}")
                            main_logger.info(f"Question: {question.page_url}")
                            logger.info(f"Full Reasoning:\n{reasoning}")
                            main_logger.info(f"Full Reasoning:\n{reasoning}")
                            logger.info(f"=== END {key.upper()} REASONING ===")
                            main_logger.info(f"=== END {key.upper()} REASONING ===")
                            predicted_option_list: PredictedOptionList = await structure_output(
                                text_to_structure=reasoning,
                                output_type=PredictedOptionList,
                                model=self.get_llm("parser", "llm"),
                                additional_instructions=parsing_instructions,
                            )
                            individual_reasonings.append(reasoning)
                            individual_predictions.append(predicted_option_list)
                            successful_forecasters.append(key)
                            model_name = self.forecaster_models.get(key, 'unknown')
                            logger.info(f"Forecast from {key} ({model_name}) for URL {question.page_url}: {predicted_option_list}")
                    except Exception as e:
                        logger.warning(f"Forecaster {key} failed for URL {question.page_url}: {str(e)}")
                        continue

                # Check if we have any successful forecasts
                if not successful_forecasters:
                    logger.error(f"All forecasters failed for multiple choice question URL {question.page_url}")
                    # Return a default prediction with equal probabilities
                    default_probs = {option: 1.0/len(question.options) for option in question.options}
                    return ReasonedPrediction(
                        prediction_value=default_probs, 
                        reasoning="All forecasters failed, defaulting to equal probabilities"
                    )

                # Synthesize final prediction
                async with self._llm_rate_limiter:  # Rate limit LLM calls
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
                        Option_N: Probability_N
                        """
                    )

                    try:
                        synth_llm = self.get_llm("synthesizer", "llm")
                        if synth_llm is None:
                            # Fallback to default LLM
                            synth_llm = self.get_llm("default", "llm")
                            
                        synth_model_name = self.forecaster_models.get('synthesizer', 'openai/gpt-4o')
                        synth_reasoning = await synth_llm.invoke(synth_prompt)
                        logger.info(f"Synthesized reasoning (using {synth_model_name}) for URL {question.page_url}: {synth_reasoning}")
                        
                        try:
                            parser_llm = self.get_llm("parser", "llm")
                            if parser_llm is None:
                                # Fallback to default LLM
                                parser_llm = self.get_llm("default", "llm")
                                
                            parser_model_name = self.forecaster_models.get('parser', 'openai/gpt-4o-mini')
                            final_predicted_option_list: PredictedOptionList = await structure_output(
                                text_to_structure=synth_reasoning,
                                output_type=PredictedOptionList,
                                model=parser_llm,
                                additional_instructions=parsing_instructions,
                            )
                            logger.info(f"Synthesized final prediction (parsed with {parser_model_name}) for URL {question.page_url}: {final_predicted_option_list}")
                        except Exception as parser_e:
                            logger.warning(f"Parser failed for URL {question.page_url}, using fallback: {str(parser_e)}")
                            # Fallback: use average of individual predictions
                            final_predicted_option_list = self._average_multiple_choice_predictions(individual_predictions, question.options)
                    except Exception as synth_e:
                        logger.warning(f"Synthesizer failed for URL {question.page_url}, using average: {str(synth_e)}")
                        # Fallback: use average of individual predictions
                        final_predicted_option_list = self._average_multiple_choice_predictions(individual_predictions, question.options)
                        synth_reasoning = "Synthesizer failed, used average of individual predictions"

                # Combined reasoning with model names
                combined_reasoning_parts = []
                for i, (key, reasoning) in enumerate(zip(successful_forecasters, individual_reasonings)):
                    model_name = self.forecaster_models.get(key, 'unknown')
                    combined_reasoning_parts.append(f"Forecaster {i+1} ({key}: {model_name}): {reasoning}")
                combined_reasoning_parts.append(f"Synthesis: {synth_reasoning}")
                combined_reasoning = "\n\n".join(combined_reasoning_parts)

                return ReasonedPrediction(
                    prediction_value=final_predicted_option_list, reasoning=combined_reasoning
                )
        except Exception as e:
            logger.error(f"Error in multiple choice forecasting for URL {question.page_url}: {str(e)}")
            # Return a default prediction with error reasoning
            default_probs = {option: 1.0/len(question.options) for option in question.options}
            return ReasonedPrediction(
                prediction_value=default_probs, 
                reasoning=f"Error in forecasting process: {str(e)}"
            )

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def _run_forecast_on_numeric(
        self, question: NumericQuestion, research: str
    ) -> ReasonedPrediction[NumericDistribution]:
        # Check if we should use the optimized reasoning system
        use_optimized_reasoning = os.getenv('USE_OPTIMIZED_REASONING', 'true').lower() == 'true'
        
        try:
            if use_optimized_reasoning:
                # Use the optimized reasoning system
                # optimizer = OptimizedReasoningSystem(self.get_llm("default", "llm"))  # Temporarily disabled
                
                # Define forecaster models (only 4 forecasters)
                forecaster_keys = ["forecaster1", "forecaster2", "forecaster3", "forecaster4"]
                individual_reasonings = []
                individual_predictions = []
                successful_forecasters = []

                # Generate individual forecasts with rate limiting and error handling
                for key in forecaster_keys:
                    try:
                        async with self._llm_rate_limiter:  # Rate limit LLM calls
                            llm = self.get_llm(key, "llm")
                            if llm is None:
                                logger.warning(f"LLM for {key} is None, skipping")
                                continue
                                
                            # Use standard numeric forecast instead of optimized system
                            result = await self._run_individual_numeric_forecast(llm, question, research)
                            reasoning = result["reasoning"]
                            prediction = result["distribution"]
                            logger.info(f"Reasoning from {key} for URL {question.page_url}: {reasoning}")
                            individual_reasonings.append(reasoning)
                            individual_predictions.append(prediction)
                            successful_forecasters.append(key)
                            model_name = self.forecaster_models.get(key, 'unknown')
                            logger.info(f"Forecast from {key} ({model_name}) for URL {question.page_url}: {prediction.declared_percentiles}")
                    except Exception as e:
                        logger.warning(f"Forecaster {key} failed for URL {question.page_url}: {str(e)}")
                        continue

                # Check if we have any successful forecasts
                if not successful_forecasters:
                    logger.error(f"All forecasters failed for numeric question URL {question.page_url}")
                    # Return a default prediction
                    default_percentiles = [
                        Percentile(percentile=0.1, value=question.lower_bound),
                        Percentile(percentile=0.2, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.2),
                        Percentile(percentile=0.4, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.4),
                        Percentile(percentile=0.6, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.6),
                        Percentile(percentile=0.8, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.8),
                        Percentile(percentile=0.9, value=question.upper_bound),
                    ]
                    default_prediction = NumericDistribution.from_question(default_percentiles, question)
                    return ReasonedPrediction(
                        prediction_value=default_prediction, 
                        reasoning="All forecasters failed, defaulting to uniform distribution"
                    )

                # Synthesize final prediction with rate limiting
                async with self._llm_rate_limiter:  # Rate limit LLM calls
                    synth_prompt = clean_indents(
                        f"""
                        You are a synthesizer comparing multiple forecaster outputs for a numeric question.

                        Question: {question.question_text}

                        Individual forecasts:
                        """
                    )
                    for i, (reason, pred) in enumerate(zip(individual_reasonings, individual_predictions), 1):
                        synth_prompt += f"\nForecaster {i}: Reasoning: {reason}\nPrediction: {pred.declared_percentiles}\n"

                    synth_prompt += clean_indents(
                        f"""
                        Compare these: Highlight agreements/disagreements, resolve via heuristics (base rates, Bayesian updates, Fermi, intangibles, qualitative elements, wide intervals, bias avoidance). Synthesize a final balanced distribution.

                        Output only the final percentiles:
                        Percentile 10: XX
                        Percentile 20: XX
                        Percentile 40: XX
                        Percentile 60: XX
                        Percentile 80: XX
                        Percentile 90: XX
                        """
                    )

                    try:
                        synth_llm = self.get_llm("synthesizer", "llm")
                        if synth_llm is None:
                            # Fallback to default LLM
                            synth_llm = self.get_llm("default", "llm")
                            
                        synth_model_name = self.forecaster_models.get('synthesizer', 'openai/gpt-4o')
                        synth_reasoning = await synth_llm.invoke(synth_prompt)
                        logger.info(f"Synthesized reasoning (using {synth_model_name}) for URL {question.page_url}: {synth_reasoning}")
                        
                        try:
                            parser_llm = self.get_llm("parser", "llm")
                            if parser_llm is None:
                                # Fallback to default LLM
                                parser_llm = self.get_llm("default", "llm")
                                
                            parser_model_name = self.forecaster_models.get('parser', 'openai/gpt-4o-mini')
                            final_percentile_list: list[Percentile] = await structure_output(
                                synth_reasoning, list[Percentile], model=parser_llm
                            )
                            final_prediction = NumericDistribution.from_question(final_percentile_list, question)
                            logger.info(f"Synthesized final prediction (parsed with {parser_model_name}) for URL {question.page_url}: {final_prediction.declared_percentiles}")
                        except Exception as parser_e:
                            logger.warning(f"Parser failed for URL {question.page_url}, using fallback: {str(parser_e)}")
                            # Fallback: average individual predictions
                            final_prediction = self._average_numeric_predictions(individual_predictions, question)
                    except Exception as synth_e:
                        logger.warning(f"Synthesizer failed for URL {question.page_url}, using average: {str(synth_e)}")
                        # Fallback: average individual predictions
                        final_prediction = self._average_numeric_predictions(individual_predictions, question)
                        synth_reasoning = "Synthesizer failed, used average of individual predictions"

                # Combined reasoning with model names
                combined_reasoning_parts = []
                for i, (key, reasoning) in enumerate(zip(successful_forecasters, individual_reasonings)):
                    model_name = self.forecaster_models.get(key, 'unknown')
                    combined_reasoning_parts.append(f"Forecaster {i+1} ({key}: {model_name}): {reasoning}")
                combined_reasoning_parts.append(f"Synthesis: {synth_reasoning}")
                combined_reasoning = "\n\n".join(combined_reasoning_parts)

                return ReasonedPrediction(prediction_value=final_prediction, reasoning=combined_reasoning)
            else:
                # Use the original reasoning system
                upper_bound_message, lower_bound_message = (
                    self._create_upper_and_lower_bound_messages(question)
                )
                prompt = clean_indents(
                    f"""
                    You are a professional forecaster interviewing for a job.

                    Your interview question is:
                    {question.question_text}

                    Background:
                    {question.background_info}

                    {question.resolution_criteria}

                    {question.fine_print}

                    Units for answer: {question.unit_of_measure if question.unit_of_measure else "Not stated (please infer this)"}

                    Your research assistant says:
                    {research}

                    Today is {datetime.now().strftime("%Y-%m-%d")}.

                    {lower_bound_message}
                    {upper_bound_message}

                    Formatting Instructions:
                    - Please notice the units requested (e.g. whether you represent a number as 1,000,000 or 1 million).
                    - Never use scientific notation.
                    - Always start with a smaller number (more negative if negative) and then increase from there

                    Before answering you write:
                    (a) The time left until the outcome to the question is known.
                    (b) The outcome if nothing changed.
                    (c) The outcome if the current trend continued.
                    (d) The expectations of experts and markets.
                    (e) A brief description of an unexpected scenario that results in a low outcome.
                    (f) A brief description of an unexpected scenario that results in a high outcome.

                    You remind yourself that good forecasters are humble and set wide 90/10 confidence intervals to account for unknown unknowns. Avoid overconfidence by using wide distributions. Don't be contrarian for its own sake, but look for information, factors, and influences that the consensus may be missing. Use nuanced weighting: anchor with outside view base rate to avoid anchoring bias, then move to inside view. Accurately update based on new information (Bayesianism). Use Fermi estimates by breaking down questions into series of easier steps. Read the rules carefully. Utilize different points of view (teams of superforecasters) and incorporate feedback. Forecast changes should be gradual. Be actively open-minded and avoid biases like scope insensitivity or need for narrative coherence.

                    The last thing you write is your final answer as:
                    "
                    Percentile 10: XX
                    Percentile 20: XX
                    Percentile 40: XX
                    Percentile 60: XX
                    Percentile 80: XX
                    Percentile 90: XX
                    "
                    """
                )
                # Define forecaster models (only 4 forecasters)
                forecaster_keys = ["forecaster1", "forecaster2", "forecaster3", "forecaster4"]
                individual_reasonings = []
                individual_predictions = []
                successful_forecasters = []

                # Generate individual forecasts with error handling
                for key in forecaster_keys:
                    try:
                        async with self._llm_rate_limiter:  # Rate limit LLM calls
                            llm = self.get_llm(key, "llm")
                            if llm is None:
                                logger.warning(f"LLM for {key} is None, skipping")
                                continue
                                
                            reasoning = await llm.invoke(prompt)
                            # Log full reasoning with proper formatting
                            logger.info(f"=== FORECASTER {key.upper()} REASONING ===")
                            main_logger.info(f"=== FORECASTER {key.upper()} REASONING ===")
                            logger.info(f"Model: {self.forecaster_models.get(key, 'unknown')}")
                            main_logger.info(f"Model: {self.forecaster_models.get(key, 'unknown')}")
                            logger.info(f"Question: {question.page_url}")
                            main_logger.info(f"Question: {question.page_url}")
                            logger.info(f"Full Reasoning:\n{reasoning}")
                            main_logger.info(f"Full Reasoning:\n{reasoning}")
                            logger.info(f"=== END {key.upper()} REASONING ===")
                            main_logger.info(f"=== END {key.upper()} REASONING ===")
                            percentile_list: list[Percentile] = await structure_output(
                                reasoning, list[Percentile], model=self.get_llm("parser", "llm")
                            )
                            prediction = NumericDistribution.from_question(percentile_list, question)
                            individual_reasonings.append(reasoning)
                            individual_predictions.append(prediction)
                            successful_forecasters.append(key)
                            model_name = self.forecaster_models.get(key, 'unknown')
                            logger.info(f"Forecast from {key} ({model_name}) for URL {question.page_url}: {prediction.declared_percentiles}")
                    except Exception as e:
                        logger.warning(f"Forecaster {key} failed for URL {question.page_url}: {str(e)}")
                        continue

                # Check if we have any successful forecasts
                if not successful_forecasters:
                    logger.error(f"All forecasters failed for numeric question URL {question.page_url}")
                    # Return a default prediction
                    default_percentiles = [
                        Percentile(percentile=0.1, value=question.lower_bound),
                        Percentile(percentile=0.2, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.2),
                        Percentile(percentile=0.4, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.4),
                        Percentile(percentile=0.6, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.6),
                        Percentile(percentile=0.8, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.8),
                        Percentile(percentile=0.9, value=question.upper_bound),
                    ]
                    default_prediction = NumericDistribution.from_question(default_percentiles, question)
                    return ReasonedPrediction(
                        prediction_value=default_prediction, 
                        reasoning="All forecasters failed, defaulting to uniform distribution"
                    )

                # Synthesize final prediction
                async with self._llm_rate_limiter:  # Rate limit LLM calls
                    synth_prompt = clean_indents(
                        f"""
                        You are a synthesizer comparing multiple forecaster outputs for a numeric question.

                        Question: {question.question_text}

                        Individual forecasts:
                        """
                    )
                    for i, (reason, pred) in enumerate(zip(individual_reasonings, individual_predictions), 1):
                        synth_prompt += f"\nForecaster {i}: Reasoning: {reason}\nPrediction: {pred.declared_percentiles}\n"

                    synth_prompt += clean_indents(
                        f"""
                        Compare these: Highlight agreements/disagreements, resolve via heuristics (base rates, Bayesian updates, Fermi, intangibles, qualitative elements, wide intervals, bias avoidance). Synthesize a final balanced distribution.

                        Output only the final percentiles:
                        Percentile 10: XX
                        Percentile 20: XX
                        Percentile 40: XX
                        Percentile 60: XX
                        Percentile 80: XX
                        Percentile 90: XX
                        """
                    )

                    try:
                        synth_llm = self.get_llm("synthesizer", "llm")
                        if synth_llm is None:
                            # Fallback to default LLM
                            synth_llm = self.get_llm("default", "llm")
                            
                        synth_model_name = self.forecaster_models.get('synthesizer', 'openai/gpt-4o')
                        synth_reasoning = await synth_llm.invoke(synth_prompt)
                        logger.info(f"Synthesized reasoning (using {synth_model_name}) for URL {question.page_url}: {synth_reasoning}")
                        
                        try:
                            parser_llm = self.get_llm("parser", "llm")
                            if parser_llm is None:
                                # Fallback to default LLM
                                parser_llm = self.get_llm("default", "llm")
                                
                            parser_model_name = self.forecaster_models.get('parser', 'openai/gpt-4o-mini')
                            final_percentile_list: list[Percentile] = await structure_output(
                                synth_reasoning, list[Percentile], model=parser_llm
                            )
                            final_prediction = NumericDistribution.from_question(final_percentile_list, question)
                            logger.info(f"Synthesized final prediction (parsed with {parser_model_name}) for URL {question.page_url}: {final_prediction.declared_percentiles}")
                        except Exception as parser_e:
                            logger.warning(f"Parser failed for URL {question.page_url}, using fallback: {str(parser_e)}")
                            # Fallback: average individual predictions
                            final_prediction = self._average_numeric_predictions(individual_predictions, question)
                    except Exception as synth_e:
                        logger.warning(f"Synthesizer failed for URL {question.page_url}, using average: {str(synth_e)}")
                        # Fallback: average individual predictions
                        final_prediction = self._average_numeric_predictions(individual_predictions, question)
                        synth_reasoning = "Synthesizer failed, used average of individual predictions"

                # Combined reasoning with model names
                combined_reasoning_parts = []
                for i, (key, reasoning) in enumerate(zip(successful_forecasters, individual_reasonings)):
                    model_name = self.forecaster_models.get(key, 'unknown')
                    combined_reasoning_parts.append(f"Forecaster {i+1} ({key}: {model_name}): {reasoning}")
                combined_reasoning_parts.append(f"Synthesis: {synth_reasoning}")
                combined_reasoning = "\n\n".join(combined_reasoning_parts)

                return ReasonedPrediction(prediction_value=final_prediction, reasoning=combined_reasoning)
        except Exception as e:
            logger.error(f"Error in numeric forecasting for URL {question.page_url}: {str(e)}")
            # Return a default prediction with error reasoning
            default_percentiles = [
                Percentile(percentile=0.1, value=question.lower_bound),
                Percentile(percentile=0.2, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.2),
                Percentile(percentile=0.4, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.4),
                Percentile(percentile=0.6, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.6),
                Percentile(percentile=0.8, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.8),
                Percentile(percentile=0.9, value=question.upper_bound),
            ]
            default_prediction = NumericDistribution.from_question(default_percentiles, question)
            return ReasonedPrediction(
                prediction_value=default_prediction, 
                reasoning=f"Error in forecasting process: {str(e)}"
            )

    def _create_upper_and_lower_bound_messages(
        self,
        question: NumericQuestion,
    ) -> tuple[str, str]:
        if question.nominal_upper_bound is not None:
            upper_bound_number = question.nominal_upper_bound
        else:
            upper_bound_number = question.upper_bound
        if question.nominal_lower_bound is not None:
            lower_bound_number = question.nominal_lower_bound
        else:
            lower_bound_number = question.lower_bound

        if question.open_upper_bound:
            upper_bound_message = f"The question creator thinks the number is likely not higher than {upper_bound_number}."
        else:
            upper_bound_message = (
                f"The outcome can not be higher than {upper_bound_number}."
            )

        if question.open_lower_bound:
            lower_bound_message = f"The question creator thinks the number is likely not lower than {lower_bound_number}."
        else:
            lower_bound_message = (
                f"The outcome can not be lower than {lower_bound_number}."
            )
        return upper_bound_message, lower_bound_message

    def _average_multiple_choice_predictions(self, predictions: list, options: list) -> dict:
        """
        Average multiple choice predictions from different forecasters.
        """
        if not predictions:
            # Return equal probabilities if no predictions
            return {option: 1.0/len(options) for option in options}
        
        # Initialize averaged probabilities
        averaged_probs = {option: 0.0 for option in options}
        valid_predictions = 0
        
        # Sum up probabilities from all predictions
        for pred in predictions:
            try:
                if isinstance(pred, dict):
                    # If it's already a dictionary
                    for option in options:
                        if option in pred:
                            averaged_probs[option] += pred[option]
                        else:
                            # Try to find the option with different formatting
                            for key in pred.keys():
                                if option.lower() in key.lower() or key.lower() in option.lower():
                                    averaged_probs[option] += pred[key]
                                    break
                    valid_predictions += 1
                elif hasattr(pred, 'options') and hasattr(pred, 'probabilities'):
                    # If it's a PredictedOptionList object
                    for i, option in enumerate(pred.options):
                        if i < len(pred.probabilities) and option in options:
                            averaged_probs[option] += pred.probabilities[i]
                    valid_predictions += 1
            except Exception as e:
                logger.warning(f"Error processing prediction for averaging: {str(e)}")
                continue
        
        # Average the probabilities
        if valid_predictions > 0:
            for option in options:
                averaged_probs[option] /= valid_predictions
        
        # Normalize to ensure probabilities sum to 1.0
        total = sum(averaged_probs.values())
        if total > 0:
            for option in options:
                averaged_probs[option] /= total
        else:
            # If all probabilities are zero, use equal distribution
            for option in options:
                averaged_probs[option] = 1.0/len(options)
        
        return averaged_probs

    def _average_numeric_predictions(self, predictions: list, question: NumericQuestion) -> NumericDistribution:
        """
        Average numeric predictions from different forecasters.
        """
        if not predictions:
            # Return a default uniform distribution if no predictions
            default_percentiles = [
                Percentile(percentile=0.1, value=question.lower_bound),
                Percentile(percentile=0.2, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.2),
                Percentile(percentile=0.4, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.4),
                Percentile(percentile=0.6, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.6),
                Percentile(percentile=0.8, value=question.lower_bound + (question.upper_bound - question.lower_bound) * 0.8),
                Percentile(percentile=0.9, value=question.upper_bound),
            ]
            return NumericDistribution.from_question(default_percentiles, question)
        
        # Initialize averaged percentiles
        averaged_values = {0.1: 0.0, 0.2: 0.0, 0.4: 0.0, 0.6: 0.0, 0.8: 0.0, 0.9: 0.0}
        valid_predictions = 0
        
        # Sum up values from all predictions
        for pred in predictions:
            try:
                if hasattr(pred, 'declared_percentiles'):
                    # If it's a NumericDistribution object
                    for percentile_obj in pred.declared_percentiles:
                        if percentile_obj.percentile in averaged_values:
                            averaged_values[percentile_obj.percentile] += percentile_obj.value
                    valid_predictions += 1
                elif isinstance(pred, list):
                    # If it's a list of Percentile objects
                    for percentile_obj in pred:
                        if hasattr(percentile_obj, 'percentile') and hasattr(percentile_obj, 'value'):
                            if percentile_obj.percentile in averaged_values:
                                averaged_values[percentile_obj.percentile] += percentile_obj.value
                    valid_predictions += 1
            except Exception as e:
                logger.warning(f"Error processing numeric prediction for averaging: {str(e)}")
                continue
        
        # Average the values
        if valid_predictions > 0:
            for percentile in averaged_values:
                averaged_values[percentile] /= valid_predictions
        
        # Create percentile objects
        percentile_list = [
            Percentile(percentile=0.1, value=averaged_values[0.1]),
            Percentile(percentile=0.2, value=averaged_values[0.2]),
            Percentile(percentile=0.4, value=averaged_values[0.4]),
            Percentile(percentile=0.6, value=averaged_values[0.6]),
            Percentile(percentile=0.8, value=averaged_values[0.8]),
            Percentile(percentile=0.9, value=averaged_values[0.9]),
        ]
        
        # Create and return the distribution
        return NumericDistribution.from_question(percentile_list, question)

    async def _run_individual_binary_forecast(self, llm: GeneralLlm, question: BinaryQuestion, research: str) -> dict:
        """
        Run individual binary forecast for a single LLM.
        """
        prompt = clean_indents(f"""
            You are forecasting the following binary question.

            Question: {question.question_text}
            Background: {question.background_info}
            Resolution Criteria: {question.resolution_criteria}

            Research Information:
            {research}

            Provide your forecast as a probability between 0 and 1, where 0 means "no" and 1 means "yes".
            Also provide your reasoning.

            Respond in JSON format:
            {{
                "prediction": <probability between 0 and 1>,
                "reasoning": "<your detailed reasoning>"
            }}
        """)

        try:
            response = await llm.invoke(prompt)
            # Try to parse as JSON, handling markdown code blocks
            import json
            # Remove markdown code block formatting if present
            if response.strip().startswith('```json'):
                response = response.strip()[7:]  # Remove ```json
            if response.strip().endswith('```'):
                response = response.strip()[:-3]  # Remove ```
            result = json.loads(response.strip())
            return {
                "prediction": float(result.get("prediction", 0.5)),
                "reasoning": result.get("reasoning", "No reasoning provided")
            }
        except Exception as e:
            logger.warning(f"Error parsing binary forecast response: {e}")
            main_logger.warning(f"Error parsing binary forecast response: {e}")
            # Fallback: extract probability from text
            fallback_response = response if 'response' in locals() else "No response available"
            full_error_reasoning = f"Error parsing response. Raw response: {fallback_response}"
            logger.info(f"Full error reasoning: {full_error_reasoning}")
            main_logger.info(f"Full error reasoning: {full_error_reasoning}")
            return {
                "prediction": 0.5,
                "reasoning": full_error_reasoning
            }

    async def _run_individual_multiple_choice_forecast(self, llm: GeneralLlm, question: MultipleChoiceQuestion, research: str) -> dict:
        """
        Run individual multiple choice forecast for a single LLM.
        """
        options = ", ".join(question.options)
        prompt = clean_indents(f"""
            You are forecasting the following multiple choice question.

            Question: {question.question_text}
            Background: {question.background_info}
            Resolution Criteria: {question.resolution_criteria}

            Options: {options}

            Research Information:
            {research}

            Provide your forecast as probabilities for each option that sum to 1.0.
            Also provide your reasoning.

            Respond in JSON format:
            {{
                "predictions": {{
                    "<option1>": <probability>,
                    "<option2>": <probability>,
                    ...
                }},
                "reasoning": "<your detailed reasoning>"
            }}
        """)

        try:
            response = await llm.invoke(prompt)
            # Try to parse as JSON, handling markdown code blocks
            import json
            # Remove markdown code block formatting if present
            if response.strip().startswith('```json'):
                response = response.strip()[7:]  # Remove ```json
            if response.strip().endswith('```'):
                response = response.strip()[:-3]  # Remove ```
            result = json.loads(response.strip())
            predictions = result.get("predictions", {})
            # Normalize predictions
            total = sum(predictions.values())
            if total > 0:
                predictions = {k: v/total for k, v in predictions.items()}
            else:
                # Equal distribution if no valid predictions
                predictions = {opt: 1.0/len(question.options) for opt in question.options}
            return {
                "predictions": predictions,
                "reasoning": result.get("reasoning", "No reasoning provided")
            }
        except Exception as e:
            logger.warning(f"Error parsing multiple choice forecast response: {e}")
            main_logger.warning(f"Error parsing multiple choice forecast response: {e}")
            # Fallback: equal distribution
            fallback_predictions = {opt: 1.0/len(question.options) for opt in question.options}
            fallback_response = response if 'response' in locals() else "No response available"
            full_error_reasoning = f"Error parsing response. Using equal distribution. Raw response: {fallback_response}"
            logger.info(f"Full error reasoning: {full_error_reasoning}")
            main_logger.info(f"Full error reasoning: {full_error_reasoning}")
            return {
                "predictions": fallback_predictions,
                "reasoning": full_error_reasoning
            }

    async def _run_individual_numeric_forecast(self, llm: GeneralLlm, question: NumericQuestion, research: str) -> dict:
        """
        Run individual numeric forecast for a single LLM.
        """
        prompt = clean_indents(f"""
            You are forecasting the following numeric question.

            Question: {question.question_text}
            Background: {question.background_info}
            Resolution Criteria: {question.resolution_criteria}

            Range: {question.lower_bound} to {question.upper_bound}

            Research Information:
            {research}

            Provide your forecast as percentiles of the probability distribution.
            Use these percentiles: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
            Each value should be between {question.lower_bound} and {question.upper_bound}.

            Respond in JSON format:
            {{
                "distribution": {{
                    "0.1": <value>,
                    "0.2": <value>,
                    "0.3": <value>,
                    "0.4": <value>,
                    "0.5": <value>,
                    "0.6": <value>,
                    "0.7": <value>,
                    "0.8": <value>,
                    "0.9": <value>
                }},
                "reasoning": "<your detailed reasoning>"
            }}
        """)

        try:
            response = await llm.invoke(prompt)
            # Try to parse as JSON, handling markdown code blocks
            import json
            # Remove markdown code block formatting if present
            if response.strip().startswith('```json'):
                response = response.strip()[7:]  # Remove ```json
            if response.strip().endswith('```'):
                response = response.strip()[:-3]  # Remove ```
            result = json.loads(response.strip())
            distribution = result.get("distribution", {})
            # Convert to proper format
            percentile_list = []
            for p in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
                value = float(distribution.get(str(p), question.lower_bound + (question.upper_bound - question.lower_bound) * 0.5))
                # Clamp to bounds
                value = max(question.lower_bound, min(question.upper_bound, value))
                percentile_list.append(Percentile(percentile=p, value=value))

            return {
                "distribution": NumericDistribution.from_question(percentile_list, question),
                "reasoning": result.get("reasoning", "No reasoning provided")
            }
        except Exception as e:
            logger.warning(f"Error parsing numeric forecast response: {e}")
            main_logger.warning(f"Error parsing numeric forecast response: {e}")
            # Fallback: uniform distribution
            fallback_percentiles = []
            for p in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
                value = question.lower_bound + (question.upper_bound - question.lower_bound) * p
                fallback_percentiles.append(Percentile(percentile=p, value=value))

            fallback_response = response if 'response' in locals() else "No response available"
            full_error_reasoning = f"Error parsing response. Using uniform distribution. Raw response: {fallback_response}"
            logger.info(f"Full error reasoning: {full_error_reasoning}")
            main_logger.info(f"Full error reasoning: {full_error_reasoning}")
            return {
                "distribution": NumericDistribution.from_question(fallback_percentiles, question),
                "reasoning": full_error_reasoning
            }


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Add file handler for markdown output with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'forecastoutput_{timestamp}.md'
    file_handler = logging.FileHandler(filename, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    markdown_formatter = logging.Formatter('## %(asctime)s\n%(name)s - %(levelname)s\n%(message)s\n\n---\n')
    file_handler.setFormatter(markdown_formatter)
    logger.addHandler(file_handler)
    print(f"Logging to {filename}")

    # Set LiteLLM environment variables to ensure proper API key handling
    # This ensures LiteLLM can find the keys even when using OpenRouter models
    openrouter_key = os.getenv('OPENROUTER_API_KEY', '')
    if openrouter_key and openrouter_key != '' and openrouter_key != 'missing_api_key':
        os.environ['LITELLM_OPENROUTER_API_KEY'] = openrouter_key
        os.environ['OPENROUTER_API_KEY'] = openrouter_key
        # Also set OPENAI_API_KEY to OpenRouter key to handle any fallback to OpenAI endpoints
        os.environ['OPENAI_API_KEY'] = openrouter_key
        os.environ['LITELLM_OPENAI_API_KEY'] = openrouter_key
        logger.info("API keys have been properly configured for LiteLLM")
    else:
        logger.error("OPENROUTER_API_KEY is not properly set!")
        logger.info(f"Current OPENROUTER_API_KEY value: {'SET' if openrouter_key else 'NOT SET'}")
        if not openrouter_key:
            logger.info("Please check that OPENROUTER_API_KEY is set in your environment variables")
        elif openrouter_key == 'missing_api_key':
            logger.info("OPENROUTER_API_KEY was set to placeholder 'missing_api_key', please update it")
    
    logger.info(f"LITELLM_OPENROUTER_API_KEY is set: {'SET' if os.getenv('LITELLM_OPENROUTER_API_KEY') else 'NOT SET'}")
    logger.info(f"LITELLM_OPENAI_API_KEY is set: {'SET' if os.getenv('LITELLM_OPENAI_API_KEY') else 'NOT SET'}")
    logger.info(f"OPENROUTER_API_KEY is set: {'SET' if os.getenv('OPENROUTER_API_KEY') else 'NOT SET'}")
    logger.info(f"OPENAI_API_KEY is set: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")

    # Debug env
    print(f"Loaded METACULUS_TOKEN: {'*' * 10 if os.getenv('METACULUS_TOKEN') else 'Not loaded'}")
    print(f"Loaded OPENROUTER_API_KEY: {'*' * 10 if os.getenv('OPENROUTER_API_KEY') else 'Not loaded'}")
    print(f"Loaded OPENAI_API_KEY: {'*' * 10 if os.getenv('OPENAI_API_KEY') else 'Not loaded'}")
    print(f"Loaded LITELLM_OPENROUTER_API_KEY: {'*' * 10 if os.getenv('LITELLM_OPENROUTER_API_KEY') else 'Not loaded'}")
    print(f"Loaded LITELLM_OPENAI_API_KEY: {'*' * 10 if os.getenv('LITELLM_OPENAI_API_KEY') else 'Not loaded'}")
    print(f"Loaded PERPLEXITY_API_KEY: {'*' * 10 if os.getenv('PERPLEXITY_API_KEY') else 'Not loaded'}")
    print(f"Loaded EXA_API_KEY: {'*' * 10 if os.getenv('EXA_API_KEY') else 'Not loaded'}")
    print(f"Loaded ANTHROPIC_API_KEY: {'*' * 10 if os.getenv('ANTHROPIC_API_KEY') else 'Not loaded'}")
    print(f"Loaded ASKNEWS_CLIENT_ID: {'*' * 10 if os.getenv('ASKNEWS_CLIENT_ID') else 'Not loaded'}")
    print(f"Loaded ASKNEWS_SECRET: {'*' * 10 if os.getenv('ASKNEWS_SECRET') else 'Not loaded'}")

    # Log all environment variables (without revealing their values)
    logger.info("Environment variables check:")
    env_vars = [
        'METACULUS_TOKEN',
        'OPENROUTER_API_KEY',
        'OPENAI_API_KEY',
        'LITELLM_OPENROUTER_API_KEY',
        'LITELLM_OPENAI_API_KEY',
        'PERPLEXITY_API_KEY',
        'EXA_API_KEY',
        'ANTHROPIC_API_KEY',
        'ASKNEWS_CLIENT_ID',
        'ASKNEWS_SECRET',
        'CHUTES_API_TOKEN'
    ]
    for var in env_vars:
        logger.info(f"{var}: {'SET' if os.getenv(var) else 'NOT SET'}")

    # Suppress LiteLLM logging
    litellm_logger = logging.getLogger("LiteLLM")
    litellm_logger.setLevel(logging.WARNING)
    litellm_logger.propagate = False

    # Check for required API keys
    required_keys = ['METACULUS_TOKEN', 'OPENROUTER_API_KEY']
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        logger.error(f"Missing required environment variables: {missing_keys}")
        exit(1)

    # Warn about missing optional API keys
    optional_keys = ['PERPLEXITY_API_KEY', 'EXA_API_KEY', 'ANTHROPIC_API_KEY', 'ASKNEWS_CLIENT_ID', 'ASKNEWS_SECRET']
    missing_optional_keys = [key for key in optional_keys if not os.getenv(key)]
    if missing_optional_keys:
        logger.warning(f"Missing optional environment variables: {missing_optional_keys}. Some models may not work.")
        
    # Log GitHub Actions specific environment
    if os.getenv('GITHUB_ACTIONS') == 'true':
        logger.info("Running in GitHub Actions environment")
        logger.info(f"GitHub repository: {os.getenv('GITHUB_REPOSITORY', 'Unknown')}")
        logger.info(f"GitHub workflow: {os.getenv('GITHUB_WORKFLOW', 'Unknown')}")
        logger.info(f"GitHub run ID: {os.getenv('GITHUB_RUN_ID', 'Unknown')}")

    parser = argparse.ArgumentParser(
        description="Run the Q1TemplateBot forecasting system"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["tournament", "metaculus_cup", "test_questions"],
        default="tournament",
        help="Specify the run mode (default: tournament)",
    )
    args = parser.parse_args()
    run_mode: Literal["tournament", "metaculus_cup", "test_questions"] = args.mode
    assert run_mode in [
        "tournament",
        "metaculus_cup",
        "test_questions",
    ], "Invalid run mode"

    publish_reports = run_mode != "test_questions"

    # Initialize the bot with mixed model configuration using multiple API keys
    # Using the correct API key configuration:
    # - OpenRouter API key (from Metaculus with free credits) for OpenAI models
    # - Personal API key for DeepSeek and Kimi models
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
    personal_api_key = "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"  # Personal key for DeepSeek and Kimi models ONLY - FREE MODELS ONLY
    
    # Validate that we have the required OpenRouter API key
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY is not set. Please check your environment variables.")
        exit(1)
    
    # Also set LiteLLM environment variables to ensure proper handling
    os.environ['LITELLM_OPENROUTER_API_KEY'] = openrouter_api_key
    
    # Don't set OPENAI_API_KEY to OpenRouter key - let OpenRouter handle it properly
    # This prevents OpenAI client from trying to authenticate directly with OpenAI
    if os.getenv('OPENAI_API_KEY') == '1234567890' or not os.getenv('OPENAI_API_KEY'):
        # Only set if we don't have a real OpenAI key
        del os.environ['OPENAI_API_KEY']  # Remove to force OpenRouter routing
    
    # Set the API key for proper routing
    os.environ['OPENROUTER_API_KEY'] = openrouter_api_key
    
    template_bot = FallTemplateBot2025(
        research_reports_per_question=1,
        predictions_per_research_report=1,  # Changed from 6 to 1 since we have 4 forecasters
        use_research_summary_to_forecast=False,
        publish_reports_to_metaculus=publish_reports,
        folder_to_save_reports_to=None,
        skip_previously_forecasted_questions=False,  # Changed to False to allow forecasting on all questions
        llms={
            "default": GeneralLlm(
                model="openrouter/openai/gpt-4o",
                api_key=openrouter_api_key,
                temperature=0.5,
                timeout=60,
                allowed_tries=2,
            ),
            "synthesizer": GeneralLlm(
                model="openrouter/openai/gpt-4o",
                api_key=openrouter_api_key,
                temperature=0.3,
                timeout=60,
                allowed_tries=2,
            ),
            # GPT models using Metaculus OpenRouter key (with free credits)
            "forecaster1": GeneralLlm(
                model="openrouter/openai/gpt-4o",
                api_key=openrouter_api_key,
                temperature=0.5,
                timeout=60,
                allowed_tries=2,
            ),
            # DeepSeek model using redundant API (Chutes first, then OpenRouter)
            "forecaster2": create_redundant_llm(
                model="openrouter/deepseek/deepseek-chat-v3-0324",
                chutes_api_key=os.getenv('CHUTES_API_TOKEN'),
                openrouter_api_key=personal_api_key,
                temperature=0.5,
                timeout=60,
                allowed_tries=2,
            ),
            # Kimi model using redundant API (OpenRouter only since Kimi not available on Chutes)
            "forecaster3": create_redundant_llm(
                model="openrouter/moonshotai/kimi-k2-0905",
                chutes_api_key=os.getenv('CHUTES_API_TOKEN'),
                openrouter_api_key=personal_api_key,
                temperature=0.5,
                timeout=60,
                allowed_tries=2,
            ),
            # GPT model using Metaculus OpenRouter key
            "forecaster4": GeneralLlm(
                model="openrouter/openai/gpt-4o",
                api_key=openrouter_api_key,
                temperature=0.5,
                timeout=60,
                allowed_tries=2,
            ),
            "parser": GeneralLlm(
                model="openrouter/openai/gpt-4o-mini",
                api_key=openrouter_api_key,
                temperature=0.3,
                timeout=60,
                allowed_tries=2,
            ),
            "researcher": GeneralLlm(
                model="openrouter/openai/gpt-4o-mini",
                api_key=openrouter_api_key,
                temperature=0.5,
                timeout=60,
                allowed_tries=2,
            ),
            "summarizer": GeneralLlm(
                model="openrouter/openai/gpt-4o-mini",
                api_key=openrouter_api_key,
                temperature=0.5,
                timeout=60,
                allowed_tries=2,
            ),
        },
    )

    # Send startup notification
    startup_subject = f"Metaculus Bot Starting - {run_mode} mode"
    startup_body = f"""
Metaculus Forecasting Bot is starting up.

Mode: {run_mode}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Host: {os.getenv('GITHUB_ACTIONS', 'Local')}
"""
    send_notification_email(startup_subject, startup_body)

    try:
        if run_mode == "tournament":
            logger.info("Starting tournament mode forecast")
            logger.info(f"Checking AI Competition Tournament ID: {MetaculusApi.CURRENT_AI_COMPETITION_ID}")
            logger.info(f"Checking MiniBench Tournament ID: {MetaculusApi.CURRENT_MINIBENCH_ID}")
            logger.info("Checking Fall AIB 2025 Tournament by slug: fall-aib-2025")

            # Fallback function to manually filter by tournament_slugs when API filtering fails
            async def get_tournament_questions_fallback(tournament_slug: str, statuses: list[str] = None):
                """Fallback function to get tournament questions when API filtering fails"""
                logger.info(f"Using fallback method to find {tournament_slug} questions...")

                # Handle API pagination by checking multiple time periods
                time_periods = [
                    timedelta(hours=3),   # Recent questions
                    timedelta(days=1),    # Last day
                    timedelta(days=7),    # Last week
                    timedelta(days=30),   # Last month
                ]

                all_questions = []
                seen_ids = set()

                for period in time_periods:
                    logger.info(f"Checking questions from last {period}")
                    time_filter = ApiFilter(open_time_gt=datetime.now() - period)
                    period_questions = await MetaculusApi.get_questions_matching_filter(time_filter)

                    # Avoid duplicates
                    for question in period_questions:
                        question_id = getattr(question, 'id', None)
                        if question_id and question_id not in seen_ids:
                            seen_ids.add(question_id)
                            all_questions.append(question)

                    # Stop if we're getting the same results (pagination limit reached)
                    if len(period_questions) < MetaculusApi.MAX_QUESTIONS_FROM_QUESTION_API_PER_REQUEST:
                        break

                logger.info(f"Total unique questions found across all time periods: {len(all_questions)}")

                # Filter by tournament slug
                filtered_questions = []
                for question in all_questions:
                    # Check if question has the target tournament slug
                    if hasattr(question, 'tournament_slugs') and tournament_slug in question.tournament_slugs:
                        # Filter by status if specified
                        if statuses:
                            if hasattr(question, 'state') and question.state.name in statuses:
                                filtered_questions.append(question)
                        else:
                            filtered_questions.append(question)

                logger.info(f"Fallback method found {len(filtered_questions)} {tournament_slug} questions")
                return filtered_questions

            # Use get_questions_matching_filter instead of forecast_on_tournament due to API issues
            from forecasting_tools.helpers.metaculus_api import ApiFilter
            
            # Get AI Competition questions
            ai_comp_filter = ApiFilter(
                allowed_statuses=["open"],
                allowed_tournaments=[MetaculusApi.CURRENT_AI_COMPETITION_ID]
            )
            ai_comp_questions = asyncio.run(
                MetaculusApi.get_questions_matching_filter(ai_comp_filter)
            )
            
            # For debugging, also get all AI Competition questions to see what's available
            all_ai_comp_filter = ApiFilter(
                allowed_tournaments=[MetaculusApi.CURRENT_AI_COMPETITION_ID]
            )
            all_ai_comp_questions = asyncio.run(
                MetaculusApi.get_questions_matching_filter(all_ai_comp_filter)
            )
            logger.info(f"Found {len(all_ai_comp_questions)} total questions for AI Competition (including closed).")
            
            logger.info(f"Found {len(ai_comp_questions)} OPEN questions for AI Competition.")
            for q in ai_comp_questions:
                logger.info(f"  - {q.page_url}: {q.question_text} (Status: {q.status})")
            seasonal_tournament_reports = asyncio.run(
                template_bot.forecast_questions(ai_comp_questions, return_exceptions=True)
            )
            
            # Get MiniBench questions
            minibench_filter = ApiFilter(
                allowed_statuses=["open"],
                allowed_tournaments=[MetaculusApi.CURRENT_MINIBENCH_ID]
            )
            minibench_questions = asyncio.run(
                MetaculusApi.get_questions_matching_filter(minibench_filter)
            )
            
            # For debugging, also get all MiniBench questions to see what's available
            all_minibench_filter = ApiFilter(
                allowed_tournaments=[MetaculusApi.CURRENT_MINIBENCH_ID]
            )
            all_minibench_questions = asyncio.run(
                MetaculusApi.get_questions_matching_filter(all_minibench_filter)
            )
            logger.info(f"Found {len(all_minibench_questions)} total questions for MiniBench (including closed).")
            
            logger.info(f"Found {len(minibench_questions)} OPEN questions for MiniBench.")
            for q in minibench_questions:
                logger.info(f"  - {q.page_url}: {q.question_text} (Status: {q.status})")
            minibench_reports = asyncio.run(
                template_bot.forecast_questions(minibench_questions, return_exceptions=True)
            )
            
            # Get Fall AIB 2025 questions
            logger.info("Setting skip_previously_forecasted_questions = False for tournament mode")
            template_bot.skip_previously_forecasted_questions = False

            # Try API filtering first, then fallback to manual filtering
            fall_aib_filter = ApiFilter(
                allowed_statuses=["open"],
                allowed_tournaments=["fall-aib-2025"]
            )
            fall_aib_questions = asyncio.run(
                MetaculusApi.get_questions_matching_filter(fall_aib_filter)
            )

            # If API filtering returns no questions, try fallback method
            if len(fall_aib_questions) == 0:
                logger.warning("API filtering found no Fall AIB 2025 questions, trying fallback method...")
                fall_aib_questions = asyncio.run(
                    get_tournament_questions_fallback("fall-aib-2025", ["open"])
                )

            # Check for recently closed questions that might have been missed
            if len(fall_aib_questions) == 0:
                logger.warning("Still no Fall AIB 2025 questions found, checking for recently closed questions...")
                recently_closed = asyncio.run(
                    get_tournament_questions_fallback("fall-aib-2025", ["CLOSED"])
                )

                # Filter for questions closed in the last 1.5 hours (within realistic forecasting window)
                now = datetime.now()
                recent_missed = []
                for q in recently_closed:
                    if hasattr(q, 'close_time') and q.close_time:
                        hours_since_close = (now - q.close_time.replace(tzinfo=None)).total_seconds() / 3600
                        if hours_since_close <= 1.5:  # Only check last 1.5 hours for recently closed questions
                            recent_missed.append(q)

                if recent_missed:
                    logger.error(f"FOUND {len(recent_missed)} RECENTLY CLOSED FALL AIB 2025 QUESTIONS THAT MAY HAVE BEEN MISSED!")
                    for q in recent_missed:
                        logger.error(f"  MISSED: {q.page_url} (closed {q.close_time})")

                    # Send alert email about missed questions
                    missed_subject = f"ALERT: Missed {len(recent_missed)} Fall AIB 2025 Tournament Questions!"
                    missed_body = f"""
The bot found {len(recent_missed)} recently closed Fall AIB 2025 questions that were likely missed due to GitHub Actions scheduling gaps or API filtering issues.

Missed questions:
"""
                    for q in recent_missed:
                        missed_body += f"- {q.page_url} (Closed: {q.close_time})\n"

                    missed_body += f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    missed_body += "Please investigate the GitHub Actions schedule and API filtering."

                    send_notification_email(missed_subject, missed_body)
            
            # For debugging, also get questions with other statuses to see what's available
            all_fall_aib_filter = ApiFilter(
                allowed_tournaments=["fall-aib-2025"]
            )
            all_fall_aib_questions = asyncio.run(
                MetaculusApi.get_questions_matching_filter(all_fall_aib_filter)
            )
            logger.info(f"Found {len(all_fall_aib_questions)} total questions for Fall AIB 2025 (including closed).")
            
            logger.info(f"Found {len(fall_aib_questions)} OPEN questions for Fall AIB 2025.")
            for q in fall_aib_questions:
                logger.info(f"  - {q.page_url}: {q.question_text} (Status: {q.status})")
            fall_aib_reports = asyncio.run(
                template_bot.forecast_questions(fall_aib_questions, return_exceptions=True)
            )
            
            forecast_reports = seasonal_tournament_reports + minibench_reports + fall_aib_reports
        elif run_mode == "metaculus_cup":
            # The Metaculus cup is a good way to test the bot's performance on regularly open questions. 
            # The permanent ID for the Metaculus Cup is now 32828
            logger.info("Starting Metaculus cup mode forecast")
            logger.info("Checking Metaculus Cup Tournament ID: 32828")
            template_bot.skip_previously_forecasted_questions = False
            forecast_reports = asyncio.run(
                template_bot.forecast_on_tournament(
                    32828, return_exceptions=True  # Use the correct ID instead of the slug
                )
            )
        elif run_mode == "test_questions":
            # Example questions are a good way to test the bot's performance on a single question
            # Temporarily use dummy numeric question for testing multi-model without API token
            logger.info("Starting test questions mode")
            from forecasting_tools import NumericQuestion
            dummy_question = NumericQuestion(
                question_text="What will be the age of the oldest human as of 2100?",
                background_info="The current record is 122 years. Advances in medicine may extend it.",
                resolution_criteria="Official Guinness record.",
                fine_print="",
                unit_of_measure="years",
                lower_bound=100,
                upper_bound=200,
                open_lower_bound=False,
                open_upper_bound=False,
                page_url="dummy://test.com",
                id=12345,
            )
            template_bot.skip_previously_forecasted_questions = False
            questions = [dummy_question]
            forecast_reports = asyncio.run(
                template_bot.forecast_questions(questions, return_exceptions=True)
            )
        else:
            logger.warning(f"Unknown run mode: {run_mode}")
            exit(1)

    # Log final summary
        if run_mode == "tournament":
            logger.info(f"All tournament processing completed. Found questions: AI Comp: {len(ai_comp_questions)}, MiniBench: {len(minibench_questions)}, Fall AIB: {len(fall_aib_questions)}")
        else:
            logger.info(f"All processing completed for {run_mode} mode")

        logger.info("Forecasting completed successfully")
        template_bot.log_report_summary(forecast_reports)
        
        # Send completion notification
        completion_subject = f"Metaculus Bot Completed - {run_mode} mode"
        completion_body = f"""
Metaculus Forecasting Bot has completed its run.

Mode: {run_mode}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Host: {os.getenv('GITHUB_ACTIONS', 'Local')}
Output file: {filename}

Questions processed: {len([r for r in forecast_reports if r is not None and not isinstance(r, Exception)])}
Questions with errors: {len([r for r in forecast_reports if isinstance(r, Exception)])}
"""
        send_notification_email(completion_subject, completion_body)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        # Don't raise in GitHub Actions to prevent workflow failures
        if os.getenv('GITHUB_ACTIONS') != 'true':
            raise
        else:
            logger.info("Exiting gracefully in GitHub Actions environment")
            # Exit gracefully in GitHub Actions
            exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error during bot execution: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        # Don't raise in GitHub Actions to prevent workflow failures
        if os.getenv('GITHUB_ACTIONS') != 'true':
            raise
        else:
            logger.info("Continuing despite error in GitHub Actions environment")