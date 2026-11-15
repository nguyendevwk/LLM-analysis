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

    def test_add_item_single(self):
        self.calc.add_item('apple', 1.0)
        self.assertEqual(self.calc.list_items(), ['apple'])
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0)

    def test_add_item_multiple_quantity(self):
        self.calc.add_item('banana', 0.5, quantity=4)
        self.assertEqual(self.calc.list_items(), ['banana'])
        self.assertEqual(self.calc.total_items(), 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0)

    def test_add_item_default_quantity(self):
        self.calc.add_item('orange', 2.0)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_multiple_items(self):
        self.calc.add_item('pen', 1.5, quantity=2)
        self.calc.add_item('pencil', 0.5, quantity=3)
        self.assertSetEqual(set(self.calc.list_items()), {'pen', 'pencil'})
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.5 * 2 + 0.5 * 3)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('bad', -1.0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('bad', 1.0, quantity=-1)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('bad', 1.0, quantity=0)

    def test_remove_item_existing(self):
        self.calc.add_item('item', 10.0)
        self.calc.remove_item('item')
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])
        self.assertEqual(self.calc.total_items(), 0)

    def test_get_subtotal_after_operations(self):
        self.calc.add_item('a', 5.0, quantity=2)
        self.calc.add_item('b', 3.0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 13.0)
        self.calc.remove_item('a')
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_apply_discount_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_partial(self):
        self.assertAlmostEqual(self.calc.apply_discount(200.0, 0.1), 180.0)
        self.assertAlmostEqual(self.calc.apply_discount(200.0, 0.5), 100.0)

    def test_apply_discount_full(self):
        self.assertAlmostEqual(self.calc.apply_discount(150.0, 1.0), 0.0)

    def test_apply_discount_invalid_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -0.1)

    def test_apply_discount_invalid_over_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, 1.5)

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_negative(self):
        self.assertEqual(self.calc.calculate_shipping(-10.0), 10.0)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_positive(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200.0), 46.0)

    def test_calculate_total_no_discount(self):
        self.calc.add_item('book', 40.0, quantity=2)
        expected = 80.0 + 10.0 + 90.0 * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('item', 50.0, quantity=3)
        expected = 120.0 + 0.0 + 120.0 * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(discount=0.2), expected)

    def test_calculate_total_free_shipping_edge(self):
        self.calc.add_item('item', 100.0)
        expected = 100.0 + 0.0 + 100.0 * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_total_items(self):
        self.calc.add_item('a', 1.0, quantity=2)
        self.calc.add_item('b', 2.0, quantity=3)
        self.assertEqual(self.calc.total_items(), 5)
        self.calc.remove_item('a')
        self.assertEqual(self.calc.total_items(), 3)

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('something', 1.0)
        self.assertFalse(self.calc.is_empty())