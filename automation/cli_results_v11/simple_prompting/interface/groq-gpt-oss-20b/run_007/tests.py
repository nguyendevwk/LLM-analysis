import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_constructor_defaults(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100), 23.0)

    def test_constructor_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.calculate_tax(100), 10.0)
        self.assertAlmostEqual(calc.calculate_shipping(49.99), 5.0)
        self.assertAlmostEqual(calc.calculate_shipping(50.0), 0.0)

    def test_add_item_basic(self):
        self.calc.add_item('apple', 1.5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)
        self.assertEqual(self.calc.total_items(), 2)

    def test_add_item_default_quantity(self):
        self.calc.add_item('banana', 0.75)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.75)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('orange', 0.5, 0)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('pear', -1.0, 1)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('peach', 1.0, -3)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('plum', '1.0', 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('plum', 1.0, '2')

    def test_remove_item_existing(self):
        self.calc.add_item('mango', 2.0, 3)
        self.calc.remove_item('mango')
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.total_items(), 0)

    def test_remove_item_nonexistent(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('nonexistent')

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('a', 1.0, 1)
        self.calc.add_item('b', 2.0, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5.0)

    def test_apply_discount_normal(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 20.0), 80.0)

    def test_apply_discount_excess(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 100.0), 0.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_tax_normal(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200.0), 46.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_total_no_discount(self):
        self.calc.add_item('item', 50.0, 1)
        expected = 50.0 + 10.0 + 23.0
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('item', 80.0, 1)
        expected = 80.0 - 10.0 + 10.0 + 18.3
        self.assertAlmostEqual(self.calc.calculate_total(10.0), expected)

    def test_calculate_total_discount_exceeds_subtotal(self):
        self.calc.add_item('item', 30.0, 1)
        expected = 0.0 + 10.0 + 2.3
        self.assertAlmostEqual(self.calc.calculate_total(50.0), expected)

    def test_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-5.0)

    def test_calculate_total_no_items(self):
        self.assertAlmostEqual(self.calc.calculate_total(), 0.0)

    def test_total_items_multiple(self):
        self.calc.add_item('x', 1.0, 3)
        self.calc.add_item('y', 2.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order(self):
        self.calc.add_item('z', 5.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.total_items(), 0)

    def test_list_items_order(self):
        self.calc.add_item('first', 1.0, 1)
        self.calc.add_item('second', 2.0, 1)
        self.assertEqual(self.calc.list_items(), ['first', 'second'])

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('item', 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('item', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())