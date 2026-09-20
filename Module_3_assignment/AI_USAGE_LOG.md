# AI Usage Log

How AI was used on the Module 3 cloud kitchen assignment. Newest entries are at the bottom.

## 2026-09-17 — Project setup (venv, Cursor rules, spec, usage log)

- **Prompt:** In `Module_3_assignment`, set up a new Python environment and Cursor rules that save chat history to `AI_USAGE_LOG.md`. For each major interaction, record the task, the prompt, a short summary of the AI response, what was accepted/changed/rejected, and issues found. The project should use `main.py` for functionality, `test_main.py` for tests, and `PROJECT_SPEC.md` as external memory (what we are building, component status, design decisions, business rules, constraints, current/next task, known issues).
- **AI response summary:** Created `Module_3_assignment/.venv` (Python 3.14), copied `seed_data-1.py` to `seed_data.py`, added always-on Cursor rules for the usage log and project spec, and wrote `PROJECT_SPEC.md` plus this log. Did not rewrite `main.py` or `test_main.py`.
- **Accepted / changed / rejected:** Accepted the existing Task 1–5 `main.py` and `test_main.py` as-is. Added `seed_data.py` so `from seed_data import ...` works. Did not add third-party packages.
- **Issues found:** First venv attempt failed in the sandbox (`Operation not permitted` on `.venv/include`) and briefly created an empty repo-root `.venv`; retried with full permissions at `Module_3_assignment/.venv`. The assignment file is named `seed_data-1.py`, which would have broken the `seed_data` import without a copy.

## 2026-09-20 — Rewrite PROJECT_SPEC.md with functional requirements

- **Prompt:** Rewrite `PROJECT_SPEC.md` to include "What does the project do?", "Who uses it", "What does it NOT do?" with no ambiguity, and incorporate all seven official functional requirements (load/display data, process orders against recipes, check inventory, fulfill/deduct, cumulative deduction, restock/expiry rules, business-friendly summary).
- **AI response summary:** Rewrote `PROJECT_SPEC.md` with explicit scope, user personas, out-of-scope table, and detailed Requirement 1–7 sections (must-do, acceptance criteria, verification status). Updated component status and next tasks to reflect gaps: expiry in fulfillment check (Req 3), multi-reason restock (Req 6), and dedicated manager summary (Req 7). Confirmed 20 existing tests still pass.
- **Accepted / changed / rejected:** Accepted the new spec structure and requirement wording. No code changes to `main.py` or `test_main.py`.
- **Issues found:** None in the spec rewrite; documented three implementation gaps vs full functional requirements that remain in code.

## 2026-09-20 — Architecture plan (single main.py)

- **Prompt:** Put the architecture plan in a separate file. Keep all logic in `main.py` and write new tests in `test_main.py` (no extra Python modules).
- **AI response summary:** Created `ARCHITECTURE_PLAN.md` with single-file layout (logical sections inside `main.py`), twelve logical components, data-shape extensions, phased build order (Phases 0–9), pipeline diagram, test class plan (`TestInventoryExpiryCheck`, `TestBusinessSummary`), and completion checklist. Linked from `PROJECT_SPEC.md`.
- **Accepted / changed / rejected:** Accepted single-file constraint; rejected the earlier multi-module split proposal. No code changes yet.
- **Issues found:** None.
