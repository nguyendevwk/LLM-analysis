import unittest
from order_calculator import OrderCalculator
from unittest.mock import patch

class TestOrderCalculator(unittest.TestCase):

    def test_constructor_default(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertEqual(oc.items, [])

    def test_constructor_custom_valid(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0)
        self.assertEqual(oc.shipping_cost, 0)

    def test_constructor_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_constructor_tax_rate_value_error_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_constructor_tax_rate_value_error_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_constructor_free_shipping_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_constructor_free_shipping_threshold_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_constructor_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    def test_constructor_shipping_cost_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_add_item_first_valid(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['quantity'], 2)
        self.assertEqual(oc.total_items(), 2)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_add_item_second_distinct(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 0.8)
        self.assertEqual(len(oc.items), 2)
        self.assertEqual(oc.total_items(), 3)

    def test_add_item_merge_same_name_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['quantity'], 5)

    def test_add_item_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0, 1)

    def test_add_item_name_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_name_value_error_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_price_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Item', 'free', 1)

    def test_add_item_price_value_error_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Item', 0, 1)

    def test_add_item_price_value_error_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Item', -1, 1)

    def test_add_item_quantity_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Item', 1.0, 2.5)

    def test_add_item_quantity_value_error_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Item', 1.0, 0)

    def test_add_item_quantity_value_error_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Item', 1.0, -3)

    def test_add_item_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Gadget', 9.99, 10000)
        self.assertEqual(oc.total_items(), 10000)

    def test_add_item_high_precision_price(self):
        oc = OrderCalculator()
        oc.add_item('Widget', 1.333333, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 1.333333)

    def test_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Pear', 0.5)
        self.assertEqual(oc.items[0]['quantity'], 1)

    def test_add_item_price_int(self):
        oc = OrderCalculator()
        oc.add_item('Mango', 2, 2)
        self.assertEqual(oc.items[0]['price'], 2)

    def test_remove_item_existing(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8, 3)
        oc.remove_item('Banana')
        self.assertFalse(any((i['name'] == 'Banana' for i in oc.items)))

    def test_remove_item_nonexistent(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Cherry')

    def test_remove_item_name_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(None)

    def test_remove_item_last_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_remove_item_multiple_same_name(self):
        oc = OrderCalculator()
        oc.items = [{'name': 'Dup', 'price': 1, 'quantity': 1}, {'name': 'Dup', 'price': 1, 'quantity': 2}]
        oc.remove_item('Dup')
        self.assertFalse(any((i['name'] == 'Dup' for i in oc.items)))

    def test_get_subtotal_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_get_subtotal_floating_precision(self):
        oc = OrderCalculator()
        oc.add_item('Tiny', 0.1, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 0.30000000000000004)

    def test_get_subtotal_large(self):
        oc = OrderCalculator()
        for _ in range(200):
            oc.add_item('Item', 100, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 20000)

    def test_apply_discount_twenty_percent(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0.2), 80.0)

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50, 0), 50)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50, 1.0), 0.0)

    def test_apply_discount_subtotal_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)

    def test_apply_discount_discount_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100, [0.1])

    def test_apply_discount_discount_value_error_low(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, -0.1)

    def test_apply_discount_discount_value_error_high(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, 1.5)

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-5, 0.1)

    def test_apply_discount_integer_discount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0), 100)

    def test_apply_discount_high_precision(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0.333333), 66.6667, places=4)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(150), 0.0)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(100), 0.0)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_always_free(self):
        oc = OrderCalculator(free_shipping_threshold=0, shipping_cost=5)
        self.assertEqual(oc.calculate_shipping(0), 0.0)
        self.assertEqual(oc.calculate_shipping(50), 0.0)

    def test_calculate_shipping_never_free(self):
        oc = OrderCalculator(free_shipping_threshold=1000, shipping_cost=7)
        self.assertEqual(oc.calculate_shipping(500), 7)

    def test_calculate_shipping_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping(None)

    def test_calculate_shipping_zero(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(0), 10.0)

    def test_calculate_tax_normal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(200), 46.0)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0), 0.0)

    def test_calculate_tax_rate_zero(self):
        oc = OrderCalculator(tax_rate=0)
        self.assertAlmostEqual(oc.calculate_tax(123), 0.0)

    def test_calculate_tax_rate_full(self):
        oc = OrderCalculator(tax_rate=1)
        self.assertAlmostEqual(oc.calculate_tax(123), 123)

    def test_calculate_tax_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax('200')

    def test_calculate_tax_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-10)

    def test_calculate_tax_integer_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(150), 34.5)

    def test_calculate_tax_high_precision(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.1), 0.023)

    def test_calculate_total_discount_triggers_free_shipping(self):
        oc = OrderCalculator()
        for _ in range(20):
            oc.add_item('Item', 10, 1)
        total = oc.calculate_total(0.5)
        self.assertAlmostEqual(total, 123.0, places=2)

    def test_calculate_total_full_discount(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        total = oc.calculate_total(1.0)
        self.assertAlmostEqual(total, 12.3, places=2)

    def test_calculate_total_discount_type_error(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total('0.1')

    def test_calculate_total_discount_value_error_low(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(-0.1)

    def test_calculate_total_discount_value_error_high(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(1.2)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_calculate_total_custom_tax_shipping(self):
        oc = OrderCalculator(tax_rate=0, shipping_cost=0)
        oc.add_item('Apple', 2, 2)
        total = oc.calculate_total(0.1)
        self.assertAlmostEqual(total, 3.6)

    def test_calculate_total_custom_free_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=50, shipping_cost=15)
        oc.add_item('Item', 10, 8)
        total = oc.calculate_total(0.3)
        self.assertAlmostEqual(total, 56 + 56 * 0.23, places=2)

    def test_calculate_total_negative_subtotal_monkeypatched(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        with patch.object(oc, 'get_subtotal', return_value=-5):
            with self.assertRaises(ValueError):
                oc.calculate_total()

    def test_total_items_after_additions(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 0.8, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 0.8, 3)
        oc.remove_item('Banana')
        self.assertEqual(oc.total_items(), 2)

    def test_total_items_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.clear_order()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Bulk', 1.0, 999)
        self.assertEqual(oc.total_items(), 999)

    def test_total_items_merge_duplicate(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_clear_order_populated(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_clear_order_already_empty(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_list_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 0.8, 3)
        oc.add_item('Apple', 1.5, 1)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana'])

    def test_list_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 0.8, 3)
        oc.remove_item('Apple')
        self.assertCountEqual(oc.list_items(), ['Banana'])

    def test_list_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_list_items_duplicate_forced(self):
        oc = OrderCalculator()
        oc.items = [{'name': 'Dup', 'price': 1, 'quantity': 1}, {'name': 'Dup', 'price': 1, 'quantity': 2}]
        self.assertCountEqual(oc.list_items(), ['Dup'])

    def test_list_items_case_sensitivity(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1, 1)
        oc.add_item('Apple', 1, 1)
        self.assertCountEqual(oc.list_items(), ['apple', 'Apple'])

    def test_is_empty_fresh(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_add(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_last_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_two_instances_independent(self):
        oc1 = OrderCalculator()
        oc2 = OrderCalculator()
        oc1.add_item('Apple', 1, 1)
        self.assertFalse(oc1.is_empty())
        self.assertTrue(oc2.is_empty())

    def test_clearing_one_does_not_affect_other(self):
        oc1 = OrderCalculator()
        oc2 = OrderCalculator()
        oc1.add_item('Apple', 1, 1)
        oc2.add_item('Banana', 1, 1)
        oc1.clear_order()
        self.assertTrue(oc1.is_empty())
        self.assertFalse(oc2.is_empty())

    def test_list_items_mutation_no_effect(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        lst = oc.list_items()
        lst.append('X')
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_calculate_total_idempotent(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        first = oc.calculate_total()
        second = oc.calculate_total()
        self.assertAlmostEqual(first, second)

    def test_integer_vs_float_inputs(self):
        oc = OrderCalculator(tax_rate=0, free_shipping_threshold=0, shipping_cost=0)
        oc.add_item('Item', 5, 2)
        self.assertAlmostEqual(oc.calculate_total(0), 10)

    def test_extremely_small_numbers(self):
        oc = OrderCalculator()
        oc.add_item('Tiny', 1e-09, 1)
        subtotal = oc.get_subtotal()
        self.assertAlmostEqual(subtotal, 1e-09)

    def test_extremely_large_numbers(self):
        oc = OrderCalculator()
        oc.add_item('Huge', 1000000000.0, 2)
        subtotal = oc.get_subtotal()
        self.assertAlmostEqual(subtotal, 2000000000.0)

    def test_large_subtotal_full_discount_shipping(self):
        oc = OrderCalculator()
        oc.add_item('Item', 1000000.0, 1)
        total = oc.calculate_total(1.0)
        self.assertAlmostEqual(total, 10 + 10 * 0.23, places=2)

    def test_malformed_items_missing_quantity(self):
        oc = OrderCalculator()
        oc.items = [{'name': 'Bad', 'price': 1}]
        with self.assertRaises(KeyError):
            oc.get_subtotal()

    def test_clear_order_new_list_object(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        old_id = id(oc.items)
        oc.clear_order()
        self.assertNotEqual(id(oc.items), old_id)