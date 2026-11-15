import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_custom_params(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertTrue(calc.is_empty())

    def test_add_item_valid(self):
        self.calc.add_item('apple', 1.0, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertIn('apple', self.calc.list_items())
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0)

    def test_add_item_single_quantity(self):
        self.calc.add_item('book', 12.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 12.5)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('bad', -1.0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('bad', 1.0, -1)

    def test_add_item_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_non_numeric_price(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('item', 'price')

    def test_add_item_non_int_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('item', 1.0, 2.5)

    def test_remove_item_after_multiple_adds(self):
        self.calc.add_item('a', 5.0, 2)
        self.calc.add_item('b', 3.0, 1)
        self.calc.remove_item('a')
        self.assertEqual(self.calc.total_items(), 1)
        self.assertIn('b', self.calc.list_items())
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('x', 4.0, 2)
        self.calc.add_item('y', 1.5, 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.0 * 2 + 1.5 * 4)

    def test_apply_discount_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_invalid_subtotal_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 10)

    def test_apply_discount_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '10')

    def test_calculate_shipping_free_threshold(self):
        self.calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_charged(self):
        self.calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(self.calc.calculate_shipping(99.99), 10.0)
        self.assertEqual(self.calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_invalid_input(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('amount')

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_positive(self):
        self.calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_invalid_input(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('amt')

    def test_calculate_total_no_discount(self):
        self.calc.add_item('item', 50.0, 2)
        subtotal = self.calc.get_subtotal()
        shipping = self.calc.calculate_shipping(subtotal)
        tax = self.calc.calculate_tax(subtotal + shipping)
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_invalid_discount_type(self):
        self.calc.add_item('item', 10.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total('discount')

    def test_total_items(self):
        self.calc.add_item('a', 1.0, 3)
        self.calc.add_item('b', 2.0, 4)
        self.assertEqual(self.calc.total_items(), 7)

    def test_list_items(self):
        self.calc.add_item('apple', 1.0)
        self.calc.add_item('banana', 2.0)
        self.calc.add_item('apple', 1.0, 2)
        self.assertCountEqual(self.calc.list_items(), ['apple', 'banana'])

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('item', 1.0)
        self.assertFalse(self.calc.is_empty())
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())