import unittest
import math
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default_values(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_zero_free_shipping_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_init_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_non_numeric_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='invalid')

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_non_numeric_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='invalid')

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_non_numeric_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='invalid')

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_add_item_normal_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0)
        self.assertEqual(calc.get_subtotal(), 1.0)
        self.assertIn('apple', calc.list_items())

    def test_add_item_normal_quantity_greater_than_one(self):
        calc = OrderCalculator()
        calc.add_item('banana', 0.5, 4)
        self.assertEqual(calc.get_subtotal(), 2.0)
        self.assertIn('banana', calc.list_items())

    def test_add_item_same_item_multiple_times(self):
        calc = OrderCalculator()
        calc.add_item('orange', 0.8, 2)
        calc.add_item('orange', 0.8, 3)
        self.assertEqual(calc.get_subtotal(), 0.8 * 5)
        self.assertEqual(calc.total_items(), 5)

    def test_add_item_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_negative_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('cheap', -1.0)

    def test_add_item_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('item', 1.0, -1)

    def test_add_item_non_numeric_price(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('item', 'price')

    def test_add_item_non_numeric_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('item', 1.0, 'qty')

    def test_remove_item_nonexistent_exception(self):
        calc = OrderCalculator()
        with self.assertRaises((KeyError, ValueError)):
            calc.remove_item('orange')

    def test_remove_item_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('item', 2.5, 3)
        self.assertEqual(calc.get_subtotal(), 7.5)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 2)
        calc.add_item('b', 2.0, 3)
        self.assertEqual(calc.get_subtotal(), 1.0 * 2 + 2.0 * 3)

    def test_get_subtotal_after_add_remove(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0)
        calc.add_item('b', 2.0)
        self.assertEqual(calc.get_subtotal(), 3.0)
        calc.remove_item('a')
        self.assertEqual(calc.get_subtotal(), 2.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(0.0, 0.1), 0.0)

    def test_apply_discount_non_numeric_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('subtotal', 0.1)

    def test_apply_discount_non_numeric_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, 'discount')

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_at_threshold_free(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(-5.0), 10.0)

    def test_calculate_shipping_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('amount')

    def test_calculate_tax_normal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.calculate_tax(50.0), 50.0)

    def test_calculate_tax_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('amount')

    def test_calculate_tax_nan_inf(self):
        calc = OrderCalculator()
        result = calc.calculate_tax(float('nan'))
        self.assertTrue(math.isnan(result))
        result = calc.calculate_tax(float('inf'))
        self.assertTrue(math.isinf(result) and result > 0)

    def test_calculate_total_single_item_shipping_applicable_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('book', 30.0)
        expected = (30.0 + 10.0) * (1 + 0.23)
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_single_item_free_shipping_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('book', 120.0)
        expected = 120.0 * (1 + 0.23)
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_multiple_items_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('a', 10.0, 2)
        calc.add_item('b', 30.0, 1)
        expected = (20.0 + 30.0 + 10.0) * (1 + 0.23)
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_discount_affects_shipping(self):
        calc = OrderCalculator()
        calc.add_item('item', 80.0)
        discounted = 80.0 * (1 - 0.2)
        expected = (discounted + 10.0) * (1 + 0.23)
        self.assertAlmostEqual(calc.calculate_total(0.2), expected)

    def test_calculate_total_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('item', 50.0)
        expected = 50.0 * (1 + 0.23)
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_zero_free_shipping_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item('item', 50.0)
        expected = 50.0 * (1 + 0.23)
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_non_numeric_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_total('discount')

    def test_calculate_total_state_change(self):
        calc = OrderCalculator()
        calc.add_item('a', 10.0)
        total1 = calc.calculate_total()
        calc.add_item('b', 20.0)
        total2 = calc.calculate_total()
        self.assertNotEqual(total1, total2)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_return_value(self):
        calc = OrderCalculator()
        self.assertIsNone(calc.clear_order())

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0)
        self.assertEqual(calc.list_items(), ['apple'])

    def test_list_items_multiple_distinct_items(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0)
        calc.add_item('banana', 2.0)
        items = calc.list_items()
        self.assertEqual(len(items), 2)
        self.assertIn('apple', items)
        self.assertIn('banana', items)

    def test_list_items_after_add_remove(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0)
        calc.add_item('b', 1.0)
        self.assertEqual(set(calc.list_items()), {'a', 'b'})
        calc.remove_item('a')
        self.assertEqual(calc.list_items(), ['b'])

    def test_list_items_return_type(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0)
        result = calc.list_items()
        self.assertIsInstance(result, list)
        for elem in result:
            self.assertIsInstance(elem, str)

    def test_list_items_immutability(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0)
        lst = calc.list_items()
        lst.append('extra')
        self.assertNotIn('extra', calc.list_items())

    def test_is_empty_empty(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_remove_last(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0)
        calc.remove_item('item')
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_clear_on_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_return_type(self):
        calc = OrderCalculator()
        self.assertIsInstance(calc.is_empty(), bool)