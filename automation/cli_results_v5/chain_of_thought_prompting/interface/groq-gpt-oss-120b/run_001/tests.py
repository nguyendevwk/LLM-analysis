import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.tax_rate, 0.23, places=5)
        self.assertAlmostEqual(calc.free_shipping_threshold, 100.0, places=5)
        self.assertAlmostEqual(calc.shipping_cost, 10.0, places=5)

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=200.0, shipping_cost=0.0)
        self.assertAlmostEqual(calc.tax_rate, 0.0, places=5)
        self.assertAlmostEqual(calc.free_shipping_threshold, 200.0, places=5)
        self.assertAlmostEqual(calc.shipping_cost, 0.0, places=5)

    def test_init_invalid_non_numeric(self):
        with self.assertRaises((TypeError, ValueError)):
            OrderCalculator(tax_rate='abc')
        with self.assertRaises((TypeError, ValueError)):
            OrderCalculator(free_shipping_threshold='xyz')
        with self.assertRaises((TypeError, ValueError)):
            OrderCalculator(shipping_cost=None)

    def test_init_invalid_negative_numbers(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_add_single_item(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.20)
        self.assertIn('apple', calc.list_items())
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 1.20, places=2)

    def test_add_multiple_distinct_items(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.00, 2)
        calc.add_item('banana', 0.50, 3)
        self.assertListEqual(calc.list_items(), ['apple', 'banana'])
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 1.00 * 2 + 0.50 * 3, places=2)

    def test_add_duplicate_name_aggregates_quantity(self):
        calc = OrderCalculator()
        calc.add_item('banana', 0.50, 2)
        calc.add_item('banana', 0.50, 3)
        self.assertListEqual(calc.list_items(), ['banana'])
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 0.50 * 5, places=2)

    def test_add_item_invalid_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_non_positive_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('apple', 0.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('apple', -5.0, 1)

    def test_add_item_invalid_non_numeric_price(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('apple', 'free', 1)

    def test_add_item_invalid_non_positive_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('apple', 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item('apple', 1.0, -2)

    def test_add_item_invalid_non_integer_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('apple', 1.0, 1.5)
        with self.assertRaises(TypeError):
            calc.add_item('apple', 1.0, 'many')

    def test_remove_existing_item(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.20)
        calc.remove_item('apple')
        self.assertNotIn('apple', calc.list_items())
        self.assertEqual(calc.total_items(), 0)
        self.assertAlmostEqual(calc.get_subtotal(), 0.0, places=2)

    def test_remove_one_of_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.00, 1)
        calc.add_item('banana', 0.50, 2)
        calc.add_item