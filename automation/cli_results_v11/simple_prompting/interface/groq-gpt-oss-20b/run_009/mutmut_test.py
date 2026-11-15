import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_default_initialization(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100), 23.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(120), 0.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(80), 10.0)

    def test_custom_initialization(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.calculate_tax(200), 20.0)
        self.assertAlmostEqual(calc.calculate_shipping(60), 0.0)
        self.assertAlmostEqual(calc.calculate_shipping(40), 5.0)

    def test_add_item_basic(self):
        self.calc.add_item('apple', 2.5, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.5)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertIn('apple', self.calc.list_items())

    def test_add_item_default_quantity(self):
        self.calc.add_item('banana', 1.0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('orange', -1.0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('orange', 1.0, -2)

    def test_remove_item(self):
        self.calc.add_item('pear', 3.0, 2)
        self.calc.remove_item('pear')
        self.assertEqual(self.calc.total_items(), 0)
        self.assertNotIn('pear', self.calc.list_items())

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('item1', 10.0, 1)
        self.calc.add_item('item2', 5.0, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 20.0)

    def test_apply_discount_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -5.0)

    def test_calculate_shipping_free(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_nonfree(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(90.0), 10.0)

    def test_calculate_tax_basic(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200.0), 46.0)

    def test_calculate_tax_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-5.0)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_multiple(self):
        self.calc.add_item('a', 1.0, 2)
        self.calc.add_item('b', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('item', 1.0)
        self.assertFalse(self.calc.is_empty())
if __name__ == '__main__':
    unittest.main()