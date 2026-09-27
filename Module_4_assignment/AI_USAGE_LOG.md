# AI Usage Log

How AI was used on the Module 4 prompt optimization assignment. Newest entries are at the bottom.

## 2026-09-22 — Module 4 AI usage log and Cursor rule

- **Prompt:** Change the rules so we are creating a new AI_USAGE_LOG for Module 4 assignment and update it whenever we work on the module 4 assignment.
- **AI response summary:** Updated `.cursor/rules/ai-usage-log.mdc` to route logs by assignment module (Module 3 → `Module_3_assignment/AI_USAGE_LOG.md`, Module 4 → `Module_4_assignment/AI_USAGE_LOG.md`). Created this file with the standard entry format.
- **Accepted / changed / rejected:** Accepted dual-module routing in the Cursor rule. Module 3 log and `project-spec.mdc` left unchanged.
- **Issues found:** None

## 2026-09-26 — Local dataset CSV paths

- **Prompt:** Update the file paths to `gold_dataset_path = "gold_reviews.csv"` and `test_dataset_path = "test_reviews.csv"`.
- **AI response summary:** Replaced Colab `/content/...` paths in `Prompt_Optimization_and_Evaluation.ipynb` (active and commented cells) with local filenames in the assignment directory.
- **Accepted / changed / rejected:** Accepted as requested; backup notebook and checkpoint not changed.
- **Issues found:** None

## 2026-09-26 — Task 1: no notebook outputs diagnosis

- **Prompt:** Run the notebook end-to-end; help understand what changed and why there are no outputs.
- **AI response summary:** Compared git diff and `config.json` to the config-loading cell; explained cleared saved outputs vs. config key mismatch (`api_key`/`base_url`/`model` vs `API_KEY`/`OPENAI_API_BASE`) and hardcoded `gpt-4o-mini` in `llm_response` / DSPy.
- **Accepted / changed / rejected:** Explanation only; no notebook code changes in this turn.
- **Issues found:** `config.json` is not in git HEAD; local Gemini config does not match notebook loader field names.

## 2026-09-26 — Gemini config format vs notebook

- **Prompt:** Using Gemini; does the project allow it; is `config.json` format correct; what should change?
- **AI response summary:** Explained OpenAI-compatible Gemini endpoint works with the notebook architecture after loader/model wiring; `api_key`/`base_url`/`model` keys are fine but ipynb still expects `API_KEY`/`OPENAI_API_BASE` and hardcodes `gpt-4o-mini`.
- **Accepted / changed / rejected:** Guidance only; no code changes in this turn.
- **Issues found:** Empty `api_key` in editor will block all LLM calls until restored.

## 2026-09-26 — Option B Gemini wiring in notebook

- **Prompt:** Use option B to fix config loading and model wiring for Gemini.
- **AI response summary:** Updated `Prompt_Optimization_and_Evaluation.ipynb` to read `api_key`/`base_url`/`model` (with legacy key fallback), set `MODEL` and `REFLECTION_MODEL`, use `MODEL` in `llm_response`, f-string prompt YAML, and DSPy `openai/{MODEL}` LMs.
- **Accepted / changed / rejected:** Applied to main notebook only; `config.json` left to user (gitignored).
- **Issues found:** User must populate `api_key` in `config.json` before running.

## 2026-09-26 — TESTING_MODE (1 gold + 1 test, real calls)

- **Prompt:** Change testing mode to run all steps once without x12/x8 repetition; 1 gold and 1 test only.
- **AI response summary:** Removed stub/skip logic; kept `workflow_records()` limit; naive/GEPA/DSPy/judges run for real on one row each; GEPA uses `max_metric_calls=20` in testing mode vs `auto=light` in production.
- **Accepted / changed / rejected:** Applied to main notebook.
- **Issues found:** None

- **Prompt:** How many requests do we need to run this project?
- **AI response summary:** Counted per-phase `llm_response` and DSPy/GEPA calls from notebook structure (gold=12, test=8, GEPA `auto="light"` ≈428 metric calls); explained free-tier rate limits.
- **Accepted / changed / rejected:** Explanation only.
- **Issues found:** GEPA reflection LM adds extra calls beyond the metric budget (approximate).

## 2026-09-26 — API rate limit 50 RPM

- **Prompt:** Limit API calls to 50 per minute in test and real modes.
- **AI response summary:** Added `max_requests_per_minute` in config; rolling-window rate limiter in `llm_response` and patched `litellm.completion` for DSPy/GEPA.
- **Accepted / changed / rejected:** Applied.
- **Issues found:** None
