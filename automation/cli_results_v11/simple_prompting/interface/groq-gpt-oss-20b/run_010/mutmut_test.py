import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_apply_discount_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -1.0)

    def test_calculate_shipping(self):
        self.calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(99.99), 10.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(150.0), 0.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(-10.0), 10.0)

    def test_calculate_tax(self):
        self.calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('Apple', 1.0, 1)
        self.assertFalse(self.calc.is_empty())
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_add_item_invalid_inputs(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', -1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.0, -1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.0, 0)
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 'price', 1)

    def test_remove_item_invalid_inputs(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)
if __name__ == '__main__':
    unittest.main()