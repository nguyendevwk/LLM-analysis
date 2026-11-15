import unittest
from order_calculator import OrderCalculator

class OrderCalculatorTest(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_single_item(self):
        self.calc.add_item('Apple', 1.5)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.5)
        self.assertEqual(self.calc.list_items(), ['Apple'])

    def test_add_multiple_items_with_quantities(self):
        self.calc.add_item('Banana', 0.8, 3)
        self.calc.add_item('Orange', 1.2, 2)
        self.assertEqual(self.calc.total_items(), 5)
        expected_subtotal = 0.8 * 3 + 1.2 * 2
        self.assertAlmostEqual(self.calc.get_subtotal(), expected_subtotal)
        self.assertCountEqual(self.calc.list_items(), ['Banana', 'Orange'])

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Bread', 'free')

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Eggs', -0.5)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Cheese', 3.0, 'many')

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Butter', 2.5, -1)

    def test_apply_discount_zero(self):
        subtotal = 50.0
        discounted = self.calc.apply_discount(subtotal, 0.0)
        self.assertAlmostEqual(discounted, 50.0)

    def test_apply_discount_exceeds_subtotal_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(20.0, 25.0)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_at_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_tax(self):
        tax = self.calc.calculate_tax(200.0)
        self.assertAlmostEqual(tax, 200.0 * 0.23)

    def test_total_items_counts_quantities(self):
        self.calc.add_item('Pen', 1.0, 5)
        self.calc.add_item('Notebook', 2.5, 3)
        self.assertEqual(self.calc.total_items(), 8)