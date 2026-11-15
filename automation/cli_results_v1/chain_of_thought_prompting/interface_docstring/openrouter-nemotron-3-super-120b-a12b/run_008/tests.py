import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=7.5)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 7.5)

    def test_init_boundary(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)
        calc2 = OrderCalculator(tax_rate=1.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc2.tax_rate, 1.0)

    def test_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_int_args(self):
        calc = OrderCalculator(tax_rate=0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_add_item_first(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(calc.list_items(), ['Apple'])
        self.assertEqual(calc.total_items(), 2)

    def test_add_item_second_distinct(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 0.5, 3)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})
        self.assertEqual(calc.total_items(), 4)

    def test_add_item_duplicate_increase_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        self.assertEqual(calc.total_items(), 1)

    def test_add_item_price_decimals(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.33333333, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 0.99999999)

    def test_add_item_large_quantity(self):
        calc = OrderCalculator()
        qty = 10 ** 9
        calc.add_item('Apple', 1.0, qty)
        self.assertEqual(calc.total_items(), qty)

    def test_add_item_empty_name_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    def test_add_item_name_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_price_nonpositive_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 0.0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', -1.0)

    def test_add_item_price_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', '1.0')

    def test_add_item_quantity_less_than_one_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, -5)

    def test_add_item_quantity_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, 1.5)
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, '2')

    def test_add_item_same_name_diff_price_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.5, 1)
        self.assertEqual(calc.total_items(), 1)

    def test_add_item_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.clear_order()
        calc.add_item('Banana', 2.0, 3)
        self.assertEqual(calc.list_items(), ['Banana'])
        self.assertEqual(calc.total_items(), 3)

    def test_remove_item_existing_qty1(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_remove_item_existing_qty_gt1(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 5)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_remove_item_missing_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            calc.remove_item('Banana')

    def test_remove_item_name_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_from_empty_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Apple')

    def test_remove_item_twice_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        with self.assertRaises(ValueError):
            calc.remove_item('Apple')

    def test_remove_then_add_same_name_same_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.remove_item('Apple')
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.total_items(), 3)

    def test_remove_then_add_same_name_diff_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.remove_item('Apple')
        calc.add_item('Apple', 1.5, 1)
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 1.5)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.5, 4)
        self.assertAlmostEqual(calc.get_subtotal(), 10.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 2)
        calc.add_item('Banana', 3.0, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 13.0)

    def test_get_subtotal_fractional_prices(self):
        calc = OrderCalculator()
        calc.add_item('A', 0.1, 5)
        calc.add_item('B', 0.3, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 1.1)

    def test_get_subtotal_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('A', 1000000.0, 2)
        calc.add_item('B', 2000000.0, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 8000000.0)

    def test_get_subtotal_empty_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_after_clear_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_twenty_percent(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_subtotal_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_negative_subtotal_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_negative_discount_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)

    def test_apply_discount_over_one_discount_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.2)

    def test_apply_discount_subtotal_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_discount_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.1')

    def test_apply_discount_int_args(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100, 10), -900.0)
        self.assertAlmostEqual(calc.apply_discount(100, 0), 100.0)
        self.assertAlmostEqual(calc.apply_discount(100, 1), 0.0)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_at_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_zero_subtotal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(-10.0), 10.0)

    def test_calculate_shipping_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('50')

    def test_calculate_shipping_int_arg(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(80), 10.0)

    def test_calculate_shipping_custom_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(30.0), 5.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)
        self.assertEqual(calc.calculate_shipping(70.0), 0.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_normal_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_full_rate(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.calculate_tax(100.0), 100.0)

    def test_calculate_tax_negative_amount_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_calculate_tax_int_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100), 23.0)

    def test_calculate_total_empty_order_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_single_item_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('Book', 50.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 73.8)

    def test_calculate_total_single_item_discount(self):
        calc = OrderCalculator()
        calc.add_item('Book', 50.0, 1)
        self.assertAlmostEqual(calc.calculate_total(0.1), 67.65)

    def test_calculate_total_multiple_items_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('A', 60.0, 1)
        calc.add_item('B', 60.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 147.6)

    def test_calculate_total_discount_affects_shipping(self):
        calc = OrderCalculator()
        calc.add_item('A', 70.0, 1)
        calc.add_item('B', 40.0, 1)
        self.assertAlmostEqual(calc.calculate_total(0.1), 134.07)

    def test_calculate_total_discount_full(self):
        calc = OrderCalculator()
        calc.add_item('Item', 50.0, 1)
        self.assertAlmostEqual(calc.calculate_total(1.0), 12.3)

    def test_calculate_total_tax_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Item', 50.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 60.0)

    def test_calculate_total_shipping_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Item', 50.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 61.5)

    def test_calculate_total_negative_discount_error(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)

    def test_calculate_total_over_one_discount_error(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.2)

    def test_calculate_total_discount_type_error(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total('0.1')

    def test_calculate_total_int_discount(self):
        calc = OrderCalculator()
        calc.add_item('Item', 100.0, 1)
        self.assertAlmostEqual(calc.calculate_total(0), 135.3)
        self.assertAlmostEqual(calc.calculate_total(1), 12.3)

    def test_calculate_total_after_clear_error(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_after_remove_all_error(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 2)
        calc.remove_item('Item')
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_one_item_qty1(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        self.assertEqual(calc.total_items(), 1)

    def test_total_items_one_item_qty_n(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 7)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 10 ** 9)
        self.assertEqual(calc.total_items(), 10 ** 9)

    def test_total_items_add_remove_cycle(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 3)
        calc.add_item('B', 1.0, 2)
        self.assertEqual(calc.total_items(), 5)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 2)
        calc.remove_item('B')
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 5)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_on_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_on_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_clear_order_then_add(self):
        calc = OrderCalculator()
        calc.add_item('Old', 1.0, 1)
        calc.clear_order()
        calc.add_item('New', 2.0, 3)
        self.assertEqual(calc.list_items(), ['New'])
        self.assertEqual(calc.total_items(), 3)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_one_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_two_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 1)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})

    def test_list_items_duplicate_name(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_after_remove(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 1)
        calc.remove_item('Apple')
        self.assertEqual(calc.list_items(), ['Banana'])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_return_copy(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        lst = calc.list_items()
        lst.append('Banana')
        self.assertNotIn('Banana', calc.list_items())

    def test_is_empty_true(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_after_add(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_true_after_remove_last(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.remove_item('Item')
        self.assertTrue(calc.is_empty())

    def test_is_empty_true_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_after_multiple_adds_same_name(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 2)
        calc.add_item('Item', 1.0, 3)
        self.assertFalse(calc.is_empty())