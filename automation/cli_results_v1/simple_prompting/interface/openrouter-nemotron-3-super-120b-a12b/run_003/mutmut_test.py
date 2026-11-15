import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_init_custom(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_add_item_valid(self):
        self.calc.add_item('apple', 1.0, 2)
        self.assertEqual(self.calc.get_subtotal(), 2.0)

    def test_add_item_default_quantity(self):
        self.calc.add_item('banana', 0.5)
        self.assertEqual(self.calc.get_subtotal(), 0.5)

    def test_add_item_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('orange', -1.0)

    def test_add_item_non_numeric_price_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('item', 'price')

    def test_add_item_non_int_quantity_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('item', 1.0, 2.5)

    def test_add_item_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('item', 1.0, -1)

    def test_add_item_duplicate_increases_quantity(self):
        self.calc.add_item('pear', 2.0)
        self.calc.add_item('pear', 2.0, 3)
        self.assertEqual(self.calc.get_subtotal(), 8.0)

    def test_remove_item_existing(self):
        self.calc.add_item('grapes', 3.0)
        self.calc.remove_item('grapes')
        self.assertTrue(self.calc.is_empty())

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('a', 10.0, 2)
        self.calc.add_item('b', 5.0, 3)
        self.assertEqual(self.calc.get_subtotal(), 35.0)

    def test_apply_discount_valid(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.1), 90.0)

    def test_apply_discount_zero(self):
        self.assertEqual(self.calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        self.assertEqual(self.calc.apply_discount(20.0, 1.0), 0.0)

    def test_apply_discount_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -0.1)

    def test_apply_discount_over_one_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, 1.5)

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_tax(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200.0), 46.0)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item('expensive', 120.0)
        self.assertAlmostEqual(self.calc.calculate_total(), 120.0 + 0.0 + 120.0 * 0.23)

    def test_total_items(self):
        self.calc.add_item('pen', 1.0, 4)
        self.calc.add_item('pencil', 0.5, 2)
        self.assertEqual(self.calc.total_items(), 6)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_list_items(self):
        self.calc.add_item('a', 1.0)
        self.calc.add_item('b', 2.0)
        self.calc.add_item('a', 1.0, 2)
        self.assertSetEqual(set(self.calc.list_items()), {'a', 'b'})

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('x', 1.0)
        self.assertFalse(self.calc.is_empty())