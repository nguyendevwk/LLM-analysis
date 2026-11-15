import unittest
import sys
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def test_constructor_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_constructor_custom_values(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_constructor_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_constructor_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_constructor_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_constructor_large_numbers(self):
        large = 1e108
        calc = OrderCalculator(tax_rate=large, free_shipping_threshold=large, shipping_cost=large)
        self.assertEqual(calc.tax_rate, large)
        self.assertEqual(calc.free_shipping_threshold, large)
        self.assertEqual(calc.shipping_cost, large)

    def test_constructor_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.23")

    def test_constructor_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_constructor_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    def test_constructor_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_constructor_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    def test_constructor_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_add_item_normal_use(self):
        calc = OrderCalculator()
        calc.add_item("apple", 1.0, 2)
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0)
        self.assertListEqual(sorted(calc.list_items()), ["apple"])

    def test_add_item_multiple_distinct(self):
        calc = OrderCalculator()
        calc.add_item("apple", 1.0, 1)
        calc.add_item("banana", 0.5, 4)
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 1.0 + 0.5*4)
        self.assertListEqual(sorted(calc.list_items()), ["apple", "banana"])

    def test_add_item_same_name_aggregates(self):
        calc = OrderCalculator()
        calc.add_item("apple", 1.0, 2)
        calc.add_item("apple", 1.0, 3)
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 5.0)
        self.assertListEqual(calc.list_items(), ["apple"])

    def test_add_item_price_zero(self):
        calc = OrderCalculator()
        calc.add_item("freebie", 0.0, 3)
        self.assertEqual(calc.total_items(), 3)
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)
        self.assertListEqual(calc.list_items(), ["freebie"])

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item("item", 2.5)
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 2.5)

    def test_add_item_large_quantity(self):
        calc = OrderCalculator()
        qty = sys.maxsize
        calc.add_item("big", 0.01, qty)
        self.assertEqual(calc.total_items(), qty)
        self.assertAlmostEqual(calc.get_subtotal(), 0.01 * qty)

    def test_add_item_fractional_price_rounding(self):
        calc = OrderCalculator()
        calc.add_item("a", 0.1, 1)
        calc.add_item("b", 0.2, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3, places=7)

    def test_add_item_invalid_name_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(None, 1.0, 1)
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            calc.add_item([], 1.0, 1)

    def test_add_item_negative_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("item", -1.0, 1)

    def test_add_item_non_numeric_price(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("item", "5.0", 1)

    def test_add_item_zero_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("item", 1.0, 0)

    def test_add_item_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("item", 1.0, -1)

    def test_add_item_non_int_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("item", 1.0, 2.5)
        with self.assertRaises(TypeError):
            calc.add_item("item", 1.0, "2")

    def test_add_item_then_clear_then_add(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        calc.clear_order()
        calc.add_item("b", 2.0, 1)
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0)
        self.assertListEqual(calc.list_items(), ["b"])

    def test_remove_item_normal_use(self):
        calc = OrderCalculator()
        calc.add_item("apple", 1.0, 2)
        calc.remove_item("apple")
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.total_items(), 0)
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)
        self.assertListEqual(calc.list_items(), [])

    def test_remove_item_multiple_quantity(self):
        calc = OrderCalculator()
        calc.add_item("apple", 1.0, 5)
        calc.remove_item("apple")
        self.assertTrue(calc.is_empty())

    def test_remove_item_nonexistent_silent_noop(self):
        calc = OrderCalculator()
        calc.add_item("apple", 1.0, 1)
        calc.remove_item("orange")  # should not raise
        self.assertFalse(calc.is_empty())
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 1.0)

    def test_remove_item_on_empty_order(self):
        calc = OrderCalculator()
        calc.remove_item("any")  # should not raise
        self.assertTrue(calc.is_empty())

    def test_remove_item_empty_string_name(self):
        calc = OrderCalculator()
        calc.add_item("", 1.0, 1)
        calc.remove_item("")
        self.assertTrue(calc.is_empty())

    def test_remove_item_invalid_name_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(None)
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_state_interaction(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        calc.add_item("b", 2.0, 2)
        calc.remove_item("a")
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 4.0)
        self.assertListEqual(calc.list_items(), ["b"])

    def test_remove_item_idempotent_nonexistent(self):
        calc = OrderCalculator()
        calc.remove_item("ghost")
        calc.remove_item("ghost")
        self.assertTrue(calc.is_empty())

    def test_get_subtotal_normal_use(self):
        calc = OrderCalculator()
        calc.add_item("a", 2.5, 2)
        calc.add_item("b", 1.0, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 2.5*2 + 1.0*3)

    def test_get_subtotal_empty_order(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)

    def test_get_subtotal_zero_price_items(self):
        calc = OrderCalculator()
        calc.add_item("free", 0.0, 5)
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)

    def test_get_subtotal_fractional_rounding(self):
        calc = OrderCalculator()
        calc.add_item("a", 0.1, 1)
        calc.add_item("b", 0.2, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3, places=7)

    def test_get_subtotal_unchanged_by_apply_discount(self):
        calc = OrderCalculator()
        calc.add_item("a", 10.0, 1)
        subtotal_before = calc.get_subtotal()
        calc.apply_discount(subtotal_before, 2.0)  # does not affect state
        self.assertAlmostEqual(calc.get_subtotal(), subtotal_before)

    def test_get_subtotal_idempotent(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        v1 = calc.get_subtotal()
        v2 = calc.get_subtotal()
        v3 = calc.get_subtotal()
        self.assertEqual(v1, v2)
        self.assertEqual(v2, v3)

    def test_apply_discount_normal_use(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 10.0), 90.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_equals_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(20.0, 20.0), 0.0)

    def test_apply_discount_greater_than_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(10.0, 15.0)

    def test_apply_discount_small_discount(self):
        calc = OrderCalculator()
        result = calc.apply_discount(1.0, 1e-12)
        self.assertAlmostEqual(result, 1.0 - 1e-12)

    def test_apply_discount_subtotal_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(0.0, 5.0), 0.0)  # clamp to zero

    def test_apply_discount_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-5.0, 1.0)

    def test_apply_discount_non_numeric_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount("10.0", 2.0)

    def test_apply_discount_negative_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(10.0, -2.0)

    def test_apply_discount_non_numeric_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(10.0, "2.0")

    def test_apply_discount_state_interaction_in_calculate_total(self):
        calc = OrderCalculator()
        calc.add_item("item", 10.0, 1)
        # apply_discount used internally by calculate_total; we test via calculate_total later

    def test_apply_discount_idempotent(self):
        calc = OrderCalculator()
        r1 = calc.apply_discount(100.0, 10.0)
        r2 = calc.apply_discount(100.0, 10.0)
        self.assertEqual(r1, r2)

    def test_calculate_shipping_normal_use_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(80.0), 10.0)

    def test_calculate_shipping_normal_use_at_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_normal_use_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_threshold_zero_always_free(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(0.0), 0.0)
        self.assertAlmostEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_shipping_cost_zero_always_free(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=0.0)
        self.assertAlmostEqual(calc.calculate_shipping(50.0), 0.0)
        self.assertAlmostEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_large_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        huge = 1e108
        self.assertAlmostEqual(calc.calculate_shipping(huge), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_shipping(-10.0)

    def test_calculate_shipping_non_numeric_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping("10.0")

    def test_calculate_shipping_state_interaction_with_apply_discount(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item("item", 30.0, 1)
        subtotal = calc.get_subtotal()
        discounted = calc.apply_discount(subtotal, 10.0)  # 20
        shipping = calc.calculate_shipping(discounted)
        self.assertAlmostEqual(shipping, 5.0)  # below threshold

    def test_calculate_shipping_idempotent(self):
        calc = OrderCalculator()
        s1 = calc.calculate_shipping(50.0)
        s2 = calc.calculate_shipping(50.0)
        self.assertEqual(s1, s2)

    def test_calculate_tax_normal_use(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_rate_greater_than_one(self):
        calc = OrderCalculator(tax_rate=1.5)
        self.assertAlmostEqual(calc.calculate_tax(10.0), 15.0)

    def test_calculate_tax_small_amount(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(0.0001), 0.000023, places=9)

    def test_calculate_tax_negative_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_non_numeric_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax("5.0")

    def test_calculate_tax_state_interaction_in_calculate_total(self):
        calc = OrderCalculator(tax_rate=0.1)
        calc.add_item("item", 100.0, 1)
        subtotal = calc.get_subtotal()
        discounted = calc.apply_discount(subtotal, 0.0)
        shipping = calc.calculate_shipping(discounted)
        tax = calc.calculate_tax(discounted + shipping)
        expected = (discounted + shipping) * 0.1
        self.assertAlmostEqual(tax, expected)

    def test_calculate_tax_idempotent(self):
        calc = OrderCalculator()
        t1 = calc.calculate_tax(50.0)
        t2 = calc.calculate_tax(50.0)
        self.assertEqual(t1, t2)

    def test_calculate_total_normal_use(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item("book", 50.0, 2)  # subtotal 100
        total = calc.calculate_total(discount=10.0)  # discounted 90 -> shipping 10 -> tax on 100
        # discounted_subtotal = 90, shipping = 10 (below threshold), amount_for_tax = 100, tax = 23
        expected = 90.0 + 10.0 + 23.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_default_discount_zero(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item("item", 30.0, 1)  # subtotal 30
        total = calc.calculate_total()  # discount 0
        # discounted 30, shipping 5 (below threshold), amount_for_tax 35, tax 3.5
        expected = 30.0 + 5.0 + 3.5
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_equals_subtotal(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=0.0, shipping_cost=5.0)
        calc.add_item("item", 20.0, 1)
        total = calc.calculate_total(discount=20.0)  # discounted 0
        # discounted 0, shipping 0 (threshold 0), amount_for_tax 0, tax 0
        expected = 0.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_greater_than_subtotal_raises(self):
        calc = OrderCalculator()
        calc.add_item("item", 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=15.0)

    def test_calculate_total_empty_order(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        total = calc.calculate_total(discount=0.0)
        # subtotal 0, discount 0 -> discounted 0, shipping 0 (threshold 50), tax 0
        self.assertAlmostEqual(total, 0.0)

    def test_calculate_total_free_shipping_threshold_zero(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=0.0, shipping_cost=5.0)
        calc.add_item("item", 10.0, 1)
        total = calc.calculate_total(discount=0.0)
        # discounted 10, shipping 0, amount_for_tax 10, tax 1
        expected = 10.0 + 0.0 + 1.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_shipping_cost_zero(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=0.0)
        calc.add_item("item", 50.0, 1)
        total = calc.calculate_total(discount=0.0)
        # discounted 50, shipping 0, amount_for_tax 50, tax 5
        expected = 50.0 + 0.0 + 5.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=50.0, shipping_cost=10.0)
        calc.add_item("item", 100.0, 1)
        total = calc.calculate_total(discount=10.0)
        # discounted 90, shipping 0 (threshold met), amount_for_tax 90, tax 0
        expected = 90.0 + 0.0 + 0.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_negative_discount(self):
        calc = OrderCalculator()
        calc.add_item("item", 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-5.0)

    def test_calculate_total_non_numeric_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_total(discount="5.0")

    def test_calculate_total_state_interaction_add_remove(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item("a", 20.0, 1)
        calc.add_item("b", 30.0, 1)  # subtotal 50
        total1 = calc.calculate_total(discount=0.0)
        # discounted 50, shipping 0 (threshold met), amount_for_tax 50, tax 5 => 55
        self.assertAlmostEqual(total1, 55.0)
        calc.remove_item("a")
        total2 = calc.calculate_total(discount=0.0)
        # subtotal 30, shipping 5, amount_for_tax 35, tax 3.5 => 38.5
        self.assertAlmostEqual(total2, 38.5)

    def test_calculate_total_idempotent(self):
        calc = OrderCalculator()
        calc.add_item("item", 10.0, 1)
        t1 = calc.calculate_total(discount=1.0)
        t2 = calc.calculate_total(discount=1.0)
        self.assertEqual(t1, t2)

    def test_total_items_normal_use(self):
        calc = OrderCalculator()
        calc.add_item("a", 2, 1)
        calc.add_item("b", 3, 1)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_empty_order(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_zero_quantity_not_allowed(self):
        # Adding zero quantity raises, so total_items stays 0
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("item", 1.0, 0)
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_large_quantities(self):
        calc = OrderCalculator()
        qty1 = sys.maxsize
        qty2 = 1
        calc.add_item("a", 1.0, qty1)
        calc.add_item("b", 2.0, qty2)
        self.assertEqual(calc.total_items(), qty1 + qty2)

    def test_total_items_state_interaction(self):
        calc = OrderCalculator()
        calc.add_item("a", 1, 1)
        calc.add_item("b", 2, 1)
        self.assertEqual(calc.total_items(), 3)
        calc.remove_item("a")
        self.assertEqual(calc.total_items(), 2)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_idempotent(self):
        calc = OrderCalculator()
        calc.add_item("a", 1, 1)
        c1 = calc.total_items()
        c2 = calc.total_items()
        self.assertEqual(c1, c2)

    def test_clear_order_normal_use(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)
        self.assertListEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_on_empty_order(self):
        calc = OrderCalculator()
        calc.clear_order()  # should not raise
        self.assertTrue(calc.is_empty())

    def test_clear_order_state_interaction(self):
        calc = OrderCalculator()
        calc.add_item("a", 10.0, 1)
        total_before = calc.calculate_total()
        calc.clear_order()
        calc.add_item("b", 20.0, 1)
        total_after = calc.calculate_total()
        self.assertNotEqual(total_before, total_after)

    def test_clear_order_idempotent(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        calc.clear_order()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_list_items_normal_use(self):
        calc = OrderCalculator()
        calc.add_item("apple", 1.0, 1)
        calc.add_item("banana", 2.0, 1)
        items = calc.list_items()
        self.assertEqual(sorted(items), ["apple", "banana"])

    def test_list_items_empty_order(self):
        calc = OrderCalculator()
        self.assertListEqual(calc.list_items(), [])

    def test_list_items_same_name_multiple_times_unique(self):
        calc = OrderCalculator()
        calc.add_item("apple", 1.0, 2)
        calc.add_item("apple", 1.0, 3)
        items = calc.list_items()
        # Assuming unique names
        self.assertListEqual(items, ["apple"])

    def test_list_items_empty_string_name(self):
        calc = OrderCalculator()
        calc.add_item("", 1.0, 1)
        items = calc.list_items()
        self.assertIn("", items)

    def test_list_items_state_interaction_remove(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        calc.add_item("b", 2.0, 1)
        calc.remove_item("a")
        items = calc.list_items()
        self.assertListEqual(items, ["b"])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        calc.clear_order()
        self.assertListEqual(calc.list_items(), [])

    def test_list_items_idempotent(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        l1 = calc.list_items()
        l2 = calc.list_items()
        self.assertEqual(l1, l2)

    def test_is_empty_new_instance(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_adding_item(self):
        calc = OrderCalculator()
        calc.add_item("item", 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_removing_all_items(self):
        calc = OrderCalculator()
        calc.add_item("item", 1.0, 2)
        calc.remove_item("item")
        self.assertTrue(calc.is_empty())

    def test_is_empty_zero_quantity_item_not_allowed(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("item", 1.0, 0)
        self.assertTrue(calc.is_empty())

    def test_is_empty_state_interaction(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 1)
        self.assertFalse(calc.is_empty())
        total = calc.calculate_total()
        self.assertFalse(calc.is_empty())
        calc.remove_item("a")
        self.assertTrue(calc.is_empty())

    def test_is_empty_idempotent(self):
        calc = OrderCalculator()
        e1 = calc.is_empty()
        e2 = calc.is_empty()
        self.assertEqual(e1, e2)