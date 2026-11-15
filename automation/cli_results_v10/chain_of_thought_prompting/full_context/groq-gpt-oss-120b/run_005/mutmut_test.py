import unittest
from unittest.mock import patch
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=5)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0)
        self.assertEqual(calc.shipping_cost, 5)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_tax_rate_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_free_shipping_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=[])

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1)

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost={})

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_single_valid(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 2)
        self.assertEqual(self.calc.total_items(), 2)

    def test_add_item_merge_quantity(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Apple', 1.5, 3)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 5)

    def test_add_item_different_name(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 2.0, 1)
        self.assertEqual(len(self.calc.items), 2)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item('Apple', 1.5, 2)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.0, 1)

    def test_add_item_name_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_name_empty(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_price_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', '1.0', 1)

    def test_add_item_price_non_positive(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', -1, 1)

    def test_add_item_quantity_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.0, 1.5)

    def test_add_item_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.0, 0)

    def test_add_item_large_quantity(self):
        self.calc.add_item('Apple', 1.0, 10000)
        self.assertEqual(self.calc.total_items(), 10000)

    def test_add_item_price_int(self):
        self.calc.add_item('Apple', 5, 1)
        self.assertEqual(self.calc.items[0]['price'], 5)

    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Orange')

    def test_remove_item_name_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(['Apple'])

    def test_remove_item_multiple_items(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Banana', 2.0, 1)
        self.calc.remove_item('Apple')
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['name'], 'Banana')

    def test_get_subtotal_normal(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 2.0, 3)
        self.assertEqual(self.calc.get_subtotal(), 9.0)

    def test_get_subtotal_single_item(self):
        self.calc.add_item('Apple', 3.0, 1)
        self.assertEqual(self.calc.get_subtotal(), 3.0)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_get_subtotal_floating_point(self):
        self.calc.add_item('Apple', 0.333, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.999, places=5)

    def test_apply_discount_zero(self):
        self.assertEqual(self.calc.apply_discount(100, 0.0), 100.0)

    def test_apply_discount_half(self):
        self.assertEqual(self.calc.apply_discount(80, 0.5), 40.0)

    def test_apply_discount_full(self):
        self.assertEqual(self.calc.apply_discount(30, 1.0), 0.0)

    def test_apply_discount_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, '0.1')

    def test_apply_discount_out_of_range(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, 1.2)

    def test_apply_discount_subtotal_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)

    def test_apply_discount_subtotal_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-5, 0.1)

    def test_apply_discount_high_precision(self):
        result = self.calc.apply_discount(0.123456, 0.333333)
        self.assertAlmostEqual(result, 0.082304, places=5)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150), 0.0)

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(80), 10.0)

    def test_calculate_shipping_custom_thresholds(self):
        calc = OrderCalculator(free_shipping_threshold=50, shipping_cost=7)
        self.assertEqual(calc.calculate_shipping(60), 0.0)
        self.assertEqual(calc.calculate_shipping(40), 7)

    def test_calculate_shipping_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping(['100'])

    def test_calculate_shipping_exact_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100), 0.0)

    def test_calculate_tax_positive_amount(self):
        self.assertEqual(self.calc.calculate_tax(200), 46.0)

    def test_calculate_tax_zero_amount(self):
        self.assertEqual(self.calc.calculate_tax(0), 0.0)

    def test_calculate_tax_custom_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(123), 0.0)

    def test_calculate_tax_custom_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.calculate_tax(45), 45.0)

    def test_calculate_tax_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10)

    def test_calculate_total_standard_no_discount(self):
        self.calc.add_item('Apple', 10, 2)
        self.calc.add_item('Banana', 20, 1)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 61.5, places=5)

    def test_calculate_total_discount_free_shipping(self):
        self.calc.add_item('Item', 200, 1)
        total = self.calc.calculate_total(discount=0.5)
        self.assertAlmostEqual(total, 123.0, places=5)

    def test_calculate_total_full_discount(self):
        self.calc.add_item('Item', 50, 1)
        total = self.calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 12.3, places=5)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_discount_type_error(self):
        self.calc.add_item('Apple', 10, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=['0.1'])

    def test_calculate_total_discount_out_of_range(self):
        self.calc.add_item('Apple', 10, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.2)

    def test_calculate_total_negative_subtotal(self):
        self.calc.add_item('Apple', 10, 1)
        with patch.object(OrderCalculator, 'get_subtotal', return_value=-5):
            with self.assertRaises(ValueError):
                self.calc.calculate_total()

    def test_calculate_total_custom_parameters(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=5)
        calc.add_item('A', 30, 2)
        total = calc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 48 + 5 + 5.3, places=5)

    def test_total_items_basic(self):
        self.calc.add_item('Apple', 1, 2)
        self.calc.add_item('Banana', 1, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_merged_quantities(self):
        self.calc.add_item('Apple', 1, 2)
        self.calc.add_item('Apple', 1, 4)
        self.assertEqual(self.calc.total_items(), 6)

    def test_total_items_after_clearing(self):
        self.calc.add_item('Apple', 1, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_no_items(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_non_empty(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.add_item('Banana', 2, 2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.items, [])
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.list_items(), [])

    def test_clear_order_already_empty(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items_distinct_names(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.add_item('Banana', 1, 1)
        self.calc.add_item('Orange', 1, 1)
        self.assertEqual(set(self.calc.list_items()), {'Apple', 'Banana', 'Orange'})

    def test_list_items_duplicate_name(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.add_item('Apple', 1, 2)
        self.assertEqual(self.calc.list_items(), ['Apple'])

    def test_list_items_after_clearing(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_fresh(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_adding(self):
        self.calc.add_item('Apple', 1, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_removing_only(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_clearing(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_integration_full_lifecycle(self):
        self.calc.add_item('Apple', 10, 2)
        self.calc.add_item('Banana', 5, 3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertEqual(set(self.calc.list_items()), {'Apple', 'Banana'})
        subtotal = self.calc.get_subtotal()
        self.assertAlmostEqual(subtotal, 35.0, places=5)
        total = self.calc.calculate_total(discount=0.1)
        self.assertAlmostEqual(total, 35 * 0.9 + 10 + (35 * 0.9 + 10) * 0.23, places=5)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.total_items(), 3)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_integration_add_remove_readd_different_price(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.remove_item('Apple')
        self.calc.add_item('Apple', 2.0, 1)
        self.assertEqual(self.calc.items[0]['price'], 2.0)

    def test_add_item_extremely_large_price(self):
        self.calc.add_item('Gold', 1000000000.0, 1)
        self.assertEqual(self.calc.items[0]['price'], 1000000000.0)
        self.assertEqual(self.calc.get_subtotal(), 1000000000.0)

    def test_apply_discount_many_decimals(self):
        result = self.calc.apply_discount(100, 0.3333333333)
        self.assertAlmostEqual(result, 66.66666667, places=5)

    def test_calculate_shipping_negative_subtotal(self):
        self.assertEqual(self.calc.calculate_shipping(-10), 10.0)

    def test_calculate_total_discount_zero_shipping_free(self):
        self.calc.add_item('Item', 120, 1)
        total = self.calc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 120 + 120 * 0.23, places=5)

    def test_calculate_total_discount_zero_shipping_applied(self):
        self.calc.add_item('Item', 80, 1)
        total = self.calc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 80 + 10 + (80 + 10) * 0.23, places=5)

    def test_remove_item_case_sensitivity(self):
        self.calc.add_item('Apple', 1, 1)
        with self.assertRaises(ValueError):
            self.calc.remove_item('apple')

    def test_add_item_whitespace_name(self):
        self.calc.add_item('  ', 1, 1)
        self.assertEqual(self.calc.items[0]['name'], '  ')

    def test_add_item_long_name(self):
        long_name = 'x' * 10000
        self.calc.add_item(long_name, 1, 1)
        self.assertEqual(self.calc.items[0]['name'], long_name)

    def test_list_items_order_independence(self):
        self.calc.add_item('Banana', 1, 1)
        self.calc.add_item('Apple', 1, 1)
        self.assertEqual(set(self.calc.list_items()), {'Apple', 'Banana'})

    def test_calculate_total_monkeypatched_shipping(self):
        self.calc.add_item('Item', 100, 1)
        with patch.object(OrderCalculator, 'calculate_shipping', return_value=99.9):
            total = self.calc.calculate_total()
            expected = 100 + 99.9 + (100 + 99.9) * 0.23
            self.assertAlmostEqual(total, expected, places=5)