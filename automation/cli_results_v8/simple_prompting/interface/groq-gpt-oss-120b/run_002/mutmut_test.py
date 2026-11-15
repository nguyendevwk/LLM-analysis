import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_item_single(self):
        self.calc.add_item('Apple', 1.5)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 1)
        self.assertEqual(self.calc.get_subtotal(), 1.5)
        self.assertEqual(self.calc.list_items(), ['Apple'])

    def test_add_item_multiple_quantities(self):
        self.calc.add_item('Banana', 0.8, quantity=3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.4)

    def test_remove_nonexistent_item_raises(self):
        with self.assertRaises(Exception):
            self.calc.remove_item('Nonexistent')

    def test_apply_discount_invalid_type(self):
        with self.assertRaises(Exception):
            self.calc.apply_discount('100', '10')

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(80.0)
        self.assertAlmostEqual(shipping, self.calc.shipping_cost)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(Exception):
            self.calc.calculate_shipping('100')

    def test_calculate_tax(self):
        amount = 100.0
        tax = self.calc.calculate_tax(amount)
        self.assertAlmostEqual(tax, amount * self.calc.tax_rate)

    def test_calculate_tax_zero(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertEqual(tax, 0.0)

    def test_total_items_counts_correctly(self):
        self.calc.add_item('A', 1.0, quantity=1)
        self.calc.add_item('B', 2.0, quantity=4)
        self.assertEqual(self.calc.total_items(), 5)

    def test_list_items_multiple(self):
        self.calc.add_item('Pen', 1.2)
        self.calc.add_item('Notebook', 3.5)
        self.assertCountEqual(self.calc.list_items(), ['Pen', 'Notebook'])

    def test_add_item_invalid_name(self):
        with self.assertRaises(Exception):
            self.calc.add_item(123, 1.0)

    def test_add_item_invalid_price(self):
        with self.assertRaises(Exception):
            self.calc.add_item('InvalidPrice', 'free')

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(Exception):
            self.calc.add_item('InvalidQty', 1.0, quantity=-2)