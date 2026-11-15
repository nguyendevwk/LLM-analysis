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
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0)

    def test_add_item_invalid_type_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_invalid_type_price(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('apple', '1.0')

    def test_add_item_invalid_type_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('apple', 1.0, '2')

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('apple', 1.0, -1)

    def test_remove_item_existing(self):
        self.calc.add_item('apple', 1.0, 2)
        self.calc.remove_item('apple')
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    def test_remove_item_invalid_type(self):
        self.calc.add_item('apple', 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_after_add(self):
        self.calc.add_item('apple', 1.0, 2)
        self.calc.add_item('banana', 0.5, 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.0)

    def test_apply_discount_valid(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.1), 90.0)
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 0.0), 50.0)
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100.0', 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '0.1')

    def test_apply_discount_out_of_range(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.5)

    def test_calculate_shipping_free(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_not_free(self):
        self.assertEqual(self.calc.calculate_shipping(99.99), 10.0)
        self.assertEqual(self.calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('100.0')

    def test_calculate_tax_valid(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100.0')

    def test_calculate_total_default_discount(self):
        self.calc.add_item('item', 50.0, 2)
        subtotal = self.calc.get_subtotal()
        discounted = self.calc.apply_discount(subtotal, 0.0)
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('item', 80.0, 1)
        self.calc.add_item('other', 30.0, 1)
        discount = 0.1
        subtotal = self.calc.get_subtotal()
        discounted = self.calc.apply_discount(subtotal, discount)
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(discount), expected)

    def test_calculate_total_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.1')

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_after_add(self):
        self.calc.add_item('a', 1.0, 3)
        self.calc.add_item('b', 2.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_list_items(self):
        self.calc.add_item('apple', 1.0, 2)
        self.calc.add_item('banana', 0.5, 1)
        items = self.calc.list_items()
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 2)
        for entry in items:
            self.assertIsInstance(entry, str)
            self.assertTrue(any((name in entry for name in ('apple', 'banana'))))

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('item', 1.0, 1)
        self.assertFalse(self.calc.is_empty())
        self.calc.remove_item('item')
        self.assertTrue(self.calc.is_empty())