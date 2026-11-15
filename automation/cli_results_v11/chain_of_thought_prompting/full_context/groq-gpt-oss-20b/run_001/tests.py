import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    # 1
    def test_init_default_parameters(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    # 2
    def test_init_custom_parameters(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    # 3
    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='a')

    # 4
    def test_init_invalid_tax_rate_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    # 5
    def test_init_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='b')

    # 6
    def test_init_invalid_free_shipping_threshold_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    # 7
    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='c')

    # 8
    def test_init_invalid_shipping_cost_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    # 9
    def test_add_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 2)

    # 10
    def test_add_multiple_items_different_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Banana', 2.0)
        self.assertEqual(len(calc.items), 2)
        names = {item['name'] for item in calc.items}
        self.assertSetEqual(names, {'Apple', 'Banana'})

    # 11
    def test_add_duplicate_item_same_name_and_price_increments_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 5)

    # 12
    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        self.assertEqual(calc.items[0]['quantity'], 1)

    # 13
    def test_add_item_with_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    # 14
    def test_add_item_with_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    # 15
    def test_add_item_with_non_number_price(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 'price')

    # 16
    def test_add_item_with_non_int_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, 1.5)

    # 17
    def test_add_item_with_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, 0)

    # 18
    def test_add_item_with_negative_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', -1.0)

    # 19
    def test_add_item_same_name_different_price_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 2.0)

    # 20
    def test_remove_existing_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    # 21
    def test_remove_nonexistent_item_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Banana')

    # 22
    def test_remove_item_with_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    # 23
    def test_get_subtotal_with_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 2.0)
        self.assertAlmostEqual(calc.get_subtotal(), 4.0)

    # 24
    def test_get_subtotal_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    # 25
    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)

    # 26
    def test_apply_discount_zero_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    # 27
    def test_apply_discount_full_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 1.0), 0.0)

    # 28
    def test_apply_discount_negative_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.2)

    # 29
    def test_apply_discount_invalid_discount_value(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.5)

    # 30
    def test_apply_discount_invalid_subtotal_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('subtotal', 0.2)

    # 31
    def test_apply_discount_invalid_discount_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, 'discount')

    # 32
    def test_calculate_shipping_free_when_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(120.0), 0.0)

    # 33
    def test_calculate_shipping_non_free_when_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(80.0), 10.0)

    # 34
    def test_calculate_shipping_exact_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    # 35
    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(-10.0), 10.0)

    # 36
    def test_calculate_shipping_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('subtotal')

    # 37
    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    # 38
    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    # 39
    def test_calculate_tax_negative_amount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    # 40
    def test_calculate_tax_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('amount')

    # 41
    def test_calculate_total_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 2.0)
        expected = 4.0 + 10.0 + 0.23 * 14.0
        self.assertAlmostEqual(calc.calculate_total(), expected)

    # 42
    def test_calculate_total_with_discount(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 2.0)
        expected = 3.2 + 10.0 + 0.23 * 13.2
        self.assertAlmostEqual(calc.calculate_total(0.2), expected)

    # 43
    def test_calculate_total_with_full_discount_and_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        self.assertAlmostEqual(calc.calculate_total(1.0), 0.0)

    # 44
    def test_calculate_total_with_full_discount_and_non_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=200.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 0.0 + 10.0 + 0.23 * 10.0
        self.assertAlmostEqual(calc.calculate_total(1.0), expected)

    # 45
    def test_calculate_total_discount_boundary_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Apple', 2.0, 100)
        expected = 100.0 + 0.0 + 0.23 * 100.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    # 46
    def test_calculate_total_invalid_discount_type(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        with self.assertRaises(TypeError):
            calc.calculate_total('discount')

    # 47
    def test_calculate_total_invalid_discount_value(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.5)

    # 48
    def test_calculate_total_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    # 49
    def test_total_items_multiple_quantities(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        calc.add_item('Banana', 2.0, 2)
        self.assertEqual(calc.total_items(), 5)

    # 50
    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    # 51
    def test_clear_order_resets_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    # 52
    def test_list_items_unique_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(set(calc.list_items()), {'Apple'})

    # 53
    def test_list_items_multiple_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Banana', 2.0)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})

    # 54
    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    # 55
    def test_is_empty_initially(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    # 56
    def test_is_empty_after_adding(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        self.assertFalse(calc.is_empty())

    # 57
    def test_is_empty_after_clearing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    # 58
    def test_total_items_after_adding(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        calc.add_item('Banana', 2.0, 2)
        self.assertEqual(calc.total_items(), 5)

    # 59
    def test_total_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        calc.remove_item('Apple')
        self.assertEqual(calc.total_items(), 0)

    # 60
    def test_list_items_after_clearing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    # 61
    def test_list_items_after_adding(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Banana', 2.0)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})

    # 62
    def test_add_same_name_same_price_increments_and_different_price_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.items[0]['quantity'], 5)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 2.0)

    # 63
    def test_calculate_total_with_multiple_items_and_discount(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 2.0)
        expected = 2.8 + 10.0 + 0.23 * 12.8
        self.assertAlmostEqual(calc.calculate_total(0.3), expected)

    # 64
    def test_calculate_total_with_zero_shipping_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 2.0 + 0.0 + 0.23 * 2.0
        self.assertAlmostEqual(calc.calculate_total(), expected)

    # 65
    def test_calculate_total_with_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 2.0 + 0.0 + 0.23 * 2.0
        self.assertAlmostEqual(calc.calculate_total(), expected)

    # 66
    def test_calculate_total_with_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 2.0 + 10.0 + 0.0
        self.assertAlmostEqual(calc.calculate_total(), expected)

    # 67
    def test_calculate_total_with_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 2.0 + 10.0 + 12.0
        self.assertAlmostEqual(calc.calculate_total(), expected)

    # 68
    def test_calculate_total_with_discount_half_and_zero_shipping(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 1.0 + 0.0 + 0.23 * 1.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    # 69
    def test_calculate_total_with_discount_half_and_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        expected = 1.0 + 10.0 + 0.23 * 11.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    # 70
    def test_calculate_total_with_discount_half_and_threshold_200(self):
        calc = OrderCalculator(free_shipping_threshold=200.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 200)
        expected = 100.0 + 0.0 + 0.23 * 100.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    # 71
    def test_calculate_total_with_discount_half_and_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 200)
        expected = 100.0 + 0.0 + 0.23 * 100.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    # 72
    def test_calculate_total_with_discount_half_and_zero_shipping(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 200)
        expected = 100.0 + 0.0 + 0.23 * 100.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    # 73
    def test_calculate_total_with_discount_half_and_zero_tax(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Apple', 1.0, 200)
        expected = 100.0 + 10.0 + 0.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    # 74
    def test_tax_rate_boundary_values(self):
        calc_zero = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc_zero.calculate_tax(100.0), 0.0)
        calc_one = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc_one.calculate_tax(100.0), 100.0)

    # 75
    def test_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(calc.calculate_shipping(2.0), 0.0)

    # 76
    def test_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(calc.calculate_shipping(2.0), 0.0)

    # 77
    def test_add_item_price_integer(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 2, 1)
        self.assertEqual(calc.items[0]['price'], 2)

    # 78
    def test_add_item_price_float(self):
        calc = OrderCalculator()
        calc.add_item('Orange', 1.5, 1)
        self.assertAlmostEqual(calc.items[0]['price'], 1.5)

    # 79
    def test_add_item_quantity_integer(self):
        calc = OrderCalculator()
        calc.add_item('Grape', 0.5, 3)
        self.assertEqual(calc.items[0]['quantity'], 3)

    # 80
    def test_add_item_quantity_default(self):
        calc = OrderCalculator()
        calc.add_item('Pear', 0.8)
        self.assertEqual(calc.items[0]['quantity'], 1)

    # 81
    def test_remove_item_multiple_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    # 82
    def test_list_items_order_independent(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Banana', 2.0)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})

    # 83
    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(-10.0), 10.0)

    # 84
    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    # 85
    def test_calculate_total_discount_zero_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 2.0 + 0.0 + 0.23 * 2.0
        self.assertAlmostEqual(calc.calculate_total(0.0), expected)

    # 86
    def test_calculate_total_discount_full_zero_shipping(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 2)
        self.assertAlmostEqual(calc.calculate_total(1.0), 0.0)

    # 87
    def test_calculate_total_discount_full_zero_tax(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 0.0 + 10.0 + 0.0
        self.assertAlmostEqual(calc.calculate_total(1.0), expected)

    # 88
    def test_calculate_total_discount_full_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        self.assertAlmostEqual(calc.calculate_total(1.0), 0.0)

    # 89
    def test_calculate_total_discount_half_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 1.0 + 0.0 + 0.23 * 1.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    # 90
    def test_calculate_total_discount_half_zero_shipping(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 1.0 + 0.0 + 0.23 * 1.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    # 91
    def test_calculate_total_discount_half_zero_tax(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 1.0 + 10.0 + 0.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    # 92
    def test_calculate_total_discount_half_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 1.0 + 10.0 + 11.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

if __name__ == '__main__':
    unittest.main()