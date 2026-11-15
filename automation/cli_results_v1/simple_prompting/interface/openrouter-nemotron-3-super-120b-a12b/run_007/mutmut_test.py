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

    def test_add_item_new(self):
        self.calc.add_item('apple', 1.0, 2)
        self.assertEqual(self.calc.get_subtotal(), 2.0)
        self.assertEqual(self.calc.total_items(), 2)

    def test_add_item_existing_increments_quantity(self):
        self.calc.add_item('apple', 1.0, 1)
        self.calc.add_item('apple', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 4)
        self.assertEqual(self.calc.get_subtotal(), 4.0)

    def test_add_item_default_quantity(self):
        self.calc.add_item('banana', 0.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertEqual(self.calc.get_subtotal(), 0.5)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('apple', '1.0')

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('apple', -1.0)

    def test_add_item_non_int_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('apple', 1.0, 2.5)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('apple', 1.0, -1)

    def test_remove_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('a', 2.0, 3)
        self.calc.add_item('b', 5.0, 1)
        self.assertEqual(self.calc.get_subtotal(), 2.0 * 3 + 5.0 * 1)

    def test_apply_discount_zero(self):
        self.assertEqual(self.calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_partial(self):
        self.assertEqual(self.calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_full(self):
        self.assertEqual(self.calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_invalid_types(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, '0.1')

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(50.0), self.calc.shipping_cost)

    def test_calculate_shipping_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50')

    def test_calculate_tax(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_no_discount(self):
        self.calc.add_item('item', 50.0, 2)
        expected = 123.0
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('item', 50.0, 2)
        expected = 123.0
        self.assertAlmostEqual(self.calc.calculate_total(0.1), expected)

    def test_calculate_total_free_shipping_after_discount(self):
        self.calc.add_item('item', 80.0, 2)
        expected = 128.0 * 1.23
        self.assertAlmostEqual(self.calc.calculate_total(0.2), expected)

    def test_calculate_total_invalid_discount_type(self):
        self.calc.add_item('item', 10.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.1')

    def test_total_items(self):
        self.calc.add_item('a', 1.0, 3)
        self.calc.add_item('b', 2.0, 4)
        self.assertEqual(self.calc.total_items(), 7)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_list_items(self):
        self.calc.add_item('apple', 1.0, 2)
        self.calc.add_item('banana', 0.5, 1)
        self.assertCountEqual(self.calc.list_items(), ['apple', 'banana'])

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('a', 1.0, 1)
        self.assertFalse(self.calc.is_empty())
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
if __name__ == '__main__':
    unittest.main()