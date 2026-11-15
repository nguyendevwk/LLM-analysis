import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_init_custom(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_too_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_free_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_init_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_free_shipping_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_add_item_single_default_quantity(self):
        self.calc.add_item('Apple', 1.0)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertIn('Apple', self.calc.list_items())

    def test_add_item_explicit_quantity(self):
        self.calc.add_item('Banana', 0.5, 3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertIn('Banana', self.calc.list_items())

    def test_add_item_duplicate_same_name_price(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Apple', 1.0, 2)
        self.assertEqual(self.calc.total_items(), 3)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item('Apple', 1.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.5)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0)

    def test_add_item_price_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', 0)

    def test_add_item_price_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', -1)

    def test_add_item_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', 0.8, 0)

    def test_add_item_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', 0.8, -2)

    def test_add_item_name_not_string(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_price_not_number(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Grape', '1.0')

    def test_add_item_quantity_not_int(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Grape', 1.0, '2')

    def test_add_item_quantity_float_integer(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.0, 2.0)

    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_merged(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Apple', 1.0, 3)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Mango')

    def test_remove_item_name_not_string(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_non_empty(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.5)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_normal(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 0.2), 80.0)

    def test_apply_discount_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(50, 0.0), 50.0)

    def test_apply_discount_full(self):
        self.assertAlmostEqual(self.calc.apply_discount(50, 1.0), 0.0)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10, 0.1)

    def test_apply_discount_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50, -0.1)

    def test_apply_discount_discount_too_high(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50, 1.5)

    def test_apply_discount_non_numeric_subtotal(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('50', 0.1)

    def test_apply_discount_non_numeric_discount(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(50, '0.1')

    def test_calculate_shipping_below_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(90), 10.0)

    def test_calculate_shipping_equal_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(100), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(150), 0.0)

    def test_calculate_shipping_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('90')

    def test_calculate_tax_positive(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100), 23.0)

    def test_calculate_tax_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0), 0.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5)

    def test_calculate_tax_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_typical_no_discount(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 3)
        total = self.calc.calculate_total()
        expected = 16.605
        self.assertAlmostEqual(total, expected, places=5)

    def test_calculate_total_free_shipping_threshold_met(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=2.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 3)
        total = calc.calculate_total()
        expected = 4.305
        self.assertAlmostEqual(total, expected, places=5)

    def test_calculate_total_discount_applied_shipping_applies(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 3)
        total = calc.calculate_total(discount=0.5)
        expected = 14.4525
        self.assertAlmostEqual(total, expected, places=5)

    def test_calculate_total_discount_applied_free_shipping(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=1.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 3)
        total = calc.calculate_total(discount=0.5)
        expected = 2.1525
        self.assertAlmostEqual(total, expected, places=5)

    def test_calculate_total_full_discount_nonzero_shipping(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 3)
        total = calc.calculate_total(discount=1.0)
        expected = 12.3
        self.assertAlmostEqual(total, expected, places=5)

    def test_calculate_total_full_discount_zero_shipping(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 3)
        total = calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 0.0, places=5)

    def test_calculate_total_full_discount_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 3)
        total = calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 10.0, places=5)

    def test_calculate_total_full_discount_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 3)
        total = calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 20.0, places=5)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)

    def test_calculate_total_discount_too_high(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.5)

    def test_calculate_total_discount_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_total_items_sum(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_after_adding(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_clear_order_already_empty(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items_unique_names(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Banana', 0.5)
        self.calc.add_item('Apple', 1.0, 2)
        items = sorted(self.calc.list_items())
        self.assertEqual(items, ['Apple', 'Banana'])

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_after_construction(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_adding(self):
        self.calc.add_item('Apple', 1.0)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clearing(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_state_consistency_add_remove_get_subtotal(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.remove_item('Apple')
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_state_consistency_add_duplicate_remove(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Apple', 1.0, 3)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_state_consistency_clear_calculate_total(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_state_consistency_clear_list_items(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_state_consistency_clear_total_items(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_state_consistency_clear_is_empty(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_numeric_precision_discount_fractional(self):
        result = self.calc.apply_discount(99.99, 0.333333)
        expected = 99.99 * (1 - 0.333333)
        self.assertAlmostEqual(result, expected, places=5)

    def test_numeric_precision_tax_small_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.1), 0.023, places=5)

    def test_numeric_precision_shipping_threshold_boundary(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(99.999999), 10.0, places=5)

    def test_edge_case_large_price_quantity(self):
        self.calc.add_item('Expensive', 1000000000.0, 1000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1000000000000.0, places=0)

    def test_edge_case_small_price_large_quantity(self):
        self.calc.add_item('Cheap', 0.0001, 1000000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 100.0, places=5)

    def test_edge_case_add_item_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.0, 0)

    def test_edge_case_remove_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_edge_case_discount_boundary_zero_one(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 0.0), 100.0)
        self.assertAlmostEqual(self.calc.apply_discount(100, 1.0), 0.0)

    def test_edge_case_tax_boundary_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0), 0.0)

    def test_edge_case_whitespace_name(self):
        self.calc.add_item(' Apple', 1.0)
        self.calc.add_item('Apple', 1.0)
        items = sorted(self.calc.list_items())
        self.assertEqual(items, [' Apple', 'Apple'])

    def test_edge_case_case_sensitivity(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('apple', 1.0)
        items = sorted(self.calc.list_items())
        self.assertEqual(items, ['Apple', 'apple'])

    def test_edge_case_list_items_order_not_guaranteed(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Banana', 0.5)
        items = sorted(self.calc.list_items())
        self.assertEqual(items, ['Apple', 'Banana'])

    def test_edge_case_total_items_merge(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Apple', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_edge_case_calculate_total_tax_application(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 3)
        total = self.calc.calculate_total(discount=0.0)
        expected = 16.605
        self.assertAlmostEqual(total, expected, places=5)

    def test_edge_case_calculate_total_no_state_change(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.calculate_total()
        self.assertFalse(self.calc.is_empty())

    def test_edge_case_clear_order_removes_all(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
if __name__ == '__main__':
    unittest.main()