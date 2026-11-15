import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_item_updates_state(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 2)
        self.assertEqual(self.calc.get_subtotal(), 3.0)
        self.assertIn('Apple', self.calc.list_items())

    def test_add_item_default_quantity(self):
        self.calc.add_item('Banana', 0.75)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertEqual(self.calc.get_subtotal(), 0.75)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Orange', 'free', 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Grapes', -2.0, 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Pear', 1.0, 'many')

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', 1.0, -3)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('ItemA', 10.0, 1)
        self.calc.add_item('ItemB', 5.5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 21.0)

    def test_apply_discount_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(80.0)
        self.assertAlmostEqual(shipping, self.calc.shipping_cost)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_tax(self):
        amount = 200.0
        tax = self.calc.calculate_tax(amount)
        self.assertAlmostEqual(tax, amount * self.calc.tax_rate)

    def test_total_items_counts_quantities(self):
        self.calc.add_item('X', 5.0, 3)
        self.calc.add_item('Y', 2.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_list_items_returns_all_names(self):
        names = ['Alpha', 'Beta', 'Gamma']
        for n in names:
            self.calc.add_item(n, 1.0)
        self.assertCountEqual(self.calc.list_items(), names)

    def test_is_empty_transitions(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('Delta', 4.0)
        self.assertFalse(self.calc.is_empty())
        self.calc.remove_item('Delta')
        self.assertTrue(self.calc.is_empty())