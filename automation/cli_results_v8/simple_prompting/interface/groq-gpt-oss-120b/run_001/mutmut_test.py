import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_single_item(self):
        self.calc.add_item('Apple', 1.5)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 1)
        self.assertEqual(self.calc.get_subtotal(), 1.5)
        self.assertEqual(self.calc.list_items(), ['Apple'])

    def test_add_multiple_quantities(self):
        self.calc.add_item('Banana', 0.8, quantity=3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.4)

    def test_apply_discount_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 10)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(80.0)
        self.assertAlmostEqual(shipping, self.calc.shipping_cost)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('100')

    def test_calculate_tax_default_rate(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_custom_rate(self):
        custom_calc = OrderCalculator(tax_rate=0.1)
        tax = custom_calc.calculate_tax(200.0)
        self.assertAlmostEqual(tax, 20.0)

    def test_total_items_counts_correctly(self):
        self.calc.add_item('Item1', 5.0, quantity=1)
        self.calc.add_item('Item2', 3.0, quantity=4)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 10.0)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('NegPrice', -5.0)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('ZeroQty', 5.0, quantity=0)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('BadQty', 5.0, quantity='two')