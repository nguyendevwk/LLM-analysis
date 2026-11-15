import unittest
from unittest.mock import patch
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertEqual(oc.items, [])

    def test_init_custom_values(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=5)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0)
        self.assertEqual(oc.shipping_cost, 5)

    def test_init_invalid_tax_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_tax_range_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_invalid_tax_range_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_invalid_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    def test_init_invalid_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_simple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['name'], 'Apple')
        self.assertEqual(oc.items[0]['price'], 1.5)
        self.assertEqual(oc.items[0]['quantity'], 2)
        self.assertEqual(oc.total_items(), 2)

    def test_add_item_multiple_distinct(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.add_item('Banana', 2.0, 1)
        self.assertEqual(len(oc.items), 2)

    def test_add_item_merge(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['quantity'], 5)

    def test_add_item_conflict_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0, 1)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_price_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 0, 1)

    def test_add_item_price_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Apple', -1, 1)

    def test_add_item_quantity_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 1.0, 0)

    def test_add_item_quantity_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 1.0, -2)

    def test_add_item_name_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_price_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', '1.5', 1)

    def test_add_item_quantity_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', 1.5, 3.5)

    def test_add_item_int_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2, 1)
        self.assertEqual(oc.items[0]['price'], 2)

    def test_add_item_bool_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, True)
        self.assertEqual(oc.items[0]['quantity'], 1)

    def test_add_item_bool_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(True, 1.5, 1)

    def test_add_item_large_numbers(self):
        oc = OrderCalculator()
        oc.add_item('Expensive', 9999.99, 1000)
        self.assertEqual(oc.items[0]['price'], 9999.99)
        self.assertEqual(oc.items[0]['quantity'], 1000)

    def test_remove_item_existing(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.remove_item('Apple')
        self.assertFalse(any((i['name'] == 'Apple' for i in oc.items)))
        self.assertTrue(oc.is_empty())

    def test_remove_item_nonexistent(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Orange')

    def test_remove_item_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_remove_item_list_updates(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.add_item('Banana', 2.0, 1)
        oc.remove_item('Apple')
        self.assertNotIn('Apple', oc.list_items())

    def test_remove_only_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_get_subtotal_normal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 2.0, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 5.0)

    def test_get_subtotal_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_get_subtotal_large(self):
        oc = OrderCalculator()
        oc.add_item('Expensive', 9999.99, 1000)
        self.assertAlmostEqual(oc.get_subtotal(), 9999.99 * 1000)

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(100, 0.0), 100)

    def test_apply_discount_twenty_percent(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0.2), 80)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(100, 1.0), 0)

    def test_apply_discount_zero_subtotal(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(0, 0.5), 0)

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-5, 0.1)

    def test_apply_discount_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, -0.1)

    def test_apply_discount_discount_over_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, 1.5)

    def test_apply_discount_subtotal_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)

    def test_apply_discount_discount_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100, '0.1')

    def test_apply_discount_int_discount(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(100, 1), 0)

    def test_apply_discount_bool_discount(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(100, True), 0)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(150), 0.0)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(100), 0.0)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_custom_zero_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=0)
        self.assertEqual(oc.calculate_shipping(0), 0.0)

    def test_calculate_shipping_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('50')

    def test_calculate_shipping_bool_subtotal(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(True), 10.0)

    def test_calculate_tax_positive(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(200), 46.0)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_tax(0), 0.0)

    def test_calculate_tax_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-10)

    def test_calculate_tax_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax(None)

    def test_calculate_tax_rate_zero(self):
        oc = OrderCalculator(tax_rate=0)
        self.assertEqual(oc.calculate_tax(100), 0.0)

    def test_calculate_tax_rate_one(self):
        oc = OrderCalculator(tax_rate=1)
        self.assertEqual(oc.calculate_tax(100), 100.0)

    def test_calculate_tax_bool_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(True), 0.23)

    def test_calculate_total_typical(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 2.0, 1)
        total = oc.calculate_total(0.1)
        self.assertAlmostEqual(total, 17.835, places=5)

    def test_calculate_total_free_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=5)
        oc.add_item('Item', 10, 1)
        total = oc.calculate_total(0.5)
        self.assertAlmostEqual(total, 6.15, places=5)

    def test_calculate_total_full_discount(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        total = oc.calculate_total(1.0)
        self.assertAlmostEqual(total, 12.3, places=5)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_calculate_total_discount_wrong_type(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total('0.2')

    def test_calculate_total_discount_out_of_range_low(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(-0.1)

    def test_calculate_total_discount_out_of_range_high(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(1.2)

    def test_calculate_total_negative_subtotal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with patch.object(oc, 'get_subtotal', return_value=-5):
            with self.assertRaises(ValueError):
                oc.calculate_total()

    def test_calculate_total_custom_rates(self):
        oc = OrderCalculator(tax_rate=0.1, shipping_cost=5, free_shipping_threshold=20)
        oc.add_item('Item', 10, 1)
        total = oc.calculate_total(0.0)
        self.assertAlmostEqual(total, 16.5, places=5)

    def test_calculate_total_discount_int(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        total = oc.calculate_total(1)
        self.assertAlmostEqual(total, 12.3, places=5)

    def test_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 2.0, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 2.0, 3)
        oc.remove_item('Banana')
        self.assertEqual(oc.total_items(), 2)

    def test_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_after_merge(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_clear_order_non_empty(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)

    def test_clear_order_already_empty(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_list_items_distinct(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.add_item('Banana', 2.0, 1)
        oc.add_item('Apple', 1.5, 1)
        items = oc.list_items()
        self.assertCountEqual(items, ['Apple', 'Banana'])

    def test_list_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_list_items_uniqueness_after_merges(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.list_items(), ['Apple'])

    def test_list_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.add_item('Banana', 2.0, 1)
        oc.remove_item('Apple')
        self.assertEqual(oc.list_items(), ['Banana'])

    def test_is_empty_fresh(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_adding(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_removing_only_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_partial_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.add_item('Banana', 2.0, 1)
        oc.remove_item('Apple')
        self.assertFalse(oc.is_empty())

    def test_merge_then_remove_results_empty(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_shipping_threshold_zero(self):
        oc = OrderCalculator(free_shipping_threshold=0)
        oc.add_item('Apple', 1, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 1.23, places=5)

    def test_tax_rate_extremes(self):
        oc_zero = OrderCalculator(tax_rate=0)
        oc_one = OrderCalculator(tax_rate=1)
        oc_zero.add_item('Item', 10, 1)
        oc_one.add_item('Item', 10, 1)
        total_zero = oc_zero.calculate_total()
        total_one = oc_one.calculate_total()
        self.assertAlmostEqual(total_zero, 20.0, places=5)
        self.assertAlmostEqual(total_one, 40.0, places=5)

    def test_boolean_inputs_handling(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, True)
        total = oc.calculate_total(True)
        self.assertAlmostEqual(total, 12.3, places=5)

    def test_monkeypatched_get_subtotal_non_numeric(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with patch.object(oc, 'get_subtotal', return_value='abc'):
            with self.assertRaises(TypeError):
                oc.calculate_total(0.1)

    def test_remove_item_multiple_occurrences(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.add_item('Apple', 1.5, 2)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_case_sensitive_names(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1, 1)
        oc.add_item('Apple', 1, 1)
        self.assertCountEqual(oc.list_items(), ['apple', 'Apple'])

    def test_whitespace_name_accepted(self):
        oc = OrderCalculator()
        oc.add_item('  ', 1.0, 1)
        self.assertIn('  ', oc.list_items())