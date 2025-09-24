Run poetry run python main.py
2025-09-10 23:27:55.861 WARNING streamlit.runtime.caching.cache_data_api: No runtime found, using MemoryCacheStorageManager
2025-09-10 23:27:55,870 - forecasting_tools.ai_models.model_tracker - WARNING - Warning: Model openrouter/openai/gpt-4o-mini does not support cost tracking.
2025-09-10 23:27:55,870 - forecasting_tools.ai_models.model_tracker - WARNING - Warning: Model openrouter/openai/gpt-4.1:online does not support cost tracking.
2025-09-10 23:27:55,871 - forecasting_tools.forecast_bots.forecast_bot - WARNING - There is no default for llm: 'synthesizer'.Please override and add it to the _llm_config_defaults method
2025-09-10 23:27:55,874 - forecasting_tools.helpers.metaculus_api - INFO - Retrieving questions from tournament 32813
2025-09-10 23:27:58,639 - forecasting_tools.helpers.metaculus_api - INFO - Returning 1 questions matching the Metaculus API filter
2025-09-10 23:27:58,639 - forecasting_tools.helpers.metaculus_api - INFO - Retrieved 1 questions from tournament 32813
2025-09-10 23:28:03,644 - openai.agents - WARNING - OPENAI_API_KEY is not set, skipping trace export
2025-09-10 23:28:07,895 - forecasting_tools.forecast_bots.forecast_bot - WARNING - Encountered errors while researching: ["BadRequestError: litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys."]
2025-09-10 23:28:07,895 - forecasting_tools.forecast_bots.forecast_bot - ERROR - Error while processing question url: 'https://www.metaculus.com/questions/39397': All 1 research reports/predictions failed: Errors: ["BadRequestError: litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys."] (1 sub-exception)
2025-09-10 23:28:07,895 - forecasting_tools.helpers.metaculus_api - INFO - Retrieving questions from tournament minibench
2025-09-10 23:28:08,648 - openai.agents - WARNING - OPENAI_API_KEY is not set, skipping trace export
2025-09-10 23:28:10,503 - forecasting_tools.helpers.metaculus_api - INFO - Returning 0 questions matching the Metaculus API filter
2025-09-10 23:28:10,503 - forecasting_tools.helpers.metaculus_api - INFO - Retrieved 0 questions from tournament minibench
2025-09-10 23:28:10,504 - forecasting_tools.forecast_bots.forecast_bot - INFO - 
----------------------------------------------------------------------------------------------------
Bot: FallTemplateBot2025
❌ Exception: ExceptionGroup | Message: Error while processing question url: 'https://www.metaculus.com/questions/39397': All 1 research reports/predictions failed: Errors: ["BadRequestError: litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys."] (1 sub-exception)

Stats for passing reports:
Total cost estimated: $0.00000
Average cost per question: $0.00000
Average time spent per question: 0.0000 minutes
----------------------------------------------------------------------------------------------------



2025-09-10 23:28:10,640 - forecasting_tools.forecast_bots.forecast_bot - ERROR - Exception occurred during forecasting:
Logging to forecastoutput_20250910_232755.md
  + Exception Group Traceback (most recent call last):
  |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 338, in _run_individual_question_with_error_propagation
  |     return await self._run_individual_question(question)
  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 370, in _run_individual_question
  |     self._reraise_exception_with_prepended_message(
  |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 649, in _reraise_exception_with_prepended_message
  |     raise ExceptionGroup(
  | ExceptionGroup: All 1 research reports/predictions failed: Errors: ["BadRequestError: litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys."] (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/opt/hostedtoolcache/Python/3.11.13/x64/lib/python3.11/asyncio/tasks.py", line 277, in __step
    |     result = coro.send(None)
    |              ^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 439, in _research_and_make_predictions
    |     research = await self.run_research(question)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/main.py", line 194, in run_research
    |     research = await self.get_llm("researcher", "llm").invoke(prompt)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/general_llm.py", line 208, in invoke
    |     await self._invoke_with_request_cost_time_and_token_limits_and_retry(prompt)
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/model_interfaces/retryable_model.py", line 58, in wrapper_with_access_to_self_variable
    |     return await wrapper_with_action(self, *args, **kwargs)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 189, in async_wrapped
    |     return await copy(fn, *args, **kwargs)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 111, in __call__
    |     do = await self.iter(retry_state=retry_state)
    |          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 153, in iter
    |     result = await action(retry_state)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/_utils.py", line 99, in inner
    |     return call(*args, **kwargs)
    |            ^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/__init__.py", line 420, in exc_check
    |     raise retry_exc.reraise()
    |           ^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/__init__.py", line 187, in reraise
    |     raise self.last_attempt.result()
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/opt/hostedtoolcache/Python/3.11.13/x64/lib/python3.11/concurrent/futures/_base.py", line 449, in result
    |     return self.__get_result()
    |            ^^^^^^^^^^^^^^^^^^^
    |   File "/opt/hostedtoolcache/Python/3.11.13/x64/lib/python3.11/concurrent/futures/_base.py", line 401, in __get_result
    |     raise self._exception
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 114, in __call__
    |     result = await fn(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/model_interfaces/retryable_model.py", line 55, in wrapper_with_action
    |     result = await func(self, *args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/general_llm.py", line 223, in _invoke_with_request_cost_time_and_token_limits_and_retry
    |     direct_call_response = await self._mockable_direct_call_to_model(prompt)
    |                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/general_llm.py", line 244, in _mockable_direct_call_to_model
    |     response = await acompletion(
    |                ^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/utils.py", line 1586, in wrapper_async
    |     raise e
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/utils.py", line 1437, in wrapper_async
    |     result = await original_function(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/main.py", line 560, in acompletion
    |     raise exception_type(
    |           ^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/litellm_core_utils/exception_mapping_utils.py", line 2301, in exception_type
    |     raise e
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/litellm_core_utils/exception_mapping_utils.py", line 391, in exception_type
    |     raise BadRequestError(
    | litellm.exceptions.BadRequestError: litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys.
    +------------------------------------

During handling of the above exception, another exception occurred:

  + Exception Group Traceback (most recent call last):
  |   File "/opt/hostedtoolcache/Python/3.11.13/x64/lib/python3.11/asyncio/tasks.py", line 277, in __step
  |     result = coro.send(None)
  |              ^^^^^^^^^^^^^^^
  |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 344, in _run_individual_question_with_error_propagation
  |     self._reraise_exception_with_prepended_message(e, error_message)
  |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 649, in _reraise_exception_with_prepended_message
  |     raise ExceptionGroup(
  | ExceptionGroup: Error while processing question url: 'https://www.metaculus.com/questions/39397': All 1 research reports/predictions failed: Errors: ["BadRequestError: litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys."] (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/llms/openai/openai.py", line 801, in acompletion
    |     headers, response = await self.make_openai_chat_completion_request(
    |                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/litellm_core_utils/logging_utils.py", line 135, in async_wrapper
    |     result = await func(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/llms/openai/openai.py", line 436, in make_openai_chat_completion_request
    |     raise e
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/llms/openai/openai.py", line 418, in make_openai_chat_completion_request
    |     await openai_aclient.chat.completions.with_raw_response.create(
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/openai/_legacy_response.py", line 381, in wrapped
    |     return cast(LegacyAPIResponse[R], await func(*args, **kwargs))
    |                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/openai/resources/chat/completions/completions.py", line 2544, in create
    |     return await self._post(
    |            ^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/openai/_base_client.py", line 1791, in post
    |     return await self.request(cast_to, opts, stream=stream, stream_cls=stream_cls)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/openai/_base_client.py", line 1591, in request
    |     raise self._make_status_error_from_response(err.response) from None
    | openai.AuthenticationError: Error code: 401 - {'error': {'message': "You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys.", 'type': 'invalid_request_error', 'param': None, 'code': None}}
    | 
    | During handling of the above exception, another exception occurred:
    | 
    | Traceback (most recent call last):
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/main.py", line 541, in acompletion
    |     response = await init_response
    |                ^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/llms/openai/openai.py", line 848, in acompletion
    |     raise OpenAIError(
    | litellm.llms.openai.common_utils.OpenAIError: Error code: 401 - {'error': {'message': "You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys.", 'type': 'invalid_request_error', 'param': None, 'code': None}}
    | 
    | During handling of the above exception, another exception occurred:
    | 
    | Traceback (most recent call last):
    |   File "/opt/hostedtoolcache/Python/3.11.13/x64/lib/python3.11/asyncio/tasks.py", line 277, in __step
    |     result = coro.send(None)
    |              ^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 439, in _research_and_make_predictions
    |     research = await self.run_research(question)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/main.py", line 194, in run_research
    |     research = await self.get_llm("researcher", "llm").invoke(prompt)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/general_llm.py", line 208, in invoke
    |     await self._invoke_with_request_cost_time_and_token_limits_and_retry(prompt)
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/model_interfaces/retryable_model.py", line 58, in wrapper_with_access_to_self_variable
    |     return await wrapper_with_action(self, *args, **kwargs)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 189, in async_wrapped
    |     return await copy(fn, *args, **kwargs)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 111, in __call__
    |     do = await self.iter(retry_state=retry_state)
    |          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 153, in iter
    |     result = await action(retry_state)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/_utils.py", line 99, in inner
    |     return call(*args, **kwargs)
    |            ^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/__init__.py", line 420, in exc_check
    |     raise retry_exc.reraise()
    |           ^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/__init__.py", line 187, in reraise
    |     raise self.last_attempt.result()
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/opt/hostedtoolcache/Python/3.11.13/x64/lib/python3.11/concurrent/futures/_base.py", line 449, in result
    |     return self.__get_result()
    |            ^^^^^^^^^^^^^^^^^^^
    |   File "/opt/hostedtoolcache/Python/3.11.13/x64/lib/python3.11/concurrent/futures/_base.py", line 401, in __get_result
    |     raise self._exception
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 114, in __call__
    |     result = await fn(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/model_interfaces/retryable_model.py", line 55, in wrapper_with_action
    |     result = await func(self, *args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/general_llm.py", line 223, in _invoke_with_request_cost_time_and_token_limits_and_retry
    |     direct_call_response = await self._mockable_direct_call_to_model(prompt)
    |                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/general_llm.py", line 244, in _mockable_direct_call_to_model
    |     response = await acompletion(
    |                ^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/utils.py", line 1586, in wrapper_async
    |     raise e
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/utils.py", line 1437, in wrapper_async
    |     result = await original_function(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/main.py", line 560, in acompletion
    |     raise exception_type(
    |           ^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/litellm_core_utils/exception_mapping_utils.py", line 2301, in exception_type
    |     raise e
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/litellm_core_utils/exception_mapping_utils.py", line 391, in exception_type
    |     raise BadRequestError(
    | litellm.exceptions.BadRequestError: litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys.
    +------------------------------------

Traceback (most recent call last):
  File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/main.py", line 696, in <module>
    template_bot.log_report_summary(forecast_reports)
Loaded OPENROUTER_API_KEY: **********
  File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 762, in log_report_summary
    raise RuntimeError(
RuntimeError: 1 errors occurred while forecasting: [ExceptionGroup('Error while processing question url: \'https://www.metaculus.com/questions/39397\': All 1 research reports/predictions failed: Errors: ["BadRequestError: litellm.BadRequestError: OpenAIException - You didn\'t provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you\'re accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys."]', (litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys.,))]
Error: Process completed with exit code 1.

# Second error log

Run poetry run python main.py
2025-09-10 23:43:05.860 WARNING streamlit.runtime.caching.cache_data_api: No runtime found, using MemoryCacheStorageManager
2025-09-10 23:43:05,869 - forecasting_tools.ai_models.model_tracker - WARNING - Warning: Model openrouter/openai/gpt-4o-mini does not support cost tracking.
2025-09-10 23:43:05,870 - forecasting_tools.ai_models.model_tracker - WARNING - Warning: Model openrouter/openai/gpt-4.1:online does not support cost tracking.
2025-09-10 23:43:05,871 - forecasting_tools.forecast_bots.forecast_bot - WARNING - There is no default for llm: 'synthesizer'.Please override and add it to the _llm_config_defaults method
2025-09-10 23:43:05,873 - forecasting_tools.helpers.metaculus_api - INFO - Retrieving questions from tournament 32813
2025-09-10 23:43:08,598 - forecasting_tools.helpers.metaculus_api - INFO - Returning 1 questions matching the Metaculus API filter
2025-09-10 23:43:08,598 - forecasting_tools.helpers.metaculus_api - INFO - Retrieved 1 questions from tournament 32813
2025-09-10 23:43:13,607 - openai.agents - WARNING - OPENAI_API_KEY is not set, skipping trace export
2025-09-10 23:43:18,685 - forecasting_tools.forecast_bots.forecast_bot - WARNING - Encountered errors while researching: ["BadRequestError: litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys."]
2025-09-10 23:43:18,685 - forecasting_tools.forecast_bots.forecast_bot - ERROR - Error while processing question url: 'https://www.metaculus.com/questions/39397': All 1 research reports/predictions failed: Errors: ["BadRequestError: litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys."] (1 sub-exception)
2025-09-10 23:43:18,686 - forecasting_tools.helpers.metaculus_api - INFO - Retrieving questions from tournament minibench
2025-09-10 23:43:21,335 - forecasting_tools.helpers.metaculus_api - INFO - Returning 0 questions matching the Metaculus API filter
2025-09-10 23:43:21,336 - forecasting_tools.helpers.metaculus_api - INFO - Retrieved 0 questions from tournament minibench
2025-09-10 23:43:21,336 - forecasting_tools.forecast_bots.forecast_bot - INFO - 
----------------------------------------------------------------------------------------------------
Bot: FallTemplateBot2025
❌ Exception: ExceptionGroup | Message: Error while processing question url: 'https://www.metaculus.com/questions/39397': All 1 research reports/predictions failed: Errors: ["BadRequestError: litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys."] (1 sub-exception)

Stats for passing reports:
Total cost estimated: $0.00000
Average cost per question: $0.00000
Average time spent per question: 0.0000 minutes
----------------------------------------------------------------------------------------------------



2025-09-10 23:43:21,392 - forecasting_tools.forecast_bots.forecast_bot - ERROR - Exception occurred during forecasting:
  + Exception Group Traceback (most recent call last):
  |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 338, in _run_individual_question_with_error_propagation
  |     return await self._run_individual_question(question)
  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 370, in _run_individual_question
Logging to forecastoutput_20250910_234305.md
Loaded OPENROUTER_API_KEY: **********
  |     self._reraise_exception_with_prepended_message(
  |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 649, in _reraise_exception_with_prepended_message
  |     raise ExceptionGroup(
  | ExceptionGroup: All 1 research reports/predictions failed: Errors: ["BadRequestError: litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys."] (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/opt/hostedtoolcache/Python/3.11.13/x64/lib/python3.11/asyncio/tasks.py", line 277, in __step
    |     result = coro.send(None)
    |              ^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 439, in _research_and_make_predictions
    |     research = await self.run_research(question)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/main.py", line 194, in run_research
    |     research = await self.get_llm("researcher", "llm").invoke(prompt)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/general_llm.py", line 208, in invoke
    |     await self._invoke_with_request_cost_time_and_token_limits_and_retry(prompt)
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/model_interfaces/retryable_model.py", line 58, in wrapper_with_access_to_self_variable
    |     return await wrapper_with_action(self, *args, **kwargs)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 189, in async_wrapped
    |     return await copy(fn, *args, **kwargs)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 111, in __call__
    |     do = await self.iter(retry_state=retry_state)
    |          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 153, in iter
    |     result = await action(retry_state)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/_utils.py", line 99, in inner
    |     return call(*args, **kwargs)
    |            ^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/__init__.py", line 420, in exc_check
    |     raise retry_exc.reraise()
    |           ^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/__init__.py", line 187, in reraise
    |     raise self.last_attempt.result()
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/opt/hostedtoolcache/Python/3.11.13/x64/lib/python3.11/concurrent/futures/_base.py", line 449, in result
    |     return self.__get_result()
    |            ^^^^^^^^^^^^^^^^^^^
    |   File "/opt/hostedtoolcache/Python/3.11.13/x64/lib/python3.11/concurrent/futures/_base.py", line 401, in __get_result
    |     raise self._exception
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 114, in __call__
    |     result = await fn(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/model_interfaces/retryable_model.py", line 55, in wrapper_with_action
    |     result = await func(self, *args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/general_llm.py", line 223, in _invoke_with_request_cost_time_and_token_limits_and_retry
    |     direct_call_response = await self._mockable_direct_call_to_model(prompt)
    |                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/general_llm.py", line 244, in _mockable_direct_call_to_model
    |     response = await acompletion(
    |                ^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/utils.py", line 1586, in wrapper_async
    |     raise e
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/utils.py", line 1437, in wrapper_async
    |     result = await original_function(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/main.py", line 560, in acompletion
    |     raise exception_type(
    |           ^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/litellm_core_utils/exception_mapping_utils.py", line 2301, in exception_type
    |     raise e
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/litellm_core_utils/exception_mapping_utils.py", line 391, in exception_type
    |     raise BadRequestError(
    | litellm.exceptions.BadRequestError: litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys.
    +------------------------------------

During handling of the above exception, another exception occurred:

  + Exception Group Traceback (most recent call last):
  |   File "/opt/hostedtoolcache/Python/3.11.13/x64/lib/python3.11/asyncio/tasks.py", line 277, in __step
  |     result = coro.send(None)
  |              ^^^^^^^^^^^^^^^
  |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 344, in _run_individual_question_with_error_propagation
  |     self._reraise_exception_with_prepended_message(e, error_message)
  |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 649, in _reraise_exception_with_prepended_message
  |     raise ExceptionGroup(
  | ExceptionGroup: Error while processing question url: 'https://www.metaculus.com/questions/39397': All 1 research reports/predictions failed: Errors: ["BadRequestError: litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys."] (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/llms/openai/openai.py", line 801, in acompletion
    |     headers, response = await self.make_openai_chat_completion_request(
    |                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/litellm_core_utils/logging_utils.py", line 135, in async_wrapper
    |     result = await func(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/llms/openai/openai.py", line 436, in make_openai_chat_completion_request
    |     raise e
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/llms/openai/openai.py", line 418, in make_openai_chat_completion_request
    |     await openai_aclient.chat.completions.with_raw_response.create(
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/openai/_legacy_response.py", line 381, in wrapped
    |     return cast(LegacyAPIResponse[R], await func(*args, **kwargs))
    |                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/openai/resources/chat/completions/completions.py", line 2544, in create
    |     return await self._post(
    |            ^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/openai/_base_client.py", line 1791, in post
    |     return await self.request(cast_to, opts, stream=stream, stream_cls=stream_cls)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/openai/_base_client.py", line 1591, in request
    |     raise self._make_status_error_from_response(err.response) from None
    | openai.AuthenticationError: Error code: 401 - {'error': {'message': "You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys.", 'type': 'invalid_request_error', 'param': None, 'code': None}}
    | 
    | During handling of the above exception, another exception occurred:
    | 
    | Traceback (most recent call last):
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/main.py", line 541, in acompletion
    |     response = await init_response
    |                ^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/llms/openai/openai.py", line 848, in acompletion
    |     raise OpenAIError(
    | litellm.llms.openai.common_utils.OpenAIError: Error code: 401 - {'error': {'message': "You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys.", 'type': 'invalid_request_error', 'param': None, 'code': None}}
    | 
    | During handling of the above exception, another exception occurred:
    | 
    | Traceback (most recent call last):
    |   File "/opt/hostedtoolcache/Python/3.11.13/x64/lib/python3.11/asyncio/tasks.py", line 277, in __step
    |     result = coro.send(None)
    |              ^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 439, in _research_and_make_predictions
    |     research = await self.run_research(question)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/main.py", line 194, in run_research
    |     research = await self.get_llm("researcher", "llm").invoke(prompt)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/general_llm.py", line 208, in invoke
    |     await self._invoke_with_request_cost_time_and_token_limits_and_retry(prompt)
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/model_interfaces/retryable_model.py", line 58, in wrapper_with_access_to_self_variable
    |     return await wrapper_with_action(self, *args, **kwargs)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 189, in async_wrapped
    |     return await copy(fn, *args, **kwargs)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 111, in __call__
    |     do = await self.iter(retry_state=retry_state)
    |          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 153, in iter
    |     result = await action(retry_state)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/_utils.py", line 99, in inner
    |     return call(*args, **kwargs)
    |            ^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/__init__.py", line 420, in exc_check
    |     raise retry_exc.reraise()
    |           ^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/__init__.py", line 187, in reraise
    |     raise self.last_attempt.result()
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/opt/hostedtoolcache/Python/3.11.13/x64/lib/python3.11/concurrent/futures/_base.py", line 449, in result
    |     return self.__get_result()
    |            ^^^^^^^^^^^^^^^^^^^
    |   File "/opt/hostedtoolcache/Python/3.11.13/x64/lib/python3.11/concurrent/futures/_base.py", line 401, in __get_result
    |     raise self._exception
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/tenacity/asyncio/__init__.py", line 114, in __call__
    |     result = await fn(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/model_interfaces/retryable_model.py", line 55, in wrapper_with_action
    |     result = await func(self, *args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/general_llm.py", line 223, in _invoke_with_request_cost_time_and_token_limits_and_retry
    |     direct_call_response = await self._mockable_direct_call_to_model(prompt)
    |                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/ai_models/general_llm.py", line 244, in _mockable_direct_call_to_model
    |     response = await acompletion(
    |                ^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/utils.py", line 1586, in wrapper_async
    |     raise e
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/utils.py", line 1437, in wrapper_async
    |     result = await original_function(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/main.py", line 560, in acompletion
    |     raise exception_type(
    |           ^^^^^^^^^^^^^^^
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/litellm_core_utils/exception_mapping_utils.py", line 2301, in exception_type
    |     raise e
    |   File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/litellm/litellm_core_utils/exception_mapping_utils.py", line 391, in exception_type
    |     raise BadRequestError(
    | litellm.exceptions.BadRequestError: litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys.
    +------------------------------------

Traceback (most recent call last):
  File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/main.py", line 696, in <module>
    template_bot.log_report_summary(forecast_reports)
  File "/home/runner/work/guillotine-forecasting/guillotine-forecasting/.venv/lib/python3.11/site-packages/forecasting_tools/forecast_bots/forecast_bot.py", line 762, in log_report_summary
    raise RuntimeError(
RuntimeError: 1 errors occurred while forecasting: [ExceptionGroup('Error while processing question url: \'https://www.metaculus.com/questions/39397\': All 1 research reports/predictions failed: Errors: ["BadRequestError: litellm.BadRequestError: OpenAIException - You didn\'t provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you\'re accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys."]', (litellm.BadRequestError: OpenAIException - You didn't provide an API key. You need to provide your API key in an Authorization header using *** (i.e. Authorization: *** or as the password field (with blank username) if you're accessing the API from your browser and are prompted for a username and password. You can obtain an API key from https://platform.openai.com/account/api-keys.,))]
2025-09-10 23:43:21,413 - openai.agents - WARNING - OPENAI_API_KEY is not set, skipping trace export
Error: Process completed with exit code 1.