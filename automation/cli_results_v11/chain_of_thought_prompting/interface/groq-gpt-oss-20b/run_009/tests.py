import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default(self):
        self.assertTrue(self.calc.is_empty())
        self.assertAlmostEqual(self.calc.calculate_tax(100), 23.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(0), 10.0)

    def test_init_custom(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=5)
        self.assertAlmostEqual(calc.calculate_tax(100), 10.0)
        self.assertAlmostEqual(calc.calculate_shipping(49), 5)
        self.assertAlmostEqual(calc.calculate_shipping(50), 0.0)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-50)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_single(self):
        self.calc.add_item("apple", 0.5, 1)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 1)
        self.assertListEqual(self.calc.list_items(), ["apple"])
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.5)

    def test_add_item_duplicate_same_price(self):
        self.calc.add_item("apple", 0.5, 1)
        self.calc.add_item("apple", 0.5, 2)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.5)

    def test_add_item_duplicate_different_price(self):
        self.calc.add_item("apple", 0.5, 1)
        self.calc.add_item("apple", 0.6, 1)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("zero", 1.0, 0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("neg", 1.0, -1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("bad", -5.0)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 1.0)

    def test_add_item_non_string_name(self):
        with self.assertRaises((ValueError, TypeError)):
            self.calc.add_item(None, 1.0)

    def test_remove_item_existing(self):
        self.calc.add_item("apple", 0.5)
        self.calc.remove_item("apple")
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    def test_remove_item_nonexistent(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item("ghost")

    def test_remove_item_after_clearing(self):
        self.calc.clear_order()
        with self.assertRaises(KeyError):
            self.calc.remove_item("apple")

    def test_get_subtotal_empty(self):
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    def test_get_subtotal_multiple(self):
        self.calc.add_item("book", 12.99)
        self.calc.add_item("pen", 1.5, 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 12.99 + 1.5 * 4)

    def test_get_subtotal_floating_point(self):
        self.calc.add_item("item", 0.1, 3)
        self.calc.add_item("item2", 0.2, 2)
        expected = 0.1 * 3 + 0.2 * 2
        self.assertAlmostEqual(self.calc.get_subtotal(), expected, places=6)

    def test_apply_discount_normal(self):
        result = self.calc.apply_discount(20, 5)
        self.assertAlmostEqual(result, 15.0)

    def test_apply_discount_equal(self):
        result = self.calc.apply_discount(20, 20)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_greater(self):
        result = self.calc.apply_discount(20, 30)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(20, -5)

    def test_calculate_shipping_below_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(50), 10.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(150), 0.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(100), 0.0)

    def test_calculate_shipping_just_below_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_negative_subtotal(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(-10), 10.0)

    def test_calculate_tax_positive(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100), 23.0)

    def test_calculate_tax_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0), 0.0)

    def test_calculate_tax_negative(self):
        self.assertAlmostEqual(self.calc.calculate_tax(-10), -2.3)

    def test_calculate_total_no_discount_below_threshold(self):
        self.calc.add_item("book", 12.99)
        total = self.calc.calculate_total()
        expected = 12.99 + self.calc.calculate_tax(12.99) + self.calc.calculate_shipping(12.99)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_no_discount_above_threshold(self):
        self.calc.add_item("expensive", 150)
        total = self.calc.calculate_total()
        expected = 150 + self.calc.calculate_tax(150)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_less(self):
        self.calc.add_item("book", 20)
        total = self.calc.calculate_total(5)
        discounted = 15
        expected = discounted + self.calc.calculate_tax(discounted) + self.calc.calculate_shipping(discounted)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_equal(self):
        self.calc.add_item("book", 20)
        total = self.calc.calculate_total(20)
        discounted = 0
        expected = self.calc.calculate_tax(0) + self.calc.calculate_shipping(0)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_greater(self):
        self.calc.add_item("book", 20)
        total = self.calc.calculate_total(30)
        discounted = 0
        expected = self.calc.calculate_tax(0) + self.calc.calculate_shipping(0)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-5)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_multiple(self):
        self.calc.add_item("book", 10, 2)
        self.calc.add_item("pen", 1, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order_normal(self):
        self.calc.add_item("book", 10)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_already_empty(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items_empty(self):
        self.assertListEqual(self.calc.list_items(), [])

    def test_list_items_multiple(self):
        self.calc.add_item("book", 10)
        self.calc.add_item("pen", 1)
        self.assertCountEqual(self.calc.list_items(), ["book", "pen"])

    def test_list_items_case_sensitive(self):
        self.calc.add_item("Apple", 1)
        self.calc.add_item("apple", 1)
        self.assertCountEqual(self.calc.list_items(), ["Apple", "apple"])

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item("book", 1)
        self.assertFalse(self.calc.is_empty())

    def test_interaction_add_remove_total(self):
        self.calc.add_item("item", 5)
        self.calc.remove_item("item")
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 0.0)

    def test_interaction_add_discount_remove_total(self):
        self.calc.add_item("item", 20)
        total1 = self.calc.calculate_total(5)
        self.calc.remove_item("item")
        total2 = self.calc.calculate_total(5)
        discounted = 15
        expected1 = discounted + self.calc.calculate_tax(discounted) + self.calc.calculate_shipping(discounted)
        self.assertAlmostEqual(total1, expected1)
        self.assertAlmostEqual(total2, 0.0)

    def test_interaction_add_clear_list(self):
        self.calc.add_item("item", 5)
        self.calc.clear_order()
        self.assertListEqual(self.calc.list_items(), [])

    def test_interaction_add_duplicate_quantity(self):
        self.calc.add_item("c", 3, 1)
        self.calc.add_item("c", 3, 2)
        self.assertEqual(self.calc.total_items(), 3)

    def test_interaction_duplicate_price_handling(self):
        self.calc.add_item("d", 2, 1)
        self.calc.add_item("d", 3, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5)

    def test_interaction_discount_shipping(self):
        self.calc.add_item("item", 90)
        total = self.calc.calculate_total(5)
        discounted = 85
        expected = discounted + self.calc.calculate_tax(discounted) + self.calc.calculate_shipping(discounted)
        self.assertAlmostEqual(total, expected)

    def test_interaction_discount_free_shipping(self):
        self.calc.add_item("item", 120)
        total = self.calc.calculate_total(20)
        discounted = 100
        expected = discounted + self.calc.calculate_tax(discounted) + self.calc.calculate_shipping(discounted)
        self.assertAlmostEqual(total, expected)

    def test_interaction_remove_nonexistent_after_clearing(self):
        self.calc.clear_order()
        with self.assertRaises(KeyError):
            self.calc.remove_item("ghost")

    def test_interaction_multiple_discounts(self):
        self.calc.add_item("item", 50)
        total1 = self.calc.calculate_total(10)
        total2 = self.calc.calculate_total(20)
        expected1 = 40 + self.calc.calculate_tax(40) + self.calc.calculate_shipping(40)
        expected2 = 30 + self.calc.calculate_tax(30) + self.calc.calculate_shipping(30)
        self.assertAlmostEqual(total1, expected1)
        self.assertAlmostEqual(total2, expected2)

    def test_interaction_tax_on_shipping_only(self):
        self.calc.add_item("item", 10)
        total = self.calc.calculate_total(20)
        expected = 10 + self.calc.calculate_tax(10)
        self.assertAlmostEqual(total, expected)

    def test_interaction_negative_tax_rate_after_construction(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_interaction_negative_free_shipping_threshold_after_construction(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-50)

    def test_interaction_negative_shipping_cost_after_construction(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_edge_floating_point_precision(self):
        self.calc.add_item("a", 0.1, 3)
        self.calc.add_item("b", 0.2, 2)
        subtotal = self.calc.get_subtotal()
        total = self.calc.calculate_total()
        expected_subtotal = 0.1 * 3 + 0.2 * 2
        expected_total = expected_subtotal + self.calc.calculate_tax(expected_subtotal) + self.calc.calculate_shipping(expected_subtotal)
        self.assertAlmostEqual(subtotal, expected_subtotal, places=6)
        self.assertAlmostEqual(total, expected_total, places=6)

    def test_edge_large_quantity(self):
        self.calc.add_item("big", 1, 1000000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1000000)
        self.assertEqual(self.calc.total_items(), 1000000)

    def test_edge_large_price(self):
        self.calc.add_item("exp", 1000000, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1000000)

    def test_edge_very_small_price(self):
        self.calc.add_item("tiny", 0.0001, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0001)

    def test_edge_large_discount(self):
        self.calc.add_item("item", 10)
        total = self.calc.calculate_total(1000)
        expected = self.calc.calculate_shipping(0) + self.calc.calculate_tax(self.calc.calculate_shipping(0))
        self.assertAlmostEqual(total, expected)

    def test_edge_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item("item", 10)
        total = calc.calculate_total()
        expected = 10 + calc.calculate_shipping(10)
        self.assertAlmostEqual(total, expected)

    def test_edge_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item("item", 10)
        total = calc.calculate_total()
        expected = 10 + calc.calculate_tax(10)
        self.assertAlmostEqual(total, expected)

    def test_edge_zero_free_shipping_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item("item", 10)
        total = calc.calculate_total()
        expected = 10 + calc.calculate_tax(10)
        self.assertAlmostEqual(total, expected)

    def test_edge_empty_name_whitespace(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("   ", 1.0)

    def test_edge_non_string_name_whitespace(self):
        with self.assertRaises((ValueError, TypeError)):
            self.calc.add_item(123, 1.0)

    def test_edge_price_as_integer(self):
        self.calc.add_item("intprice", 5, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5.0)

    def test_edge_quantity_as_float(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("floatqty", 1.0, 2.5)

    def test_edge_negative_quantity_as_float(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("negfloat", 1.0, -1.0)

    def test_edge_removing_item_after_clearing(self):
        self.calc.clear_order()
        with self.assertRaises(KeyError):
            self.calc.remove_item("apple")

    def test_edge_list_items_after_clearing(self):
        self.calc.clear_order()
        self.assertListEqual(self.calc.list_items(), [])

    def test_edge_total_items_after_clearing(self):
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_edge_total_after_clearing_and_adding(self):
        self.calc.clear_order()
        self.calc.add_item("new", 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5)

    def test_edge_repeatedly_add_remove_same_item(self):
        self.calc.add_item("repeat", 1, 1)
        self.calc.remove_item("repeat")
        self.calc.add_item("repeat", 1, 1)
        self.assertEqual(self.calc.total_items(), 1)

    def test_edge_removing_item_with_different_case(self):
        self.calc.add_item("Apple", 1)
        with self.assertRaises(KeyError):
            self.calc.remove_item("apple")

    def test_edge_long_name(self):
        long_name = "a" * 10000
        self.calc.add_item(long_name, 1)
        self.assertIn(long_name, self.calc.list_items())

    def test_edge_special_characters(self):
        self.calc.add_item("café", 1)
        self.assertIn("café", self.calc.list_items())

    def test_edge_price_string(self):
        with self.assertRaises((ValueError, TypeError)):
            self.calc.add_item("strprice", "10.99")

    def test_edge_calculate_total_no_items_discount(self):
        total = self.calc.calculate_total(5)
        self.assertAlmostEqual(total, 0.0)

    def test_edge_calculate_tax_negative_amount(self):
        tax = self.calc.calculate_tax(-10)
        self.assertAlmostEqual(tax, -2.3)

    def test_edge_calculate_shipping_negative_subtotal(self):
        shipping = self.calc.calculate_shipping(-10)
        self.assertAlmostEqual(shipping, 10.0)

    def test_edge_apply_discount_negative_subtotal(self):
        result = self.calc.apply_discount(-10, 5)
        self.assertAlmostEqual(result, 0.0)

    def test_edge_list_items_unique(self):
        self.calc.add_item("pen", 1, 2)
        self.calc.add_item("pen", 1, 3)
        self.assertCountEqual(self.calc.list_items(), ["pen"])

    def test_edge_total_items_duplicate(self):
        self.calc.add_item("pen", 1, 2)
        self.calc.add_item("pen", 1, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_edge_calculate_total_floating_point(self):
        self.calc.add_item("a", 0.333333, 3)
        self.calc.add_item("b", 0.666667, 2)
        subtotal = self.calc.get_subtotal()
        total = self.calc.calculate_total()
        expected_subtotal = 0.333333 * 3 + 0.666667 * 2
        expected_total = expected_subtotal + self.calc.calculate_tax(expected_subtotal) + self.calc.calculate_shipping(expected_subtotal)
        self.assertAlmostEqual(subtotal, expected_subtotal, places=6)
        self.assertAlmostEqual(total, expected_total, places=6)

    def test_edge_tax_rate_100_percent(self):
        calc = OrderCalculator(tax_rate=1.0)
        calc.add_item("item", 10)
        total = calc.calculate_total()
        expected = 10 + 10 + calc.calculate_shipping(10)
        self.assertAlmostEqual(total, expected)

    def test_edge_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item("item", 10)
        total = calc.calculate_total()
        expected = 10 + calc.calculate_tax(10)
        self.assertAlmostEqual(total, expected)

    def test_edge_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item("item", 10)
        total = calc.calculate_total()
        expected = 10 + calc.calculate_tax(10)
        self.assertAlmostEqual(total, expected)

    def test_edge_high_tax_rate(self):
        calc = OrderCalculator(tax_rate=10.0)
        calc.add_item("item", 10)
        total = calc.calculate_total()
        expected = 10 + 100 + calc.calculate_shipping(10)
        self.assertAlmostEqual(total, expected)

    def test_edge_high_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=1000000)
        calc.add_item("item", 10)
        total = calc.calculate_total()
        expected = 10 + calc.calculate_tax(10) + 1000000
        self.assertAlmostEqual(total, expected)

    def test_edge_high_free_shipping_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=1000000)
        calc.add_item("item", 10)
        total = calc.calculate_total()
        expected = 10 + calc.calculate_tax(10) + 10
        self.assertAlmostEqual(total, expected)

    def test_edge_calculate_total_after_clear(self):
        self.calc.add_item("item", 10)
        self.calc.clear_order()
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 0.0)

    def test_edge_calculate_total_after_removing_all(self):
        self.calc.add_item("item1", 5)
        self.calc.add_item("item2", 10)
        self.calc.remove_item("item1")
        self.calc.remove_item("item2")
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 0.0)

    def test_edge_discount_exactly_equals_shipping_cost(self):
        self.calc.add_item("item", 90)
        total = self.calc.calculate_total(5)
        self.assertAlmostEqual(self.calc.calculate_shipping(85), 10.0)

    def test_edge_discount_pushed_subtotal_below_zero_shipping_applies(self):
        self.calc.add_item("item", 10)
        total = self.calc.calculate_total(20)
        self.assertAlmostEqual(self.calc.calculate_shipping(0), 10.0)

    def test_edge_discount_pushed_subtotal_below_zero_and_threshold_met(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item("item", 10)
        total = calc.calculate_total(20)
        self.assertAlmostEqual(calc.calculate_shipping(0), 0.0)

    def test_edge_discount_pushed_subtotal_below_zero_and_threshold_not_met(self):
        self.calc.add_item("item", 10)
        total = self.calc.calculate_total(20)
        self.assertAlmostEqual(self.calc.calculate_shipping(0), 10.0)

if __name__ == "__main__":
    unittest.main()