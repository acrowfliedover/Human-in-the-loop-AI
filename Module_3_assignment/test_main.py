"""Unit tests for the baseline seed-data loading functions."""

from copy import deepcopy
from datetime import date
from io import StringIO
import sys
import unittest

from main import (
    PAR_LEVEL_G,
    REASON_EXPIRED,
    REASON_EXPIRING_SOON,
    REASON_OUT_OF_STOCK,
    REASON_RUNNING_LOW,
    REMARK_DELIVERED,
    REMARK_EMPTY_ORDER,
    UNAVAIL_EXPIRED,
    UNAVAIL_INSUFFICIENT,
    UNAVAIL_MISSING,
    build_business_summary,
    build_inventory_alerts,
    calculate_ingredient_requirements,
    calculate_restock_needs,
    check_inventory_availability,
    find_recipe_by_name,
    load_inventory,
    load_orders,
    load_recipes,
    load_restock,
    load_status,
    main,
    print_restock,
    process_orders,
)
from seed_data import inventory, orders, recipes, restock, status

TEST_REFERENCE_DATE = date(2026, 6, 3)


class TestLoadFunctions(unittest.TestCase):
    """Verify the Task 1 data-loading helpers return the expected seed tables."""

    def test_loads_all_five_tables_successfully(self):
        """Each load function should return a non-empty list from seed_data."""
        # Assumption to verify: Task 1 considers a successful import equivalent to
        # each loader returning the seeded module-level list without raising errors.
        self.assertIsInstance(load_recipes(), list)
        self.assertIsInstance(load_inventory(), list)
        self.assertIsInstance(load_orders(), list)
        self.assertIsInstance(load_restock(), list)
        self.assertIsInstance(load_status(), list)

        self.assertGreater(len(load_recipes()), 0)
        self.assertGreater(len(load_inventory()), 0)
        self.assertGreater(len(load_orders()), 0)
        self.assertGreater(len(load_restock()), 0)
        self.assertGreater(len(load_status()), 0)

    def test_record_counts_match_seed_data(self):
        """Each load function should return the expected number of seed records."""
        self.assertEqual(len(load_recipes()), 5)
        self.assertEqual(len(load_inventory()), 14)
        self.assertEqual(len(load_orders()), 5)
        self.assertEqual(len(load_restock()), 5)
        self.assertEqual(len(load_status()), 5)

    def test_recipe_key_field_types(self):
        """Recipe records should expose the expected identifier and ingredient types."""
        recipe = load_recipes()[0]
        ingredient = recipe["ingredients"][0]

        self.assertIsInstance(recipe["recipe_id"], int)
        self.assertIsInstance(recipe["name"], str)
        self.assertIsInstance(recipe["ingredients"], list)
        self.assertIsInstance(ingredient["name"], str)
        self.assertIsInstance(ingredient["qty_grams"], (int, float))

    def test_inventory_key_field_types(self):
        """Inventory records should provide valid quantity and expiry field types."""
        item = load_inventory()[0]

        self.assertIsInstance(item["ingredient"], str)
        self.assertIsInstance(item["qty_grams"], (int, float))
        self.assertIsInstance(item["expiry_date"], str)

    def test_order_key_field_types(self):
        """Order records should expose valid identifiers, brands, and quantities."""
        order = load_orders()[0]
        item = order["items"][0]

        self.assertIsInstance(order["order_id"], int)
        self.assertIsInstance(order["brand"], str)
        self.assertIsInstance(order["items"], list)
        self.assertIsInstance(item["item"], str)
        self.assertIsInstance(item["qty"], int)

    def test_restock_key_field_types(self):
        """Restock records should provide an item name, numeric quantity, and reason."""
        item = load_restock()[0]

        self.assertIsInstance(item["item"], str)
        self.assertIsInstance(item["qty_needed_grams"], (int, float))
        self.assertIsInstance(item["reason"], str)

    def test_status_key_field_types(self):
        """Status records should provide order linkage and delivery state types."""
        item = load_status()[0]

        self.assertIsInstance(item["order_id"], int)
        self.assertIsInstance(item["delivered"], bool)
        self.assertIsInstance(item["remark"], str)
        # Incomplete / follow-up: if the project later formalizes a status enum or
        # richer state machine, these tests should be expanded beyond simple types.

    def test_loaders_return_seed_module_lists(self):
        """Each loader should return the corresponding seed_data module list."""
        self.assertIs(load_recipes(), recipes)
        self.assertIs(load_inventory(), inventory)
        self.assertIs(load_orders(), orders)
        self.assertIs(load_restock(), restock)
        self.assertIs(load_status(), status)

    def test_all_records_have_required_key_fields(self):
        """Every record in each seed table should expose all required key fields."""
        for recipe in load_recipes():
            self.assertIn("recipe_id", recipe)
            self.assertIn("name", recipe)
            self.assertIn("ingredients", recipe)
            self.assertGreater(len(recipe["ingredients"]), 0)
            for ingredient in recipe["ingredients"]:
                self.assertIn("name", ingredient)
                self.assertIn("qty_grams", ingredient)

        for item in load_inventory():
            self.assertIn("ingredient", item)
            self.assertIn("qty_grams", item)
            self.assertIn("expiry_date", item)

        for order in load_orders():
            self.assertIn("order_id", order)
            self.assertIn("brand", order)
            self.assertIn("items", order)
            self.assertGreater(len(order["items"]), 0)
            for order_item in order["items"]:
                self.assertIn("item", order_item)
                self.assertIn("qty", order_item)

        for item in load_restock():
            self.assertIn("item", item)
            self.assertIn("qty_needed_grams", item)
            self.assertIn("reason", item)

        for entry in load_status():
            self.assertIn("order_id", entry)
            self.assertIn("delivered", entry)
            self.assertIn("remark", entry)

    def test_print_restock_seed_data_does_not_crash(self):
        """print_restock should handle seed restock rows without raising."""
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        try:
            print_restock(load_restock())
        finally:
            sys.stdout = original_stdout

        output = captured_output.getvalue()
        self.assertIn("=== Restock ===", output)
        self.assertIn("Flour", output)
        self.assertIn("Running low stock", output)
        self.assertIn("Current Quantity: N/A", output)

    def test_print_restock_calculated_rows(self):
        """print_restock should display calculated restock rows with full detail."""
        inventory_data = [
            {"ingredient": "Bun", "qty_grams": 0, "expiry_date": "2026-12-31"}
        ]
        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        try:
            print_restock(restock_data)
        finally:
            sys.stdout = original_stdout

        output = captured_output.getvalue()
        self.assertIn("Bun", output)
        self.assertIn("Out of stock", output)
        self.assertIn("Current Quantity: 0 grams", output)
        self.assertIn("Days Until Expiry: 211", output)

    def test_main_displays_seed_tables_before_processing(self):
        """main() should print all five seed tables before order processing."""
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        try:
            main()
        finally:
            sys.stdout = original_stdout

        output = captured_output.getvalue()
        processing_index = output.find("=== Order Processing ===")
        self.assertGreater(processing_index, 0)

        startup = output[:processing_index]
        self.assertIn("=== Recipes ===", startup)
        self.assertIn("=== Inventory ===", startup)
        self.assertIn("=== Orders ===", startup)
        self.assertIn("=== Restock ===", startup)
        self.assertIn("=== Status ===", startup)
        self.assertIn("Margherita Pizza", startup)
        self.assertIn("Ingredient: Flour", startup)
        self.assertIn("Current Quantity: N/A", startup)
        self.assertIn("Running low stock", startup)
        self.assertEqual(startup.count("=== Inventory ==="), 1)
        self.assertEqual(startup.count("=== Restock ==="), 1)

        self.assertIn("=== Inventory ===", output[processing_index:])
        self.assertIn("=== Restock ===", output[processing_index:])
        self.assertIn("=== Status ===", output[processing_index:])
        self.assertIn("=== Business Summary ===", output[processing_index:])


class TestOrderRecipeLookup(unittest.TestCase):
    """Verify order items can be matched to recipes and scaled correctly."""

    def test_find_recipe_by_name_returns_matching_recipe(self):
        """A valid order item should return its matching recipe record."""
        recipe = find_recipe_by_name(load_recipes(), "Chicken Burger")

        self.assertIsNotNone(recipe)
        self.assertEqual(recipe["recipe_id"], 2)
        self.assertEqual(recipe["name"], "Chicken Burger")

    def test_find_recipe_by_name_handles_missing_recipe_gracefully(self):
        """A missing order item should return None instead of raising an error."""
        recipe = find_recipe_by_name(load_recipes(), "Paneer Wrap")

        self.assertIsNone(recipe)

    def test_calculate_ingredient_requirements_scales_for_quantity_two(self):
        """Ingredient requirements should double when the order quantity is two."""
        recipe = find_recipe_by_name(load_recipes(), "Margherita Pizza")
        requirements = calculate_ingredient_requirements(recipe, 2)

        expected_requirements = [
            {"name": "Flour", "required_qty_grams": 600},
            {"name": "Tomato Sauce", "required_qty_grams": 200},
            {"name": "Mozzarella Cheese", "required_qty_grams": 300},
        ]

        self.assertEqual(requirements, expected_requirements)

    def test_valid_item_returns_scaled_ingredients_at_quantity_one(self):
        """A valid item should return base ingredient quantities when quantity is one."""
        recipe = find_recipe_by_name(load_recipes(), "Chicken Burger")
        requirements = calculate_ingredient_requirements(recipe, 1)

        expected_requirements = [
            {"name": "Chicken Breast", "required_qty_grams": 200},
            {"name": "Bun", "required_qty_grams": 100},
            {"name": "Lettuce", "required_qty_grams": 50},
        ]

        self.assertEqual(requirements, expected_requirements)

    def test_process_orders_rejects_order_with_missing_recipe(self):
        """An order with an unknown item should fail gracefully without changing inventory."""
        recipe_data = deepcopy(load_recipes())
        inventory_data = deepcopy(load_inventory())
        original_inventory = deepcopy(inventory_data)
        status_data = []
        restock_data = []
        order_data = [
            {
                "order_id": 303,
                "brand": "Test Kitchen",
                "items": [{"item": "Paneer Wrap", "qty": 1}],
            }
        ]

        processed_orders = process_orders(
            recipe_data,
            inventory_data,
            order_data,
            status_data,
            restock_data,
            reference_date=TEST_REFERENCE_DATE,
        )

        self.assertFalse(processed_orders[0]["fulfilled"])
        self.assertIn("No matching recipe for item(s): Paneer Wrap", processed_orders[0]["reason"])
        self.assertFalse(processed_orders[0]["items"][0]["recipe_found"])
        self.assertEqual(processed_orders[0]["items"][0]["requirements"], [])
        self.assertEqual(inventory_data, original_inventory)
        self.assertEqual(status_data[0]["order_id"], 303)
        self.assertFalse(status_data[0]["delivered"])
        self.assertIn("Paneer Wrap", status_data[0]["remark"])


class TestInventoryAvailabilityCheck(unittest.TestCase):
    """Verify inventory availability checks classify ingredient shortages correctly."""

    def test_all_ingredients_available(self):
        """Every required ingredient should pass when stock is sufficient and not expired."""
        inventory_data = [
            {"ingredient": "Chicken Breast", "qty_grams": 500, "expiry_date": "2026-12-31"},
            {"ingredient": "Bun", "qty_grams": 300, "expiry_date": "2026-12-31"},
        ]
        requirements = [
            {"name": "Chicken Breast", "required_qty_grams": 200},
            {"name": "Bun", "required_qty_grams": 100},
        ]

        result = check_inventory_availability(
            inventory_data, requirements, reference_date=TEST_REFERENCE_DATE
        )

        self.assertTrue(result["all_available"])
        for detail in result["details"]:
            self.assertTrue(detail["is_available"])
            self.assertIsNone(detail["unavailability_reason"])

    def test_one_ingredient_missing(self):
        """A required ingredient absent from inventory should be marked as missing."""
        inventory_data = [
            {"ingredient": "Chicken Breast", "qty_grams": 500, "expiry_date": "2026-12-31"}
        ]
        requirements = [
            {"name": "Chicken Breast", "required_qty_grams": 200},
            {"name": "Sauce", "required_qty_grams": 50},
        ]

        result = check_inventory_availability(
            inventory_data, requirements, reference_date=TEST_REFERENCE_DATE
        )

        self.assertFalse(result["all_available"])
        sauce_detail = next(
            detail for detail in result["details"] if detail["ingredient"] == "Sauce"
        )
        self.assertFalse(sauce_detail["is_available"])
        self.assertEqual(sauce_detail["unavailability_reason"], UNAVAIL_MISSING)
        self.assertEqual(sauce_detail["available_qty_grams"], 0)

    def test_one_ingredient_insufficient_quantity(self):
        """A present ingredient with too little stock should be marked insufficient."""
        inventory_data = [
            {"ingredient": "Chicken Breast", "qty_grams": 50, "expiry_date": "2026-12-31"}
        ]
        requirements = [{"name": "Chicken Breast", "required_qty_grams": 200}]

        result = check_inventory_availability(
            inventory_data, requirements, reference_date=TEST_REFERENCE_DATE
        )

        self.assertFalse(result["all_available"])
        chicken_detail = result["details"][0]
        self.assertFalse(chicken_detail["is_available"])
        self.assertEqual(chicken_detail["unavailability_reason"], UNAVAIL_INSUFFICIENT)
        self.assertEqual(chicken_detail["available_qty_grams"], 50)

    def test_one_expired_ingredient(self):
        """Expired stock should be unavailable even when quantity is sufficient."""
        inventory_data = [
            {"ingredient": "Flour", "qty_grams": 5000, "expiry_date": "2026-05-12"}
        ]
        requirements = [{"name": "Flour", "required_qty_grams": 300}]

        result = check_inventory_availability(
            inventory_data, requirements, reference_date=TEST_REFERENCE_DATE
        )

        self.assertFalse(result["all_available"])
        flour_detail = result["details"][0]
        self.assertFalse(flour_detail["is_available"])
        self.assertEqual(flour_detail["unavailability_reason"], UNAVAIL_EXPIRED)
        self.assertLess(flour_detail["days_until_expiry"], 0)

    def test_invalid_expiry_date_does_not_crash_availability_check(self):
        """An invalid expiry string should mark the ingredient unavailable without raising."""
        inventory_data = [
            {"ingredient": "Flour", "qty_grams": 5000, "expiry_date": "not-a-date"}
        ]
        requirements = [{"name": "Flour", "required_qty_grams": 300}]

        result = check_inventory_availability(
            inventory_data, requirements, reference_date=TEST_REFERENCE_DATE
        )

        self.assertFalse(result["all_available"])
        flour_detail = result["details"][0]
        self.assertFalse(flour_detail["is_available"])
        self.assertEqual(flour_detail["unavailability_reason"], UNAVAIL_EXPIRED)
        self.assertIsNone(flour_detail["days_until_expiry"])


class TestOrderFulfillment(unittest.TestCase):
    """Verify fulfillment updates status, restock, and inventory correctly."""

    def test_process_orders_marks_delivered_when_ingredients_are_available(self):
        """An order with sufficient stock should be marked as delivered."""
        recipe_data = deepcopy(load_recipes())
        inventory_data = deepcopy(load_inventory())
        status_data = deepcopy(load_status())
        restock_data = deepcopy(load_restock())
        order_data = [
            {
                "order_id": 101,
                "brand": "Test Kitchen",
                "items": [{"item": "Chicken Burger", "qty": 1}],
            }
        ]

        processed_orders = process_orders(
            recipe_data,
            inventory_data,
            order_data,
            status_data,
            restock_data,
            reference_date=TEST_REFERENCE_DATE,
        )

        self.assertTrue(processed_orders[0]["fulfilled"])
        self.assertEqual(processed_orders[0]["reason"], REMARK_DELIVERED)
        self.assertEqual(status_data[-1]["order_id"], 101)
        self.assertTrue(status_data[-1]["delivered"])
        self.assertEqual(status_data[-1]["remark"], REMARK_DELIVERED)

    def test_process_orders_rejects_empty_order(self):
        """An order with no items should not be marked as delivered."""
        recipe_data = deepcopy(load_recipes())
        inventory_data = deepcopy(load_inventory())
        order_data = [{"order_id": 100, "brand": "Test Kitchen", "items": []}]
        status_data = []
        restock_data = []

        processed_orders = process_orders(
            recipe_data,
            inventory_data,
            order_data,
            status_data,
            restock_data,
            reference_date=TEST_REFERENCE_DATE,
        )

        self.assertFalse(processed_orders[0]["fulfilled"])
        self.assertEqual(processed_orders[0]["reason"], REMARK_EMPTY_ORDER)
        self.assertFalse(status_data[0]["delivered"])
        self.assertEqual(status_data[0]["remark"], REMARK_EMPTY_ORDER)

    def test_process_orders_marks_not_delivered_and_adds_missing_item_to_restock(self):
        """An order with a missing ingredient should fail and log the shortage."""
        recipe_data = [
            {
                "recipe_id": 1,
                "name": "Test Wrap",
                "ingredients": [
                    {"name": "Chicken Breast", "qty_grams": 200},
                    {"name": "Bun", "qty_grams": 100},
                ],
            }
        ]
        inventory_data = [
            {"ingredient": "Chicken Breast", "qty_grams": 500, "expiry_date": "2026-12-31"},
            {"ingredient": "Bun", "qty_grams": 0, "expiry_date": "2026-12-31"},
        ]
        order_data = [
            {"order_id": 202, "brand": "Test Kitchen", "items": [{"item": "Test Wrap", "qty": 1}]}
        ]
        status_data = []
        restock_data = []

        processed_orders = process_orders(
            recipe_data,
            inventory_data,
            order_data,
            status_data,
            restock_data,
            reference_date=TEST_REFERENCE_DATE,
        )

        self.assertFalse(processed_orders[0]["fulfilled"])
        self.assertIn("Missing or insufficient ingredients: Bun", processed_orders[0]["reason"])
        self.assertEqual(status_data[0]["order_id"], 202)
        self.assertFalse(status_data[0]["delivered"])
        self.assertIn("Bun", status_data[0]["remark"])
        bun_restock = next(item for item in restock_data if item["item"] == "Bun")
        self.assertEqual(bun_restock["qty_needed_grams"], PAR_LEVEL_G)
        self.assertEqual(bun_restock["reasons"], [REASON_OUT_OF_STOCK])

    def test_process_orders_adds_missing_from_inventory_ingredient_to_restock(self):
        """An ingredient absent from the inventory table should restock as missing."""
        recipe_data = [
            {
                "recipe_id": 1,
                "name": "Ghost Burger",
                "ingredients": [{"name": "Ghost Pepper", "qty_grams": 50}],
            }
        ]
        inventory_data = []
        order_data = [
            {
                "order_id": 606,
                "brand": "Test Kitchen",
                "items": [{"item": "Ghost Burger", "qty": 1}],
            }
        ]
        status_data = []
        restock_data = []

        processed_orders = process_orders(
            recipe_data,
            inventory_data,
            order_data,
            status_data,
            restock_data,
            reference_date=TEST_REFERENCE_DATE,
        )

        self.assertFalse(processed_orders[0]["fulfilled"])
        ghost_pepper_restock = next(
            item for item in restock_data if item["item"] == "Ghost Pepper"
        )
        self.assertEqual(ghost_pepper_restock["current_qty_grams"], 0)
        self.assertEqual(ghost_pepper_restock["reasons"], ["Missing from inventory"])
        self.assertEqual(ghost_pepper_restock["qty_needed_grams"], PAR_LEVEL_G)

    def test_process_orders_rejects_expired_ingredient(self):
        """An order requiring expired stock should fail without deducting inventory."""
        recipe_data = [
            {
                "recipe_id": 99,
                "name": "Flour Bread",
                "ingredients": [{"name": "Flour", "qty_grams": 300}],
            }
        ]
        inventory_data = [
            {"ingredient": "Flour", "qty_grams": 5000, "expiry_date": "2026-05-12"}
        ]
        order_data = [
            {
                "order_id": 404,
                "brand": "Test Kitchen",
                "items": [{"item": "Flour Bread", "qty": 1}],
            }
        ]
        status_data = []
        restock_data = []
        original_flour_qty = inventory_data[0]["qty_grams"]

        processed_orders = process_orders(
            recipe_data,
            inventory_data,
            order_data,
            status_data,
            restock_data,
            reference_date=TEST_REFERENCE_DATE,
        )

        self.assertFalse(processed_orders[0]["fulfilled"])
        self.assertIn("Flour (expired)", processed_orders[0]["reason"])
        self.assertEqual(inventory_data[0]["qty_grams"], original_flour_qty)
        self.assertFalse(status_data[0]["delivered"])
        self.assertIn("expired", status_data[0]["remark"])

    def test_process_orders_does_not_deduct_inventory_when_stock_insufficient(self):
        """An order with insufficient stock should fail without deducting inventory."""
        recipe_data = [
            {
                "recipe_id": 1,
                "name": "Chicken Wrap",
                "ingredients": [{"name": "Chicken Breast", "qty_grams": 200}],
            }
        ]
        inventory_data = [
            {"ingredient": "Chicken Breast", "qty_grams": 50, "expiry_date": "2026-12-31"}
        ]
        order_data = [
            {
                "order_id": 505,
                "brand": "Test Kitchen",
                "items": [{"item": "Chicken Wrap", "qty": 1}],
            }
        ]
        status_data = []
        restock_data = []
        original_chicken_qty = inventory_data[0]["qty_grams"]

        processed_orders = process_orders(
            recipe_data,
            inventory_data,
            order_data,
            status_data,
            restock_data,
            reference_date=TEST_REFERENCE_DATE,
        )

        self.assertFalse(processed_orders[0]["fulfilled"])
        self.assertIn("Chicken Breast", processed_orders[0]["reason"])
        self.assertFalse(status_data[0]["delivered"])
        self.assertIn("Chicken Breast", status_data[0]["remark"])
        self.assertEqual(inventory_data[0]["qty_grams"], original_chicken_qty)

    def test_process_orders_deducts_inventory_after_successful_delivery(self):
        """A delivered order should reduce inventory by the required grams."""
        recipe_data = deepcopy(load_recipes())
        inventory_data = deepcopy(load_inventory())
        for item in inventory_data:
            if item["ingredient"] == "Flour":
                item["expiry_date"] = "2026-12-31"
        status_data = []
        restock_data = []
        order_data = [
            {
                "order_id": 303,
                "brand": "Test Kitchen",
                "items": [{"item": "Margherita Pizza", "qty": 2}],
            }
        ]

        original_flour_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Flour"
        )
        original_sauce_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Tomato Sauce"
        )
        original_cheese_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Mozzarella Cheese"
        )

        process_orders(
            recipe_data,
            inventory_data,
            order_data,
            status_data,
            restock_data,
            reference_date=TEST_REFERENCE_DATE,
        )

        updated_flour_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Flour"
        )
        updated_sauce_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Tomato Sauce"
        )
        updated_cheese_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Mozzarella Cheese"
        )

        self.assertEqual(updated_flour_qty, original_flour_qty - 600)
        self.assertEqual(updated_sauce_qty, original_sauce_qty - 200)
        self.assertEqual(updated_cheese_qty, original_cheese_qty - 300)


class TestCumulativeInventoryDeduction(unittest.TestCase):
    """Verify inventory is consumed cumulatively across sequential orders."""

    def test_two_orders_consuming_same_ingredient_use_combined_deduction(self):
        """Two delivered orders should deduct the combined shared ingredient total."""
        recipe_data = deepcopy(load_recipes())
        inventory_data = deepcopy(load_inventory())
        for item in inventory_data:
            if item["ingredient"] in ("Flour", "Chocolate", "Sugar"):
                item["expiry_date"] = "2026-12-31"
        status_data = []
        restock_data = []
        order_data = [
            {"order_id": 401, "brand": "Test Kitchen", "items": [{"item": "Margherita Pizza", "qty": 1}]},
            {"order_id": 402, "brand": "Test Kitchen", "items": [{"item": "Chocolate Cake", "qty": 1}]},
        ]

        original_flour_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Flour"
        )

        processed_orders = process_orders(
            recipe_data,
            inventory_data,
            order_data,
            status_data,
            restock_data,
            reference_date=TEST_REFERENCE_DATE,
        )

        updated_flour_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Flour"
        )

        self.assertTrue(processed_orders[0]["fulfilled"])
        self.assertTrue(processed_orders[1]["fulfilled"])
        self.assertEqual(updated_flour_qty, original_flour_qty - 550)

    def test_later_order_fails_after_prior_order_consumes_remaining_stock(self):
        """A later order should fail if an earlier order uses the remaining shared stock."""
        recipe_data = [
            {
                "recipe_id": 1,
                "name": "First Dish",
                "ingredients": [{"name": "Cheese", "qty_grams": 600}],
            },
            {
                "recipe_id": 2,
                "name": "Second Dish",
                "ingredients": [{"name": "Cheese", "qty_grams": 500}],
            },
        ]
        inventory_data = [
            {"ingredient": "Cheese", "qty_grams": 1000, "expiry_date": "2026-12-31"}
        ]
        order_data = [
            {"order_id": 501, "brand": "Test Kitchen", "items": [{"item": "First Dish", "qty": 1}]},
            {"order_id": 502, "brand": "Test Kitchen", "items": [{"item": "Second Dish", "qty": 1}]},
        ]
        status_data = []
        restock_data = []

        processed_orders = process_orders(
            recipe_data,
            inventory_data,
            order_data,
            status_data,
            restock_data,
            reference_date=TEST_REFERENCE_DATE,
        )

        self.assertTrue(processed_orders[0]["fulfilled"])
        self.assertFalse(processed_orders[1]["fulfilled"])
        self.assertIn("Cheese", processed_orders[1]["reason"])
        self.assertEqual(status_data[1]["order_id"], 502)
        self.assertFalse(status_data[1]["delivered"])
        self.assertEqual(restock_data[0]["item"], "Cheese")
        self.assertEqual(restock_data[0]["qty_needed_grams"], 9600)
        self.assertEqual(restock_data[0]["reasons"], [REASON_RUNNING_LOW])

    def test_final_inventory_matches_expected_remaining_quantities(self):
        """Final inventory should reflect all successful cumulative deductions."""
        recipe_data = deepcopy(load_recipes())
        inventory_data = deepcopy(load_inventory())
        for item in inventory_data:
            if item["ingredient"] in ("Flour", "Chocolate", "Sugar"):
                item["expiry_date"] = "2026-12-31"
        status_data = []
        restock_data = []
        order_data = [
            {"order_id": 601, "brand": "Test Kitchen", "items": [{"item": "Margherita Pizza", "qty": 2}]},
            {"order_id": 602, "brand": "Test Kitchen", "items": [{"item": "Chocolate Cake", "qty": 1}]},
        ]

        process_orders(
            recipe_data,
            inventory_data,
            order_data,
            status_data,
            restock_data,
            reference_date=TEST_REFERENCE_DATE,
        )

        flour_qty = next(item["qty_grams"] for item in inventory_data if item["ingredient"] == "Flour")
        sauce_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Tomato Sauce"
        )
        cheese_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Mozzarella Cheese"
        )
        chocolate_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Chocolate"
        )
        sugar_qty = next(item["qty_grams"] for item in inventory_data if item["ingredient"] == "Sugar")

        self.assertEqual(flour_qty, 9150)
        self.assertEqual(sauce_qty, 9800)
        self.assertEqual(cheese_qty, 9700)
        self.assertEqual(chocolate_qty, 9850)
        self.assertEqual(sugar_qty, 9900)


class TestRestockRules(unittest.TestCase):
    """Verify the Task 8 rule-based restock calculations."""

    def test_expiring_soon_sets_full_restock_quantity(self):
        """Ingredients expiring within 5 days should be marked as expiring soon."""
        inventory_data = [
            {"ingredient": "Cream", "qty_grams": 7000, "expiry_date": "2026-06-06"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        self.assertEqual(len(restock_data), 1)
        self.assertEqual(restock_data[0]["item"], "Cream")
        self.assertEqual(restock_data[0]["current_qty_grams"], 7000)
        self.assertEqual(restock_data[0]["qty_needed_grams"], PAR_LEVEL_G)
        self.assertEqual(restock_data[0]["reasons"], [REASON_EXPIRING_SOON])
        self.assertEqual(restock_data[0]["expiry_date"], "2026-06-06")
        self.assertEqual(restock_data[0]["days_until_expiry"], 3)

    def test_out_of_stock_sets_full_restock_quantity(self):
        """Zero final stock should be marked as out of stock with 10,000 grams needed."""
        inventory_data = [
            {"ingredient": "Bun", "qty_grams": 0, "expiry_date": "2026-12-31"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        self.assertEqual(len(restock_data), 1)
        self.assertEqual(restock_data[0]["item"], "Bun")
        self.assertEqual(restock_data[0]["current_qty_grams"], 0)
        self.assertEqual(restock_data[0]["qty_needed_grams"], PAR_LEVEL_G)
        self.assertEqual(restock_data[0]["reasons"], [REASON_OUT_OF_STOCK])
        self.assertEqual(restock_data[0]["expiry_date"], "2026-12-31")
        self.assertEqual(restock_data[0]["days_until_expiry"], 211)

    def test_running_low_calculates_amount_needed_to_reach_ten_thousand(self):
        """Low stock should request only the amount needed to reach 10,000 grams."""
        inventory_data = [
            {"ingredient": "Chicken Breast", "qty_grams": 500, "expiry_date": "2026-12-31"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        self.assertEqual(len(restock_data), 1)
        self.assertEqual(restock_data[0]["item"], "Chicken Breast")
        self.assertEqual(restock_data[0]["current_qty_grams"], 500)
        self.assertEqual(restock_data[0]["qty_needed_grams"], 9500)
        self.assertEqual(restock_data[0]["reasons"], [REASON_RUNNING_LOW])
        self.assertEqual(restock_data[0]["expiry_date"], "2026-12-31")
        self.assertEqual(restock_data[0]["days_until_expiry"], 211)

    def test_adequate_stock_without_expiry_issue_is_not_flagged(self):
        """Adequate stock with no near-expiry condition should not appear in restock."""
        inventory_data = [
            {"ingredient": "Tomato Sauce", "qty_grams": 7000, "expiry_date": "2026-12-31"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        self.assertEqual(restock_data, [])

    def test_running_low_at_exact_threshold(self):
        """Stock at exactly 1,000 grams should be flagged as running low."""
        inventory_data = [
            {"ingredient": "Sugar", "qty_grams": 1000, "expiry_date": "2026-12-31"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        self.assertEqual(len(restock_data), 1)
        self.assertEqual(restock_data[0]["reasons"], [REASON_RUNNING_LOW])
        self.assertEqual(restock_data[0]["qty_needed_grams"], 9000)

    def test_above_threshold_not_flagged(self):
        """Stock above 1,000 grams with no expiry issue should not appear in restock."""
        inventory_data = [
            {"ingredient": "Flour", "qty_grams": 1001, "expiry_date": "2026-12-31"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        self.assertEqual(restock_data, [])

    def test_expiring_on_boundary_day_zero(self):
        """Expiry on the reference date should be flagged as expiring soon."""
        inventory_data = [
            {"ingredient": "Lettuce", "qty_grams": 5000, "expiry_date": "2026-06-03"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        self.assertEqual(restock_data[0]["reasons"], [REASON_EXPIRING_SOON])
        self.assertEqual(restock_data[0]["days_until_expiry"], 0)

    def test_expiring_on_boundary_day_five(self):
        """Expiry exactly 5 days out should be flagged as expiring soon."""
        inventory_data = [
            {"ingredient": "Cream", "qty_grams": 5000, "expiry_date": "2026-06-08"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        self.assertEqual(restock_data[0]["reasons"], [REASON_EXPIRING_SOON])
        self.assertEqual(restock_data[0]["days_until_expiry"], 5)

    def test_not_expiring_beyond_window(self):
        """Expiry beyond 5 days with adequate stock should not appear in restock."""
        inventory_data = [
            {"ingredient": "Mozzarella Cheese", "qty_grams": 5000, "expiry_date": "2026-06-09"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        self.assertEqual(restock_data, [])

    def test_multiple_restock_reasons_preserved(self):
        """Low stock plus expiring soon should preserve both reasons."""
        inventory_data = [
            {"ingredient": "Romaine Lettuce", "qty_grams": 500, "expiry_date": "2026-06-06"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        self.assertEqual(len(restock_data), 1)
        self.assertEqual(
            restock_data[0]["reasons"],
            [REASON_EXPIRING_SOON, REASON_RUNNING_LOW],
        )
        self.assertEqual(restock_data[0]["qty_needed_grams"], PAR_LEVEL_G)

    def test_restock_row_includes_expiry_fields(self):
        """Every flagged restock row should include expiry metadata."""
        inventory_data = [
            {"ingredient": "Croutons", "qty_grams": 800, "expiry_date": "2026-06-04"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        self.assertEqual(restock_data[0]["expiry_date"], "2026-06-04")
        self.assertEqual(restock_data[0]["days_until_expiry"], 1)

    def test_out_of_stock_and_expiring_soon(self):
        """Zero stock plus expiring soon should preserve both reasons."""
        inventory_data = [
            {"ingredient": "Bun", "qty_grams": 0, "expiry_date": "2026-06-05"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        self.assertEqual(
            restock_data[0]["reasons"],
            [REASON_EXPIRING_SOON, REASON_OUT_OF_STOCK],
        )
        self.assertEqual(restock_data[0]["qty_needed_grams"], PAR_LEVEL_G)

    def test_expired_stock_above_threshold_restocked_to_par(self):
        """Already-expired stock above 1,000 g should be flagged and restocked to par."""
        inventory_data = [
            {"ingredient": "Yogurt", "qty_grams": 5000, "expiry_date": "2026-06-01"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        self.assertEqual(len(restock_data), 1)
        self.assertEqual(restock_data[0]["item"], "Yogurt")
        self.assertEqual(restock_data[0]["current_qty_grams"], 5000)
        self.assertEqual(restock_data[0]["reasons"], [REASON_EXPIRED])
        self.assertEqual(restock_data[0]["qty_needed_grams"], PAR_LEVEL_G)
        self.assertEqual(restock_data[0]["days_until_expiry"], -2)

    def test_expired_and_running_low_preserves_both_reasons(self):
        """Expired low stock should preserve both expired and running-low reasons."""
        inventory_data = [
            {"ingredient": "Spinach", "qty_grams": 500, "expiry_date": "2026-05-30"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=TEST_REFERENCE_DATE)

        self.assertEqual(len(restock_data), 1)
        self.assertEqual(
            restock_data[0]["reasons"],
            [REASON_EXPIRED, REASON_RUNNING_LOW],
        )
        self.assertEqual(restock_data[0]["qty_needed_grams"], PAR_LEVEL_G)


class TestBusinessSummary(unittest.TestCase):
    """Verify the Task 9 manager-facing business summary."""

    def test_summary_counts_delivered_and_not_delivered(self):
        """Mixed fulfilled and failed orders should produce matching counts."""
        processed_orders = [
            {"order_id": 1, "brand": "Taco Bell", "fulfilled": True, "reason": "Delivered"},
            {"order_id": 2, "brand": "Subway", "fulfilled": False, "reason": "Missing Bun"},
            {"order_id": 3, "brand": "Subway", "fulfilled": True, "reason": "Delivered"},
        ]
        inventory_data = [
            {"ingredient": "Bun", "qty_grams": 500, "expiry_date": "2026-12-31"}
        ]
        restock_data = []
        status_data = [
            {"order_id": 1, "delivered": True, "remark": "Delivered"},
            {"order_id": 2, "delivered": False, "remark": "Missing Bun"},
            {"order_id": 3, "delivered": True, "remark": "Delivered"},
        ]

        summary = build_business_summary(
            processed_orders,
            inventory_data,
            restock_data,
            status_data,
            reference_date=TEST_REFERENCE_DATE,
        )

        self.assertEqual(summary["orders_delivered"], 2)
        self.assertEqual(summary["orders_not_delivered"], 1)
        self.assertEqual(len(summary["delivered_orders"]), 2)
        self.assertEqual(len(summary["not_delivered_orders"]), 1)
        self.assertEqual(len(summary["not_delivered_orders"]), 1)

    def test_summary_lists_failed_orders_with_reasons(self):
        """Failed orders should include order id, brand, and plain-language reasons."""
        processed_orders = [
            {
                "order_id": 10,
                "brand": "Test Kitchen",
                "fulfilled": False,
                "reason": "Missing or insufficient ingredients: Bun",
            },
            {
                "order_id": 11,
                "brand": "Test Kitchen",
                "fulfilled": False,
                "reason": "Missing or insufficient ingredients: Flour (expired)",
            },
            {
                "order_id": 12,
                "brand": "Test Kitchen",
                "fulfilled": False,
                "reason": "No matching recipe for item(s): Mystery Wrap",
            },
        ]

        summary = build_business_summary(
            processed_orders,
            [],
            [],
            [],
            reference_date=TEST_REFERENCE_DATE,
        )

        self.assertEqual(len(summary["not_delivered_orders"]), 3)
        self.assertEqual(summary["not_delivered_orders"][0]["order_id"], 10)
        self.assertIn("Bun", summary["not_delivered_orders"][0]["reason"])
        self.assertIn("expired", summary["not_delivered_orders"][1]["reason"])
        self.assertIn("No matching recipe", summary["not_delivered_orders"][2]["reason"])

    def test_summary_includes_final_inventory(self):
        """The summary should snapshot final inventory quantities and expiry dates."""
        inventory_data = [
            {"ingredient": "Flour", "qty_grams": 4200, "expiry_date": "2026-05-12"},
            {"ingredient": "Bun", "qty_grams": 8000, "expiry_date": "2026-10-09"},
        ]

        summary = build_business_summary([], inventory_data, [], [])

        self.assertEqual(len(summary["final_inventory"]), 2)
        self.assertEqual(summary["final_inventory"][0]["ingredient"], "Flour")
        self.assertEqual(summary["final_inventory"][0]["qty_grams"], 4200)
        self.assertEqual(summary["final_inventory"][0]["expiry_date"], "2026-05-12")

    def test_summary_includes_restock_recommendations(self):
        """Restock rows should pass through unchanged with reasons and expiry fields."""
        restock_data = [
            {
                "item": "Romaine Lettuce",
                "current_qty_grams": 500,
                "reasons": [REASON_EXPIRING_SOON, REASON_RUNNING_LOW],
                "qty_needed_grams": PAR_LEVEL_G,
                "expiry_date": "2026-06-06",
                "days_until_expiry": 3,
            }
        ]

        summary = build_business_summary([], [], restock_data, [])

        self.assertEqual(len(summary["restock_recommendations"]), 1)
        self.assertEqual(
            summary["restock_recommendations"][0]["reasons"],
            [REASON_EXPIRING_SOON, REASON_RUNNING_LOW],
        )
        self.assertEqual(summary["restock_recommendations"][0]["qty_needed_grams"], PAR_LEVEL_G)
        self.assertEqual(summary["restock_recommendations"][0]["days_until_expiry"], 3)

    def test_summary_inventory_alerts_expired_and_expiring(self):
        """Expired and expiring-soon stock should appear in inventory alerts."""
        inventory_data = [
            {"ingredient": "Flour", "qty_grams": 5000, "expiry_date": "2026-05-12"},
            {"ingredient": "Cream", "qty_grams": 7000, "expiry_date": "2026-06-06"},
            {"ingredient": "Tomato Sauce", "qty_grams": 7000, "expiry_date": "2026-12-31"},
        ]

        summary = build_business_summary(
            [],
            inventory_data,
            [],
            [],
            reference_date=TEST_REFERENCE_DATE,
        )

        flour_alert = next(
            alert for alert in summary["inventory_alerts"] if alert["ingredient"] == "Flour"
        )
        cream_alert = next(
            alert for alert in summary["inventory_alerts"] if alert["ingredient"] == "Cream"
        )

        self.assertIn(REASON_EXPIRED, flour_alert["issues"])
        self.assertIn(REASON_EXPIRING_SOON, cream_alert["issues"])
        self.assertEqual(len(summary["expiry_concerns"]), 2)
        self.assertEqual(
            {alert["ingredient"] for alert in summary["expiry_concerns"]},
            {"Flour", "Cream"},
        )

    def test_summary_multi_reason_restock_preserved(self):
        """Multi-reason restock rows should remain unchanged in the summary."""
        restock_data = calculate_restock_needs(
            [{"ingredient": "Romaine Lettuce", "qty_grams": 500, "expiry_date": "2026-06-06"}],
            reference_date=TEST_REFERENCE_DATE,
        )

        summary = build_business_summary([], [], restock_data, [])

        self.assertEqual(
            summary["restock_recommendations"][0]["reasons"],
            [REASON_EXPIRING_SOON, REASON_RUNNING_LOW],
        )

    def test_summary_empty_processed_orders(self):
        """An empty order list should produce zero counts without errors."""
        summary = build_business_summary([], [], [], [])

        self.assertEqual(summary["orders_delivered"], 0)
        self.assertEqual(summary["orders_not_delivered"], 0)
        self.assertEqual(summary["delivered_orders"], [])
        self.assertEqual(summary["not_delivered_orders"], [])

    def test_summary_multiple_inventory_alert_issues(self):
        """One ingredient can report multiple stock and expiry issues."""
        alerts = build_inventory_alerts(
            [{"ingredient": "Flour", "qty_grams": 0, "expiry_date": "2026-05-12"}],
            reference_date=TEST_REFERENCE_DATE,
        )

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["issues"], [REASON_EXPIRED, REASON_OUT_OF_STOCK])

    def test_summary_integration_with_seed_orders(self):
        """A full seed simulation should align summary counts with status data."""
        recipe_data = load_recipes()
        inventory_data = deepcopy(load_inventory())
        order_data = load_orders()
        status_data = deepcopy(load_status())
        restock_data = []

        processed_orders = process_orders(
            recipe_data,
            inventory_data,
            order_data,
            status_data,
            restock_data,
            reference_date=TEST_REFERENCE_DATE,
        )
        summary = build_business_summary(
            processed_orders,
            inventory_data,
            restock_data,
            status_data,
            reference_date=TEST_REFERENCE_DATE,
        )

        delivered_from_status = sum(1 for entry in status_data if entry["delivered"])
        not_delivered_from_status = sum(1 for entry in status_data if not entry["delivered"])

        self.assertEqual(summary["orders_delivered"], delivered_from_status)
        self.assertEqual(summary["orders_not_delivered"], not_delivered_from_status)
        self.assertEqual(len(summary["final_inventory"]), len(inventory_data))
        self.assertIsInstance(summary["restock_recommendations"], list)
        self.assertGreater(len(summary["expiry_concerns"]), 0)
        self.assertEqual(len(summary["not_delivered_orders"]), not_delivered_from_status)


if __name__ == "__main__":
    unittest.main()
