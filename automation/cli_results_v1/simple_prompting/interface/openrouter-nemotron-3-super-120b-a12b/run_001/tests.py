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
        self.calc.add_item('apple', 1.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertFalse(self.calc.is_empty())
        self.assertIn('apple', self.calc.list_items())

    def test_add_item_zero_quantity(self):
        self.calc.add_item('banana', 0.5, 0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.total_items(), 0)
        self.assertTrue(self.calc.is_empty())

    def test_add_item_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('orange', -1.0, 2)

    def test_add_item_non_numeric_price_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('pear', 'two', 1)

    def test_add_item_non_string_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_remove_item_existing(self):
        self.calc.add_item('item1', 10.0, 2)
        self.calc.remove_item('item1')
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])

    def test_remove_item_nonexistent_raises(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('ghost')

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('a', 2.5, 4)
        self.calc.add_item('b', 3.0, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 13.0)

    def test_apply_discount_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_partial(self):
        self.assertAlmostEqual(self.calc.apply_discount(200.0, 0.25), 150.0)

    def test_apply_discount_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -0.1)

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_tax(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200.0), 46.0)

    def test_calculate_total_no_discount(self):
        self.calc.add_item('book', 40.0, 2)
        expected = 80.0 + 10.0 + (80.0 + 10.0) * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('game', 60.0, 1)
        discounted = self.calc.apply_discount(60.0, 0.1)
        expected = discounted + 10.0 + (discounted + 10.0) * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(0.1), expected)

    def test_total_items(self):
        self.calc.add_item('pen', 1.0, 5)
        self.calc.add_item('pencil', 0.5, 3)
        self.assertEqual(self.calc.total_items(), 8)

    def test_clear_order(self):
        self.calc.add_item('x', 5.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items(self):
        self.calc.add_item('a', 1.0, 2)
        self.calc.add_item('b', 2.0, 1)
        self.assertEqual(set(self.calc.list_items()), {'a', 'b'})

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('z', 1.0, 1)
        self.assertFalse(self.calc.is_empty())