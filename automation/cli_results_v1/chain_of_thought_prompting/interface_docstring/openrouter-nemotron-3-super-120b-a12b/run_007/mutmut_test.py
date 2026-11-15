import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default_parameters(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.list_items(), [])

    def test_init_custom_valid_values(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_tax_rate_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.2)

    def test_init_tax_rate_wrong_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_free_shipping_threshold_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_free_shipping_threshold_wrong_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_shipping_cost_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_shipping_cost_wrong_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    def test_add_item_first_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(calc.list_items(), ['Apple'])
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.5)
        self.assertEqual(calc.list_items(), ['Banana'])
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.5)

    def test_add_item_same_name_price_increases_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Orange', 2.0, 1)
        calc.add_item('Orange', 2.0, 3)
        self.assertEqual(calc.list_items(), ['Orange'])
        self.assertEqual(calc.total_items(), 4)
        self.assertAlmostEqual(calc.get_subtotal(), 8.0)

    def test_add_item_different_name_new_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 0.5, 2)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})
        self.assertEqual(calc.total_items(), 3)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0)

    def test_add_item_same_name_different_price_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.5)

    def test_add_item_empty_name_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    def test_add_item_name_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_price_non_positive_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 0.0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', -1.0)

    def test_add_item_price_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', '1.0')

    def test_add_item_quantity_less_than_one_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, -1)

    def test_add_item_quantity_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, 1.5)
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, '2')

    def test_add_item_many_distinct_items_state_consistency(self):
        calc = OrderCalculator()
        items = [('A', 1.0, 2), ('B', 2.5, 1), ('C', 0.5, 4)]
        for name, price, qty in items:
            calc.add_item(name, price, qty)
        expected_total_qty = sum((q for _, _, q in items))
        expected_subtotal = sum((p * q for _, p, q in items))
        self.assertEqual(calc.total_items(), expected_total_qty)
        self.assertAlmostEqual(calc.get_subtotal(), expected_subtotal)

    def test_remove_item_existing_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_remove_item_item_with_quantity_greater_than_one(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_remove_item_one_of_several_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 2)
        calc.remove_item('Apple')
        self.assertEqual(calc.list_items(), ['Banana'])
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 4.0)

    def test_remove_item_non_existent_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Apple')

    def test_remove_item_name_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_subsequent_operations_work(self):
        calc = OrderCalculator()
        calc.add_item('A', 10.0, 1)
        calc.add_item('B', 5.0, 2)
        calc.remove_item('A')
        self.assertAlmostEqual(calc.get_subtotal(), 10.0)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 3.0, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 6.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 2.0, 3)
        calc.add_item('B', 4.0, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 10.0)

    def test_get_subtotal_returns_float_even_if_integer(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 3)
        result = calc.get_subtotal()
        self.assertIsInstance(result, float)
        self.assertAlmostEqual(result, 6.0)

    def test_get_subtotal_empty_order_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_state_consistency_after_adds_removes(self):
        calc = OrderCalculator()
        calc.add_item('A', 2.0, 2)
        calc.add_item('B', 3.0, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 7.0)
        calc.remove_item('A')
        self.assertAlmostEqual(calc.get_subtotal(), 3.0)
        calc.add_item('C', 5.0, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 13.0)

    def test_apply_discount_zero_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_typical_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_fractional_result(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(55.5, 0.15), 55.5 * 0.85)

    def test_apply_discount_subtotal_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_negative_subtotal_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_discount_negative_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_above_one_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.2)

    def test_apply_discount_subtotal_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_discount_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.1')

    def test_calculate_shipping_amount_equals_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_amount_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_amount_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(40.0), 10.0)

    def test_calculate_shipping_amount_zero_threshold_positive(self):
        calc = OrderCalculator(free_shipping_threshold=10.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(0.0), 5.0)

    def test_calculate_shipping_amount_zero_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)

    def test_calculate_shipping_negative_amount(self):
        calc = OrderCalculator(free_shipping_threshold=10.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(-5.0), 5.0)

    def test_calculate_shipping_amount_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('10')

    def test_calculate_shipping_constructor_parameters_affect_result(self):
        calc1 = OrderCalculator(free_shipping_threshold=30.0, shipping_cost=7.0)
        calc2 = OrderCalculator(free_shipping_threshold=30.0, shipping_cost=7.0)
        self.assertEqual(calc1.calculate_shipping(20.0), 7.0)
        self.assertEqual(calc2.calculate_shipping(40.0), 0.0)

    def test_calculate_tax_amount_zero(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_positive_amount(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_fractional_amount(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(33.33), 33.33 * 0.23)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-1.0)

    def test_calculate_tax_amount_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_calculate_tax_uses_instance_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(calc.calculate_tax(200.0), 10.0)

    def test_calculate_tax_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(150.0), 0.0)

    def test_calculate_tax_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.calculate_tax(150.0), 150.0)

    def test_calculate_total_simple_order_no_discount_shipping_applied(self):
        calc = OrderCalculator(tax_rate=0.2, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Book', 20.0, 3)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 84.0)

    def test_calculate_total_order_qualifies_for_free_shipping(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item('A', 30.0, 2)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 66.0)

    def test_calculate_total_discount_brings_subtotal_below_threshold(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('A', 60.0, 2)
        total = calc.calculate_total(discount=0.4)
        self.assertAlmostEqual(total, 90.2)

    def test_calculate_total_discount_keeps_subtotal_above_threshold(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('A', 60.0, 2)
        total = calc.calculate_total(discount=0.1)
        self.assertAlmostEqual(total, 118.8)

    def test_calculate_total_full_discount(self):
        calc = OrderCalculator(tax_rate=0.2, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item('A', 30.0, 1)
        total = calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 6.0)

    def test_calculate_total_empty_order_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_discount_negative_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item('A', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.1)

    def test_calculate_total_discount_above_one_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item('A', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.2)

    def test_calculate_total_discount_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        calc.add_item('A', 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='0.1')

    def test_calculate_total_many_items_state_consistency(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=200.0, shipping_cost=20.0)
        items = [('A', 10.0, 5), ('B', 20.0, 3), ('C', 5.0, 10)]
        for name, price, qty in items:
            calc.add_item(name, price, qty)
        subtotal = sum((p * q for _, p, q in items))
        discount = 0.1
        discounted = subtotal * (1 - discount)
        shipping = 0.0 if discounted >= 200.0 else 20.0
        taxable = discounted + shipping
        expected = taxable * (1 + 0.05)
        self.assertAlmostEqual(calc.calculate_total(discount), expected)

    def test_calculate_total_uses_instance_parameters(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=5.0)
        calc.add_item('A', 50.0, 2)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 110.0)
        calc2 = OrderCalculator(tax_rate=0.2, free_shipping_threshold=80.0, shipping_cost=10.0)
        calc2.add_item('A', 50.0, 2)
        total2 = calc2.calculate_total()
        self.assertAlmostEqual(total2, 120.0)

    def test_calculate_total_does_not_mutate_order(self):
        calc = OrderCalculator()
        calc.add_item('A', 10.0, 2)
        calc.add_item('B', 5.0, 1)
        before_items = set(calc.list_items())
        before_total = calc.total_items()
        before_sub = calc.get_subtotal()
        calc.calculate_total()
        calc.calculate_total(discount=0.1)
        after_items = set(calc.list_items())
        after_total = calc.total_items()
        after_sub = calc.get_subtotal()
        self.assertEqual(before_items, after_items)
        self.assertEqual(before_total, after_total)
        self.assertAlmostEqual(before_sub, after_sub)

    def test_total_items_empty_order(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 3)
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 2.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_adding_same_item_again_increases_total(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('A', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_removal_decreases(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 4)
        calc.add_item('B', 2.0, 1)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 1)

    def test_total_items_after_clear_order(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 5)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_clears_non_empty_order(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 2.0, 2)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_clear_order_idempotent_on_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_adding_same_name_after_clear_starts_fresh(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.clear_order()
        calc.add_item('A', 1.0, 3)
        self.assertEqual(calc.total_items(), 3)
        self.assertEqual(calc.list_items(), ['A'])

    def test_list_items_empty_order(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_duplicate_name_same_price_quantity_increase(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('A', 1.0, 3)
        self.assertEqual(calc.list_items(), ['A'])

    def test_list_items_after_clear_order(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_is_empty_empty_order(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_non_empty_order(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_removing_last_item(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.remove_item('A')
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_clear_order(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_state_consistency_after_operations(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        calc.add_item('A', 1.0, 1)
        self.assertFalse(calc.is_empty())
        calc.add_item('B', 2.0, 1)
        self.assertFalse(calc.is_empty())
        calc.remove_item('A')
        self.assertFalse(calc.is_empty())
        calc.remove_item('B')
        self.assertTrue(calc.is_empty())
        calc.clear_order()
        self.assertTrue(calc.is_empty())