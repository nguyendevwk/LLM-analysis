import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_parameters(self):
        self.assertAlmostEqual(self.calc.tax_rate, 0.23, places=6)
        self.assertAlmostEqual(self.calc.free_shipping_threshold, 100.0, places=6)
        self.assertAlmostEqual(self.calc.shipping_cost, 10.0, places=6)
        self.assertTrue(self.calc.is_empty())

    def test_init_custom_parameters(self):
        calc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.tax_rate, 0.15, places=6)
        self.assertAlmostEqual(calc.free_shipping_threshold, 50.0, places=6)
        self.assertAlmostEqual(calc.shipping_cost, 5.0, places=6)

    def test_init_tax_rate_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_free_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_free_shipping_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_basic(self):
        self.calc.add_item('Apple', 2.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertEqual(self.calc.list_items(), ['Apple'])
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.5, places=6)

    def test_add_item_multiple_quantities(self):
        self.calc.add_item('Apple', 2.5, 2)
        self.calc.add_item('Apple', 2.5, 3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.5 * 5, places=6)

    def test_add_item_same_name_same_price(self):
        self.calc.add_item('Apple', 2.5)
        self.calc.add_item('Apple', 2.5)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5.0, places=6)

    def test_add_item_same_name_diff_price(self):
        self.calc.add_item('Apple', 2.5)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 3.0)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', -1.0)

    def test_add_item_zero_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 0.0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.0, -1)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.0, 0)

    def test_add_item_name_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_price_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', '1.0')

    def test_add_item_quantity_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.0, '2')

    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 2.5)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_name_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_remove_item_affects_other_items(self):
        self.calc.add_item('Apple', 2.5)
        self.calc.add_item('Banana', 1.5)
        self.calc.remove_item('Apple')
        self.assertFalse(self.calc.is_empty())
        self.assertIn('Banana', self.calc.list_items())
        self.assertNotIn('Apple', self.calc.list_items())

    def test_get_subtotal_with_items(self):
        self.calc.add_item('Apple', 2.5, 2)
        self.calc.add_item('Banana', 1.5, 3)
        expected = 2.5 * 2 + 1.5 * 3
        self.assertAlmostEqual(self.calc.get_subtotal(), expected, places=6)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_valid(self):
        result = self.calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0, places=6)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(100.0, 0.0)
        self.assertAlmostEqual(result, 100.0, places=6)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(100.0, 1.0)
        self.assertAlmostEqual(result, 0.0, places=6)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.2)

    def test_apply_discount_discount_low(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_high(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.1)

    def test_apply_discount_subtotal_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.2)

    def test_apply_discount_discount_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '0.2')

    def test_calculate_shipping_free(self):
        shipping = self.calc.calculate_shipping(120.0)
        self.assertAlmostEqual(shipping, 0.0, places=6)

    def test_calculate_shipping_paid(self):
        shipping = self.calc.calculate_shipping(80.0)
        self.assertAlmostEqual(shipping, self.calc.shipping_cost, places=6)

    def test_calculate_shipping_exact_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0, places=6)

    def test_calculate_shipping_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('80')

    def test_calculate_tax_valid(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0, places=6)

    def test_calculate_tax_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0, places=6)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_tax_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_no_discount(self):
        self.calc.add_item('Apple', 50.0)
        self.calc.add_item('Banana', 30.0)
        subtotal = 80.0
        shipping = self.calc.shipping_cost
        tax = (subtotal + shipping) * self.calc.tax_rate
        expected = subtotal + shipping + tax
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, expected, places=6)

    def test_calculate_total_full_discount(self):
        self.calc.add_item('Apple', 50.0)
        self.calc.add_item('Banana', 30.0)
        subtotal = 80.0
        discounted = 0.0
        shipping = self.calc.shipping_cost
        tax = shipping * self.calc.tax_rate
        expected = discounted + shipping + tax
        total = self.calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, expected, places=6)

    def test_calculate_total_half_discount(self):
        self.calc.add_item('Apple', 50.0)
        self.calc.add_item('Banana', 30.0)
        subtotal = 80.0
        discounted = subtotal * 0.5
        shipping = self.calc.shipping_cost
        tax = (discounted + shipping) * self.calc.tax_rate
        expected = discounted + shipping + tax
        total = self.calc.calculate_total(discount=0.5)
        self.assertAlmostEqual(total, expected, places=6)

    def test_calculate_total_exact_threshold(self):
        self.calc.add_item('Apple', 200.0)
        subtotal = 200.0
        discounted = subtotal * 0.5
        shipping = 0.0
        tax = discounted * self.calc.tax_rate
        expected = discounted + shipping + tax
        total = self.calc.calculate_total(discount=0.5)
        self.assertAlmostEqual(total, expected, places=6)

    def test_calculate_total_tax_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Apple', 80.0)
        subtotal = 80.0
        shipping = calc.shipping_cost
        tax = 0.0
        expected = subtotal + shipping + tax
        total = calc.calculate_total()
        self.assertAlmostEqual(total, expected, places=6)

    def test_calculate_total_tax_full(self):
        calc = OrderCalculator(tax_rate=1.0)
        calc.add_item('Apple', 80.0)
        subtotal = 80.0
        shipping = calc.shipping_cost
        tax = (subtotal + shipping) * 1.0
        expected = subtotal + shipping + tax
        total = calc.calculate_total()
        self.assertAlmostEqual(total, expected, places=6)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_discount_low(self):
        self.calc.add_item('Apple', 50.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)

    def test_calculate_total_discount_high(self):
        self.calc.add_item('Apple', 50.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.1)

    def test_calculate_total_type_error(self):
        self.calc.add_item('Apple', 50.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.2')

    def test_calculate_total_after_clear_order(self):
        self.calc.add_item('Apple', 50.0)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_total_items_single(self):
        self.calc.add_item('Apple', 1.0)
        self.assertEqual(self.calc.total_items(), 1)

    def test_total_items_multiple_quantities(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.calc.add_item('Banana', 1.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_clear(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_resets_state(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.list_items(), [])

    def test_clear_order_then_add(self):
        self.calc.clear_order()
        self.calc.add_item('Apple', 1.0)
        self.assertEqual(self.calc.total_items(), 1)

    def test_list_items_unique_names(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Apple', 1.0)
        self.assertEqual(len(self.calc.list_items()), 1)

    def test_list_items_multiple_names(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Banana', 1.0)
        self.assertEqual(set(self.calc.list_items()), {'Apple', 'Banana'})

    def test_list_items_after_clear(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('Apple', 1.0)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
if __name__ == '__main__':
    unittest.main()