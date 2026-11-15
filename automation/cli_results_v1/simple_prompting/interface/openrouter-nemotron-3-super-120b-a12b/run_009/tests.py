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
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_add_item_single(self):
        self.calc.add_item('apple', 1.0, 2)
        self.assertEqual(self.calc.get_subtotal(), 2.0)

    def test_add_item_multiple(self):
        self.calc.add_item('book', 10.0, 1)
        self.calc.add_item('pen', 2.0, 3)
        self.assertEqual(self.calc.get_subtotal(), 16.0)

    def test_add_item_zero_quantity(self):
        self.calc.add_item('item', 5.0, 0)
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_add_item_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('bad', -1.0, 1)

    def test_add_item_non_float_price_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('bad', 'price', 1)

    def test_remove_item_existing(self):
        self.calc.add_item('to_remove', 5.0, 1)
        self.calc.remove_item('to_remove')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent_raises(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('ghost')

    def test_get_subtotal_empty(self):
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_apply_discount_normal(self):
        self.assertEqual(self.calc.apply_discount(100.0, 10.0), 90.0)

    def test_apply_discount_zero(self):
        self.assertEqual(self.calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -5.0)

    def test_apply_discount_exceeds_subtotal(self):
        self.assertEqual(self.calc.apply_discount(20.0, 30.0), -10.0)

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(80.0), 10.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        self.assertEqual(self.calc.calculate_shipping(-10.0), 10.0)

    def test_calculate_tax_normal(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        self.assertAlmostEqual(self.calc.calculate_tax(-50.0), -11.5)

    def test_calculate_total_no_discount_no_shipping(self):
        self.calc.add_item('item', 50.0, 2)
        total = self.calc.calculate_total()
        expected_subtotal = 100.0
        expected_shipping = 0.0
        expected_tax = expected_subtotal * self.calc.tax_rate
        self.assertAlmostEqual(total, expected_subtotal + expected_shipping + expected_tax)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('item', 80.0, 1)
        total = self.calc.calculate_total(discount=10.0)
        discounted = 70.0
        shipping = 10.0
        tax = (discounted + shipping) * self.calc.tax_rate
        self.assertAlmostEqual(total, discounted + shipping + tax)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item('item', 120.0, 1)
        total = self.calc.calculate_total()
        discounted = 120.0
        shipping = 0.0
        tax = (discounted + shipping) * self.calc.tax_rate
        self.assertAlmostEqual(total, discounted + shipping + tax)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_single(self):
        self.calc.add_item('item', 5.0, 3)
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_multiple(self):
        self.calc.add_item('a', 1.0, 2)
        self.calc.add_item('b', 2.0, 4)
        self.assertEqual(self.calc.total_items(), 6)

    def test_clear_order(self):
        self.calc.add_item('x', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items(self):
        self.calc.add_item('apple', 1.0, 2)
        self.calc.add_item('banana', 0.5, 1)
        self.assertCountEqual(self.calc.list_items(), ['apple', 'banana'])

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('item', 1.0, 1)
        self.assertFalse(self.calc.is_empty())