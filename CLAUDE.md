# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains two main components:

1. **forecasting-tools/** - A comprehensive Python package for AI forecasting and research tools, designed to help users reason about and forecast the future, particularly for Metaculus questions
2. **guillotine-forecasting/** - A Metaculus AI forecasting bot implementation for the AI Forecasting Tournament

## Common Development Commands

### For forecasting-tools (main package)
```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Run tests
pytest code_tests/unit_tests/
pytest code_tests/low_cost_or_live_api_tests/
pytest -nauto  # Parallel execution

# Run specific test
pytest code_tests/unit_tests/test_specific_file.py::test_function_name

# Run Streamlit frontend
streamlit run front_end/Home.py
```

### For guillotine-forecasting (bot implementation)
```bash
# Install dependencies
poetry install

# Run bot in different modes
poetry run python main.py --mode test_questions
poetry run python main.py --mode tournament
poetry run python main.py --mode metaculus_cup

# Run benchmarking
poetry run python community_benchmark.py --mode run
poetry run python community_benchmark.py --mode custom
```

## Architecture Overview

### forecasting-tools Package Structure

**Core Forecasting Framework** (`forecasting_tools/forecast_bots/`):
- `ForecastBot` - Abstract base class for all forecasting bots
- `TemplateBot` - Main bot template for customization (inherits from `Q2TemplateBot2025`)
- `MainBot` - Production-ready bot with advanced features
- `Notepad` - Context object that persists across forecasts on the same question

**AI Models & Integration** (`forecasting_tools/ai_models/`):
- `GeneralLlm` - Main wrapper around litellm for any AI model with retry logic, cost tracking, and structured outputs
- `SmartSearcher` - AI-powered internet search using Exa.ai, similar to Perplexity but more configurable
- `ExaSearcher` - Direct interface to Exa.ai search API
- `MonetaryCostManager` - Context manager for tracking and limiting API costs

**Research Tools** (`forecasting_tools/agents_and_tools/`):
- `KeyFactorsResearcher` - Identifies and scores key factors for forecasting questions
- `BaseRateResearcher` - Calculates historical base rates for events
- `NicheListResearcher` - Analyzes specific lists of events with fact-checking
- `Estimator` - Fermi estimation for numerical predictions
- `QuestionDecomposer` - Breaks down questions into sub-questions

**Data Models** (`forecasting_tools/data_models/`):
- `MetaculusQuestion` - Base question class with subclasses for Binary, MultipleChoice, Numeric, Date
- `ForecastReport` - Contains question, prediction, reasoning, and metadata
- Question-specific reports: `BinaryReport`, `MultipleChoiceReport`, `NumericReport`

**Metaculus API** (`forecasting_tools/helpers/`):
- `MetaculusApi` - API wrapper for questions, tournaments, predictions, and comments
- `ApiFilter` - Filtering class for querying questions

**Benchmarking** (`forecasting_tools/cp_benchmarking/`):
- `Benchmarker` - Runs comparative evaluations between bots
- `BenchmarkForBot` - Contains benchmark results and statistics
- `PromptOptimizer` - Iteratively improves bot prompts

### guillotine-forecasting Bot Implementation

**Main Bot** (`main.py`):
- `FallTemplateBot2025` - Main bot class inheriting from `ForecastBot`
- Multi-LLM ensemble using 6 different forecaster models
- Support for binary, multiple choice, and numeric questions
- Automated research using various search providers
- GitHub Actions automation for regular forecasting

**Key Features**:
- Multi-model ensemble approach for diverse predictions
- Research phase using AskNews, SmartSearcher, and other providers
- Synthesis phase combining predictions using GPT-4o
- Rate limiting and retry logic
- Comprehensive logging and error handling

## Environment Variables

### Required for Basic Functionality
- `OPENAI_API_KEY` - For OpenAI models
- `EXA_API_KEY` - For web search functionality
- `METACULUS_TOKEN` - For posting predictions/comments to Metaculus

### Optional but Commonly Used
- `ANTHROPIC_API_KEY` - For Claude models
- `PERPLEXITY_API_KEY` - Alternative to Exa for search
- `OPENROUTER_API_KEY` - For OpenRouter models
- `ASKNEWS_CLIENT_ID` and `ASKNEWS_SECRET` - For AskNews search
- `FILE_WRITING_ALLOWED` - Set to "TRUE" to enable log file writing

### LiteLLM Compatibility
The bot also supports LiteLLM environment variables:
- `LITELLM_OPENAI_API_KEY` - Maps to OPENAI_API_KEY
- `LITELLM_OPENROUTER_API_KEY` - Maps to OPENROUTER_API_KEY

## Code Style and Patterns

### Type Hints
- All functions should have type hints for parameters and outputs
- Use built-in type hints (like `list`, `dict`, `tuple`) instead of importing from `typing`
- Follow modern Python type annotation practices

### Code Formatting
- Black formatter with line length 88
- isort with black profile
- ruff linter with specific ignored rules (E741, E731, E402, E711, E712, E721)
- Avoid unnecessary comments; use descriptive names instead

### Bot Customization Pattern
Standard approach is to inherit from `TemplateBot` and override:
- `run_research()` - Custom research approach
- `_run_forecast_on_binary()` - Binary question forecasting
- `_run_forecast_on_multiple_choice()` - Multiple choice forecasting
- `_run_forecast_on_numeric()` - Numeric forecasting
- `_initialize_notepad()` - Maintain state between forecasts

## Model Integration

The project uses litellm for unified model access. Models can be specified as:
- Direct: `"gpt-4o"`, `"claude-3-5-sonnet-20241022"`
- With provider: `"openai/gpt-4o"`, `"anthropic/claude-3-5-sonnet"`
- Via Metaculus proxy: `"metaculus/claude-3-5-sonnet-20241022"`

All models support structured outputs via `invoke_and_return_verified_type()` with Pydantic validation.

## Testing Guidelines

- Tests are organized by cost: unit_tests (free), low_cost_or_live_api, expensive
- `asyncio_mode = auto` is set in pytest.ini, so no need to mark tests with pytest.mark.asyncio
- When testing errors with `pytest.raises()`, don't match exception text to predefined values
- Use parallel execution with `pytest -nauto`

## Project Structure Notes

- Main entry point: `forecasting_tools/__init__.py` with comprehensive exports
- Tests are in `code_tests/` organized by cost
- Frontend uses Streamlit with pages in `front_end/`
- Logs are written to rotating files in `logs/` directory
- Dev container configuration in `.devcontainer/` for consistent environments
- Individual forecast outputs saved as markdown files with timestamps in guillotine-forecasting

## Key Dependencies

### forecasting-tools
- Python 3.11+
- Poetry for dependency management
- openai, litellm for AI model access
- pydantic for data validation
- streamlit for frontend
- scikit-learn, pandas, numpy for data processing
- asyncio for concurrent processing

### guillotine-forecasting
- forecasting-tools (v0.2.54+) for Metaculus API integration
- asknews for news search
- Additional AI model providers via OpenRouter

## Cost Management

Use `MonetaryCostManager` as a context manager to track and limit API costs:
```python
with MonetaryCostManager(max_cost=5.00) as cost_manager:
    # API calls here
    current_cost = cost_manager.current_usage
```

## Rate Limiting and Concurrency

- Built-in rate limiting with `asyncio.Semaphore`
- Retry logic for failed API calls
- Configurable concurrent question processing limits
- LLM-specific rate limiting to avoid API quotas

## Development History & Changes Log

### September 2025 - Critical Reliability Improvements

#### Issue: Bot Missed Tournament Questions (Sept 25, 2025)
**Problem**: Bot failed to forecast on 4 Fall AIB 2025 tournament questions despite 20-minute GitHub Actions schedule.

**Root Causes Identified**:
1. **GitHub Actions Gap**: 6.5-hour gap in workflow runs (14:30-20:58) when questions were open (15:30-18:33)
2. **API Filtering Bug**: Questions with `tournament_slugs: ['fall-aib-2025']` not returned by `ApiFilter(allowed_tournaments=['fall-aib-2025'])`
3. **Unrealistic Time Windows**: Initial 7-day search window was too long for tournament questions (only open 1-2 hours)

**Solutions Implemented**:

1. **GitHub Actions Redundancy** (`.github/workflows/run_bot_on_tournament.yaml`):
   - Added multiple backup schedules: 15, 20, and 30-minute intervals
   - Added 30-minute timeout protection
   - Implemented `continue-on-error: true` for resilience
   ```yaml
   schedule:
     # Multiple schedules for redundancy - if one fails, others should catch it
     - cron: "*/15 * * * *" # Every 15 minutes
     - cron: "*/20 * * * *" # Every 20 minutes (backup)
     - cron: "*/30 * * * *" # Every 30 minutes (backup)
   ```

2. **API Fallback Mechanism** (`main.py`):
   - Added `get_tournament_questions_fallback()` function for when API filtering fails
   - Manually filters recent questions by `tournament_slugs` field
   - Uses realistic 3-hour time window for fallback search
   ```python
   async def get_tournament_questions_fallback(tournament_slug: str, statuses: list[str] = None):
       """Fallback function to get tournament questions when API filtering fails"""
       recent_filter = ApiFilter(open_time_gt=datetime.now() - timedelta(hours=3))
       all_recent_questions = await MetaculusApi.get_questions_matching_filter(recent_filter)
       # Manual filtering by tournament_slugs field
   ```

3. **Missed Question Detection & Alerting** (`main.py:905-930`):
   - Added function to detect missed questions from past 1.5 hours
   - Integrates with both email and ntfy notification systems
   - Provides detailed alerts about missed forecasting opportunities

4. **Time Window Corrections**:
   - Changed fallback search from 7 days to 3 hours
   - Changed missed question detection from 6 hours to 1.5 hours
   - User feedback: "Theres no point in searching the last 7 days of questions and checking more than 1.5 hrs in the past because the questions will be closed by then"

5. **ntfy Notification System Setup**:
   - Configured with topic: `metaculus-bot-jsgle`
   - Free service from ntfy.sh (10,000 messages/day, 12-hour retention)
   - Mobile app integration for real-time alerts
   - Alerts for: new questions, bot status, missed questions, forecasts

**Files Modified**:
- `.github/workflows/run_bot_on_tournament.yaml` - Added redundant scheduling
- `main.py` - Added fallback mechanism and missed question detection
- `.env` - Added `NTFY_TOPIC=metaculus-bot-jsgle`

**Testing**:
- Created `test_fallback_fix.py` to verify API fallback functionality
- Verified ntfy notifications work correctly
- Confirmed time windows are appropriate for tournament question lifecycle

**Key Learnings**:
- Tournament questions have very short windows (1-2 hours open)
- API filtering cannot be relied upon exclusively
- Multiple redundancy layers are essential for reliability
- Real-time notifications are critical for time-sensitive opportunities