# Cloud Kitchen Inventory Simulation — Project Spec

## What does the project do?

This project is a **Python console simulation** of one operational day at a **multi-brand cloud kitchen**. All brands share a single in-memory inventory. The program:

1. **Loads** seed data for recipes, inventory, orders, restock records, and delivery status.
2. **Processes every order in sequence** by looking up recipes, calculating ingredient demand, and checking whether shared inventory can fulfill the order.
3. **Fulfills or rejects each order** using all-or-nothing rules: delivered orders deduct inventory; failed orders deduct nothing.
4. **Tracks cumulative inventory** so each later order is checked against stock remaining after earlier delivered orders.
5. **Rebuilds restock recommendations** from final inventory using stock-level and expiry rules.
6. **Prints results** — per-order processing detail, updated inventory, restock list, delivery status, and an end-of-run summary understandable to a kitchen manager.

The simulation answers one practical question: *Given today’s orders and current stock, what can we deliver, what stock remains, and what must we reorder?*

---

## Who uses it?

| User | How they use it | What they need from it |
|---|---|---|
| **Kitchen / operations manager** | Reads the printed end-of-run summary and restock list | Clear counts of delivered vs failed orders, remaining stock, and what to reorder — without reading code |
| **Inventory or procurement staff** | Uses restock output to plan next-day purchasing | Ingredient name, current quantity, restock reason, quantity needed to reach par, and expiry warnings |
| **Student / developer (assignment)** | Runs `main.py`, maintains `main.py` logic, verifies with `test_main.py` | Correct fulfillment behavior, cumulative deduction, and reproducible restock rules |
| **Instructor / grader** | Runs tests and inspects console output against functional requirements | Deterministic behavior when `reference_date` is set; no crashes on missing recipes |

This is **not** a customer-facing ordering app, a live POS integration, or a production inventory system.

---

## What does this project NOT do?

The following are **explicitly out of scope** for the base assignment. Do not assume they exist unless listed as an optional enhancement.

| Out of scope | Detail |
|---|---|
| **Partial order fulfillment** | If any item or ingredient fails, the **entire order** is not delivered. No item-level or ingredient-level partial deduction. |
| **Persistence** | No database, file save, or API. All tables live in memory for one run. Seed data is not written back to disk. |
| **Real-time or external integrations** | No connection to delivery apps, POS systems, suppliers, or notifications. |
| **Recipe intelligence** | No fuzzy matching, aliases, substitutions, or brand-specific recipe variants. Lookup is **exact name match** only. |
| **Inventory reset between orders** | Within one simulation run, inventory is **not** reset between orders. Each order sees cumulative deductions from prior delivered orders. |
| **Periodic mid-run restock** | Restock is calculated **once** from final inventory after all orders are processed, not after every N orders. |
| **Predictive stockout alerts** | Optional enhancement only — not part of the base requirements. |
| **Dynamic menu disabling** | Optional enhancement only — not part of the base requirements. |
| **Web or GUI interface** | Console output only. |
| **Multi-location inventory** | One kitchen, one shared inventory pool. |
| **Financial reporting** | No revenue, food-cost, or margin calculations in the base program. |

---

## Functional requirements

Each requirement below is mandatory for the **final** program. Verify against existing code and tests before changing working behavior.

### Requirement 1: Load and Display Data

**Must do:**

- Load and display all five data structures from `seed_data.py`:
  - Recipes
  - Inventory
  - Orders
  - Restock records
  - Delivery status records
- Use existing loader and printer functions in `main.py` unless a change is required to meet this requirement.

**Acceptance criteria:**

- `load_recipes()`, `load_inventory()`, `load_orders()`, `load_restock()`, and `load_status()` each return the corresponding seed table.
- Printer functions output human-readable console tables for each structure.
- `print_restock()` accepts both seed rows (`reason` singular) and calculated rows (`reasons` list with expiry fields) without crashing.
- `main()` displays all five seed tables before order processing, using unmutated loader results for inventory, restock, and status.
- Tests in `TestLoadFunctions` confirm record counts, key field types, required keys on every record, correct seed wiring, restock printing for both row shapes, and startup display in `main()`.

**Verification status:** **Complete.** Task 1: `print_restock()` detects row format per item (`reasons` vs `reason`) and prints seed or calculated fields accordingly. Task 2: `main()` prints all five seed tables (recipes, inventory, orders, seed restock, status) before `process_orders()`, then keeps post-processing inventory, calculated restock, updated status, and the business summary. `TestLoadFunctions` includes `test_print_restock_seed_data_does_not_crash`, `test_print_restock_calculated_rows`, and `test_main_displays_seed_tables_before_processing`.

---

### Requirement 2: Process Orders Against Recipes

**Must do:**

For each order:

- Identify the menu item(s) ordered.
- Look up the corresponding recipe by name.
- Calculate total ingredient quantity required per ingredient.
- Multiply recipe quantities by the ordered item quantity (e.g., qty 2 doubles all ingredient grams).
- Handle missing or unknown recipes **gracefully** (no crash; record the failure).

**Acceptance criteria:**

- `find_recipe_by_name()` returns the matching recipe or `None`.
- `calculate_ingredient_requirements()` scales `qty_grams` by order item `qty`.
- `combine_requirements()` merges duplicate ingredients within one order.
- Missing recipes are recorded; processing continues for the rest of the order list.

**Verification status:** **Complete.** Task 4 audit confirmed `find_recipe_by_name`, `calculate_ingredient_requirements`, and `combine_requirements` meet Req 2 with no code changes. `TestOrderRecipeLookup` (5 tests) passes.

---

### Requirement 3: Check Inventory Availability

**Must do:**

Before fulfilling an order, verify every required ingredient is:

- Present in inventory (by ingredient name).
- Available in sufficient quantity (required vs available grams).
- **Usable** with respect to expiry, when expiry dates exist in inventory data.

**Must return:**

- Whether the **entire order** can be fulfilled.
- If not, clear detail on what is missing, insufficient, expired, or otherwise unavailable.

**Acceptance criteria:**

- `check_inventory_availability()` compares required grams to available grams per ingredient.
- Unavailable ingredients are listed with required and available quantities.
- Expired or unusable stock is treated as unavailable during the check (not only at restock time).

**Verification status:** **Complete.**

- `check_inventory_availability()` classifies missing, insufficient, and expired ingredients with `unavailability_reason` and expiry metadata in each detail row.
- `process_orders()` passes `reference_date` into the availability check; expired stock blocks delivery.
- `TestInventoryAvailabilityCheck` (4 tests) and `test_process_orders_rejects_expired_ingredient` in `TestOrderFulfillment` verify all scenarios.

---

### Requirement 4: Fulfill Orders and Deduct Inventory

**Must do:**

**When all required ingredients are available and usable:**

- Mark the order as **Delivered**.
- Deduct used ingredient quantities from inventory.

**When any required ingredient is missing, insufficient, expired, or otherwise unavailable:**

- Mark the order as **Not Delivered**.
- Record the reason in the status table.
- Add missing or unavailable ingredients to the restock list (via final restock rebuild per Requirement 6).

**Rules:**

- **All-or-nothing fulfillment:** a failed order must **not** deduct partial inventory.
- Partial fulfillment is an **optional enhancement only**.

**Acceptance criteria:**

- `process_orders()` sets `delivered` True/False and writes `remark` via `update_status_entry()`.
- `deduct_inventory()` runs only after a successful full-order check.
- Failed orders leave working inventory unchanged for that order.
- Ingredients with `unavailability_reason == "missing"` (absent from the inventory table) are merged into restock after the final-inventory rebuild, with current quantity 0, reason `Missing from inventory`, and quantity needed to par.

**Verification status:** **Complete.** Task 6 audit confirmed fulfillment branches. Task 4 gap: missing-from-inventory names are collected from availability details and merged after `refresh_restock_table()`. `TestOrderFulfillment` (6 tests) covers delivered, failed (out-of-stock, missing-from-table, expired, insufficient), correct deduction, and no deduction on failure.

---

### Requirement 5: Make Inventory Deduction Cumulative

**Must do:**

- Order 1 consumes inventory.
- Order 2 is checked against inventory **after** Order 1.
- Order 3 is checked against inventory **after** Orders 1 and 2.
- Final inventory reflects **all** delivered orders in sequence.
- Do **not** reset inventory between orders within the same run (except isolated test fixtures).

**Acceptance criteria:**

- `process_orders()` uses a `working_inventory` deep copy that persists deductions across the order loop.
- `apply_final_inventory_snapshot()` writes cumulative results back once after all orders.
- Tests confirm shared-ingredient consumption and later-order failure when stock is exhausted.

**Verification status:** **Complete.** Task 7 audit confirmed `process_orders()` uses a persistent `working_inventory` deep copy, deducts only on successful delivery, and writes cumulative results via `apply_final_inventory_snapshot()`. `TestCumulativeInventoryDeduction` (3 tests) passes; no `main.py` changes required.

---

### Requirement 6: Apply Restock and Expiry Rules

**Must do:**

After all orders are processed, identify ingredients that meet **any** of:

- Out of stock (quantity = 0 g).
- Running low (quantity ≤ 1,000 g and > 0 g).
- Expired or expiring soon (within 5 days of the simulation reference date).

**Default business constants** (unless instructor specifies otherwise):

| Constant | Value |
|---|---|
| Running low threshold | ≤ 1,000 g |
| Par level | 10,000 g |
| Expiring soon window | 0–5 days from reference date (inclusive) |
| Test reference date | `2026-06-03` (for reproducible unit tests) |
| Runtime default reference date | `date.today()` when caller omits `reference_date` |

**Restock output must include:**

- Ingredient name
- Current quantity
- Reason for restock
- Quantity needed to reach par level
- Relevant expiry information when applicable

**Multi-reason rule:** If an ingredient qualifies for more than one reason, **preserve all relevant reasons** — do not silently overwrite with a single reason.

**Acceptance criteria:**

- `calculate_restock_needs()` and `refresh_restock_table()` run after all orders.
- Restock is rebuilt from **final** inventory, not intermediate per-order shortages.
- Unit tests cover expiring soon, out of stock, running low, and adequate stock.

**Verification status:** **Complete.**

- `build_restock_reasons()` evaluates expired, expiring soon, out of stock, and running low with independent checks (no `elif` priority between stock rules; expired vs expiring soon are mutually exclusive).
- `calculate_restock_needs()` outputs enriched rows: `current_qty_grams`, `reasons` (list), `qty_needed_grams`, `expiry_date`, `days_until_expiry`.
- Multi-reason preservation and max-quantity logic verified in `TestRestockRules` (14 tests), including already-expired stock above the running-low threshold.

---

### Requirement 7: Produce a Business-Friendly Summary

**Must do:**

At the end of the simulation, produce a clear summary that includes:

- Number of orders delivered
- Number of orders not delivered
- Final inventory levels
- Restock recommendations
- Ingredients that are low, out of stock, expired, or expiring soon
- Orders that could not be fulfilled and **why**

The summary must be understandable to a **non-technical kitchen manager** (plain language, counts, and short explanations — not raw debug structures).

**Acceptance criteria:**

- A dedicated summary section (function or formatted block) appears after processing.
- Manager can answer: “How many orders succeeded?”, “What’s left on the shelf?”, “What do I need to buy?”, and “Why did order X fail?” without reading Python objects.

**Verification status:** **Complete.**

- `build_business_summary()` returns a structured dictionary with delivered/not-delivered counts, order lists, failure reasons, final inventory, restock recommendations, inventory alerts, and expiry concerns.
- `print_business_summary()` prints a plain-language `=== Business Summary ===` section after processing.
- `build_inventory_alerts()` flags expired, expiring-soon, out-of-stock, and running-low ingredients from final inventory (including expired stock not covered by restock rules).
- `main()` calls both functions after existing technical print sections.
- `TestBusinessSummary` (9 tests) verifies counts, failure reasons, inventory snapshot, restock pass-through, expiry alerts, multi-issue rows, empty orders, and seed integration.

---

## Component status

| Component | File | Status |
|---|---|---|
| Seed tables (Recipes, Inventory, Orders, Restock, Status) | `seed_data.py` (from `seed_data-1.py`) | Complete |
| Data loaders and console printers | `main.py` | Complete (Req 1; `print_restock` dual-format; `main()` seed display) |
| Order → recipe lookup and ingredient demand | `main.py` | Complete (Req 2) |
| Inventory availability check | `main.py` | Complete (Req 3) |
| Fulfillment, status updates, inventory deduction | `main.py` | Complete (Req 4; missing-from-inventory restock merge) |
| Cumulative deduction across sequential orders | `main.py` | Complete (Req 5) |
| Restock rules from final inventory | `main.py` | Complete (Req 6) |
| Business-friendly end-of-run summary | `main.py` | Complete (Req 7) |
| Unit tests | `test_main.py` | 54 tests pass (12 in `TestLoadFunctions` for Req 1 / Tasks 1–2) |
| Refactor and review | `main.py` | Complete (Task 10) |
| Python environment | `.venv` | Optional; system Python also runs tests |
| AI usage log | `AI_USAGE_LOG.md` | Active |

---

## Design decisions

- All brands consume **one shared in-memory inventory**.
- Recipe lookup is **exact name match** between `Orders.item` and `Recipes.name`.
- Ingredient quantities are **grams** for every item, including buns.
- An order is **all-or-nothing**: no partial item fulfillment in the base assignment.
- Inventory is deducted **only** when the full order can be fulfilled.
- Orders are processed against a **working deep copy**; the main inventory table is updated once after the full order list completes.
- Live restock is **rebuilt from final inventory** after all orders, not from intermediate shortages. Ingredients absent from the inventory table (`unavailability_reason == "missing"`) are then **merged** into that restock list (deduped by item name).
- Default simulation “today” is `date.today()` unless the caller passes `reference_date`. Tests use `2026-06-03`.
- `main()` prints seed tables from loaders before processing (unmutated inventory, restock, and status). Post-processing prints use working copies: deducted inventory, rebuilt restock, and updated status.

---

## Business rules (restock)

1. **Expired:** if `days_until_expiry` is negative or the expiry date is invalid/missing, restock to par (`10,000 g`) with reason `Expired`.
2. **Expiring soon:** if `0 <= days_until_expiry <= 5`, restock to par (`10,000 g`) with reason `Expiring soon`.
3. **Out of stock:** if final quantity is `0`, restock `10,000 g` with reason `Out of stock`.
4. **Running low:** if final quantity is `<= 1,000 g` (and not zero), request `10,000 - current` grams with reason `Running low on stock`.
5. Adequate stock with no expiry issue is **omitted** from restock.
6. Missing recipes do **not** crash the run; the order is not delivered and missing item names are recorded in the status remark.

**Target behavior (Requirement 6):** when multiple rules apply, output must list **all** applicable reasons, not only the highest-priority one.

---

## Architecture

Implementation plan (components, `main.py` section layout, build order, and test plan): see `ARCHITECTURE_PLAN.md`.

All application logic stays in `main.py`. All tests stay in `test_main.py`. No additional Python modules.

---

## Constraints

- Keep the code simple. Prefer Python standard library only.
- `main.py` holds application logic. `test_main.py` is the verification suite. Re-run **all** tests after a change, not only the failing case.
- Do not change previously completed function behavior unless the current task requires it.
- Restock threshold (`1,000 g`), par level (`10,000 g`), and expiry window (`5` days) are business constants shared across ingredients.
- After implementation changes, add validation-hook comments for assumptions, uncertain parts, and incomplete follow-up.

---

## Current task and next task

- **Current task:** Task 4 complete — ingredients missing from the inventory table are added to restock with reason `Missing from inventory` and quantity needed to par.
- **Next task:** Optional enhancements.

---

## Refactoring improvements (Task 10)

1. **Shared expiry/date helpers** — Added `EXPIRY_DATE_FORMAT`, `_resolve_reference_date()`, and `_inventory_expiry_days()` so restock, alerts, usability, and availability checks no longer repeat `date.today()` defaults and expiry parsing. `parse_expiry_date()` now returns `None` on invalid input instead of raising, so bad dates mark stock as expired rather than crashing the simulation.

2. **Split `process_orders`** — Extracted `_collect_order_item_requirements()` and `_apply_order_fulfillment()` so the orchestrator only manages the working-inventory loop, snapshot, and restock refresh. Duplicated item-row dicts and the `"Missing or insufficient ingredients"` remark string were collapsed into these helpers.

---

## Known issues or assumptions

- `main.py` imports `seed_data`. The course file arrived as `seed_data-1.py`; a copy named `seed_data.py` is used at runtime.
- **Summary:** manager-facing output is provided by `build_business_summary()` / `print_business_summary()`; technical detail remains in separate print sections.
- Calculated restock rows use `reasons` (list); seed `restock` table in `seed_data.py` still uses singular `reason` for loader tests. `print_restock()` supports both shapes.
- Seed `restock` and `status` tables are baseline data shown at startup. Live restock starts empty and is recalculated after processing; status rows are updated or appended during processing.
- **Restock on failure:** ingredients that exist in inventory still restock only via final-inventory rules (out of stock, running low, expiry). Ingredients with `unavailability_reason == "missing"` are merged after that rebuild: current quantity 0, reason `Missing from inventory`, quantity needed to par (`10,000 g`). Duplicate item names are skipped. Out-of-stock rows that exist in inventory (quantity 0 g) keep reason `Out of stock`, not `Missing from inventory`.
- `date.today()` changes restock output for real `main.py` runs as the calendar moves; tests pin `reference_date` to `2026-06-03`.
