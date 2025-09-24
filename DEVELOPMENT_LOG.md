# Development Log - Troubleshooting Multiple API Keys for OpenRouter Models

## Issue Summary
When attempting to use multiple OpenRouter models that require different API keys (e.g., GPT models with one API key and DeepSeek/Kimi models with another), the bot was failing with "No allowed providers are available for the selected model" errors.

## Root Cause Analysis
The issue was that the forecasting-tools library was trying to use a single API key for all models, but different OpenRouter models require different API keys based on which provider/account they're associated with.

## Solution Implemented

### 1. Understanding the Problem
After researching the forecasting-tools GitHub repository, I discovered that the library supports configuring multiple API keys for different models through the `GeneralLlm` class constructor's `api_key` parameter.

### 2. Configuration Approach
The solution involves explicitly configuring each `GeneralLlm` instance with the appropriate API key:

```python
# For GPT models (using first API key)
"forecaster1": GeneralLlm(
    model="openrouter/openai/gpt-4o",
    api_key=os.getenv('OPENROUTER_API_KEY'),  # First API key
    temperature=0.5,
    timeout=60,
    allowed_tries=2,
),

# For DeepSeek/Kimi models (using second API key)
"forecaster2": GeneralLlm(
    model="openrouter/deepseek/deepseek-chat-v3-0324",
    api_key="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",  # Second API key
    temperature=0.5,
    timeout=60,
    allowed_tries=2,
),
```

### 3. Key Implementation Details

#### A. Bot Initialization
Updated the bot initialization to configure each model with its specific API key:

```python
template_bot = FallTemplateBot2025(
    llms={
        # GPT models using original key (first API key)
        "forecaster1": GeneralLlm(
            model="openrouter/openai/gpt-4o",
            api_key=os.getenv('OPENROUTER_API_KEY'),
            temperature=0.5,
            timeout=60,
            allowed_tries=2,
        ),
        # DeepSeek model using second API key
        "forecaster2": GeneralLlm(
            model="openrouter/deepseek/deepseek-chat-v3-0324",
            api_key="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",
            temperature=0.5,
            timeout=60,
            allowed_tries=2,
        ),
        # Kimi model using second API key
        "forecaster3": GeneralLlm(
            model="openrouter/moonshotai/kimi-k2-0905",
            api_key="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",
            temperature=0.5,
            timeout=60,
            allowed_tries=2,
        ),
        # Continue with other models as needed...
    },
)
```

#### B. Class-Level Configuration
Also updated the `_llm_config_defaults` method to ensure proper API key assignment:

```python
def _llm_config_defaults(self) -> dict:
    defaults = super()._llm_config_defaults()
    forecaster_defaults = {
        "forecaster1": {"model": "openrouter/openai/gpt-4o", "api_key": os.getenv('OPENROUTER_API_KEY'), **defaults},
        "forecaster2": {"model": "openrouter/deepseek/deepseek-chat-v3-0324", "api_key": "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", **defaults},
        "forecaster3": {"model": "openrouter/moonshotai/kimi-k2-0905", "api_key": "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", **defaults},
        "forecaster4": {"model": "openrouter/openai/gpt-4o", "api_key": os.getenv('OPENROUTER_API_KEY'), **defaults},
    }
    return {**defaults, **forecaster_defaults}
```

### 4. Verification
The solution was verified by:
- Testing with multiple models requiring different API keys
- Confirming successful API calls to both GPT and DeepSeek/Kimi models
- Verifying that forecasts were generated from all configured models
- Ensuring the synthesizer successfully combined predictions from different models

## Common Mistakes to Avoid

### 1. Using String Model Names Instead of GeneralLlm Instances
**Incorrect:**
```python
"forecaster1": "openrouter/openai/gpt-4o",  # Uses default API key only
```

**Correct:**
```python
"forecaster1": GeneralLlm(
    model="openrouter/openai/gpt-4o",
    api_key=os.getenv('OPENROUTER_API_KEY'),  # Explicit API key specification
    temperature=0.5,
    timeout=60,
    allowed_tries=2,
),
```

### 2. Assuming All Models Use the Same API Key
Different OpenRouter models may be associated with different accounts/providers, requiring specific API keys for each.

### 3. Not Checking Model Availability
Always verify that models are available with the specific API key being used. Some models may only be accessible with certain API keys.

## Best Practices

### 1. Environment Variable Management
Store API keys in environment variables for security:
```python
api_key=os.getenv('OPENROUTER_API_KEY')
```

### 2. Error Handling
Implement proper error handling for API key authentication failures:
- Check for "No allowed providers are available" errors
- Implement fallback strategies for unavailable models
- Log specific model/API key combinations that fail

### 3. Model Documentation
Document which models require which API keys:
- GPT models typically use the primary OpenRouter API key
- DeepSeek and Kimi models may require specific partner API keys
- Always test model availability with each API key before deployment

## Future Improvements

### 1. Dynamic API Key Selection
Implement logic to automatically select the appropriate API key based on the model provider:
```python
def get_api_key_for_model(model_name: str) -> str:
    if model_name.startswith("openrouter/openai/") or model_name.startswith("openrouter/anthropic/"):
        return os.getenv('OPENROUTER_API_KEY_PRIMARY')
    elif model_name.startswith("openrouter/deepseek/") or model_name.startswith("openrouter/moonshotai/"):
        return os.getenv('OPENROUTER_API_KEY_SECONDARY')
    else:
        return os.getenv('OPENROUTER_API_KEY_DEFAULT')
```

### 2. Configuration Validation
Add startup validation to verify all configured models are accessible with their respective API keys.

### 3. Automatic Fallback
Implement automatic fallback to alternative models when primary models are unavailable with specific API keys.