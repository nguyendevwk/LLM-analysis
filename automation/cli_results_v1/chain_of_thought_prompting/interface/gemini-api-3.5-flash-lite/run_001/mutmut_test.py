import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_default_initialization(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    def test_custom_initialization(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.5)
        self.assertFalse(calc.is_empty())
        self.assertEqual(calc.total_items(), 1)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_add_item_custom_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 5)
        self.assertEqual(calc.total_items(), 5)
        self.assertEqual(calc.get_subtotal(), 10.0)

    def test_add_multiple_distinct_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 2)
        calc.add_item('Banana', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})

    def test_add_existing_item_updates_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 2)
        calc.add_item('Apple', 2.0, 3)
        self.assertEqual(calc.total_items(), 5)
        self.assertEqual(len(calc.list_items()), 1)
        self.assertEqual(calc.get_subtotal(), 10.0)

    def test_add_item_invalid_price_or_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', -1.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, -2)

    def test_remove_existing_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 2)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.total_items(), 0)

    def test_remove_non_existent_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 2)
        try:
            calc.remove_item('Banana')
        except Exception as e:
            self.assertIsInstance(e, (KeyError, ValueError))

    def test_clear_populated_order(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 2)
        calc.add_item('Banana', 1.0, 3)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.list_items(), [])

    def test_check_state_empty_order(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.list_items(), [])

    def test_check_state_populated_order(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 2)
        calc.add_item('Banana', 1.0, 3)
        self.assertFalse(calc.is_empty())
        self.assertEqual(calc.total_items(), 5)
        self.assertEqual(sorted(calc.list_items()), ['Apple', 'Banana'])

    def test_get_subtotal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.5, 4)
        calc.add_item('Banana', 1.25, 2)
        self.assertEqual(calc.get_subtotal(), 12.5)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        shipping = calc.calculate_shipping(99.99)
        self.assertEqual(shipping, 10.0)

    def test_calculate_shipping_at_and_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_tax(self):
        calc = OrderCalculator(tax_rate=0.2)
        tax = calc.calculate_tax(50.0)
        self.assertEqual(tax, 10.0)