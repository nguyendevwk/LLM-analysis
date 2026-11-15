import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_item_basic(self):
        self.calc.add_item('apple', 1.0, 3)
        self.assertIn('apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 3)

    def test_add_item_default_quantity(self):
        self.calc.add_item('banana', 2.5)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('orange', 'free', 2)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('orange', 1.0, 'two')

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('orange', 1.0, -1)

    def test_remove_item_existing(self):
        self.calc.add_item('apple', 1.0, 2)
        self.calc.remove_item('apple')
        self.assertFalse(self.calc.list_items())
        self.assertTrue(self.calc.is_empty())

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('apple', 1.0, 2)
        self.calc.add_item('banana', 2.5, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.5)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, self.calc.shipping_cost)

    def test_calculate_shipping_at_threshold(self):
        shipping = self.calc.calculate_shipping(self.calc.free_shipping_threshold)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(self.calc.free_shipping_threshold + 1)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_tax_positive(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 100.0 * self.calc.tax_rate)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_total_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='ten')

    def test_total_items_multiple(self):
        self.calc.add_item('a', 1.0, 2)
        self.calc.add_item('b', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_list_items_order(self):
        self.calc.add_item('first', 1.0)
        self.calc.add_item('second', 2.0)
        self.assertListEqual(self.calc.list_items(), ['first', 'second'])

    def test_list_items_empty(self):
        self.assertListEqual(self.calc.list_items(), [])

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('apple', 1.0)
        self.assertFalse(self.calc.is_empty())