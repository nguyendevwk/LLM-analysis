import unittest
from unittest.mock import patch
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_init_custom_valid_values(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0.0)
        self.assertEqual(oc.shipping_cost, 0.0)
        self.assertTrue(oc.is_empty())

    def test_init_invalid_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_invalid_tax_rate_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_invalid_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_init_invalid_type_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_type_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_invalid_type_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_add_item_new(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(oc.list_items()), 1)
        self.assertEqual(oc.total_items(), 2)

    def test_add_item_increment_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8)
        self.assertEqual(oc.total_items(), 1)

    def test_add_item_price_just_above_zero(self):
        oc = OrderCalculator()
        oc.add_item('Gum', 0.0001)
        self.assertEqual(oc.total_items(), 1)

    def test_add_item_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Rice', 0.5, 10000)
        self.assertEqual(oc.total_items(), 10000)

    def test_add_item_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0)

    def test_add_item_name_not_string(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(None, 1.0)

    def test_add_item_price_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pen', 0)

    def test_add_item_price_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pen', -0.1)

    def test_add_item_price_not_numeric(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Pen', 'free')

    def test_add_item_quantity_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pen', 1.0, 0)

    def test_add_item_quantity_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pen', 1.0, -3)

    def test_add_item_quantity_not_int(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Pen', 1.0, 2.5)

    def test_add_item_quantity_bool(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Pen', 1.0, True)

    def test_remove_existing_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_remove_last_item_makes_empty(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_remove_nonexistent_name(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5)
        with self.assertRaises(ValueError):
            oc.remove_item('Banana')

    def test_remove_name_not_string(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5)
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_remove_name_with_whitespace(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5)
        with self.assertRaises(ValueError):
            oc.remove_item('  Apple  ')

    def test_get_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 0.8, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 5.9)

    def test_get_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Gum', 0.05)
        self.assertAlmostEqual(oc.get_subtotal(), 0.05)

    def test_get_subtotal_large_numbers(self):
        oc = OrderCalculator()
        oc.add_item('Widget', 999.99, 10000)
        self.assertAlmostEqual(oc.get_subtotal(), 999.99 * 10000)

    def test_get_subtotal_floating_point_rounding(self):
        oc = OrderCalculator()
        oc.add_item('Item', 0.1, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 0.3)

    def test_get_subtotal_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_no_discount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 1.0), 0.0)

    def test_apply_discount_typical(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(200, 0.2), 160.0)

    def test_apply_discount_zero_subtotal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(0, 0.5), 0.0)

    def test_apply_discount_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, -0.1)

    def test_apply_discount_discount_over_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, 1.5)

    def test_apply_discount_subtotal_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-5, 0.1)

    def test_apply_discount_subtotal_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)

    def test_apply_discount_discount_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100, None)

    def test_apply_discount_discount_as_integer(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0), 100.0)
        self.assertAlmostEqual(oc.apply_discount(100, 1), 0.0)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_zero_subtotal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_custom_threshold_and_cost(self):
        oc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        self.assertAlmostEqual(oc.calculate_shipping(49.9), 5.0)

    def test_calculate_shipping_custom_at_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        self.assertAlmostEqual(oc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_input_not_number(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('50')

    def test_calculate_shipping_negative_subtotal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(-10), 10.0)

    def test_calculate_tax_typical_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(100), 23.0)

    def test_calculate_tax_zero_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0), 0.0)

    def test_calculate_tax_large_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(1000000), 230000)

    def test_calculate_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5)

    def test_calculate_tax_non_numeric(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax([100])

    def test_calculate_tax_int_vs_float(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(100), oc.calculate_tax(100.0))

    def test_calculate_total_shipping_applied_no_discount(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 10, 2)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 36.9)

    def test_calculate_total_free_shipping(self):
        oc = OrderCalculator()
        oc.add_item('Laptop', 150, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 184.5)

    def test_calculate_total_discount_pushes_below_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 120, 1)
        total = oc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 130.38, places=2)

    def test_calculate_total_full_discount(self):
        oc = OrderCalculator()
        oc.add_item('Pen', 1, 5)
        total = oc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 12.3)

    def test_calculate_total_discount_exactly_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Stuff', 125, 1)
        total = oc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 123.0)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_calculate_total_discount_negative(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 10, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-0.1)

    def test_calculate_total_discount_over_one(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 10, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=1.5)

    def test_calculate_total_discount_wrong_type(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 10, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount='0.1')

    def test_calculate_total_negative_subtotal_defensive(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 10, 1)
        with patch.object(oc, 'get_subtotal', return_value=-5):
            with self.assertRaises(ValueError):
                oc.calculate_total()

    def test_calculate_total_zero_subtotal_shipping_applied(self):
        oc = OrderCalculator()
        oc.add_item('Pen', 1, 5)
        total = oc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 12.3)

    def test_calculate_total_large_order(self):
        oc = OrderCalculator()
        for i in range(100):
            oc.add_item(f'Item{i}', 999.99, 1)
        total = oc.calculate_total(discount=0.05)
        self.assertTrue(total > 0)

    def test_total_items_empty_order(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        self.assertEqual(oc.total_items(), 1)

    def test_total_items_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Banana', 1, 5)
        self.assertEqual(oc.total_items(), 7)

    def test_total_items_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Rice', 1, 10000)
        self.assertEqual(oc.total_items(), 10000)

    def test_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 3)
        oc.add_item('Banana', 1, 2)
        oc.remove_item('Apple')
        self.assertEqual(oc.total_items(), 2)

    def test_clear_order_populated(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Banana', 1, 3)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.list_items(), [])
        self.assertEqual(oc.total_items(), 0)

    def test_clear_order_idempotent(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_list_items_empty_order(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_list_items_multiple_distinct(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Banana', 1, 3)
        items = oc.list_items()
        self.assertCountEqual(items, ['Apple', 'Banana'])

    def test_list_items_duplicate_names(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Apple', 1, 3)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_list_items_returned_is_copy(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        lst = oc.list_items()
        lst.append('X')
        self.assertNotIn('X', oc.list_items())

    def test_list_items_elements_are_strings(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        for name in oc.list_items():
            self.assertIsInstance(name, str)

    def test_list_items_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.clear_order()
        self.assertEqual(oc.list_items(), [])

    def test_is_empty_fresh_instance(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_adding_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_removing_only_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_clear_order(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_readding(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.clear_order()
        oc.add_item('Banana', 1, 1)
        self.assertFalse(oc.is_empty())

    def test_interaction_add_remove_add_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5)
        oc.remove_item('Apple')
        oc.add_item('Apple', 2.0)
        self.assertEqual(oc.total_items(), 1)

    def test_interaction_discount_free_shipping_edge(self):
        oc = OrderCalculator()
        oc.add_item('Stuff', 125, 1)
        total = oc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 123.0)

    def test_interaction_tax_rounding_consistency(self):
        oc = OrderCalculator()
        oc.add_item('Item', 33.33, 3)
        manual = oc.apply_discount(oc.get_subtotal(), 0) + oc.calculate_shipping(oc.get_subtotal())
        manual += oc.calculate_tax(manual)
        self.assertAlmostEqual(oc.calculate_total(), manual)

    def test_interaction_sequence_operations(self):
        oc = OrderCalculator()
        oc.add_item('A', 10, 2)
        oc.add_item('B', 5, 1)
        total1 = oc.calculate_total()
        oc.clear_order()
        oc.add_item('C', 20, 1)
        total2 = oc.calculate_total()
        self.assertNotEqual(total1, total2)

    def test_interaction_large_scale_stress(self):
        oc = OrderCalculator()
        for i in range(1000):
            oc.add_item(f'Item{i}', 1.23, 1)
        self.assertEqual(oc.total_items(), 1000)
        self.assertAlmostEqual(oc.get_subtotal(), 1230.0)
        self.assertTrue(oc.calculate_total() > 0)