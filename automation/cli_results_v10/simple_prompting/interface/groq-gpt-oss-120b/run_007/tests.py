import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_initial_state_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.list_items(), [])

    def test_add_item_updates_subtotal_and_items(self):
        self.calc.add_item('apple', 2.5, 3)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.get_subtotal(), 7.5)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertIn('apple', self.calc.list_items())

    def test_add_item_default_quantity(self):
        self.calc.add_item('banana', 1.0)
        self.assertEqual(self.calc.get_subtotal(), 1.0)
        self.assertEqual(self.calc.total_items(), 1)

    def test_remove_item(self):
        self.calc.add_item('apple', 2.0, 2)
        self.calc.add_item('banana', 1.5, 1)
        self.calc.remove_item('apple')
        self.assertEqual(self.calc.get_subtotal(), 1.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertNotIn('apple', self.calc.list_items())

    def test_remove_nonexistent_raises(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('nonexistent')

    def test_apply_discount_typical(self):
        result = self.calc.apply_discount(100.0, 10.0)
        self.assertEqual(result, 90.0)

    def test_apply_discount_excessive(self):
        result = self.calc.apply_discount(20.0, 30.0)
        self.assertGreaterEqual(result, 0.0)

    def test_apply_discount_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, 'ten')

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertEqual(shipping, self.calc.shipping_cost)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_custom_threshold(self):
        custom = OrderCalculator(free_shipping_threshold=200.0, shipping_cost=15.0)
        self.assertEqual(custom.calculate_shipping(150.0), 15.0)
        self.assertEqual(custom.calculate_shipping(250.0), 0.0)

    def test_calculate_tax(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 100.0 * self.calc.tax_rate)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('hundred')

    def test_calculate_total_no_discount(self):
        self.calc.add_item('item', 20.0, 2)
        total = self.calc.calculate_total()
        expected = 40.0 + self.calc.calculate_tax(40.0) + self.calc.calculate_shipping(40.0)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_and_free_shipping(self):
        self.calc.add_item('expensive', 120.0, 1)
        total = self.calc.calculate_total(discount=30.0)
        expected = 90.0 + self.calc.calculate_tax(90.0) + 0.0
        self.assertAlmostEqual(total, expected)

    def test_total_items_counts_quantities(self):
        self.calc.add_item('a', 1.0, 2)
        self.calc.add_item('b', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order(self):
        self.calc.add_item('x', 5.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_is_empty_true_false(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('y', 3.0)
        self.assertFalse(self.calc.is_empty())

    def test_list_items_order(self):
        self.calc.add_item('first', 1.0)
        self.calc.add_item('second', 2.0)
        self.assertEqual(self.calc.list_items(), ['first', 'second'])

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('bad', 'price', 1)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('neg', 1.0, -1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('negprice', -5.0, 1)