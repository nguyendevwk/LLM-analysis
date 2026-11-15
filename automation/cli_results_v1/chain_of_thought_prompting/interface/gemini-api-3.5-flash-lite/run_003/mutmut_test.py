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

    def test_add_single_item_default_quantity(self):
        self.calc.add_item('Apple', 2.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertEqual(self.calc.get_subtotal(), 2.5)
        self.assertIn('Apple', self.calc.list_items())
        self.assertFalse(self.calc.is_empty())

    def test_add_item_custom_quantity(self):
        self.calc.add_item('Apple', 2.5, quantity=4)
        self.assertEqual(self.calc.total_items(), 4)
        self.assertEqual(self.calc.get_subtotal(), 10.0)

    def test_add_duplicate_item(self):
        self.calc.add_item('Apple', 2.5, quantity=2)
        self.calc.add_item('Apple', 2.5, quantity=3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertEqual(self.calc.get_subtotal(), 12.5)

    def test_add_item_invalid_price_or_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Invalid', -5.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Invalid', 5.0, quantity=0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Invalid', 5.0, quantity=-2)

    def test_remove_non_existent_item(self):
        self.calc.add_item('Apple', 2.5)
        try:
            self.calc.remove_item('Banana')
        except Exception as e:
            self.assertIsInstance(e, (KeyError, ValueError))

    def test_state_checks(self):
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.list_items(), [])
        self.calc.add_item('Apple', 10.0, 2)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 2)
        self.assertEqual(self.calc.list_items(), ['Apple'])

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('Apple', 2.0, 3)
        self.calc.add_item('Banana', 1.5, 2)
        self.assertEqual(self.calc.get_subtotal(), 9.0)

    def test_apply_valid_discount(self):
        subtotal = 100.0
        discounted = self.calc.apply_discount(subtotal, 0.2)
        self.assertEqual(discounted, 80.0)

    def test_apply_edge_case_discounts(self):
        subtotal = 100.0
        self.assertEqual(self.calc.apply_discount(subtotal, 0.0), 100.0)
        self.assertEqual(self.calc.apply_discount(subtotal, 1.0), 0.0)

    def test_apply_invalid_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.5)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertEqual(shipping, 10.0)

    def test_calculate_shipping_at_or_above_threshold(self):
        shipping_at = self.calc.calculate_shipping(100.0)
        shipping_above = self.calc.calculate_shipping(150.0)
        self.assertEqual(shipping_at, 0.0)
        self.assertEqual(shipping_above, 0.0)

    def test_calculate_tax(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertEqual(tax, 23.0)

    def test_calculate_total_no_discount(self):
        self.calc.add_item('Item', 50.0, 1)
        total = self.calc.calculate_total(discount=0.0)
        expected_subtotal = 50.0
        expected_shipping = 10.0
        expected_tax = (expected_subtotal + expected_shipping) * 0.23
        expected_total = expected_subtotal + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)