from dotenv import load_dotenv
load_dotenv()
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

logger = logging.getLogger(__name__)


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
        forecaster_defaults = {
            "forecaster1": {"model": "openrouter/moonshotai/kimi-k2-0905", **defaults},
            "forecaster2": {"model": "openrouter/deepseek/deepseek-r1", **defaults},
            "forecaster3": {"model": "openrouter/qwen/qwen3-max", **defaults},
            "forecaster4": {"model": "openrouter/mistralai/mistral-large", **defaults},
            "forecaster5": {"model": "openrouter/bytedance/seed-oss-36b-instruct", **defaults},
            "forecaster6": {"model": "openrouter/microsoft/wizardlm-2-8x22b", **defaults},
        }
        return {**defaults, **forecaster_defaults}

    # Define model names for logging
    forecaster_models = {
        "forecaster1": "openrouter/moonshotai/kimi-k2-0905",
        "forecaster2": "openrouter/deepseek/deepseek-r1",
        "forecaster3": "openrouter/qwen/qwen3-max",
        "forecaster4": "openrouter/mistralai/mistral-large",
        "forecaster5": "openrouter/bytedance/seed-oss-36b-instruct",
        "forecaster6": "openrouter/microsoft/wizardlm-2-8x22b",
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

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def run_research(self, question: MetaculusQuestion) -> str:
        async with self._concurrency_limiter:
            research = ""
            researcher = self.get_llm("researcher")

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
            logger.info(f"Found Research for URL {question.page_url}:\n{research}")
            return research

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def _run_forecast_on_binary(
        self, question: BinaryQuestion, research: str
    ) -> ReasonedPrediction[float]:
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
        
        # Define forecaster models
        forecaster_keys = ["forecaster1", "forecaster2", "forecaster3", "forecaster4", "forecaster5", "forecaster6"]
        individual_reasonings = []
        individual_predictions = []

        # Generate individual forecasts with rate limiting
        for key in forecaster_keys:
            async with self._llm_rate_limiter:  # Rate limit LLM calls
                llm = self.get_llm(key, "llm")
                reasoning = await llm.invoke(prompt)
                logger.info(f"Reasoning from {key} for URL {question.page_url}: {reasoning}")
                binary_prediction: BinaryPrediction = await structure_output(
                    reasoning, BinaryPrediction, model=self.get_llm("parser", "llm")
                )
                decimal_pred = max(0.01, min(0.99, binary_prediction.prediction_in_decimal))
                individual_reasonings.append(reasoning)
                individual_predictions.append(decimal_pred)
                model_name = self.forecaster_models.get(key, 'unknown')
                logger.info(f"Forecast from {key} ({model_name}) for URL {question.page_url}: {decimal_pred}")

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

            synth_llm = self.get_llm("synthesizer", "llm")
            synth_model_name = self.forecaster_models.get('synthesizer', 'openai/gpt-4o')
            synth_reasoning = await synth_llm.invoke(synth_prompt)
            logger.info(f"Synthesized reasoning (using {synth_model_name}) for URL {question.page_url}: {synth_reasoning}")
            parser_llm = self.get_llm("parser", "llm")
            parser_model_name = self.forecaster_models.get('parser', 'openai/gpt-4o-mini')
            final_binary_prediction: BinaryPrediction = await structure_output(
                synth_reasoning, BinaryPrediction, model=parser_llm
            )
            final_decimal_pred = max(0.01, min(0.99, final_binary_prediction.prediction_in_decimal))
            logger.info(f"Synthesized final prediction (parsed with {parser_model_name}) for URL {question.page_url}: {final_decimal_pred}")

        # Combined reasoning with model names
        forecaster_keys = ["forecaster1", "forecaster2", "forecaster3", "forecaster4", "forecaster5", "forecaster6"]
        combined_reasoning_parts = []
        for i, (key, reasoning) in enumerate(zip(forecaster_keys, individual_reasonings)):
            model_name = self.forecaster_models.get(key, 'unknown')
            combined_reasoning_parts.append(f"Forecaster {i+1} ({key}: {model_name}): {reasoning}")
        combined_reasoning_parts.append(f"Synthesis (using {self.forecaster_models.get('synthesizer', 'unknown')}): {synth_reasoning}")
        combined_reasoning = "\n\n".join(combined_reasoning_parts)

        return ReasonedPrediction(prediction_value=final_decimal_pred, reasoning=combined_reasoning)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def _run_forecast_on_multiple_choice(
        self, question: MultipleChoiceQuestion, research: str
    ) -> ReasonedPrediction[PredictedOptionList]:
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
        
        # Define forecaster models
        forecaster_keys = ["forecaster1", "forecaster2", "forecaster3", "forecaster4", "forecaster5", "forecaster6"]
        individual_reasonings = []
        individual_predictions = []

        # Generate individual forecasts
        for key in forecaster_keys:
            llm = self.get_llm(key, "llm")
            reasoning = await llm.invoke(prompt)
            logger.info(f"Reasoning from {key} for URL {question.page_url}: {reasoning}")
            predicted_option_list: PredictedOptionList = await structure_output(
                text_to_structure=reasoning,
                output_type=PredictedOptionList,
                model=self.get_llm("parser", "llm"),
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
            Option_N: Probability_N
            """
        )

        synth_llm = self.get_llm("synthesizer", "llm")
        synth_model_name = self.forecaster_models.get('synthesizer', 'openai/gpt-4o')
        synth_reasoning = await synth_llm.invoke(synth_prompt)
        logger.info(f"Synthesized reasoning (using {synth_model_name}) for URL {question.page_url}: {synth_reasoning}")
        parser_llm = self.get_llm("parser", "llm")
        parser_model_name = self.forecaster_models.get('parser', 'openai/gpt-4o-mini')
        final_predicted_option_list: PredictedOptionList = await structure_output(
            text_to_structure=synth_reasoning,
            output_type=PredictedOptionList,
            model=parser_llm,
            additional_instructions=parsing_instructions,
        )
        logger.info(f"Synthesized final prediction (parsed with {parser_model_name}) for URL {question.page_url}: {final_predicted_option_list}")

        # Combined reasoning with model names
        forecaster_keys = ["forecaster1", "forecaster2", "forecaster3", "forecaster4", "forecaster5", "forecaster6"]
        combined_reasoning_parts = []
        for i, (key, reasoning) in enumerate(zip(forecaster_keys, individual_reasonings)):
            model_name = self.forecaster_models.get(key, 'unknown')
            combined_reasoning_parts.append(f"Forecaster {i+1} ({key}: {model_name}): {reasoning}")
        combined_reasoning_parts.append(f"Synthesis (using {self.forecaster_models.get('synthesizer', 'unknown')}): {synth_reasoning}")
        combined_reasoning = "\n\n".join(combined_reasoning_parts)

        return ReasonedPrediction(
            prediction_value=final_predicted_option_list, reasoning=combined_reasoning
        )

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def _run_forecast_on_numeric(
        self, question: NumericQuestion, research: str
    ) -> ReasonedPrediction[NumericDistribution]:
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
        # Define forecaster models
        forecaster_keys = ["forecaster1", "forecaster2", "forecaster3", "forecaster4", "forecaster5", "forecaster6"]
        individual_reasonings = []
        individual_predictions = []

        # Generate individual forecasts
        for key in forecaster_keys:
            llm = self.get_llm(key, "llm")
            reasoning = await llm.invoke(prompt)
            logger.info(f"Reasoning from {key} for URL {question.page_url}: {reasoning}")
            percentile_list: list[Percentile] = await structure_output(
                reasoning, list[Percentile], model=self.get_llm("parser", "llm")
            )
            prediction = NumericDistribution.from_question(percentile_list, question)
            individual_reasonings.append(reasoning)
            individual_predictions.append(prediction)
            model_name = self.forecaster_models.get(key, 'unknown')
            logger.info(f"Forecast from {key} ({model_name}) for URL {question.page_url}: {prediction.declared_percentiles}")

        # Synthesize final prediction
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

        synth_llm = self.get_llm("synthesizer", "llm")
        synth_model_name = self.forecaster_models.get('synthesizer', 'openai/gpt-4o')
        synth_reasoning = await synth_llm.invoke(synth_prompt)
        logger.info(f"Synthesized reasoning (using {synth_model_name}) for URL {question.page_url}: {synth_reasoning}")
        parser_llm = self.get_llm("parser", "llm")
        parser_model_name = self.forecaster_models.get('parser', 'openai/gpt-4o-mini')
        final_percentile_list: list[Percentile] = await structure_output(
            synth_reasoning, list[Percentile], model=parser_llm
        )
        final_prediction = NumericDistribution.from_question(final_percentile_list, question)
        logger.info(f"Synthesized final prediction (parsed with {parser_model_name}) for URL {question.page_url}: {final_prediction.declared_percentiles}")

        # Combined reasoning with model names
        forecaster_keys = ["forecaster1", "forecaster2", "forecaster3", "forecaster4", "forecaster5", "forecaster6"]
        combined_reasoning_parts = []
        for i, (key, reasoning) in enumerate(zip(forecaster_keys, individual_reasonings)):
            model_name = self.forecaster_models.get(key, 'unknown')
            combined_reasoning_parts.append(f"Forecaster {i+1} ({key}: {model_name}): {reasoning}")
        combined_reasoning_parts.append(f"Synthesis (using {self.forecaster_models.get('synthesizer', 'unknown')}): {synth_reasoning}")
        combined_reasoning = "\n\n".join(combined_reasoning_parts)

        return ReasonedPrediction(prediction_value=final_prediction, reasoning=combined_reasoning)

    def _create_upper_and_lower_bound_messages(
        self, question: NumericQuestion
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


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Add file handler for markdown output with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'forecastoutput_{timestamp}.md'
    file_handler = logging.FileHandler(filename, mode='w')
    file_handler.setLevel(logging.INFO)
    markdown_formatter = logging.Formatter('## %(asctime)s\n%(name)s - %(levelname)s\n%(message)s\n\n---\n')
    file_handler.setFormatter(markdown_formatter)
    logger.addHandler(file_handler)
    print(f"Logging to {filename}")

    # Load .env
    from dotenv import load_dotenv
    load_dotenv()

    # Debug env
    import os
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
        'ASKNEWS_SECRET'
    ]
    for var in env_vars:
        logger.info(f"{var}: {'SET' if os.getenv(var) else 'NOT SET'}")

    # Suppress LiteLLM logging
    litellm_logger = logging.getLogger("LiteLLM")
    litellm_logger.setLevel(logging.WARNING)
    litellm_logger.propagate = False

    # Check for required API keys
    required_keys = ['METACULUS_TOKEN', 'OPENAI_API_KEY', 'OPENROUTER_API_KEY']
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

    # Initialize the bot with reduced DeepSeek models
    template_bot = FallTemplateBot2025(
        research_reports_per_question=1,
        predictions_per_research_report=1,  # Changed from 6 to 1 since we have 6 forecasters
        use_research_summary_to_forecast=False,
        publish_reports_to_metaculus=True,
        folder_to_save_reports_to=None,
        skip_previously_forecasted_questions=True,
        llms={
            "default": GeneralLlm(
                model="openrouter/openai/gpt-4o",
                temperature=0.5,
                timeout=60,
                allowed_tries=2,
            ),
            "synthesizer": GeneralLlm(
                model="openrouter/openai/gpt-4o",
                temperature=0.3,
                timeout=60,
                allowed_tries=2,
            ),
            "forecaster1": "openrouter/moonshotai/kimi-k2-0905",
            "forecaster2": "openrouter/deepseek/deepseek-r1",  # Most advanced DeepSeek model
            "forecaster3": "openrouter/qwen/qwen3-max",
            "forecaster4": "openrouter/mistralai/mistral-large",
            "forecaster5": "openrouter/bytedance/seed-oss-36b-instruct",
            "forecaster6": "openrouter/microsoft/wizardlm-2-8x22b",
            "parser": "openrouter/openai/gpt-4o-mini",
            "researcher": "openrouter/openai/gpt-4o-mini",
            "summarizer": "openrouter/openai/gpt-4o-mini",
        },
    )

    if run_mode == "tournament":
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
        from forecasting_tools.helpers.metaculus_api import ApiFilter
        api_filter = ApiFilter(
            statuses=["open"],
            tournaments=["fall-aib-2025"]
        )
        fall_aib_questions = asyncio.run(
            MetaculusApi.get_questions_matching_filter(api_filter)
        )
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
    logger.info("Forecasting completed successfully")
    template_bot.log_report_summary(forecast_reports)

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
            # Exit gracefully in GitHub Actions
            exit(0)
