import unittest
import math
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default_parameters(self):
        calc = OrderCalculator()
        self.assertEqual(calc.items, [])
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom_parameters(self):
        calc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.15)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_low(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_high(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_init_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_invalid_type_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='high')

    def test_init_invalid_type_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='low')

    def test_init_invalid_type_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='cheap')

    def test_init_invalid_value_tax_rate_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_invalid_value_tax_rate_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_invalid_value_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_value_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_basic(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0], {'name': 'Apple', 'price': 1.5, 'quantity': 2})

    def test_add_item_multiple_quantities(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.5, 3)
        calc.add_item('Banana', 0.5, 2)
        self.assertEqual(calc.items[0]['quantity'], 5)

    def test_add_item_price_integer(self):
        calc = OrderCalculator()
        calc.add_item('Orange', 2, 1)
        self.assertEqual(calc.items[0]['price'], 2)

    def test_add_item_price_float(self):
        calc = OrderCalculator()
        calc.add_item('Grape', 1.25, 1)
        self.assertEqual(calc.items[0]['price'], 1.25)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Peach', 3.0)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_quantity_greater_than_one(self):
        calc = OrderCalculator()
        calc.add_item('Pear', 2.5, 4)
        self.assertEqual(calc.items[0]['quantity'], 4)

    def test_add_item_empty_name_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0, 1)

    def test_add_item_name_none_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(None, 1.0, 1)

    def test_add_item_negative_price_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Mango', -1.0, 1)

    def test_add_item_price_none_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Mango', None, 1)

    def test_add_item_zero_quantity_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Kiwi', 1.0, 0)

    def test_add_item_quantity_none_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Kiwi', 1.0, None)

    def test_add_item_name_non_string_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_add_item_price_non_numeric_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Lemon', 'cheap', 1)

    def test_add_item_quantity_non_int_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Lemon', 1.0, 1.5)

    def test_add_item_same_name_different_price_error(self):
        calc = OrderCalculator()
        calc.add_item('Cherry', 0.2, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Cherry', 0.3, 1)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 0.5, 1)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'Banana')

    def test_remove_item_multiple_same_name(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Apple', 1.0, 2)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 0)

    def test_remove_item_nonexistent_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            calc.remove_item('Orange')

    def test_remove_item_name_none_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(None)

    def test_remove_item_name_non_string_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_empty_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 6.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 3)
        calc.add_item('Banana', 1.0, 4)
        self.assertAlmostEqual(calc.get_subtotal(), 10.0)

    def test_apply_discount_basic(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        result = calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(result, 50.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        result = calc.apply_discount(75.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative_subtotal_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_discount_low_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(10.0, -0.1)

    def test_apply_discount_discount_high_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(10.0, 1.1)

    def test_apply_discount_subtotal_non_numeric_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('ten', 0.1)

    def test_apply_discount_discount_non_numeric_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(10.0, 'ten')

    def test_calculate_shipping_free(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_paid(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(80.0), 10.0)

    def test_calculate_shipping_exact_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('fifty')

    def test_calculate_tax_basic(self):
        calc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(calc.calculate_tax(50.0), 10.0)

    def test_calculate_tax_zero(self):
        calc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('ten')

    def test_calculate_tax_negative_amount_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_total_basic_no_discount(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item('Apple', 20.0, 2)
        total = calc.calculate_total()
        expected = 40.0 + 5.0 + 4.5
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item('Apple', 20.0, 2)
        total = calc.calculate_total(discount=0.25)
        discounted = 30.0
        shipping = 5.0
        tax = 3.5
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_full_discount(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item('Apple', 20.0, 2)
        total = calc.calculate_total(discount=1.0)
        shipping = 5.0
        tax = 0.5
        expected = shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=30.0, shipping_cost=5.0)
        calc.add_item('Apple', 20.0, 2)
        total = calc.calculate_total()
        shipping = 0.0
        tax = 4.0
        expected = 40.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_exact_threshold(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=40.0, shipping_cost=5.0)
        calc.add_item('Apple', 20.0, 2)
        total = calc.calculate_total()
        shipping = 0.0
        tax = 4.0
        expected = 40.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_zero_shipping(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=0.0)
        calc.add_item('Apple', 20.0, 2)
        total = calc.calculate_total()
        shipping = 0.0
        tax = 4.0
        expected = 40.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_zero_tax(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item('Apple', 20.0, 2)
        total = calc.calculate_total()
        shipping = 5.0
        tax = 0.0
        expected = 40.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_full_tax(self):
        calc = OrderCalculator(tax_rate=1.0, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item('Apple', 20.0, 2)
        total = calc.calculate_total()
        shipping = 5.0
        tax = 45.0
        expected = 40.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_empty_order_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_invalid_discount_type(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='ten')

    def test_calculate_total_discount_low_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.1)

    def test_calculate_total_discount_high_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.1)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_clear_order(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(len(calc.items), 0)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_unique_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 1.0, 1)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})

    def test_list_items_order_irrelevant(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 1.0, 1)
        calc.add_item('Cherry', 1.0, 1)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana', 'Cherry'})

    def test_is_empty_initial(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_add(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_remove_all(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_add_item_whitespace_name(self):
        calc = OrderCalculator()
        calc.add_item('   ', 1.0, 1)
        self.assertEqual(calc.items[0]['name'], '   ')

    def test_add_item_large_price(self):
        calc = OrderCalculator()
        calc.add_item('Expensive', 1000000000000.0, 1)
        self.assertEqual(calc.items[0]['price'], 1000000000000.0)

    def test_add_item_small_price(self):
        calc = OrderCalculator()
        calc.add_item('Cheap', 1e-09, 1)
        self.assertEqual(calc.items[0]['price'], 1e-09)

    def test_add_item_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Bulk', 1.0, 1000000)
        self.assertEqual(calc.items[0]['quantity'], 1000000)

    def test_add_item_small_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Single', 1.0, 1)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_calculate_total_small_totals_precision(self):
        calc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=0.01, shipping_cost=0.01)
        calc.add_item('Tiny', 0.0001, 1)
        total = calc.calculate_total()
        expected = 0.0001 + 0.01 + (0.0001 + 0.01) * 0.15
        self.assertAlmostEqual(total, expected, places=8)

    def test_calculate_shipping_large_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=1000000000000.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(1000000.0), 10.0)

    def test_calculate_shipping_small_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.01, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(0.02), 0.0)

    def test_calculate_tax_small_rate(self):
        calc = OrderCalculator(tax_rate=0.0001)
        self.assertAlmostEqual(calc.calculate_tax(1000.0), 0.1)

    def test_calculate_tax_large_rate(self):
        calc = OrderCalculator(tax_rate=0.9999)
        self.assertAlmostEqual(calc.calculate_tax(1000.0), 999.9, places=1)

    def test_calculate_total_small_values(self):
        calc = OrderCalculator(tax_rate=0.0001, free_shipping_threshold=0.01, shipping_cost=0.01)
        calc.add_item('Tiny', 0.0001, 1)
        total = calc.calculate_total()
        expected = 0.0001 + 0.01 + (0.0001 + 0.01) * 0.0001
        self.assertAlmostEqual(total, expected, places=8)

    def test_add_item_nan_price(self):
        calc = OrderCalculator()
        calc.add_item('NaNPrice', float('nan'), 1)
        self.assertTrue(math.isnan(calc.items[0]['price']))

    def test_calculate_tax_nan_amount(self):
        calc = OrderCalculator()
        result = calc.calculate_tax(float('nan'))
        self.assertTrue(math.isnan(result))

    def test_calculate_shipping_nan_subtotal(self):
        calc = OrderCalculator()
        result = calc.calculate_shipping(float('nan'))
        self.assertEqual(result, 10.0)

    def test_apply_discount_nan_subtotal(self):
        calc = OrderCalculator()
        result = calc.apply_discount(float('nan'), 0.1)
        self.assertTrue(math.isnan(result))

    def test_calculate_total_zero_discount_zero_shipping(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=0.0)
        calc.add_item('Apple', 20.0, 2)
        total = calc.calculate_total(discount=0.0)
        expected = 40.0 + 0.0 + 4.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_full_discount_zero_shipping(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=0.0)
        calc.add_item('Apple', 20.0, 2)
        total = calc.calculate_total(discount=1.0)
        expected = 0.0 + 0.0 + 0.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_half_discount_near_threshold(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=30.0, shipping_cost=5.0)
        calc.add_item('Apple', 19.0, 2)
        total = calc.calculate_total(discount=0.5)
        discounted = 19.0
        shipping = 5.0
        tax = 2.4
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_list_items_case_sensitive(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('apple', 1.0, 1)
        self.assertEqual(set(calc.list_items()), {'Apple', 'apple'})

    def test_remove_item_multiple_same_name_different_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Apple', 1.0, 2)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 0)
if __name__ == '__main__':
    unittest.main()