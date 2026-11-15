import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_values(self):
        self.assertEqual(self.calc.is_empty(), True)
        self.assertEqual(self.calc.total_items(), 0)

    def test_init_custom_values(self):
        custom_calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        custom_calc.add_item('Item', 60.0, 1)
        self.assertEqual(custom_calc.calculate_shipping(60.0), 0.0)
        self.assertEqual(custom_calc.calculate_tax(100.0), 10.0)

    def test_add_item_typical(self):
        self.calc.add_item('Apple', 2.5, 4)
        self.assertEqual(self.calc.total_items(), 4)
        self.assertEqual(self.calc.get_subtotal(), 10.0)
        self.assertFalse(self.calc.is_empty())

    def test_add_item_default_quantity(self):
        self.calc.add_item('Book', 15.0)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertEqual(self.calc.get_subtotal(), 15.0)

    def test_add_item_multiple_times_updates_quantity(self):
        self.calc.add_item('Pen', 1.0, 2)
        self.calc.add_item('Pen', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertEqual(self.calc.get_subtotal(), 5.0)

    def test_add_item_zero_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', 10.0, 0)

    def test_add_item_negative_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', 10.0, -1)

    def test_add_item_negative_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', -5.0, 1)

    def test_add_item_invalid_types_raises_type_error(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calc.add_item(123, 10.0, 1)
        with self.assertRaises((TypeError, ValueError)):
            self.calc.add_item('Item', 'invalid', 1)
        with self.assertRaises((TypeError, ValueError)):
            self.calc.add_item('Item', 10.0, 'invalid')

    def test_remove_nonexistent_item_raises_key_error(self):
        with self.assertRaises((KeyError, ValueError)):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_invalid_type_raises_type_error(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calc.remove_item(None)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('A', 10.0, 2)
        self.calc.add_item('B', 5.5, 4)
        self.assertEqual(self.calc.get_subtotal(), 42.0)

    def test_apply_discount_zero(self):
        discounted = self.calc.apply_discount(100.0, 0.0)
        self.assertEqual(discounted, 100.0)

    def test_apply_discount_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -10.0)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertEqual(shipping, 10.0)

    def test_calculate_shipping_at_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_tax_typical(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertEqual(tax, 0.0)

    def test_calculate_tax_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-50.0)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_multiple(self):
        self.calc.add_item('A', 10.0, 2)
        self.calc.add_item('B', 5.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_populated(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Banana', 2.0, 1)
        items = self.calc.list_items()
        self.assertIn('Apple', items)
        self.assertIn('Banana', items)
        self.assertEqual(len(items), 2)

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('Item', 1.0, 1)
        self.assertFalse(self.calc.is_empty())