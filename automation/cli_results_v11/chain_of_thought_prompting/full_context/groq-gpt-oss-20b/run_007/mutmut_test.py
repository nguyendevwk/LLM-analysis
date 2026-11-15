import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_tax_rate_out_of_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_negative_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_normal(self):
        self.calc.add_item('Apple', 2.5, 3)
        self.assertIn({'name': 'Apple', 'price': 2.5, 'quantity': 3}, self.calc.items)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Banana', 1.0)
        self.assertIn({'name': 'Banana', 'price': 1.0, 'quantity': 1}, self.calc.items)

    def test_add_item_increment_existing(self):
        self.calc.add_item('Apple', 2.5, 3)
        self.calc.add_item('Apple', 2.5, 2)
        self.assertIn({'name': 'Apple', 'price': 2.5, 'quantity': 5}, self.calc.items)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item('Apple', 2.5)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 3.0)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', -1.0)

    def test_add_item_zero_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', 0.0)

    def test_add_item_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', 1.0, 0)

    def test_add_item_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_non_numeric_price(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Orange', '1.0')

    def test_add_item_non_int_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Orange', 1.0, 1.5)

    def test_add_item_large_quantity(self):
        self.calc.add_item('Grapes', 0.5, 10 ** 6)
        self.assertIn({'name': 'Grapes', 'price': 0.5, 'quantity': 10 ** 6}, self.calc.items)

    def test_add_item_price_as_int(self):
        self.calc.add_item('Pear', 3)
        self.assertIn({'name': 'Pear', 'price': 3, 'quantity': 1}, self.calc.items)

    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 2.5)
        self.calc.remove_item('Apple')
        self.assertNotIn({'name': 'Apple', 'price': 2.5, 'quantity': 1}, self.calc.items)

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Mango')

    def test_remove_item_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_remove_item_multiple_same_name(self):
        self.calc.add_item('Apple', 2.5, 2)
        self.calc.add_item('Apple', 2.5, 3)
        self.calc.remove_item('Apple')
        self.assertEqual(len(self.calc.items), 0)

    def test_remove_item_from_empty(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Apple')

    def test_get_subtotal_normal(self):
        self.calc.add_item('Apple', 2.0, 2)
        self.calc.add_item('Banana', 1.5, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 8.5)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_no_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(8.5, 0.0), 8.5)

    def test_apply_discount_partial(self):
        self.assertAlmostEqual(self.calc.apply_discount(8.5, 0.5), 4.25)

    def test_apply_discount_full(self):
        self.assertAlmostEqual(self.calc.apply_discount(8.5, 1.0), 0.0)

    def test_apply_discount_discount_gt_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(8.5, 1.2)

    def test_apply_discount_discount_lt_zero(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(8.5, -0.1)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-5.0, 0.2)

    def test_apply_discount_non_numeric_subtotal(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('8.5', 0.2)

    def test_apply_discount_non_numeric_discount(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(8.5, '0.2')

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(90.0), 10.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        self.assertEqual(self.calc.calculate_shipping(-5.0), 10.0)

    def test_calculate_shipping_non_numeric_input(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('90.0')

    def test_calculate_tax_normal(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_tax_non_numeric_amount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100.0')

    def test_calculate_total_no_discount_free_shipping(self):
        self.calc.add_item('Apple', 60.0, 2)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 147.6)

    def test_calculate_total_partial_discount_shipping_applies(self):
        self.calc.add_item('Apple', 2.0, 2)
        total = self.calc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 16.236)

    def test_calculate_total_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.2')

    def test_calculate_total_invalid_discount_value(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.5)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_negative_subtotal_monkeypatch(self):
        self.calc.get_subtotal = lambda: -5.0
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_total_items_after_adding(self):
        self.calc.add_item('Apple', 2.0, 2)
        self.calc.add_item('Banana', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_clearing(self):
        self.calc.add_item('Apple', 2.0, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_after_removing_one(self):
        self.calc.add_item('Apple', 2.0, 2)
        self.calc.add_item('Banana', 1.0, 3)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.total_items(), 3)

    def test_clear_order_after_adding(self):
        self.calc.add_item('Apple', 2.0, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.items, [])

    def test_clear_order_when_already_empty(self):
        self.calc.clear_order()
        self.assertEqual(self.calc.items, [])

    def test_clear_order_subsequent_operations(self):
        self.calc.clear_order()
        self.calc.add_item('Apple', 2.0, 2)
        self.assertIn({'name': 'Apple', 'price': 2.0, 'quantity': 2}, self.calc.items)

    def test_list_items_unique_names(self):
        self.calc.add_item('Apple', 2.0, 2)
        self.calc.add_item('Apple', 2.0, 1)
        self.calc.add_item('Banana', 1.0, 3)
        self.assertCountEqual(self.calc.list_items(), ['Apple', 'Banana'])

    def test_list_items_after_removal(self):
        self.calc.add_item('Apple', 2.0, 2)
        self.calc.add_item('Banana', 1.0, 3)
        self.calc.remove_item('Apple')
        self.assertCountEqual(self.calc.list_items(), ['Banana'])

    def test_list_items_after_clear(self):
        self.calc.add_item('Apple', 2.0, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_fresh_instance(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_adding(self):
        self.calc.add_item('Apple', 2.0, 2)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clearing(self):
        self.calc.add_item('Apple', 2.0, 2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_edge_extremely_large_price(self):
        self.calc.add_item('Expensive', 1000000000000.0, 1)
        self.assertIn({'name': 'Expensive', 'price': 1000000000000.0, 'quantity': 1}, self.calc.items)

    def test_edge_extremely_large_quantity(self):
        self.calc.add_item('Bulk', 0.01, int(1000000000.0))
        self.assertIn({'name': 'Bulk', 'price': 0.01, 'quantity': int(1000000000.0)}, self.calc.items)

    def test_custom_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 5.0)

    def test_custom_free_shipping_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_custom_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=20)
        self.assertEqual(calc.calculate_shipping(90.0), 20)

    def test_multiple_items_same_name_same_price(self):
        self.calc.add_item('Apple', 2.0, 2)
        self.calc.add_item('Apple', 2.0, 3)
        self.assertIn({'name': 'Apple', 'price': 2.0, 'quantity': 5}, self.calc.items)

    def test_multiple_items_same_name_different_price(self):
        self.calc.add_item('Apple', 2.0, 2)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 3.0, 1)

    def test_remove_item_when_multiple_entries_exist(self):
        self.calc.add_item('Apple', 2.0, 2)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 3.0, 1)
        self.calc.remove_item('Apple')
        self.assertEqual(len(self.calc.items), 0)

    def test_calculate_total_with_zero_items_non_zero_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=0.2)

    def test_calculate_shipping_negative_subtotal_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0)
        self.assertEqual(calc.calculate_shipping(-5.0), 10.0)

    def test_calculate_tax_non_float_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100), 23.0)

    def test_apply_discount_integer_subtotal(self):
        self.assertAlmostEqual(self.calc.apply_discount(10, 0.2), 8.0)

    def test_add_item_price_as_string(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Orange', '3.5')

    def test_add_item_quantity_as_string(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Orange', 1.0, '5')

    def test_remove_item_case_sensitivity(self):
        self.calc.add_item('Apple', 2.0, 2)
        with self.assertRaises(ValueError):
            self.calc.remove_item('apple')

    def test_list_items_order_independence(self):
        self.calc.add_item('Banana', 1.0, 1)
        self.calc.add_item('Apple', 2.0, 1)
        self.calc.add_item('Cherry', 3.0, 1)
        self.assertCountEqual(self.calc.list_items(), ['Banana', 'Apple', 'Cherry'])

    def test_total_items_after_multiple_removals(self):
        self.calc.add_item('Apple', 2.0, 3)
        self.calc.add_item('Banana', 1.0, 2)
        self.calc.remove_item('Apple')
        self.calc.remove_item('Banana')
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_resets_internal_list_reference(self):
        old_id = id(self.calc.items)
        self.calc.clear_order()
        self.assertNotEqual(id(self.calc.items), old_id)

    def test_constructor_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 0.0)

    def test_constructor_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 100.0)

    def test_constructor_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.calculate_shipping(10.0), 0.0)

    def test_constructor_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(90.0), 0.0)

    def test_add_item_extremely_small_price(self):
        self.calc.add_item('Tiny', 1e-09, 1)
        self.assertIn({'name': 'Tiny', 'price': 1e-09, 'quantity': 1}, self.calc.items)

    def test_add_item_smallest_valid_quantity(self):
        self.calc.add_item('Small', 1.0, 1)
        self.assertIn({'name': 'Small', 'price': 1.0, 'quantity': 1}, self.calc.items)

    def test_calculate_shipping_at_threshold_exact(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_just_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(99.99), 10.0)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_amount_equal_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_shipping_never_negative(self):
        self.assertGreaterEqual(self.calc.calculate_shipping(90.0), 0.0)

    def test_add_item_name_whitespace(self):
        self.calc.add_item('  ', 1.0, 1)
        self.assertIn({'name': '  ', 'price': 1.0, 'quantity': 1}, self.calc.items)

    def test_add_item_unicode_name(self):
        self.calc.add_item('🍎', 2.0, 1)
        self.assertIn({'name': '🍎', 'price': 2.0, 'quantity': 1}, self.calc.items)

    def test_remove_item_unicode_name(self):
        self.calc.add_item('🍎', 2.0, 1)
        self.calc.remove_item('🍎')
        self.assertNotIn({'name': '🍎', 'price': 2.0, 'quantity': 1}, self.calc.items)

    def test_list_items_after_adding_unicode_names(self):
        self.calc.add_item('🍎', 2.0, 1)
        self.calc.add_item('🍌', 1.0, 2)
        self.assertCountEqual(self.calc.list_items(), ['🍎', '🍌'])
if __name__ == '__main__':
    unittest.main()