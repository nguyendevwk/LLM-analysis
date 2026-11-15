import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_01_default_constructor(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_02_custom_valid_parameters(self):
        c = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(c.tax_rate, 0.0)
        self.assertEqual(c.free_shipping_threshold, 0.0)
        self.assertEqual(c.shipping_cost, 0.0)

    def test_03_invalid_tax_rate_out_of_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_04_invalid_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate=None)

    def test_05_invalid_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_06_invalid_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_07_invalid_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_08_invalid_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_09_add_single_valid_item(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 2)

    def test_10_add_default_quantity(self):
        self.calc.add_item('Banana', 0.8)
        self.assertIn('Banana', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 1)

    def test_11_merge_same_name_and_price(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Apple', 1.5, 3)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 5)

    def test_12_add_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_13_add_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_14_add_price_not_positive(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Milk', 0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Milk', -5, 1)

    def test_15_add_price_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Milk', '9.99', 1)

    def test_16_add_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Egg', 0.5, 0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Egg', 0.5, -2)

    def test_17_add_quantity_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Egg', 0.5, 2.5)
        with self.assertRaises(TypeError):
            self.calc.add_item('Egg', 0.5, '3')

    def test_18_add_same_name_different_price(self):
        self.calc.add_item('Milk', 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Milk', 1.2, 1)

    def test_19_remove_existing_item(self):
        self.calc.add_item('Bread', 2.0, 1)
        self.calc.remove_item('Bread')
        self.assertNotIn('Bread', self.calc.list_items())
        self.assertTrue(self.calc.is_empty())

    def test_20_remove_nonexistent_item(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_21_remove_name_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(None)
        with self.assertRaises(TypeError):
            self.calc.remove_item(5)

    def test_22_get_subtotal_non_empty(self):
        self.calc.add_item('A', 10.0, 2)
        self.calc.add_item('B', 5.5, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 25.5, places=2)

    def test_23_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_24_apply_discount_typical(self):
        result = self.calc.apply_discount(200, 0.2)
        self.assertAlmostEqual(result, 160.0, places=2)

    def test_25_apply_discount_zero(self):
        result = self.calc.apply_discount(100, 0.0)
        self.assertAlmostEqual(result, 100.0, places=2)

    def test_26_apply_discount_full(self):
        result = self.calc.apply_discount(100, 1.0)
        self.assertAlmostEqual(result, 0.0, places=2)

    def test_27_apply_discount_subtotal_zero(self):
        result = self.calc.apply_discount(0.0, 0.5)
        self.assertAlmostEqual(result, 0.0, places=2)

    def test_28_apply_discount_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, -0.1)

    def test_29_apply_discount_discount_over_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, 1.5)

    def test_30_apply_discount_discount_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, '0.2')
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, None)

    def test_31_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10, 0.1)

    def test_32_apply_discount_subtotal_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)

    def test_33_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(80.0), 10.0)

    def test_34_calculate_shipping_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_35_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_36_calculate_shipping_zero_threshold(self):
        c = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(c.calculate_shipping(5.0), 0.0)

    def test_37_calculate_shipping_zero_cost(self):
        c = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(c.calculate_shipping(50.0), 0.0)

    def test_38_calculate_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50')

    def test_39_calculate_shipping_negative_subtotal(self):
        self.assertEqual(self.calc.calculate_shipping(-5.0), 10.0)

    def test_40_calculate_tax_default_rate(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100), 23.0, places=2)

    def test_41_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0), 0.0, places=2)

    def test_42_calculate_tax_custom_rate_zero(self):
        c = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(c.calculate_tax(100), 0.0, places=2)

    def test_43_calculate_tax_custom_rate_one(self):
        c = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(c.calculate_tax(50), 50.0, places=2)

    def test_44_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10)

    def test_45_calculate_tax_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_46_calculate_total_typical(self):
        self.calc.add_item('A', 30.0, 2)
        self.calc.add_item('B', 20.0, 1)
        total = self.calc.calculate_total(0.1)
        self.assertAlmostEqual(total, 100.86, places=2)

    def test_47_calculate_total_free_shipping(self):
        c = OrderCalculator(free_shipping_threshold=20.0)
        c.add_item('A', 15.0, 2)
        total = c.calculate_total(0.0)
        self.assertAlmostEqual(total, 36.9, places=2)

    def test_49_calculate_total_zero_discount(self):
        self.calc.add_item('A', 40.0, 1)
        subtotal = self.calc.get_subtotal()
        shipping = self.calc.calculate_shipping(subtotal)
        tax = self.calc.calculate_tax(subtotal + shipping)
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.0), expected, places=2)

    def test_50_calculate_total_discount_negative(self):
        self.calc.add_item('A', 10, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-0.1)

    def test_51_calculate_total_discount_over_one(self):
        self.calc.add_item('A', 10, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.5)

    def test_52_calculate_total_discount_wrong_type(self):
        self.calc.add_item('A', 10, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.1')

    def test_53_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_54_calculate_total_custom_tax_zero(self):
        c = OrderCalculator(tax_rate=0.0)
        c.add_item('A', 20, 1)
        total = c.calculate_total(0.0)
        self.assertAlmostEqual(total, 30.0, places=2)

    def test_55_calculate_total_custom_shipping_zero(self):
        c = OrderCalculator(shipping_cost=0.0)
        c.add_item('A', 20, 1)
        total = c.calculate_total(0.0)
        self.assertAlmostEqual(total, 24.6, places=2)

    def test_57_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_58_total_items_after_adding(self):
        self.calc.add_item('A', 1, 3)
        self.calc.add_item('B', 2, 4)
        self.assertEqual(self.calc.total_items(), 7)

    def test_59_total_items_after_removal(self):
        self.calc.add_item('A', 1, 3)
        self.calc.add_item('B', 2, 4)
        self.calc.remove_item('A')
        self.assertEqual(self.calc.total_items(), 4)

    def test_60_total_items_after_clear(self):
        self.calc.add_item('A', 1, 3)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_61_clear_order_non_empty(self):
        self.calc.add_item('A', 1, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])
        self.assertEqual(self.calc.total_items(), 0)

    def test_62_clear_order_already_empty(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_63_list_items_distinct_names(self):
        self.calc.add_item('A', 1, 1)
        self.calc.add_item('B', 2, 1)
        self.calc.add_item('C', 3, 1)
        self.assertEqual(set(self.calc.list_items()), {'A', 'B', 'C'})

    def test_64_list_items_duplicate_name_same_price(self):
        self.calc.add_item('A', 1, 1)
        self.calc.add_item('A', 1, 2)
        self.assertEqual(self.calc.list_items(), ['A'])

    def test_65_list_items_after_removal(self):
        self.calc.add_item('A', 1, 1)
        self.calc.add_item('B', 2, 1)
        self.calc.remove_item('A')
        self.assertEqual(self.calc.list_items(), ['B'])

    def test_66_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_67_is_empty_fresh(self):
        self.assertTrue(self.calc.is_empty())

    def test_68_is_empty_after_adding(self):
        self.calc.add_item('A', 1, 1)
        self.assertFalse(self.calc.is_empty())

    def test_69_is_empty_after_removing_last(self):
        self.calc.add_item('A', 1, 1)
        self.calc.remove_item('A')
        self.assertTrue(self.calc.is_empty())

    def test_70_is_empty_after_clear(self):
        self.calc.add_item('A', 1, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_71_interaction_add_remove_add_again(self):
        self.calc.add_item('X', 5, 2)
        self.calc.remove_item('X')
        self.calc.add_item('X', 5, 4)
        self.assertIn('X', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 4)

    def test_72_interaction_multiple_calculate_total_calls(self):
        self.calc.add_item('A', 10, 2)
        total1 = self.calc.calculate_total(0.1)
        total2 = self.calc.calculate_total(0.2)
        self.assertAlmostEqual(total1, 34.44, places=2)
        self.assertAlmostEqual(total2, 31.98, places=2)

    def test_73_interaction_exception_does_not_corrupt_state(self):
        self.calc.add_item('A', 10, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('A', 12, 1)
        self.assertIn('A', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 1)

    def test_74_interaction_price_as_int(self):
        self.calc.add_item('IntPrice', 5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10.0, places=2)

    def test_75_interaction_full_discount_shipping_rule(self):
        c = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=5.0)
        c.add_item('A', 20, 1)
        total = c.calculate_total(1.0)
        self.assertAlmostEqual(total, 0.0, places=2)

    def test_76_interaction_negative_discounted_subtotal_shipping(self):
        self.assertEqual(self.calc.calculate_shipping(-1.0), 10.0)

    def test_77_interaction_floating_point_rounding(self):
        self.calc.add_item('A', 0.1, 3)
        self.calc.add_item('B', 0.2, 2)
        total = self.calc.calculate_total(0.0)
        expected_subtotal = 0.7
        expected_shipping = 10.0
        expected_tax = 0.23 * (expected_subtotal + expected_shipping)
        expected_total = expected_subtotal + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total, places=2)

    def test_78_interaction_large_quantity(self):
        self.calc.add_item('Bulk', 0.5, 1000000)
        self.assertEqual(self.calc.total_items(), 1000000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 500000.0, places=2)