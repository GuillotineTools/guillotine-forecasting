# CRUSH.md

## Build & Test Commands

### Environment Setup
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Running the Bot
```bash
# Main modes (includes all tournaments: AI Competition, MiniBench, Fall AIB 2025, POTUS Predictions)
poetry run python main.py --mode tournament      # Production tournament mode
poetry run python main.py --mode metaculus_cup   # Testing on regular questions
poetry run python main.py --mode test_questions  # Debug with dummy questions
```

### Individual Testing
```bash
# Run specific test scripts (no test framework)
python test_basic.py
python test_openrouter.py
python test_metaculus_api.py
python test_forecast_method.py

# Diagnostic scripts
python check_tournaments.py
python check_available.py
python check_env_vars.py
```

### Benchmarking
```bash
poetry run python community_benchmark.py --mode run
poetry run python community_benchmark.py --mode custom
poetry run streamlit run community_benchmark.py
```

## Code Style Guidelines

### Imports & Structure
- Standard library imports first, then third-party, then local
- Use `from dotenv import load_dotenv` and `load_dotenv()` at top of main files
- Async files start with `import asyncio`
- Type hints using `from typing import` for complex types

### Naming Conventions
- Classes: `PascalCase` (e.g., `FallTemplateBot2025`)
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: prefix with underscore (`_method_name`)

### Error Handling
- Use `tenacity` retry decorator: `@retry(stop_after_attempt(3), wait_fixed(1))`
- Graceful error handling in GitHub Actions environment
- Log errors with `logging.getLogger(__name__)`

### API Integration
- Environment variables via `python-decouple` or `python-dotenv`
- Use fallback LLM system from `fallback_llm.py`
- Rate limiting with `asyncio.Semaphore(5)` for concurrent LLM calls
- Maximum concurrent questions: `1`

### File Organization
- Main bot: `main.py` with `FallTemplateBot2025` class
- Test files: `test_*.py` prefix
- Diagnostic scripts: `check_*.py` prefix
- Outputs saved to `outputs/` with timestamps
- Use `forecasting-tools` framework for Metaculus API

### LLM Configuration
- Multiple forecaster models (forecaster1-6) with fallback system
- Synthesizer: GPT-4o for combining predictions
- Researcher: GPT-4o-mini for initial research
- Use OpenRouter for free models when possible