import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_parameters(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom_parameters(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_add_item_typical(self):
        self.calc.add_item('apple', 1.0, 2)
        self.assertEqual(self.calc.get_subtotal(), 2.0)
        self.assertEqual(self.calc.total_items(), 2)

    def test_add_item_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('orange', -1.0, 1)

    def test_add_item_non_string_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_non_float_price_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('pear', '1.0', 1)

    def test_add_item_non_int_quantity_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('pear', 1.0, 1.5)

    def test_remove_item_non_string_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_after_add(self):
        self.calc.add_item('book', 12.5, 2)
        self.assertEqual(self.calc.get_subtotal(), 25.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('pen', 1.0, 3)
        self.calc.add_item('pencil', 0.5, 4)
        self.assertEqual(self.calc.get_subtotal(), 1.0 * 3 + 0.5 * 4)

    def test_apply_discount_typical(self):
        result = self.calc.apply_discount(100.0, 0.1)
        self.assertEqual(result, 90.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(50.0, 0.0)
        self.assertEqual(result, 50.0)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(30.0, 1.0)
        self.assertEqual(result, 0.0)

    def test_apply_discount_invalid_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -0.1)

    def test_apply_discount_invalid_over_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, 1.5)

    def test_apply_discount_non_numeric_subtotal(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)

    def test_apply_discount_non_numeric_discount(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '0.1')

    def test_calculate_shipping_below_threshold(self):
        self.calc.free_shipping_threshold = 100.0
        self.calc.shipping_cost = 10.0
        cost = self.calc.calculate_shipping(50.0)
        self.assertEqual(cost, 10.0)

    def test_calculate_shipping_at_threshold(self):
        self.calc.free_shipping_threshold = 100.0
        self.calc.shipping_cost = 10.0
        cost = self.calc.calculate_shipping(100.0)
        self.assertEqual(cost, 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.calc.free_shipping_threshold = 100.0
        self.calc.shipping_cost = 10.0
        cost = self.calc.calculate_shipping(150.0)
        self.assertEqual(cost, 0.0)

    def test_calculate_shipping_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50')

    def test_calculate_tax_typical(self):
        self.calc.tax_rate = 0.23
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero(self):
        self.calc.tax_rate = 0.23
        tax = self.calc.calculate_tax(0.0)
        self.assertEqual(tax, 0.0)

    def test_calculate_tax_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_no_discount(self):
        self.calc.add_item('item', 50.0, 1)
        total = self.calc.calculate_total()
        expected = (50.0 + 10.0) * (1 + self.calc.tax_rate)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('item', 80.0, 1)
        total = self.calc.calculate_total(discount=0.1)
        discounted = 80.0 - 8.0
        shipping = 10.0
        amount_before_tax = discounted + shipping
        tax = amount_before_tax * self.calc.tax_rate
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount_type(self):
        self.calc.add_item('item', 10.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_calculate_total_invalid_discount_range(self):
        self.calc.add_item('item', 10.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.5)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_after_add(self):
        self.calc.add_item('a', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_multiple(self):
        self.calc.add_item('a', 1.0, 2)
        self.calc.add_item('b', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('y', 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_after_add(self):
        self.calc.add_item('foo', 1.0, 1)
        self.calc.add_item('bar', 2.0, 1)
        items = self.calc.list_items()
        self.assertEqual(set(items), {'foo', 'bar'})
        self.assertEqual(len(items), 2)

    def test_list_items_duplicate_names(self):
        self.calc.add_item('same', 1.0, 2)
        self.calc.add_item('same', 1.0, 3)
        items = self.calc.list_items()
        self.assertIsInstance(items, list)
        self.assertTrue(all((isinstance(i, str) for i in items)))
        self.assertIn('same', items)