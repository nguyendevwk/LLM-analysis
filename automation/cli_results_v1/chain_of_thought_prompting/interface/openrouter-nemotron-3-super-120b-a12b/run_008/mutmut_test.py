import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.tax_rate, 0.23)
        self.assertAlmostEqual(calc.free_shipping_threshold, 100.0)
        self.assertAlmostEqual(calc.shipping_cost, 10.0)

    def test_init_custom_params(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.tax_rate, 0.05)
        self.assertAlmostEqual(calc.free_shipping_threshold, 50.0)
        self.assertAlmostEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc.tax_rate, 0.0)

    def test_init_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertAlmostEqual(calc.free_shipping_threshold, 0.0)

    def test_init_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertAlmostEqual(calc.shipping_cost, 0.0)

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_normal_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0)
        self.assertEqual(calc.list_items(), ['apple'])
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 1.0)

    def test_add_item_normal_quantity_greater_than_one(self):
        calc = OrderCalculator()
        calc.add_item('banana', 0.5, 4)
        self.assertEqual(calc.list_items(), ['banana'])
        self.assertEqual(calc.total_items(), 4)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0)

    def test_add_item_duplicate_name_accumulates_quantity(self):
        calc = OrderCalculator()
        calc.add_item('orange', 2.0, 2)
        calc.add_item('orange', 2.0, 3)
        self.assertEqual(calc.list_items(), ['orange'])
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 10.0)

    def test_add_item_large_price_and_quantity(self):
        calc = OrderCalculator()
        calc.add_item('expensive', 1000000000000.0, 2)
        self.assertEqual(calc.list_items(), ['expensive'])
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 2000000000000.0)

    def test_add_item_non_string_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(None, 1.0)
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_non_numeric_price_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('item', '1.0')
        with self.assertRaises(TypeError):
            calc.add_item('item', None)

    def test_add_item_non_integer_quantity_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('item', 1.0, 2.5)
        with self.assertRaises(TypeError):
            calc.add_item('item', 1.0, '2')

    def test_add_item_negative_quantity_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('item', 1.0, -1)

    def test_add_item_negative_price_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('item', -1.0, 2)

    def test_add_item_sets_non_empty(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        calc.add_item('something', 1.0)
        self.assertFalse(calc.is_empty())

    def test_add_item_list_items_returns_unique_names_once(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 2)
        calc.add_item('b', 2.0, 3)
        calc.add_item('a', 1.0, 1)
        self.assertEqual(calc.list_items(), ['a', 'b'])

    def test_remove_item_existing_item(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0, 2)
        calc.add_item('banana', 0.5, 4)
        calc.remove_item('apple')
        self.assertEqual(calc.list_items(), ['banana'])
        self.assertEqual(calc.total_items(), 4)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0)

    def test_remove_item_existing_item_quantity_gt_one(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0, 2)
        calc.remove_item('apple')
        self.assertTrue(calc.is_empty())

    def test_remove_item_non_existent_raises_keyerror_if_designed_so(self):
        pass

    def test_remove_item_non_string_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(None)
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_single_item_quantity_one(self):
        calc = OrderCalculator()
        calc.add_item('item', 5.0)
        self.assertAlmostEqual(calc.get_subtotal(), 5.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('a', 2.0, 2)
        calc.add_item('b', 3.0, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 7.0)

    def test_get_subtotal_negative_price_if_allowed(self):
        pass

    def test_get_subtotal_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('big', 1000000.0, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 3000000.0)

    def test_apply_discount_zero_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_non_numeric_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 10)
        with self.assertRaises(TypeError):
            calc.apply_discount(None, 10)

    def test_apply_discount_non_numeric_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100, '10')
        with self.assertRaises(TypeError):
            calc.apply_discount(100, None)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_at_threshold_free(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_threshold_zero_always_free(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(0.0), 0.0)
        self.assertAlmostEqual(calc.calculate_shipping(10.0), 0.0)

    def test_calculate_shipping_shipping_cost_zero(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=0.0)
        self.assertAlmostEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_non_numeric_input_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('50')
        with self.assertRaises(TypeError):
            calc.calculate_shipping(None)

    def test_calculate_shipping_uses_instance_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=30.0, shipping_cost=7.0)
        self.assertAlmostEqual(calc.calculate_shipping(20.0), 7.0)
        self.assertAlmostEqual(calc.calculate_shipping(30.0), 0.0)

    def test_calculate_shipping_floating_point_near_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(99.9999), 10.0)
        self.assertAlmostEqual(calc.calculate_shipping(100.0001), 0.0)

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_non_numeric_input_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')
        with self.assertRaises(TypeError):
            calc.calculate_tax(None)

    def test_calculate_tax_does_not_modify_state(self):
        calc = OrderCalculator()
        calc.add_item('item', 10.0)
        before = calc.get_subtotal()
        calc.calculate_tax(50.0)
        after = calc.get_subtotal()
        self.assertAlmostEqual(before, after)

    def test_calculate_tax_large_amount(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(calc.calculate_tax(1000000000000.0), 50000000000.0)

    def test_calculate_tax_floating_point_precision(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(0.1), 0.023, places=7)

    def test_calculate_total_single_item_no_discount(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('book', 50.0)
        self.assertAlmostEqual(calc.calculate_total(), 73.8)

    def test_calculate_total_multiple_items_no_discount(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=5.0)
        calc.add_item('a', 30.0, 2)
        calc.add_item('b', 20.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 93.5)

    def test_calculate_total_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=100.0, shipping_cost=5.0)
        calc.add_item('item', 100.0)
        self.assertAlmostEqual(calc.calculate_total(), 100.0)

    def test_calculate_total_zero_shipping_cost(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=0.0)
        calc.add_item('item', 50.0)
        self.assertAlmostEqual(calc.calculate_total(), 55.0)

    def test_calculate_total_free_shipping_always(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=0.0, shipping_cost=5.0)
        calc.add_item('item', 10.0)
        self.assertAlmostEqual(calc.calculate_total(), 11.0)

    def test_calculate_total_non_numeric_discount_raises(self):
        calc = OrderCalculator()
        calc.add_item('item', 10.0)
        with self.assertRaises(TypeError):
            calc.calculate_total('5')
        with self.assertRaises(TypeError):
            calc.calculate_total(None)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_item_quantity_one(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0)
        self.assertEqual(calc.total_items(), 1)

    def test_total_items_single_item_quantity_n(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 7)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 2)
        calc.add_item('b', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_negative_quantity_not_allowed(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('item', 1.0, -1)
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_after_remove(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 2)
        calc.add_item('b', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)
        calc.remove_item('a')
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 5)
        self.assertEqual(calc.total_items(), 5)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_already_empty_idempotent(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_multiple_calls(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0)
        calc.add_item('b', 2.0)
        calc.clear_order()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_preserves_constructor_params(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=30.0, shipping_cost=7.0)
        calc.add_item('item', 10.0)
        calc.clear_order()
        self.assertAlmostEqual(calc.tax_rate, 0.05)
        self.assertAlmostEqual(calc.free_shipping_threshold, 30.0)
        self.assertAlmostEqual(calc.shipping_cost, 7.0)

    def test_clear_order_returns_none(self):
        calc = OrderCalculator()
        result = calc.clear_order()
        self.assertIsNone(result)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0)
        self.assertEqual(calc.list_items(), ['apple'])

    def test_list_items_multiple_distinct_items(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0)
        calc.add_item('b', 2.0)
        calc.add_item('c', 3.0)
        self.assertEqual(calc.list_items(), ['a', 'b', 'c'])

    def test_list_items_preserves_insertion_order(self):
        calc = OrderCalculator()
        calc.add_item('first', 1.0)
        calc.add_item('second', 1.0)
        calc.add_item('third', 1.0)
        self.assertEqual(calc.list_items(), ['first', 'second', 'third'])

    def test_list_items_duplicate_name_appears_once(self):
        calc = OrderCalculator()
        calc.add_item('dup', 1.0, 2)
        calc.add_item('dup', 1.0, 3)
        self.assertEqual(calc.list_items(), ['dup'])

    def test_list_items_after_remove(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0)
        calc.add_item('b', 1.0)
        calc.remove_item('a')
        self.assertEqual(calc.list_items(), ['b'])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_returned_list_is_copy(self):
        calc = OrderCalculator()
        calc.add_item('x', 1.0)
        lst = calc.list_items()
        lst.append('y')
        self.assertNotIn('y', calc.list_items())

    def test_list_items_long_names(self):
        calc = OrderCalculator()
        long_name = 'a' * 1000
        calc.add_item(long_name, 1.0)
        self.assertEqual(calc.list_items(), [long_name])

    def test_is_empty_empty_order(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_add_item(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_remove_last_item(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0)
        calc.remove_item('item')
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_returns_bool(self):
        calc = OrderCalculator()
        self.assertIsInstance(calc.is_empty(), bool)

    def test_is_empty_toggles(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        calc.add_item('a', 1.0)
        self.assertFalse(calc.is_empty())
        calc.remove_item('a')
        self.assertTrue(calc.is_empty())
if __name__ == '__main__':
    unittest.main()