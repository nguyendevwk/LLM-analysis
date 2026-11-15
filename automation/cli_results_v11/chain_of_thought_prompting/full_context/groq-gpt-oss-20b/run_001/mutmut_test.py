import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default_parameters(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    def test_init_custom_parameters(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='a')

    def test_init_invalid_tax_rate_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='b')

    def test_init_invalid_free_shipping_threshold_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='c')

    def test_init_invalid_shipping_cost_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_add_multiple_items_different_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Banana', 2.0)
        self.assertEqual(len(calc.items), 2)
        names = {item['name'] for item in calc.items}
        self.assertSetEqual(names, {'Apple', 'Banana'})

    def test_add_duplicate_item_same_name_and_price_increments_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 5)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_with_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    def test_add_item_with_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_with_non_number_price(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 'price')

    def test_add_item_with_non_int_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, 1.5)

    def test_add_item_with_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, 0)

    def test_add_item_with_negative_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', -1.0)

    def test_add_item_same_name_different_price_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 2.0)

    def test_remove_existing_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_remove_nonexistent_item_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Banana')

    def test_remove_item_with_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_with_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 2.0)
        self.assertAlmostEqual(calc.get_subtotal(), 4.0)

    def test_get_subtotal_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_negative_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.2)

    def test_apply_discount_invalid_discount_value(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.5)

    def test_apply_discount_invalid_subtotal_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('subtotal', 0.2)

    def test_apply_discount_invalid_discount_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, 'discount')

    def test_calculate_shipping_free_when_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(120.0), 0.0)

    def test_calculate_shipping_non_free_when_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(80.0), 10.0)

    def test_calculate_shipping_exact_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(-10.0), 10.0)

    def test_calculate_shipping_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('subtotal')

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('amount')

    def test_calculate_total_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 2.0)
        expected = 4.0 + 10.0 + 0.23 * 14.0
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_with_discount(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 2.0)
        expected = 3.2 + 10.0 + 0.23 * 13.2
        self.assertAlmostEqual(calc.calculate_total(0.2), expected)

    def test_calculate_total_with_full_discount_and_non_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=200.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 0.0 + 10.0 + 0.23 * 10.0
        self.assertAlmostEqual(calc.calculate_total(1.0), expected)

    def test_calculate_total_discount_boundary_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Apple', 2.0, 100)
        expected = 100.0 + 0.0 + 0.23 * 100.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    def test_calculate_total_invalid_discount_type(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        with self.assertRaises(TypeError):
            calc.calculate_total('discount')

    def test_calculate_total_invalid_discount_value(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.5)

    def test_calculate_total_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_total_items_multiple_quantities(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        calc.add_item('Banana', 2.0, 2)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_resets_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_list_items_unique_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(set(calc.list_items()), {'Apple'})

    def test_list_items_multiple_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Banana', 2.0)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_is_empty_initially(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_adding(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_clearing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_total_items_after_adding(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        calc.add_item('Banana', 2.0, 2)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        calc.remove_item('Apple')
        self.assertEqual(calc.total_items(), 0)

    def test_list_items_after_clearing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_after_adding(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Banana', 2.0)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})

    def test_add_same_name_same_price_increments_and_different_price_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.items[0]['quantity'], 5)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 2.0)

    def test_calculate_total_with_multiple_items_and_discount(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 2.0)
        expected = 2.8 + 10.0 + 0.23 * 12.8
        self.assertAlmostEqual(calc.calculate_total(0.3), expected)

    def test_calculate_total_with_zero_shipping_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 2.0 + 0.0 + 0.23 * 2.0
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_with_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 2.0 + 0.0 + 0.23 * 2.0
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_with_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 2.0 + 10.0 + 0.0
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_with_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 2.0 + 10.0 + 12.0
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_with_discount_half_and_zero_shipping(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 1.0 + 0.0 + 0.23 * 1.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    def test_calculate_total_with_discount_half_and_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        expected = 1.0 + 10.0 + 0.23 * 11.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    def test_calculate_total_with_discount_half_and_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 200)
        expected = 100.0 + 0.0 + 0.23 * 100.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    def test_calculate_total_with_discount_half_and_zero_shipping(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 200)
        expected = 100.0 + 0.0 + 0.23 * 100.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    def test_tax_rate_boundary_values(self):
        calc_zero = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc_zero.calculate_tax(100.0), 0.0)
        calc_one = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc_one.calculate_tax(100.0), 100.0)

    def test_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(calc.calculate_shipping(2.0), 0.0)

    def test_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(calc.calculate_shipping(2.0), 0.0)

    def test_add_item_price_integer(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 2, 1)
        self.assertEqual(calc.items[0]['price'], 2)

    def test_add_item_price_float(self):
        calc = OrderCalculator()
        calc.add_item('Orange', 1.5, 1)
        self.assertAlmostEqual(calc.items[0]['price'], 1.5)

    def test_add_item_quantity_integer(self):
        calc = OrderCalculator()
        calc.add_item('Grape', 0.5, 3)
        self.assertEqual(calc.items[0]['quantity'], 3)

    def test_add_item_quantity_default(self):
        calc = OrderCalculator()
        calc.add_item('Pear', 0.8)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_remove_item_multiple_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_list_items_order_independent(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Banana', 2.0)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(-10.0), 10.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_total_discount_zero_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 2.0 + 0.0 + 0.23 * 2.0
        self.assertAlmostEqual(calc.calculate_total(0.0), expected)

    def test_calculate_total_discount_full_zero_shipping(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 2)
        self.assertAlmostEqual(calc.calculate_total(1.0), 0.0)

    def test_calculate_total_discount_full_zero_tax(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 0.0 + 10.0 + 0.0
        self.assertAlmostEqual(calc.calculate_total(1.0), expected)

    def test_calculate_total_discount_full_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        self.assertAlmostEqual(calc.calculate_total(1.0), 0.0)

    def test_calculate_total_discount_half_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 1.0 + 0.0 + 0.23 * 1.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    def test_calculate_total_discount_half_zero_shipping(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 1.0 + 0.0 + 0.23 * 1.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    def test_calculate_total_discount_half_zero_tax(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 1.0 + 10.0 + 0.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    def test_calculate_total_discount_half_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        calc.add_item('Apple', 1.0, 2)
        expected = 1.0 + 10.0 + 11.0
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)
if __name__ == '__main__':
    unittest.main()