"""
Modular LLM API calling system with configurable fallback chains.
Provides unified API calling with automatic fallback to alternative models when primary models fail.
"""

import asyncio
import logging
import os
from typing import List, Optional, Dict, Any, Union, TypeVar, TYPE_CHECKING
from forecasting_tools.ai_models.general_llm import GeneralLlm

T = TypeVar('T')
logger = logging.getLogger(__name__)


class FallbackLLM:
    """
    A modular LLM wrapper that tries models in a configurable fallback chain.
    All models use the same API key (OpenRouter) for consistency and cost management.
    Compatible with GeneralLlm interface for drop-in replacement.
    """

    def __init__(
        self,
        model_chain: List[str],
        api_key: Optional[str] = None,
        temperature: float = 0.5,
        timeout: int = 60,
        allowed_tries: int = 2,
        **kwargs
    ):
        """
        Initialize the fallback LLM system.

        Args:
            model_chain: List of model names in priority order (highest priority first)
            api_key: OpenRouter API key (falls back to OPENROUTER_API_KEY env var)
            temperature: Temperature parameter for all models
            timeout: Timeout in seconds for all models
            allowed_tries: Number of allowed retries per model
            **kwargs: Additional parameters passed to all GeneralLlm instances
        """
        self.model_chain = model_chain
        self.api_key = api_key if api_key else os.getenv('OPENROUTER_API_KEY', '')
        self.temperature = temperature
        self.timeout = timeout
        self.allowed_tries = allowed_tries
        self.kwargs = kwargs

        # Validate that we have an API key
        if not self.api_key:
            logger.error("No OpenRouter API key provided. Set OPENROUTER_API_KEY environment variable.")
            raise ValueError("OpenRouter API key is required")

        # Validate that we have at least one model
        if not self.model_chain:
            raise ValueError("At least one model must be specified in the model chain")

        # Set properties to mimic GeneralLlm interface
        self.model = self.model_chain[0] if self.model_chain else "unknown"
        self.fallback_models = self.model_chain[1:] if len(self.model_chain) > 1 else []

        logger.info(f"Initialized FallbackLLM with chain: {self.model_chain}")
        logger.info(f"API key configured: {'YES' if self.api_key else 'NO'}")

    async def invoke(self, prompt: str) -> str:
        """
        Invoke the LLM with the given prompt, trying models in fallback order.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            The LLM response

        Raises:
            RuntimeError: If all models in the chain fail
        """
        # Log the complete prompt for debugging
        main_logger = logging.getLogger('__main__')
        main_logger.info("=== FALLBACK LLM COMPLETE PROMPT ===")
        main_logger.info(f"Model chain: {self.model_chain}")
        main_logger.info(f"Prompt length: {len(prompt)} characters")
        main_logger.info(f"Full prompt:\n{prompt}")
        main_logger.info("=== END PROMPT ===\n")

        last_error = None

        # Try each model in the chain
        for i, model_name in enumerate(self.model_chain):
            try:
                logger.info(f"Trying model {i+1}/{len(self.model_chain)}: {model_name}")

                # Create GeneralLlm instance for this model
                llm = GeneralLlm(
                    model=model_name,
                    api_key=self.api_key,
                    temperature=self.temperature,
                    timeout=self.timeout,
                    allowed_tries=self.allowed_tries,
                    **self.kwargs
                )

                # Attempt to invoke the model
                logger.info(f"Making API call to model: {model_name}")
                main_logger.info(f"=== MAKING API CALL TO {model_name} ===")
                main_logger.info(f"API Key: {'***' + self.api_key[-4:] if self.api_key else 'None'}")
                main_logger.info(f"Temperature: {self.temperature}")
                main_logger.info(f"Timeout: {self.timeout}")
                main_logger.info(f"Prompt length: {len(prompt)} characters")
                main_logger.info(f"Prompt preview:\n{prompt[:200]}{'...' if len(prompt) > 200 else ''}")
                main_logger.info("=== END API CALL DETAILS ===\n")

                response = await llm.invoke(prompt)

                # Success! Log and return
                logger.info(f"Model {model_name} succeeded")
                main_logger.info(f"=== SUCCESSFUL RESPONSE FROM {model_name} ===")
                main_logger.info(f"Response length: {len(response)} characters")
                main_logger.info(f"Response preview:\n{response[:300]}{'...' if len(response) > 300 else ''}")
                main_logger.info(f"Full response:\n{response}")
                main_logger.info("=== END RESPONSE ===\n")
                return response

            except Exception as e:
                error_msg = f"Model {model_name} failed: {str(e)}"
                logger.warning(error_msg)
                main_logger.info(f"=== MODEL {model_name} FAILED ===")
                main_logger.info(error_msg)
                main_logger.info("=== END ERROR ===\n")
                last_error = e
                continue

        # All models failed
        final_error_msg = f"All {len(self.model_chain)} models in fallback chain failed. Last error: {last_error}"
        logger.error(final_error_msg)
        main_logger.info("=== ALL MODELS IN FALLBACK CHAIN FAILED ===")
        main_logger.info(final_error_msg)
        main_logger.info("=== END ERROR ===\n")
        raise RuntimeError(final_error_msg)

    async def __call__(self, *args, **kwargs) -> str:
        """
        Make the FallbackLLM callable directly like GeneralLlm.
        This bypasses litellm's internal serialization.
        """
        # Extract prompt from args/kwargs
        if args:
            prompt = args[0]
        else:
            prompt = kwargs.get('messages', [{}])[-1].get('content', '') if kwargs.get('messages') else kwargs.get('prompt', '')

        return await self.invoke(prompt)

    def is_available(self) -> bool:
        """
        Check if the fallback system is available (has API key and models).
        """
        return bool(self.api_key and self.model_chain)

    def get_model_chain_info(self) -> Dict[str, Any]:
        """
        Get information about the current model chain configuration.
        """
        return {
            "primary_model": self.model_chain[0] if self.model_chain else None,
            "fallback_models": self.model_chain[1:] if len(self.model_chain) > 1 else [],
            "total_models": len(self.model_chain),
            "api_key_configured": bool(self.api_key),
            "temperature": self.temperature,
            "timeout": self.timeout,
            "allowed_tries": self.allowed_tries
        }

    async def invoke_and_return_verified_type(
        self,
        input: Any,
        normal_complex_or_pydantic_type: type[T],
        allowed_invoke_tries_for_failed_output: int = 2,
    ) -> T:
        """
        Invoke the LLM and return a verified type, with fallback through the model chain.
        Matches the interface expected by structure_output and other forecasting-tools components.
        """
        for i, model_name in enumerate(self.model_chain):
            try:
                llm = GeneralLlm(
                    model=model_name,
                    api_key=self.api_key,
                    temperature=self.temperature,
                    timeout=self.timeout,
                    allowed_tries=self.allowed_tries,
                    **self.kwargs
                )
                # Note: GeneralLlm.invoke_and_return_verified_type may not accept the allowed_invoke_tries_for_failed_output parameter
                # So we don't pass it to avoid interface mismatch
                response = await llm.invoke_and_return_verified_type(
                    input, normal_complex_or_pydantic_type
                )
                return response
            except Exception as e:
                logger.warning(f"Model {model_name} failed in invoke_and_return_verified_type: {e}")
                continue
        raise RuntimeError(f"All {len(self.model_chain)} models in fallback chain failed for invoke_and_return_verified_type")

    def get_schema_format_instructions_for_pydantic_type(self, pydantic_type: Any) -> str:
        """
        Return schema format instructions for compatibility with GeneralLlm interface.
        """
        # This is a simplified version - in practice, you'd want to generate proper schema instructions
        return "Respond with valid JSON that matches the expected schema."

    def startswith(self, prefix: str) -> bool:
        """
        Compatibility method for code that expects a string but gets a FallbackLLM.
        Delegates to the primary model name.
        """
        return self.model.startswith(prefix)


def create_default_fallback_llm(
    api_key: Optional[str] = None,
    temperature: float = 0.5,
    timeout: int = 60,
    allowed_tries: int = 2
) -> FallbackLLM:
    """
    Create a FallbackLLM with the default model chain for forecasting.

    Primary: x-ai/grok-4-fast:free
    Fallbacks: deepseek/deepseek-chat-v3.1:free, z-ai/glm-4.5-air:free,
               deepseek/deepseek-r1-0528:free, deepseek/deepseek-chat-v3-0324:free,
               deepseek/deepseek-r1:free, qwen/qwen3-235b-a22b:free,
               google/gemini-2.0-flash-exp:free

    Args:
        api_key: OpenRouter API key (optional, uses env var if not provided)
        temperature: Temperature parameter
        timeout: Timeout in seconds
        allowed_tries: Number of allowed retries per model

    Returns:
        Configured FallbackLLM instance
    """
    model_chain = [
        "openrouter/deepseek/deepseek-chat",
        "openrouter/deepseek/deepseek-chat-v3",
        "openrouter/tngtech/deepseek-r1t2-chimera:free",
        "openrouter/z-ai/glm-4.5-air:free",
        "openrouter/tngtech/deepseek-r1t-chimera:free",
        "openrouter/microsoft/mai-ds-r1:free",
        "openrouter/qwen/qwen3-235b-a22b:free",
        "openrouter/google/gemini-2.0-flash-exp:free",
        "openrouter/meta-llama/llama-3.3-70b-instruct:free"
    ]

    return FallbackLLM(
        model_chain=model_chain,
        api_key=api_key,
        temperature=temperature,
        timeout=timeout,
        allowed_tries=allowed_tries
    )


def create_research_fallback_llm(
    api_key: Optional[str] = None,
    temperature: float = 0.3,
    timeout: int = 60,
    allowed_tries: int = 2
) -> FallbackLLM:
    """
    Create a FallbackLLM optimized for research tasks (lower temperature for consistency).

    Args:
        api_key: OpenRouter API key (optional, uses env var if not provided)
        temperature: Temperature parameter (default 0.3 for research)
        timeout: Timeout in seconds
        allowed_tries: Number of allowed retries per model

    Returns:
        Configured FallbackLLM instance for research
    """
    return create_default_fallback_llm(
        api_key=api_key,
        temperature=temperature,
        timeout=timeout,
        allowed_tries=allowed_tries
    )


def create_synthesis_fallback_llm(
    api_key: Optional[str] = None,
    temperature: float = 0.3,
    timeout: int = 60,
    allowed_tries: int = 2
) -> FallbackLLM:
    """
    Create a FallbackLLM optimized for synthesis tasks (lower temperature for consistency).

    Args:
        api_key: OpenRouter API key (optional, uses env var if not provided)
        temperature: Temperature parameter (default 0.3 for synthesis)
        timeout: Timeout in seconds
        allowed_tries: Number of allowed retries per model

    Returns:
        Configured FallbackLLM instance for synthesis
    """
    return create_default_fallback_llm(
        api_key=api_key,
        temperature=temperature,
        timeout=timeout,
        allowed_tries=allowed_tries
    )


def create_forecasting_fallback_llm(
    api_key: Optional[str] = None,
    temperature: float = 0.5,
    timeout: int = 60,
    allowed_tries: int = 2
) -> FallbackLLM:
    """
    Create a FallbackLLM optimized for forecasting tasks (moderate temperature for creativity).

    Args:
        api_key: OpenRouter API key (optional, uses env var if not provided)
        temperature: Temperature parameter (default 0.5 for forecasting)
        timeout: Timeout in seconds
        allowed_tries: Number of allowed retries per model

    Returns:
        Configured FallbackLLM instance for forecasting
    """
    return create_default_fallback_llm(
        api_key=api_key,
        temperature=temperature,
        timeout=timeout,
        allowed_tries=allowed_tries
    )