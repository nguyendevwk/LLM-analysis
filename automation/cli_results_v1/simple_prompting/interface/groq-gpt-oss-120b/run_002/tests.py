import unittest
from order_calculator import OrderCalculator

class OrderCalculatorTest(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_default_initialization(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_custom_initialization(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_add_item_normal(self):
        self.calc.add_item('Apple', 2.5, 3)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.5)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Banana', 1.0)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0)

    def test_add_item_invalid_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', -0.5, 2)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Grape', 0.5, 0)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Pear', 0.5, 'two')

    def test_remove_item_existing(self):
        self.calc.add_item('Mango', 3.0, 2)
        self.calc.remove_item('Mango')
        self.assertTrue(self.calc.is_empty())
        self.assertNotIn('Mango', self.calc.list_items())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('Nonexistent')

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('ItemA', 10.0, 1)
        self.calc.add_item('ItemB', 5.0, 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 30.0)

    def test_apply_discount_normal(self):
        result = self.calc.apply_discount(100.0, 15.0)
        self.assertAlmostEqual(result, 85.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(result, 50.0)

    def test_apply_discount_exceeds_subtotal(self):
        result = self.calc.apply_discount(20.0, 30.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(80.0)
        self.assertAlmostEqual(shipping, self.calc.shipping_cost)

    def test_calculate_shipping_at_threshold(self):
        shipping = self.calc.calculate_shipping(self.calc.free_shipping_threshold)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_shipping(-10.0)

    def test_calculate_tax_normal(self):
        tax = self.calc.calculate_tax(200.0)
        self.assertAlmostEqual(tax, 46.0)

    def test_calculate_tax_zero(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_total_no_discount(self):
        self.calc.add_item('Item1', 40.0, 1)
        self.calc.add_item('Item2', 30.0, 2)
        total = self.calc.calculate_total()
        expected_shipping = 0.0
        expected_tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(total, 100.0 + expected_shipping + expected_tax)

    def test_calculate_total_with_discount_and_shipping(self):
        self.calc.add_item('Item1', 20.0, 2)
        total = self.calc.calculate_total(discount=5.0)
        discounted = self.calc.apply_discount(40.0, 5.0)
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_exceeds_subtotal(self):
        self.calc.add_item('Item1', 10.0, 1)
        total = self.calc.calculate_total(discount=20.0)
        discounted = self.calc.apply_discount(10.0, 20.0)
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_total_items(self):
        self.calc.add_item('A', 1.0, 3)
        self.calc.add_item('B', 2.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order(self):
        self.calc.add_item('X', 5.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_list_items(self):
        self.calc.add_item('Alpha', 1.0)
        self.calc.add_item('Beta', 2.0)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['Alpha', 'Beta'])

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('Gamma', 3.0)
        self.assertFalse(self.calc.is_empty())