import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_and_remove_item(self):
        self.calc.add_item('apple', 1.0, 2)
        self.calc.add_item('banana', 0.5)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertIn('apple', self.calc.list_items())
        self.assertIn('banana', self.calc.list_items())
        self.calc.remove_item('apple')
        self.assertNotIn('apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_invalid_types(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)
        with self.assertRaises(TypeError):
            self.calc.add_item('orange', '1.0')
        with self.assertRaises(TypeError):
            self.calc.add_item('orange', 1.0, '2')

    def test_get_subtotal(self):
        self.calc.add_item('item1', 10.0, 2)
        self.calc.add_item('item2', 5.0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 25.0)

    def test_calculate_shipping(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(120.0), 0.0)
        self.assertAlmostEqual(calc.calculate_shipping(100.0), 0.0)
        self.assertAlmostEqual(calc.calculate_shipping(99.99), 10.0)

    def test_calculate_tax(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_total_items_and_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('item', 1.0)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    def test_calculate_total_with_zero_tax_and_shipping(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        calc.add_item('item', 10.0)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 10.0)

    def test_calculate_total_with_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='10')

    def test_list_items_returns_strings(self):
        self.calc.add_item('apple', 1.0)
        self.calc.add_item('banana', 2.0)
        items = self.calc.list_items()
        self.assertIsInstance(items, list)
        self.assertTrue(all((isinstance(i, str) for i in items)))
        self.assertEqual(set(items), {'apple', 'banana'})

    def test_calculate_shipping_with_negative_amount(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(-50.0), 10.0)
if __name__ == '__main__':
    unittest.main()