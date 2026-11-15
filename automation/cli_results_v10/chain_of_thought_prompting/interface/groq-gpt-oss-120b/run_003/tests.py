import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_default_initialization(self):
        self.assertAlmostEqual(self.calc.tax_rate, 0.23)
        self.assertAlmostEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertAlmostEqual(self.calc.shipping_cost, 10.0)

    def test_custom_initialization(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.tax_rate, 0.1)
        self.assertAlmostEqual(calc.free_shipping_threshold, 50.0)
        self.assertAlmostEqual(calc.shipping_cost, 5.0)

    def test_add_item_first(self):
        self.calc.add_item('Apple', 1.5)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.5)

    def test_add_item_explicit_quantity(self):
        self.calc.add_item('Banana', 0.8, 5)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.0)

    def test_add_item_repeat_same_price(self):
        self.calc.add_item('Banana', 0.8, 2)
        self.calc.add_item('Banana', 0.8, 3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.0)
        self.assertEqual(self.calc.list_items(), ['Banana'])

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 2.0, 1)

    def test_add_item_non_string_name(self):
        with self.assertRaises(Exception):
            self.calc.add_item(123, 2.0, 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', -0.5, 1)

    def test_add_item_zero_price(self):
        self.calc.add_item('Freebie', 0.0, 1)
        self.assertIn('Freebie', self.calc.list_items())
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Grapes', 2.0, -3)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Grapes', 2.0, 0)

    def test_add_item_price_mismatch_on_repeat(self):
        self.calc.add_item('Milk', 1.2, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Milk', 1.5, 1)

    def test_remove_item_success(self):
        self.calc.add_item('Bread', 2.0)
        self.calc.remove_item('Bread')
        self.assertTrue(self.calc.is_empty())
        self.assertNotIn('Bread', self.calc.list_items())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('NonExisting')

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.5, 1)
        self.calc.add_item('C', 0.5, 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0 * 2 + 2.5 * 1 + 0.5 * 4)

    def test_get_subtotal_empty(self):
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    def test_apply_discount_normal(self):
        result = self.calc.apply_discount(200.0, 20.0)
        self.assertAlmostEqual(result, 180.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(150.0, 0.0)
        self.assertAlmostEqual(result, 150.0)

    def test_apply_discount_equal_subtotal(self):
        result = self.calc.apply_discount(50.0, 50.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_exceeds_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(30.0, 40.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(75.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_at_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_shipping(-10.0)

    def test_calculate_tax_positive(self):
        tax = self.calc.calculate_tax(200.0)
        self.assertAlmostEqual(tax, 46.0)

    def test_calculate_tax_zero(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_total_no_discount_below_threshold(self):
        self.calc.add_item('Item1', 30.0, 2)
        total = self.calc.calculate_total()
        expected = 60.0 + 10.0 + 60.0 * 0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_no_discount_above_threshold(self):
        self.calc.add_item('Item1', 50.0, 3)
        total = self.calc.calculate_total()
        expected = 150.0 + 150.0 * 0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_below_threshold(self):
        self.calc.add_item('Item1', 30.0, 3)
        total = self.calc.calculate_total(discount=10.0)
        discounted = 80.0
        expected = discounted + 10.0 + discounted * 0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_above_threshold(self):
        self.calc.add_item('Item1', 60.0, 3)
        total = self.calc.calculate_total(discount=20.0)
        discounted = 160.0
        expected = discounted + discounted * 0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_equals_subtotal(self):
        self.calc.add_item('Item1', 40.0, 1)
        total = self.calc.calculate_total(discount=40.0)
        expected = 10.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_exceeds_subtotal(self):
        self.calc.add_item('Item1', 30.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=35.0)

    def test_calculate_total_custom_configuration(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item('Item', 45.0, 1)
        total = calc.calculate_total()
        expected = 45.0 + 5.0 + 45.0 * 0.1
        self.assertAlmostEqual(total, expected)

    def test_total_items_aggregated_quantity(self):
        self.calc.add_item('Pen', 1.0, 2)
        self.calc.add_item('Pen', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_list_items_insertion_order(self):
        self.calc.add_item('A', 1.0)
        self.calc.add_item('B', 2.0)
        self.calc.add_item('C', 3.0)
        self.assertEqual(self.calc.list_items(), ['A', 'B', 'C'])

    def test_list_items_no_duplicate_on_repeat(self):
        self.calc.add_item('A', 1.0, 1)
        self.calc.add_item('A', 1.0, 2)
        self.assertEqual(self.calc.list_items(), ['A'])

    def test_list_items_after_removal(self):
        self.calc.add_item('X', 1.0)
        self.calc.add_item('Y', 2.0)
        self.calc.remove_item('X')
        self.assertEqual(self.calc.list_items(), ['Y'])

    def test_list_items_after_clear(self):
        self.calc.add_item('A', 1.0)
        self.calc.add_item('B', 2.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('Item', 1.0)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('Item', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_clear_order_resets_state(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.list_items(), [])
        self.assertAlmostEqual(self.calc.calculate_total(), 0.0)

    def test_clear_order_idempotent(self):
        self.calc.clear_order()
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_add_remove_add_sequence(self):
        self.calc.add_item('Item', 1.0)
        self.calc.remove_item('Item')
        self.calc.add_item('Item', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_large_quantity_and_price(self):
        self.calc.add_item('Expensive', 9999.99, 10000)
        self.assertEqual(self.calc.total_items(), 10000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 9999.99 * 10000)

    def test_floating_point_rounding(self):
        self.calc.add_item('Item', 0.1, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.3)
        total = self.calc.calculate_total()
        expected = 0.3 + 10.0 + 0.3 * 0.23
        self.assertAlmostEqual(total, expected)

    def test_shipping_threshold_change_effect(self):
        self.calc.add_item('Item', 95.0)
        total1 = self.calc.calculate_total(discount=5.0)
        expected1 = 90.0 + 10.0 + 90.0 * 0.23
        self.assertAlmostEqual(total1, expected1)
        self.calc.free_shipping_threshold = 80.0
        total2 = self.calc.calculate_total(discount=5.0)
        expected2 = 90.0 + 90.0 * 0.23
        self.assertAlmostEqual(total2, expected2)

    def test_calculate_total_negative_discount(self):
        self.calc.add_item('Item', 50.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-10.0)

    def test_direct_helper_invalid_inputs(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_shipping(-1.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-0.5)

    def test_list_items_immutability(self):
        self.calc.add_item('A', 1.0)
        items = self.calc.list_items()
        items.pop()
        self.assertEqual(self.calc.list_items(), ['A'])

    def test_add_item_whitespace_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('   ', 1.0, 1)

    def test_add_item_non_numeric_price_quantity(self):
        with self.assertRaises(Exception):
            self.calc.add_item('Item', 'price', 1)
        with self.assertRaises(Exception):
            self.calc.add_item('Item', 1.0, 'qty')

    def test_remove_item_after_clear(self):
        self.calc.clear_order()
        with self.assertRaises(KeyError):
            self.calc.remove_item('Anything')

    def test_calculate_total_empty_order_nonzero_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=5.0)

    def test_calculate_total_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Item', 80.0)
        total = calc.calculate_total()
        expected = 80.0 + 80.0 * 0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Item', 120.0)
        total = calc.calculate_total()
        expected = 120.0
        self.assertAlmostEqual(total, expected)