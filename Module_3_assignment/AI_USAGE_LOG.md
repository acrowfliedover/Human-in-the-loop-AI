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

## 2026-09-20 — Task 3: Audit data loading and seed data

- **Prompt:** Task 3: Audit Data Loading and Seed Data — inspect existing loading and display functions, verify access to all five data structures (Recipes, Inventory, Orders, Restock, Status), modify only if needed, run tests and add/update tests for presence, types, records, and key fields.
- **AI response summary:** Audited `load_*()` and `print_*()` in `main.py` and all records in `seed_data.py`; no loader, printer, or seed defects found. Ran baseline suite (20 tests, all pass). Added `test_loaders_return_seed_module_lists` and `test_all_records_have_required_key_fields` to `TestLoadFunctions`. Full suite now 22 tests, all pass. Updated `PROJECT_SPEC.md` (Task 3 complete, test class name aligned).
- **Accepted / changed / rejected:** Accepted existing loader/printer behavior unchanged. Accepted two new tests only. Rejected `main()` changes to load/display seed Restock at runtime (loaders verified via unit tests instead).
- **Issues found:** None; audit passed without code fixes to `main.py` or `seed_data.py`.

## 2026-09-20 — Task 4: Audit recipe lookup and ingredient calculation

- **Prompt:** Task 4: Audit Recipe Lookup and Ingredient Calculation — inspect existing functions, modify only if necessary, run tests and add/update tests for valid item, invalid item, and quantity greater than 1.
- **AI response summary:** Audited `find_recipe_by_name`, `calculate_ingredient_requirements`, and the missing-recipe path in `process_orders`; no `main.py` changes needed. Ran full suite (22 baseline tests pass). Added `test_valid_item_returns_scaled_ingredients_at_quantity_one` and `test_process_orders_rejects_order_with_missing_recipe` to `TestOrderRecipeLookup`. Full suite now 24 tests, all pass. Updated `PROJECT_SPEC.md` Task 4 status.
- **Accepted / changed / rejected:** Accepted split API (`find_recipe_by_name` + `calculate_ingredient_requirements`); rejected unified wrapper. Accepted two new tests only; no production code changes.
- **Issues found:** None; audit passed without fixes to `main.py`.

## 2026-09-20 — Task 5: Complete inventory availability check

- **Prompt:** Task 5: Complete the Inventory Availability Check — compare required ingredients against stock, identify missing/insufficient/expired ingredients, run tests and add coverage for all four scenarios.
- **AI response summary:** Added `parse_expiry_date`, `days_until_expiry`, `is_ingredient_usable`, and `format_unavailable_ingredient` to `main.py`. Extended `check_inventory_availability()` with `reference_date`, `unavailability_reason`, and expiry metadata. Wired `reference_date` through `process_orders()` and appended `(expired)` to failure remarks. Added `TestInventoryAvailabilityCheck` (4 tests) and `test_process_orders_rejects_expired_ingredient`. Updated existing fulfillment/cumulative tests to pass `reference_date` and fix expired seed ingredients in fixtures. Full suite: 29 tests pass.
- **Accepted / changed / rejected:** Accepted plan-aligned implementation. Accepted minimal test fixture updates where seed expiry dates blocked quantity-only scenarios. Rejected rewriting restock or summary logic (out of scope).
- **Issues found:** Seed inventory contains ingredients expired at the test reference date (`2026-06-03`); fulfillment tests that use seed data now set usable expiry dates on required ingredients in deepcopy fixtures.

## 2026-09-20 — Task 6: Audit and complete fulfillment logic

- **Prompt:** Task 6: Audit and Complete Fulfillment Logic — inspect order-processing and fulfillment logic, modify only as needed so delivered orders deduct inventory and failed orders record reasons and surface restock via final rebuild; run tests and add/update coverage for successful delivery, failed delivery, correct deduction, and no deduction on failure.
- **AI response summary:** Ran baseline suite (29 tests, all pass). Audited `process_orders`, `deduct_inventory`, and `update_status_entry` against Task 6 checklist; no `main.py` changes required. Added `test_process_orders_does_not_deduct_inventory_when_stock_insufficient` to `TestOrderFulfillment`. Full suite now 30 tests, all pass. Updated `PROJECT_SPEC.md` Task 6 status and test count.
- **Accepted / changed / rejected:** Accepted existing fulfillment branches unchanged. Accepted one new test only. Rejected per-order restock append (user confirmed final-inventory rebuild design).
- **Issues found:** None; audit passed without production code changes.

## 2026-09-20 — Task 7: Audit cumulative order processing

- **Prompt:** Task 7: Implement Cumulative Order Processing — process all orders in sequence so each order uses inventory remaining after previous delivered orders; unit tests for two orders sharing an ingredient, later-order failure after stock exhaustion, and final inventory matching expected values.
- **AI response summary:** Audited `process_orders()`, `deduct_inventory()`, and `apply_final_inventory_snapshot()` against the Task 7 checklist; cumulative flow already implemented via `working_inventory` deep copy with deduct-only-on-success. Ran `TestCumulativeInventoryDeduction` (3/3 pass) and full suite (30/30 pass). No `main.py` or `test_main.py` changes required. Updated `PROJECT_SPEC.md` Task 7 / Req 5 verification status and current/next task.
- **Accepted / changed / rejected:** Accepted existing cumulative implementation unchanged. Rejected rewriting `process_orders()` loop or duplicating existing tests. No production or test code changes.
- **Issues found:** None; audit passed without code changes.

## 2026-09-20 — Task 8: Restock and expiry rules

- **Prompt:** Task 8: Implement Restock and Expiry Rules — multi-reason restock recommendations for out-of-stock, low-stock, and expiring-soon ingredients; unit tests for zero stock, threshold boundaries, expiring soon, and multiple reasons.
- **AI response summary:** Added `PAR_LEVEL_G`, `LOW_STOCK_THRESHOLD_G`, `EXPIRING_SOON_DAYS` constants. Implemented `build_restock_reasons()` and `calculate_restock_qty_needed()`. Refactored `calculate_restock_needs()` to output enriched rows with `reasons` list, `current_qty_grams`, `expiry_date`, and `days_until_expiry`. Updated `print_restock()` for new shape. Extended `TestRestockRules` from 4 to 12 tests (boundary and multi-reason cases). Updated fulfillment/cumulative tests for `reasons` field. Full suite: 38 tests pass.
- **Accepted / changed / rejected:** Accepted `reasons` list shape per architecture plan. Accepted max-quantity logic across applicable rules. Rejected changes to fulfillment, cumulative deduction, or inventory availability logic.
- **Issues found:** None.

## 2026-09-20 — Task 9: Generate final business summary

- **Prompt:** Task 9: Generate Final Business Summary — implement plan for manager-facing end-of-run summary with delivered/not-delivered orders, failure reasons, final inventory, restock recommendations, and expiry concerns (console + dictionary output).
- **AI response summary:** Added `build_inventory_alerts()`, `build_business_summary()`, and `print_business_summary()` to `main.py`. Wired summary into `main()` after existing print sections. Added `TestBusinessSummary` with 9 tests covering counts, failure reasons, inventory snapshot, restock pass-through, expiry alerts, multi-issue rows, empty orders, and seed integration. Updated `PROJECT_SPEC.md` Req 7 status. Full suite: 47 tests pass.
- **Accepted / changed / rejected:** Accepted console + dict output per plan. Accepted separate `build_inventory_alerts()` to flag expired stock not covered by restock rules. Rejected file/Markdown export and changes to fulfillment/restock logic.
- **Issues found:** Seed simulation at `2026-06-03` can produce zero restock rows when final quantities stay above thresholds; integration test asserts structure and expiry concerns rather than requiring non-empty restock.

## 2026-09-20 — Task 10: Refactor and review

- **Prompt:** Task 10: Refactor and Review — review code for duplicate logic, hard-coded values, unclear names, missing comments, weak error handling, and functions that do too much; document at least two improvements made during refactoring.
- **AI response summary:** Refactored `main.py` with shared expiry/date helpers (`EXPIRY_DATE_FORMAT`, `_resolve_reference_date`, `_inventory_expiry_days`), hardened `parse_expiry_date` to return `None` on invalid input, split `process_orders` into `_collect_order_item_requirements` and `_apply_order_fulfillment`, added architecture section comments, and added `test_invalid_expiry_date_does_not_crash_availability_check`. Updated `PROJECT_SPEC.md` with Task 10 refactoring notes. Full suite: 48 tests pass.
- **Accepted / changed / rejected:** Accepted both documented improvements (shared helpers and split `process_orders`). Accepted one new test for invalid expiry handling. Rejected merging restock and alert classification (different labels and expired handling by design).
- **Issues found:** None; all existing behavior preserved for valid seed data.

## 2026-09-20 — Verify all assignment requirements

- **Prompt:** Verify all of the requirements are completely satisfied. Show any unsatisfied requirements (required files, core data structures, functional requirements 1–7).
- **AI response summary:** Audited required files, `PROJECT_SPEC.md`, `AI_USAGE_LOG.md`, `main.py`, `seed_data.py`, and `test_main.py`; ran all 48 unit tests (pass). Found three partial gaps: `print_restock()` crashes on seed restock schema; already-expired inventory is not added to restock recommendations (Req 6); ingredients absent from the inventory table are not added to restock on order failure (Req 4).
- **Accepted / changed / rejected:** Accepted verification report only; no code changes.
- **Issues found:** Seed restock uses `reason` (singular) while `print_restock()` expects calculated rows with `reasons`, `current_qty_grams`, and expiry fields; `build_restock_reasons()` only flags 0–5 days until expiry, not already-expired stock with quantity above thresholds.

## 2026-09-20 — Task 1: Fix print_restock() for seed data

- **Prompt:** Fix print_restock() in main.py so it can display both seed restock rows (reason singular, no expiry fields) and calculated restock rows (reasons list, current_qty_grams, expiry fields). Add unit test(s) proving print_restock(load_restock()) does not crash. Update PROJECT_SPEC.md Req 1 status.
- **AI response summary:** Updated `print_restock()` to detect row format via `"reasons" in item` vs seed `"reason"` field; seed rows print N/A for missing fields, calculated rows unchanged. Added `test_print_restock_seed_data_does_not_crash` and `test_print_restock_calculated_rows` in `TestLoadFunctions`. Updated `PROJECT_SPEC.md` Req 1 acceptance criteria and verification status. Full suite: 50 tests pass.
- **Accepted / changed / rejected:** Accepted minimal per-row format detection approach. Accepted N/A placeholders for seed-only fields.
- **Issues found:** None.

## 2026-09-20 — Task 2: Display seed inventory and restock in main()

- **Prompt:** Update main() to display all five seed tables before order processing (recipes, inventory, orders, seed restock, status). Keep post-processing output as-is. Add a short test or smoke assertion if practical. Update PROJECT_SPEC.md.
- **AI response summary:** Added a startup print section in `main()` before `process_orders()` using `load_inventory()`, `load_restock()`, and `load_status()` so seed rows are not mutated. Moved recipes/orders prints to that section; kept post-processing inventory, calculated restock, updated status, and business summary. Added `test_main_displays_seed_tables_before_processing`. Updated `PROJECT_SPEC.md` Req 1, component status, and current task.
- **Accepted / changed / rejected:** Accepted startup display of all five tables including seed status. Recipes and orders now print once at startup rather than after processing (same unmutated content).
- **Issues found:** None.

## 2026-09-20 — Task 3: Flag already-expired inventory for restock

- **Prompt:** Fix restock rules so already-expired ingredients are included in restock recommendations with reason Expired, restocked to par (10,000 g). Update build_restock_reasons() and calculate_restock_qty_needed() in main.py. Add unit test(s) for expired stock with quantity above 1,000 g. Update PROJECT_SPEC.md business rules.
- **AI response summary:** Updated `build_restock_reasons()` to append `Expired` when `days_left is None or days_left < 0`. Updated `calculate_restock_qty_needed()` to treat `Expired` like `Expiring soon` / `Out of stock` (full par). Added `test_expired_stock_above_threshold_restocked_to_par` and `test_expired_and_running_low_preserves_both_reasons` in `TestRestockRules`. Updated `PROJECT_SPEC.md` business rules and Req 6 verification. Full suite: 53 tests pass.
- **Accepted / changed / rejected:** Accepted expired vs expiring-soon as mutually exclusive (`elif`); stock rules remain independent. Accepted multi-reason preservation for expired + running low.
- **Issues found:** None.

## 2026-09-20 — Task 4: Add missing-from-inventory ingredients to restock

- **Prompt:** When an order fails because a required ingredient is missing from the inventory table, add that ingredient to the restock list with current quantity 0, reason Missing from inventory, and qty needed to par (10,000 g). Keep all-or-nothing fulfillment and final-inventory restock rebuild. Add unit test(s). Update PROJECT_SPEC.md known issues.
- **AI response summary:** After `refresh_restock_table()` in `process_orders()`, merge unique missing-from-table ingredient names (`unavailability_reason == "missing"`) into restock. Added `_collect_missing_from_inventory_names()` and `_merge_missing_ingredients_into_restock()`. Added `test_process_orders_adds_missing_from_inventory_ingredient_to_restock` (Ghost Pepper). Updated Req 4, design decisions, current/next task, and known issues. Full suite: 54 tests pass.
- **Accepted / changed / rejected:** Accepted post-rebuild merge so Req 6 inventory restock stays unchanged. Did not add missing ingredients into inventory or deduct on failure. Existing Bun 0 g test remains `Out of stock`.
- **Issues found:** None.

## 2026-09-20 — Code quality audit implementation

- **Prompt:** Implement the code quality audit plan: extract shared stock/expiry evaluator, promote string constants, deduplicate business summary output, and harden edge cases (deduct_inventory guards, empty orders).
- **AI response summary:** Added `_evaluate_stock_expiry_issues()` and reason/unavailability/remark constants in `main.py`. Unified alert and restock labels to `"Running low on stock"`. Removed `failed_orders` key and duplicate print section from business summary. Guarded `deduct_inventory()` against missing keys and negative quantities; empty orders reject with `REMARK_EMPTY_ORDER`. Cached expiry days in availability check. Updated `test_main.py` with `TEST_REFERENCE_DATE`, constant imports, and `test_process_orders_rejects_empty_order`. Updated `PROJECT_SPEC.md`. Full suite: 55 tests pass.
- **Accepted / changed / rejected:** Accepted all four audit todos. Did not remove `seed_data-1.py` (not in todo list).
- **Issues found:** None.
