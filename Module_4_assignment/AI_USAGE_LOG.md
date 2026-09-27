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
