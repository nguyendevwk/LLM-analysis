import unittest
from temp_upload import OrderCalculator, Item

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_item_updates_state(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)
        self.assertIn('Apple', self.calc.list_items())

    def test_add_multiple_items_and_counts(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Banana', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0 + 2.0 * 3)

    def test_remove_item(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 2.0, 1)
        self.calc.remove_item('Apple')
        self.assertNotIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0)

    def test_remove_nonexistent_raises(self):
        with self.assertRaises(Exception):
            self.calc.remove_item('Nonexistent')

    def test_calculate_shipping_free_above_threshold(self):
        discounted = self.calc.free_shipping_threshold + 0.01
        shipping = self.calc.calculate_shipping(discounted)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_below_threshold(self):
        discounted = self.calc.free_shipping_threshold - 10.0
        shipping = self.calc.calculate_shipping(discounted)
        self.assertAlmostEqual(shipping, self.calc.shipping_cost)

    def test_calculate_tax(self):
        amount = 100.0
        tax = self.calc.calculate_tax(amount)
        self.assertAlmostEqual(tax, amount * self.calc.tax_rate)

    def test_list_items_returns_names(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Banana', 2.0, 2)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['Apple', 'Banana'])

    def test_is_empty_true_false(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('Apple', 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(Exception):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(Exception):
            self.calc.add_item('Apple', -1.0, 1)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(Exception):
            self.calc.add_item('Apple', 1.0, -5)