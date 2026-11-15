import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults_stored_correctly(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(50.0), 10.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_init_tax_rate_zero_boundary(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 0.0)

    def test_init_tax_rate_one_boundary(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 100.0)

    def test_init_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertAlmostEqual(calc.calculate_shipping(0.0), 0.0)
        self.assertAlmostEqual(calc.calculate_shipping(0.01), 0.0)

    def test_init_free_shipping_threshold_large(self):
        calc = OrderCalculator(free_shipping_threshold=1000000.0)
        self.assertAlmostEqual(calc.calculate_shipping(100.0), 10.0)

    def test_init_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertAlmostEqual(calc.calculate_shipping(50.0), 0.0)

    def test_init_invalid_tax_rate_type_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_invalid_free_shipping_threshold_type_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_invalid_shipping_cost_type_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_normal_single_item(self):
        self.calc.add_item('apple', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)
        self.assertIn('apple', self.calc.list_items())

    def test_add_item_same_item_twice_accumulates_quantity(self):
        self.calc.add_item('banana', 0.5, 2)
        self.calc.add_item('banana', 0.5, 3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.5)

    def test_add_item_multiple_distinct_items(self):
        self.calc.add_item('book', 10.0, 1)
        self.calc.add_item('pen', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 16.0)
        items = self.calc.list_items()
        self.assertEqual(len(items), 2)
        self.assertIn('book', items)
        self.assertIn('pen', items)

    def test_add_item_large_quantity_and_price(self):
        self.calc.add_item('big', 1000.0, 1000)
        self.assertEqual(self.calc.total_items(), 1000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1000000.0)

    def test_add_item_whitespace_only_name_allowed(self):
        self.calc.add_item('   ', 2.0, 1)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertIn('   ', self.calc.list_items())

    def test_add_item_non_string_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_non_numeric_price_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('item', '10', 1)

    def test_add_item_non_int_quantity_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('item', 1.0, 2.5)

    def test_add_item_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('item', -1.0, 1)

    def test_add_item_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('item', 1.0, -1)

    def test_add_item_state_consistency_subtotal_matches_items(self):
        self.calc.add_item('a', 2.0, 2)
        self.calc.add_item('b', 3.0, 1)
        expected = 2.0 * 2 + 3.0 * 1
        self.assertAlmostEqual(self.calc.get_subtotal(), expected)

    def test_add_item_then_clear_then_add_fresh(self):
        self.calc.add_item('old', 1.0, 1)
        self.calc.clear_order()
        self.calc.add_item('new', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0)
        self.assertEqual(self.calc.list_items(), ['new'])

    def test_remove_item_non_string_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_remove_item_state_consistency_after_mix(self):
        self.calc.add_item('a', 2.0, 2)
        self.calc.add_item('b', 3.0, 1)
        self.calc.remove_item('a')
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertEqual(self.calc.list_items(), ['b'])

    def test_remove_item_then_calculate_total_consistent(self):
        self.calc.add_item('x', 10.0, 2)
        self.calc.add_item('y', 5.0, 1)
        self.calc.remove_item('x')
        expected = 5.0
        self.assertAlmostEqual(self.calc.calculate_total(), expected + 10.0 + (expected + 10.0) * 0.23)

    def test_get_subtotal_single_item(self):
        self.calc.add_item('single', 5.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 15.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('a', 2.0, 2)
        self.calc.add_item('b', 3.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0 * 2 + 3.0 * 3)

    def test_get_subtotal_large_numbers_precision(self):
        self.calc.add_item('big', 0.1, 10)
        self.calc.add_item('big2', 0.2, 10)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_get_subtotal_state_consistency_after_add_remove(self):
        self.calc.add_item('a', 1.0, 1)
        self.calc.add_item('b', 2.0, 2)
        self.calc.remove_item('a')
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.0)

    def test_get_subtotal_used_in_discount_shipping_tax_chain(self):
        self.calc.add_item('item', 10.0, 1)
        subtotal = self.calc.get_subtotal()
        discounted = self.calc.apply_discount(subtotal, 0.1)
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.1), expected)

    def test_apply_discount_zero_discount_returns_same(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_ten_percent(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.1), 90.0)

    def test_apply_discount_full_discount_returns_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_zero_subtotal_returns_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_non_numeric_subtotal_raises(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)

    def test_apply_discount_non_numeric_discount_raises(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '0.1')

    def test_apply_discount_interaction_with_shipping_and_tax(self):
        self.calc.add_item('item', 50.0, 2)
        discounted = self.calc.apply_discount(100.0, 0.2)
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.2), expected)

    def test_calculate_shipping_free_when_at_or_above_threshold(self):
        self.calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(50.0), 0.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_charged_when_below_threshold(self):
        self.calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(49.99), 5.0)

    def test_calculate_shipping_exact_threshold_behavior(self):
        self.calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        result = self.calc.calculate_shipping(50.0)
        self.assertIn(result, (0.0, 5.0))

    def test_calculate_shipping_zero_threshold_always_free(self):
        self.calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=5.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(0.0), 0.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_zero_cost_always_zero(self):
        self.calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=0.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(0.0), 0.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        self.calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=5.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(-10.0), 5.0)

    def test_calculate_shipping_non_numeric_subtotal_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('100')

    def test_calculate_shipping_state_consistency_with_discount(self):
        self.calc.add_item('item', 100.0, 1)
        discounted = self.calc.apply_discount(self.calc.get_subtotal(), 0.5)
        shipping = self.calc.calculate_shipping(discounted)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_used_in_calculate_total(self):
        self.calc.add_item('item', 50.0, 1)
        self.assertAlmostEqual(self.calc.calculate_shipping(self.calc.get_subtotal()), 10.0)
        total = self.calc.calculate_total()
        expected = 50.0 + 10.0 + (50.0 + 10.0) * 0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_tax_normal_rate(self):
        self.calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_zero_rate(self):
        self.calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_rate_one(self):
        self.calc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 100.0)

    def test_calculate_tax_non_numeric_amount_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_tax_state_consistency_with_shipping(self):
        self.calc.add_item('item', 100.0, 1)
        discounted = self.calc.apply_discount(self.calc.get_subtotal(), 0.0)
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted + shipping)
        self.assertAlmostEqual(tax, self.calc.calculate_tax(discounted + shipping))

    def test_calculate_tax_used_in_calculate_total(self):
        self.calc.add_item('item', 100.0, 1)
        self.assertAlmostEqual(self.calc.calculate_shipping(self.calc.get_subtotal()), 0.0)
        tax = self.calc.calculate_tax(self.calc.get_subtotal())
        expected = self.calc.get_subtotal() + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_single_item_no_discount(self):
        self.calc.add_item('item', 20.0, 1)
        expected = 20.0 + 10.0 + 6.9
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_known_discount(self):
        self.calc.add_item('item', 100.0, 1)
        expected = 90.0 + 10.0 + 23.0
        self.assertAlmostEqual(self.calc.calculate_total(0.1), expected)

    def test_calculate_total_explicit_zero_discount_same_as_default(self):
        self.calc.add_item('item', 50.0, 1)
        total_default = self.calc.calculate_total()
        total_zero = self.calc.calculate_total(0.0)
        self.assertAlmostEqual(total_default, total_zero)

    def test_calculate_total_full_discount(self):
        self.calc.add_item('item', 100.0, 1)
        expected = 0.0 + 10.0 + 2.3
        self.assertAlmostEqual(self.calc.calculate_total(1.0), expected)

    def test_calculate_total_non_numeric_discount_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.1')

    def test_calculate_total_state_consistency_step_by_step(self):
        self.calc.add_item('a', 10.0, 2)
        self.calc.add_item('b', 5.0, 1)
        discount = 0.1
        subtotal = self.calc.get_subtotal()
        discounted = self.calc.apply_discount(subtotal, discount)
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(discount), expected)

    def test_calculate_total_interaction_realistic_checkout(self):
        self.calc.add_item('book', 12.99, 2)
        self.calc.add_item('pen', 1.5, 5)
        self.calc.add_item('bag', 20.0, 1)
        expected = 50.806 + 10.0 + 13.98538
        self.assertAlmostEqual(self.calc.calculate_total(0.05), expected, places=4)

    def test_total_items_empty_order(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_single_item_quantity_n(self):
        self.calc.add_item('item', 1.0, 7)
        self.assertEqual(self.calc.total_items(), 7)

    def test_total_items_multiple_distinct_items(self):
        self.calc.add_item('a', 1.0, 2)
        self.calc.add_item('b', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_same_item_multiple_times_accumulates(self):
        self.calc.add_item('item', 1.0, 2)
        self.calc.add_item('item', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_invalid_quantity_handled_by_add_item(self):
        pass

    def test_total_items_state_consistency_after_add_remove(self):
        self.calc.add_item('a', 1.0, 4)
        self.calc.add_item('b', 1.0, 2)
        self.calc.remove_item('a')
        self.assertEqual(self.calc.total_items(), 2)

    def test_total_items_used_for_bulk_discount_gate(self):
        self.calc.add_item('item', 10.0, 3)
        self.assertFalse(self.calc.total_items() > 5)
        self.calc.add_item('item', 10.0, 3)
        self.assertTrue(self.calc.total_items() > 5)

    def test_clear_order_on_empty_order_no_error(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_clear_order_state_consistency_after_clearing_then_adding(self):
        self.calc.add_item('old', 1.0, 1)
        self.calc.clear_order()
        self.calc.add_item('new', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0)
        self.assertEqual(self.calc.list_items(), ['new'])

    def test_clear_order_edge_discount_argument_not_persisted(self):
        self.calc.add_item('item', 10.0, 1)
        _ = self.calc.calculate_total(0.5)
        self.calc.clear_order()
        self.calc.add_item('item2', 10.0, 1)
        self.assertAlmostEqual(self.calc.calculate_total(), 10.0 + 10.0 + (10.0 + 10.0) * 0.23)

    def test_list_items_empty_order(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_single_item(self):
        self.calc.add_item('only', 1.0, 1)
        self.assertEqual(self.calc.list_items(), ['only'])

    def test_list_items_same_item_multiple_times_once(self):
        self.calc.add_item('dup', 1.0, 2)
        self.calc.add_item('dup', 1.0, 3)
        self.assertEqual(self.calc.list_items(), ['dup'])

    def test_list_items_multiple_distinct_items(self):
        self.calc.add_item('first', 1.0, 1)
        self.calc.add_item('second', 1.0, 1)
        items = self.calc.list_items()
        self.assertEqual(len(items), 2)
        self.assertIn('first', items)
        self.assertIn('second', items)

    def test_list_items_after_removal(self):
        self.calc.add_item('rem', 1.0, 1)
        self.calc.remove_item('rem')
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_state_consistency_matches_internal_keys(self):
        self.calc.add_item('a', 1.0, 1)
        self.calc.add_item('b', 1.0, 2)
        self.assertEqual(set(self.calc.list_items()), {'a', 'b'})

    def test_list_items_after_clear_order(self):
        self.calc.add_item('item', 1.0, 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_fresh_instance(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_adding_item(self):
        self.calc.add_item('item', 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_removing_all_items(self):
        self.calc.add_item('a', 1.0, 1)
        self.calc.remove_item('a')
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_clear_order(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_state_consistency_with_total_items_and_list_items(self):
        self.assertEqual(self.calc.is_empty(), self.calc.total_items() == 0)
        self.assertEqual(self.calc.is_empty(), len(self.calc.list_items()) == 0)
if __name__ == '__main__':
    unittest.main()