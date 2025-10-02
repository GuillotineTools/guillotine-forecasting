# Project Context: Metaculus Forecasting Bot

## Project Overview

This is a Metaculus forecasting bot template designed for the AI Forecasting Tournament. The bot automatically forecasts on open questions in Metaculus tournaments by researching questions using AI models and search providers, then submitting probabilistic forecasts.

The project provides two main implementations:
1. `main.py` - A template bot using the `forecasting-tools` package for handling API calls and complex forecasting logic
2. `main_with_no_framework.py` - A minimal dependencies implementation for more custom approaches

## Key Features

- Automated research using various search providers (AskNews, Perplexity, Exa, etc.)
- Multi-model forecasting approach with ensemble predictions
- Support for binary, numeric, and multiple-choice questions
- Automated submission of forecasts to Metaculus
- Benchmarking against community predictions
- GitHub Actions automation for regular forecasting

## Technologies Used

- Python 3.11+
- Poetry for dependency management
- forecasting-tools package (Metaculus' official forecasting library)
- Various LLM providers (OpenAI, OpenRouter, Anthropic, etc.)
- Search providers (AskNews, Perplexity, Exa)

## Setup and Installation

1. Install Python 3.11+ and Poetry
2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables by copying `.env.template` to `.env` and filling in your API keys:
   - `METACULUS_TOKEN` (required)
   - `OPENROUTER_API_KEY` or other LLM provider keys
   - Search provider keys (AskNews, Perplexity, etc.)

## Running the Bot

### Local Execution

To run the bot locally in test mode:
```bash
poetry run python main.py --mode test_questions
```

Other modes:
- `--mode tournament` - Forecast on current tournament questions (default)
- `--mode metaculus_cup` - Forecast on Metaculus Cup questions

### GitHub Actions Automation

The bot can be automated using GitHub Actions:
1. Fork the repository
2. Set repository secrets for API keys
3. Enable GitHub Actions workflows
4. The bot will run every 20 minutes automatically

Workflows:
- `run_bot_on_tournament.yaml` - Runs on tournament questions
- `run_bot_on_metaculus_cup.yaml` - Runs on Metaculus Cup questions
- `test_bot.yaml` - Tests the bot

## Code Structure

### Main Implementation (`main.py`)

The main implementation uses the `FallTemplateBot2025` class which extends `ForecastBot` from the forecasting-tools package. Key features include:

- Multi-model ensemble forecasting (6 different models)
- Research synthesis using various search strategies
- Structured output parsing using LLMs
- Concurrent question processing with rate limiting

### Minimal Implementation (`main_with_no_framework.py`)

A ground-up implementation without the forecasting-tools framework that:
- Handles API calls directly
- Implements custom research and forecasting logic
- Supports all question types (binary, numeric, multiple choice)
- Provides more control but requires more manual implementation

## Key Components

### Forecasting Logic

1. **Research Phase**: Uses search providers to gather relevant information
2. **Forecasting Phase**: Multiple LLMs generate independent forecasts
3. **Synthesis Phase**: Combines multiple forecasts into a final prediction
4. **Submission Phase**: Posts forecast to Metaculus with reasoning

### Benchmarking

The `community_benchmark.py` script allows benchmarking bot performance against community predictions using expected baseline scores.

### Configuration

The bot can be configured with:
- Different LLM models for different roles (researcher, forecaster, synthesizer)
- Adjustable number of research reports and predictions per question
- Custom search strategies
- Rate limiting for API calls

## Development Guidelines

- Use the `forecasting-tools` package for standardized functionality
- Follow the multi-model ensemble approach for better calibration
- Implement proper error handling and logging
- Use structured output parsing for consistent results
- Test with dummy questions before running on real tournaments

## Important Notes

- The bot requires valid API keys for Metaculus and at least one LLM/search provider
- Rate limits should be considered when configuring concurrent processing
- Forecasts are submitted automatically unless configured otherwise
- Previous forecasts are skipped by default to avoid duplicate submissions