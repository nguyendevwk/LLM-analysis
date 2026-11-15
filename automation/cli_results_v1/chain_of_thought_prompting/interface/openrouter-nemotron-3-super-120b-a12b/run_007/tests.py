import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=0.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_edge_values(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)
        calc2 = OrderCalculator(tax_rate=1.0, free_shipping_threshold=1e12, shipping_cost=1e12)
        self.assertEqual(calc2.tax_rate, 1.0)
        self.assertEqual(calc2.free_shipping_threshold, 1e12)
        self.assertEqual(calc2.shipping_cost, 1e12)

    def test_init_negative_input(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_type_mismatch(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.23")
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    def test_add_item_normal_use(self):
        calc = OrderCalculator()
        calc.add_item("apple", 1.0, 2)
        self.assertIn("apple", calc.list_items())
        self.assertEqual(calc.total_items(), 2)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item("banana", 0.5)
        self.assertIn("banana", calc.list_items())
        self.assertEqual(calc.total_items(), 1)

    def test_add_item_multiple_additions_same_name_aggregation(self):
        calc = OrderCalculator()
        calc.add_item("orange", 0.8, 2)
        calc.add_item("orange", 0.8, 3)
        self.assertEqual(calc.total_items(), 5)
        self.assertEqual(calc.list_items().count("orange"), 1)

    def test_add_item_multiple_additions_same_name_separate_entries(self):
        calc = OrderCalculator()
        calc.add_item("orange", 0.8, 2)
        calc.add_item("orange", 0.8, 3)
        self.assertEqual(calc.list_items().count("orange"), 2)
        self.assertEqual(calc.total_items(), 5)

    def test_add_item_zero_quantity(self):
        calc = OrderCalculator()
        initial_total = calc.total_items()
        calc.add_item("pear", 0.5, 0)
        self.assertEqual(calc.total_items(), initial_total)

    def test_add_item_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("pear", 0.5, -1)

    def test_add_item_negative_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("discount", -5.0, 1)

    def test_add_item_zero_price(self):
        calc = OrderCalculator()
        calc.add_item("freebie", 0.0, 1)
        self.assertIn("freebie", calc.list_items())
        self.assertEqual(calc.total_items(), 1)

    def test_add_item_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(None, 1.0, 1)
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            calc.add_item([], 1.0, 1)

    def test_add_item_non_numeric_price_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("item", "price", 1)
        with self.assertRaises(TypeError):
            calc.add_item("item", 1.0, "qty")

    def test_add_item_very_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item("big", 1e12, 10**10)
        self.assertEqual(calc.total_items(), 10**10)
        self.assertAlmostEqual(calc.get_subtotal(), 1e12 * 10**10)

    def test_remove_item_normal_use(self):
        calc = OrderCalculator()
        calc.add_item("item", 10.0, 1)
        calc.remove_item("item")
        self.assertNotIn("item", calc.list_items())
        self.assertEqual(calc.total_items(), 0)

    def test_remove_item_non_existent_item(self):
        calc = OrderCalculator()
        calc.remove_item("nonexistent")
        self.assertEqual(calc.total_items(), 0)

    def test_remove_item_multiple_removals_same_name(self):
        calc = OrderCalculator()
        calc.add_item("item", 10.0, 1)
        calc.remove_item("item")
        calc.remove_item("item")
        self.assertNotIn("item", calc.list_items())
        self.assertEqual(calc.total_items(), 0)

    def test_remove_item_invalid_name_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(None)
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_empty_string_name(self):
        calc = OrderCalculator()
        calc.add_item("", 5.0, 1)
        calc.remove_item("")
        self.assertEqual(calc.total_items(), 0)

    def test_get_subtotal_empty_order(self):
        calc = OrderCalculator()
        self.assertEqual(calc.get_subtotal(), 0.0)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item("book", 12.0, 3)
        self.assertEqual(calc.get_subtotal(), 36.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item("a", 2.0, 2)
        calc.add_item("b", 3.0, 4)
        self.assertEqual(calc.get_subtotal(), 2*2 + 3*4)

    def test_get_subtotal_zero_price_items(self):
        calc = OrderCalculator()
        calc.add_item("free", 0.0, 5)
        calc.add_item("costly", 10.0, 1)
        self.assertEqual(calc.get_subtotal(), 10.0)

    def test_get_subtotal_negative_prices_if_allowed(self):
        calc = OrderCalculator()
        calc.add_item("refund", -5.0, 2)
        self.assertEqual(calc.get_subtotal(), -10.0)

    def test_get_subtotal_floating_point_precision(self):
        calc = OrderCalculator()
        calc.add_item("x", 0.1, 1)
        calc.add_item("y", 0.2, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3, places=7)

    def test_get_subtotal_after_removal_clear(self):
        calc = OrderCalculator()
        calc.add_item("a", 5.0, 2)
        calc.add_item("b", 3.0, 1)
        calc.remove_item("a")
        self.assertEqual(calc.get_subtotal(), 3.0)
        calc.clear_order()
        self.assertEqual(calc.get_subtotal(), 0.0)

    def test_apply_discount_normal_use(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100.0, 0.10)
        self.assertEqual(result, 90.0)

    def test_apply_discount_zero_discount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full_discount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(80.0, 1.0), 0.0)

    def test_apply_discount_over_100_percent(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 1.5), -50.0)

    def test_apply_discount_negative_discount_surcharge(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, -0.2), 120.0)

    def test_apply_discount_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount("100", 0.1)
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, "0.1")

    def test_apply_discount_extreme_values(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(1.0, 1e-9), 1.0 * (1 - 1e-9))
        self.assertAlmostEqual(calc.apply_discount(1.0, 1e6), 1.0 * (1 - 1e6))

    def test_calculate_shipping_free_shipping_threshold_met(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_shipping_cost_applied(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(40.0), 10.0)

    def test_calculate_shipping_exact_threshold_inclusive(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(30.0), 0.0)

    def test_calculate_shipping_zero_free_shipping_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)

    def test_calculate_shipping_negative_threshold_or_cost_if_allowed(self):
        calc = OrderCalculator(free_shipping_threshold=-10.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(5.0), 0.0)

    def test_calculate_shipping_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping("50")

    def test_calculate_tax_normal_use(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(150.0), 0.0)

    def test_calculate_tax_negative_amount_if_allowed(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(-50.0), -11.5)

    def test_calculate_tax_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax("100")

    def test_calculate_tax_large_numbers(self):
        calc = OrderCalculator()
        big = 1e12
        self.assertAlmostEqual(calc.calculate_tax(big), big * 0.23)

    def test_calculate_total_normal_use_no_discount(self):
        calc = OrderCalculator()
        calc.add_item("a", 10.0, 2)
        calc.add_item("b", 5.0, 3)
        expected = 55.35
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_explicit_discount(self):
        calc = OrderCalculator()
        calc.add_item("a", 100.0, 1)
        expected = 123.0
        self.assertAlmostEqual(calc.calculate_total(discount=0.1), expected)

    def test_calculate_total_discount_triggers_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item("item", 80.0, 1)
        expected = 68.88
        self.assertAlmostEqual(calc.calculate_total(discount=0.3), expected)

    def test_calculate_total_discount_exceeding_subtotal(self):
        calc = OrderCalculator()
        calc.add_item("item", 10.0, 1)
        expected = 6.15
        self.assertAlmostEqual(calc.calculate_total(discount=1.5), expected)

    def test_calculate_total_invalid_discount_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_total(discount="0.1")

    def test_calculate_total_empty_order(self):
        calc = OrderCalculator()
        expected = 12.3
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_state_changes(self):
        calc = OrderCalculator()
        calc.add_item("a", 10.0, 1)
        total1 = calc.calculate_total()
        calc.remove_item("a")
        total2 = calc.calculate_total()
        self.assertNotEqual(total1, total2)
        expected_empty = 12.3
        self.assertAlmostEqual(total2, expected_empty)

    def test_calculate_total_floating_point_tolerance(self):
        calc = OrderCalculator()
        calc.add_item("a", 0.1, 1)
        calc.add_item("b", 0.2, 1)
        expected = 12.669
        self.assertAlmostEqual(calc.calculate_total(), expected, places=7)

    def test_total_items_empty_order(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item("item", 5.0, 4)
        self.assertEqual(calc.total_items(), 4)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 2)
        calc.add_item("b", 2.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item("item", 1.0, 3)
        calc.remove_item("item")
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("item", 1.0, 5)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_non_integer_quantities_if_ever_allowed(self):
        calc = OrderCalculator()
        calc.add_item("item", 1.0, 2)
        self.assertEqual(calc.total_items(), 2)

    def test_total_items_very_large_quantities(self):
        calc = OrderCalculator()
        huge = 10**100
        calc.add_item("item", 1.0, huge)
        self.assertEqual(calc.total_items(), huge)

    def test_clear_order_normal_use(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.get_subtotal(), 0.0)
        self.assertEqual(calc.list_items(), [])

    def test_clear_order_idempotence(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        calc.clear_order()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_state_after_other_operations(self):
        calc = OrderCalculator()
        calc.add_item("old", 1.0, 1)
        calc.clear_order()
        calc.add_item("new", 2.0, 1)
        self.assertEqual(calc.list_items(), ["new"])
        self.assertEqual(calc.total_items(), 1)

    def test_clear_order_return_value(self):
        calc = OrderCalculator()
        self.assertIsNone(calc.clear_order())

    def test_list_items_empty_order(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item("only", 1.0, 1)
        self.assertEqual(calc.list_items(), ["only"])

    def test_list_items_multiple_distinct_items(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        calc.add_item("b", 1.0, 1)
        calc.add_item("c", 1.0, 1)
        self.assertEqual(sorted(calc.list_items()), ["a", "b", "c"])

    def test_list_items_duplicate_names_aggregated(self):
        calc = OrderCalculator()
        calc.add_item("dup", 1.0, 2)
        calc.add_item("dup", 1.0, 3)
        self.assertEqual(calc.list_items(), ["dup"])

    def test_list_items_duplicate_names_separate_entries(self):
        calc = OrderCalculator()
        calc.add_item("dup", 1.0, 2)
        calc.add_item("dup", 1.0, 3)
        self.assertEqual(len(calc.list_items()), 2)
        self.assertEqual(calc.list_items().count("dup"), 2)

    def test_list_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        calc.add_item("b", 1.0, 1)
        calc.remove_item("a")
        self.assertEqual(calc.list_items(), ["b"])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_order_preservation(self):
        calc = OrderCalculator()
        calc.add_item("first", 1.0, 1)
        calc.add_item("second", 1.0, 1)
        calc.add_item("third", 1.0, 1)
        self.assertEqual(calc.list_items(), ["first", "second", "third"])

    def test_list_items_return_type_and_immutability(self):
        calc = OrderCalculator()
        calc.add_item("item", 1.0, 1)
        lst = calc.list_items()
        self.assertIsInstance(lst, list)
        for elem in lst:
            self.assertIsInstance(elem, str)
        lst.append("extra")
        self.assertNotIn("extra", calc.list_items())

    def test_is_empty_empty_order(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_adding_items(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_removing_all_items(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 2)
        calc.remove_item("a")
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_zero_quantity_items_if_allowed(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 0)
        self.assertTrue(calc.is_empty())

    def test_is_empty_return_type(self):
        calc = OrderCalculator()
        self.assertIsInstance(calc.is_empty(), bool)

if __name__ == '__main__':
    unittest.main()