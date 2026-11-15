import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_below_zero(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        self.assertEqual(calc.total_items(), 1)
        self.assertIn('Apple', calc.list_items())

    def test_add_item_explicit_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.8, 3)
        self.assertEqual(calc.total_items(), 3)
        self.assertIn('Banana', calc.list_items())

    def test_add_item_duplicate_same_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        calc.add_item('Apple', 1.5, 4)
        self.assertEqual(calc.total_items(), 6)

    def test_add_item_duplicate_name_diff_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.7)

    def test_add_item_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    def test_add_item_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_non_numeric_price(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Pear', '1.0')

    def test_add_item_price_le_zero(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Pear', 0)

    def test_add_item_quantity_lt_one(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Pear', 1.0, 0)

    def test_add_item_non_int_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Pear', 1.0, 1.5)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_remove_item_nonexistent(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Orange')

    def test_remove_item_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        calc.add_item('Banana', 0.8, 3)
        subtotal = calc.get_subtotal()
        self.assertAlmostEqual(subtotal, 5.4, places=5)

    def test_get_subtotal_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_valid(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100, 0.2)
        self.assertAlmostEqual(result, 80.0, places=5)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        result = calc.apply_discount(50, 0.0)
        self.assertAlmostEqual(result, 50.0, places=5)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        result = calc.apply_discount(50, 1.0)
        self.assertAlmostEqual(result, 0.0, places=5)

    def test_apply_discount_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10, 0.1)

    def test_apply_discount_discount_lt_zero(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50, -0.1)

    def test_apply_discount_discount_gt_one(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50, 1.5)

    def test_apply_discount_non_numeric_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('50', 0.1)

    def test_apply_discount_non_numeric_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(50, '0.1')

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(80)
        self.assertAlmostEqual(shipping, 10.0, places=5)

    def test_calculate_shipping_at_threshold(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(100)
        self.assertAlmostEqual(shipping, 0.0, places=5)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(150)
        self.assertAlmostEqual(shipping, 0.0, places=5)

    def test_calculate_shipping_non_numeric_input(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('80')

    def test_calculate_tax_positive_amount(self):
        calc = OrderCalculator()
        tax = calc.calculate_tax(100)
        self.assertAlmostEqual(tax, 23.0, places=5)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        tax = calc.calculate_tax(0)
        self.assertAlmostEqual(tax, 0.0, places=5)

    def test_calculate_tax_negative_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5)

    def test_calculate_tax_non_numeric_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_calculate_total_normal_case(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.1)
        self.assertAlmostEqual(total, 132.84, places=5)

    def test_calculate_total_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 147.6, places=5)

    def test_calculate_total_discount_full(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 12.3, places=5)

    def test_calculate_total_discount_full_free_shipping_threshold_zero(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=0, shipping_cost=10)
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 0.0, places=5)

    def test_calculate_total_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_discount_lt_zero(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)

    def test_calculate_total_discount_gt_one(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(1.5)

    def test_calculate_total_discount_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_total('0.1')

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_clear_order_after_adding(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Banana', 1.0)
        calc.add_item('Apple', 1.0)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})

    def test_is_empty_fresh(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_adding(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_clearing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_integration_full_workflow(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        calc.add_item('Banana', 0.8, 3)
        total = calc.calculate_total(0.1)
        self.assertAlmostEqual(total, 18.2778, places=5)

    def test_integration_merge_and_remove(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_integration_clear_and_subtotal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_add_item_edge_quantity_one(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(calc.total_items(), 1)

    def test_add_item_edge_price_smallest_positive(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.01, 1)
        self.assertEqual(calc.total_items(), 1)

    def test_apply_discount_edge_zero(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100, 0.0)
        self.assertAlmostEqual(result, 100.0, places=5)

    def test_apply_discount_edge_full(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100, 1.0)
        self.assertAlmostEqual(result, 0.0, places=5)

    def test_calculate_shipping_edge_threshold_equal(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(100)
        self.assertAlmostEqual(shipping, 0.0, places=5)

    def test_calculate_tax_edge_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        tax = calc.calculate_tax(100)
        self.assertAlmostEqual(tax, 0.0, places=5)

    def test_calculate_total_edge_free_shipping_threshold_equal(self):
        calc = OrderCalculator(free_shipping_threshold=120)
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 147.6, places=5)

    def test_calculate_total_edge_discount_full_threshold_equal(self):
        calc = OrderCalculator(free_shipping_threshold=120)
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 0.0, places=5)

    def test_add_item_edge_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 10000)
        self.assertEqual(calc.total_items(), 10000)

    def test_add_item_edge_large_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1000000, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 1000000.0, places=5)

    def test_calculate_total_edge_large_subtotal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1000000, 1)
        total = calc.calculate_total(0.1)
        self.assertAlmostEqual(total, 1107000.0, places=5)

    def test_calculate_total_edge_small_subtotal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.01, 1)
        total = calc.calculate_total(0.1)
        self.assertAlmostEqual(total, 12.31107, places=5)

    def test_calculate_total_edge_shipping_once(self):
        calc = OrderCalculator(free_shipping_threshold=300, shipping_cost=10)
        calc.add_item('Apple', 100, 2)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 258.7, places=5)

    def test_total_items_edge_merge(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_list_items_edge_order_not_significant(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Banana', 1.0)
        calc.add_item('Apple', 1.0)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})

    def test_remove_item_edge_remove_all(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_calculate_tax_edge_rate_change(self):
        calc = OrderCalculator()
        calc.tax_rate = 0.5
        tax = calc.calculate_tax(100)
        self.assertAlmostEqual(tax, 50.0, places=5)

    def test_calculate_total_edge_discount_zero_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 147.6, places=5)

    def test_calculate_total_edge_discount_full_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=0)
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 0.0, places=5)

    def test_calculate_total_edge_discount_half_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0)
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 73.8, places=5)

    def test_calculate_total_edge_discount_half_threshold_high(self):
        calc = OrderCalculator(free_shipping_threshold=200)
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 85.7, places=5)

    def test_calculate_total_edge_order_of_operations(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 200)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 123.0, places=5)

    def test_add_item_edge_case_sensitive(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('apple', 1.0)
        self.assertEqual(set(calc.list_items()), {'Apple', 'apple'})

    def test_add_item_edge_whitespace_name(self):
        calc = OrderCalculator()
        calc.add_item(' Apple ', 1.0)
        calc.add_item('Apple', 1.0)
        self.assertEqual(set(calc.list_items()), {' Apple ', 'Apple'})

    def test_remove_item_edge_whitespace_name(self):
        calc = OrderCalculator()
        calc.add_item(' Apple ', 1.0)
        calc.remove_item(' Apple ')
        self.assertTrue(calc.is_empty())

    def test_list_items_edge_whitespace_names(self):
        calc = OrderCalculator()
        calc.add_item(' Apple ', 1.0)
        calc.add_item('Banana', 1.0)
        self.assertEqual(set(calc.list_items()), {' Apple ', 'Banana'})

    def test_calculate_total_edge_discount_close_to_one(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 100)
        total = calc.calculate_total(0.9999)
        self.assertAlmostEqual(total, 12.300123, places=5)

    def test_calculate_total_edge_discount_close_to_zero(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 100)
        total = calc.calculate_total(0.0001)
        self.assertAlmostEqual(total, 135.2877, places=5)

    def test_calculate_total_edge_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0)
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 147.6, places=5)

    def test_calculate_total_edge_shipping_threshold_max(self):
        calc = OrderCalculator(free_shipping_threshold=1000000)
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 157.7, places=5)

    def test_calculate_total_edge_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0)
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 147.6, places=5)

    def test_calculate_total_edge_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 120.0, places=5)

    def test_calculate_total_edge_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 240.0, places=5)

    def test_calculate_total_edge_tax_rate_default(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 147.6, places=5)

    def test_calculate_total_edge_tax_rate_default_discount_below_threshold(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 85.7, places=5)

    def test_calculate_total_edge_tax_rate_default_discount_above_threshold(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 147.6, places=5)

    def test_calculate_total_edge_tax_rate_default_discount_at_threshold(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.2)
        self.assertAlmostEqual(total, 130.28, places=5)

    def test_calculate_total_edge_tax_rate_default_discount_zero(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 120)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 147.6, places=5)

    def test_calculate_total_edge_tax_rate_default_discount_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)

    def test_calculate_total_edge_tax_rate_default_discount_string(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_total('0.1')

if __name__ == '__main__':
    unittest.main()