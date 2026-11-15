import unittest
import math
from decimal import Decimal
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_uses_default_values(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_init_custom_values(self):
        c = OrderCalculator(tax_rate=0.15, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(c.tax_rate, 0.15)
        self.assertEqual(c.free_shipping_threshold, 50.0)
        self.assertEqual(c.shipping_cost, 5.0)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_greater_than_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_non_numeric_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='high')

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2)

    def test_add_item_single(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0, places=2)

    def test_add_item_multiple_distinct(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.calc.add_item('Banana', 2.0, 2)
        self.assertCountEqual(self.calc.list_items(), ['Apple', 'Banana'])
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.0, places=2)

    def test_add_item_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Banana', 0.5, 0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Banana', 0.5, -1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Banana', -0.5, 1)

    def test_add_item_zero_price(self):
        self.calc.add_item('Freebie', 0.0, 5)
        self.assertIn('Freebie', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0, places=2)

    def test_add_item_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_non_numeric_price(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 'free', 1)

    def test_add_item_non_int_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.0, 2.5)

    def test_add_item_duplicate_name_aggregates_quantity(self):
        self.calc.add_item('Milk', 1.0, 1)
        self.calc.add_item('Milk', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.0, places=2)

    def test_add_item_duplicate_name_updates_price(self):
        self.calc.add_item('Milk', 1.0, 2)
        self.calc.add_item('Milk', 1.2, 2)
        self.assertEqual(self.calc.total_items(), 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.8, places=2)

    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.remove_item('Apple')
        self.assertNotIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0, places=2)

    def test_remove_item_nonexistent(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('NonExisting')

    def test_remove_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(42)

    def test_remove_item_last_item(self):
        self.calc.add_item('A', 1.0, 1)
        self.calc.add_item('B', 2.0, 1)
        self.calc.remove_item('A')
        self.calc.remove_item('B')
        self.assertTrue(self.calc.is_empty())

    def test_get_subtotal_empty(self):
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0, places=2)

    def test_get_subtotal_single_item(self):
        self.calc.add_item('Apple', 2.5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5.0, places=2)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.calc.add_item('Banana', 2.0, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.0, places=2)

    def test_get_subtotal_floating_point_rounding(self):
        self.calc.add_item('Item1', 0.1, 1)
        self.calc.add_item('Item2', 0.2, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.3, places=2)

    def test_apply_discount_normal(self):
        result = self.calc.apply_discount(50.0, 5.0)
        self.assertAlmostEqual(result, 45.0, places=2)

    def test_apply_discount_equal(self):
        result = self.calc.apply_discount(20.0, 20.0)
        self.assertAlmostEqual(result, 0.0, places=2)

    def test_apply_discount_larger_than_subtotal(self):
        result = self.calc.apply_discount(30.0, 40.0)
        self.assertAlmostEqual(result, 0.0, places=2)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(30.0, 0.0)
        self.assertAlmostEqual(result, 30.0, places=2)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(30.0, -5.0)

    def test_apply_discount_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('30', 5)

    def test_calculate_shipping_below_threshold(self):
        cost = self.calc.calculate_shipping(80.0)
        self.assertAlmostEqual(cost, 10.0, places=2)

    def test_calculate_shipping_at_threshold(self):
        cost = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(cost, 0.0, places=2)

    def test_calculate_shipping_above_threshold(self):
        cost = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(cost, 0.0, places=2)

    def test_calculate_shipping_custom_threshold(self):
        c = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(c.calculate_shipping(40.0), 5.0, places=2)
        self.assertAlmostEqual(c.calculate_shipping(60.0), 0.0, places=2)

    def test_calculate_shipping_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_shipping(-10.0)

    def test_calculate_shipping_infinite_subtotal(self):
        cost = self.calc.calculate_shipping(float('inf'))
        self.assertAlmostEqual(cost, 0.0, places=2)

    def test_calculate_tax_typical(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0, places=2)

    def test_calculate_tax_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0, places=2)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_tax_custom_rate_zero(self):
        c = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(c.calculate_tax(100.0), 0.0, places=2)

    def test_calculate_tax_custom_rate_half(self):
        c = OrderCalculator(tax_rate=0.5)
        self.assertAlmostEqual(c.calculate_tax(100.0), 50.0, places=2)

    def test_calculate_total_no_discount_below_threshold(self):
        self.calc.add_item('A', 40.0, 2)
        total = self.calc.calculate_total()
        expected = 80.0 + self.calc.calculate_tax(80.0) + 10.0
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_no_discount_above_threshold(self):
        self.calc.add_item('A', 60.0, 2)
        total = self.calc.calculate_total()
        expected = 120.0 + self.calc.calculate_tax(120.0)
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_with_discount_not_eliminate(self):
        self.calc.add_item('A', 50.0, 2)
        total = self.calc.calculate_total(discount=20.0)
        discounted = 80.0
        expected = discounted + self.calc.calculate_tax(discounted) + 10.0
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_discount_equal_subtotal(self):
        self.calc.add_item('A', 25.0, 2)
        total = self.calc.calculate_total(discount=50.0)
        discounted = 0.0
        expected = discounted + self.calc.calculate_tax(discounted) + 10.0
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_discount_greater_than_subtotal(self):
        self.calc.add_item('A', 30.0, 1)
        total = self.calc.calculate_total(discount=40.0)
        discounted = 0.0
        expected = discounted + self.calc.calculate_tax(discounted) + 10.0
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-5.0)

    def test_calculate_total_empty_order(self):
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 0.0, places=2)

    def test_calculate_total_custom_settings(self):
        c = OrderCalculator(tax_rate=0.1, free_shipping_threshold=20.0, shipping_cost=7.0)
        c.add_item('A', 15.0, 2)
        total = c.calculate_total(discount=5.0)
        discounted = 25.0
        expected = discounted + c.calculate_tax(discounted) + 0.0
        self.assertAlmostEqual(total, expected, places=2)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_single(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_multiple(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_removal(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 2.0, 3)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_after_clear(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_non_empty(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])
        self.assertEqual(self.calc.total_items(), 0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0, places=2)

    def test_clear_order_idempotent(self):
        self.calc.clear_order()
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_after_adds(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Banana', 2.0, 1)
        self.assertCountEqual(self.calc.list_items(), ['Apple', 'Banana'])

    def test_list_items_after_removal(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Banana', 2.0, 1)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.list_items(), ['Banana'])

    def test_list_items_no_duplicates(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Apple', 1.0, 2)
        self.assertEqual(self.calc.list_items(), ['Apple'])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_last_removal(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_integration_full_workflow(self):
        self.calc.add_item('A', 10.0, 3)
        self.calc.add_item('B', 5.0, 2)
        total_before = self.calc.calculate_total(discount=5.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0, places=2)
        self.assertAlmostEqual(self.calc.calculate_total(), 0.0, places=2)

    def test_integration_error_propagation(self):
        self.calc.add_item('A', 10.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-3.0)

    def test_large_quantity(self):
        self.calc.add_item('Bulk', 0.01, 10 ** 9)
        self.assertEqual(self.calc.total_items(), 10 ** 9)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10 ** 7, places=2)

    def test_price_nan(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Weird', float('nan'), 1)

    def test_price_infinite(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Weird', float('inf'), 1)

    def test_discount_infinite(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, float('inf'))

    def test_tax_rate_zero(self):
        c = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(c.calculate_tax(100.0), 0.0, places=2)

    def test_shipping_cost_zero(self):
        c = OrderCalculator(shipping_cost=0.0)
        self.assertAlmostEqual(c.calculate_shipping(50.0), 0.0, places=2)

    def test_free_shipping_threshold_zero(self):
        c = OrderCalculator(free_shipping_threshold=0.0)
        self.assertAlmostEqual(c.calculate_shipping(0.0), 0.0, places=2)
        self.assertAlmostEqual(c.calculate_shipping(10.0), 0.0, places=2)

    def test_mixed_type_decimal_input(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', Decimal('1.0'), 1)