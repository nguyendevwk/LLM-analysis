import unittest
import math
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_01_default_constructor(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.tax_rate, 0.23)
        self.assertAlmostEqual(calc.free_shipping_threshold, 100.0)
        self.assertAlmostEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    def test_02_custom_constructor(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.tax_rate, 0.05)
        self.assertAlmostEqual(calc.free_shipping_threshold, 50.0)
        self.assertAlmostEqual(calc.shipping_cost, 5.0)

    def test_03_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_04_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_05_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_06_add_single_item_default_qty(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5)
        self.assertEqual(calc.total_items(), 1)
        self.assertIn('Apple', calc.list_items())
        self.assertAlmostEqual(calc.get_subtotal(), 0.5)

    def test_07_add_multiple_items_explicit_qty(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.2, 3)
        calc.add_item('Orange', 0.8, 2)
        self.assertEqual(calc.total_items(), 5)
        self.assertCountEqual(calc.list_items(), ['Banana', 'Orange'])
        self.assertAlmostEqual(calc.get_subtotal(), 0.2 * 3 + 0.8 * 2)

    def test_08_add_same_name_increment(self):
        calc = OrderCalculator()
        calc.add_item('Milk', 1.0, 1)
        calc.add_item('Milk', 1.0, 2)
        self.assertEqual(calc.total_items(), 3)
        self.assertAlmostEqual(calc.get_subtotal(), 3.0)

    def test_09_add_same_name_different_price(self):
        calc = OrderCalculator()
        calc.add_item('Bread', 2.0, 1)
        calc.add_item('Bread', 1.5, 1)
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 1.5 * 2)

    def test_10_add_item_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    def test_11_add_item_whitespace_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('   ', 1.0)

    def test_12_add_item_negative_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Soda', -0.99)

    def test_13_add_item_nan_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Soda', float('nan'))

    def test_14_add_item_zero_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Cookie', 0.5, 0)

    def test_15_add_item_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Cookie', 0.5, -2)

    def test_16_add_item_nonint_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Cookie', 0.5, 2.5)

    def test_17_add_item_nonnumeric_price(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Candy', '1.00')

    def test_18_remove_existing_item(self):
        calc = OrderCalculator()
        calc.add_item('Eggs', 2.0)
        calc.remove_item('Eggs')
        self.assertTrue(calc.is_empty())
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)
        self.assertEqual(calc.list_items(), [])

    def test_19_remove_one_of_several_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Banana', 2.0)
        calc.remove_item('Apple')
        self.assertFalse(calc.is_empty())
        self.assertEqual(calc.list_items(), ['Banana'])
        self.assertAlmostEqual(calc.get_subtotal(), 2.0)

    def test_20_remove_nonexistent_name(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        with self.assertRaises(KeyError):
            calc.remove_item('Nonexistent')

    def test_21_remove_from_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(KeyError):
            calc.remove_item('Anything')

    def test_22_get_subtotal_after_adds(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 3.0, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 1.0 * 2 + 3.0 * 1)

    def test_23_get_subtotal_empty(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)

    def test_24_get_subtotal_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('A', 2.0, 3)
        calc.add_item('B', 5.0, 1)
        calc.remove_item('A')
        self.assertAlmostEqual(calc.get_subtotal(), 5.0)

    def test_25_apply_discount_zero(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100.0, 0.0)
        self.assertAlmostEqual(result, 100.0)

    def test_26_apply_discount_less_than_subtotal(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100.0, 15.0)
        self.assertAlmostEqual(result, 85.0)

    def test_27_apply_discount_equal_subtotal(self):
        calc = OrderCalculator()
        result = calc.apply_discount(20.0, 20.0)
        self.assertAlmostEqual(result, 0.0)

    def test_28_apply_discount_greater_than_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(30.0, 40.0)

    def test_29_apply_discount_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(30.0, -5.0)

    def test_30_apply_discount_nonnumeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(30.0, '10')

    def test_31_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        cost = calc.calculate_shipping(99.99)
        self.assertAlmostEqual(cost, 10.0)

    def test_32_calculate_shipping_at_threshold(self):
        calc = OrderCalculator()
        cost = calc.calculate_shipping(100.0)
        self.assertAlmostEqual(cost, 0.0)

    def test_33_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        cost = calc.calculate_shipping(150.0)
        self.assertAlmostEqual(cost, 0.0)

    def test_34_calculate_shipping_zero_subtotal(self):
        calc = OrderCalculator()
        cost = calc.calculate_shipping(0.0)
        self.assertAlmostEqual(cost, 10.0)

    def test_35_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_shipping(-5.0)

    def test_36_calculate_tax_typical(self):
        calc = OrderCalculator()
        tax = calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_37_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        tax = calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_38_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        tax = calc.calculate_tax(50.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_39_calculate_tax_full_rate(self):
        calc = OrderCalculator(tax_rate=1.0)
        tax = calc.calculate_tax(50.0)
        self.assertAlmostEqual(tax, 50.0)

    def test_40_calculate_tax_negative_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-10.0)

    def test_41_calculate_tax_nonnumeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('20')

    def test_42_calculate_total_empty_order(self):
        calc = OrderCalculator()
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 0.0)

    def test_43_calculate_total_single_item_below_threshold(self):
        calc = OrderCalculator()
        calc.add_item('Item', 50.0)
        subtotal = 50.0
        expected = subtotal + calc.calculate_tax(subtotal) + calc.shipping_cost
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_44_calculate_total_multiple_items_above_threshold(self):
        calc = OrderCalculator()
        calc.add_item('A', 60.0)
        calc.add_item('B', 50.0)
        subtotal = 110.0
        expected = subtotal + calc.calculate_tax(subtotal)
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_45_calculate_total_discount_below_threshold(self):
        calc = OrderCalculator()
        calc.add_item('A', 120.0)
        total = calc.calculate_total(discount=30.0)
        discounted = 90.0
        expected = discounted + calc.calculate_tax(discounted) + calc.shipping_cost
        self.assertAlmostEqual(total, expected)

    def test_46_calculate_total_discount_not_crossing_threshold(self):
        calc = OrderCalculator()
        calc.add_item('A', 120.0)
        total = calc.calculate_total(discount=10.0)
        discounted = 110.0
        expected = discounted + calc.calculate_tax(discounted)
        self.assertAlmostEqual(total, expected)

    def test_47_calculate_total_discount_to_exact_threshold(self):
        calc = OrderCalculator()
        calc.add_item('A', 110.0)
        total = calc.calculate_total(discount=10.0)
        discounted = 100.0
        expected = discounted + calc.calculate_tax(discounted)
        self.assertAlmostEqual(total, expected)

    def test_48_calculate_total_discount_exceeds_subtotal(self):
        calc = OrderCalculator()
        calc.add_item('A', 20.0)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=30.0)

    def test_49_calculate_total_negative_discount(self):
        calc = OrderCalculator()
        calc.add_item('A', 20.0)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-5.0)

    def test_50_calculate_total_custom_params(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=7.5)
        calc.add_item('A', 45.0)
        subtotal = 45.0
        expected = subtotal + calc.calculate_tax(subtotal) + 7.5
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_51_total_items_after_adds(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_52_total_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 1.0, 3)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 3)

    def test_53_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_54_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_55_clear_order_clears_populated(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 2.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.list_items(), [])
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)

    def test_56_clear_order_idempotent(self):
        calc = OrderCalculator()
        calc.clear_order()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_57_list_items_after_adds(self):
        calc = OrderCalculator()
        calc.add_item('X', 1.0)
        calc.add_item('Y', 1.0)
        calc.add_item('Z', 1.0)
        self.assertCountEqual(calc.list_items(), ['X', 'Y', 'Z'])

    def test_58_list_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('X', 1.0)
        calc.add_item('Y', 1.0)
        calc.add_item('Z', 1.0)
        calc.remove_item('Y')
        self.assertCountEqual(calc.list_items(), ['X', 'Z'])

    def test_59_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_60_is_empty_fresh(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_61_is_empty_after_add(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0)
        self.assertFalse(calc.is_empty())

    def test_62_is_empty_after_removing_last(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0)
        calc.remove_item('A')
        self.assertTrue(calc.is_empty())

    def test_63_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_64_sequence_add_remove_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0)
        calc.add_item('B', 2.0)
        calc.remove_item('A')
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.list_items(), [])
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)

    def test_65_total_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 10.0)
        calc.clear_order()
        self.assertAlmostEqual(calc.calculate_total(), 0.0)

    def test_66_apply_discount_floating_precision(self):
        calc = OrderCalculator()
        result = calc.apply_discount(0.1, 0.03)
        self.assertTrue(math.isclose(result, 0.07, rel_tol=1e-09))

    def test_67_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('Expensive', 1000000.0, 10)
        subtotal = 10000000.0
        tax = calc.calculate_tax(subtotal)
        total = calc.calculate_total()
        expected = subtotal + tax
        self.assertTrue(math.isclose(total, expected, rel_tol=1e-09))

    def test_68_zero_price_items(self):
        calc = OrderCalculator()
        calc.add_item('Gift', 0.0, 5)
        self.assertEqual(calc.total_items(), 5)
        self.assertIn('Gift', calc.list_items())
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)

    def test_69_invalid_add_does_not_corrupt_state(self):
        calc = OrderCalculator()
        calc.add_item('Valid', 1.0)
        with self.assertRaises(ValueError):
            calc.add_item('Invalid', -2.0)
        self.assertIn('Valid', calc.list_items())
        self.assertEqual(calc.total_items(), 1)

    def test_70_remove_after_increment(self):
        calc = OrderCalculator()
        calc.add_item('Milk', 1.0, 1)
        calc.add_item('Milk', 1.0, 2)
        calc.remove_item('Milk')
        self.assertTrue(calc.is_empty())

    def test_71_total_with_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('A', 80.0)
        total = calc.calculate_total()
        expected = 80.0 + calc.calculate_tax(80.0)
        self.assertAlmostEqual(total, expected)

    def test_72_total_with_zero_free_shipping_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item('A', 10.0)
        total = calc.calculate_total()
        expected = 10.0 + calc.calculate_tax(10.0)
        self.assertAlmostEqual(total, expected)

    def test_73_total_with_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('A', 50.0)
        total = calc.calculate_total()
        expected = 50.0 + calc.shipping_cost
        self.assertAlmostEqual(total, expected)

    def test_74_total_with_zero_tax_and_shipping(self):
        calc = OrderCalculator(tax_rate=0.0, shipping_cost=0.0)
        calc.add_item('A', 30.0)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 30.0)

    def test_75_list_items_order_stability(self):
        calc = OrderCalculator()
        calc.add_item('First', 1.0)
        calc.add_item('Second', 1.0)
        calc.add_item('Third', 1.0)
        self.assertEqual(calc.list_items(), ['First', 'Second', 'Third'])

    def test_76_add_unicode_names(self):
        calc = OrderCalculator()
        calc.add_item('Café', 2.0)
        calc.add_item('寿司', 3.0)
        self.assertCountEqual(calc.list_items(), ['Café', '寿司'])

    def test_77_add_extremely_long_name(self):
        long_name = 'X' * 2000
        calc = OrderCalculator()
        calc.add_item(long_name, 1.0)
        self.assertIn(long_name, calc.list_items())

    def test_78_remove_case_sensitive(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        with self.assertRaises(KeyError):
            calc.remove_item('apple')

    def test_79_apply_discount_floating_rounding(self):
        calc = OrderCalculator()
        result = calc.apply_discount(0.3, 0.1)
        self.assertTrue(math.isclose(result, 0.2, rel_tol=1e-09))

    def test_80_shipping_always_charged_infinite_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=float('inf'))
        cost = calc.calculate_shipping(500.0)
        self.assertAlmostEqual(cost, calc.shipping_cost)

    def test_81_shipping_always_free_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        cost = calc.calculate_shipping(0.0)
        self.assertAlmostEqual(cost, 0.0)
        cost = calc.calculate_shipping(10.0)
        self.assertAlmostEqual(cost, 0.0)

    def test_82_zero_price_items_with_discount(self):
        calc = OrderCalculator()
        calc.add_item('Free', 0.0, 2)
        calc.add_item('Paid', 20.0, 1)
        total = calc.calculate_total(discount=20.0)
        expected = calc.calculate_tax(0.0) + calc.shipping_cost
        self.assertAlmostEqual(total, expected)

    def test_83_clear_after_failed_add(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Bad', -1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_84_remove_after_clear(self):
        calc = OrderCalculator()
        calc.clear_order()
        with self.assertRaises(KeyError):
            calc.remove_item('Anything')

    def test_85_total_with_tiny_discount(self):
        calc = OrderCalculator()
        calc.add_item('A', 100.0)
        total = calc.calculate_total(discount=1e-12)
        discounted = 100.0 - 1e-12
        expected = discounted + calc.calculate_tax(discounted) + calc.shipping_cost
        self.assertTrue(math.isclose(total, expected, rel_tol=1e-12))

    def test_86_total_just_below_threshold(self):
        calc = OrderCalculator()
        calc.add_item('A', 99.9999999)
        total = calc.calculate_total()
        expected = 99.9999999 + calc.calculate_tax(99.9999999) + calc.shipping_cost
        self.assertTrue(math.isclose(total, expected, rel_tol=1e-09))

    def test_87_total_just_above_threshold(self):
        calc = OrderCalculator()
        calc.add_item('A', 100.0000001)
        total = calc.calculate_total()
        expected = 100.0000001 + calc.calculate_tax(100.0000001)
        self.assertTrue(math.isclose(total, expected, rel_tol=1e-09))

    def test_88_increment_quantity_by_repeated_adds(self):
        calc = OrderCalculator()
        for _ in range(100):
            calc.add_item('Item', 1.0, 1)
        self.assertEqual(calc.total_items(), 100)
        self.assertAlmostEqual(calc.get_subtotal(), 100.0)

    def test_89_many_distinct_items(self):
        calc = OrderCalculator()
        names = [f'Item{i}' for i in range(50)]
        for i, name in enumerate(names):
            calc.add_item(name, i + 1.0, 1)
        self.assertCountEqual(calc.list_items(), names)
        self.assertEqual(calc.total_items(), 50)

    def test_90_total_with_discount_equal_subtotal(self):
        calc = OrderCalculator()
        calc.add_item('A', 200.0)
        total = calc.calculate_total(discount=200.0)
        expected = calc.calculate_tax(0.0) + calc.shipping_cost
        self.assertAlmostEqual(total, expected)