import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(1.0), 0.23)
        self.assertEqual(calc.calculate_shipping(50.0), 10.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_tax(1.0), 0.05)
        self.assertEqual(calc.calculate_shipping(40.0), 5.0)
        self.assertEqual(calc.calculate_shipping(60.0), 0.0)

    def test_init_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(10.0), 0.0)

    def test_init_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.calculate_tax(10.0), 10.0)

    def test_init_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)
        self.assertEqual(calc.calculate_shipping(-1.0), 10.0)

    def test_init_free_shipping_threshold_large(self):
        calc = OrderCalculator(free_shipping_threshold=1000000.0)
        self.assertEqual(calc.calculate_shipping(100000.0), 10.0)

    def test_init_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_init_shipping_cost_large(self):
        calc = OrderCalculator(shipping_cost=20.0)
        self.assertEqual(calc.calculate_shipping(50.0), 20.0)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_non_numeric_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_non_numeric_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_non_numeric_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_new(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0, 2)
        self.assertEqual(calc.total_items(), 2)
        self.assertEqual(calc.get_subtotal(), 2.0)
        self.assertIn('apple', calc.list_items())

    def test_add_item_existing_increase_quantity(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0, 1)
        calc.add_item('apple', 1.0, 3)
        self.assertEqual(calc.total_items(), 4)
        self.assertEqual(calc.get_subtotal(), 4.0)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('banana', 0.5)
        self.assertEqual(calc.total_items(), 1)
        self.assertEqual(calc.get_subtotal(), 0.5)

    def test_add_item_multiple_different(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.add_item('b', 2.0, 2)
        self.assertEqual(calc.total_items(), 3)
        self.assertEqual(calc.get_subtotal(), 5.0)

    def test_add_item_price_zero(self):
        calc = OrderCalculator()
        calc.add_item('free', 0.0, 5)
        self.assertEqual(calc.total_items(), 5)
        self.assertEqual(calc.get_subtotal(), 0.0)

    def test_add_item_large_price(self):
        calc = OrderCalculator()
        calc.add_item('expensive', 1000000000.0, 2)
        self.assertEqual(calc.get_subtotal(), 2000000000.0)

    def test_add_item_quantity_zero(self):
        calc = OrderCalculator()
        calc.add_item('zero', 10.0, 0)
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.get_subtotal(), 0.0)

    def test_add_item_fractional_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('frac', 1.0, 1.5)

    def test_add_item_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_add_item_negative_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('bad', -1.0, 1)

    def test_add_item_non_numeric_price(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('bad', '1.0', 1)

    def test_add_item_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('bad', 1.0, -1)

    def test_add_item_non_integer_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('bad', 1.0, 2.5)

    def test_add_item_subtotal_consistency(self):
        calc = OrderCalculator()
        calc.add_item('a', 2.0, 3)
        calc.add_item('b', 1.0, 4)
        self.assertEqual(calc.get_subtotal(), 2.0 * 3 + 1.0 * 4)

    def test_add_item_total_items_consistency(self):
        calc = OrderCalculator()
        calc.add_item('a', 2.0, 3)
        calc.add_item('b', 1.0, 4)
        self.assertEqual(calc.total_items(), 3 + 4)

    def test_add_item_idempotent_same_call(self):
        calc = OrderCalculator()
        calc.add_item('x', 1.0, 1)
        calc.add_item('x', 1.0, 1)
        self.assertEqual(calc.total_items(), 2)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 2)
        calc.add_item('b', 2.0, 3)
        calc.remove_item('a')
        self.assertEqual(calc.total_items(), 3)
        self.assertEqual(calc.get_subtotal(), 2.0 * 3)
        self.assertNotIn('a', calc.list_items())

    def test_remove_item_existing_multiple_quantity(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 5)
        calc.remove_item('a')
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.get_subtotal(), 0.0)

    def test_remove_item_after_multiple_adds(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 2)
        calc.add_item('a', 1.0, 3)
        calc.remove_item('a')
        self.assertEqual(calc.total_items(), 0)

    def test_remove_item_missing(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('nonexistent')

    def test_remove_item_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_subtotal_consistency(self):
        calc = OrderCalculator()
        calc.add_item('a', 2.0, 3)
        calc.add_item('b', 3.0, 2)
        calc.remove_item('a')
        self.assertEqual(calc.get_subtotal(), 3.0 * 2)

    def test_remove_item_idempotent_second_call(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.remove_item('a')
        calc.remove_item('a')
        self.assertEqual(calc.total_items(), 0)

    def test_remove_item_all_then_empty(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.remove_item('a')
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('a', 2.0, 3)
        calc.add_item('b', 1.0, 4)
        self.assertEqual(calc.get_subtotal(), 2.0 * 3 + 1.0 * 4)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('a', 5.0, 2)
        self.assertEqual(calc.get_subtotal(), 10.0)

    def test_get_subtotal_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.get_subtotal(), 0.0)

    def test_get_subtotal_zero_price(self):
        calc = OrderCalculator()
        calc.add_item('free', 0.0, 5)
        self.assertEqual(calc.get_subtotal(), 0.0)

    def test_get_subtotal_zero_quantity(self):
        calc = OrderCalculator()
        calc.add_item('zero', 10.0, 0)
        self.assertEqual(calc.get_subtotal(), 0.0)

    def test_get_subtotal_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('big', 1000000.0, 1000000.0)
        self.assertEqual(calc.get_subtotal(), 1000000000000.0)

    def test_get_subtotal_after_add_remove(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.add_item('b', 2.0, 1)
        calc.remove_item('a')
        self.assertEqual(calc.get_subtotal(), 2.0)

    def test_get_subtotal_idempotent(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        v1 = calc.get_subtotal()
        v2 = calc.get_subtotal()
        self.assertEqual(v1, v2)

    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 0.1), 90.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_zero_subtotal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_small_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(0.0001, 0.5), 5e-05)

    def test_apply_discount_large_subtotal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(1000000000.0, 0.1), 900000000.0)

    def test_apply_discount_negative_subtotal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(-50.0, 0.1), -45.0)

    def test_apply_discount_negative_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_above_one(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.2)

    def test_apply_discount_non_numeric_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_non_numeric_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.1')

    def test_apply_discount_chaining(self):
        calc = OrderCalculator()
        calc.add_item('a', 10.0, 5)
        subtotal = calc.get_subtotal()
        discounted = calc.apply_discount(subtotal, 0.2)
        shipping = calc.calculate_shipping(discounted)
        tax = calc.calculate_tax(discounted + shipping)
        total = discounted + shipping + tax
        self.assertEqual(calc.calculate_total(0.2), total)

    def test_apply_discount_idempotent(self):
        calc = OrderCalculator()
        v1 = calc.apply_discount(50.0, 0.1)
        v2 = calc.apply_discount(50.0, 0.1)
        self.assertEqual(v1, v2)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_at_threshold_free(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_at_threshold_cost(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        result = calc.calculate_shipping(100.0)
        self.assertIn(result, (0.0, 10.0))

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(-50.0), 10.0)

    def test_calculate_shipping_zero_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_large_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(1000000000.0), 0.0)

    def test_calculate_shipping_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('100')

    def test_calculate_shipping_chaining(self):
        calc = OrderCalculator()
        calc.add_item('a', 10.0, 5)
        subtotal = calc.get_subtotal()
        discounted = calc.apply_discount(subtotal, 0.1)
        shipping = calc.calculate_shipping(discounted)
        self.assertEqual(shipping, calc.calculate_shipping(discounted))

    def test_calculate_shipping_idempotent(self):
        calc = OrderCalculator()
        v1 = calc.calculate_shipping(50.0)
        v2 = calc.calculate_shipping(50.0)
        self.assertEqual(v1, v2)

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.2)
        self.assertEqual(calc.calculate_tax(50.0), 10.0)

    def test_calculate_tax_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_small(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(calc.calculate_tax(0.001), 5e-05)

    def test_calculate_tax_large(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(1000000000.0), 230000000.0)

    def test_calculate_tax_negative(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(-10.0), -2.3)

    def test_calculate_tax_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('10')

    def test_calculate_tax_chaining(self):
        calc = OrderCalculator()
        calc.add_item('a', 10.0, 2)
        subtotal = calc.get_subtotal()
        discounted = calc.apply_discount(subtotal, 0.1)
        shipping = calc.calculate_shipping(discounted)
        tax = calc.calculate_tax(discounted + shipping)
        self.assertEqual(tax, calc.calculate_tax(discounted + shipping))

    def test_calculate_tax_idempotent(self):
        calc = OrderCalculator()
        v1 = calc.calculate_tax(50.0)
        v2 = calc.calculate_tax(50.0)
        self.assertEqual(v1, v2)

    def test_calculate_total_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('a', 10.0, 2)
        calc.add_item('b', 5.0, 3)
        expected = calc.get_subtotal() + calc.calculate_shipping(calc.get_subtotal()) + calc.calculate_tax(calc.get_subtotal() + calc.calculate_shipping(calc.get_subtotal()))
        self.assertEqual(calc.calculate_total(), expected)

    def test_calculate_total_discount_below_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0, tax_rate=0.1)
        calc.add_item('a', 60.0, 1)
        expected = 48.0 + 10.0 + calc.calculate_tax(48.0 + 10.0)
        self.assertEqual(calc.calculate_total(0.2), expected)

    def test_calculate_total_discount_at_or_above_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0, tax_rate=0.1)
        calc.add_item('a', 150.0, 1)
        expected = 120.0 + 0.0 + calc.calculate_tax(120.0 + 0.0)
        self.assertEqual(calc.calculate_total(0.2), expected)

    def test_calculate_total_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_total(), 0.0)

    def test_calculate_total_zero_discount(self):
        calc = OrderCalculator()
        calc.add_item('a', 10.0, 1)
        self.assertEqual(calc.calculate_total(0.0), calc.calculate_total())

    def test_calculate_total_full_discount(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0, tax_rate=0.1)
        calc.add_item('a', 50.0, 1)
        expected = 0.0 + 10.0 + calc.calculate_tax(10.0)
        self.assertEqual(calc.calculate_total(1.0), expected)

    def test_calculate_total_discount_above_one(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(1.5)

    def test_calculate_total_discount_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)

    def test_calculate_total_zero_price_items(self):
        calc = OrderCalculator()
        calc.add_item('free', 0.0, 5)
        self.assertEqual(calc.calculate_total(), calc.calculate_shipping(0.0) + calc.calculate_tax(0.0 + calc.calculate_shipping(0.0)))

    def test_calculate_total_zero_quantity_items(self):
        calc = OrderCalculator()
        calc.add_item('zero', 10.0, 0)
        self.assertEqual(calc.calculate_total(), 0.0)

    def test_calculate_total_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('big', 1000000.0, 2)
        self.assertEqual(calc.calculate_total(), calc.get_subtotal() * 1.23 + calc.calculate_shipping(calc.get_subtotal() * 1.23) + calc.calculate_tax(calc.get_subtotal() * 1.23 + calc.calculate_shipping(calc.get_subtotal() * 1.23)))

    def test_calculate_total_non_numeric_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_total('0.1')

    def test_calculate_total_state_interaction(self):
        calc = OrderCalculator()
        calc.add_item('a', 10.0, 2)
        calc.add_item('b', 5.0, 1)
        manual = calc.get_subtotal()
        disc = calc.apply_discount(manual, 0.1)
        ship = calc.calculate_shipping(disc)
        tax = calc.calculate_tax(disc + ship)
        expected = disc + ship + tax
        self.assertEqual(calc.calculate_total(0.1), expected)

    def test_calculate_total_idempotent(self):
        calc = OrderCalculator()
        calc.add_item('a', 10.0, 1)
        v1 = calc.calculate_total(0.1)
        v2 = calc.calculate_total(0.1)
        self.assertEqual(v1, v2)

    def test_calculate_total_exception_propagation(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)

    def test_total_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 2)
        calc.add_item('b', 2.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_single(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 4)
        self.assertEqual(calc.total_items(), 4)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_zero_quantity(self):
        calc = OrderCalculator()
        calc.add_item('zero', 1.0, 0)
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('neg', 1.0, -1)

    def test_total_items_large(self):
        calc = OrderCalculator()
        calc.add_item('big', 1.0, 10 ** 6)
        self.assertEqual(calc.total_items(), 10 ** 6)

    def test_total_items_state_interaction(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 2)
        self.assertEqual(calc.total_items(), 2)
        calc.remove_item('a')
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_idempotent(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        v1 = calc.total_items()
        v2 = calc.total_items()
        self.assertEqual(v1, v2)

    def test_clear_order_normal(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.get_subtotal(), 0.0)
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_state_interaction(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.clear_order()
        calc.add_item('b', 2.0, 1)
        self.assertEqual(calc.total_items(), 1)
        self.assertEqual(calc.get_subtotal(), 2.0)

    def test_clear_order_idempotent(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.clear_order()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_no_exception(self):
        calc = OrderCalculator()
        try:
            calc.clear_order()
        except Exception:
            self.fail('clear_order raised Exception')

    def test_list_items_distinct(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.add_item('b', 1.0, 1)
        self.assertCountEqual(calc.list_items(), ['a', 'b'])

    def test_list_items_same_name_multiple_quantity(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 2)
        self.assertEqual(calc.list_items(), ['a'])

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_list_items_state_interaction(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        self.assertEqual(calc.list_items(), ['a'])
        calc.add_item('b', 1.0, 1)
        self.assertCountEqual(calc.list_items(), ['a', 'b'])
        calc.remove_item('a')
        self.assertEqual(calc.list_items(), ['b'])

    def test_list_items_idempotent(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        l1 = calc.list_items()
        l2 = calc.list_items()
        self.assertEqual(l1, l2)

    def test_list_items_type_safety(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        items = calc.list_items()
        self.assertIsInstance(items, list)
        for i in items:
            self.assertIsInstance(i, str)

    def test_is_empty_true_initially(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_after_add(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_true_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_zero_quantity_items(self):
        calc = OrderCalculator()
        calc.add_item('zero', 1.0, 0)
        self.assertFalse(calc.is_empty())

    def test_is_empty_state_interaction(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        calc.add_item('a', 1.0, 1)
        self.assertFalse(calc.is_empty())
        calc.remove_item('a')
        self.assertTrue(calc.is_empty())

    def test_is_empty_idempotent(self):
        calc = OrderCalculator()
        v1 = calc.is_empty()
        v2 = calc.is_empty()
        self.assertEqual(v1, v2)