import unittest
from decimal import Decimal
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_constructor_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    def test_constructor_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=7.5)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 7.5)

    def test_constructor_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_constructor_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_constructor_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_constructor_shipping_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_constructor_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_constructor_tax_rate_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_constructor_negative_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_constructor_negative_shipping(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2)

    def test_constructor_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_constructor_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=[100])

    def test_constructor_shipping_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_add_item_single(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Banana', 0.8)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_integer_price(self):
        self.calc.add_item('Pear', 5, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5.0)

    def test_add_item_merge_duplicate(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Apple', 1.5, 3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.5)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.0, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_name_not_string(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_price_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', 0.0, 1)

    def test_add_item_price_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', -0.5, 1)

    def test_add_item_price_not_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Orange', '1.0', 1)

    def test_add_item_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Kiwi', 1.2, 0)

    def test_add_item_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Kiwi', 1.2, -3)

    def test_add_item_quantity_not_int_float(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Kiwi', 1.2, 2.5)

    def test_add_item_quantity_not_int_string(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Kiwi', 1.2, '2')

    def test_add_item_large_numbers(self):
        self.calc.add_item('GoldBar', 1000000.0, int(10000.0))
        self.assertAlmostEqual(self.calc.get_subtotal(), 10000000000.0)

    def test_add_item_whitespace_name(self):
        self.calc.add_item('   ', 1.0, 1)
        self.assertIn('   ', self.calc.list_items())

    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 0.8, 3)
        self.calc.remove_item('Apple')
        self.assertNotIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 3)

    def test_remove_item_only_one(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        self.calc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_twice(self):
        self.calc.add_item('Apple', 1.5, 1)
        self.calc.remove_item('Apple')
        with self.assertRaises(ValueError):
            self.calc.remove_item('Apple')

    def test_remove_item_name_not_string(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(42)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 0.8, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5.4)

    def test_get_subtotal_single_item(self):
        self.calc.add_item('Pear', 5.0, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5.0)

    def test_get_subtotal_after_merge(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Apple', 1.5, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.5)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_get_subtotal_after_clear(self):
        self.calc.add_item('Apple', 1.5, 1)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_get_subtotal_floating_precision(self):
        self.calc.add_item('Item', 0.1, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.3, places=7)

    def test_apply_discount_no_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(200.0, 0.0), 200.0)

    def test_apply_discount_twenty_five_percent(self):
        self.assertAlmostEqual(self.calc.apply_discount(200.0, 0.25), 150.0)

    def test_apply_discount_full(self):
        self.assertAlmostEqual(self.calc.apply_discount(200.0, 1.0), 0.0)

    def test_apply_discount_boundary_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_boundary_one(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_over_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.5)

    def test_apply_discount_subtotal_not_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)

    def test_apply_discount_discount_not_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '0.1')

    def test_apply_discount_decimal_discount(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, Decimal('0.2'))

    def test_apply_discount_large_subtotal(self):
        self.assertAlmostEqual(self.calc.apply_discount(1000000000000.0, 0.5), 500000000000.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_just_below_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_zero(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_custom_values(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.calculate_shipping(60.0), 0.0)
        self.assertAlmostEqual(calc.calculate_shipping(40.0), 5.0)

    def test_calculate_shipping_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('abc')

    def test_calculate_shipping_negative_subtotal(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(-10.0), 10.0)

    def test_calculate_shipping_decimal_input(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(Decimal('30')), 10.0)

    def test_calculate_tax_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_positive_default(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_custom_rate(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(calc.calculate_tax(200.0), 10.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_tax_large_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(1000000000.0), 230000000.0)

    def test_calculate_tax_decimal_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(Decimal('100')), 23.0)

    def test_calculate_total_no_discount_above_threshold(self):
        self.calc.add_item('Apple', 2.0, 30)
        self.calc.add_item('Banana', 1.5, 30)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 129.15, places=2)

    def test_calculate_total_no_discount_below_threshold(self):
        self.calc.add_item('Apple', 10.0, 2)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 36.9, places=2)

    def test_calculate_total_discount_below_threshold(self):
        self.calc.add_item('Item', 20.0, 4)
        total = self.calc.calculate_total(0.2)
        self.assertAlmostEqual(total, 141.02, places=2)

    def test_calculate_total_discount_crosses_threshold(self):
        self.calc.add_item('Item', 130.0, 1)
        total = self.calc.calculate_total(0.2)
        self.assertAlmostEqual(total, 127.92, places=2)

    def test_calculate_total_full_discount(self):
        self.calc.add_item('Item', 50.0, 1)
        total = self.calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 12.3, places=2)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_discount_negative(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-0.1)

    def test_calculate_total_discount_over_one(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.5)

    def test_calculate_total_discount_type_error(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.2')

    def test_calculate_total_custom_parameters(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=7.0)
        calc.add_item('Item', 60.0, 1)
        total = calc.calculate_total(0.1)
        self.assertAlmostEqual(total, 56.7, places=2)

    def test_calculate_total_discount_exact_threshold(self):
        self.calc.add_item('Item', 125.0, 1)
        total = self.calc.calculate_total(0.2)
        self.assertAlmostEqual(total, 127.92, places=2)

    def test_calculate_total_zero_shipping_custom(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        calc.add_item('Item', 10.0, 1)
        total = calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 0.0, places=2)

    def test_calculate_total_propagates_type_error(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=Decimal('0.1'))

    def test_calculate_total_large_numbers(self):
        self.calc.add_item('Expensive', 1000000.0, int(10000.0))
        total = self.calc.calculate_total(0.5)
        expected_subtotal = 10000000000.0
        discounted = expected_subtotal * 0.5
        shipping = 0.0
        tax = discounted * 0.23
        self.assertAlmostEqual(total, discounted + shipping + tax, places=2)

    def test_calculate_total_idempotent(self):
        self.calc.add_item('Apple', 2.0, 10)
        first = self.calc.calculate_total()
        second = self.calc.calculate_total()
        self.assertAlmostEqual(first, second, places=2)

    def test_total_items_distinct(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.calc.add_item('Banana', 1.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_merge(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.calc.add_item('Apple', 1.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_removal(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.calc.add_item('Banana', 1.0, 2)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.total_items(), 2)

    def test_total_items_after_clear(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_large_quantity(self):
        self.calc.add_item('Gold', 1.0, 1000000)
        self.assertEqual(self.calc.total_items(), 1000000)

    def test_clear_order_clears(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_subsequent_use(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.calc.add_item('Banana', 2.0, 2)
        self.assertIn('Banana', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 2)

    def test_clear_order_subsequent_subtotal_error(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_list_items_three_distinct(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Banana', 1.0, 1)
        self.calc.add_item('Pear', 1.0, 1)
        self.assertEqual(set(self.calc.list_items()), {'Apple', 'Banana', 'Pear'})

    def test_list_items_duplicate(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Apple', 1.0, 2)
        self.assertEqual(self.calc.list_items(), ['Apple'])

    def test_list_items_after_removal(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Banana', 1.0, 1)
        self.calc.remove_item('Banana')
        self.assertEqual(self.calc.list_items(), ['Apple'])

    def test_list_items_after_clear(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_whitespace_name(self):
        self.calc.add_item('   ', 1.0, 1)
        self.assertIn('   ', self.calc.list_items())

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_remove_only(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_integration_discount_triggers_free_shipping(self):
        self.calc.add_item('Item', 130.0, 1)
        total = self.calc.calculate_total(0.2)
        shipping = self.calc.calculate_shipping(self.calc.apply_discount(130.0, 0.2))
        self.assertAlmostEqual(shipping, 0.0, places=2)

    def test_integration_removal_affects_total(self):
        self.calc.add_item('Apple', 2.0, 10)
        self.calc.add_item('Banana', 1.0, 5)
        total_before = self.calc.calculate_total()
        self.calc.remove_item('Banana')
        total_after = self.calc.calculate_total()
        self.assertNotEqual(total_before, total_after)

    def test_integration_total_after_clearing(self):
        self.calc.add_item('Apple', 2.0, 1)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_integration_custom_configuration(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=7.0)
        calc.add_item('Item', 60.0, 1)
        total = calc.calculate_total(0.1)
        self.assertAlmostEqual(total, 56.7, places=2)

    def test_integration_state_consistency(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 2.0, 1)
        self.calc.remove_item('Apple')
        self.calc.add_item('Apple', 1.0, 1)
        self.assertEqual(set(self.calc.list_items()), {'Apple', 'Banana'})
        self.assertEqual(self.calc.total_items(), 2)

    def test_integration_repeated_add_remove_cycles(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.remove_item('Apple')
        self.calc.add_item('Apple', 1.0, 3)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_edge_floating_precision(self):
        self.calc.add_item('Item', 0.1, 3)
        subtotal = self.calc.get_subtotal()
        discounted = self.calc.apply_discount(subtotal, 0.2)
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted + shipping)
        total = discounted + shipping + tax
        self.assertAlmostEqual(total, 0.244, places=3)

    def test_edge_non_numeric_numpy_float(self):
        import numpy as np
        with self.assertRaises(TypeError):
            self.calc.add_item('Num', np.float64(1.0), 1)

    def test_edge_very_large_numbers(self):
        self.calc.add_item('Huge', 1000000000000.0, int(1000000.0))
        total = self.calc.calculate_total()
        self.assertTrue(total > 0)

    def test_edge_none_arguments(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(None, 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('Item', None, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('Item', 1.0, None)

    def test_edge_same_name_same_price_different_representation(self):
        self.calc.add_item('Item', 1.0, 1)
        self.calc.add_item('Item', 1.0, 2)
        self.assertEqual(self.calc.total_items(), 3)

    def test_edge_decimal_price_equality(self):
        self.calc.add_item('Item', Decimal('1.0'), 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', 1.0, 1)