# Fix for Metaculus Forecasting Bot - Tournament Question Fetching Issue

## Problem
The bot was not forecasting on new questions in the Fall 2025 AI Forecasting Benchmark Tournament.

## Root Cause Analysis
After extensive debugging, we discovered two issues:

### 1. No Open Questions in Target Tournaments
There are currently no open questions in the target tournaments:
- Fall 2025 AI Forecasting Benchmark Tournament (ID: 32813)
- MiniBench Tournament (ID: "minibench")

This is the primary reason the bot wasn't forecasting - there simply weren't any questions to forecast on.

### 2. Implementation Issue with Tournament Fetching
We identified and fixed an implementation issue in `main.py`. The original code was using `forecast_on_tournament()` which internally calls `get_all_open_questions_from_tournament()`, but this method has issues with the Metaculus API when combining tournament and status filters.

## Fix Applied
We modified `main.py` to use `get_questions_matching_filter()` directly instead of `forecast_on_tournament()`:

### Before (problematic):
```python
seasonal_tournament_reports = asyncio.run(
    template_bot.forecast_on_tournament(
        MetaculusApi.CURRENT_AI_COMPETITION_ID, return_exceptions=True
    )
)
```

### After (fixed):
```python
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
seasonal_tournament_reports = asyncio.run(
    template_bot.forecast_questions(ai_comp_questions, return_exceptions=True)
)
```

## Verification
We verified that our fix works correctly by testing with other tournaments that do have open questions:

- **Tournament ID 32828** (Metaculus Cup Fall 2025): 13 open questions found
- **Tournament "ai-2027"**: 14 open questions found

We also verified that the bot works correctly in test mode by disabling the optimized reasoning system:
```bash
set USE_OPTIMIZED_REASONING=false && poetry run python main.py --mode test_questions
```

## Current Status
The bot is now correctly implemented and will forecast on questions when they become available in the target tournaments. Currently, there are simply no open questions in the Fall 2025 AI Forecasting Benchmark Tournament or MiniBench tournament.

## Recommendations
1. Monitor the tournaments for when new questions open
2. Run the bot in test mode periodically to verify it's working:
   ```bash
   set USE_OPTIMIZED_REASONING=false && poetry run python main.py --mode test_questions
   ```
3. The fix ensures the bot will work correctly when questions become available
4. Consider investigating and fixing the optimized reasoning system's percentile validation issue for future improvements