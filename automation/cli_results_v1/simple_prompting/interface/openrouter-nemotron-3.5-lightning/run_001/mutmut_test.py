import unittest
from order_calculator import OrderCalculator
from typing import List

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_init_custom_params(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_add_item_typical(self):
        self.calc.add_item('Widget', 10.0, 2)

    def test_add_item_with_quantity(self):
        self.calc.add_item('Gadget', 25.0, 4)
        self.assertEqual(self.calc.total_items(), 4)

    def test_remove_item_existing(self):
        self.calc.add_item('Thingamajig', 5.0, 1)
        self.calc.remove_item('Thingamajig')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent_raises(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('AbsentItem')

    def test_get_subtotal(self):
        self.calc.add_item('A', 10.0, 3)
        self.calc.add_item('B', 20.0, 1)
        self.assertEqual(self.calc.get_subtotal(), 50.0)

    def test_clear_order(self):
        self.calc.add_item('A', 10.0, 2)
        self.calc.add_item('B', 20.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items(self):
        self.calc.add_item('Item1', 1.0)
        self.calc.add_item('Item2', 2.0)
        items = self.calc.list_items()
        self.assertIn('Item1', items)
        self.assertIn('Item2', items)

    def test_is_empty_initially(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('X', 1.0)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('X', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_apply_discount_zero(self):
        self.assertEqual(self.calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_tax_typical(self):
        self.assertEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_total_no_discount(self):
        self.calc.add_item('Item', 50.0, 1)
        total = self.calc.calculate_total()
        self.assertIsInstance(total, float)
        self.assertGreater(total, 0)

    def test_total_items_multiple_quantities(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('X', 'not_a_price')

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('X', 10.0, -1)

    def test_remove_item_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)