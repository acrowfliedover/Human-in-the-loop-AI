"""Baseline entry point for loading and printing cloud kitchen seed data."""

from copy import deepcopy
from datetime import date, datetime

from seed_data import inventory, orders, recipes, restock, status

PAR_LEVEL_G = 10000
LOW_STOCK_THRESHOLD_G = 1000
EXPIRING_SOON_DAYS = 5


def load_recipes():
    """Return the seeded recipe records for use in the application."""
    # Assumption to verify: importing these module-level lists directly is acceptable
    # for Task 1, and we do not yet need defensive copying or a database/file loader.
    return recipes


def print_recipes(recipe_data):
    """Print every recipe and its ingredient requirements to the console."""
    print("\n=== Recipes ===")
    for recipe in recipe_data:
        print(f"Recipe ID: {recipe['recipe_id']}")
        print(f"Name: {recipe['name']}")
        print("Ingredients:")
        for ingredient in recipe["ingredients"]:
            print(f"  - {ingredient['name']}: {ingredient['qty_grams']} grams")
        print()


def load_inventory():
    """Return the seeded inventory records for the simulation."""
    # Assumption to verify: inventory quantities are intentionally stored in grams
    # for every ingredient, including items like buns that might later use unit counts.
    return inventory


def print_inventory(inventory_data):
    """Print every inventory item with quantity and expiry information."""
    print("\n=== Inventory ===")
    for item in inventory_data:
        print(f"Ingredient: {item['ingredient']}")
        print(f"Quantity: {item['qty_grams']} grams")
        print(f"Expiry Date: {item['expiry_date']}")
        print()


def load_orders():
    """Return the seeded customer order records."""
    # Assumption to verify: order item names are expected to match recipe names exactly.
    return orders


def print_orders(order_data):
    """Print every order, including its brand and requested items."""
    print("\n=== Orders ===")
    for order in order_data:
        print(f"Order ID: {order['order_id']}")
        print(f"Brand: {order['brand']}")
        print("Items:")
        for item in order["items"]:
            print(f"  - {item['item']}: {item['qty']}")
        print()


def load_restock():
    """Return the seeded restock recommendations."""
    # Incomplete / follow-up: the seed table is still available for baseline loading
    # tests, but the live restock output is now recalculated from final inventory.
    return restock


def print_restock(restock_data):
    """Print every restock item with quantity needed and reason."""
    print("\n=== Restock ===")
    for item in restock_data:
        print(f"Item: {item['item']}")
        print(f"Current Quantity: {item['current_qty_grams']} grams")
        print(f"Quantity Needed: {item['qty_needed_grams']} grams")
        print(f"Reasons: {', '.join(item['reasons'])}")
        print(f"Expiry Date: {item['expiry_date']}")
        print(f"Days Until Expiry: {item['days_until_expiry']}")
        print()


def load_status():
    """Return the seeded delivery status records."""
    # Uncertain: it is not yet clear whether status should remain independent seed
    # data or later be derived from order fulfillment results in the simulation.
    return status


def print_status(status_data):
    """Print every order status with delivery result and remark."""
    print("\n=== Status ===")
    for entry in status_data:
        print(f"Order ID: {entry['order_id']}")
        print(f"Delivered: {entry['delivered']}")
        print(f"Remark: {entry['remark']}")
        print()


def find_recipe_by_name(recipe_data, item_name):
    """Return the recipe that matches an order item name, or None if missing."""
    # Step 1: look through the recipe table for a recipe whose name matches
    # the order item exactly so we can determine the required ingredients.
    # Assumption to verify: recipe lookup currently relies on exact name matching
    # between Orders.item and Recipes.name, with no normalization or aliases.
    for recipe in recipe_data:
        if recipe["name"] == item_name:
            return recipe
    # Assumption to verify: case-insensitive matching, trimming, or brand-specific
    # recipe variants are not needed yet for successful recipe lookup.
    return None


def calculate_ingredient_requirements(recipe, quantity):
    """Return the total grams required for each ingredient in an order item."""
    requirements = []

    # Step 2: multiply each recipe ingredient quantity by the ordered item count
    # so we know the total grams needed to prepare that order item.
    for ingredient in recipe["ingredients"]:
        requirements.append(
            {
                "name": ingredient["name"],
                "required_qty_grams": ingredient["qty_grams"] * quantity,
            }
        )

    return requirements


def parse_expiry_date(expiry_str):
    """Parse an inventory expiry string in YYYY-MM-DD format into a date."""
    return datetime.strptime(expiry_str, "%Y-%m-%d").date()


def days_until_expiry(expiry_date, reference_date):
    """Return the number of days from reference_date until expiry_date."""
    return (expiry_date - reference_date).days


def is_ingredient_usable(inventory_item, reference_date):
    """Return whether an inventory item is not expired as of reference_date."""
    if reference_date is None:
        reference_date = date.today()

    expiry_date = parse_expiry_date(inventory_item["expiry_date"])
    if days_until_expiry(expiry_date, reference_date) < 0:
        return False, "expired"

    return True, None


def check_inventory_availability(inventory_data, requirements, reference_date=None):
    """Check whether inventory can fulfill every required ingredient in usable quantity."""
    if reference_date is None:
        reference_date = date.today()

    inventory_lookup = {item["ingredient"]: item for item in inventory_data}
    availability_results = []
    all_available = True

    # Step 3: compare each required ingredient against inventory for presence,
    # expiry usability, and sufficient quantity before fulfillment.
    for requirement in requirements:
        inventory_item = inventory_lookup.get(requirement["name"])
        expiry_date_str = None
        days_remaining = None
        unavailability_reason = None
        is_available = True

        if inventory_item is None:
            available_qty = 0
            is_available = False
            unavailability_reason = "missing"
        else:
            available_qty = inventory_item["qty_grams"]
            expiry_date_str = inventory_item["expiry_date"]
            expiry_date = parse_expiry_date(expiry_date_str)
            days_remaining = days_until_expiry(expiry_date, reference_date)
            ingredient_usable, usability_reason = is_ingredient_usable(
                inventory_item, reference_date
            )

            if not ingredient_usable:
                is_available = False
                unavailability_reason = usability_reason
            elif available_qty < requirement["required_qty_grams"]:
                is_available = False
                unavailability_reason = "insufficient"

        availability_results.append(
            {
                "ingredient": requirement["name"],
                "required_qty_grams": requirement["required_qty_grams"],
                "available_qty_grams": available_qty,
                "is_available": is_available,
                "unavailability_reason": unavailability_reason,
                "expiry_date": expiry_date_str,
                "days_until_expiry": days_remaining,
            }
        )

        if not is_available:
            all_available = False

    return {"all_available": all_available, "details": availability_results}


def format_unavailable_ingredient(detail):
    """Format an unavailable ingredient name for order failure remarks."""
    ingredient_name = detail["ingredient"]
    if detail.get("unavailability_reason") == "expired":
        return f"{ingredient_name} (expired)"
    return ingredient_name


def combine_requirements(requirement_groups):
    """Merge repeated ingredient requirements into a single total per ingredient."""
    combined_requirements = {}

    # Step 2: combine ingredient demand across all items in the same order so
    # fulfillment is checked against the total grams needed for the entire order.
    for requirements in requirement_groups:
        for requirement in requirements:
            ingredient_name = requirement["name"]
            combined_requirements.setdefault(ingredient_name, 0)
            combined_requirements[ingredient_name] += requirement["required_qty_grams"]

    return [
        {"name": ingredient_name, "required_qty_grams": required_qty}
        for ingredient_name, required_qty in combined_requirements.items()
    ]


def deduct_inventory(inventory_data, requirements):
    """Subtract the used ingredient grams from inventory after a successful order."""
    inventory_lookup = {item["ingredient"]: item for item in inventory_data}

    # Step 4: deduct only after the full order passes the availability check so
    # we do not partially consume stock for orders that cannot be delivered.
    # Assumption to verify: partial stock should not be deducted for failed orders;
    # inventory changes only when the entire order is considered deliverable.
    for requirement in requirements:
        inventory_lookup[requirement["name"]]["qty_grams"] -= requirement["required_qty_grams"]


def apply_final_inventory_snapshot(inventory_data, final_inventory_data):
    """Copy the final cumulative inventory quantities back into the main table."""
    final_inventory_lookup = {
        item["ingredient"]: item["qty_grams"] for item in final_inventory_data
    }

    # Step 6: update the final inventory table only after all orders have been
    # processed so the printed inventory reflects the true remaining stock.
    for item in inventory_data:
        if item["ingredient"] in final_inventory_lookup:
            item["qty_grams"] = final_inventory_lookup[item["ingredient"]]


def update_status_entry(status_data, order_id, delivered, remark):
    """Update or create a status-table entry for a processed order."""
    for entry in status_data:
        if entry["order_id"] == order_id:
            entry["delivered"] = delivered
            entry["remark"] = remark
            return

    # Incomplete / follow-up: if later tasks formalize a stricter schema, we may
    # want to prevent new status rows and require every order to exist up front.
    status_data.append({"order_id": order_id, "delivered": delivered, "remark": remark})


def build_restock_reasons(inventory_item, reference_date):
    """Return all applicable restock reasons for one inventory item."""
    expiry_date = parse_expiry_date(inventory_item["expiry_date"])
    days_left = days_until_expiry(expiry_date, reference_date)
    current_qty_grams = inventory_item["qty_grams"]
    reasons = []

    if 0 <= days_left <= EXPIRING_SOON_DAYS:
        reasons.append("Expiring soon")
    if current_qty_grams == 0:
        reasons.append("Out of stock")
    if 0 < current_qty_grams <= LOW_STOCK_THRESHOLD_G:
        reasons.append("Running low on stock")

    return reasons


def calculate_restock_qty_needed(inventory_item, reasons):
    """Return the grams needed to reach par, using the max across applicable rules."""
    qty_options = []
    current_qty_grams = inventory_item["qty_grams"]

    if "Expiring soon" in reasons or "Out of stock" in reasons:
        qty_options.append(PAR_LEVEL_G)
    if "Running low on stock" in reasons:
        qty_options.append(PAR_LEVEL_G - current_qty_grams)

    return max(qty_options) if qty_options else 0


def calculate_restock_needs(inventory_data, reference_date=None):
    """Build restock recommendations from final inventory using stock and expiry rules."""
    if reference_date is None:
        # Assumption to verify: when no simulation date is passed in, the code uses
        # Python's date.today() from the local runtime environment as "today."
        reference_date = date.today()

    restock_recommendations = []

    for item in inventory_data:
        expiry_date = parse_expiry_date(item["expiry_date"])
        days_left = days_until_expiry(expiry_date, reference_date)
        reasons = build_restock_reasons(item, reference_date)

        if not reasons:
            continue

        restock_recommendations.append(
            {
                "item": item["ingredient"],
                "current_qty_grams": item["qty_grams"],
                "reasons": reasons,
                "qty_needed_grams": calculate_restock_qty_needed(item, reasons),
                "expiry_date": item["expiry_date"],
                "days_until_expiry": days_left,
            }
        )

    return restock_recommendations


def refresh_restock_table(restock_data, inventory_data, reference_date=None):
    """Replace the live restock table with recommendations from final inventory."""
    # Step 7: rebuild the restock table after all orders have been processed so it
    # reflects the final inventory state instead of intermediate order failures.
    # Incomplete / follow-up: this replaces the whole restock table each run, so it
    # does not preserve historical/manual restock notes outside the current simulation.
    restock_data.clear()
    restock_data.extend(calculate_restock_needs(inventory_data, reference_date))


def process_orders(
    recipe_data,
    inventory_data,
    order_data,
    status_data,
    restock_data,
    reference_date=None,
):
    """Process orders, update fulfillment status, deduct inventory, and add restocks."""
    processed_orders = []
    working_inventory = deepcopy(inventory_data)

    # Step 0: use a working inventory snapshot during processing so each order is
    # checked against stock remaining after previous successful orders, while the
    # final inventory table is only updated once the full order list is complete.
    # Assumption to verify: working_inventory is a deep copy, not a shared reference,
    # so interim deductions during processing do not immediately mutate inventory_data.
    # Incomplete / follow-up: this remains an in-memory simulation only; later tasks
    # may need transaction handling or persistence if inventory state is stored externally.

    for order in order_data:
        order_result = {
            "order_id": order["order_id"],
            "brand": order["brand"],
            "items": [],
            "order_requirements": [],
            "inventory_check": None,
            "fulfilled": False,
            "reason": "",
        }
        requirement_groups = []
        missing_recipe_items = []

        for item in order["items"]:
            # Step 1: find the recipe for the ordered menu item.
            recipe = find_recipe_by_name(recipe_data, item["item"])

            if recipe is None:
                # If an order item has no matching recipe, we do not stop the program
                # or attempt substitution. We record recipe_found=False, skip demand
                # calculation and inventory checking for that item, and continue.
                # Incomplete / follow-up: later tasks may convert this into a formal
                # rejection reason, validation error, or fulfillment status update.
                order_result["items"].append(
                    {
                        "item": item["item"],
                        "qty": item["qty"],
                        "recipe_found": False,
                        "requirements": [],
                    }
                )
                missing_recipe_items.append(item["item"])
                continue

            # Step 2: calculate the total ingredient grams needed for this order item.
            requirements = calculate_ingredient_requirements(recipe, item["qty"])
            requirement_groups.append(requirements)

            order_result["items"].append(
                {
                    "item": item["item"],
                    "qty": item["qty"],
                    "recipe_found": True,
                    "requirements": requirements,
                }
            )

        order_requirements = combine_requirements(requirement_groups)
        order_result["order_requirements"] = order_requirements

        # Step 3: check the inventory table against the total ingredient demand for
        # the whole order, not just individual items, before deciding fulfillment.
        # Because this uses working_inventory, Order 2 is checked against whatever
        # stock remains after Order 1 was successfully served.
        # If two orders compete for the same ingredient, the earlier successful order
        # consumes from working_inventory first, and the later order is evaluated
        # against the reduced quantity that remains.
        inventory_check = check_inventory_availability(
            working_inventory, order_requirements, reference_date
        )
        order_result["inventory_check"] = inventory_check

        missing_ingredients = [
            detail for detail in inventory_check["details"] if not detail["is_available"]
        ]
        unavailable_names = ", ".join(
            format_unavailable_ingredient(detail) for detail in missing_ingredients
        )

        if missing_recipe_items:
            reason_parts = [
                "No matching recipe for item(s): " + ", ".join(missing_recipe_items)
            ]
            if missing_ingredients:
                reason_parts.append(
                    "Missing or insufficient ingredients: " + unavailable_names
                )

            order_result["fulfilled"] = False
            order_result["reason"] = " | ".join(reason_parts)
            update_status_entry(status_data, order["order_id"], False, order_result["reason"])
        elif inventory_check["all_available"]:
            # Step 4: when every required ingredient is available, mark the order as
            # delivered and deduct the used grams from the working inventory only.
            deduct_inventory(working_inventory, order_requirements)
            order_result["fulfilled"] = True
            order_result["reason"] = "Delivered"
            update_status_entry(status_data, order["order_id"], True, "Delivered")
        else:
            # Step 5: when any ingredient is missing, insufficient, or expired, do not
            # deduct inventory. Mark the order as not delivered, record the reason,
            # and add the shortage reason to status. The final restock table is
            # rebuilt later from ending inventory according to the Task 5 expiry/stock
            # rules. Assumption to verify: this flow rejects the full order rather than
            # allowing partial fulfillment of the items that do have enough stock.
            order_result["fulfilled"] = False
            order_result["reason"] = f"Missing or insufficient ingredients: {unavailable_names}"
            update_status_entry(status_data, order["order_id"], False, order_result["reason"])

        processed_orders.append(order_result)

    apply_final_inventory_snapshot(inventory_data, working_inventory)
    refresh_restock_table(restock_data, inventory_data, reference_date)

    return processed_orders


def print_order_processing_results(processed_orders):
    """Print recipe lookup, ingredient demand, inventory checks, and fulfillment."""
    print("\n=== Order Processing ===")
    for order in processed_orders:
        print(f"Order ID: {order['order_id']}")
        print(f"Brand: {order['brand']}")

        for item in order["items"]:
            print(f"Item: {item['item']}")
            print(f"Quantity Ordered: {item['qty']}")
            print(f"Recipe Found: {item['recipe_found']}")

            if not item["recipe_found"]:
                print("Inventory Check: Skipped because the recipe was not found.")
                print()
                continue

            print("Required Ingredients:")
            for requirement in item["requirements"]:
                print(
                    f"  - {requirement['name']}: "
                    f"{requirement['required_qty_grams']} grams required"
                )

            print()

        print("Combined Order Requirements:")
        for requirement in order["order_requirements"]:
            print(f"  - {requirement['name']}: {requirement['required_qty_grams']} grams required")

        print(f"All Ingredients Available: {order['inventory_check']['all_available']}")
        print("Inventory Details:")
        for detail in order["inventory_check"]["details"]:
            print(
                f"  - {detail['ingredient']}: "
                f"required={detail['required_qty_grams']} grams, "
                f"available={detail['available_qty_grams']} grams, "
                f"enough={detail['is_available']}"
            )

        print(f"Fulfilled: {order['fulfilled']}")
        print(f"Reason: {order['reason']}")
        print()


def build_inventory_alerts(inventory_data, reference_date=None):
    """Return stock and expiry alert rows for ingredients that need manager attention."""
    if reference_date is None:
        reference_date = date.today()

    alerts = []
    for item in inventory_data:
        expiry_date = parse_expiry_date(item["expiry_date"])
        days_left = days_until_expiry(expiry_date, reference_date)
        current_qty_grams = item["qty_grams"]
        issues = []

        if days_left < 0:
            issues.append("Expired")
        elif days_left <= EXPIRING_SOON_DAYS:
            issues.append("Expiring soon")
        if current_qty_grams == 0:
            issues.append("Out of stock")
        elif current_qty_grams <= LOW_STOCK_THRESHOLD_G:
            issues.append("Running low")

        if not issues:
            continue

        alerts.append(
            {
                "ingredient": item["ingredient"],
                "qty_grams": current_qty_grams,
                "expiry_date": item["expiry_date"],
                "days_until_expiry": days_left,
                "issues": issues,
            }
        )

    return alerts


def _lookup_status_remark(status_data, order_id):
    """Return the status remark for an order, or an empty string if not found."""
    for entry in status_data:
        if entry["order_id"] == order_id:
            return entry["remark"]
    return ""


def _build_not_delivered_orders(processed_orders, status_data):
    """Build failed-order rows using processed-order reasons with status fallback."""
    not_delivered_orders = []
    for order in processed_orders:
        if order["fulfilled"]:
            continue

        reason = order["reason"] or _lookup_status_remark(status_data, order["order_id"])
        not_delivered_orders.append(
            {
                "order_id": order["order_id"],
                "brand": order["brand"],
                "reason": reason,
            }
        )

    return not_delivered_orders


def build_business_summary(
    processed_orders,
    inventory_data,
    restock_data,
    status_data,
    reference_date=None,
):
    """Build a manager-facing summary dictionary from post-simulation outputs."""
    delivered_orders = [
        {"order_id": order["order_id"], "brand": order["brand"]}
        for order in processed_orders
        if order["fulfilled"]
    ]
    not_delivered_orders = _build_not_delivered_orders(processed_orders, status_data)
    inventory_alerts = build_inventory_alerts(inventory_data, reference_date)
    expiry_concerns = [
        alert
        for alert in inventory_alerts
        if "Expired" in alert["issues"] or "Expiring soon" in alert["issues"]
    ]
    final_inventory = [
        {
            "ingredient": item["ingredient"],
            "qty_grams": item["qty_grams"],
            "expiry_date": item["expiry_date"],
        }
        for item in inventory_data
    ]

    return {
        "orders_delivered": len(delivered_orders),
        "orders_not_delivered": len(not_delivered_orders),
        "delivered_orders": delivered_orders,
        "not_delivered_orders": not_delivered_orders,
        "failed_orders": not_delivered_orders,
        "final_inventory": final_inventory,
        "restock_recommendations": list(restock_data),
        "inventory_alerts": inventory_alerts,
        "expiry_concerns": expiry_concerns,
    }


def print_business_summary(summary):
    """Print a plain-language end-of-run summary for kitchen managers."""
    print("\n=== Business Summary ===")
    print(
        f"Orders delivered: {summary['orders_delivered']} | "
        f"Orders not delivered: {summary['orders_not_delivered']}"
    )

    print("\nDelivered orders:")
    if summary["delivered_orders"]:
        for order in summary["delivered_orders"]:
            print(f"  - Order {order['order_id']} ({order['brand']})")
    else:
        print("  - None")

    print("\nNot delivered orders:")
    if summary["not_delivered_orders"]:
        for order in summary["not_delivered_orders"]:
            print(
                f"  - Order {order['order_id']} ({order['brand']}): {order['reason']}"
            )
    else:
        print("  - None")

    print("\nFailure explanations:")
    if summary["failed_orders"]:
        for order in summary["failed_orders"]:
            print(
                f"  - Order {order['order_id']} ({order['brand']}): {order['reason']}"
            )
    else:
        print("  - No failed orders.")

    print("\nFinal inventory:")
    for item in summary["final_inventory"]:
        print(
            f"  - {item['ingredient']}: {item['qty_grams']} grams "
            f"(expires {item['expiry_date']})"
        )

    print("\nRestock recommendations:")
    if summary["restock_recommendations"]:
        for item in summary["restock_recommendations"]:
            print(
                f"  - {item['item']}: current {item['current_qty_grams']} grams, "
                f"order {item['qty_needed_grams']} grams "
                f"({', '.join(item['reasons'])}) "
                f"[expires {item['expiry_date']}, "
                f"{item['days_until_expiry']} day(s) left]"
            )
    else:
        print("  - No restock needed.")

    print("\nExpiry concerns:")
    if summary["expiry_concerns"]:
        for alert in summary["expiry_concerns"]:
            print(
                f"  - {alert['ingredient']}: {', '.join(alert['issues'])} "
                f"({alert['qty_grams']} grams, expires {alert['expiry_date']}, "
                f"{alert['days_until_expiry']} day(s) left)"
            )
    else:
        print("  - No expiry concerns.")


def main():
    """Load seed tables, process fulfillment, and print the updated results."""
    # Assumption to verify: we process working copies of mutable tables so the seed
    # definitions stay unchanged across runs and tests.
    # Incomplete / follow-up: this script still prints results directly to the console
    # and does not yet persist updated inventory, restock, or status tables anywhere.
    recipe_data = load_recipes()
    inventory_data = deepcopy(load_inventory())
    order_data = load_orders()
    # Step 8: start with an empty live restock table because recommendations are
    # now generated from final inventory after all orders have been processed.
    restock_data = []
    status_data = deepcopy(load_status())
    processed_orders = process_orders(
        recipe_data,
        inventory_data,
        order_data,
        status_data,
        restock_data,
    )

    print_recipes(recipe_data)
    print_orders(order_data)
    print_order_processing_results(processed_orders)
    print_inventory(inventory_data)
    print_restock(restock_data)
    print_status(status_data)
    summary = build_business_summary(
        processed_orders,
        inventory_data,
        restock_data,
        status_data,
    )
    print_business_summary(summary)


if __name__ == "__main__":
    main()
