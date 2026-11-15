import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.list_items(), [])

    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_tax_rate_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_free_shipping_threshold_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_shipping_cost_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_tax_rate_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_free_shipping_threshold_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_add_item_first_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(calc.list_items(), ['Apple'])
        self.assertAlmostEqual(calc.get_subtotal(), 2.0)

    def test_add_item_second_distinct_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 0.5, 3)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})
        self.assertAlmostEqual(calc.get_subtotal(), 1.0 * 1 + 0.5 * 3)

    def test_add_item_increase_quantity_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.list_items(), ['Apple'])
        self.assertAlmostEqual(calc.get_subtotal(), 4.0)

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

    def test_add_item_price_non_positive_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 0.0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', -5.0)

    def test_add_item_price_wrong_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', '10')

    def test_add_item_quantity_less_than_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, -2)

    def test_add_item_quantity_wrong_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, 1.5)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Orange', 0.8)
        self.assertEqual(calc.list_items(), ['Orange'])
        self.assertAlmostEqual(calc.get_subtotal(), 0.8)

    def test_remove_item_existing_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_remove_item_one_of_several(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 0.5, 2)
        calc.remove_item('Banana')
        self.assertEqual(calc.list_items(), ['Apple'])
        self.assertAlmostEqual(calc.get_subtotal(), 1.0)

    def test_remove_item_nonexistent_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            calc.remove_item('Cherry')

    def test_remove_item_order_becomes_empty(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_remove_item_non_string_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_none_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(None)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 6.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 2)
        calc.add_item('Banana', 1.0, 5)
        self.assertAlmostEqual(calc.get_subtotal(), 9.0)

    def test_get_subtotal_fractional(self):
        calc = OrderCalculator()
        calc.add_item('Widget', 0.99, 7)
        self.assertAlmostEqual(calc.get_subtotal(), 6.93)

    def test_get_subtotal_empty_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_no_side_effects(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        before = calc.list_items()
        calc.get_subtotal()
        after = calc.list_items()
        self.assertEqual(before, after)

    def test_apply_discount_zero_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_partial(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(200.0, 0.25), 150.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_zero_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(0.0, 0.2), 0.0)

    def test_apply_discount_negative_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_negative_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.05)

    def test_apply_discount_discount_over_one_raises(self):
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

    def test_apply_discount_no_state_change(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        before = calc.list_items()
        calc.apply_discount(50.0, 0.1)
        after = calc.list_items()
        self.assertEqual(before, after)

    def test_calculate_shipping_free_above_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(120.0), 0.0)

    def test_calculate_shipping_free_at_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_cost_below_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(80.0), 10.0)

    def test_calculate_shipping_custom_threshold_cost(self):
        calc = OrderCalculator(shipping_cost=5.0, free_shipping_threshold=50.0)
        self.assertEqual(calc.calculate_shipping(40.0), 5.0)

    def test_calculate_shipping_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(30.0), 0.0)

    def test_calculate_shipping_non_numeric_input_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('50')

    def test_calculate_shipping_none_input_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping(None)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_positive_amount_default_rate(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_custom_rate(self):
        calc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(calc.calculate_tax(12.5), 2.5)

    def test_calculate_tax_negative_amount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_non_numeric_amount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_calculate_tax_none_amount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax(None)

    def test_calculate_total_no_discount_shipping_applied(self):
        calc = OrderCalculator()
        calc.add_item('Book', 20.0, 2)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 61.5)

    def test_calculate_total_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Item', 60.0, 2)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 147.6)

    def test_calculate_total_discount_below_threshold_shipping_added(self):
        calc = OrderCalculator()
        calc.add_item('Item', 50.0, 2)
        total = calc.calculate_total(0.2)
        self.assertAlmostEqual(total, 110.7)

    def test_calculate_total_full_discount_only_shipping_taxed(self):
        calc = OrderCalculator()
        calc.add_item('Item', 50.0, 1)
        total = calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 12.3)

    def test_calculate_total_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(0.0)

    def test_calculate_total_negative_discount_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)

    def test_calculate_total_discount_over_one_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.5)

    def test_calculate_total_non_numeric_discount_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total('0.2')

    def test_calculate_total_tax_after_shipping(self):
        calc = OrderCalculator()
        calc.add_item('A', 10.0, 1)
        total = calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 24.6)

    def test_calculate_total_no_side_effects(self):
        calc = OrderCalculator()
        calc.add_item('A', 10.0, 1)
        before = calc.list_items()
        calc.calculate_total(0.0)
        after = calc.list_items()
        self.assertEqual(before, after)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_qty_one(self):
        calc = OrderCalculator()
        calc.add_item('Pen', 1.0, 1)
        self.assertEqual(calc.total_items(), 1)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 2.0, 2)
        calc.add_item('B', 3.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_add_then_remove(self):
        calc = OrderCalculator()
        calc.add_item('C', 5.0, 2)
        self.assertEqual(calc.total_items(), 2)
        calc.remove_item('C')
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_returns_int(self):
        calc = OrderCalculator()
        calc.add_item('X', 1.0, 1)
        self.assertIsInstance(calc.total_items(), int)

    def test_clear_order_clears_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 2.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_clears_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_configuration_unchanged(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=20.0, shipping_cost=3.0)
        calc.add_item('Item', 5.0, 1)
        calc.clear_order()
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 20.0)
        self.assertEqual(calc.shipping_cost, 3.0)

    def test_clear_order_returns_none(self):
        calc = OrderCalculator()
        self.assertIsNone(calc.clear_order())

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_multiple_distinct(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 1)
        calc.add_item('Cherry', 3.0, 1)
        result = calc.list_items()
        self.assertEqual(set(result), {'Apple', 'Banana', 'Cherry'})
        self.assertEqual(len(result), 3)

    def test_list_items_duplicate_name_single_entry(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_returned_list_is_copy(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        lst = calc.list_items()
        lst.append('B')
        self.assertNotIn('B', calc.list_items())

    def test_is_empty_empty_true(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_nonempty_false(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_clear_true(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_remove_last_true(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.remove_item('Item')
        self.assertTrue(calc.is_empty())

    def test_is_empty_returns_bool(self):
        calc = OrderCalculator()
        self.assertIsInstance(calc.is_empty(), bool)