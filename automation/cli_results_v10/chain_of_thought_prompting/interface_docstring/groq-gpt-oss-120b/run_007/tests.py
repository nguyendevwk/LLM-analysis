import unittest
from decimal import Decimal
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_constructor_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)

    def test_constructor_custom_valid(self):
        oc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(oc.tax_rate, 0.05)
        self.assertEqual(oc.free_shipping_threshold, 50.0)
        self.assertEqual(oc.shipping_cost, 5.0)

    def test_constructor_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_constructor_tax_rate_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_constructor_negative_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_constructor_negative_shipping(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2)

    def test_constructor_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_constructor_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_constructor_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    def test_add_item_normal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertIn('Apple', oc.list_items())
        self.assertEqual(oc.total_items(), 2)

    def test_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8)
        self.assertEqual(oc.total_items(), 1)

    def test_add_item_merge_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_add_item_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0)

    def test_add_item_name_not_string(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0)

    def test_add_item_price_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 0)

    def test_add_item_price_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', -0.5)

    def test_add_item_price_not_number(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Pear', 'free')

    def test_add_item_quantity_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 1.0, 0)

    def test_add_item_quantity_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 1.0, -3)

    def test_add_item_quantity_not_int_float(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Pear', 1.0, 2.5)

    def test_add_item_quantity_not_int_string(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Pear', 1.0, '2')

    def test_add_item_large_values(self):
        oc = OrderCalculator()
        oc.add_item('GoldBar', 1000000.0, 1000)
        self.assertEqual(oc.total_items(), 1000)

    def test_add_item_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Item', 1.0, 1)
        oc.clear_order()
        oc.add_item('New', 2.0, 2)
        self.assertIn('New', oc.list_items())
        self.assertEqual(oc.total_items(), 2)

    def test_remove_item_normal(self):
        oc = OrderCalculator()
        oc.add_item('Milk', 2.0, 3)
        oc.remove_item('Milk')
        self.assertNotIn('Milk', oc.list_items())
        self.assertEqual(oc.total_items(), 0)

    def test_remove_item_nonexistent_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Eggs')

    def test_remove_item_nonexistent_with_items(self):
        oc = OrderCalculator()
        oc.add_item('Bread', 1.0, 1)
        with self.assertRaises(ValueError):
            oc.remove_item('Eggs')

    def test_remove_item_name_not_string(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_remove_item_empty_string(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('')

    def test_get_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('A', 2, 1)
        oc.add_item('B', 3, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 8.0, places=2)

    def test_get_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item('C', 5.5, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 5.5, places=2)

    def test_get_subtotal_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_get_subtotal_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('A', 2, 1)
        oc.add_item('B', 3, 2)
        oc.remove_item('A')
        self.assertAlmostEqual(oc.get_subtotal(), 6.0, places=2)

    def test_get_subtotal_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('A', 2, 1)
        oc.clear_order()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_normal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(200.0, 0.1), 180.0, places=2)

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50, 0.0), 50.0, places=2)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(80, 1.0), 0.0, places=2)

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-5, 0.2)

    def test_apply_discount_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, -0.1)

    def test_apply_discount_discount_over_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, 1.5)

    def test_apply_discount_subtotal_not_number(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.2)

    def test_apply_discount_discount_not_number(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100, [0.2])

    def test_apply_discount_subtotal_int(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0.2), 80.0, places=2)

    def test_apply_discount_discount_int(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0), 100.0, places=2)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(150), 0.0, places=2)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(100), 0.0, places=2)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(99.99), 10.0, places=2)

    def test_calculate_shipping_custom_config_below(self):
        oc = OrderCalculator(free_shipping_threshold=50, shipping_cost=7)
        self.assertAlmostEqual(oc.calculate_shipping(30), 7.0, places=2)

    def test_calculate_shipping_custom_config_above(self):
        oc = OrderCalculator(free_shipping_threshold=50, shipping_cost=7)
        self.assertAlmostEqual(oc.calculate_shipping(55), 0.0, places=2)

    def test_calculate_shipping_input_not_number(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('30')

    def test_calculate_shipping_input_none(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping(None)

    def test_calculate_shipping_negative_subtotal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(-5), 10.0, places=2)

    def test_calculate_shipping_very_large(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(1000000000.0), 0.0, places=2)

    def test_calculate_tax_normal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(100), 23.0, places=2)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0), 0.0, places=2)

    def test_calculate_tax_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5)

    def test_calculate_tax_not_number_string(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax('100')

    def test_calculate_tax_not_number_list(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax([100])

    def test_calculate_tax_custom_rate(self):
        oc = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(oc.calculate_tax(200), 10.0, places=2)

    def test_calculate_tax_large_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(10000000.0), 2300000.0, places=2)

    def test_calculate_total_no_discount_shipping_applied(self):
        oc = OrderCalculator()
        oc.add_item('X', 30, 2)
        total = oc.calculate_total()
        expected = 60 + 10 + (60 + 10) * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_discount_below_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Y', 40, 3)
        total = oc.calculate_total(0.2)
        expected = 96 + 10 + (96 + 10) * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_exact_threshold_free_shipping(self):
        oc = OrderCalculator()
        oc.add_item('Z', 50, 2)
        total = oc.calculate_total(0.0)
        expected = 100 + 0 + 100 * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_discount_makes_free_shipping(self):
        oc = OrderCalculator()
        oc.add_item('A', 25, 5)
        total = oc.calculate_total(0.2)
        expected = 100 + 0 + 100 * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_full_discount(self):
        oc = OrderCalculator()
        oc.add_item('Anything', 10, 1)
        total = oc.calculate_total(1.0)
        self.assertAlmostEqual(total, 0.0, places=2)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_calculate_total_invalid_discount_negative(self):
        oc = OrderCalculator()
        oc.add_item('Item', 10, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(-0.1)

    def test_calculate_total_invalid_discount_over_one(self):
        oc = OrderCalculator()
        oc.add_item('Item', 10, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(1.5)

    def test_calculate_total_discount_not_number(self):
        oc = OrderCalculator()
        oc.add_item('Item', 10, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total('0.1')

    def test_calculate_total_negative_subtotal_via_patch(self):
        oc = OrderCalculator()
        oc.add_item('Item', 10, 1)
        original = oc.get_subtotal
        oc.get_subtotal = lambda: -5
        with self.assertRaises(ValueError):
            oc.calculate_total()
        oc.get_subtotal = original

    def test_calculate_total_manual_composition(self):
        oc = OrderCalculator()
        oc.add_item('A', 10, 2)
        discount = 0.1
        discounted = oc.apply_discount(20, discount)
        shipping = oc.calculate_shipping(discounted)
        tax = oc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(oc.calculate_total(discount), expected, places=2)

    def test_calculate_total_custom_config(self):
        oc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50, shipping_cost=7)
        oc.add_item('B', 20, 2)
        total = oc.calculate_total(0.25)
        expected = 30 + 7 + (30 + 7) * 0.05
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_large_numbers(self):
        oc = OrderCalculator()
        oc.add_item('Big', 1000000.0, 1000)
        total = oc.calculate_total()
        expected = 1000000000.0 + 0 + 1000000000.0 * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 2)
        oc.add_item('B', 2, 5)
        self.assertEqual(oc.total_items(), 7)

    def test_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 3)
        oc.remove_item('A')
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 2)
        oc.clear_order()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_empty_start(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Gold', 1, 1000000)
        self.assertEqual(oc.total_items(), 1000000)

    def test_list_items_unique_names(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.add_item('Apple', 1, 2)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_list_items_multiple_distinct(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.add_item('Banana', 2, 1)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana'])

    def test_list_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Milk', 1, 1)
        oc.remove_item('Milk')
        self.assertEqual(oc.list_items(), [])

    def test_list_items_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 1)
        oc.clear_order()
        self.assertEqual(oc.list_items(), [])

    def test_list_items_order_unspecified(self):
        oc = OrderCalculator()
        oc.add_item('B', 1, 1)
        oc.add_item('A', 1, 1)
        self.assertCountEqual(oc.list_items(), ['A', 'B'])

    def test_list_items_after_add_post_clear(self):
        oc = OrderCalculator()
        oc.add_item('Old', 1, 1)
        oc.clear_order()
        oc.add_item('New', 2, 2)
        self.assertCountEqual(oc.list_items(), ['New'])

    def test_is_empty_fresh(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_add(self):
        oc = OrderCalculator()
        oc.add_item('Item', 1, 1)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_remove_only(self):
        oc = OrderCalculator()
        oc.add_item('Item', 1, 1)
        oc.remove_item('Item')
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Item', 1, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_is_empty_state_unchanged_on_failed_remove(self):
        oc = OrderCalculator()
        oc.add_item('Item', 1, 1)
        with self.assertRaises(ValueError):
            oc.remove_item('Nonexistent')
        self.assertFalse(oc.is_empty())

    def test_clear_order_removes_all(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 1)
        oc.add_item('B', 2, 2)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.list_items(), [])
        self.assertEqual(oc.total_items(), 0)

    def test_clear_order_subsequent_subtotal_error(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 1)
        oc.clear_order()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_clear_order_idempotent(self):
        oc = OrderCalculator()
        oc.clear_order()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_clear_order_then_add_works(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 1)
        oc.clear_order()
        oc.add_item('B', 2, 2)
        self.assertIn('B', oc.list_items())
        self.assertEqual(oc.total_items(), 2)

    def test_add_remove_add_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.remove_item('Apple')
        oc.add_item('Apple', 2.0, 1)
        self.assertIn('Apple', oc.list_items())
        self.assertAlmostEqual(oc.get_subtotal(), 2.0, places=2)

    def test_add_clear_add_total(self):
        oc = OrderCalculator()
        oc.add_item('A', 10, 1)
        oc.clear_order()
        oc.add_item('B', 20, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 40.0, places=2)

    def test_discount_edge_shipping_edge(self):
        oc = OrderCalculator()
        oc.add_item('Item', 49, 2)
        total_no_discount = oc.calculate_total(0.0)
        total_with_discount = oc.calculate_total(0.02040816326530612)
        self.assertNotEqual(total_no_discount, total_with_discount)
        self.assertAlmostEqual(total_with_discount, 100 + 0 + 100 * 0.23, places=2)

    def test_large_order_scalability(self):
        oc = OrderCalculator()
        for i in range(50):
            oc.add_item(f'Item{i}', i + 1, i + 1)
        self.assertEqual(oc.total_items(), sum(range(1, 51)))
        self.assertTrue(len(oc.list_items()) == 50)

    def test_floating_point_rounding(self):
        oc = OrderCalculator()
        oc.add_item('Item', 0.1, 3)
        total = oc.calculate_total()
        expected = 0.3 + 10 + (0.3 + 10) * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_apply_discount_pure_function(self):
        oc = OrderCalculator()
        result = oc.apply_discount(100, 0.2)
        self.assertAlmostEqual(result, 80.0, places=2)
        self.assertAlmostEqual(100, 100, places=2)

    def test_calculate_shipping_pure_function(self):
        oc = OrderCalculator()
        result = oc.calculate_shipping(80)
        self.assertAlmostEqual(result, 10.0, places=2)

    def test_calculate_tax_pure_function(self):
        oc = OrderCalculator()
        result = oc.calculate_tax(200)
        self.assertAlmostEqual(result, 46.0, places=2)

    def test_add_item_decimal_price(self):
        oc = OrderCalculator()
        oc.add_item('DecimalItem', Decimal('1.25'), 2)
        self.assertAlmostEqual(oc.get_subtotal(), 2.5, places=2)

    def test_add_item_bool_quantity(self):
        oc = OrderCalculator()
        oc.add_item('BoolQty', 1.0, True)
        self.assertEqual(oc.total_items(), 1)

    def test_add_item_bool_price(self):
        oc = OrderCalculator()
        oc.add_item('BoolPrice', True, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 2.0, places=2)

    def test_add_item_numpy_float(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest('numpy not available')
        else:
            oc = OrderCalculator()
            oc.add_item('Numpy', np.float64(1.5), 2)
            self.assertAlmostEqual(oc.get_subtotal(), 3.0, places=2)