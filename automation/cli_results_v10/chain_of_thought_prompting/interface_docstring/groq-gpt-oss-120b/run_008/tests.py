import unittest
from decimal import Decimal
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_init_valid_custom(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0.0)
        self.assertEqual(oc.shipping_cost, 0.0)

    def test_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='big')

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_add_item_normal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(oc.total_items(), 2)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_add_item_quantity_aggregation(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.total_items(), 5)
        self.assertAlmostEqual(oc.get_subtotal(), 7.5)

    def test_add_item_name_conflict_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0, 1)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_zero_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Banana', 0, 1)

    def test_add_item_negative_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Banana', -0.5, 1)

    def test_add_item_quantity_less_than_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Banana', 0.5, 0)

    def test_add_item_name_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_price_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Banana', 'free', 1)

    def test_add_item_quantity_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Banana', 0.5, 2.5)

    def test_add_item_price_as_int(self):
        oc = OrderCalculator()
        oc.add_item('Orange', 2, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 2.0)

    def test_add_item_very_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Gadget', 9.99, 10000)
        self.assertEqual(oc.total_items(), 10000)
        self.assertAlmostEqual(oc.get_subtotal(), 9.99 * 10000)

    def test_add_item_whitespace_name(self):
        oc = OrderCalculator()
        oc.add_item('  Pear  ', 1.0, 1)
        self.assertIn('  Pear  ', oc.list_items())

    def test_add_item_boolean_as_numeric(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('BoolItem', True, False)

    def test_add_item_decimal_price(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('DecimalItem', Decimal('1.23'), 1)

    def test_add_item_after_removal_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.remove_item('Apple')
        oc.add_item('Apple', 2.0, 1)
        self.assertEqual(oc.total_items(), 1)
        self.assertAlmostEqual(oc.get_subtotal(), 2.0)

    def test_remove_item_successful(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_remove_item_nonexistent(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        with self.assertRaises(ValueError):
            oc.remove_item('Pear')

    def test_remove_item_name_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_remove_item_after_aggregation(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_remove_item_from_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Anything')

    def test_get_subtotal_typical(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 3)
        oc.add_item('Banana', 1.0, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 8.0)

    def test_get_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Gizmo', 9.99, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 9.99)

    def test_get_subtotal_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_get_subtotal_floating_point(self):
        oc = OrderCalculator()
        oc.add_item('Item', 0.1, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 0.3, places=7)

    def test_get_subtotal_very_small_price(self):
        oc = OrderCalculator()
        oc.add_item('Micro', 0.0001, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 0.0001)

    def test_get_subtotal_very_large(self):
        oc = OrderCalculator()
        oc.add_item('Mega', 1000000.0, 1000)
        self.assertAlmostEqual(oc.get_subtotal(), 1000000000.0)

    def test_get_subtotal_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 3)
        oc.add_item('Banana', 1.0, 2)
        oc.remove_item('Apple')
        self.assertAlmostEqual(oc.get_subtotal(), 2.0)

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_twenty_percent(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(200.0, 0.2), 160.0)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(50.0, -0.1)

    def test_apply_discount_over_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(50.0, 1.5)

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 0.1)

    def test_apply_discount_subtotal_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('ten', 0.1)

    def test_apply_discount_discount_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(10.0, 'half')

    def test_apply_discount_subtotal_int(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(120, 0.1), 108.0)

    def test_apply_discount_discount_int_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0), 100.0)

    def test_apply_discount_discount_int_one(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 1), 0.0)

    def test_apply_discount_boolean_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(10, True)

    def test_apply_discount_decimal_inputs(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(Decimal('100'), Decimal('0.2'))

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_custom_parameters(self):
        oc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        self.assertAlmostEqual(oc.calculate_shipping(30), 5.0)

    def test_calculate_shipping_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('twenty')

    def test_calculate_shipping_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_shipping(-5.0)

    def test_calculate_shipping_zero_subtotal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_very_large(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(1000000000.0), 0.0)

    def test_calculate_shipping_boolean_input(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping(True)

    def test_calculate_tax_typical(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(200.0), 46.0)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-10.0)

    def test_calculate_tax_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax([100])

    def test_calculate_tax_integer_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(100), 23.0)

    def test_calculate_tax_boolean_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax(False)

    def test_calculate_tax_decimal_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax(Decimal('100'))

    def test_calculate_tax_very_large(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(1000000000.0), 230000000.0)

    def test_calculate_total_no_discount_shipping_needed(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        self.assertAlmostEqual(oc.calculate_total(0.0), 61.5)

    def test_calculate_total_twenty_percent_discount(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        self.assertAlmostEqual(oc.calculate_total(0.2), 51.66, places=2)

    def test_calculate_total_thirty_percent_discount(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        self.assertAlmostEqual(oc.calculate_total(0.3), 46.74, places=2)

    def test_calculate_total_fifty_percent_discount(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        self.assertAlmostEqual(oc.calculate_total(0.5), 36.9)

    def test_calculate_total_sixty_percent_discount(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        self.assertAlmostEqual(oc.calculate_total(0.6), 31.98, places=2)

    def test_calculate_total_seventy_five_percent_discount(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        self.assertAlmostEqual(oc.calculate_total(0.75), 24.6)

    def test_calculate_total_free_shipping_no_discount(self):
        oc = OrderCalculator()
        oc.add_item('Expensive', 120, 1)
        self.assertAlmostEqual(oc.calculate_total(0.0), 147.6)

    def test_calculate_total_free_shipping_after_discount_still_above(self):
        oc = OrderCalculator()
        oc.add_item('Expensive', 150, 1)
        self.assertAlmostEqual(oc.calculate_total(0.2), 147.6)

    def test_calculate_total_free_shipping_after_discount_below(self):
        oc = OrderCalculator()
        oc.add_item('Expensive', 150, 1)
        self.assertAlmostEqual(oc.calculate_total(0.4), 123.0)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total(0.0)

    def test_calculate_total_invalid_discount_negative(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        with self.assertRaises(ValueError):
            oc.calculate_total(-0.1)

    def test_calculate_total_invalid_discount_over_one(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        with self.assertRaises(ValueError):
            oc.calculate_total(1.2)

    def test_calculate_total_discount_wrong_type(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        with self.assertRaises(TypeError):
            oc.calculate_total('half')

    def test_calculate_total_custom_tax_rate(self):
        oc = OrderCalculator(tax_rate=0.1)
        oc.add_item('Item', 50, 1)
        self.assertAlmostEqual(oc.calculate_total(0.0), 66.0)

    def test_calculate_total_custom_shipping_and_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        oc.add_item('Item', 40, 1)
        self.assertAlmostEqual(oc.calculate_total(0.0), 55.35, places=2)

    def test_calculate_total_discount_exactly_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 120, 1)
        discount = (120 - 100) / 120
        total = oc.calculate_total(discount)
        self.assertAlmostEqual(total, 147.6)

    def test_calculate_total_full_discount(self):
        oc = OrderCalculator()
        oc.add_item('Item', 80, 1)
        total = oc.calculate_total(1.0)
        self.assertAlmostEqual(total, 12.3, places=2)

    def test_calculate_total_very_large_order(self):
        oc = OrderCalculator()
        oc.add_item('Bulk', 9.99, 10000)
        total = oc.calculate_total(0.05)
        discounted = 9.99 * 10000 * 0.95
        tax = discounted * 0.23
        expected = discounted + tax
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_boolean_discount(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        with self.assertRaises(TypeError):
            oc.calculate_total(True)

    def test_calculate_total_decimal_discount(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        with self.assertRaises(TypeError):
            oc.calculate_total(Decimal('0.2'))

    def test_calculate_total_discount_int_zero(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        self.assertAlmostEqual(oc.calculate_total(0), 61.5)

    def test_calculate_total_discount_int_one(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        total = oc.calculate_total(1)
        self.assertAlmostEqual(total, 12.3, places=2)

    def test_calculate_total_tax_on_discounted_plus_shipping(self):
        oc = OrderCalculator()
        oc.add_item('Item', 80, 1)
        total = oc.calculate_total(0.25)
        discounted = 60.0
        shipping = 10.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_no_side_effects(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        first = oc.calculate_total(0.0)
        second = oc.calculate_total(0.0)
        self.assertAlmostEqual(first, second)

    def test_calculate_total_state_after_exception(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        with self.assertRaises(ValueError):
            oc.calculate_total(-0.1)
        self.assertFalse(oc.is_empty())

    def test_calculate_total_after_clearing(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        oc.clear_order()
        with self.assertRaises(ValueError):
            oc.calculate_total(0.0)

    def test_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_single(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        self.assertEqual(oc.total_items(), 1)

    def test_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 3)
        oc.add_item('Banana', 2.0, 2)
        self.assertEqual(oc.total_items(), 5)

    def test_total_items_aggregation(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Apple', 1.0, 4)
        self.assertEqual(oc.total_items(), 6)

    def test_total_items_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Gadget', 9.99, 10000)
        self.assertEqual(oc.total_items(), 10000)

    def test_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 3)
        oc.add_item('Banana', 2.0, 2)
        oc.remove_item('Apple')
        self.assertEqual(oc.total_items(), 2)

    def test_total_items_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 3)
        oc.clear_order()
        self.assertEqual(oc.total_items(), 0)

    def test_list_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_list_items_single(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_list_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('Banana', 2.0, 1)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana'])

    def test_list_items_duplicate_name(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('Apple', 1.0, 2)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_list_items_same_price_different_names(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('Banana', 1.0, 1)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana'])

    def test_list_items_whitespace_name(self):
        oc = OrderCalculator()
        oc.add_item('  Pear  ', 1.0, 1)
        self.assertIn('  Pear  ', oc.list_items())

    def test_list_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.remove_item('Apple')
        self.assertEqual(oc.list_items(), [])

    def test_list_items_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.clear_order()
        self.assertEqual(oc.list_items(), [])

    def test_is_empty_fresh(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_add(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_remove_only(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_multiple_ops(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('Banana', 2.0, 1)
        oc.remove_item('Apple')
        oc.remove_item('Banana')
        self.assertTrue(oc.is_empty())

    def test_clear_order_populated(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('Banana', 2.0, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)
        self.assertEqual(oc.list_items(), [])

    def test_clear_order_idempotent(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_clear_order_then_add(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.clear_order()
        oc.add_item('Banana', 2.0, 1)
        self.assertFalse(oc.is_empty())
        self.assertCountEqual(oc.list_items(), ['Banana'])

    def test_interaction_add_remove_add_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.remove_item('Apple')
        oc.add_item('Apple', 2, 1)
        self.assertEqual(oc.total_items(), 1)
        self.assertAlmostEqual(oc.get_subtotal(), 2.0)

    def test_interaction_add_duplicate_then_remove(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Apple', 1, 3)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_interaction_full_workflow(self):
        oc = OrderCalculator()
        oc.add_item('A', 30, 1)
        oc.add_item('B', 20, 2)
        subtotal = oc.get_subtotal()
        self.assertAlmostEqual(subtotal, 70.0)
        discounted = oc.apply_discount(subtotal, 0.1)
        self.assertAlmostEqual(discounted, 63.0)
        shipping = oc.calculate_shipping(discounted)
        self.assertAlmostEqual(shipping, 10.0)
        tax = oc.calculate_tax(discounted + shipping)
        self.assertAlmostEqual(tax, 16.79, places=2)
        total = oc.calculate_total(0.1)
        self.assertAlmostEqual(total, 63.0 + 10.0 + 16.79, places=2)

    def test_interaction_custom_config_full_workflow(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=5)
        oc.add_item('X', 40, 1)
        total = oc.calculate_total(0.0)
        self.assertAlmostEqual(total, 55.35, places=2)

    def test_interaction_repeated_total_calls(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        first = oc.calculate_total(0.0)
        second = oc.calculate_total(0.0)
        self.assertAlmostEqual(first, second)

    def test_interaction_state_after_failed_add(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Bad', -1, 1)
        oc.add_item('Good', 1, 1)
        self.assertEqual(oc.total_items(), 1)

    def test_interaction_sequential_ops(self):
        oc = OrderCalculator()
        oc.add_item('A', 10, 1)
        oc.add_item('B', 20, 2)
        oc.remove_item('A')
        oc.add_item('C', 5, 3)
        self.assertCountEqual(oc.list_items(), ['B', 'C'])
        self.assertEqual(oc.total_items(), 5)

    def test_interaction_small_price_large_discount(self):
        oc = OrderCalculator()
        oc.add_item('Micro', 0.0001, 1)
        total = oc.calculate_total(0.9999)
        self.assertGreaterEqual(total, 0.0)

    def test_interaction_boolean_arguments(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        with self.assertRaises(TypeError):
            oc.apply_discount(100, True)
        with self.assertRaises(TypeError):
            oc.calculate_shipping(True)
        with self.assertRaises(TypeError):
            oc.calculate_tax(True)
        with self.assertRaises(TypeError):
            oc.calculate_total(True)

    def test_interaction_decimal_inputs(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Decimal', Decimal('1.0'), 1)
        with self.assertRaises(TypeError):
            oc.apply_discount(Decimal('100'), 0.1)
        with self.assertRaises(TypeError):
            oc.calculate_shipping(Decimal('10'))
        with self.assertRaises(TypeError):
            oc.calculate_tax(Decimal('5'))
        with self.assertRaises(TypeError):
            oc.calculate_total(Decimal('0.1'))

    def test_edge_extremely_small_floats(self):
        oc = OrderCalculator()
        oc.add_item('Tiny', 1e-07, 1)
        total = oc.calculate_total(0.0)
        self.assertGreaterEqual(total, 0.0)

    def test_edge_extremely_large_numbers(self):
        oc = OrderCalculator()
        oc.add_item('Huge', 1000000000000.0, int(1000000.0))
        total = oc.calculate_total(0.0)
        self.assertTrue(total > 0)

    def test_edge_mixed_int_float_invalid(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Mixed', 5, 2.5)

    def test_edge_whitespace_only_name(self):
        oc = OrderCalculator()
        oc.add_item('   ', 1.0, 1)
        self.assertIn('   ', oc.list_items())

    def test_edge_case_sensitive_names(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('apple', 1.0, 1)
        self.assertCountEqual(oc.list_items(), ['Apple', 'apple'])

    def test_edge_negative_zero_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('NegZero', -0.0, 1)

    def test_edge_zero_shipping_cost(self):
        oc = OrderCalculator(shipping_cost=0)
        oc.add_item('Item', 40, 1)
        self.assertAlmostEqual(oc.calculate_shipping(0), 0.0)

    def test_edge_zero_free_shipping_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=0)
        oc.add_item('Item', 10, 1)
        self.assertAlmostEqual(oc.calculate_shipping(5), 0.0)

    def test_edge_tax_rate_one(self):
        oc = OrderCalculator(tax_rate=1.0)
        oc.add_item('Item', 50, 1)
        total = oc.calculate_total(0.0)
        self.assertAlmostEqual(total, 110.0)

    def test_edge_tax_rate_zero(self):
        oc = OrderCalculator(tax_rate=0.0)
        oc.add_item('Item', 50, 1)
        total = oc.calculate_total(0.0)
        self.assertAlmostEqual(total, 60.0)