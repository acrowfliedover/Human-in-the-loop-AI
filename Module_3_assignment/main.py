"""Baseline entry point for loading and printing cloud kitchen seed data."""

from copy import deepcopy
from datetime import date, datetime

from seed_data import inventory, orders, recipes, restock, status

# --- Section 1: Module constants ---
PAR_LEVEL_G = 10000
LOW_STOCK_THRESHOLD_G = 1000
EXPIRING_SOON_DAYS = 5
EXPIRY_DATE_FORMAT = "%Y-%m-%d"
MISSING_INGREDIENTS_PREFIX = "Missing or insufficient ingredients: "


# --- Section 2: Data access (load_*) ---
def load_recipes():
    """Return the seeded recipe records for use in the application."""
    return recipes


def load_inventory():
    """Return the seeded inventory records for the simulation."""
    return inventory


def load_orders():
    """Return the seeded customer order records."""
    return orders


def load_restock():
    """Return the seeded restock recommendations."""
    return restock


def load_status():
    """Return the seeded delivery status records."""
    return status


# --- Section 3: Data display (print_*) ---
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


def print_inventory(inventory_data):
    """Print every inventory item with quantity and expiry information."""
    print("\n=== Inventory ===")
    for item in inventory_data:
        print(f"Ingredient: {item['ingredient']}")
        print(f"Quantity: {item['qty_grams']} grams")
        print(f"Expiry Date: {item['expiry_date']}")
        print()


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


def print_restock(restock_data):
    """Print every restock item with quantity needed and reason."""
    print("\n=== Restock ===")
    for item in restock_data:
        print(f"Item: {item['item']}")
        if "reasons" in item:
            print(f"Current Quantity: {item['current_qty_grams']} grams")
            print(f"Quantity Needed: {item['qty_needed_grams']} grams")
            print(f"Reasons: {', '.join(item['reasons'])}")
            print(f"Expiry Date: {item['expiry_date']}")
            print(f"Days Until Expiry: {item['days_until_expiry']}")
        else:
            print("Current Quantity: N/A")
            print(f"Quantity Needed: {item['qty_needed_grams']} grams")
            print(f"Reason: {item['reason']}")
            print("Expiry Date: N/A")
            print("Days Until Expiry: N/A")
        print()


def print_status(status_data):
    """Print every order status with delivery result and remark."""
    print("\n=== Status ===")
    for entry in status_data:
        print(f"Order ID: {entry['order_id']}")
        print(f"Delivered: {entry['delivered']}")
        print(f"Remark: {entry['remark']}")
        print()


# --- Section 4: Recipe engine ---
def find_recipe_by_name(recipe_data, item_name):
    """Return the recipe that matches an order item name, or None if missing."""
    for recipe in recipe_data:
        if recipe["name"] == item_name:
            return recipe
    return None


def calculate_ingredient_requirements(recipe, quantity):
    """Return the total grams required for each ingredient in an order item."""
    requirements = []
    for ingredient in recipe["ingredients"]:
        requirements.append(
            {
                "name": ingredient["name"],
                "required_qty_grams": ingredient["qty_grams"] * quantity,
            }
        )
    return requirements


def combine_requirements(requirement_groups):
    """Merge repeated ingredient requirements into a single total per ingredient."""
    combined_requirements = {}
    for requirements in requirement_groups:
        for requirement in requirements:
            ingredient_name = requirement["name"]
            combined_requirements.setdefault(ingredient_name, 0)
            combined_requirements[ingredient_name] += requirement["required_qty_grams"]

    return [
        {"name": ingredient_name, "required_qty_grams": required_qty}
        for ingredient_name, required_qty in combined_requirements.items()
    ]


# --- Section 5: Expiry helpers ---
def _resolve_reference_date(reference_date):
    """Return reference_date or today's date when the caller omits a date."""
    if reference_date is None:
        return date.today()
    return reference_date


def parse_expiry_date(expiry_str):
    """Parse an inventory expiry string in YYYY-MM-DD format into a date."""
    if not expiry_str:
        return None
    try:
        return datetime.strptime(expiry_str, EXPIRY_DATE_FORMAT).date()
    except (ValueError, TypeError):
        return None


def days_until_expiry(expiry_date, reference_date):
    """Return the number of days from reference_date until expiry_date."""
    return (expiry_date - reference_date).days


def _inventory_expiry_days(inventory_item, reference_date):
    """Return (expiry_str, days_left) for one inventory row."""
    resolved_date = _resolve_reference_date(reference_date)
    expiry_date_str = inventory_item.get("expiry_date")
    expiry_date = parse_expiry_date(expiry_date_str)
    if expiry_date is None:
        return expiry_date_str, None
    days_left = days_until_expiry(expiry_date, resolved_date)
    return expiry_date_str, days_left


def is_ingredient_usable(inventory_item, reference_date):
    """Return whether an inventory item is not expired as of reference_date."""
    _, days_left = _inventory_expiry_days(inventory_item, reference_date)
    if days_left is None or days_left < 0:
        return False, "expired"
    return True, None


# --- Section 6: Inventory engine ---
def check_inventory_availability(inventory_data, requirements, reference_date=None):
    """Check whether inventory can fulfill every required ingredient in usable quantity."""
    resolved_date = _resolve_reference_date(reference_date)
    inventory_lookup = {item["ingredient"]: item for item in inventory_data}
    availability_results = []
    all_available = True

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
            expiry_date_str, days_remaining = _inventory_expiry_days(
                inventory_item, resolved_date
            )
            ingredient_usable, usability_reason = is_ingredient_usable(
                inventory_item, resolved_date
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


def deduct_inventory(inventory_data, requirements):
    """Subtract the used ingredient grams from inventory after a successful order."""
    inventory_lookup = {item["ingredient"]: item for item in inventory_data}
    for requirement in requirements:
        inventory_lookup[requirement["name"]]["qty_grams"] -= requirement["required_qty_grams"]


def apply_final_inventory_snapshot(inventory_data, final_inventory_data):
    """Copy the final cumulative inventory quantities back into the main table."""
    final_inventory_lookup = {
        item["ingredient"]: item["qty_grams"] for item in final_inventory_data
    }
    for item in inventory_data:
        if item["ingredient"] in final_inventory_lookup:
            item["qty_grams"] = final_inventory_lookup[item["ingredient"]]


# --- Section 7: Status tracking ---
def update_status_entry(status_data, order_id, delivered, remark):
    """Update or create a status-table entry for a processed order."""
    for entry in status_data:
        if entry["order_id"] == order_id:
            entry["delivered"] = delivered
            entry["remark"] = remark
            return
    status_data.append({"order_id": order_id, "delivered": delivered, "remark": remark})


# --- Section 8: Restock engine ---
def build_restock_reasons(inventory_item, reference_date):
    """Return all applicable restock reasons for one inventory item."""
    _, days_left = _inventory_expiry_days(inventory_item, reference_date)
    current_qty_grams = inventory_item["qty_grams"]
    reasons = []

    if days_left is None or days_left < 0:
        reasons.append("Expired")
    elif 0 <= days_left <= EXPIRING_SOON_DAYS:
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

    if "Expired" in reasons or "Expiring soon" in reasons or "Out of stock" in reasons:
        qty_options.append(PAR_LEVEL_G)
    if "Running low on stock" in reasons:
        qty_options.append(PAR_LEVEL_G - current_qty_grams)

    return max(qty_options) if qty_options else 0


def calculate_restock_needs(inventory_data, reference_date=None):
    """Build restock recommendations from final inventory using stock and expiry rules."""
    resolved_date = _resolve_reference_date(reference_date)
    restock_recommendations = []

    for item in inventory_data:
        expiry_date_str, days_left = _inventory_expiry_days(item, resolved_date)
        reasons = build_restock_reasons(item, resolved_date)

        if not reasons:
            continue

        restock_recommendations.append(
            {
                "item": item["ingredient"],
                "current_qty_grams": item["qty_grams"],
                "reasons": reasons,
                "qty_needed_grams": calculate_restock_qty_needed(item, reasons),
                "expiry_date": expiry_date_str,
                "days_until_expiry": days_left,
            }
        )

    return restock_recommendations


def refresh_restock_table(restock_data, inventory_data, reference_date=None):
    """Replace the live restock table with recommendations from final inventory."""
    restock_data.clear()
    restock_data.extend(calculate_restock_needs(inventory_data, reference_date))


# --- Section 9: Order orchestration ---
def _collect_order_item_requirements(recipe_data, order):
    """Collect recipe lookup results, demand groups, and missing recipe names for one order."""
    items = []
    requirement_groups = []
    missing_recipe_items = []

    for item in order["items"]:
        recipe = find_recipe_by_name(recipe_data, item["item"])
        if recipe is None:
            items.append(
                {
                    "item": item["item"],
                    "qty": item["qty"],
                    "recipe_found": False,
                    "requirements": [],
                }
            )
            missing_recipe_items.append(item["item"])
            continue

        requirements = calculate_ingredient_requirements(recipe, item["qty"])
        requirement_groups.append(requirements)
        items.append(
            {
                "item": item["item"],
                "qty": item["qty"],
                "recipe_found": True,
                "requirements": requirements,
            }
        )

    return items, requirement_groups, missing_recipe_items


def _format_missing_ingredients_remark(unavailable_names):
    """Build the standard remark prefix for unavailable ingredients."""
    return MISSING_INGREDIENTS_PREFIX + unavailable_names


def _apply_order_fulfillment(
    order,
    order_result,
    working_inventory,
    status_data,
    missing_recipe_items,
    reference_date,
):
    """Check availability, update status, and deduct inventory for one order."""
    order_requirements = order_result["order_requirements"]
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
            reason_parts.append(_format_missing_ingredients_remark(unavailable_names))
        order_result["fulfilled"] = False
        order_result["reason"] = " | ".join(reason_parts)
        update_status_entry(status_data, order["order_id"], False, order_result["reason"])
    elif inventory_check["all_available"]:
        deduct_inventory(working_inventory, order_requirements)
        order_result["fulfilled"] = True
        order_result["reason"] = "Delivered"
        update_status_entry(status_data, order["order_id"], True, "Delivered")
    else:
        order_result["fulfilled"] = False
        order_result["reason"] = _format_missing_ingredients_remark(unavailable_names)
        update_status_entry(status_data, order["order_id"], False, order_result["reason"])

    return order_result


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
        items, requirement_groups, missing_recipe_items = _collect_order_item_requirements(
            recipe_data, order
        )
        order_result["items"] = items
        order_result["order_requirements"] = combine_requirements(requirement_groups)
        order_result = _apply_order_fulfillment(
            order,
            order_result,
            working_inventory,
            status_data,
            missing_recipe_items,
            reference_date,
        )
        processed_orders.append(order_result)

    apply_final_inventory_snapshot(inventory_data, working_inventory)
    refresh_restock_table(restock_data, inventory_data, reference_date)

    return processed_orders


# --- Section 10: Processing display ---
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


# --- Section 11: Business summary ---
def build_inventory_alerts(inventory_data, reference_date=None):
    """Return stock and expiry alert rows for ingredients that need manager attention."""
    resolved_date = _resolve_reference_date(reference_date)
    alerts = []

    for item in inventory_data:
        expiry_date_str, days_left = _inventory_expiry_days(item, resolved_date)
        current_qty_grams = item["qty_grams"]
        issues = []

        if days_left is None or days_left < 0:
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
                "expiry_date": expiry_date_str,
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


# --- Section 12: Entry point ---
def main():
    """Load seed tables, display them, process fulfillment, and print updated results."""
    recipe_data = load_recipes()
    inventory_data = deepcopy(load_inventory())
    order_data = load_orders()
    restock_data = []
    status_data = deepcopy(load_status())

    # Seed tables before processing; loaders return unmutated module lists.
    print_recipes(recipe_data)
    print_inventory(load_inventory())
    print_orders(order_data)
    print_restock(load_restock())
    print_status(load_status())

    processed_orders = process_orders(
        recipe_data,
        inventory_data,
        order_data,
        status_data,
        restock_data,
    )

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
