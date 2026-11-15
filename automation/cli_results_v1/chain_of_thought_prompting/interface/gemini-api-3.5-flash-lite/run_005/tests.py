import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_default_initialization(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_custom_initialization(self):
        custom_calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(custom_calc.tax_rate, 0.1)
        self.assertEqual(custom_calc.free_shipping_threshold, 50.0)
        self.assertEqual(custom_calc.shipping_cost, 5.0)

    def test_invalid_initialization_parameters(self):
        pass

    def test_add_item_single_default_quantity(self):
        self.calc.add_item('Apple', 2.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertFalse(self.calc.is_empty())
        self.assertIn('Apple', self.calc.list_items())

    def test_add_item_custom_quantity(self):
        self.calc.add_item('Banana', 1.5, quantity=4)
        self.assertEqual(self.calc.total_items(), 4)

    def test_add_existing_item(self):
        self.calc.add_item('Orange', 2.0, quantity=2)
        self.calc.add_item('Orange', 2.0, quantity=3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertEqual(len(self.calc.list_items()), 1)

    def test_add_item_negative_or_zero_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Invalid', -5.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Free', 0.0)

    def test_add_item_zero_or_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', 10.0, quantity=0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', 10.0, quantity=-2)

    def test_add_item_empty_or_invalid_name(self):
        with self.assertRaises((ValueError, TypeError)):
            self.calc.add_item('', 10.0)

    def test_remove_existing_item(self):
        self.calc.add_item('Book', 15.0)
        self.calc.remove_item('Book')
        self.assertTrue(self.calc.is_empty())

    def test_remove_non_existent_item(self):
        with self.assertRaises((KeyError, ValueError)):
            self.calc.remove_item('NonExistent')

    def test_check_empty_order_state(self):
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.list_items(), [])

    def test_check_populated_order_state(self):
        self.calc.add_item('Pen', 1.0, 2)
        self.calc.add_item('Notebook', 5.0, 1)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 3)
        self.assertEqual(set(self.calc.list_items()), {'Pen', 'Notebook'})

    def test_clear_order(self):
        self.calc.add_item('Pen', 1.0, 2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    def test_subtotal_with_single_and_multiple_items(self):
        self.calc.add_item('ItemA', 10.0, 2)
        self.calc.add_item('ItemB', 5.0, 3)
        self.assertEqual(self.calc.get_subtotal(), 35.0)

    def test_subtotal_of_an_empty_order(self):
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_apply_valid_discount(self):
        subtotal = 100.0
        discounted = self.calc.apply_discount(subtotal, 10.0)
        self.assertEqual(discounted, 90.0)

    def test_apply_zero_discount(self):
        subtotal = 50.0
        discounted = self.calc.apply_discount(subtotal, 0.0)
        self.assertEqual(discounted, 50.0)

    def test_apply_discount_greater_than_subtotal(self):
        subtotal = 20.0
        discounted = self.calc.apply_discount(subtotal, 25.0)
        self.assertIn(discounted, (0.0, -5.0))

    def test_apply_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -5.0)

    def test_subtotal_below_free_shipping_threshold(self):
        shipping = self.calc.calculate_shipping(90.0)
        self.assertEqual(shipping, 10.0)

    def test_subtotal_exactly_at_free_shipping_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertEqual(shipping, 0.0)

    def test_subtotal_above_free_shipping_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_tax_on_positive_amount(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertEqual(tax, 23.0)

    def test_calculate_tax_on_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertEqual(tax, 0.0)

    def test_calculate_total_without_discount(self):
        self.calc.add_item('Item', 50.0, 1)
        total = self.calc.calculate_total(discount=0.0)
        expected_subtotal = 50.0
        expected_shipping = 10.0
        expected_tax = (expected_subtotal + expected_shipping) * 0.23
        expected_total = expected_subtotal + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_with_discount_and_free_shipping(self):
        self.calc.add_item('Item', 150.0, 1)
        total = self.calc.calculate_total(discount=30.0)
        expected_subtotal = 120.0
        expected_shipping = 0.0
        expected_tax = expected_subtotal * 0.23
        expected_total = expected_subtotal + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_for_an_empty_order(self):
        total = self.calc.calculate_total()
        self.assertEqual(total, 0.0)