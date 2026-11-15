import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_default_initialization(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_custom_initialization(self):
        custom_calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(custom_calc.tax_rate, 0.1)
        self.assertEqual(custom_calc.free_shipping_threshold, 50.0)
        self.assertEqual(custom_calc.shipping_cost, 5.0)

    def test_add_single_new_item(self):
        self.calc.add_item('Apple', 2.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertIn('Apple', self.calc.list_items())

    def test_add_item_with_custom_quantity(self):
        self.calc.add_item('Banana', 1.5, 4)
        self.assertEqual(self.calc.total_items(), 4)
        self.assertEqual(self.calc.get_subtotal(), 6.0)

    def test_add_existing_item(self):
        self.calc.add_item('Milk', 3.0, 2)
        self.calc.add_item('Milk', 3.0, 3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertEqual(self.calc.get_subtotal(), 15.0)

    def test_add_item_with_invalid_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Invalid', -5.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Invalid', 0.0)

    def test_add_item_with_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Invalid', 10.0, 0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Invalid', 10.0, -2)

    def test_add_item_with_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 10.0, 1)

    def test_remove_existing_item(self):
        self.calc.add_item('Bread', 2.0)
        self.calc.remove_item('Bread')
        self.assertTrue(self.calc.is_empty())

    def test_remove_non_existent_item(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('NonExistent')

    def test_subtotal_on_empty_order(self):
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_subtotal_with_multiple_items(self):
        self.calc.add_item('Item1', 10.0, 2)
        self.calc.add_item('Item2', 5.5, 4)
        self.assertEqual(self.calc.get_subtotal(), 42.0)

    def test_apply_valid_discount(self):
        subtotal = 100.0
        discounted = self.calc.apply_discount(subtotal, 15.0)
        self.assertEqual(discounted, 85.0)

    def test_apply_zero_discount(self):
        subtotal = 50.0
        discounted = self.calc.apply_discount(subtotal, 0.0)
        self.assertEqual(discounted, 50.0)

    def test_apply_discount_exceeding_subtotal(self):
        subtotal = 20.0
        discounted = self.calc.apply_discount(subtotal, 25.0)
        self.assertEqual(discounted, 0.0)

    def test_apply_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -5.0)

    def test_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertEqual(shipping, 10.0)

    def test_shipping_at_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertEqual(shipping, 0.0)

    def test_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_tax_with_default_rate(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertEqual(tax, 23.0)

    def test_calculate_tax_on_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertEqual(tax, 0.0)

    def test_calculate_total_standard_order(self):
        self.calc.add_item('Item', 50.0, 1)
        total = self.calc.calculate_total(discount=0.0)
        expected_subtotal = 50.0
        expected_shipping = 10.0
        expected_tax = (expected_subtotal + expected_shipping) * 0.23
        expected_total = expected_subtotal + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_on_empty_order(self):
        total = self.calc.calculate_total()
        self.assertEqual(total, 0.0)

    def test_check_is_empty_state(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('Test', 10.0)
        self.assertFalse(self.calc.is_empty())

    def test_count_total_items(self):
        self.calc.add_item('A', 1.0, 3)
        self.calc.add_item('B', 2.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_list_items(self):
        self.calc.add_item('Pen', 1.5)
        self.calc.add_item('Notebook', 3.0)
        items = self.calc.list_items()
        self.assertIn('Pen', items)
        self.assertIn('Notebook', items)
        self.assertEqual(len(items), 2)

    def test_clear_order(self):
        self.calc.add_item('Eraser', 0.5, 5)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.get_subtotal(), 0.0)