import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    # 1. Constructor tests
    def test_constructor_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_constructor_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_constructor_zero_values(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_constructor_extreme_values(self):
        calc = OrderCalculator(tax_rate=1.0, free_shipping_threshold=1e9, shipping_cost=1e9)
        self.assertEqual(calc.tax_rate, 1.0)
        self.assertEqual(calc.free_shipping_threshold, 1e9)
        self.assertEqual(calc.shipping_cost, 1e9)

    def test_constructor_negative_tax(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_constructor_tax_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_constructor_negative_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_constructor_negative_shipping(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_constructor_non_numeric_params(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.1")
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="50")
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    # 2. Item Management tests
    def test_add_item_single(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.5)
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 1.5)

    def test_add_item_multiple(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.5)
        calc.add_item("Banana", 0.5, 2)
        self.assertEqual(calc.total_items(), 3)
        self.assertAlmostEqual(calc.get_subtotal(), 1.5 + 0.5 * 2)

    def test_add_item_duplicate_name(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Apple", 1.0, 3)
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 1.0 * 5)

    def test_add_item_zero_price(self):
        calc = OrderCalculator()
        calc.add_item("Freebie", 0.0, 4)
        self.assertEqual(calc.total_items(), 4)
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)

    def test_add_item_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Bulk", 2.0, 1000000)
        self.assertEqual(calc.total_items(), 1000000)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0 * 1000000)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Single")
        self.assertEqual(calc.total_items(), 1)

    def test_add_item_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("", 1.0)

    def test_add_item_none_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(None, 1.0)

    def test_add_item_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_negative_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Bad", -5.0)

    def test_add_item_non_float_price(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Bad", "5.0")

    def test_add_item_zero_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("ZeroQty", 1.0, 0)

    def test_add_item_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("NegQty", 1.0, -3)

    def test_add_item_non_int_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("FloatQty", 1.0, 2.5)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.remove_item("Apple")
        self.assertTrue(calc.is_empty())

    def test_remove_item_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        with self.assertRaises(KeyError):
            calc.remove_item("Apple")

    def test_remove_item_one_of_many(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.add_item("Banana", 0.5)
        calc.remove_item("Apple")
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.5)

    def test_remove_item_nonexistent(self):
        calc = OrderCalculator()
        with self.assertRaises(KeyError):
            calc.remove_item("NonExistent")

    def test_remove_item_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item("")

    def test_remove_item_none_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(None)

    def test_remove_item_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Banana", 0.5, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.remove_item("Apple")
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.add_item("Banana", 0.5)
        self.assertCountEqual(calc.list_items(), ["Apple", "Banana"])

    def test_list_items_insertion_order(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.add_item("Banana", 0.5)
        self.assertEqual(calc.list_items(), ["Apple", "Banana"])

    def test_list_items_immutability(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        items = calc.list_items()
        items.append("Fake")
        self.assertNotIn("Fake", calc.list_items())

    def test_is_empty_true(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_after_adding(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_subsequent_operations(self):
        calc = OrderCalculator()
        calc.clear_order()
        calc.add_item("Apple", 1.0)
        self.assertEqual(calc.total_items(), 1)

    # 3. Pricing Calculations
    def test_subtotal_empty(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)

    def test_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.5)
        self.assertAlmostEqual(calc.get_subtotal(), 1.5)

    def test_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.5)
        calc.add_item("Banana", 0.5, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 1.5 + 0.5 * 2)

    def test_subtotal_precision(self):
        calc = OrderCalculator()
        calc.add_item("Precise", 0.1)
        calc.add_item("Precise", 0.2)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3, places=7)

    def test_subtotal_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item("Large", 1e6, 1e6)
        self.assertAlmostEqual(calc.get_subtotal(), 1e12)

    def test_apply_discount_less(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100.0, 20.0)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_equal(self):
        calc = OrderCalculator()
        result = calc.apply_discount(50.0, 50.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_greater(self):
        calc = OrderCalculator()
        result = calc.apply_discount(30.0, 50.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        result = calc.apply_discount(30.0, 0.0)
        self.assertAlmostEqual(result, 30.0)

    def test_apply_discount_subtotal_zero(self):
        calc = OrderCalculator()
        result = calc.apply_discount(0.0, 10.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -10.0)

    def test_apply_discount_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, "10")

    def test_shipping_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        result = calc.calculate_shipping(60.0)
        self.assertAlmostEqual(result, 0.0)

    def test_shipping_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        result = calc.calculate_shipping(40.0)
        self.assertAlmostEqual(result, 10.0)

    def test_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        result = calc.calculate_shipping(10.0)
        self.assertAlmostEqual(result, 0.0)

    def test_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        result = calc.calculate_shipping(10.0)
        self.assertAlmostEqual(result, 0.0)

    def test_shipping_negative_subtotal(self):
        calc = OrderCalculator(shipping_cost=10.0)
        result = calc.calculate_shipping(-5.0)
        self.assertAlmostEqual(result, 10.0)

    def test_shipping_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping("10")

    def test_tax_positive(self):
        calc = OrderCalculator(tax_rate=0.2)
        result = calc.calculate_tax(100.0)
        self.assertAlmostEqual(result, 20.0)

    def test_tax_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        result = calc.calculate_tax(100.0)
        self.assertAlmostEqual(result, 0.0)

    def test_tax_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-10.0)

    def test_tax_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax("10")

    def test_total_no_discount(self):
        calc = OrderCalculator(tax_rate=0.1, shipping_cost=5.0, free_shipping_threshold=100.0)
        calc.add_item("Apple", 50.0)
        total = calc.calculate_total()
        expected = 50.0 + 5.0 + 5.0 * 0.1
        self.assertAlmostEqual(total, expected)

    def test_total_discount_less(self):
        calc = OrderCalculator(tax_rate=0.1, shipping_cost=5.0, free_shipping_threshold=100.0)
        calc.add_item("Apple", 50.0)
        total = calc.calculate_total(discount=20.0)
        discounted = 30.0
        expected = discounted + 5.0 + 5.0 * 0.1
        self.assertAlmostEqual(total, expected)

    def test_total_discount_equal(self):
        calc = OrderCalculator(tax_rate=0.1, shipping_cost=5.0, free_shipping_threshold=100.0)
        calc.add_item("Apple", 50.0)
        total = calc.calculate_total(discount=50.0)
        expected = 0.0 + 5.0 + 5.0 * 0.1
        self.assertAlmostEqual(total, expected)

    def test_total_discount_greater(self):
        calc = OrderCalculator(tax_rate=0.1, shipping_cost=5.0, free_shipping_threshold=100.0)
        calc.add_item("Apple", 50.0)
        total = calc.calculate_total(discount=60.0)
        expected = 0.0 + 5.0 + 5.0 * 0.1
        self.assertAlmostEqual(total, expected)

    def test_total_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0, shipping_cost=5.0, free_shipping_threshold=100.0)
        calc.add_item("Apple", 50.0)
        total = calc.calculate_total()
        expected = 50.0 + 5.0
        self.assertAlmostEqual(total, expected)

    def test_total_zero_shipping_cost(self):
        calc = OrderCalculator(tax_rate=0.1, shipping_cost=0.0, free_shipping_threshold=100.0)
        calc.add_item("Apple", 50.0)
        total = calc.calculate_total()
        expected = 50.0 + 0.0 + 50.0 * 0.1
        self.assertAlmostEqual(total, expected)

    def test_total_zero_free_shipping_threshold(self):
        calc = OrderCalculator(tax_rate=0.1, shipping_cost=5.0, free_shipping_threshold=0.0)
        calc.add_item("Apple", 50.0)
        total = calc.calculate_total()
        expected = 50.0 + 0.0 + 50.0 * 0.1
        self.assertAlmostEqual(total, expected)

    def test_total_all_zero(self):
        calc = OrderCalculator(tax_rate=0.0, shipping_cost=0.0, free_shipping_threshold=0.0)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 0.0)

    def test_total_large_numbers(self):
        calc = OrderCalculator(tax_rate=0.1, shipping_cost=5.0, free_shipping_threshold=100.0)
        calc.add_item("Large", 1e6, 1e6)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 1e12 + 5.0 + 1e12 * 0.1)

    def test_total_precision(self):
        calc = OrderCalculator(tax_rate=0.1, shipping_cost=5.0, free_shipping_threshold=100.0)
        calc.add_item("Precise", 0.1)
        total = calc.calculate_total()
        expected = 0.1 + 5.0 + 0.1 * 0.1
        self.assertAlmostEqual(total, expected, places=7)

    def test_total_negative_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-5.0)

    def test_total_non_numeric_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_total(discount="10")

    def test_total_edge_discount_greater_threshold_zero(self):
        calc = OrderCalculator(tax_rate=0.1, shipping_cost=5.0, free_shipping_threshold=0.0)
        calc.add_item("Apple", 50.0)
        total = calc.calculate_total(discount=60.0)
        expected = 0.0 + 0.0 + 0.0 * 0.1
        self.assertAlmostEqual(total, expected)

    def test_total_edge_discount_greater_shipping_cost(self):
        calc = OrderCalculator(tax_rate=0.1, shipping_cost=5.0, free_shipping_threshold=100.0)
        calc.add_item("Apple", 50.0)
        total = calc.calculate_total(discount=60.0)
        expected = 0.0 + 5.0 + 5.0 * 0.1
        self.assertAlmostEqual(total, expected)

    def test_total_edge_discount_greater_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.2, shipping_cost=5.0, free_shipping_threshold=100.0)
        calc.add_item("Apple", 50.0)
        total = calc.calculate_total(discount=60.0)
        expected = 0.0 + 5.0 + 5.0 * 0.2
        self.assertAlmostEqual(total, expected)

    def test_total_edge_discount_greater_tax_zero(self):
        calc = OrderCalculator(tax_rate=0.0, shipping_cost=5.0, free_shipping_threshold=100.0)
        calc.add_item("Apple", 50.0)
        total = calc.calculate_total(discount=60.0)
        expected = 0.0 + 5.0 + 5.0 * 0.0
        self.assertAlmostEqual(total, expected)

    def test_total_edge_discount_greater_shipping_zero(self):
        calc = OrderCalculator(tax_rate=0.1, shipping_cost=0.0, free_shipping_threshold=100.0)
        calc.add_item("Apple", 50.0)
        total = calc.calculate_total(discount=60.0)
        expected = 0.0 + 0.0 + 0.0 * 0.1
        self.assertAlmostEqual(total, expected)

    def test_total_state_no_mutation(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 50.0)
        subtotal_before = calc.get_subtotal()
        total = calc.calculate_total()
        self.assertAlmostEqual(calc.get_subtotal(), subtotal_before)

    def test_total_list_items_immutability(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        items = calc.list_items()
        items.append("Fake")
        self.assertNotIn("Fake", calc.list_items())

    # 4. State consistency tests
    def test_state_subtotal_and_count_after_add(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0)

    def test_state_subtotal_and_count_after_remove(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.remove_item("Apple")
        self.assertEqual(calc.total_items(), 0)
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)

    def test_state_all_getters_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.total_items(), 0)
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)
        self.assertEqual(calc.list_items(), [])

    def test_state_remove_nonexistent_exception(self):
        calc = OrderCalculator()
        with self.assertRaises(KeyError):
            calc.remove_item("Missing")

    def test_state_duplicate_names_list_items(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Apple", 1.0, 3)
        self.assertCountEqual(calc.list_items(), ["Apple"])

    def test_state_duplicate_names_total_items(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Apple", 1.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_state_duplicate_names_subtotal(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Apple", 1.0, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 5.0)

    def test_state_calculate_total_after_add(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 50.0)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 50.0 + 10.0 + 50.0 * 0.23)

    def test_state_calculate_total_no_mutation(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 50.0)
        subtotal_before = calc.get_subtotal()
        calc.calculate_total()
        self.assertAlmostEqual(calc.get_subtotal(), subtotal_before)

    # 5. Edge cases
    def test_edge_zero_all_numeric(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        calc.add_item("Zero", 0.0, 0)
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)
        self.assertAlmostEqual(calc.calculate_total(), 0.0)

    def test_edge_large_numeric(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=1e9, shipping_cost=1e9)
        calc.add_item("Huge", 1e9, 1e9)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 1e18 + 1e9 + 1e18 * 0.1)

    def test_edge_floating_rounding(self):
        calc = OrderCalculator()
        calc.add_item("Float", 0.1)
        calc.add_item("Float", 0.2)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3, places=7)

    def test_edge_negative_inputs_all(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Neg", -1.0)
        with self.assertRaises(ValueError):
            calc.add_item("NegQty", 1.0, -2)
        with self.assertRaises(ValueError):
            calc.apply_discount(10.0, -5.0)
        with self.assertRaises(ValueError):
            calc.calculate_tax(-10.0)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-5.0)

    def test_edge_duplicate_names_case_sensitive(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.add_item("apple", 2.0)
        self.assertCountEqual(calc.list_items(), ["Apple", "apple"])
        self.assertEqual(calc.total_items(), 2)

    def test_edge_non_string_names_special_chars(self):
        calc = OrderCalculator()
        calc.add_item("Café", 1.5)
        calc.add_item("naïve", 2.5)
        self.assertCountEqual(calc.list_items(), ["Café", "naïve"])

    def test_edge_non_numeric_price_quantity_after_add(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("BadPrice", "5.0")
        with self.assertRaises(TypeError):
            calc.add_item("BadQty", 1.0, "3")

    def test_edge_remove_from_empty(self):
        calc = OrderCalculator()
        with self.assertRaises(KeyError):
            calc.remove_item("Nothing")

    def test_edge_clear_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

if __name__ == "__main__":
    unittest.main()