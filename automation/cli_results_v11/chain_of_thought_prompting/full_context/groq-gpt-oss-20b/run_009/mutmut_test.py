import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default_values(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.5, free_shipping_threshold=200, shipping_cost=20)
        self.assertEqual(calc.tax_rate, 0.5)
        self.assertEqual(calc.free_shipping_threshold, 200)
        self.assertEqual(calc.shipping_cost, 20)

    def test_init_tax_rate_boundary_low(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_boundary_high(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_free_shipping_threshold_boundary(self):
        calc = OrderCalculator(free_shipping_threshold=0)
        self.assertEqual(calc.free_shipping_threshold, 0)

    def test_init_shipping_cost_boundary(self):
        calc = OrderCalculator(shipping_cost=0)
        self.assertEqual(calc.shipping_cost, 0)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_free_shipping_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_tax_rate_value_error_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_value_error_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_free_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-3)

    def test_add_item_basic(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 1)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'Apple')
        self.assertEqual(calc.items[0]['price'], 2.0)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 1.5)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_multiple_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Orange', 1.0, 3)
        self.assertEqual(calc.items[0]['quantity'], 3)

    def test_add_item_merge_same_name_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 1)
        calc.add_item('Apple', 2.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 3)

    def test_add_item_same_name_diff_price_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 3.0, 1)

    def test_add_item_empty_name_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0, 1)

    def test_add_item_negative_quantity_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, 0)

    def test_add_item_negative_price_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', -1.0, 1)

    def test_add_item_name_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_add_item_price_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', '1.0', 1)

    def test_add_item_quantity_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, '2')

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 1)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 0)

    def test_remove_item_multiple_instances(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 1)
        calc.add_item('Apple', 2.0, 2)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 0)

    def test_remove_item_nonexistent_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Pear')

    def test_remove_item_name_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 3)
        calc.add_item('Banana', 1.5, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 9.0)

    def test_get_subtotal_empty_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_basic(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100, 0.2), 80.0)

    def test_apply_discount_zero_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100, 1.0), 0.0)

    def test_apply_discount_negative_subtotal_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10, 0.2)

    def test_apply_discount_discount_out_of_range_low_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100, -0.1)

    def test_apply_discount_discount_out_of_range_high_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100, 1.5)

    def test_apply_discount_subtotal_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.2)

    def test_apply_discount_discount_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100, '0.2')

    def test_calculate_shipping_free(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(120), 0.0)

    def test_calculate_shipping_standard(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(80), 10.0)

    def test_calculate_shipping_exact_threshold(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(100), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(-5), 10.0)

    def test_calculate_shipping_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('80')

    def test_calculate_tax_basic(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100), 23.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0), 0.0)

    def test_calculate_tax_negative_amount_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-10)

    def test_calculate_tax_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_calculate_total_no_discount_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 50)
        self.assertAlmostEqual(calc.calculate_total(), 123.0)

    def test_calculate_total_with_discount(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 50)
        self.assertAlmostEqual(calc.calculate_total(discount=0.5), 73.8)

    def test_calculate_total_full_discount(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 50)
        self.assertAlmostEqual(calc.calculate_total(discount=1.0), 12.3)

    def test_calculate_total_discount_boundary(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 50)
        self.assertAlmostEqual(calc.calculate_total(discount=0.5), 73.8)

    def test_calculate_total_discount_edge_threshold(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 50)
        self.assertAlmostEqual(calc.calculate_total(discount=0.5), 73.8)

    def test_calculate_total_discount_invalid_type(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 50)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='0.2')

    def test_calculate_total_discount_out_of_range_low_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 50)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.1)

    def test_calculate_total_discount_out_of_range_high_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 50)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.5)

    def test_calculate_total_empty_order_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 3)
        calc.add_item('Banana', 1.5, 2)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_merge(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 3)
        calc.add_item('Apple', 2.0, 2)
        self.assertEqual(calc.total_items(), 5)

    def test_clear_order(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 1)
        calc.clear_order()
        self.assertEqual(calc.items, [])
        self.assertTrue(calc.is_empty())

    def test_clear_order_then_add(self):
        calc = OrderCalculator()
        calc.clear_order()
        calc.add_item('Pear', 3.0, 1)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'Pear')

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_unique_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 1)
        calc.add_item('Banana', 1.5, 1)
        calc.add_item('Apple', 2.0, 2)
        self.assertCountEqual(calc.list_items(), ['Apple', 'Banana'])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_is_empty_initial(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_add(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_add_item_edge_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Gadget', 10.0, 10 ** 6)
        self.assertEqual(calc.items[0]['quantity'], 10 ** 6)

    def test_add_item_edge_large_price(self):
        calc = OrderCalculator()
        calc.add_item('Gadget', 10 ** 9, 1)
        self.assertEqual(calc.items[0]['price'], 10 ** 9)

    def test_apply_discount_edge_high_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(1000, 0.999999), 0.001)

    def test_apply_discount_edge_low_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(1000, 1e-06), 999.999)

    def test_calculate_shipping_edge_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0)
        self.assertAlmostEqual(calc.calculate_shipping(10), 0.0)

    def test_calculate_shipping_edge_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0)
        self.assertAlmostEqual(calc.calculate_shipping(80), 0.0)

    def test_calculate_total_edge_tax_rate_zero_shipping_zero(self):
        calc = OrderCalculator(tax_rate=0.0, shipping_cost=0)
        calc.add_item('Apple', 2.0, 50)
        self.assertAlmostEqual(calc.calculate_total(), 100.0)

    def test_calculate_total_edge_tax_rate_one_shipping_zero(self):
        calc = OrderCalculator(tax_rate=1.0, shipping_cost=0)
        calc.add_item('Apple', 2.0, 50)
        self.assertAlmostEqual(calc.calculate_total(), 200.0)

    def test_calculate_total_edge_discount_one_threshold_zero_shipping_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0, shipping_cost=0)
        calc.add_item('Apple', 2.0, 50)
        self.assertAlmostEqual(calc.calculate_total(discount=1.0), 0.0)

    def test_remove_item_edge_multiple_removals(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 3)
        calc.add_item('Apple', 2.0, 2)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 0)

    def test_remove_item_edge_case_sensitivity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 1)
        with self.assertRaises(ValueError):
            calc.remove_item('apple')

    def test_add_item_edge_whitespace_name(self):
        calc = OrderCalculator()
        calc.add_item('  ', 1.0, 1)
        self.assertEqual(calc.items[0]['name'], '  ')

    def test_add_item_edge_special_characters(self):
        calc = OrderCalculator()
        calc.add_item('Café-123!', 5.0, 1)
        self.assertEqual(calc.items[0]['name'], 'Café-123!')

    def test_add_item_edge_price_integer(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 5, 1)
        self.assertEqual(calc.items[0]['price'], 5)

    def test_add_item_edge_quantity_float(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, 2.0)

    def test_calculate_tax_edge_amount_integer(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100), 23.0)

    def test_calculate_tax_edge_amount_float(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_shipping_edge_float_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(99.999), 10.0)

    def test_calculate_shipping_edge_int_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(100), 0.0)

    def test_calculate_total_edge_multiple_items_different_price_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 3.0, 1)

    def test_calculate_total_edge_discount_exact_zero(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 50)
        self.assertAlmostEqual(calc.calculate_total(discount=0.0), 123.0)

    def test_calculate_total_edge_discount_exact_one(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 50)
        self.assertAlmostEqual(calc.calculate_total(discount=1.0), 12.3)

    def test_calculate_total_edge_free_shipping_threshold_exact(self):
        calc = OrderCalculator(free_shipping_threshold=100)
        calc.add_item('Apple', 2.0, 50)
        self.assertAlmostEqual(calc.calculate_total(), 123.0)

    def test_calculate_total_edge_free_shipping_threshold_above(self):
        calc = OrderCalculator(free_shipping_threshold=99)
        calc.add_item('Apple', 2.0, 50)
        self.assertAlmostEqual(calc.calculate_total(), 123.0)

    def test_calculate_total_edge_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0)
        calc.add_item('Apple', 2.0, 50)
        self.assertAlmostEqual(calc.calculate_total(), 123.0)

    def test_calculate_total_edge_large_subtotal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10 ** 6, 10 ** 3)
        self.assertAlmostEqual(calc.calculate_total(), 10 ** 9 * 1.23)

    def test_calculate_total_edge_combination_large_values(self):
        calc = OrderCalculator(tax_rate=0.999999, free_shipping_threshold=10 ** 9, shipping_cost=10 ** 6)
        calc.add_item('Apple', 10 ** 6, 10 ** 3)
        self.assertAlmostEqual(calc.calculate_total(), 10 ** 9 * 1.999999)

    def test_total_items_edge_many_items(self):
        calc = OrderCalculator()
        for _ in range(1000):
            calc.add_item(f'Item{_}', 1.0, 1)
        self.assertEqual(calc.total_items(), 1000)

    def test_list_items_edge_many_items_duplicates(self):
        calc = OrderCalculator()
        for i in range(500):
            calc.add_item(f'Item{i}', 1.0, 1)
            calc.add_item(f'Item{i}', 1.0, 1)
        self.assertEqual(len(calc.list_items()), 500)

    def test_is_empty_edge_many_operations(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        calc.add_item('Apple', 1.0, 1)
        self.assertFalse(calc.is_empty())
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_add_item_edge_leading_trailing_spaces(self):
        calc = OrderCalculator()
        calc.add_item('  Apple  ', 1.0, 1)
        self.assertEqual(calc.items[0]['name'], '  Apple  ')

    def test_add_item_edge_case_sensitivity(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0, 1)
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(len(calc.items), 2)

    def test_remove_item_edge_case_sensitivity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            calc.remove_item('apple')

    def test_calculate_total_edge_discount_before_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=100, shipping_cost=10)
        calc.add_item('Apple', 200, 1)
        self.assertAlmostEqual(calc.calculate_total(discount=0.5), 123.0)

    def test_calculate_total_edge_shipping_before_tax(self):
        calc = OrderCalculator(free_shipping_threshold=100, shipping_cost=10)
        calc.add_item('Apple', 200, 1)
        self.assertAlmostEqual(calc.calculate_total(discount=0.5), 123.0)
if __name__ == '__main__':
    unittest.main()