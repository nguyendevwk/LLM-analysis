import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    def test_default_constructor(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.list_items(), [])

    def test_custom_constructor_values(self):
        c = OrderCalculator(tax_rate=0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(c.tax_rate, 0)
        self.assertEqual(c.free_shipping_threshold, 0)
        self.assertEqual(c.shipping_cost, 0)

    def test_constructor_negative_values_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_single_updates(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0, places=2)

    def test_add_multiple_distinct_items(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 2.0, 3)
        self.assertCountEqual(self.calc.list_items(), ['Apple', 'Banana'])
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0*2 + 2.0*3, places=2)

    def test_add_duplicate_name_behavior(self):
        self.calc.add_item('Banana', 2.0, 1)
        self.calc.add_item('Banana', 2.0, 3)
        subtotal = self.calc.get_subtotal()
        self.assertIn(subtotal, (2.0*4, 2.0*3))

    def test_add_item_zero_price(self):
        self.calc.add_item('Freebie', 0.0, 5)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0, places=2)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Pear', 2.0)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0, places=2)

    def test_add_item_large_quantity(self):
        self.calc.add_item('Bulk', 0.01, 10000)
        self.assertEqual(self.calc.total_items(), 10000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 100.0, places=2)

    def test_add_item_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_non_string_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Milk', -1.0, 1)

    def test_add_item_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Eggs', 0.5, -2)

    def test_add_item_zero_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Bread', 1.0, 0)

    def test_remove_existing_item(self):
        self.calc.add_item('Orange', 1.0, 2)
        self.calc.remove_item('Orange')
        self.assertNotIn('Orange', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0, places=2)

    def test_remove_last_item(self):
        self.calc.add_item('Solo', 5.0, 1)
        self.calc.remove_item('Solo')
        self.assertTrue(self.calc.is_empty())

    def test_remove_nonexistent_item_raises(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(KeyError):
            self.calc.remove_item('NonExisting')

    def test_remove_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('')

    def test_remove_non_string_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(456)

    def test_get_subtotal_empty(self):
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0, places=2)

    def test_get_subtotal_after_adds(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.5, 1)
        self.calc.add_item('C', 0.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0*2 + 2.5*1, places=2)

    def test_get_subtotal_after_removal(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.0, 1)
        self.calc.remove_item('A')
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0, places=2)

    def test_apply_discount_normal(self):
        result = self.calc.apply_discount(50.0, 10