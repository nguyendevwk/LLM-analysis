import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertEqual(self.calc.items, [])

    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)
        self.assertEqual(calc.items, [])

    def test_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_greater_than_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_new(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0], {'name': 'Apple', 'price': 1.5, 'quantity': 2})

    def test_add_item_same_name_price(self):
        self.calc.add_item('Banana', 0.5, 3)
        self.calc.add_item('Banana', 0.5, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 5)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item('Orange', 0.8, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', 0.9, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_price_le_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Grapes', 0, 1)

    def test_add_item_non_numeric_price(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Grapes', '1.0', 1)

    def test_add_item_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Peach', 1.0, 0)

    def test_add_item_non_int_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Peach', 1.0, 1.5)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Mango', 2.0)
        self.assertEqual(self.calc.items[0]['quantity'], 1)

    def test_add_item_large_quantity(self):
        self.calc.add_item('Pineapple', 3.0, 1000)
        self.assertEqual(self.calc.items[0]['quantity'], 1000)

    def test_add_item_float_price(self):
        self.calc.add_item('Kiwi', 1.75, 2)
        self.assertEqual(self.calc.items[0]['price'], 1.75)

    def test_add_item_int_price(self):
        self.calc.add_item('Lemon', 2, 1)
        self.assertEqual(self.calc.items[0]['price'], 2)

    def test_add_item_int_quantity(self):
        self.calc.add_item('Cherry', 0.5, 5)
        self.assertEqual(self.calc.items[0]['quantity'], 5)

    def test_add_item_float_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Berry', 0.3, 1.5)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Watermelon', -1.0, 1)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Coconut', 1.0, -2)

    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.remove_item('Apple')
        self.assertEqual(len(self.calc.items), 0)

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_remove_item_after_all_removed_is_empty(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_duplicate_names(self):
        self.calc.add_item('Banana', 0.5, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.calc.remove_item('Banana')
        self.assertEqual(len(self.calc.items), 0)

    def test_get_subtotal_normal(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 4)
        expected = 1.0 * 2 + 0.5 * 4
        self.assertAlmostEqual(self.calc.get_subtotal(), expected)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_20_percent(self):
        result = self.calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(100.0, 0.0)
        self.assertAlmostEqual(result, 100.0)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(100.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)

    def test_apply_discount_greater_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.1)

    def test_apply_discount_non_numeric_subtotal(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.2)

    def test_apply_discount_non_numeric_discount(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '0.2')

    def test_calculate_shipping_free(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_paid(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(40.0), 10.0)

    def test_calculate_shipping_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50')

    def test_calculate_tax_positive(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_tax_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('10')

    def test_calculate_total_no_discount(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 4)
        subtotal = 1.0 * 2 + 0.5 * 4
        shipping = 10.0 if subtotal < 100.0 else 0.0
        tax = (subtotal + shipping) * 0.23
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_half_discount(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 4)
        subtotal = 1.0 * 2 + 0.5 * 4
        discounted = subtotal * 0.5
        shipping = 10.0 if discounted < 100.0 else 0.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.5), expected)

    def test_calculate_total_full_discount(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 4)
        subtotal = 1.0 * 2 + 0.5 * 4
        discounted = 0.0
        shipping = 10.0 if discounted < 100.0 else 0.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(1.0), expected)

    def test_calculate_total_discount_zero_threshold_met(self):
        self.calc.add_item('Expensive', 200.0, 1)
        subtotal = 200.0
        shipping = 0.0
        tax = subtotal * 0.23
        expected = subtotal + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.0), expected)

    def test_calculate_total_discount_zero_threshold_not_met(self):
        self.calc.add_item('Cheap', 30.0, 1)
        subtotal = 30.0
        shipping = 10.0
        tax = (subtotal + shipping) * 0.23
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.0), expected)

    def test_calculate_total_discount_full_threshold_not_met(self):
        self.calc.add_item('Cheap', 30.0, 1)
        subtotal = 30.0
        discounted = 0.0
        shipping = 10.0
        tax = shipping * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(1.0), expected)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_discount_negative(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-0.1)

    def test_calculate_total_discount_greater_than_one(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.1)

    def test_calculate_total_non_numeric_discount(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.2')

    def test_total_items_multiple(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_none(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.items, [])

    def test_list_items_unique(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Banana', 0.5, 1)
        self.assertCountEqual(self.calc.list_items(), ['Apple', 'Banana'])

    def test_list_items_duplicate_names(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Apple', 1.0, 2)
        self.assertCountEqual(self.calc.list_items(), ['Apple'])

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_get_subtotal_after_clear(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_calculate_total_after_clear(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_remove_item_after_clear(self):
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.remove_item('Apple')

    def test_add_remove_calculate_total_empty(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.remove_item('Apple')
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)
        self.assertEqual(calc.calculate_shipping(5.0), 0.0)

    def test_calculate_shipping_cost_zero(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 100.0)

    def test_calculate_total_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Apple', 1.0, 2)
        subtotal = 2.0
        shipping = 10.0 if subtotal < 100.0 else 0.0
        expected = subtotal + shipping
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        calc.add_item('Apple', 1.0, 2)
        subtotal = 2.0
        shipping = 10.0 if subtotal < 100.0 else 0.0
        tax = (subtotal + shipping) * 1.0
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_add_item_duplicate_names_same_price(self):
        self.calc.add_item('Banana', 0.5, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 5)

    def test_calculate_total_discount_25_threshold_exact(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        subtotal = 133.33333333333334
        calc.add_item('Expensive', subtotal, 1)
        expected_discounted = subtotal * 0.75
        shipping = 0.0
        tax = expected_discounted * 0.23
        expected_total = expected_discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(0.25), expected_total)

    def test_calculate_total_discount_25_threshold_below(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        subtotal = 133.33233333333334
        calc.add_item('Expensive', subtotal, 1)
        expected_discounted = subtotal * 0.75
        shipping = 10.0
        tax = (expected_discounted + shipping) * 0.23
        expected_total = expected_discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(0.25), expected_total)

    def test_calculate_total_discount_25_threshold_above(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        subtotal = 133.33433333333335
        calc.add_item('Expensive', subtotal, 1)
        expected_discounted = subtotal * 0.75
        shipping = 0.0
        tax = expected_discounted * 0.23
        expected_total = expected_discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(0.25), expected_total)

    def test_calculate_total_discount_25_threshold_exact_boundary(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        subtotal = 133.33333333333334
        calc.add_item('Expensive', subtotal, 1)
        expected_discounted = subtotal * 0.75
        shipping = 0.0
        tax = expected_discounted * 0.23
        expected_total = expected_discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(0.25), expected_total)

    def test_calculate_total_discount_25_threshold_below_boundary(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        subtotal = 133.33233333333334
        calc.add_item('Expensive', subtotal, 1)
        expected_discounted = subtotal * 0.75
        shipping = 10.0
        tax = (expected_discounted + shipping) * 0.23
        expected_total = expected_discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(0.25), expected_total)

    def test_calculate_total_discount_25_threshold_above_boundary(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        subtotal = 133.33433333333335
        calc.add_item('Expensive', subtotal, 1)
        expected_discounted = subtotal * 0.75
        shipping = 0.0
        tax = expected_discounted * 0.23
        expected_total = expected_discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(0.25), expected_total)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Mango', 2.0)
        self.assertEqual(self.calc.items[0]['quantity'], 1)

    def test_add_item_large_quantity_again(self):
        self.calc.add_item('Pineapple', 3.0, 1000)
        self.assertEqual(self.calc.items[0]['quantity'], 1000)

    def test_add_item_float_price_again(self):
        self.calc.add_item('Kiwi', 1.75, 2)
        self.assertEqual(self.calc.items[0]['price'], 1.75)

    def test_add_item_int_price_again(self):
        self.calc.add_item('Lemon', 2, 1)
        self.assertEqual(self.calc.items[0]['price'], 2)

    def test_add_item_int_quantity_again(self):
        self.calc.add_item('Cherry', 0.5, 5)
        self.assertEqual(self.calc.items[0]['quantity'], 5)

    def test_add_item_float_quantity_again(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Berry', 0.3, 1.5)

    def test_add_item_negative_price_again(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Watermelon', -1.0, 1)

    def test_add_item_negative_quantity_again(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Coconut', 1.0, -2)

    def test_remove_item_after_duplicate_names(self):
        self.calc.add_item('Banana', 0.5, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.calc.remove_item('Banana')
        self.assertEqual(len(self.calc.items), 0)

    def test_calculate_total_discount_25_threshold_exact_again(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        subtotal = 133.33333333333334
        calc.add_item('Expensive', subtotal, 1)
        expected_discounted = subtotal * 0.75
        shipping = 0.0
        tax = expected_discounted * 0.23
        expected_total = expected_discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(0.25), expected_total)

    def test_calculate_total_discount_25_threshold_below_again(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        subtotal = 133.33233333333334
        calc.add_item('Expensive', subtotal, 1)
        expected_discounted = subtotal * 0.75
        shipping = 10.0
        tax = (expected_discounted + shipping) * 0.23
        expected_total = expected_discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(0.25), expected_total)

    def test_calculate_total_discount_25_threshold_above_again(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        subtotal = 133.33433333333335
        calc.add_item('Expensive', subtotal, 1)
        expected_discounted = subtotal * 0.75
        shipping = 0.0
        tax = expected_discounted * 0.23
        expected_total = expected_discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(0.25), expected_total)
if __name__ == '__main__':
    unittest.main()