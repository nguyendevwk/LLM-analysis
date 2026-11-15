import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)
        self.assertEqual(calc.items, [])

    def test_init_tax_rate_boundary_low(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_boundary_high(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_free_shipping_threshold_boundary_low(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_init_free_shipping_threshold_large(self):
        calc = OrderCalculator(free_shipping_threshold=1000.0)
        self.assertEqual(calc.free_shipping_threshold, 1000.0)

    def test_init_shipping_cost_boundary_low(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_shipping_cost_large(self):
        calc = OrderCalculator(shipping_cost=1000.0)
        self.assertEqual(calc.shipping_cost, 1000.0)

    def test_init_tax_rate_out_of_range_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_out_of_range_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_mixed_valid_invalid(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=0.2, free_shipping_threshold=-10)

    def test_add_item_new_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(len(calc.items), 1)
        item = calc.items[0]
        self.assertEqual(item['name'], 'Apple')
        self.assertEqual(item['price'], 1.0)
        self.assertEqual(item['quantity'], 3)

    def test_add_item_existing_same_name_price_increases_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 5)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.5)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_price_as_int(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 5, 2)
        self.assertEqual(calc.items[0]['price'], 5)

    def test_add_item_price_as_float(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 4.99, 1)
        self.assertEqual(calc.items[0]['price'], 4.99)

    def test_add_item_empty_name_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    def test_add_item_name_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_price_zero_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 0.0)

    def test_add_item_price_negative_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', -2.5)

    def test_add_item_quantity_zero_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, 0)

    def test_add_item_quantity_negative_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, -3)

    def test_add_item_quantity_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, 2.5)

    def test_add_item_price_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', '5.0')

    def test_add_item_same_name_different_price_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item('Book', 10.0)
        with self.assertRaises(ValueError):
            calc.add_item('Book', 12.0)

    def test_add_item_after_removal_behaves_as_new(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.remove_item('Apple')
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 3)

    def test_add_item_multiple_distinct_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 5)
        calc.add_item('Cherry', 2.0, 1)
        self.assertEqual(len(calc.items), 3)
        names = {item['name'] for item in calc.items}
        self.assertEqual(names, {'Apple', 'Banana', 'Cherry'})
        for item in calc.items:
            if item['name'] == 'Apple':
                self.assertEqual(item['quantity'], 2)
            elif item['name'] == 'Banana':
                self.assertEqual(item['quantity'], 5)
            else:
                self.assertEqual(item['quantity'], 1)

    def test_remove_item_existing_single(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        self.assertEqual(calc.items, [])

    def test_remove_item_existing_multiple_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        calc.remove_item('Apple')
        self.assertEqual(calc.items, [])

    def test_remove_item_after_quantity_increase(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 2)
        calc.remove_item('Apple')
        self.assertEqual(calc.items, [])

    def test_remove_item_not_found_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Nonexistent')

    def test_remove_item_name_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_from_empty_order_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Apple')

    def test_remove_item_state_verification(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 4)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'Banana')
        self.assertEqual(calc.items[0]['quantity'], 4)

    def test_remove_item_double_removal_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        with self.assertRaises(ValueError):
            calc.remove_item('Apple')

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 3)
        self.assertEqual(calc.get_subtotal(), 6.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 3)
        calc.add_item('Banana', 0.5, 4)
        self.assertEqual(calc.get_subtotal(), 8.0)

    def test_get_subtotal_int_price_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 5, 2)
        self.assertEqual(calc.get_subtotal(), 10.0)

    def test_get_subtotal_floating_point_precision(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.1, 10)
        self.assertAlmostEqual(calc.get_subtotal(), 1.0)

    def test_get_subtotal_empty_order_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_after_clear_order_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_after_remove_all_items_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_no_side_effects(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 3)
        before = list(calc.items)
        calc.get_subtotal()
        self.assertEqual(calc.items, before)

    def test_apply_discount_typical(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100.0, 0.2)
        self.assertEqual(result, 80.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100.0, 0.0)
        self.assertEqual(result, 100.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100.0, 1.0)
        self.assertEqual(result, 0.0)

    def test_apply_discount_zero_subtotal(self):
        calc = OrderCalculator()
        result = calc.apply_discount(0.0, 0.5)
        self.assertEqual(result, 0.0)

    def test_apply_discount_int_subtotal_float_discount(self):
        calc = OrderCalculator()
        result = calc.apply_discount(50, 0.1)
        self.assertEqual(result, 45.0)

    def test_apply_discount_negative_subtotal_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_discount_out_of_range_low(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_out_of_range_high(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.1)

    def test_apply_discount_subtotal_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_discount_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.1')

    def test_apply_discount_floating_point_edge(self):
        calc = OrderCalculator()
        result = calc.apply_discount(1e-12, 0.5)
        self.assertAlmostEqual(result, 5e-13)

    def test_calculate_shipping_free_when_at_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_free_when_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_cost_when_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_zero_subtotal_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('100')

    def test_calculate_shipping_int_vs_float_input(self):
        calc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(calc.calculate_shipping(50), 0.0)
        self.assertEqual(calc.calculate_shipping(49), 5.0)

    def test_calculate_shipping_modified_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=7.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)
        self.assertEqual(calc.calculate_shipping(49.9), 7.0)

    def test_calculate_shipping_modified_shipping_cost(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(90.0), 5.0)

    def test_calculate_shipping_no_side_effects(self):
        calc = OrderCalculator()
        before = (calc.tax_rate, calc.free_shipping_threshold, calc.shipping_cost, list(calc.items))
        calc.calculate_shipping(50.0)
        after = (calc.tax_rate, calc.free_shipping_threshold, calc.shipping_cost, list(calc.items))
        self.assertEqual(before, after)

    def test_calculate_tax_default_rate(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(50.0), 11.5)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_int_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(100), 23.0)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('50')

    def test_calculate_tax_custom_rate(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertEqual(calc.calculate_tax(100.0), 5.0)

    def test_calculate_tax_floating_point_edge(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(1e-09), 2.3e-10)

    def test_calculate_tax_large_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(1000000.0), 230000.0)

    def test_calculate_tax_no_side_effects(self):
        calc = OrderCalculator()
        before = (calc.tax_rate, calc.free_shipping_threshold, calc.shipping_cost, list(calc.items))
        calc.calculate_tax(50.0)
        after = (calc.tax_rate, calc.free_shipping_threshold, calc.shipping_cost, list(calc.items))
        self.assertEqual(before, after)

    def test_calculate_total_normal_order(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 3)
        total = calc.calculate_total(discount=0.1)
        expected = 3.15 + 10.0 + (3.15 + 10.0) * 0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping_after_discount(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        calc.add_item('Item', 30.0, 2)
        total = calc.calculate_total(discount=0.0)
        expected = 60.0 + 0.0 + 60.0 * 0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_default_discount(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10.0, 1)
        total_default = calc.calculate_total()
        total_explicit = calc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total_default, total_explicit)

    def test_calculate_total_full_discount(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=5.0)
        calc.add_item('Apple', 10.0, 1)
        total = calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 0.0)

    def test_calculate_total_empty_order_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_negative_discount_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.1)

    def test_calculate_total_discount_over_one_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.2)

    def test_calculate_total_discount_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='0.1')

    def test_calculate_total_after_clear_order_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10.0, 1)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_zero_subtotal_after_full_discount(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Apple', 10.0, 1)
        total = calc.calculate_total(discount=1.0)
        expected = 0.0 + 10.0 + (0.0 + 10.0) * 0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_no_side_effects(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10.0, 1)
        before_items = list(calc.items)
        calc.calculate_total()
        self.assertEqual(calc.items, before_items)

    def test_calculate_total_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('Expensive', 1000000.0, 2)
        total = calc.calculate_total(discount=0.1)
        expected = 1800000.0 + 1800000.0 * 0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_floating_point_precision(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.1, 1)
        calc.add_item('Banana', 0.2, 1)
        total = calc.calculate_total(discount=0.05)
        expected = 0.285 + 10.0 + (0.285 + 10.0) * 0.23
        self.assertAlmostEqual(total, expected)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 5)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_add_same_name_multiple_times(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_remove_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 4)
        calc.add_item('Banana', 2.0, 3)
        calc.remove_item('Apple')
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_after_clear_order(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 5)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_return_type_int(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 5)
        self.assertIsInstance(calc.total_items(), int)

    def test_total_items_large_quantities(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 10 ** 6)
        self.assertEqual(calc.total_items(), 10 ** 6)

    def test_clear_order_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_clear_order_is_empty_true(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_get_subtotal_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_clear_order_total_items_zero(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_list_items_empty(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_clear_order_attributes_unchanged(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=7.0)
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 7.0)

    def test_clear_order_idempotent(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_one_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_two_distinct_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 1)
        result = calc.list_items()
        self.assertCountEqual(result, ['Apple', 'Banana'])

    def test_list_items_duplicate_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_after_add_remove_add(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        self.assertEqual(calc.list_items(), [])
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_after_clear_order(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_element_type_strings(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 1)
        for name in calc.list_items():
            self.assertIsInstance(name, str)

    def test_list_items_no_side_effects(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        before = list(calc.items)
        calc.list_items()
        self.assertEqual(calc.items, before)

    def test_is_empty_true_initially(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_after_add_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_true_after_remove_last_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_is_empty_true_after_clear_order(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_return_type_bool(self):
        calc = OrderCalculator()
        self.assertIsInstance(calc.is_empty(), bool)

    def test_is_empty_no_side_effects(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        before = list(calc.items)
        calc.is_empty()
        self.assertEqual(calc.items, before)