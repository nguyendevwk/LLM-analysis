import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_init_custom_values(self):
        custom_calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(custom_calc.tax_rate, 0.1)
        self.assertEqual(custom_calc.free_shipping_threshold, 50.0)
        self.assertEqual(custom_calc.shipping_cost, 5.0)

    def test_add_item_single_default_quantity(self):
        self.calc.add_item('Apple', 2.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertIn('Apple', self.calc.list_items())

    def test_add_item_single_custom_quantity(self):
        self.calc.add_item('Banana', 1.5, quantity=4)
        self.assertEqual(self.calc.total_items(), 4)

    def test_add_item_multiple_items(self):
        self.calc.add_item('Apple', 2.5)
        self.calc.add_item('Banana', 1.5, quantity=2)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertEqual(set(self.calc.list_items()), {'Apple', 'Banana'})

    def test_add_item_existing_item(self):
        self.calc.add_item('Apple', 2.5, quantity=2)
        self.calc.add_item('Apple', 2.5, quantity=3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertEqual(self.calc.get_subtotal(), 12.5)

    def test_add_item_invalid_zero_or_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Freebie', 0.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Negative', -5.0)

    def test_add_item_invalid_zero_or_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.5, quantity=0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.5, quantity=-2)

    def test_add_item_invalid_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 2.5)

    def test_remove_item_normal(self):
        self.calc.add_item('Apple', 2.5)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_non_existent(self):
        with self.assertRaises((KeyError, ValueError)):
            self.calc.remove_item('NonExistent')

    def test_get_subtotal_normal(self):
        self.calc.add_item('Apple', 2.0, quantity=3)
        self.calc.add_item('Banana', 4.0, quantity=1)
        self.assertEqual(self.calc.get_subtotal(), 10.0)

    def test_apply_discount_zero(self):
        discounted = self.calc.apply_discount(100.0, 0.0)
        self.assertEqual(discounted, 100.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -10.0)

    def test_apply_discount_excessive(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 150.0)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertEqual(shipping, 10.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_exact_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_tax_normal(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertEqual(tax, 23.0)

    def test_calculate_tax_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertEqual(tax, 0.0)

    def test_total_items_normal(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_empty_order(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_normal(self):
        self.calc.add_item('A', 10.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_normal(self):
        self.calc.add_item('A', 10.0)
        self.calc.add_item('B', 20.0)
        self.assertEqual(sorted(self.calc.list_items()), ['A', 'B'])

    def test_list_items_empty_order(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_true_case(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false_case(self):
        self.calc.add_item('A', 10.0)
        self.assertFalse(self.calc.is_empty())