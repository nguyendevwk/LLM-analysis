import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default_values(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.15)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_custom_int_values(self):
        calc = OrderCalculator(tax_rate=1, free_shipping_threshold=200, shipping_cost=20)
        self.assertEqual(calc.tax_rate, 1)
        self.assertEqual(calc.free_shipping_threshold, 200)
        self.assertEqual(calc.shipping_cost, 20)

    def test_init_tax_rate_bounds_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_bounds_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_init_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='high')

    def test_init_free_shipping_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='low')

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='cheap')

    def test_init_tax_rate_value_error_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_value_error_over(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_free_shipping_threshold_value_error_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_shipping_cost_value_error_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_add_item_basic(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'Apple')
        self.assertEqual(calc.items[0]['price'], 1.0)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_with_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.5, quantity=3)
        self.assertEqual(calc.items[0]['quantity'], 3)

    def test_add_item_increment(self):
        calc = OrderCalculator()
        calc.add_item('Orange', 0.8)
        calc.add_item('Orange', 0.8, quantity=2)
        self.assertEqual(calc.items[0]['quantity'], 3)

    def test_add_item_different_price_error(self):
        calc = OrderCalculator()
        calc.add_item('Grapes', 2.0)
        with self.assertRaises(ValueError):
            calc.add_item('Grapes', 3.0)

    def test_add_item_empty_name_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    def test_add_item_zero_quantity_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Peach', 1.5, quantity=0)

    def test_add_item_negative_quantity_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Peach', 1.5, quantity=-2)

    def test_add_item_zero_price_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Pear', 0.0)

    def test_add_item_negative_price_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Pear', -1.0)

    def test_add_item_name_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_price_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Mango', 'expensive')

    def test_add_item_quantity_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Mango', 1.0, quantity=2.5)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 0)

    def test_remove_item_nonexistent_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Nonexistent')

    def test_remove_item_name_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_all_instances(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Apple', 1.0, quantity=2)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 0)

    def test_remove_item_empty_order_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Apple')

    def test_get_subtotal_nonempty(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, quantity=2)
        calc.add_item('Banana', 0.5, quantity=4)
        self.assertAlmostEqual(calc.get_subtotal(), 1.0 * 2 + 0.5 * 4)

    def test_get_subtotal_empty_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_precision(self):
        calc = OrderCalculator()
        calc.add_item('Item', 0.1, quantity=3)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3)

    def test_apply_discount_no_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_half_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(200.0, 0.5), 100.0)

    def test_apply_discount_invalid_discount_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, 'half')

    def test_apply_discount_subtotal_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('hundred', 0.1)

    def test_apply_discount_invalid_discount_value_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)

    def test_apply_discount_invalid_discount_value_over(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.1)

    def test_apply_discount_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.2)

    def test_calculate_shipping_free(self):
        calc = OrderCalculator(free_shipping_threshold=50.0)
        self.assertAlmostEqual(calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_paid(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=15.0)
        self.assertAlmostEqual(calc.calculate_shipping(40.0), 15.0)

    def test_calculate_shipping_exact_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=30.0)
        self.assertAlmostEqual(calc.calculate_shipping(30.0), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=30.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(-5.0), 10.0)

    def test_calculate_shipping_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('ten')

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_positive_amount(self):
        calc = OrderCalculator(tax_rate=0.25)
        self.assertAlmostEqual(calc.calculate_tax(200.0), 50.0)

    def test_calculate_tax_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('amount')

    def test_calculate_tax_negative_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-10.0)

    def test_calculate_tax_custom_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_custom_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 100.0)

    def test_calculate_total_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, quantity=2)
        calc.add_item('Banana', 0.5, quantity=4)
        subtotal = calc.get_subtotal()
        shipping = calc.calculate_shipping(subtotal)
        tax = calc.calculate_tax(subtotal + shipping)
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_full_discount(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, quantity=2)
        subtotal = calc.get_subtotal()
        shipping = calc.calculate_shipping(0.0)
        tax = calc.calculate_tax(shipping)
        expected = 0.0 + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(discount=1.0), expected)

    def test_calculate_total_half_discount(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, quantity=5)
        subtotal = calc.get_subtotal()
        discounted = calc.apply_discount(subtotal, 0.5)
        shipping = calc.calculate_shipping(discounted)
        tax = calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(discount=0.5), expected)

    def test_calculate_total_paid_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=12.0)
        calc.add_item('Item', 30.0, quantity=2)
        subtotal = calc.get_subtotal()
        discounted = calc.apply_discount(subtotal, 0.0)
        self.assertAlmostEqual(calc.calculate_shipping(discounted), 12.0)

    def test_calculate_total_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        calc.add_item('Item', 10.0)
        subtotal = calc.get_subtotal()
        shipping = calc.calculate_shipping(subtotal)
        tax = calc.calculate_tax(subtotal + shipping)
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_invalid_discount_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='half')

    def test_calculate_total_invalid_discount_value_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.1)

    def test_calculate_total_invalid_discount_value_over(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.1)

    def test_calculate_total_empty_order_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_custom_parameters(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=30.0, shipping_cost=5.0)
        calc.add_item('Item', 20.0, quantity=2)
        subtotal = calc.get_subtotal()
        discounted = calc.apply_discount(subtotal, 0.2)
        shipping = calc.calculate_shipping(discounted)
        tax = calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(discount=0.2), expected)

    def test_calculate_total_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item('Item', 10.0)
        self.assertAlmostEqual(calc.calculate_shipping(calc.get_subtotal()), 0.0)

    def test_calculate_total_free_shipping_threshold_zero_nonzero_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item('Item', 10.0)
        self.assertAlmostEqual(calc.calculate_shipping(calc.get_subtotal()), 0.0)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, quantity=2)
        calc.add_item('B', 2.0, quantity=3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, quantity=2)
        calc.add_item('B', 2.0, quantity=3)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 3)

    def test_clear_order_resets_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0)
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_clear_order_is_empty(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_list_items_empty(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_clear_order_total_items_zero(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_get_subtotal_error(self):
        calc = OrderCalculator()
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_clear_order_calculate_total_error(self):
        calc = OrderCalculator()
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_clear_order_add_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0)
        calc.clear_order()
        calc.add_item('B', 2.0)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'B')

    def test_list_items_unique(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Apple', 1.0, quantity=2)
        self.assertEqual(set(calc.list_items()), {'Apple'})

    def test_list_items_multiple_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Banana', 0.5)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_type(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        for name in calc.list_items():
            self.assertIsInstance(name, str)

    def test_is_empty_initial(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_add(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_remove_all(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_integration_add_remove_sequence(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, quantity=2)
        calc.add_item('B', 2.0, quantity=3)
        calc.remove_item('A')
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'B')
        self.assertAlmostEqual(calc.get_subtotal(), 6.0)

    def test_integration_full_order_flow(self):
        calc = OrderCalculator()
        calc.add_item('A', 10.0, quantity=2)
        calc.add_item('B', 5.0, quantity=4)
        subtotal = calc.get_subtotal()
        discount = 0.1
        discounted = calc.apply_discount(subtotal, discount)
        shipping = calc.calculate_shipping(discounted)
        tax = calc.calculate_tax(discounted + shipping)
        expected_total = discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(discount=discount), expected_total)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_integration_discount_and_shipping_edge(self):
        calc = OrderCalculator(free_shipping_threshold=50.0)
        calc.add_item('Item', 25.0, quantity=2)
        subtotal = calc.get_subtotal()
        discounted = calc.apply_discount(subtotal, 0.0)
        self.assertAlmostEqual(calc.calculate_shipping(discounted), 0.0)

    def test_integration_discount_and_shipping_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=8.0)
        calc.add_item('Item', 20.0, quantity=2)
        subtotal = calc.get_subtotal()
        discounted = calc.apply_discount(subtotal, 0.0)
        self.assertAlmostEqual(calc.calculate_shipping(discounted), 8.0)

    def test_integration_invalid_inputs_across_methods(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(1, 1.0)
        with self.assertRaises(ValueError):
            calc.add_item('A', -1.0)
        with self.assertRaises(TypeError):
            calc.remove_item(1)
        with self.assertRaises(ValueError):
            calc.remove_item('Nonexistent')
        with self.assertRaises(ValueError):
            calc.get_subtotal()
        with self.assertRaises(TypeError):
            calc.apply_discount('subtotal', 0.1)
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)
        with self.assertRaises(TypeError):
            calc.calculate_shipping('subtotal')
        with self.assertRaises(TypeError):
            calc.calculate_tax('amount')
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='half')

    def test_instance_isolation(self):
        calc1 = OrderCalculator()
        calc2 = OrderCalculator()
        calc1.add_item('A', 1.0)
        self.assertEqual(len(calc1.items), 1)
        self.assertEqual(len(calc2.items), 0)

    def test_duplicate_name_handling(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0)
        with self.assertRaises(ValueError):
            calc.add_item('A', 2.0)

    def test_remove_all_instances(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, quantity=2)
        calc.add_item('A', 1.0, quantity=3)
        calc.remove_item('A')
        self.assertEqual(len(calc.items), 0)

    def test_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Item', 10.0)
        self.assertAlmostEqual(calc.calculate_shipping(calc.get_subtotal()), 0.0)

    def test_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item('Item', 10.0)
        self.assertAlmostEqual(calc.calculate_shipping(calc.get_subtotal()), 0.0)
if __name__ == '__main__':
    unittest.main()