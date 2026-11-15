import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_valid_custom(self):
        calc = OrderCalculator(tax_rate=0.07, free_shipping_threshold=50, shipping_cost=5.5)
        self.assertEqual(calc.tax_rate, 0.07)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.5)

    def test_init_mixed_int_float(self):
        calc = OrderCalculator(tax_rate=0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_free_shipping_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_tax_rate_negative_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_free_shipping_threshold_negative_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_shipping_cost_negative_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2)

    def test_add_item_new_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(len(calc.items), 1)
        item = calc.items[0]
        self.assertEqual(item['name'], 'Apple')
        self.assertEqual(item['price'], 1.0)
        self.assertEqual(item['quantity'], 2)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.5)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_same_name_price_increases_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 4)

    def test_add_item_same_name_different_price_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 2.0, 1)

    def test_add_item_empty_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    def test_add_item_non_string_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_price_zero_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', 0.0)

    def test_add_item_price_negative_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', -5.0)

    def test_add_item_price_wrong_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', '10')

    def test_add_item_quantity_less_than_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', 1.0, 0)

    def test_add_item_quantity_negative_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', 1.0, -3)

    def test_add_item_quantity_wrong_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', 1.0, 2.5)

    def test_add_item_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        calc.add_item('B', 2.0, 1)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'B')

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        self.assertEqual(calc.items, [])

    def test_remove_item_non_existing_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError) as cm:
            calc.remove_item('Pear')
        self.assertIn('Pear', str(cm.exception))

    def test_remove_item_non_string_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(5)

    def test_remove_one_of_multiple(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 1)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'Banana')

    def test_remove_item_quantity_greater_than_one(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        calc.remove_item('Apple')
        self.assertEqual(calc.items, [])

    def test_remove_then_add_same_name_same_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_get_subtotal_empty_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('A', 2.5, 4)
        self.assertEqual(calc.get_subtotal(), 10.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 2.0, 2)
        calc.add_item('B', 3.0, 3)
        self.assertEqual(calc.get_subtotal(), 13.0)

    def test_get_subtotal_float_precision(self):
        calc = OrderCalculator()
        calc.add_item('A', 0.1, 1)
        calc.add_item('B', 0.2, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3)

    def test_get_subtotal_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.25, 1000000)
        self.assertEqual(calc.get_subtotal(), 1250000.0)

    def test_get_subtotal_updates_after_remove(self):
        calc = OrderCalculator()
        calc.add_item('A', 2.0, 2)
        calc.add_item('B', 3.0, 1)
        self.assertEqual(calc.get_subtotal(), 7.0)
        calc.remove_item('A')
        self.assertEqual(calc.get_subtotal(), 3.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_fractional(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(200.0, 0.25), 150.0)

    def test_apply_discount_subtotal_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(0.0, 0.3), 0.0)

    def test_apply_discount_negative_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_negative_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.05)

    def test_apply_discount_discount_above_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.2)

    def test_apply_discount_non_numeric_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_non_numeric_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.2')

    def test_apply_discount_int_inputs_valid(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100, 0), 100.0)

    def test_apply_discount_int_invalid_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100, 2)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_at_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_negative_input(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(-10.0), 10.0)

    def test_calculate_shipping_non_numeric_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('50')

    def test_calculate_shipping_custom_threshold_and_cost(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(49.0), 5.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)
        self.assertEqual(calc.calculate_shipping(51.0), 0.0)

    def test_calculate_shipping_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=7.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)
        self.assertEqual(calc.calculate_shipping(5.0), 0.0)

    def test_calculate_shipping_large_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=1000000000000.0, shipping_cost=3.0)
        self.assertEqual(calc.calculate_shipping(100.0), 3.0)

    def test_calculate_tax_positive(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_non_numeric_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_calculate_tax_float_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(12.345), 12.345 * 0.23)

    def test_calculate_tax_different_rates(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(100.0), 0.0)
        calc = OrderCalculator(tax_rate=0.5)
        self.assertEqual(calc.calculate_tax(100.0), 50.0)
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.calculate_tax(100.0), 100.0)

    def test_calculate_tax_large_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(1000000000.0), 230000000.0)

    def test_calculate_total_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_single_item_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 2)
        expected = 20.0 + 10.0 + (20.0 + 10.0) * 0.23
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_with_discount(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 2)
        expected = 18.0 + 10.0 + (18.0 + 10.0) * 0.23
        self.assertAlmostEqual(calc.calculate_total(0.1), expected)

    def test_calculate_total_free_shipping_triggered(self):
        calc = OrderCalculator(free_shipping_threshold=15.0, shipping_cost=5.0)
        calc.add_item('Item', 10.0, 2)
        expected = 20.0 + 0.0 + 20.0 * 0.23
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_discount_100(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 2)
        expected = 0.0 + 10.0 + (0.0 + 10.0) * 0.23
        self.assertAlmostEqual(calc.calculate_total(1.0), expected)

    def test_calculate_total_default_discount(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 2)
        self.assertAlmostEqual(calc.calculate_total(), calc.calculate_total(0.0))

    def test_calculate_total_invalid_discount_type_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 2)
        with self.assertRaises(TypeError):
            calc.calculate_total('0.2')

    def test_calculate_total_discount_out_of_range_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 2)
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.5)

    def test_calculate_total_multiple_items_custom_setup(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=7.0)
        calc.add_item('A', 25.0, 2)
        calc.add_item('B', 30.0, 1)
        expected = 76.0 + 7.0 + (76.0 + 7.0) * 0.1
        self.assertAlmostEqual(calc.calculate_total(0.05), expected)

    def test_calculate_total_after_clear_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 5.0, 1)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 7)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 1.0, 3)
        calc.add_item('C', 1.0, 4)
        self.assertEqual(calc.total_items(), 9)

    def test_total_items_after_add_remove(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 5)
        calc.add_item('B', 1.0, 3)
        self.assertEqual(calc.total_items(), 8)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1000000)
        self.assertEqual(calc.total_items(), 1000000)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 5)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.items, [])
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_clear_order_then_add_item(self):
        calc = OrderCalculator()
        calc.clear_order()
        calc.add_item('Item', 2.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 3)

    def test_clear_order_then_get_subtotal_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(set(calc.list_items()), {'Apple'})

    def test_list_items_multiple_distinct(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 1.0, 1)
        calc.add_item('Cherry', 1.0, 1)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana', 'Cherry'})

    def test_list_items_duplicate_names_same_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_after_remove(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 1.0, 1)
        calc.remove_item('Apple')
        self.assertEqual(calc.list_items(), ['Banana'])

    def test_list_items_return_type(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        result = calc.list_items()
        self.assertIsInstance(result, list)
        self.assertTrue(all((isinstance(x, str) for x in result)))

    def test_is_empty_true(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_add_then_false(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        calc.add_item('Item', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_remove_last_then_true(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        self.assertFalse(calc.is_empty())
        calc.remove_item('Item')
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
if __name__ == '__main__':
    unittest.main()