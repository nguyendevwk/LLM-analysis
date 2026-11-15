import unittest
from order_calculator import OrderCalculator

class OrderCalculatorTest(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_add_item_normal(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Banana', '1.0', 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Banana', 1.0, '2')

    def test_add_item_zero_quantity(self):
        self.calc.add_item('Orange', 2.0, 0)
        self.assertEqual(self.calc.total_items(), 0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    def test_remove_item_existing(self):
        self.calc.add_item('Milk', 2.5, 1)
        self.calc.remove_item('Milk')
        self.assertNotIn('Milk', self.calc.list_items())
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent_raises(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('Nonexistent')

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('ItemA', 10.0, 1)
        self.calc.add_item('ItemB', 5.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 25.0)

    def test_apply_discount_normal(self):
        subtotal = 100.0
        discounted = self.calc.apply_discount(subtotal, 10.0)
        self.assertAlmostEqual(discounted, 90.0)

    def test_apply_discount_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -5.0)

    def test_calculate_shipping_free(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_cost(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_tax(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_total_no_discount(self):
        self.calc.add_item('A', 20.0, 2)
        total = self.calc.calculate_total()
        expected = 40.0 + self.calc.calculate_tax(40.0) + self.calc.calculate_shipping(40.0)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('B', 50.0, 1)
        total = self.calc.calculate_total(discount=5.0)
        discounted = self.calc.apply_discount(50.0, 5.0)
        expected = discounted + self.calc.calculate_tax(discounted) + self.calc.calculate_shipping(discounted)
        self.assertAlmostEqual(total, expected)

    def test_total_items_count(self):
        self.calc.add_item('X', 1.0, 4)
        self.calc.add_item('Y', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 7)

    def test_clear_order(self):
        self.calc.add_item('Z', 10.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    def test_is_empty_true_after_clear(self):
        self.calc.add_item('Item', 5.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items_contents(self):
        self.calc.add_item('Alpha', 3.0, 1)
        self.calc.add_item('Beta', 4.0, 2)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['Alpha', 'Beta'])