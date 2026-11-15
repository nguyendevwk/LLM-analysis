import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError) as cm:
            OrderCalculator(tax_rate='0.2')
        self.assertIn('Tax rate must be a float or int', str(cm.exception))

    def test_init_tax_rate_too_low(self):
        with self.assertRaises(ValueError) as cm:
            OrderCalculator(tax_rate=-0.01)
        self.assertIn('Tax rate must be between 0.0 and 1.0', str(cm.exception))

    def test_init_tax_rate_too_high(self):
        with self.assertRaises(ValueError) as cm:
            OrderCalculator(tax_rate=1.5)
        self.assertIn('Tax rate must be between 0.0 and 1.0', str(cm.exception))

    def test_init_free_shipping_threshold_type_error(self):
        with self.assertRaises(TypeError) as cm:
            OrderCalculator(free_shipping_threshold='100')
        self.assertIn('Free shipping threshold must be a float or int', str(cm.exception))

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError) as cm:
            OrderCalculator(free_shipping_threshold=-5.0)
        self.assertIn('Free shipping threshold cannot be negative', str(cm.exception))

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError) as cm:
            OrderCalculator(shipping_cost=None)
        self.assertIn('Shipping cost must be a float or int', str(cm.exception))

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError) as cm:
            OrderCalculator(shipping_cost=-2.0)
        self.assertIn('Shipping cost cannot be negative', str(cm.exception))

    def test_init_mixed_invalid_inputs(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='invalid', shipping_cost=-5)

    def test_add_item_normal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(len(calc.items), 1)
        item = calc.items[0]
        self.assertEqual(item['name'], 'Apple')
        self.assertEqual(item['price'], 1.0)
        self.assertEqual(item['quantity'], 3)

    def test_add_item_merge_same_name_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 4)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 6)

    def test_add_item_same_name_diff_price_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        with self.assertRaises(ValueError) as cm:
            calc.add_item('Apple', 1.5, 1)
        self.assertIn('Item with the same name but different price already exists', str(cm.exception))

    def test_add_item_empty_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 5.0, 1)

    def test_add_item_name_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 5.0, 1)

    def test_add_item_nonpositive_price_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Book', 0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Book', -2.0, 1)

    def test_add_item_price_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Book', '10', 1)

    def test_add_item_quantity_less_than_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Pen', 2.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item('Pen', 2.0, -3)

    def test_add_item_quantity_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Pen', 2.0, 2.5)

    def test_add_item_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        calc.clear_order()
        calc.add_item('Item', 10.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.remove_item('Apple')
        self.assertEqual(calc.items, [])

    def test_remove_item_multi_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 5)
        calc.remove_item('Apple')
        self.assertEqual(calc.items, [])

    def test_remove_item_nonexistent_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError) as cm:
            calc.remove_item('Banana')
        self.assertIn("Item with name 'Banana' does not exist", str(cm.exception))

    def test_remove_item_name_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(42)

    def test_remove_item_among_multiple(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 3)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'Banana')

    def test_remove_then_add_same_name(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_get_subtotal_normal(self):
        calc = OrderCalculator()
        calc.add_item('A', 2.0, 3)
        calc.add_item('B', 5.0, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 11.0)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('C', 7.5, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 15.0)

    def test_get_subtotal_empty_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_fractional_price(self):
        calc = OrderCalculator()
        calc.add_item('D', 1.333, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 3.999, places=3)

    def test_get_subtotal_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item('E', 0.01, 1000000)
        self.assertAlmostEqual(calc.get_subtotal(), 10000.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_fifty_percent(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(80.0, 0.5), 40.0)

    def test_apply_discount_hundred_percent(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(20.0, 1.0), 0.0)

    def test_apply_discount_zero_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(0.0, 0.3), 0.0)

    def test_apply_discount_negative_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-5.0, 0.1)

    def test_apply_discount_negative_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(10.0, -0.05)

    def test_apply_discount_over_one_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(10.0, 1.2)

    def test_apply_discount_subtotal_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_discount_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100, None)

    def test_apply_discount_invalid_subtotal_first(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('invalid', 0.5)

    def test_calculate_shipping_free_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_free_exact_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_paid_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_zero_cost(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_input_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('50')

    def test_calculate_shipping_negative_input(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(-5.0), 10.0)

    def test_calculate_shipping_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(123.45), 0.0)

    def test_calculate_tax_full_rate(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc.calculate_tax(50.0), 50.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_amount_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('10')

    def test_calculate_total_no_discount_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Book', 20.0, 2)
        expected = 40.0 + 10.0 + (40.0 + 10.0) * 0.23
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_discount_shipping_applies(self):
        calc = OrderCalculator()
        calc.add_item('Book', 20.0, 2)
        discounted = 40.0 * 0.9
        expected = discounted + 10.0 + (discounted + 10.0) * 0.23
        self.assertAlmostEqual(calc.calculate_total(discount=0.1), expected)

    def test_calculate_total_discount_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Item', 75.0, 2)
        discounted = 150.0 * 0.8
        expected = discounted + 0.0 + discounted * 0.23
        self.assertAlmostEqual(calc.calculate_total(discount=0.2), expected)

    def test_calculate_total_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_negative_subtotal_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        calc.get_subtotal = lambda: -5.0
        with self.assertRaises(ValueError) as cm:
            calc.calculate_total()
        self.assertIn('Cannot calculate total on negative subtotal', str(cm.exception))

    def test_calculate_total_discount_type_error(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='0.1')

    def test_calculate_total_discount_out_of_range(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.5)

    def test_calculate_total_negative_discount(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.2)

    def test_calculate_total_default_discount(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        total_no_arg = calc.calculate_total()
        total_zero_arg = calc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total_no_arg, total_zero_arg)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_qty_one(self):
        calc = OrderCalculator()
        calc.add_item('A', 5.0, 1)
        self.assertEqual(calc.total_items(), 1)

    def test_total_items_multiple_quantities(self):
        calc = OrderCalculator()
        calc.add_item('A', 5.0, 3)
        calc.add_item('B', 2.0, 4)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('A', 5.0, 3)
        calc.add_item('B', 2.0, 4)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 4)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 5.0, 3)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1000000)
        self.assertEqual(calc.total_items(), 1000000)

    def test_clear_order_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_clear_order_reuse_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        calc.add_item('A', 1.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertSetEqual(set(calc.list_items()), {'Apple'})

    def test_list_items_multiple_distinct(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 1)
        calc.add_item('Cherry', 3.0, 1)
        self.assertSetEqual(set(calc.list_items()), {'Apple', 'Banana', 'Cherry'})

    def test_list_items_duplicate_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertSetEqual(set(calc.list_items()), {'Apple'})
        self.assertEqual(len(calc.list_items()), 1)

    def test_list_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 1)
        calc.remove_item('Apple')
        self.assertSetEqual(set(calc.list_items()), {'Banana'})

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_is_empty_fresh(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_add_then_remove(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.remove_item('A')
        self.assertTrue(calc.is_empty())
if __name__ == '__main__':
    unittest.main()