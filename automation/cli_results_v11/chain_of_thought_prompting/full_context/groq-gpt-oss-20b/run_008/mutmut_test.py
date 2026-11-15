import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertEqual(self.calc.items, [])

    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_type_error_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_type_error_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_value_error_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_value_error_tax_rate_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_value_error_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_value_error_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_init_integer_tax_rate(self):
        calc = OrderCalculator(tax_rate=1)
        self.assertEqual(calc.tax_rate, 1)

    def test_init_integer_free_shipping_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0)
        self.assertEqual(calc.free_shipping_threshold, 0)

    def test_init_integer_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0)
        self.assertEqual(calc.shipping_cost, 0)

    def test_add_item_new(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 2)

    def test_add_item_same_name_price(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Apple', 1.5, 3)
        self.assertEqual(self.calc.items[0]['quantity'], 5)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item('Apple', 1.5, 2)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.0, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.5, 1)

    def test_add_item_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.5, 1)

    def test_add_item_price_non_positive(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', -1, 1)

    def test_add_item_price_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', '1.5', 1)

    def test_add_item_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.5, 0)

    def test_add_item_quantity_non_int(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.5, 1.5)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Apple', 1.5)
        self.assertEqual(self.calc.items[0]['quantity'], 1)

    def test_add_item_large_quantity(self):
        self.calc.add_item('Apple', 1.5, 10)
        self.assertEqual(self.calc.items[0]['quantity'], 10)

    def test_add_item_multiple_distinct(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertEqual(len(self.calc.items), 2)

    def test_add_item_duplicate_names_same_price(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Apple', 1.5, 3)
        self.assertEqual(len(self.calc.list_items()), 1)

    def test_add_item_duplicate_names_different_price(self):
        self.calc.add_item('Apple', 1.5, 2)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.0, 1)

    def test_add_item_internal_state(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertEqual(self.calc.items[0]['name'], 'Apple')
        self.assertEqual(self.calc.items[0]['price'], 1.5)
        self.assertEqual(self.calc.items[0]['quantity'], 2)
        self.assertEqual(self.calc.items[1]['name'], 'Banana')
        self.assertEqual(self.calc.items[1]['price'], 0.5)
        self.assertEqual(self.calc.items[1]['quantity'], 3)

    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Banana')

    def test_remove_item_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_remove_item_partial(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.calc.remove_item('Apple')
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['name'], 'Banana')

    def test_remove_item_is_empty_after_last(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_is_empty_after_partial(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.calc.remove_item('Apple')
        self.assertFalse(self.calc.is_empty())

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_get_subtotal_single_item(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0 + 1.5)

    def test_get_subtotal_type_float(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertIsInstance(self.calc.get_subtotal(), float)

    def test_apply_discount_valid(self):
        result = self.calc.apply_discount(10.0, 0.2)
        self.assertAlmostEqual(result, 8.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(10.0, 0.0)
        self.assertAlmostEqual(result, 10.0)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(10.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -0.1)

    def test_apply_discount_discount_over_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, 1.1)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-5.0, 0.2)

    def test_apply_discount_non_numeric_subtotal(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('10', 0.2)

    def test_apply_discount_non_numeric_discount(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(10.0, '0.2')

    def test_calculate_shipping_above_threshold(self):
        result = self.calc.calculate_shipping(120.0)
        self.assertAlmostEqual(result, 0.0)

    def test_calculate_shipping_below_threshold(self):
        result = self.calc.calculate_shipping(80.0)
        self.assertAlmostEqual(result, self.calc.shipping_cost)

    def test_calculate_shipping_exact_threshold(self):
        result = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(result, 0.0)

    def test_calculate_shipping_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('80')

    def test_calculate_shipping_negative_value(self):
        result = self.calc.calculate_shipping(-10.0)
        self.assertAlmostEqual(result, self.calc.shipping_cost)

    def test_calculate_tax_positive(self):
        result = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(result, 23.0)

    def test_calculate_tax_zero(self):
        result = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(result, 0.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_empty(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_no_discount(self):
        self.calc.add_item('Apple', 1.5, 2)
        subtotal = self.calc.get_subtotal()
        shipping = self.calc.calculate_shipping(subtotal)
        tax = self.calc.calculate_tax(subtotal + shipping)
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_half_discount(self):
        self.calc.add_item('Apple', 1.5, 2)
        subtotal = self.calc.get_subtotal()
        discounted = self.calc.apply_discount(subtotal, 0.5)
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.5), expected)

    def test_calculate_total_full_discount(self):
        self.calc.add_item('Apple', 1.5, 2)
        subtotal = self.calc.get_subtotal()
        discounted = self.calc.apply_discount(subtotal, 1.0)
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(1.0), expected)

    def test_calculate_total_discount_out_of_range(self):
        self.calc.add_item('Apple', 1.5, 2)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.1)

    def test_calculate_total_non_numeric_discount(self):
        self.calc.add_item('Apple', 1.5, 2)
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.5')

    def test_calculate_total_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Apple', 10.0, 1)
        subtotal = calc.get_subtotal()
        shipping = calc.calculate_shipping(subtotal)
        tax = calc.calculate_tax(subtotal + shipping)
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 10.0, 1)
        subtotal = calc.get_subtotal()
        shipping = calc.calculate_shipping(subtotal)
        tax = calc.calculate_tax(subtotal + shipping)
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item('Apple', 10.0, 1)
        subtotal = calc.get_subtotal()
        shipping = calc.calculate_shipping(subtotal)
        tax = calc.calculate_tax(subtotal + shipping)
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_threshold_above_discounted(self):
        calc = OrderCalculator(free_shipping_threshold=100.0)
        calc.add_item('Apple', 10.0, 1)
        discounted = calc.apply_discount(calc.get_subtotal(), 0.5)
        shipping = calc.calculate_shipping(discounted)
        self.assertAlmostEqual(shipping, calc.shipping_cost)

    def test_calculate_total_threshold_below_discounted(self):
        calc = OrderCalculator(free_shipping_threshold=100.0)
        calc.add_item('Apple', 200.0, 1)
        discounted = calc.apply_discount(calc.get_subtotal(), 0.0)
        shipping = calc.calculate_shipping(discounted)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_total_edge_discount1_threshold0_tax(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=0.0)
        calc.add_item('Apple', 10.0, 1)
        self.assertAlmostEqual(calc.calculate_total(1.0), 0.0)

    def test_calculate_total_edge_discount1_threshold100_tax(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0)
        calc.add_item('Apple', 10.0, 1)
        self.assertAlmostEqual(calc.calculate_total(1.0), 12.3)

    def test_calculate_total_type_float(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertIsInstance(self.calc.calculate_total(), float)

    def test_total_items_no_items(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_multiple(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_type_int(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertIsInstance(self.calc.total_items(), int)

    def test_clear_order_with_items(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_clear_order_already_empty(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_clear_order_is_empty(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items_no_items(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_multiple_distinct(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertCountEqual(self.calc.list_items(), ['Apple', 'Banana'])

    def test_list_items_duplicate_same_price(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Apple', 1.5, 3)
        self.assertCountEqual(self.calc.list_items(), ['Apple'])

    def test_list_items_elements_are_strings(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertTrue(all((isinstance(n, str) for n in self.calc.list_items())))

    def test_is_empty_empty(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_with_items(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
if __name__ == '__main__':
    unittest.main()