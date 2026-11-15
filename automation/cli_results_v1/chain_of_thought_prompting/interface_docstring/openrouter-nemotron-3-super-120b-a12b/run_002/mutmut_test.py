import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_explicit(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)
        self.assertEqual(calc.items, [])

    def test_init_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_init_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_free_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_free_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_init_mixed_types(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate=0.2, free_shipping_threshold='100', shipping_cost=5.0)

    def test_add_item_normal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'Apple')
        self.assertEqual(calc.items[0]['price'], 0.5)
        self.assertEqual(calc.items[0]['quantity'], 3)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 1.0)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_merge_same_name_price(self):
        calc = OrderCalculator()
        calc.add_item('Book', 10.0, 2)
        calc.add_item('Book', 10.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 5)

    def test_add_item_quantity_one(self):
        calc = OrderCalculator()
        calc.add_item('Pen', 2.0, 1)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_quantity_zero(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Pen', 2.0, 0)

    def test_add_item_quantity_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Pen', 2.0, -2)

    def test_add_item_quantity_non_int(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Pen', 2.0, 1.5)

    def test_add_item_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 2.0, 1)

    def test_add_item_name_wrong_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 2.0, 1)

    def test_add_item_price_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Pen', -1.0, 1)

    def test_add_item_price_zero(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Pen', 0.0, 1)

    def test_add_item_price_wrong_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Pen', '5', 1)

    def test_add_item_same_name_diff_price(self):
        calc = OrderCalculator()
        calc.add_item('Book', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Book', 12.0, 1)

    def test_add_item_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 5.0, 1)
        calc.clear_order()
        calc.add_item('Item', 5.0, 2)
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_add_item_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('Big', 1000000000.0, 1000000)
        self.assertEqual(calc.items[0]['price'], 1000000000.0)
        self.assertEqual(calc.items[0]['quantity'], 1000000)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('Item', 5.0, 1)
        calc.remove_item('Item')
        self.assertEqual(calc.items, [])

    def test_remove_item_quantity_gt_one(self):
        calc = OrderCalculator()
        calc.add_item('Item', 5.0, 10)
        calc.remove_item('Item')
        self.assertEqual(calc.items, [])

    def test_remove_item_nonexistent(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Missing')

    def test_remove_item_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Any')

    def test_remove_item_name_wrong_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(42)

    def test_remove_item_name_none(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(None)

    def test_remove_item_after_multiple_adds(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 2.0, 1)
        calc.remove_item('A')
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'B')

    def test_remove_item_case_sensitivity(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0, 1)
        with self.assertRaises(ValueError):
            calc.remove_item('Apple')

    def test_get_subtotal_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 2)
        self.assertEqual(calc.get_subtotal(), 20.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 5.0, 3)
        calc.add_item('B', 2.0, 4)
        self.assertEqual(calc.get_subtotal(), 5.0 * 3 + 2.0 * 4)

    def test_get_subtotal_zero_price_item_defensive(self):
        calc = OrderCalculator()
        calc.items.append({'name': 'Zero', 'price': 0.0, 'quantity': 5})
        self.assertEqual(calc.get_subtotal(), 0.0)

    def test_get_subtotal_large_quantities(self):
        calc = OrderCalculator()
        calc.add_item('Small', 0.01, 1000000)
        self.assertEqual(calc.get_subtotal(), 10000.0)

    def test_get_subtotal_after_add_remove(self):
        calc = OrderCalculator()
        calc.add_item('A', 5.0, 2)
        calc.add_item('B', 3.0, 1)
        self.assertEqual(calc.get_subtotal(), 5.0 * 2 + 3.0 * 1)
        calc.remove_item('A')
        self.assertEqual(calc.get_subtotal(), 3.0 * 1)

    def test_get_subtotal_floating_point(self):
        calc = OrderCalculator()
        calc.add_item('A', 0.1, 1)
        calc.add_item('B', 0.2, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3, places=7)

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

    def test_apply_discount_bounds(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(50.0, 0.0), 50.0)
        self.assertEqual(calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-5.0, 0.1)

    def test_apply_discount_negative_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, -0.1)

    def test_apply_discount_over_one(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, 1.1)

    def test_apply_discount_subtotal_wrong_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_discount_wrong_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.1')

    def test_apply_discount_none_inputs(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(None, 0.1)
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, None)

    def test_apply_discount_floating_point(self):
        calc = OrderCalculator()
        result = calc.apply_discount(1.0, 0.333333)
        self.assertAlmostEqual(result, 0.666667, places=6)

    def test_apply_discount_purity(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        before = len(calc.items)
        calc.apply_discount(20.0, 0.1)
        after = len(calc.items)
        self.assertEqual(before, after)

    def test_calculate_shipping_free_threshold_met(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_free_threshold_not_met(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_exact_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_just_below_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_zero_subtotal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('100')
        with self.assertRaises(TypeError):
            calc.calculate_shipping(None)

    def test_calculate_shipping_custom_config(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)
        self.assertEqual(calc.calculate_shipping(49.99), 5.0)

    def test_calculate_shipping_floating_point_edge(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(99.999999), 10.0)

    def test_calculate_tax_typical(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-1.0)

    def test_calculate_tax_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')
        with self.assertRaises(TypeError):
            calc.calculate_tax(None)

    def test_calculate_tax_custom_rate(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertEqual(calc.calculate_tax(200.0), 10.0)

    def test_calculate_tax_floating_point(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(1.0), 0.23, places=7)

    def test_calculate_tax_purity(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        before = len(calc.items)
        calc.calculate_tax(50.0)
        after = len(calc.items)
        self.assertEqual(before, after)

    def test_calculate_total_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_no_discount_shipping_applies(self):
        calc = OrderCalculator()
        calc.add_item('A', 20.0, 2)
        calc.add_item('B', 5.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 67.65, places=2)

    def test_calculate_total_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('A', 60.0, 1)
        calc.add_item('B', 60.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 147.6, places=2)

    def test_calculate_total_with_discount(self):
        calc = OrderCalculator()
        calc.add_item('A', 20.0, 2)
        calc.add_item('B', 5.0, 1)
        self.assertAlmostEqual(calc.calculate_total(0.1), 62.115, places=3)

    def test_calculate_total_discount_free_shipping_still_free(self):
        calc = OrderCalculator()
        calc.add_item('A', 80.0, 1)
        calc.add_item('B', 80.0, 1)
        self.assertAlmostEqual(calc.calculate_total(0.1), 177.12, places=2)

    def test_calculate_total_invalid_discount_negative(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.05)

    def test_calculate_total_invalid_discount_over_one(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.2)

    def test_calculate_total_discount_wrong_type(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total('0.1')

    def test_calculate_total_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        _ = calc.calculate_total()
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_floating_point(self):
        calc = OrderCalculator()
        calc.add_item('A', 0.1, 1)
        calc.add_item('B', 0.2, 1)
        self.assertAlmostEqual(calc.calculate_total(), 12.669, places=3)

    def test_calculate_total_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Item', 10.0, 1)
        self.assertEqual(calc.calculate_total(), 20.0)

    def test_calculate_total_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Item', 50.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 61.5, places=2)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Item', 5.0, 7)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 3)
        calc.add_item('B', 2.0, 4)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_after_add_remove(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 5)
        calc.add_item('B', 2.0, 3)
        self.assertEqual(calc.total_items(), 8)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 5)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 10 ** 6)
        self.assertEqual(calc.total_items(), 10 ** 6)

    def test_total_items_zero_quantity_item_defensive(self):
        calc = OrderCalculator()
        calc.items.append({'name': 'Zero', 'price': 1.0, 'quantity': 0})
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('Item', 5.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_after_partial_removes(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 1)
        calc.remove_item('A')
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_does_not_reset_config(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=30.0, shipping_cost=3.0)
        calc.add_item('Item', 10.0, 1)
        calc.clear_order()
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 30.0)
        self.assertEqual(calc.shipping_cost, 3.0)

    def test_clear_order_return_value(self):
        calc = OrderCalculator()
        self.assertIsNone(calc.clear_order())

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_multiple_unique(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 1)
        result = calc.list_items()
        self.assertCountEqual(result, ['Apple', 'Banana'])

    def test_list_items_duplicate_name_same_price(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 2)
        calc.add_item('Item', 1.0, 3)
        self.assertEqual(calc.list_items(), ['Item'])

    def test_list_items_after_remove(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 1)
        calc.remove_item('A')
        self.assertEqual(calc.list_items(), ['B'])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_return_type(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        result = calc.list_items()
        self.assertIsInstance(result, list)
        for elem in result:
            self.assertIsInstance(elem, str)

    def test_list_items_immutability(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        lst = calc.list_items()
        lst.append('Extra')
        self.assertEqual(calc.list_items(), ['Item'])

    def test_is_empty_true_initially(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_after_add(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_true_after_remove(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.remove_item('Item')
        self.assertTrue(calc.is_empty())

    def test_is_empty_true_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_with_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_return_type(self):
        calc = OrderCalculator()
        self.assertIsInstance(calc.is_empty(), bool)