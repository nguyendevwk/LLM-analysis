import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_values(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.tax_rate, 0.23)
        self.assertAlmostEqual(calc.free_shipping_threshold, 100.0)
        self.assertAlmostEqual(calc.shipping_cost, 10.0)

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.tax_rate, 0.15)
        self.assertAlmostEqual(calc.free_shipping_threshold, 50.0)
        self.assertAlmostEqual(calc.shipping_cost, 5.0)

    def test_init_invalid_values_raises_exception(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Book', 15.0)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertIn('Book', self.calc.list_items())

    def test_add_item_custom_quantity(self):
        self.calc.add_item('Pen', 2.0, quantity=5)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_existing_item(self):
        self.calc.add_item('Notebook', 5.0, quantity=2)
        self.calc.add_item('Notebook', 5.0, quantity=3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_invalid_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('InvalidItem', -10.0)

    def test_add_item_invalid_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('InvalidItem', 10.0, quantity=0)

    def test_add_item_invalid_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 10.0)

    def test_remove_item_existing(self):
        self.calc.add_item('Laptop', 1000.0)
        self.calc.remove_item('Laptop')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_non_existent_raises_exception(self):
        with self.assertRaises((KeyError, ValueError)):
            self.calc.remove_item('NonExistentItem')

    def test_clear_order_populated_cart(self):
        self.calc.add_item('Phone', 500.0, 2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_empty_cart(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('Item1', 10.0, 2)
        self.calc.add_item('Item2', 15.0, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 35.0)

    def test_total_items_multiple_quantities(self):
        self.calc.add_item('Item1', 10.0, 3)
        self.calc.add_item('Item2', 20.0, 4)
        self.assertEqual(self.calc.total_items(), 7)

    def test_total_items_empty_order(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_list_items_populated_cart(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Banana', 0.5)
        self.assertEqual(sorted(self.calc.list_items()), ['Apple', 'Banana'])

    def test_list_items_empty_cart(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('Shirt', 20.0)
        self.assertFalse(self.calc.is_empty())

    def test_apply_discount_zero(self):
        discounted = self.calc.apply_discount(100.0, 0.0)
        self.assertAlmostEqual(discounted, 100.0)

    def test_apply_discount_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -10.0)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_equal_or_above_threshold(self):
        shipping_equal = self.calc.calculate_shipping(100.0)
        shipping_above = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping_equal, 0.0)
        self.assertAlmostEqual(shipping_above, 0.0)

    def test_calculate_shipping_zero_or_negative_subtotal(self):
        shipping_zero = self.calc.calculate_shipping(0.0)
        self.assertAlmostEqual(shipping_zero, 10.0)

    def test_calculate_tax_positive_amount(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-50.0)

    def test_calculate_total_standard_order(self):
        self.calc.add_item('Item1', 40.0, 1)
        total = self.calc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 61.5)