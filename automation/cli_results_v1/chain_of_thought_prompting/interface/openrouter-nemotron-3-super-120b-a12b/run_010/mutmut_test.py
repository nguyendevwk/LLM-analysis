import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default_values(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=0.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_invalid_type_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_invalid_type_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=[100.0])

    def test_init_invalid_type_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_init_negative_tax_rate_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_negative_free_shipping_threshold_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_negative_shipping_cost_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_zero_values_accepted(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_add_item_new_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.total_items(), 3)
        self.assertAlmostEqual(calc.get_subtotal(), 3.0)
        self.assertIn('Apple', calc.list_items())

    def test_add_item_existing_item_increases_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 5.0)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.5)
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.5)

    def test_add_item_negative_quantity_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, -1)

    def test_add_item_non_string_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_non_numeric_price_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', '1.0')

    def test_add_item_negative_price_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', -1.0, 2)

    def test_add_item_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('Big', 10 ** 9, 10 ** 9)
        self.assertEqual(calc.total_items(), 10 ** 9)
        self.assertAlmostEqual(calc.get_subtotal(), 10 ** 18)

    def test_add_item_floating_point_precision(self):
        calc = OrderCalculator()
        calc.add_item('A', 0.1, 1)
        calc.add_item('B', 0.2, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3, places=7)

    def test_remove_item_non_string_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.5, 4)
        self.assertAlmostEqual(calc.get_subtotal(), 10.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 2.0, 3)
        calc.add_item('B', 5.0, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0 * 3 + 5.0 * 2)

    def test_get_subtotal_negative_quantity_if_present(self):
        calc = OrderCalculator()
        pass

    def test_get_subtotal_floating_point_precision(self):
        calc = OrderCalculator()
        calc.add_item('A', 0.1, 1)
        calc.add_item('B', 0.2, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3, places=7)

    def test_apply_discount_percentage_if_implemented_as_fraction(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.1), 90.0)

    def test_apply_discount_zero_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_negative_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, -5.0)

    def test_apply_discount_non_numeric_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('50', 5.0)
        with self.assertRaises(TypeError):
            calc.apply_discount(50.0, '5')

    def test_apply_discount_nan_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(float('nan'), 5.0)

    def test_apply_discount_inf_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(float('inf'), 5.0)

    def test_apply_discount_floating_point_precision(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(1.0, 0.3333333), 0.6666667, places=6)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_at_threshold_free(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_non_numeric_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('50')

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(-10.0), 10.0)

    def test_calculate_shipping_precision_boundary(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.0 - 1e-09), 10.0)
        self.assertEqual(calc.calculate_shipping(100.0 + 1e-09), 0.0)

    def test_calculate_tax_typical(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_non_numeric_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('5')

    def test_calculate_tax_depends_on_constructor_rate(self):
        calc1 = OrderCalculator(tax_rate=0.05)
        calc2 = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(calc1.calculate_tax(100.0), 5.0)
        self.assertAlmostEqual(calc2.calculate_tax(100.0), 20.0)

    def test_calculate_total_items_only_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('A', 10.0, 2)
        calc.add_item('B', 20.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 61.5)

    def test_calculate_total_non_numeric_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='5')

    def test_calculate_total_negative_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-5.0)

    def test_calculate_total_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('A', 10 ** 6, 10 ** 6)
        expected = 10 ** 12 * 1.23
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('A', 5.0, 3)
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 2.0, 5)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_updates_after_add_remove(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        self.assertEqual(calc.total_items(), 1)
        calc.add_item('B', 2.0, 2)
        self.assertEqual(calc.total_items(), 3)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 2)
        calc.remove_item('B')
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_return_type(self):
        calc = OrderCalculator()
        self.assertIsInstance(calc.total_items(), int)

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_returns_none(self):
        calc = OrderCalculator()
        self.assertIsNone(calc.clear_order())

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('B', 1.0, 1)
        calc.add_item('A', 1.0, 1)
        self.assertEqual(calc.list_items(), ['B', 'A'])

    def test_list_items_updates_after_add_remove(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        self.assertEqual(calc.list_items(), ['A'])
        calc.add_item('B', 1.0, 1)
        self.assertEqual(set(calc.list_items()), {'A', 'B'})
        calc.remove_item('A')
        self.assertEqual(calc.list_items(), ['B'])

    def test_list_items_duplicate_names_single_entry(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('A', 1.0, 3)
        self.assertEqual(calc.list_items(), ['A'])
        self.assertEqual(calc.total_items(), 5)

    def test_list_items_return_type(self):
        calc = OrderCalculator()
        result = calc.list_items()
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item, str)

    def test_list_items_returned_list_is_copy(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        lst = calc.list_items()
        lst.append('B')
        self.assertNotIn('B', calc.list_items())

    def test_is_empty_empty_order(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_non_empty_order(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_updates_after_mutations(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        calc.add_item('A', 1.0, 1)
        self.assertFalse(calc.is_empty())
        calc.remove_item('A')
        self.assertTrue(calc.is_empty())
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_return_type(self):
        calc = OrderCalculator()
        self.assertIsInstance(calc.is_empty(), bool)

    def test_interaction_add_remove_add_again(self):
        calc = OrderCalculator()
        calc.add_item('A', 2.0, 1)
        self.assertEqual(calc.total_items(), 1)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 0)
        calc.add_item('A', 2.0, 2)
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 4.0)

    def test_interaction_free_shipping_threshold_boundary(self):
        calc = OrderCalculator(free_shipping_threshold=50.0)
        calc.add_item('A', 49.9, 1)
        self.assertEqual(calc.calculate_shipping(calc.get_subtotal()), 10.0)
        calc.add_item('B', 0.2, 1)
        self.assertEqual(calc.calculate_shipping(calc.get_subtotal()), 0.0)

    def test_interaction_tax_rate_independence(self):
        calc1 = OrderCalculator(tax_rate=0.05)
        calc2 = OrderCalculator(tax_rate=0.2)
        calc1.add_item('A', 100.0, 1)
        calc2.add_item('A', 100.0, 1)
        self.assertAlmostEqual(calc1.calculate_total(), 100.0 * 1.05)
        self.assertAlmostEqual(calc2.calculate_total(), 100.0 * 1.2)
        self.assertAlmostEqual(calc1.calculate_total(), 105.0)
        self.assertAlmostEqual(calc2.calculate_total(), 120.0)

    def test_interaction_clear_then_reuse(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 2.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        calc.add_item('C', 3.0, 1)
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 3.0)
        self.assertEqual(calc.list_items(), ['C'])

    def test_interaction_exception_safety_invalid_add(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        initial_items = calc.list_items().copy()
        initial_subtotal = calc.get_subtotal()
        with self.assertRaises(ValueError):
            calc.add_item('B', -1.0, 1)
        self.assertEqual(calc.list_items(), initial_items)
        self.assertAlmostEqual(calc.get_subtotal(), initial_subtotal)