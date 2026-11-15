import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_default_initialization(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_custom_initialization(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 10.0)

    def test_add_item_and_subtotal(self):
        self.calc.add_item('apple', 2.5, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.5)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertIn('apple', self.calc.list_items())

    def test_add_item_default_quantity(self):
        self.calc.add_item('orange', 1.5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.5)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_multiple_items(self):
        self.calc.add_item('apple', 2.5, 3)
        self.calc.add_item('banana', 1.0, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 9.5)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertCountEqual(self.calc.list_items(), ['apple', 'banana'])

    def test_add_item_invalid_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('pear', -1.0, 1)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('pear', 1.0, 0)
        with self.assertRaises(ValueError):
            self.calc.add_item('pear', 1.0, -2)

    def test_add_item_invalid_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_apply_discount_excess(self):
        self.calc.add_item('apple', 2.5, 3)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(self.calc.get_subtotal(), 10.0)

    def test_calculate_shipping_below_threshold(self):
        self.calc.add_item('apple', 2.5, 3)
        shipping = self.calc.calculate_shipping(self.calc.get_subtotal())
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_at_threshold(self):
        self.calc.add_item('apple', 50.0, 2)
        shipping = self.calc.calculate_shipping(self.calc.get_subtotal())
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.calc.add_item('apple', 60.0, 2)
        shipping = self.calc.calculate_shipping(self.calc.get_subtotal())
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_tax(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-1.0)

    def test_total_items(self):
        self.calc.add_item('apple', 2.5, 3)
        self.calc.add_item('banana', 1.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_list_items(self):
        self.calc.add_item('apple', 2.5, 3)
        self.calc.add_item('banana', 1.0, 2)
        items = self.calc.list_items()
        self.assertIn('apple', items)
        self.assertIn('banana', items)
        self.assertEqual(len(items), 2)

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('apple', 2.5, 3)
        self.assertFalse(self.calc.is_empty())
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_invalid_initialization(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-50.0)
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -2.0)

    def test_remove_item_invalid_name(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_add_item_quantity_float(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('pear', 1.0, 1.5)

    def test_add_item_price_float(self):
        self.calc.add_item('pear', 1.5, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.5)
if __name__ == '__main__':
    unittest.main()