import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_item_increases_subtotal(self):
        self.calc.add_item('apple', 2.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0)

    def test_add_item_default_quantity(self):
        self.calc.add_item('banana', 1.5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.5)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('orange', -1.0, 2)

    def test_add_item_zero_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('pear', 1.0, 0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('bread', 2.5, 2)
        self.calc.add_item('butter', 4.0, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 9.0)

    def test_apply_discount_zero(self):
        subtotal = 20.0
        discounted = self.calc.apply_discount(subtotal, 0.0)
        self.assertAlmostEqual(discounted, 20.0)

    def test_apply_discount_excess_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, 15.0)

    def test_apply_discount_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(80.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_at_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_tax(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_total_items_counts_quantities(self):
        self.calc.add_item('a', 1.0, 3)
        self.calc.add_item('b', 2.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_adding(self):
        self.calc.add_item('thing', 1.0)
        self.assertFalse(self.calc.is_empty())

    def test_add_item_non_string_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)