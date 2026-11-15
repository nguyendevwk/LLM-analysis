import unittest
from order_calculator import OrderCalculator

class OrderCalculatorTest(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_item_and_subtotal(self):
        self.calc.add_item('apple', 2.0, 3)
        self.calc.add_item('banana', 1.5, 2)
        self.assertFalse(self.calc.is_empty())
        self.assertCountEqual(self.calc.list_items(), ['apple', 'banana'])
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 9.0)

    def test_calculate_shipping_free(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_tax(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_add_item_invalid_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('apple', 'free', 1)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('apple', 1.0, 'many')
        with self.assertRaises(ValueError):
            self.calc.add_item('apple', 1.0, 0)