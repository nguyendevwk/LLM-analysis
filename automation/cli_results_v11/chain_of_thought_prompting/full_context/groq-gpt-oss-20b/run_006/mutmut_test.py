import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(calc.tax_rate, 0.15)
        self.assertEqual(calc.free_shipping_threshold, 50)
        self.assertEqual(calc.shipping_cost, 5)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_free_shipping_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_tax_rate_value_error_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_value_error_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_free_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-3)

    def test_add_item_basic(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.8)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_merge_same_name_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        calc.add_item('Apple', 1.5, 3)
        self.assertEqual(calc.items[0]['quantity'], 5)

    def test_add_item_conflict_different_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 2.0)

    def test_add_item_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    def test_add_item_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, 0)

    def test_add_item_negative_quantity_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, -1)

    def test_add_item_zero_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 0)

    def test_add_item_negative_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', -5)

    def test_add_item_name_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_price_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', '1.5')

    def test_add_item_quantity_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, 1.5)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_remove_item_multiple_same_name(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        calc.add_item('Apple', 1.5, 3)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_remove_item_nonexistent(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Orange')

    def test_remove_item_name_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_nonempty(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        calc.add_item('Banana', 0.8, 3)
        subtotal = calc.get_subtotal()
        self.assertAlmostEqual(subtotal, 1.5 * 2 + 0.8 * 3, places=5)

    def test_get_subtotal_empty(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100, 0.2)
        self.assertAlmostEqual(result, 80.0, places=5)

    def test_apply_discount_zero_discount(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100, 0)
        self.assertAlmostEqual(result, 100.0, places=5)

    def test_apply_discount_full_discount(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100, 1)
        self.assertAlmostEqual(result, 0.0, places=5)

    def test_apply_discount_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10, 0.2)

    def test_apply_discount_discount_out_of_range_low(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100, -0.1)

    def test_apply_discount_discount_out_of_range_high(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100, 1.1)

    def test_apply_discount_subtotal_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.2)

    def test_apply_discount_discount_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100, '0.2')

    def test_calculate_shipping_free(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(150)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_paid(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(50)
        self.assertEqual(shipping, calc.shipping_cost)

    def test_calculate_shipping_exact_threshold(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(100)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('50')

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.23)
        tax = calc.calculate_tax(200)
        self.assertAlmostEqual(tax, 46.0, places=5)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        tax = calc.calculate_tax(0)
        self.assertAlmostEqual(tax, 0.0, places=5)

    def test_calculate_tax_negative_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5)

    def test_calculate_tax_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('200')

    def test_calculate_total_no_discount_no_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 20, 4)
        total = calc.calculate_total()
        expected = 80 + 10 + 20 * 0.23
        self.assertAlmostEqual(total, 110.7, places=5)

    def test_calculate_total_with_discount_and_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 50, 4)
        total = calc.calculate_total(discount=0.5)
        expected = 100 + 0 + 100 * 0.23
        self.assertAlmostEqual(total, 123.0, places=5)

    def test_calculate_total_with_discount_and_paid_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 20, 4)
        total = calc.calculate_total(discount=0.5)
        expected = 40 + 10 + 50 * 0.23
        self.assertAlmostEqual(total, 61.5, places=5)

    def test_calculate_total_full_discount(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 20, 4)
        total = calc.calculate_total(discount=1)
        expected = 0 + 10 + 10 * 0.23
        self.assertAlmostEqual(total, 12.3, places=5)

    def test_calculate_total_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0)
        calc.add_item('Apple', 20, 4)
        total = calc.calculate_total()
        expected = 80 + 10 + 0
        self.assertAlmostEqual(total, 90.0, places=5)

    def test_calculate_total_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1)
        calc.add_item('Apple', 20, 4)
        total = calc.calculate_total()
        expected = 80 + 10 + 90
        self.assertAlmostEqual(total, 180.0, places=5)

    def test_calculate_total_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_negative_discount(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 20, 4)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.1)

    def test_calculate_total_discount_out_of_range(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 20, 4)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.5)

    def test_calculate_total_discount_type_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 20, 4)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='0.2')

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 3)
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        calc.add_item('Banana', 0.8, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_merge(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        calc.add_item('Apple', 1.5, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 3)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_nonempty(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_followed_by_get_subtotal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_clear_order_followed_by_total_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_followed_by_is_empty(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_followed_by_list_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_multiple_unique(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.add_item('Banana', 0.8)
        self.assertCountEqual(calc.list_items(), ['Apple', 'Banana'])

    def test_list_items_merge(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        calc.add_item('Apple', 1.5, 3)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_is_empty_initial(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_add(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_integration_full_flow(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10, 2)
        calc.add_item('Banana', 5, 4)
        total = calc.calculate_total(discount=0.25)
        expected = 30 + 10 + 40 * 0.23
        self.assertAlmostEqual(total, 49.2, places=5)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_integration_discount_and_shipping_boundary(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 20, 6)
        total = calc.calculate_total(discount=0.1)
        expected = 108 + 0 + 108 * 0.23
        self.assertAlmostEqual(total, 132.84, places=5)

    def test_integration_discount_and_shipping_boundary_exact(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 25, 4)
        total = calc.calculate_total()
        expected = 100 + 0 + 100 * 0.23
        self.assertAlmostEqual(total, 123.0, places=5)

    def test_integration_discount_and_shipping_paid(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 20, 4)
        total = calc.calculate_total()
        expected = 80 + 10 + 90 * 0.23
        self.assertAlmostEqual(total, 110.7, places=5)
if __name__ == '__main__':
    unittest.main()