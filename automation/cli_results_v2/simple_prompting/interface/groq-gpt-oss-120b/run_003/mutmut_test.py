import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_item_typical(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 2)
        self.assertEqual(self.calc.get_subtotal(), 3.0)
        self.assertListEqual(self.calc.list_items(), ['Apple'])

    def test_add_item_default_quantity(self):
        self.calc.add_item('Banana', 0.75)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertEqual(self.calc.get_subtotal(), 0.75)

    def test_add_item_invalid_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Orange', 'free', 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Grape', 2.0, 'many')

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Lemon', -0.5, 1)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Peach', 1.0, 0)

    def test_remove_item_existing(self):
        self.calc.add_item('Mango', 2.0, 3)
        self.calc.remove_item('Mango')
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('ItemA', 10.0, 1)
        self.calc.add_item('ItemB', 5.0, 2)
        self.assertEqual(self.calc.get_subtotal(), 20.0)

    def test_apply_discount_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(80.0)
        self.assertEqual(shipping, self.calc.shipping_cost)

    def test_calculate_shipping_at_threshold(self):
        shipping = self.calc.calculate_shipping(self.calc.free_shipping_threshold)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        shipping = self.calc.calculate_shipping(-10.0)
        self.assertEqual(shipping, self.calc.shipping_cost)

    def test_calculate_tax_typical(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertEqual(tax, 0.0)

    def test_calculate_total_no_discount_free_shipping(self):
        self.calc.add_item('Item1', 60.0, 2)
        total = self.calc.calculate_total()
        discounted = 120.0
        shipping = 0.0
        tax = discounted * self.calc.tax_rate
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_total_items_multiple(self):
        self.calc.add_item('A', 1.0, 3)
        self.calc.add_item('B', 2.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_list_items_order(self):
        self.calc.add_item('First', 1.0, 1)
        self.calc.add_item('Second', 2.0, 1)
        self.assertListEqual(self.calc.list_items(), ['First', 'Second'])

    def test_is_empty_after_removal(self):
        self.calc.add_item('Solo', 10.0, 1)
        self.calc.remove_item('Solo')
        self.assertTrue(self.calc.is_empty())