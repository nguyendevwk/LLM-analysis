import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_custom_parameters(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 5.0)
        self.assertAlmostEqual(calc.calculate_shipping(30.0), 5.0)
        self.assertAlmostEqual(calc.calculate_shipping(60.0), 0.0)

    def test_add_item_single(self):
        self.calc.add_item('apple', 1.0, 3)
        self.assertIn('apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_add_item_multiple_different(self):
        self.calc.add_item('book', 10.0, 2)
        self.calc.add_item('pen', 2.0, 5)
        items = set(self.calc.list_items())
        self.assertEqual(items, {'book', 'pen'})
        self.assertEqual(self.calc.total_items(), 7)
        self.assertAlmostEqual(self.calc.get_subtotal(), 30.0)

    def test_add_item_same_name_increases_quantity(self):
        self.calc.add_item('nut', 1.5, 1)
        self.calc.add_item('nut', 1.5, 4)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.5)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('item', 'price', 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('item', -1.0, 1)

    def test_add_item_non_int_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('item', 1.0, 2.5)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('item', 1.0, -1)

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('ghost')

    def test_get_subtotal_after_operations(self):
        self.calc.add_item('a', 4.0, 1)
        self.calc.add_item('b', 3.0, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10.0)
        self.calc.remove_item('a')
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0)

    def test_apply_discount_typical(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.2), 80.0)
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 0.0), 50.0)
        self.assertAlmostEqual(self.calc.apply_discount(30.0, 1.0), 0.0)

    def test_apply_discount_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '0.1')

    def test_apply_discount_out_of_range(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.5)

    def test_calculate_shipping_below_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(80.0), 10.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_custom_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=200.0, shipping_cost=15.0)
        self.assertAlmostEqual(calc.calculate_shipping(199.0), 15.0)
        self.assertAlmostEqual(calc.calculate_shipping(200.0), 0.0)

    def test_calculate_total_no_discount(self):
        self.calc.add_item('item1', 40.0, 2)
        self.calc.add_item('item2', 30.0, 1)
        expected = 110.0 + 0.0 + 25.3
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('item', 50.0, 2)
        expected = 90.0 + 10.0 + 23.0
        self.assertAlmostEqual(self.calc.calculate_total(0.1), expected)

    def test_calculate_total_free_shipping_after_discount(self):
        self.calc.add_item('cheap', 30.0, 4)
        self.calc.clear_order()
        self.calc.add_item('mid', 55.0, 2)
        expected = 99.0 + 10.0 + 25.07
        self.assertAlmostEqual(self.calc.calculate_total(0.1), expected)

    def test_total_items(self):
        self.calc.add_item('a', 1.0, 3)
        self.calc.add_item('b', 2.0, 4)
        self.assertEqual(self.calc.total_items(), 7)
        self.calc.remove_item('a')
        self.assertEqual(self.calc.total_items(), 4)

    def test_list_items_returns_names(self):
        self.calc.add_item('alpha', 1.0, 1)
        self.calc.add_item('beta', 2.0, 2)
        self.calc.add_item('gamma', 3.0, 3)
        listed = self.calc.list_items()
        self.assertEqual(set(listed), {'alpha', 'beta', 'gamma'})
        self.assertEqual(len(listed), 3)

    def test_is_empty_behavior(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('z', 1.0, 1)
        self.assertFalse(self.calc.is_empty())
        self.calc.remove_item('z')
        self.assertTrue(self.calc.is_empty())