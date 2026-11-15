import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_default_initialization(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_custom_initialization(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_add_item_updates_subtotal_and_counts(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0, 3)
        self.assertIn('apple', calc.list_items())
        self.assertEqual(calc.total_items(), 3)
        self.assertAlmostEqual(calc.get_subtotal(), 6.0)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('banana', 1.5)
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 1.5)

    def test_add_item_invalid_name(self):
        calc = OrderCalculator()
        with self.assertRaises(Exception):
            calc.add_item(123, 1.0, 1)

    def test_add_item_negative_price(self):
        calc = OrderCalculator()
        with self.assertRaises(Exception):
            calc.add_item('orange', -1.0, 1)

    def test_add_item_zero_quantity(self):
        calc = OrderCalculator()
        calc.add_item('pear', 2.0, 0)
        self.assertEqual(calc.total_items(), 0)
        self.assertFalse(calc.list_items())

    def test_remove_existing_item(self):
        calc = OrderCalculator()
        calc.add_item('milk', 3.0, 2)
        calc.remove_item('milk')
        self.assertFalse(calc.list_items())
        self.assertEqual(calc.total_items(), 0)

    def test_remove_nonexistent_item_raises(self):
        calc = OrderCalculator()
        calc.add_item('bread', 2.5, 1)
        with self.assertRaises(Exception):
            calc.remove_item('cheese')

    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        subtotal = 100.0
        discounted = calc.apply_discount(subtotal, 10.0)
        self.assertAlmostEqual(discounted, 90.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        subtotal = 50.0
        discounted = calc.apply_discount(subtotal, 0.0)
        self.assertAlmostEqual(discounted, 50.0)

    def test_apply_discount_exceeds_subtotal(self):
        calc = OrderCalculator()
        subtotal = 30.0
        discounted = calc.apply_discount(subtotal, 40.0)
        self.assertLessEqual(discounted, 0.0)

    def test_apply_discount_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(Exception):
            calc.apply_discount('100', 10)

    def test_calculate_shipping_free_above_threshold(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_free_at_threshold(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(calc.free_shipping_threshold)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_cost_below_threshold(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(20.0)
        self.assertAlmostEqual(shipping, calc.shipping_cost)

    def test_calculate_tax(self):
        calc = OrderCalculator()
        amount = 200.0
        tax = calc.calculate_tax(amount)
        self.assertAlmostEqual(tax, amount * calc.tax_rate)

    def test_calculate_total_without_discount(self):
        calc = OrderCalculator()
        calc.add_item('item1', 40.0, 1)
        calc.add_item('item2', 30.0, 2)
        total = calc.calculate_total()
        expected_subtotal = 100.0
        expected_shipping = 0.0
        expected_tax = expected_subtotal * calc.tax_rate
        self.assertAlmostEqual(total, expected_subtotal + expected_shipping + expected_tax)

    def test_calculate_total_with_discount_and_shipping(self):
        calc = OrderCalculator()
        calc.add_item('item', 20.0, 2)
        total = calc.calculate_total(discount=5.0)
        discounted = 35.0
        shipping = calc.shipping_cost
        tax = discounted * calc.tax_rate
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_total_items_counts_multiple(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 2)
        calc.add_item('b', 2.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_clear_order_resets_state(self):
        calc = OrderCalculator()
        calc.add_item('x', 5.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.get_subtotal(), 0.0)

    def test_is_empty_initially(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_adding(self):
        calc = OrderCalculator()
        calc.add_item('y', 3.0)
        self.assertFalse(calc.is_empty())

    def test_list_items_returns_names(self):
        calc = OrderCalculator()
        calc.add_item('alpha', 1.0)
        calc.add_item('beta', 2.0)
        self.assertCountEqual(calc.list_items(), ['alpha', 'beta'])

    def test_multiple_operations_sequence(self):
        calc = OrderCalculator()
        calc.add_item('a', 10.0, 1)
        calc.add_item('b', 20.0, 2)
        calc.remove_item('a')
        calc.add_item('c', 5.0, 3)
        self.assertCountEqual(calc.list_items(), ['b', 'c'])
        self.assertEqual(calc.total_items(), 5)
        subtotal = calc.get_subtotal()
        self.assertAlmostEqual(subtotal, 20.0 * 2 + 5.0 * 3)