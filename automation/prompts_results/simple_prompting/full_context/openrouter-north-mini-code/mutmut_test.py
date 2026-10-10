import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_values(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertEqual(self.calc.items, [])

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="high")

    def test_init_invalid_tax_rate_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="low")

    def test_init_invalid_threshold_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="cost")

    def test_init_invalid_shipping_cost_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_add_item_valid(self):
        self.calc.add_item("Apple", 1.0, 5)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]["name"], "Apple")
        self.assertEqual(self.calc.items[0]["price"], 1.0)
        self.assertEqual(self.calc.items[0]["quantity"], 5)

    def test_add_item_duplicate_same_price(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.add_item("Apple", 1.0, 3)
        self.assertEqual(len(self.calc.items