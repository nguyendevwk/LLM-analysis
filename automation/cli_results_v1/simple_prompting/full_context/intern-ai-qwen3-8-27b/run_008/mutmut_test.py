import unittest
from order_calculator import OrderCalculator

class OrderCalculatorTests(unittest.TestCase):

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50)
        self.assertEqual(calc.shipping_cost, 5)

    def test_init_accepts_int_values(self):
        calc = OrderCalculator(tax_rate=0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(calc.tax_rate, 0)
        self.assertEqual(calc.free_shipping_threshold, 0)
        self.assertEqual(calc.shipping_cost, 0)

    def test_init_accepts_boundary_tax_rate(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_tax_rate_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate=None)

    def test_init_threshold_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_threshold_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_shipping_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_shipping_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_init_tax_rate_below_zero_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_negative_threshold_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1)

    def test_init_negative_shipping_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_add_item_adds_single_item(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0, 3)
        self.assertEqual(calc.items, [{'name': 'apple', 'price': 2.0, 'quantity': 3}])

    def test_add_item_default_quantity_is_one(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_accepts_int_price(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2, 3)
        self.assertEqual(calc.items[0]['price'], 2)

    def test_add_item_increases_quantity_for_same_name_and_price(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0, 2)
        calc.add_item('apple', 2.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 5)

    def test_add_item_keeps_separate_items_with_different_names(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0)
        calc.add_item('banana', 3.0)
        self.assertEqual(len(calc.items), 2)

    def test_add_item_whitespace_name_is_accepted(self):
        calc = OrderCalculator()
        calc.add_item(' ', 2.0)
        self.assertEqual(calc.items[0]['name'], ' ')

    def test_add_item_same_name_different_price_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0)
        with self.assertRaises(ValueError):
            calc.add_item('apple', 3.0)

    def test_add_item_same_name_different_price_does_not_modify_existing(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('apple', 3.0, 2)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_non_string_name_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 2.0)

    def test_add_item_none_name_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(None, 2.0)

    def test_add_item_non_number_price_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('apple', '2.0')

    def test_add_item_none_price_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('apple', None)

    def test_add_item_float_quantity_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('apple', 2.0, 1.0)

    def test_add_item_string_quantity_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('apple', 2.0, '1')

    def test_add_item_none_quantity_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('apple', 2.0, None)

    def test_add_item_empty_name_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 2.0)

    def test_add_item_zero_price_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('apple', 0)

    def test_add_item_negative_price_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('apple', -2.0)

    def test_add_item_zero_quantity_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('apple', 2.0, 0)

    def test_add_item_negative_quantity_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('apple', 2.0, -1)

    def test_remove_item_removes_existing_item(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0)
        calc.remove_item('apple')
        self.assertEqual(calc.items, [])

    def test_remove_item_leaves_other_items(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0)
        calc.add_item('banana', 3.0)
        calc.remove_item('apple')
        self.assertEqual([item['name'] for item in calc.items], ['banana'])

    def test_remove_item_nonexistent_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('apple')

    def test_remove_item_nonexistent_does_not_modify_items(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0)
        with self.assertRaises(ValueError):
            calc.remove_item('banana')
        self.assertEqual(len(calc.items), 1)

    def test_remove_item_empty_string_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('')

    def test_remove_item_non_string_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_none_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(None)

    def test_get_subtotal_empty_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0, 3)
        self.assertEqual(calc.get_subtotal(), 6.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0, 3)
        calc.add_item('banana', 5.0, 2)
        self.assertEqual(calc.get_subtotal(), 16.0)

    def test_get_subtotal_int_prices(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2, 3)
        self.assertEqual(calc.get_subtotal(), 6)

    def test_apply_discount_typical(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_zero_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_int_inputs(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100, 0), 100)

    def test_apply_discount_string_subtotal_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.2)

    def test_apply_discount_none_subtotal_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(None, 0.2)

    def test_apply_discount_string_discount_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.2')

    def test_apply_discount_none_discount_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, None)

    def test_apply_discount_negative_subtotal_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-1.0, 0.2)

    def test_apply_discount_discount_below_zero_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_above_one_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.1)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_equal_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.01), 0.0)

    def test_calculate_shipping_int_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(99), 10.0)

    def test_calculate_shipping_custom_threshold_and_cost(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(49.99), 5.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)

    def test_calculate_shipping_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(1.0), 0.0)

    def test_calculate_shipping_non_number_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('100')

    def test_calculate_shipping_none_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping(None)

    def test_calculate_tax_typical(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_full_rate(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 100.0)

    def test_calculate_tax_int_amount(self):
        calc = OrderCalculator(tax_rate=0.5)
        self.assertAlmostEqual(calc.calculate_tax(100), 50.0)

    def test_calculate_tax_non_number_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_calculate_tax_none_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax(None)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-1.0)

    def test_calculate_total_empty_order_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_below_threshold_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('apple', 10.0, 2)
        self.assertAlmostEqual(calc.calculate_total(), 36.9)

    def test_calculate_total_above_threshold_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('apple', 150.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 184.5)

    def test_calculate_total_equal_threshold_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('apple', 100.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 123.0)

    def test_calculate_total_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('apple', 10.0, 2)
        calc.add_item('banana', 5.0, 2)
        self.assertAlmostEqual(calc.calculate_total(), 49.2)

    def test_calculate_total_with_discount_below_threshold(self):
        calc = OrderCalculator()
        calc.add_item('apple', 100.0, 1)
        self.assertAlmostEqual(calc.calculate_total(discount=0.5), 73.8)

    def test_calculate_total_with_discount_above_threshold(self):
        calc = OrderCalculator()
        calc.add_item('apple', 300.0, 1)
        self.assertAlmostEqual(calc.calculate_total(discount=0.5), 184.5)

    def test_calculate_total_with_discount_equal_threshold(self):
        calc = OrderCalculator()
        calc.add_item('apple', 200.0, 1)
        self.assertAlmostEqual(calc.calculate_total(discount=0.5), 123.0)

    def test_calculate_total_full_discount(self):
        calc = OrderCalculator()
        calc.add_item('apple', 100.0, 1)
        self.assertAlmostEqual(calc.calculate_total(discount=1.0), 12.3)

    def test_calculate_total_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('apple', 10.0, 2)
        self.assertAlmostEqual(calc.calculate_total(), 30.0)

    def test_calculate_total_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('apple', 10.0, 2)
        self.assertAlmostEqual(calc.calculate_total(), 24.6)

    def test_calculate_total_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item('apple', 10.0, 2)
        self.assertAlmostEqual(calc.calculate_total(), 24.6)

    def test_calculate_total_full_discount_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item('apple', 100.0, 1)
        self.assertAlmostEqual(calc.calculate_total(discount=1.0), 0.0)

    def test_calculate_total_int_discount(self):
        calc = OrderCalculator()
        calc.add_item('apple', 100.0, 1)
        self.assertAlmostEqual(calc.calculate_total(discount=0), 123.0)

    def test_calculate_total_negative_subtotal_raises_value_error(self):
        calc = OrderCalculator()
        calc.items = [{'name': 'bad', 'price': -1.0, 'quantity': 1}]
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_invalid_discount_type_raises_type_error(self):
        calc = OrderCalculator()
        calc.add_item('apple', 10.0)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='0.1')

    def test_calculate_total_none_discount_raises_type_error(self):
        calc = OrderCalculator()
        calc.add_item('apple', 10.0)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount=None)

    def test_calculate_total_discount_below_zero_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item('apple', 10.0)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.1)

    def test_calculate_total_discount_above_one_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item('apple', 10.0)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.1)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0, 3)
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0, 3)
        calc.add_item('banana', 3.0, 2)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_quantity_increase(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0, 2)
        calc.add_item('apple', 2.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_remove(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0, 3)
        calc.add_item('banana', 3.0, 2)
        calc.remove_item('apple')
        self.assertEqual(calc.total_items(), 2)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0, 3)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_removes_all_items(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0)
        calc.add_item('banana', 3.0)
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_clear_order_empty_order(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_clear_order_keeps_configuration(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=5)
        calc.add_item('apple', 2.0)
        calc.clear_order()
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50)
        self.assertEqual(calc.shipping_cost, 5)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_returns_unique_names(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0, 2)
        calc.add_item('banana', 3.0, 1)
        self.assertCountEqual(calc.list_items(), ['apple', 'banana'])

    def test_list_items_no_duplicates_after_quantity_increase(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0, 2)
        calc.add_item('apple', 2.0, 3)
        self.assertEqual(calc.list_items(), ['apple'])

    def test_list_items_after_remove(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0)
        calc.add_item('banana', 3.0)
        calc.remove_item('apple')
        self.assertEqual(calc.list_items(), ['banana'])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_is_empty_new_order(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_add(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_remove_all(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0)
        calc.remove_item('apple')
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
if __name__ == '__main__':
    unittest.main()