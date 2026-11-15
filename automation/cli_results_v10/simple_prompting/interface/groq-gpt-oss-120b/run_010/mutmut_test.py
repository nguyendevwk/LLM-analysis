import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_item_valid(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 2)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Banana', 0.75)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(Exception):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(Exception):
            self.calc.add_item('Orange', 'free', 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(Exception):
            self.calc.add_item('Grapes', -2.0, 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(Exception):
            self.calc.add_item('Pear', 1.0, 'many')

    def test_add_item_negative_quantity(self):
        with self.assertRaises(Exception):
            self.calc.add_item('Peach', 1.0, -3)

    def test_remove_item_existing(self):
        self.calc.add_item('Mango', 2.0, 1)
        self.calc.remove_item('Mango')
        self.assertNotIn('Mango', self.calc.list_items())
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(Exception):
            self.calc.remove_item('Nonexistent')

    def test_get_subtotal(self):
        self.calc.add_item('ItemA', 10.0, 3)
        self.calc.add_item('ItemB', 5.0, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 40.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(Exception):
            self.calc.apply_discount(100.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(80.0)
        self.assertAlmostEqual(shipping, self.calc.shipping_cost)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_tax(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_total_items_multiple(self):
        self.calc.add_item('A', 1.0, 1)
        self.calc.add_item('B', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 4)

    def test_clear_order(self):
        self.calc.add_item('X', 5.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_order(self):
        self.calc.add_item('First', 1.0, 1)
        self.calc.add_item('Second', 2.0, 1)
        self.assertEqual(self.calc.list_items(), ['First', 'Second'])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('Item', 1.0, 1)
        self.assertFalse(self.calc.is_empty())