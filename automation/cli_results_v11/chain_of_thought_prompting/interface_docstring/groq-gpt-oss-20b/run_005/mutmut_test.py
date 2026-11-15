import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_parameters(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom_parameters(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_out_of_range_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_out_of_range_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='high')

    def test_init_free_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_free_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='cheap')

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='free')

    def test_add_item_basic(self):
        self.calc.add_item('Apple', 1.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertEqual(self.calc.list_items(), ['Apple'])

    def test_add_item_with_quantity(self):
        self.calc.add_item('Banana', 0.8, quantity=3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertEqual(set(self.calc.list_items()), {'Banana'})

    def test_add_item_merge_same_name_price(self):
        self.calc.add_item('Orange', 0.9)
        self.calc.add_item('Orange', 0.9, quantity=2)
        self.assertEqual(self.calc.total_items(), 3)

    def test_add_item_error_same_name_diff_price(self):
        self.calc.add_item('Grape', 1.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Grape', 1.2)

    def test_add_item_error_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0)

    def test_add_item_error_price_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', 0.0)

    def test_add_item_error_price_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', -0.5)

    def test_add_item_error_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', 1.0, quantity=0)

    def test_add_item_error_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', 1.0, quantity=-3)

    def test_add_item_type_error_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_type_error_price(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Pear', 'cheap')

    def test_add_item_type_error_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Pear', 1.0, quantity=1.5)

    def test_remove_item_existing(self):
        self.calc.add_item('Mango', 2.0)
        self.calc.remove_item('Mango')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Papaya')

    def test_remove_item_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(42)

    def test_get_subtotal_single_item(self):
        self.calc.add_item('Tea', 3.0, quantity=2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('Tea', 3.0, quantity=2)
        self.calc.add_item('Coffee', 4.0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10.0)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_no_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_half_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(80.0, 0.5), 40.0)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.2)

    def test_apply_discount_discount_out_of_range_low(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -0.1)

    def test_apply_discount_discount_out_of_range_high(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, 1.2)

    def test_apply_discount_type_error_subtotal(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('fifty', 0.2)

    def test_apply_discount_type_error_discount(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(50.0, 'twenty')

    def test_calculate_shipping_free(self):
        calc = OrderCalculator(free_shipping_threshold=50.0)
        self.assertAlmostEqual(calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_paid(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=7.5)
        self.assertAlmostEqual(calc.calculate_shipping(30.0), 7.5)

    def test_calculate_shipping_exact_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0)
        self.assertAlmostEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertAlmostEqual(calc.calculate_shipping(0.0), 0.0)

    def test_calculate_shipping_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('cheap')

    def test_calculate_tax_basic(self):
        calc = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(calc.calculate_tax(200.0), 20.0)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('ten')

    def test_calculate_total_no_discount(self):
        self.calc.add_item('Book', 30.0)
        expected = 30.0 + 10.0 + 0.23 * 40.0
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_full_discount(self):
        self.calc.add_item('Pen', 5.0)
        expected = 10.0 + 0.23 * 10.0
        self.assertAlmostEqual(self.calc.calculate_total(discount=1.0), expected)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_invalid_discount_low(self):
        self.calc.add_item('Pen', 5.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)

    def test_calculate_total_invalid_discount_high(self):
        self.calc.add_item('Pen', 5.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.2)

    def test_calculate_total_type_error(self):
        self.calc.add_item('Pen', 5.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='half')

    def test_total_items_single(self):
        self.calc.add_item('Apple', 1.0, quantity=3)
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_multiple(self):
        self.calc.add_item('Apple', 1.0, quantity=3)
        self.calc.add_item('Banana', 0.5, quantity=2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_clear(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_removes_all_items(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Banana', 0.5)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_unique_names(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Apple', 1.0, quantity=2)
        self.calc.add_item('Banana', 0.5)
        self.assertEqual(set(self.calc.list_items()), {'Apple', 'Banana'})

    def test_list_items_after_clear(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('Apple', 1.0)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_add_item_edge_large_quantity(self):
        self.calc.add_item('Mega', 1.0, quantity=10 ** 6)
        self.assertEqual(self.calc.total_items(), 10 ** 6)

    def test_add_item_edge_small_price(self):
        self.calc.add_item('Tiny', 1e-09, quantity=1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1e-09)

    def test_calculate_shipping_edge_threshold_equal(self):
        calc = OrderCalculator(free_shipping_threshold=50.0)
        self.assertAlmostEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_tax_edge_bounds(self):
        calc0 = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc0.calculate_tax(100.0), 0.0)
        calc1 = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc1.calculate_tax(100.0), 100.0)

    def test_add_item_integration_sequence(self):
        self.calc.add_item('A', 1.0)
        self.calc.add_item('B', 2.0)
        self.calc.add_item('C', 3.0)
        self.calc.remove_item('B')
        self.assertEqual(set(self.calc.list_items()), {'A', 'C'})
        self.assertEqual(self.calc.total_items(), 2)

    def test_calculate_total_edge_threshold_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item('Item', 30.0)
        expected = 39.36
        self.assertAlmostEqual(calc.calculate_total(discount=0.1), expected)

    def test_list_items_integration_many(self):
        for i in range(10):
            self.calc.add_item(f'Item{i}', 1.0)
        self.assertEqual(set(self.calc.list_items()), {f'Item{i}' for i in range(10)})

    def test_total_items_integration_updates(self):
        self.calc.add_item('A', 1.0, quantity=2)
        self.calc.add_item('B', 1.0, quantity=3)
        self.calc.remove_item('A')
        self.assertEqual(self.calc.total_items(), 3)

    def test_calculate_total_tax_application_order(self):
        calc = OrderCalculator(tax_rate=0.2, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('X', 50.0)
        expected = 42.0
        self.assertAlmostEqual(calc.calculate_total(discount=0.5), expected)

    def test_add_item_integration_merge_quantity(self):
        self.calc.add_item('Same', 5.0)
        self.calc.add_item('Same', 5.0, quantity=4)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_integration_type_error_quantity_string(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Same', 5.0, quantity='3')

    def test_calculate_total_custom_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=20.0)
        calc.add_item('Item', 80.0)
        expected = 123.0
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_internal_call_order(self):
        calc = OrderCalculator(tax_rate=0.2, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('X', 50.0)
        expected = 42.0
        self.assertAlmostEqual(calc.calculate_total(discount=0.5), expected)

    def test_clear_order_integration(self):
        self.calc.add_item('A', 1.0)
        self.calc.clear_order()
        self.calc.add_item('B', 2.0)
        self.assertEqual(set(self.calc.list_items()), {'B'})
        self.assertEqual(self.calc.total_items(), 1)

    def test_is_empty_after_clear_integration(self):
        self.calc.add_item('A', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])

    def test_add_item_edge_negative_quantity_float(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Item', 1.0, quantity=-1.0)

    def test_calculate_tax_edge_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_apply_discount_edge_exact_bounds(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.0), 100.0)
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_edge_zero_subtotal(self):
        self.assertAlmostEqual(self.calc.apply_discount(0.0, 0.5), 0.0)

    def test_calculate_total_edge_discount_string(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.2')

    def test_calculate_total_edge_discount_precision(self):
        self.calc.add_item('Item', 100.0)
        expected = 94.300041
        self.assertAlmostEqual(self.calc.calculate_total(discount=0.333333), expected, places=5)

    def test_calculate_total_edge_float_precision(self):
        self.calc.add_item('Item', 0.1)
        expected = 0.1 + 10.0 + 0.23 * 10.1
        self.assertAlmostEqual(self.calc.calculate_total(), expected, places=5)

    def test_list_items_edge_case_insensitive(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('apple', 1.0)
        self.assertEqual(set(self.calc.list_items()), {'Apple', 'apple'})

    def test_list_items_edge_whitespace_identical(self):
        self.calc.add_item('Item', 1.0)
        self.calc.add_item('Item ', 1.0)
        self.assertEqual(set(self.calc.list_items()), {'Item', 'Item '})

    def test_total_items_edge_remove_all(self):
        self.calc.add_item('A', 1.0, quantity=1)
        self.calc.remove_item('A')
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_edge_large_quantities(self):
        self.calc.add_item('Large', 1.0, quantity=10 ** 9)
        self.assertEqual(self.calc.total_items(), 10 ** 9)

    def test_calculate_total_edge_small_subtotal(self):
        self.calc.add_item('Tiny', 1e-12)
        expected = 1e-12 + 10.0 + 0.23 * (10.0 + 1e-12)
        self.assertAlmostEqual(self.calc.calculate_total(), expected, places=12)

    def test_calculate_total_edge_negative_subtotal_defensive(self):

        class Dummy(OrderCalculator):

            def get_subtotal(self):
                return -1
        dummy = Dummy()
        dummy.add_item('Item', 1.0)
        with self.assertRaises(ValueError):
            dummy.calculate_total()

    def test_add_item_edge_many_decimals(self):
        self.calc.add_item('Precise', 1.23456789)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.23456789, places=8)

    def test_add_item_edge_string_price(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('StrPrice', '1.5')

    def test_remove_item_edge_quantity_gt1(self):
        self.calc.add_item('Multi', 2.0, quantity=5)
        self.calc.remove_item('Multi')
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
if __name__ == '__main__':
    unittest.main()