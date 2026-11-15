import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default(self):
        self.assertTrue(self.calc.is_empty())

    def test_init_invalid_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_invalid_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_init_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_success(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertIn('Apple', self.calc.list_items())
        self.assertFalse(self.calc.is_empty())

    def test_add_item_merge_quantity(self):
        self.calc.add_item('Banana', 0.5, 3)
        self.calc.add_item('Banana', 0.5, 2)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertEqual(len(self.calc.list_items()), 1)

    def test_add_item_duplicate_name_different_price(self):
        self.calc.add_item('Orange', 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', 1.5, 1)

    def test_add_item_invalid_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_invalid_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Grapes', 0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Grapes', -1, 1)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Peach', 1.0, 0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Peach', 1.0, -2)

    def test_add_item_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('Mango', '1.0', 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('Mango', 1.0, '2')

    def test_remove_item_success(self):
        self.calc.add_item('Kiwi', 2.0, 1)
        self.calc.remove_item('Kiwi')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_not_found(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal(self):
        self.calc.add_item('Item1', 10.0, 2)
        self.calc.add_item('Item2', 5.0, 3)
        subtotal = 10.0 * 2 + 5.0 * 3
        self.assertAlmostEqual(self.calc.get_subtotal(), subtotal)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount(self):
        subtotal = 100.0
        discount = 0.2
        discounted = 80.0
        self.assertAlmostEqual(self.calc.apply_discount(subtotal, discount), discounted)

    def test_apply_discount_invalid_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10, 0.1)

    def test_apply_discount_invalid_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, 1.1)

    def test_apply_discount_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, '0.1')

    def test_calculate_shipping_free(self):
        discounted_subtotal = 120.0
        self.assertAlmostEqual(self.calc.calculate_shipping(discounted_subtotal), 0.0)

    def test_calculate_shipping_paid(self):
        discounted_subtotal = 50.0
        self.assertAlmostEqual(self.calc.calculate_shipping(discounted_subtotal), self.calc.shipping_cost)

    def test_calculate_shipping_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50')

    def test_calculate_tax(self):
        amount = 100.0
        tax = amount * self.calc.tax_rate
        self.assertAlmostEqual(self.calc.calculate_tax(amount), tax)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5)

    def test_calculate_tax_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total(self):
        self.calc.add_item('A', 50.0, 1)
        self.calc.add_item('B', 30.0, 1)
        discount = 0.5
        subtotal = 80.0
        discounted_subtotal = subtotal * (1 - discount)
        shipping = self.calc.shipping_cost if discounted_subtotal < self.calc.free_shipping_threshold else 0.0
        tax = (discounted_subtotal + shipping) * self.calc.tax_rate
        expected_total = discounted_subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(discount), expected_total)

    def test_calculate_total_empty(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(0.1)

    def test_calculate_total_invalid_discount(self):
        self.calc.add_item('C', 20.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.1)

    def test_calculate_total_type_error(self):
        self.calc.add_item('C', 20.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.1')

    def test_total_items(self):
        self.calc.add_item('X', 1.0, 4)
        self.calc.add_item('Y', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 7)

    def test_clear_order(self):
        self.calc.add_item('Z', 5.0, 2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(len(self.calc.list_items()), 0)

    def test_list_items(self):
        self.calc.add_item('P', 1.0, 1)
        self.calc.add_item('Q', 2.0, 1)
        self.calc.add_item('P', 1.0, 2)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['P', 'Q'])
        self.assertEqual(len(items), 2)

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('R', 3.0, 1)
        self.assertFalse(self.calc.is_empty())
        self.calc.remove_item('R')
        self.assertTrue(self.calc.is_empty())


if __name__ == '__main__':
    unittest.main()