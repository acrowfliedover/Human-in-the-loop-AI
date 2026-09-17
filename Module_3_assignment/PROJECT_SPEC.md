# Cloud Kitchen Inventory Simulation — Project Spec

## What we are building

A Python simulation of a multi-brand cloud kitchen for one operational day. Shared inventory is consumed from recipes when orders are processed. The kitchen must avoid silent stockouts, track expiry-driven waste, and produce a restock list for the next day.

Why it matters: after aggregator commissions, packaging, labor, and food cost, contribution margins are often only 5–15%. Stockouts lose sales and ranking; expired stock wastes food cost.

## Current components and status

| Component | File | Status |
|---|---|---|
| Seed tables (Recipes, Inventory, Orders, Restock, Status) | `seed_data.py` (copied from `seed_data-1.py`) | Complete |
| Data loaders and console printers | `main.py` | Complete (Task 1) |
| Order → recipe lookup and ingredient demand | `main.py` | Complete (Task 2) |
| Fulfillment, status updates, inventory deduction | `main.py` | Complete (Task 3) |
| Cumulative deduction across sequential orders | `main.py` | Complete (Task 4) |
| Restock rules from final inventory | `main.py` | Complete (Task 5) |
| Unit tests | `test_main.py` | Complete for Tasks 1–5 |
| Python environment | `.venv` | Created (Python 3.14) |
| AI usage log | `AI_USAGE_LOG.md` | Active |
| Enhancements (partial fulfillment, stockout alerts, item disabling) | — | Not started |

## Important design decisions

- All brands consume one shared in-memory inventory.
- Recipe lookup is exact name match between `Orders.item` and `Recipes.name`.
- Ingredient quantities are grams for every item, including buns.
- An order is all-or-nothing: no partial item fulfillment yet.
- Inventory is deducted only when the full order can be fulfilled.
- Orders are processed against a working deep copy; the printed inventory is updated only after the full order list is processed.
- Live restock is rebuilt from **final** inventory after all orders, not from intermediate shortages.
- Default simulation “today” is `date.today()` unless a caller passes `reference_date`. Tests use `2026-06-03`.

## Business rules

1. **Expiring soon:** if `0 <= days_until_expiry <= 5`, restock `10,000g` with reason `Expiring soon`. This rule wins over stock-level rules.
2. **Out of stock:** if final quantity is `0`, restock `10,000g` with reason `Out of stock`.
3. **Running low:** if final quantity is `<= 1,000g` (and not zero), request `10,000 - current` grams with reason `Running low on stock`.
4. Adequate stock with no near-expiry flag is omitted from restock.
5. Missing recipes do not crash the run; the order is not delivered and the missing item names are recorded.

## Constraints

- Keep the code simple. Prefer Python standard library only.
- Implement one assignment task per prompt; do not bundle later enhancements into earlier tasks.
- Do not change previously completed function behavior unless the current task requires it.
- `main.py` holds application logic. `test_main.py` is the verification suite. Re-run **all** tests after a fix, not only the failing case.
- After every implementation, add validation-hook comments for assumptions, uncertain parts, and incomplete follow-up.
- Restock threshold (`1,000g`), par level (`10,000g`), and expiry window (`5` days) are business constants, not one-off magic unique to a single ingredient.

## Current task and next task

- **Current task:** Setup is done. Tasks 1–5 pass (`20` tests OK under `.venv`).
- **Next task:** Choose the next course step — Enhancement 1 (partial fulfillment), Enhancement 2 (predictive stockout alerts), or Enhancement 3 (dynamic item disabling).

## Known issues or assumptions

- `main.py` imports `seed_data`. The course file arrived as `seed_data-1.py`; a copy named `seed_data.py` is used at runtime.
- Expired inventory (`days_until_expiry < 0`) is **not** flagged as `Expiring soon`. Fulfillment also does not block expired ingredients; expiry is only used in restock.
- The course design notes mention periodic restock every N orders and multi-reason flags on one ingredient. The implemented Task 5 path uses a single winning reason and rebuilds restock once at the end.
- Seed `restock` and `status` tables are baseline data. Live restock starts empty and is recalculated; status rows are updated or appended during processing.
- `date.today()` will change restock output for real `main.py` runs as the calendar moves; tests pin `reference_date`.
