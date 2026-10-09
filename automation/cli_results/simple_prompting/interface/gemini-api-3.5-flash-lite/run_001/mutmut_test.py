import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_values(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_add_item_typical(self):
        self.calc.add_item('Apple', 2.0, 3)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 3)
        self.assertEqual(self.calc.get_subtotal(), 6.0)
        self.assertEqual(self.calc.list_items(), ['Apple'])

    def test_add_item_default_quantity(self):
        self.calc.add_item('Banana', 1.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertEqual(self.calc.get_subtotal(), 1.5)

    def test_add_item_accumulates_existing(self):
        self.calc.add_item('Milk', 3.0, 2)
        self.calc.add_item('Milk', 3.0, 1)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertEqual(self.calc.get_subtotal(), 9.0)
        self.assertEqual(self.calc.list_items(), ['Milk'])

    def test_add_item_invalid_price_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Invalid', 0.0, 1)

    def test_add_item_invalid_price_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Invalid', -5.0, 1)

    def test_add_item_invalid_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Invalid', 10.0, 0)

    def test_add_item_invalid_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Invalid', 10.0, -2)

    def test_add_item_invalid_types(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calc.add_item(123, 'ten', 'one')

    def test_remove_item_non_existing(self):
        self.calc.add_item('Apple', 2.0)
        with self.assertRaises((KeyError, ValueError)):
            self.calc.remove_item('NonExistent')

    def test_remove_item_invalid_type(self):
        with self.assertRaises((TypeError, KeyError, ValueError)):
            self.calc.remove_item(None)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('Apple', 2.5, 2)
        self.calc.add_item('Orange', 3.0, 4)
        self.assertEqual(self.calc.get_subtotal(), 17.0)

    def test_apply_discount_percentage(self):
        discounted = self.calc.apply_discount(100.0, 0.2)
        self.assertEqual(discounted, 80.0)

    def test_apply_discount_zero(self):
        discounted = self.calc.apply_discount(100.0, 0.0)
        self.assertEqual(discounted, 100.0)

    def test_apply_discount_full(self):
        discounted = self.calc.apply_discount(100.0, 1.0)
        self.assertEqual(discounted, 0.0)

    def test_apply_discount_invalid_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)

    def test_apply_discount_invalid_greater_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.1)

    def test_apply_discount_invalid_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-50.0, 0.1)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertEqual(shipping, 10.0)

    def test_calculate_shipping_at_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_tax_positive(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertEqual(tax, 23.0)

    def test_calculate_tax_zero(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertEqual(tax, 0.0)

    def test_calculate_tax_invalid_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-50.0)

    def test_calculate_total_invalid_discount(self):
        self.calc.add_item('Item', 50.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.5)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_populated(self):
        self.calc.add_item('A', 10.0, 2)
        self.calc.add_item('B', 5.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_multiple(self):
        self.calc.add_item('Pen', 1.0)
        self.calc.add_item('Notebook', 3.0)
        items = self.calc.list_items()
        self.assertIn('Pen', items)
        self.assertIn('Notebook', items)
        self.assertEqual(len(items), 2)

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('Eraser', 0.5)
        self.assertFalse(self.calc.is_empty())
if __name__ == '__main__':
    unittest.main()