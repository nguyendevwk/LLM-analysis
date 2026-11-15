import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    # 1
    def test_init_default(self):
        order = OrderCalculator()
        self.assertEqual(order.tax_rate, 0.23)
        self.assertEqual(order.free_shipping_threshold, 100.0)
        self.assertEqual(order.shipping_cost, 10.0)
        self.assertTrue(order.is_empty())

    # 2
    def test_init_custom_valid(self):
        order = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(order.tax_rate, 0.1)
        self.assertEqual(order.free_shipping_threshold, 50.0)
        self.assertEqual(order.shipping_cost, 5.0)

    # 3
    def test_init_tax_rate_zero(self):
        order = OrderCalculator(tax_rate=0.0)
        self.assertEqual(order.tax_rate, 0.0)

    # 4
    def test_init_tax_rate_one(self):
        order = OrderCalculator(tax_rate=1.0)
        self.assertEqual(order.tax_rate, 1.0)

    # 5
    def test_init_free_shipping_threshold_zero(self):
        order = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(order.free_shipping_threshold, 0.0)

    # 6
    def test_init_shipping_cost_zero(self):
        order = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(order.shipping_cost, 0.0)

    # 7
    def test_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    # 8
    def test_init_tax_rate_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    # 9
    def test_init_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    # 10
    def test_init_free_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    # 11
    def test_init_free_shipping_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    # 12
    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    # 13
    def test_init_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    # 14
    def test_add_item_basic(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0, 1)
        self.assertEqual(order.total_items(), 1)
        self.assertIn('Apple', order.list_items())

    # 15
    def test_add_item_default_quantity(self):
        order = OrderCalculator()
        order.add_item('Banana', 2.0)
        self.assertEqual(order.total_items(), 1)

    # 16
    def test_add_item_large_quantity(self):
        order = OrderCalculator()
        order.add_item('Orange', 3.0, 1000)
        self.assertEqual(order.total_items(), 1000)

    # 17
    def test_add_item_increment_same(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0, 2)
        order.add_item('Apple', 1.0, 3)
        self.assertEqual(order.total_items(), 5)

    # 18
    def test_add_item_duplicate_different_price(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        with self.assertRaises(ValueError):
            order.add_item('Apple', 1.5)

    # 19
    def test_add_item_empty_name(self):
        order = OrderCalculator()
        with self.assertRaises(ValueError):
            order.add_item('', 1.0)

    # 20
    def test_add_item_zero_price(self):
        order = OrderCalculator()
        with self.assertRaises(ValueError):
            order.add_item('Apple', 0)

    # 21
    def test_add_item_negative_price(self):
        order = OrderCalculator()
        with self.assertRaises(ValueError):
            order.add_item('Apple', -5)

    # 22
    def test_add_item_zero_quantity(self):
        order = OrderCalculator()
        with self.assertRaises(ValueError):
            order.add_item('Apple', 1.0, 0)

    # 23
    def test_add_item_negative_quantity(self):
        order = OrderCalculator()
        with self.assertRaises(ValueError):
            order.add_item('Apple', 1.0, -2)

    # 24
    def test_add_item_name_type(self):
        order = OrderCalculator()
        with self.assertRaises(TypeError):
            order.add_item(123, 1.0)

    # 25
    def test_add_item_price_type(self):
        order = OrderCalculator()
        with self.assertRaises(TypeError):
            order.add_item('Apple', '1.0')

    # 26
    def test_add_item_quantity_type(self):
        order = OrderCalculator()
        with self.assertRaises(TypeError):
            order.add_item('Apple', 1.0, '2')

    # 27
    def test_add_item_none_name(self):
        order = OrderCalculator()
        with self.assertRaises(TypeError):
            order.add_item(None, 1.0)

    # 28
    def test_add_item_none_price(self):
        order = OrderCalculator()
        with self.assertRaises(TypeError):
            order.add_item('Apple', None)

    # 29
    def test_add_item_none_quantity(self):
        order = OrderCalculator()
        with self.assertRaises(TypeError):
            order.add_item('Apple', 1.0, None)

    # 30
    def test_remove_existing_item(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        order.remove_item('Apple')
        self.assertTrue(order.is_empty())

    # 31
    def test_remove_nonexistent_item(self):
        order = OrderCalculator()
        with self.assertRaises(ValueError):
            order.remove_item('Pear')

    # 32
    def test_remove_from_empty_order(self):
        order = OrderCalculator()
        with self.assertRaises(ValueError):
            order.remove_item('Apple')

    # 33
    def test_remove_name_type(self):
        order = OrderCalculator()
        with self.assertRaises(TypeError):
            order.remove_item(123)

    # 34
    def test_remove_name_none(self):
        order = OrderCalculator()
        with self.assertRaises(TypeError):
            order.remove_item(None)

    # 35
    def test_get_subtotal_single_item(self):
        order = OrderCalculator()
        order.add_item('Apple', 2.0, 3)
        self.assertAlmostEqual(order.get_subtotal(), 6.0, places=2)

    # 36
    def test_get_subtotal_multiple_items(self):
        order = OrderCalculator()
        order.add_item('Apple', 2.0, 3)
        order.add_item('Banana', 1.5, 2)
        self.assertAlmostEqual(order.get_subtotal(), 9.0, places=2)

    # 37
    def test_get_subtotal_after_clear(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        order.clear_order()
        with self.assertRaises(ValueError):
            order.get_subtotal()

    # 38
    def test_get_subtotal_type(self):
        order = OrderCalculator()
        with self.assertRaises(ValueError):
            order.get_subtotal()

    # 39
    def test_apply_discount_no_discount(self):
        order = OrderCalculator()
        self.assertAlmostEqual(order.apply_discount(100, 0.0), 100.0, places=2)

    # 40
    def test_apply_discount_full_discount(self):
        order = OrderCalculator()
        self.assertAlmostEqual(order.apply_discount(100, 1.0), 0.0, places=2)

    # 41
    def test_apply_discount_half(self):
        order = OrderCalculator()
        self.assertAlmostEqual(order.apply_discount(80, 0.5), 40.0, places=2)

    # 42
    def test_apply_discount_negative_subtotal(self):
        order = OrderCalculator()
        with self.assertRaises(ValueError):
            order.apply_discount(-10, 0.2)

    # 43
    def test_apply_discount_discount_out_of_range_low(self):
        order = OrderCalculator()
        with self.assertRaises(ValueError):
            order.apply_discount(100, -0.1)

    # 44
    def test_apply_discount_discount_out_of_range_high(self):
        order = OrderCalculator()
        with self.assertRaises(ValueError):
            order.apply_discount(100, 1.1)

    # 45
    def test_apply_discount_subtotal_type(self):
        order = OrderCalculator()
        with self.assertRaises(TypeError):
            order.apply_discount('100', 0.2)

    # 46
    def test_apply_discount_discount_type(self):
        order = OrderCalculator()
        with self.assertRaises(TypeError):
            order.apply_discount(100, '0.2')

    # 47
    def test_calculate_shipping_free_above_threshold(self):
        order = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(order.calculate_shipping(120), 0.0, places=2)

    # 48
    def test_calculate_shipping_paid_below_threshold(self):
        order = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(order.calculate_shipping(80), 10.0, places=2)

    # 49
    def test_calculate_shipping_exact_threshold(self):
        order = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(order.calculate_shipping(100), 0.0, places=2)

    # 50
    def test_calculate_shipping_zero_threshold(self):
        order = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertAlmostEqual(order.calculate_shipping(50), 0.0, places=2)

    # 51
    def test_calculate_shipping_zero_shipping_cost(self):
        order = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=0.0)
        self.assertAlmostEqual(order.calculate_shipping(80), 0.0, places=2)

    # 52
    def test_calculate_shipping_type_error(self):
        order = OrderCalculator()
        with self.assertRaises(TypeError):
            order.calculate_shipping('abc')

    # 53
    def test_calculate_shipping_negative_subtotal(self):
        order = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(order.calculate_shipping(-5), 10.0, places=2)

    # 54
    def test_calculate_tax_basic(self):
        order = OrderCalculator()
        self.assertAlmostEqual(order.calculate_tax(100), 23.0, places=2)

    # 55
    def test_calculate_tax_zero_amount(self):
        order = OrderCalculator()
        self.assertAlmostEqual(order.calculate_tax(0), 0.0, places=2)

    # 56
    def test_calculate_tax_custom_rate(self):
        order = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(order.calculate_tax(200), 20.0, places=2)

    # 57
    def test_calculate_tax_negative_amount(self):
        order = OrderCalculator()
        with self.assertRaises(ValueError):
            order.calculate_tax(-10)

    # 58
    def test_calculate_tax_type_error(self):
        order = OrderCalculator()
        with self.assertRaises(TypeError):
            order.calculate_tax('100')

    # 59
    def test_calculate_total_basic_no_discount(self):
        order = OrderCalculator()
        order.add_item('Apple', 2.0, 3)
        total = order.calculate_total()
        self.assertAlmostEqual(total, 19.68, places=2)

    # 60
    def test_calculate_total_free_shipping(self):
        order = OrderCalculator()
        order.add_item('Apple', 10.0, 12)
        total = order.calculate_total()
        self.assertAlmostEqual(total, 147.6, places=2)

    # 61
    def test_calculate_total_with_discount(self):
        order = OrderCalculator()
        order.add_item('Apple', 10.0, 12)
        total = order.calculate_total(discount=0.5)
        self.assertAlmostEqual(total, 86.1, places=2)

    # 62
    def test_calculate_total_full_discount(self):
        order = OrderCalculator()
        order.add_item('Apple', 10.0, 12)
        total = order.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 12.3, places=2)

    # 63
    def test_calculate_total_discount_edge_cases(self):
        order = OrderCalculator()
        order.add_item('Apple', 10.0, 12)
        total_no = order.calculate_total(discount=0.0)
        total_full = order.calculate_total(discount=1.0)
        self.assertAlmostEqual(total_no, 147.6, places=2)
        self.assertAlmostEqual(total_full, 12.3, places=2)

    # 64
    def test_calculate_total_invalid_discount_low(self):
        order = OrderCalculator()
        order.add_item('Apple', 10.0, 12)
        with self.assertRaises(ValueError):
            order.calculate_total(discount=-0.1)

    # 65
    def test_calculate_total_invalid_discount_high(self):
        order = OrderCalculator()
        order.add_item('Apple', 10.0, 12)
        with self.assertRaises(ValueError):
            order.calculate_total(discount=1.1)

    # 66
    def test_calculate_total_type_error(self):
        order = OrderCalculator()
        order.add_item('Apple', 10.0, 12)
        with self.assertRaises(TypeError):
            order.calculate_total(discount='0.2')

    # 67
    def test_calculate_total_empty_order(self):
        order = OrderCalculator()
        with self.assertRaises(ValueError):
            order.calculate_total()

    # 68
    def test_calculate_total_custom_tax_rate(self):
        order = OrderCalculator(tax_rate=0.1)
        order.add_item('Apple', 10.0, 10)
        total = order.calculate_total()
        self.assertAlmostEqual(total, 121.0, places=2)

    # 69
    def test_calculate_total_custom_threshold(self):
        order = OrderCalculator(free_shipping_threshold=50.0)
        order.add_item('Apple', 10.0, 4)
        total = order.calculate_total()
        self.assertAlmostEqual(total, 61.5, places=2)

    # 70
    def test_calculate_total_custom_shipping_cost(self):
        order = OrderCalculator(shipping_cost=5.0)
        order.add_item('Apple', 10.0, 4)
        total = order.calculate_total()
        self.assertAlmostEqual(total, 55.35, places=2)

    # 71
    def test_total_items_single(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0, 3)
        self.assertEqual(order.total_items(), 3)

    # 72
    def test_total_items_multiple(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0, 3)
        order.add_item('Banana', 1.0, 2)
        self.assertEqual(order.total_items(), 5)

    # 73
    def test_total_items_after_clear(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0, 3)
        order.clear_order()
        self.assertEqual(order.total_items(), 0)

    # 74
    def test_total_items_empty(self):
        order = OrderCalculator()
        self.assertEqual(order.total_items(), 0)

    # 75
    def test_clear_order(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        order.clear_order()
        self.assertTrue(order.is_empty())

    # 76
    def test_clear_order_idempotent(self):
        order = OrderCalculator()
        order.clear_order()
        order.clear_order()
        self.assertTrue(order.is_empty())

    # 77
    def test_clear_order_state(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        order.clear_order()
        self.assertEqual(order.total_items(), 0)
        self.assertEqual(order.list_items(), [])

    # 78
    def test_list_items_single(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        self.assertEqual(order.list_items(), ['Apple'])

    # 79
    def test_list_items_multiple(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        order.add_item('Banana', 1.0)
        items = order.list_items()
        self.assertCountEqual(items, ['Apple', 'Banana'])

    # 80
    def test_list_items_duplicates(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        order.add_item('Apple', 1.0)
        self.assertEqual(order.list_items(), ['Apple'])

    # 81
    def test_list_items_after_remove(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        order.remove_item('Apple')
        self.assertEqual(order.list_items(), [])

    # 82
    def test_list_items_empty(self):
        order = OrderCalculator()
        self.assertEqual(order.list_items(), [])

    # 83
    def test_is_empty_initial(self):
        order = OrderCalculator()
        self.assertTrue(order.is_empty())

    # 84
    def test_is_empty_after_add(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        self.assertFalse(order.is_empty())

    # 85
    def test_is_empty_after_remove(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        order.remove_item('Apple')
        self.assertTrue(order.is_empty())

    # 86
    def test_is_empty_after_clear(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        order.clear_order()
        self.assertTrue(order.is_empty())

    # 87
    def test_cross_method_state_consistency(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0, 3)
        order.add_item('Banana', 2.0, 2)
        self.assertEqual(order.total_items(), 5)
        self.assertEqual(len(order.list_items()), 2)

    # 88
    def test_cross_method_order_of_operations(self):
        order = OrderCalculator(free_shipping_threshold=15.0, shipping_cost=10.0)
        order.add_item('Apple', 10.0, 2)
        order.add_item('Banana', 5.0, 1)
        total = order.calculate_total(discount=0.5)
        self.assertAlmostEqual(total, 27.68, places=2)

    # 89
    def test_cross_method_floating_point_accuracy(self):
        order = OrderCalculator()
        order.add_item('Apple', 10.0, 12)
        total = order.calculate_total()
        self.assertAlmostEqual(total, 147.6, places=2)

    # 90
    def test_cross_method_edge_threshold(self):
        order = OrderCalculator(free_shipping_threshold=50.0)
        order.add_item('Apple', 10.0, 5)
        total = order.calculate_total()
        self.assertAlmostEqual(total, 61.5, places=2)

    # 91
    def test_cross_method_edge_shipping_cost(self):
        order = OrderCalculator(shipping_cost=0.01, free_shipping_threshold=50.0)
        order.add_item('Apple', 10.0, 4)
        total = order.calculate_total()
        self.assertAlmostEqual(total, 49.2123, places=4)

    # 92
    def test_cross_method_edge_tax_rate_zero(self):
        order = OrderCalculator(tax_rate=0.0)
        order.add_item('Apple', 10.0, 10)
        total = order.calculate_total()
        self.assertAlmostEqual(total, 110.0, places=2)

    # 93
    def test_cross_method_edge_tax_rate_one(self):
        order = OrderCalculator(tax_rate=1.0)
        order.add_item('Apple', 10.0, 10)
        total = order.calculate_total()
        self.assertAlmostEqual(total, 210.0, places=2)

    # 94
    def test_cross_method_invalid_item_state(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        with self.assertRaises(ValueError):
            order.add_item('Apple', 1.5)

    # 95
    def test_cross_method_removal_of_nonexistent_item(self):
        order = OrderCalculator()
        order.clear_order()
        with self.assertRaises(ValueError):
            order.remove_item('Apple')

    # 96
    def test_cross_method_large_quantities(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0, 10000)
        self.assertEqual(order.total_items(), 10000)
        self.assertAlmostEqual(order.get_subtotal(), 10000.0, places=2)

    # 97
    def test_cross_method_large_prices(self):
        order = OrderCalculator()
        order.add_item('Apple', 1000000.0, 1)
        self.assertAlmostEqual(order.get_subtotal(), 1000000.0, places=2)
        self.assertAlmostEqual(order.calculate_tax(1000000.0), 230000.0, places=2)
        self.assertAlmostEqual(order.calculate_total(), 1230000.0, places=2)

    # 98
    def test_cross_method_mixed_types(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        order.add_item('apple', 1.0)
        items = order.list_items()
        self.assertCountEqual(items, ['Apple', 'apple'])

    # 99
    def test_cross_method_immutability_of_item_dict(self):
        order = OrderCalculator()
        order.add_item('Apple', 1.0)
        items = order.list_items()
        items.append('Banana')
        self.assertEqual(order.list_items(), ['Apple'])

    # 100
    def test_cross_method_idempotent_clear_order(self):
        order = OrderCalculator()
        order.clear_order()
        order.clear_order()
        self.assertTrue(order.is_empty())

if __name__ == '__main__':
    unittest.main()