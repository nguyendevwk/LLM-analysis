import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.tax_rate, 0.23)
        self.assertAlmostEqual(calc.free_shipping_threshold, 100.0)
        self.assertAlmostEqual(calc.shipping_cost, 10.0)

    def test_init_explicit_valid(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.tax_rate, 0.1)
        self.assertAlmostEqual(calc.free_shipping_threshold, 50.0)
        self.assertAlmostEqual(calc.shipping_cost, 5.0)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_greater_than_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_non_numeric_tax_rate(self):
        with self.assertRaises((TypeError, ValueError)):
            OrderCalculator(tax_rate='high')

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_add_item_normal(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0, 2)
        self.assertIn('apple', calc.list_items())
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0)

    def test_add_item_duplicate_same_price(self):
        calc = OrderCalculator()
        calc.add_item('banana', 0.5, 3)
        calc.add_item('banana', 0.5, 2)
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 2.5)

    def test_add_item_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0, 1)

    def test_add_item_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises((TypeError, ValueError)):
            calc.add_item(123, 1.0, 1)

    def test_add_item_negative_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('pear', -1.0, 1)

    def test_add_item_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('pear', 1.0, -2)

    def test_add_item_zero_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('pear', 1.0, 0)

    def test_add_item_non_int_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises((TypeError, ValueError)):
            calc.add_item('pear', 1.0, 2.5)

    def test_add_item_large_quantity_price(self):
        calc = OrderCalculator()
        calc.add_item('expensive', 1000000.0, 1000000)
        self.assertAlmostEqual(calc.get_subtotal(), 1000000000000.0)

    def test_remove_item_normal(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0, 1)
        calc.remove_item('apple')
        self.assertTrue(calc.is_empty())

    def test_remove_item_quantity_greater_than_one(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0, 3)
        calc.remove_item('apple')
        self.assertTrue(calc.is_empty())

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.5, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 5.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('apple', 2.0, 1)
        calc.add_item('banana', 1.5, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 6.5)

    def test_get_subtotal_precision(self):
        calc = OrderCalculator()
        calc.add_item('item', 0.1, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3, places=7)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        result = calc.apply_discount(10.0, 0.0)
        self.assertAlmostEqual(result, 10.0)

    def test_apply_discount_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(10.0, -1.0)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_equal_threshold(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        shipping = calc.calculate_shipping(10.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        shipping = calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_tax_normal(self):
        calc = OrderCalculator()
        tax = calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        tax = calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-10.0)

    def test_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        tax = calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_full_rate(self):
        calc = OrderCalculator(tax_rate=1.0)
        tax = calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 100.0)

    def test_calculate_total_negative_discount(self):
        calc = OrderCalculator()
        calc.add_item('apple', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-5.0)

    def test_calculate_total_free_shipping_met(self):
        calc = OrderCalculator()
        calc.add_item('apple', 60.0, 2)
        total = calc.calculate_total()
        expected = 120.0 + 0.0 + 27.6
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('apple', 50.0, 1)
        total = calc.calculate_total()
        expected = 50.0 + 0.0 + 11.5
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('apple', 50.0, 1)
        total = calc.calculate_total()
        expected = 50.0 + 10.0 + 0.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_tax_rate_full(self):
        calc = OrderCalculator(tax_rate=1.0)
        calc.add_item('apple', 50.0, 1)
        total = calc.calculate_total()
        expected = 50.0 + 10.0 + 60.0
        self.assertAlmostEqual(total, expected)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 2)
        calc.add_item('b', 2.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_clear_order_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.add_item('b', 2.0, 1)
        self.assertEqual(set(calc.list_items()), {'a', 'b'})

    def test_list_items_duplicate_names(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.add_item('a', 1.0, 2)
        self.assertEqual(calc.list_items(), ['a'])

    def test_is_empty_empty(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_state_consistency_add_remove(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 2)
        calc.add_item('b', 2.0, 3)
        calc.remove_item('a')
        self.assertEqual(calc.total_items(), 3)
        self.assertEqual(calc.list_items(), ['b'])
        self.assertAlmostEqual(calc.get_subtotal(), 6.0)
        self.assertFalse(calc.is_empty())

    def test_edge_numeric_free_shipping_threshold_exact(self):
        calc = OrderCalculator(free_shipping_threshold=100.0)
        calc.add_item('a', 50.0, 2)
        shipping = calc.calculate_shipping(calc.get_subtotal())
        self.assertAlmostEqual(shipping, 0.0)

    def test_edge_numeric_free_shipping_threshold_just_below(self):
        calc = OrderCalculator(free_shipping_threshold=100.0)
        calc.add_item('a', 49.99, 2)
        shipping = calc.calculate_shipping(calc.get_subtotal())
        self.assertAlmostEqual(shipping, 10.0)

    def test_edge_numeric_tax_and_shipping_zero(self):
        calc = OrderCalculator(tax_rate=0.0, shipping_cost=0.0)
        calc.add_item('a', 50.0, 1)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 50.0)

    def test_edge_numeric_tax_full_and_shipping_zero(self):
        calc = OrderCalculator(tax_rate=1.0, shipping_cost=0.0)
        calc.add_item('a', 50.0, 1)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 100.0)

    def test_exception_propagation_invalid_inputs_calculate_total(self):
        calc = OrderCalculator()
        calc.add_item('a', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-5.0)

    def test_performance_large_batch(self):
        calc = OrderCalculator()
        for i in range(10000):
            calc.add_item(f'item{i}', 1.0, 1)
        self.assertEqual(calc.total_items(), 10000)
        self.assertAlmostEqual(calc.get_subtotal(), 10000.0)

    def test_method_chaining_clear_order_idempotent(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.clear_order()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_method_chaining_add_item_accumulate(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.add_item('a', 1.0, 2)
        self.assertEqual(calc.total_items(), 3)

    def test_method_chaining_calculate_total_multiple(self):
        calc = OrderCalculator()
        calc.add_item('a', 10.0, 1)
        total1 = calc.calculate_total()
        total2 = calc.calculate_total()
        self.assertAlmostEqual(total1, total2)

    def test_method_chaining_get_subtotal_after_modifications(self):
        calc = OrderCalculator()
        calc.add_item('a', 5.0, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 10.0)
        calc.add_item('b', 3.0, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 13.0)

    def test_method_chaining_list_items_after_modifications(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.add_item('b', 2.0, 1)
        self.assertEqual(set(calc.list_items()), {'a', 'b'})
if __name__ == '__main__':
    unittest.main()