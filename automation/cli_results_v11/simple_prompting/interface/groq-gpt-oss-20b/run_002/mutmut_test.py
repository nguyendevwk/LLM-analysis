import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_item_valid(self):
        self.calc.add_item('apple', 1.5, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertIn('apple', self.calc.list_items())

    def test_add_item_default_quantity(self):
        self.calc.add_item('banana', 0.5)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('orange', '1.0', 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('orange', 1.0, '2')

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('pear', 1.0, -3)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('pear', 1.0, 0)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('pear', -1.0, 1)

    def test_remove_item_existing(self):
        self.calc.add_item('apple', 1.0, 3)
        self.calc.remove_item('apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('a', 2.0, 2)
        self.calc.add_item('b', 3.5, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.5)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -2.0)

    def test_calculate_shipping_free(self):
        discounted_subtotal = 120.0
        shipping = self.calc.calculate_shipping(discounted_subtotal)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_nonfree(self):
        discounted_subtotal = 80.0
        shipping = self.calc.calculate_shipping(discounted_subtotal)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_at_threshold(self):
        discounted_subtotal = 100.0
        shipping = self.calc.calculate_shipping(discounted_subtotal)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_tax_positive_amount(self):
        amount = 100.0
        tax = self.calc.calculate_tax(amount)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-5.0)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_multiple(self):
        self.calc.add_item('a', 1.0, 2)
        self.calc.add_item('b', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_multiple(self):
        self.calc.add_item('a', 1.0, 1)
        self.calc.add_item('b', 2.0, 1)
        self.assertEqual(self.calc.list_items(), ['a', 'b'])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('a', 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('a', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_add_item_duplicate_name_accumulates_quantity(self):
        self.calc.add_item('dup', 2.0, 1)
        self.calc.add_item('dup', 2.0, 2)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0)

    def test_remove_item_partial_quantity_not_supported(self):
        self.calc.add_item('partial', 5.0, 3)
        self.calc.remove_item('partial')
        self.assertTrue(self.calc.is_empty())

    def test_calculate_shipping_no_items(self):
        shipping = self.calc.calculate_shipping(0.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_tax_no_items(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)
if __name__ == '__main__':
    unittest.main()