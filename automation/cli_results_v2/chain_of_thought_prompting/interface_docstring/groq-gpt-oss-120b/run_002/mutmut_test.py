import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.default_calc = OrderCalculator()
        self.custom_calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.empty_calc = OrderCalculator()

    def test_C1_default_values(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_C2_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=200, shipping_cost=15)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 200)
        self.assertEqual(calc.shipping_cost, 15)

    def test_C3_tax_rate_below_zero(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_C4_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_C5_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_C6_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_C7_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='big')

    def test_C8_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_C9_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_A1_add_single_valid_item(self):
        self.empty_calc.add_item('Apple', 1.5, 2)
        self.assertEqual(self.empty_calc.total_items(), 2)

    def test_A2_add_same_name_and_price_aggregates(self):
        self.empty_calc.add_item('Apple', 1.5, 2)
        self.empty_calc.add_item('Apple', 1.5, 3)
        self.assertEqual(self.empty_calc.total_items(), 5)

    def test_A3_same_name_different_price_error(self):
        self.empty_calc.add_item('Apple', 1.5, 2)
        with self.assertRaises(ValueError):
            self.empty_calc.add_item('Apple', 2.0, 1)

    def test_A4_add_default_quantity(self):
        self.empty_calc.add_item('Banana', 0.8)
        self.assertEqual(self.empty_calc.total_items(), 1)

    def test_A5_empty_name_error(self):
        with self.assertRaises(ValueError):
            self.empty_calc.add_item('', 1.0, 1)

    def test_A6_name_wrong_type_error(self):
        with self.assertRaises(TypeError):
            self.empty_calc.add_item(123, 1.0, 1)

    def test_A7_price_non_positive_error(self):
        with self.assertRaises(ValueError):
            self.empty_calc.add_item('Pear', 0, 1)

    def test_A8_price_wrong_type_error(self):
        with self.assertRaises(TypeError):
            self.empty_calc.add_item('Pear', 'free', 1)

    def test_A9_quantity_less_than_one_error(self):
        with self.assertRaises(ValueError):
            self.empty_calc.add_item('Grape', 2.0, 0)

    def test_A10_quantity_wrong_type_error(self):
        with self.assertRaises(TypeError):
            self.empty_calc.add_item('Grape', 2.0, 1.5)

    def test_A11_add_many_distinct_items(self):
        self.empty_calc.add_item('Apple', 1.5, 2)
        self.empty_calc.add_item('Apple', 1.5, 3)
        self.empty_calc.add_item('Orange', 3.0, 4)
        self.assertEqual(self.empty_calc.total_items(), 9)
        items = self.empty_calc.list_items()
        self.assertIn('Apple', items)
        self.assertIn('Orange', items)

    def test_A12_large_quantity(self):
        self.empty_calc.add_item('Mega', 0.01, 1000000)
        self.assertEqual(self.empty_calc.total_items(), 1000000)

    def test_A13_price_many_decimals(self):
        self.empty_calc.add_item('Precise', 0.3333333, 3)
        subtotal = self.empty_calc.get_subtotal()
        self.assertAlmostEqual(subtotal, 0.9999999, places=7)

    def test_R1_remove_existing_item(self):
        self.empty_calc.add_item('Apple', 1.5, 2)
        self.empty_calc.remove_item('Apple')
        self.assertTrue(self.empty_calc.is_empty())

    def test_R2_remove_existing_item_among_others(self):
        self.empty_calc.add_item('Apple', 1.5, 2)
        self.empty_calc.add_item('Orange', 3.0, 4)
        self.empty_calc.remove_item('Apple')
        self.assertFalse(self.empty_calc.is_empty())
        self.assertEqual(self.empty_calc.total_items(), 4)

    def test_R3_remove_nonexistent_raises(self):
        with self.assertRaises(ValueError):
            self.empty_calc.remove_item('Nonexistent')

    def test_R4_remove_name_wrong_type(self):
        self.empty_calc.add_item('Apple', 1.5, 2)
        with self.assertRaises(TypeError):
            self.empty_calc.remove_item(123)

    def test_R5_case_sensitivity_removal(self):
        self.empty_calc.add_item('apple', 1.0, 1)
        with self.assertRaises(ValueError):
            self.empty_calc.remove_item('Apple')

    def test_S1_single_item_subtotal(self):
        self.empty_calc.add_item('Apple', 2.0, 3)
        self.assertEqual(self.empty_calc.get_subtotal(), 6.0)

    def test_S2_multiple_items_subtotal(self):
        self.empty_calc.add_item('Apple', 2.0, 3)
        self.empty_calc.add_item('Banana', 1.5, 2)
        self.assertEqual(self.empty_calc.get_subtotal(), 9.0)

    def test_S3_subtotal_empty_order_error(self):
        with self.assertRaises(ValueError):
            self.empty_calc.get_subtotal()

    def test_S4_subtotal_floating_point(self):
        self.empty_calc.add_item('Precise', 0.3333333, 3)
        self.assertAlmostEqual(self.empty_calc.get_subtotal(), 0.9999999, places=7)

    def test_D1_zero_percent_discount(self):
        self.assertEqual(self.empty_calc.apply_discount(100.0, 0.0), 100.0)

    def test_D2_full_discount(self):
        self.assertEqual(self.empty_calc.apply_discount(100.0, 1.0), 0.0)

    def test_D3_typical_discount(self):
        self.assertEqual(self.empty_calc.apply_discount(200.0, 0.2), 160.0)

    def test_D4_negative_subtotal_error(self):
        with self.assertRaises(ValueError):
            self.empty_calc.apply_discount(-10.0, 0.1)

    def test_D5_subtotal_wrong_type_error(self):
        with self.assertRaises(TypeError):
            self.empty_calc.apply_discount('big', 0.1)

    def test_D6_discount_below_zero_error(self):
        with self.assertRaises(ValueError):
            self.empty_calc.apply_discount(100.0, -0.01)

    def test_D7_discount_above_one_error(self):
        with self.assertRaises(ValueError):
            self.empty_calc.apply_discount(100.0, 1.5)

    def test_D8_discount_wrong_type_error(self):
        with self.assertRaises(TypeError):
            self.empty_calc.apply_discount(100.0, 'half')

    def test_SH1_above_threshold_free_shipping(self):
        self.assertEqual(self.empty_calc.calculate_shipping(150.0), 0.0)

    def test_SH2_at_threshold_free_shipping(self):
        self.assertEqual(self.empty_calc.calculate_shipping(100.0), 0.0)

    def test_SH3_below_threshold_standard_shipping(self):
        self.assertEqual(self.empty_calc.calculate_shipping(99.99), 10.0)

    def test_SH4_custom_config_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(calc.calculate_shipping(30), 5.0)

    def test_SH5_non_numeric_input_error(self):
        with self.assertRaises(TypeError):
            self.empty_calc.calculate_shipping('free')

    def test_SH6_integer_input(self):
        self.assertEqual(self.empty_calc.calculate_shipping(80), 10.0)

    def test_SH7_very_large_subtotal(self):
        self.assertEqual(self.empty_calc.calculate_shipping(1000000), 0.0)

    def test_SH8_just_below_threshold(self):
        self.assertEqual(self.empty_calc.calculate_shipping(99.999999), 10.0)

    def test_T1_default_tax(self):
        self.assertEqual(self.empty_calc.calculate_tax(100.0), 23.0)

    def test_T2_zero_amount_tax(self):
        self.assertEqual(self.empty_calc.calculate_tax(0.0), 0.0)

    def test_T3_custom_tax_rate(self):
        self.assertEqual(self.custom_calc.calculate_tax(200), 10.0)

    def test_T4_negative_amount_error(self):
        with self.assertRaises(ValueError):
            self.empty_calc.calculate_tax(-5.0)

    def test_T5_amount_wrong_type_error(self):
        with self.assertRaises(TypeError):
            self.empty_calc.calculate_tax('ten')

    def test_T6_very_small_amount(self):
        self.assertAlmostEqual(self.empty_calc.calculate_tax(0.0001), 2.3e-05, places=8)

    def test_T7_large_amount(self):
        self.assertEqual(self.empty_calc.calculate_tax(1000000), 230000)

    def test_CT1_no_discount_below_threshold(self):
        self.empty_calc.add_item('Apple', 30, 2)
        total = self.empty_calc.calculate_total()
        self.assertAlmostEqual(total, 86.1, places=2)

    def test_CT2_no_discount_above_threshold(self):
        self.empty_calc.add_item('Apple', 60, 2)
        total = self.empty_calc.calculate_total()
        self.assertAlmostEqual(total, 147.6, places=2)

    def test_CT3_discount_below_threshold(self):
        self.empty_calc.add_item('Apple', 30, 2)
        total = self.empty_calc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 71.34, places=2)

    def test_CT4_discount_above_threshold(self):
        self.empty_calc.add_item('Apple', 80, 2)
        total = self.empty_calc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 157.44, places=2)

    def test_CT5_full_discount(self):
        self.empty_calc.add_item('Apple', 50, 1)
        total = self.empty_calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 12.3, places=2)

    def test_CT6_empty_order_error(self):
        with self.assertRaises(ValueError):
            self.empty_calc.calculate_total()

    def test_CT7_invalid_discount_negative(self):
        self.empty_calc.add_item('Apple', 10, 1)
        with self.assertRaises(ValueError):
            self.empty_calc.calculate_total(discount=-0.1)

    def test_CT8_invalid_discount_above_one(self):
        self.empty_calc.add_item('Apple', 10, 1)
        with self.assertRaises(ValueError):
            self.empty_calc.calculate_total(discount=1.5)

    def test_CT9_discount_wrong_type_error(self):
        self.empty_calc.add_item('Apple', 10, 1)
        with self.assertRaises(TypeError):
            self.empty_calc.calculate_total(discount='half')

    def test_CT10_custom_tax_and_shipping(self):
        self.custom_calc.add_item('Item', 20, 3)
        total = self.custom_calc.calculate_total()
        self.assertAlmostEqual(total, 63.0, places=2)