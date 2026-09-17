# AI Usage Log

How AI was used on the Module 3 cloud kitchen assignment. Newest entries are at the bottom.

## 2026-09-17 — Project setup (venv, Cursor rules, spec, usage log)

- **Prompt:** In `Module_3_assignment`, set up a new Python environment and Cursor rules that save chat history to `AI_USAGE_LOG.md`. For each major interaction, record the task, the prompt, a short summary of the AI response, what was accepted/changed/rejected, and issues found. The project should use `main.py` for functionality, `test_main.py` for tests, and `PROJECT_SPEC.md` as external memory (what we are building, component status, design decisions, business rules, constraints, current/next task, known issues).
- **AI response summary:** Created `Module_3_assignment/.venv` (Python 3.14), copied `seed_data-1.py` to `seed_data.py`, added always-on Cursor rules for the usage log and project spec, and wrote `PROJECT_SPEC.md` plus this log. Did not rewrite `main.py` or `test_main.py`.
- **Accepted / changed / rejected:** Accepted the existing Task 1–5 `main.py` and `test_main.py` as-is. Added `seed_data.py` so `from seed_data import ...` works. Did not add third-party packages.
- **Issues found:** First venv attempt failed in the sandbox (`Operation not permitted` on `.venv/include`) and briefly created an empty repo-root `.venv`; retried with full permissions at `Module_3_assignment/.venv`. The assignment file is named `seed_data-1.py`, which would have broken the `seed_data` import without a copy.
