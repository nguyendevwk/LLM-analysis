import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_parameters(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_init_custom_parameters(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_out_of_range_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_out_of_range_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_basic(self):
        self.calc.add_item('Apple', 1.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertIn('Apple', self.calc.list_items())

    def test_add_item_default_quantity(self):
        self.calc.add_item('Banana', 0.5)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_multiple_quantities(self):
        self.calc.add_item('Orange', 1.0, quantity=3)
        self.assertEqual(self.calc.total_items(), 3)

    def test_add_item_merge_same_name_price(self):
        self.calc.add_item('Pear', 1.0)
        self.calc.add_item('Pear', 1.0, quantity=2)
        self.assertEqual(self.calc.total_items(), 3)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item('Pear', 1.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', 1.5)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.5)

    def test_add_item_name_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.5)

    def test_add_item_price_non_positive(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', -2)

    def test_add_item_price_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', '1.5')

    def test_add_item_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.5, quantity=0)

    def test_add_item_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.5, quantity=-3)

    def test_add_item_quantity_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.5, quantity=1.5)

    def test_add_item_name_whitespace(self):
        self.calc.add_item(' ', 1.5)
        self.assertIn(' ', self.calc.list_items())

    def test_add_item_price_as_int(self):
        self.calc.add_item('Apple', 5)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_quantity_as_float(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.5, quantity=2.0)

    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 1.5)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_name_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_remove_item_after_clear(self):
        self.calc.add_item('Apple', 1.5)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.remove_item('Apple')

    def test_remove_item_case_sensitivity(self):
        self.calc.add_item('Apple', 1.5)
        with self.assertRaises(ValueError):
            self.calc.remove_item('apple')

    def test_get_subtotal_single_item(self):
        self.calc.add_item('Apple', 2.0, quantity=3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('Apple', 2.0, quantity=3)
        self.calc.add_item('Banana', 1.0, quantity=2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 8.0)

    def test_get_subtotal_after_clear(self):
        self.calc.add_item('Apple', 1.5)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_no_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 0), 100)

    def test_apply_discount_full_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 1), 0)

    def test_apply_discount_partial(self):
        self.assertAlmostEqual(self.calc.apply_discount(200, 0.25), 150)

    def test_apply_discount_subtotal_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10, 0.2)

    def test_apply_discount_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, -0.1)

    def test_apply_discount_discount_over_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, 1.5)

    def test_apply_discount_subtotal_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.2)

    def test_apply_discount_discount_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, '0.2')

    def test_calculate_shipping_free(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(120), 0.0)

    def test_calculate_shipping_paid(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(80), 10.0)

    def test_calculate_shipping_exact_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(100), 0.0)

    def test_calculate_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50')

    def test_calculate_tax_normal(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100), 23.0)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0), 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10)

    def test_calculate_tax_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_no_discount(self):
        self.calc.add_item('Apple', 50)
        self.calc.add_item('Banana', 30)
        expected = 80 + 10 + (80 + 10) * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('Apple', 50)
        self.calc.add_item('Banana', 30)
        expected = 40 + 10 + (40 + 10) * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(discount=0.5), expected)

    def test_calculate_total_full_discount(self):
        self.calc.add_item('Apple', 50)
        self.calc.add_item('Banana', 30)
        expected = 0 + 10 + 10 * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(discount=1), expected)

    def test_calculate_total_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0)
        calc.add_item('Apple', 50)
        calc.add_item('Banana', 30)
        expected = 80 + 10 + 0
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_full_tax_rate(self):
        calc = OrderCalculator(tax_rate=1)
        calc.add_item('Apple', 50)
        calc.add_item('Banana', 30)
        expected = 80 + 10 + 90
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_discount_negative(self):
        self.calc.add_item('Apple', 50)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)

    def test_calculate_total_discount_over_one(self):
        self.calc.add_item('Apple', 50)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.2)

    def test_calculate_total_discount_wrong_type(self):
        self.calc.add_item('Apple', 50)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.2')

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_custom_threshold_and_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        calc.add_item('Apple', 30)
        calc.add_item('Banana', 30)
        expected = 60 + 0 + 60 * 0.23
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_rounding(self):
        self.calc.add_item('Apple', 33.33)
        self.calc.add_item('Banana', 66.67)
        expected = 100 + 0 + 100 * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_total_items_single(self):
        self.calc.add_item('Apple', 1.5, quantity=3)
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_multiple(self):
        self.calc.add_item('Apple', 1.5, quantity=2)
        self.calc.add_item('Banana', 2.0, quantity=3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_clear(self):
        self.calc.add_item('Apple', 1.5)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_empty_order(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_resets_items(self):
        self.calc.add_item('Apple', 1.5)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_clear_order_is_empty(self):
        self.calc.add_item('Apple', 1.5)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_clear_order_total_items(self):
        self.calc.add_item('Apple', 1.5)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_list_items(self):
        self.calc.add_item('Apple', 1.5)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_single(self):
        self.calc.add_item('Apple', 1.5)
        self.assertEqual(self.calc.list_items(), ['Apple'])

    def test_list_items_multiple(self):
        self.calc.add_item('Apple', 1.5)
        self.calc.add_item('Banana', 2.0)
        self.assertCountEqual(self.calc.list_items(), ['Apple', 'Banana'])

    def test_list_items_duplicates(self):
        self.calc.add_item('Apple', 1.5)
        self.calc.add_item('Apple', 1.5)
        self.assertEqual(self.calc.list_items(), ['Apple'])

    def test_list_items_after_clear(self):
        self.calc.add_item('Apple', 1.5)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_order_independent(self):
        self.calc.add_item('Banana', 2.0)
        self.calc.add_item('Apple', 1.5)
        self.assertCountEqual(self.calc.list_items(), ['Apple', 'Banana'])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('Apple', 1.5)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('Apple', 1.5)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_remove_all(self):
        self.calc.add_item('Apple', 1.5)
        self.calc.add_item('Banana', 2.0)
        self.calc.remove_item('Apple')
        self.calc.remove_item('Banana')
        self.assertTrue(self.calc.is_empty())

    def test_misc_add_item_name_whitespace(self):
        self.calc.add_item(' ', 1.5)
        self.assertIn(' ', self.calc.list_items())

    def test_misc_add_item_price_as_int(self):
        self.calc.add_item('Apple', 5)
        self.assertEqual(self.calc.total_items(), 1)

    def test_misc_add_item_quantity_as_float(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.5, quantity=2.0)

    def test_misc_remove_item_case_sensitivity(self):
        self.calc.add_item('Apple', 1.5)
        with self.assertRaises(ValueError):
            self.calc.remove_item('apple')

    def test_misc_calculate_total_with_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0, shipping_cost=10)
        calc.add_item('Apple', 10)
        expected = 10 + 0 + 10 * 0.23
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_misc_calculate_total_with_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0)
        calc.add_item('Apple', 10)
        expected = 10 + 0 + 10 * 0.23
        self.assertAlmostEqual(calc.calculate_total(), expected)
if __name__ == '__main__':
    unittest.main()