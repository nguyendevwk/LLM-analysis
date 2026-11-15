import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_item_valid(self):
        self.calc.add_item('apple', 1.5, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.5)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertIn('apple', self.calc.list_items())

    def test_add_item_invalid_types(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.5, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('banana', '2.0', 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('banana', 2.0, '1')

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('orange', -1.0, 1)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('orange', 1.0, -2)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('orange', 1.0, 0)

    def test_add_item_duplicate_name(self):
        self.calc.add_item('apple', 1.0, 2)
        self.calc.add_item('apple', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5.0)

    def test_remove_item_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal(self):
        self.calc.add_item('apple', 2.0, 3)
        self.calc.add_item('banana', 1.5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0 * 3 + 1.5 * 2)

    def test_total_items(self):
        self.calc.add_item('apple', 1.0, 2)
        self.calc.add_item('banana', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_list_items(self):
        self.calc.add_item('apple', 1.0, 1)
        self.calc.add_item('banana', 1.0, 1)
        self.assertCountEqual(self.calc.list_items(), ['apple', 'banana'])

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('apple', 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -5.0)

    def test_apply_discount_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '10')

    def test_calculate_shipping_above_threshold(self):
        discounted_subtotal = 120.0
        self.assertAlmostEqual(self.calc.calculate_shipping(discounted_subtotal), 0.0)

    def test_calculate_shipping_below_threshold(self):
        discounted_subtotal = 80.0
        self.assertAlmostEqual(self.calc.calculate_shipping(discounted_subtotal), 10.0)

    def test_calculate_shipping_negative(self):
        discounted_subtotal = -10.0
        self.assertAlmostEqual(self.calc.calculate_shipping(discounted_subtotal), 10.0)

    def test_calculate_tax_valid(self):
        amount = 50.0
        self.assertAlmostEqual(self.calc.calculate_tax(amount), 11.5)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('50')

    def test_calculate_total_no_discount(self):
        self.calc.add_item('apple', 20.0, 2)
        total = self.calc.calculate_total()
        expected_subtotal = 40.0
        expected_shipping = 10.0
        expected_tax = (expected_subtotal + expected_shipping) * 0.23
        expected_total = expected_subtotal + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-5.0)

    def test_constructor_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item('apple', 20.0, 2)
        total = calc.calculate_total()
        expected_subtotal = 40.0
        expected_shipping = 5.0
        expected_tax = (expected_subtotal + expected_shipping) * 0.1
        expected_total = expected_subtotal + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_constructor_invalid_types(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_constructor_negative_values(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-100)
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-10)
if __name__ == '__main__':
    unittest.main()