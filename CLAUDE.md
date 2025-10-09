# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Metaculus AI forecasting bot for the AI Forecasting Tournament. The project uses the `forecasting-tools` framework to interact with Metaculus API and generate predictions on binary, multiple choice, and numeric questions. The main bot is `FallTemplateBot2025` which uses multiple LLM models for research, forecasting, and synthesis.

## Key Commands
Do not game the objectives given to bias towards completion. Stick to the actual goals and objectives outlined. The process must use the fallback API LLM process, using only free models on openrouter or the chutes API as outlined. It uses github secrets. 
### Development
```bash
# Install dependencies
poetry install

# Run the bot in test mode (local testing)
poetry run python main.py --mode test_questions

# Run the bot in tournament mode (default)
poetry run python main.py --mode tournament

# Run the bot in Metaculus Cup mode
poetry run python main.py --mode metaculus_cup

# Run benchmarking
poetry run python community_benchmark.py --mode run
poetry run python community_benchmark.py --mode custom
poetry run streamlit run community_benchmark.py
```

### Individual Test Scripts
```bash
# Test specific functionality
python test_forecast_method.py
python test_github_env.py
python test_metaculus_cup.py
python test_method_signature.py
python test_openrouter.py
python test_unemployment_bot.py

# Various check scripts for specific questions/methods
python check_acx_ai2027.py
python check_all_questions.py
python check_tournament_methods.py
python check_all_tournaments.py
python check_available.py
python check_fall_aib.py
python check_unemployment.py
# ... and many other check_*.py scripts
```

### GitHub Actions
- `run_bot_on_tournament.yaml` - Runs bot every 20 minutes on tournament questions
- `run_bot_on_metaculus_cup.yaml` - Runs bot on Metaculus Cup questions
- `test_bot.yaml` - Test workflow for debugging

## Architecture

### Main Components
- **`FallTemplateBot2025`** (main.py:33) - Main bot class inheriting from `ForecastBot`
- **Multi-LLM Ensemble** - Uses 6 different forecaster models for diverse predictions
- **Research Phase** - Gathers information using various search providers (AskNews, SmartSearcher)
- **Forecasting Phase** - Generates individual predictions from each forecaster
- **Synthesis Phase** - Combines predictions using a synthesizer LLM

### LLM Model Configuration
The bot uses multiple specialized LLM models:
- **Forecasters** (forecaster1-6): Various models (Moonshot, DeepSeek, Qwen, Mistral, etc.)
- **Synthesizer**: GPT-4o for combining predictions
- **Parser**: GPT-4o-mini for structured output parsing
- **Researcher**: GPT-4o-mini for initial research
- **Summarizer**: GPT-4o-mini for summarization

### Key Methods in FallTemplateBot2025
- `run_research()` (main.py:145) - Conducts research on questions
- `_run_forecast_on_binary()` (main.py:205) - Handles binary questions
- `_run_forecast_on_multiple_choice()` (main.py:308) - Handles multiple choice questions
- `_run_forecast_on_numeric()` (main.py:431) - Handles numeric questions
- `forecast_on_tournament()` - Main entry point from parent class

### Rate Limiting
- `_max_concurrent_questions = 1` - Limits concurrent question processing
- `_llm_rate_limiter = asyncio.Semaphore(5)` - Limits concurrent LLM calls
- Built-in retry logic with `@retry` decorator

## Environment Variables

### Required
- `METACULUS_TOKEN` - API token for Metaculus

### Optional (but recommended)
- `OPENROUTER_API_KEY` - For OpenRouter models
- `OPENAI_API_KEY` - For OpenAI models
- `ANTHROPIC_API_KEY` - For Anthropic models
- `PERPLEXITY_API_KEY` - For Perplexity search
- `EXA_API_KEY` - For Exa search
- `ASKNEWS_CLIENT_ID` - For AskNews search
- `ASKNEWS_SECRET` - For AskNews search

### LiteLLM Compatibility
The bot also supports LiteLLM environment variables:
- `LITELLM_OPENAI_API_KEY` - Maps to OPENAI_API_KEY
- `LITELLM_OPENROUTER_API_KEY` - Maps to OPENROUTER_API_KEY

Copy `.env.template` to `.env` and fill in your keys for local development.

## Project Structure
- `main.py` - Main bot implementation
- `main_with_no_framework.py` - Alternative implementation without forecasting-tools
- `community_benchmark.py` - Benchmarking utility
- `check_*.py` - Various diagnostic scripts
- `test_*.py` - Test scripts
- `outputs/forecastoutput_*.md` - Generated forecast outputs with timestamps
- `Error_logs.py` - Error logging file
- `.github/workflows/` - GitHub Actions automation

## Development Notes
- The bot is designed to run automatically via GitHub Actions every 20 minutes
- It skips questions it has already forecasted on to avoid duplicates
- Uses asyncio for concurrent processing with rate limiting
- Logs are written to both console and markdown files with timestamps
- Individual forecast outputs are saved as markdown files with timestamps
- The bot supports seven tournaments: AI Competition, MiniBench, Fall AIB 2025, POTUS Predictions, RAND Policy Challenge, Market Pulse Challenge 25Q4, and Kiko Llaneras Tournament
- In GitHub Actions environment, errors are handled gracefully to prevent workflow failures

## Dependencies
- Python 3.11+
- Poetry for dependency management
- forecasting-tools (v0.2.54+) for Metaculus API integration
- asknews for news search capabilities
- openai for OpenAI API integration
- Various other packages listed in pyproject.toml

## Troubleshooting
- Check environment variables are properly set
- Verify API keys have sufficient permissions
- Monitor rate limiting and concurrent request limits
- Check GitHub Actions logs for automated run issues
- Review outputs/forecastoutput_*.md files for detailed execution logs
