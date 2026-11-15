import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_C_01_default_initialisation(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_C_02_custom_valid_zero_values(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0.0)
        self.assertEqual(oc.shipping_cost, 0.0)

    def test_C_03_custom_non_default_values(self):
        oc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=250.5, shipping_cost=12.75)
        self.assertEqual(oc.tax_rate, 0.15)
        self.assertEqual(oc.free_shipping_threshold, 250.5)
        self.assertEqual(oc.shipping_cost, 12.75)

    def test_C_04_invalid_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_C_05_invalid_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_C_06_invalid_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_C_07_invalid_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_C_08_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_C_09_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=[100])

    def test_C_10_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_A_01_add_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.total_items(), 3)
        self.assertIn('Apple', oc.list_items())

    def test_A_02_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 2.0)
        self.assertEqual(oc.total_items(), 1)
        self.assertIn('Banana', oc.list_items())

    def test_A_03_merge_quantity_same_name_and_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 4)
        self.assertEqual(oc.total_items(), 6)

    def test_A_04_multiple_distinct_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.add_item('Orange', 2.0)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Orange'])

    def test_A_05_price_minimum_positive(self):
        oc = OrderCalculator()
        oc.add_item('Gum', 0.01, 5)
        self.assertEqual(oc.total_items(), 5)

    def test_A_06_quantity_minimum_one(self):
        oc = OrderCalculator()
        oc.add_item('Pen', 1.0, 1)
        self.assertEqual(oc.total_items(), 1)

    def test_A_07_error_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_A_08_error_name_not_string(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_A_09_error_price_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Item', 0.0, 1)

    def test_A_10_error_price_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Item', -5.0, 1)

    def test_A_11_error_price_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Item', '5', 1)

    def test_A_12_error_quantity_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Item', 1.0, 0)

    def test_A_13_error_quantity_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Item', 1.0, -2)

    def test_A_14_error_quantity_not_int(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Item', 1.0, 2.5)

    def test_A_15_error_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0, 1)

    def test_A_16_error_name_none(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(None, 1.0, 1)

    def test_A_17_edge_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Bulk', 1.0, 10000)
        self.assertEqual(oc.total_items(), 10000)

    def test_A_18_edge_large_price(self):
        oc = OrderCalculator()
        oc.add_item('Expensive', 1000000.0, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 2000000.0)

    def test_R_01_remove_existing_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_R_02_remove_one_of_several_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.add_item('Banana', 2.0)
        oc.remove_item('Apple')
        self.assertFalse(oc.is_empty())
        self.assertNotIn('Apple', oc.list_items())
        self.assertIn('Banana', oc.list_items())

    def test_R_03_remove_last_item_makes_order_empty(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_R_04_error_remove_nonexistent_item(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Nonexistent')

    def test_R_05_error_remove_invalid_name_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_R_06_error_remove_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('')

    def test_E_01_is_empty_initially(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_E_02_is_empty_after_adding(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        self.assertFalse(oc.is_empty())

    def test_E_03_is_empty_after_removing_last(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_E_04_is_empty_after_clearing(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_L_01_list_items_empty_order(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_L_02_list_items_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        self.assertEqual(oc.list_items(), ['Apple'])

    def test_L_03_list_items_multiple_distinct(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.add_item('Orange', 2.0)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Orange'])

    def test_L_04_list_items_no_duplicates_on_merge(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Apple', 1.0, 3)
        self.assertEqual(oc.list_items(), ['Apple'])

    def test_L_05_list_items_large_number(self):
        oc = OrderCalculator()
        names = [f'Item{i}' for i in range(100)]
        for n in names:
            oc.add_item(n, 1.0)
        self.assertCountEqual(oc.list_items(), names)

    def test_TI_01_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_TI_02_total_items_single_quantity_one(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        self.assertEqual(oc.total_items(), 1)

    def test_TI_03_total_items_multiple_quantities(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Orange', 2.0, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_TI_04_total_items_after_merge(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Apple', 1.0, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_TI_05_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 1.0, 3)
        oc.remove_item('Apple')
        self.assertEqual(oc.total_items(), 3)

    def test_TI_06_total_items_very_large(self):
        oc = OrderCalculator()
        oc.add_item('Bulk', 1.0, 1000000)
        self.assertEqual(oc.total_items(), 1000000)

    def test_CL_01_clear_non_empty_order(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.add_item('Banana', 2.0)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.list_items(), [])
        self.assertEqual(oc.total_items(), 0)

    def test_CL_02_clear_already_empty(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_S_01_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.5, 4)
        self.assertAlmostEqual(oc.get_subtotal(), 10.0)

    def test_S_02_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 2.5, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 4.5)

    def test_S_03_subtotal_large_numbers(self):
        oc = OrderCalculator()
        oc.add_item('GoldBar', 1000000.0, 1000)
        self.assertAlmostEqual(oc.get_subtotal(), 1000000000.0)

    def test_S_04_subtotal_raises_when_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_D_01_apply_discount_normal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(200, 0.15), 170.0)

    def test_D_02_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(123.45, 0.0), 123.45)

    def test_D_03_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(99.99, 1.0), 0.0)

    def test_D_04_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10, 0.1)

    def test_D_05_apply_discount_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, -0.1)

    def test_D_06_apply_discount_discount_above_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, 1.5)

    def test_D_07_apply_discount_subtotal_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)

    def test_D_08_apply_discount_discount_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100, [0.1])

    def test_D_09_apply_discount_subtotal_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(0, 0.5), 0.0)

    def test_D_10_apply_discount_rounding(self):
        oc = OrderCalculator()
        result = oc.apply_discount(0.1, 0.33)
        self.assertAlmostEqual(result, 0.1 * (1 - 0.33), places=7)

    def test_SH_01_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(150), 0.0)

    def test_SH_02_shipping_exact_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(100), 0.0)

    def test_SH_03_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(75), 10.0)

    def test_SH_04_shipping_custom_parameters(self):
        oc = OrderCalculator(free_shipping_threshold=200, shipping_cost=25)
        self.assertAlmostEqual(oc.calculate_shipping(199), 25.0)
        self.assertAlmostEqual(oc.calculate_shipping(200), 0.0)

    def test_SH_05_shipping_negative_subtotal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(-5), 10.0)

    def test_SH_06_shipping_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping({'value': 10})

    def test_SH_07_shipping_float_just_below_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(99.999), 10.0)

    def test_T_01_tax_normal_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(100), 23.0)

    def test_T_02_tax_zero_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0), 0.0)

    def test_T_03_tax_large_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(10000000), 2300000.0)

    def test_T_04_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-1)

    def test_T_05_tax_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax('100')

    def test_T_06_tax_amount_many_decimals(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(123.456), 28.395, places=3)

    def test_CT_01_total_no_discount_shipping_applied(self):
        oc = OrderCalculator()
        oc.add_item('A', 10.0, 2)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 36.9, places=2)

    def test_CT_02_total_discount_triggers_free_shipping(self):
        oc = OrderCalculator()
        oc.add_item('Item', 200.0, 1)
        total = oc.calculate_total(discount=0.5)
        self.assertAlmostEqual(total, 123.0, places=2)

    def test_CT_03_total_discount_above_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 150.0, 2)
        total = oc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 240 + 0 + 240 * 0.23, places=2)

    def test_CT_04_total_full_discount(self):
        oc = OrderCalculator()
        oc.add_item('Item', 50.0, 1)
        total = oc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 10.0, places=2)

    def test_CT_05_total_empty_order_raises(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_CT_06_total_invalid_discount_negative(self):
        oc = OrderCalculator()
        oc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-0.1)

    def test_CT_07_total_invalid_discount_above_one(self):
        oc = OrderCalculator()
        oc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=1.5)

    def test_CT_08_total_invalid_discount_type(self):
        oc = OrderCalculator()
        oc.add_item('Item', 10.0, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount='0.1')

    def test_CT_09_total_explicit_zero_discount(self):
        oc = OrderCalculator()
        oc.add_item('A', 10.0, 2)
        total = oc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 36.9, places=2)

    def test_CT_10_total_custom_parameters(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=5)
        oc.add_item('Item', 30.0, 2)
        total = oc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 66.0, places=2)

    def test_CT_11_total_large_order(self):
        oc = OrderCalculator()
        oc.add_item('GoldBar', 1000000.0, 1000)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 1230000000.0, delta=0.01)

    def test_CT_12_total_reflects_item_removal(self):
        oc = OrderCalculator()
        oc.add_item('A', 10.0, 2)
        total1 = oc.calculate_total()
        oc.remove_item('A')
        oc.add_item('A', 10.0, 1)
        total2 = oc.calculate_total()
        self.assertNotEqual(total1, total2)

    def test_CT_13_total_after_clearing_order(self):
        oc = OrderCalculator()
        oc.add_item('A', 10.0, 1)
        oc.clear_order()
        with self.assertRaises(ValueError):
            oc.calculate_total()
        oc.add_item('B', 20.0, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 20 + 10 + (20 + 10) * 0.23, places=2)

    def test_CT_14_total_after_merging_quantities(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 5.0, 2)
        oc.add_item('Apple', 5.0, 3)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 43.05, places=2)

    def test_CT_15_total_shipping_change_around_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 60.0, 2)
        total1 = oc.calculate_total(discount=0.0)
        total2 = oc.calculate_total(discount=0.1)
        total3 = oc.calculate_total(discount=0.5)
        self.assertAlmostEqual(total1, total2, places=2)
        self.assertNotEqual(total2, total3)
        self.assertAlmostEqual(total3 - total2, 10.0, places=2)

    def test_IM_01_add_subtotal_clear_subtotal_raises(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 1.0)
        oc.clear_order()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_IM_02_add_remove_list_items(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0)
        oc.add_item('B', 2.0)
        oc.add_item('C', 3.0)
        oc.remove_item('B')
        self.assertCountEqual(oc.list_items(), ['A', 'C'])

    def test_IM_03_add_duplicate_total_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Apple', 1.0, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_IM_04_discount_affects_shipping(self):
        oc = OrderCalculator()
        oc.add_item('Item', 90.0, 1)
        total_no_discount = oc.calculate_total(discount=0.0)
        total_with_discount = oc.calculate_total(discount=0.2)
        self.assertNotEqual(total_no_discount, total_with_discount)
        self.assertAlmostEqual(total_no_discount - total_with_discount, 10.0, places=2)

    def test_IM_05_tax_changes_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('A', 10.0, 1)
        tax1 = oc.calculate_tax(oc.get_subtotal())
        oc.remove_item('A')
        oc.add_item('A', 5.0, 1)
        tax2 = oc.calculate_tax(oc.get_subtotal())
        self.assertNotEqual(tax1, tax2)

    def test_IM_06_multiple_clears(self):
        oc = OrderCalculator()
        oc.clear_order()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_IM_07_add_after_clear(self):
        oc = OrderCalculator()
        oc.clear_order()
        oc.add_item('A', 1.0, 1)
        self.assertFalse(oc.is_empty())
        self.assertEqual(oc.total_items(), 1)

    def test_IM_08_large_quantity_price_discount(self):
        oc = OrderCalculator()
        oc.add_item('GoldBar', 1000000.0, 1000)
        total = oc.calculate_total(discount=0.99)
        self.assertAlmostEqual(total, 12300000.0, delta=0.01)

    def test_IM_09_invalid_discount_type_propagates(self):
        oc = OrderCalculator()
        oc.add_item('A', 10.0, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount=[0.1])

    def test_IM_10_boundary_free_shipping_rounding(self):
        oc = OrderCalculator()
        oc.add_item('Item', 100.0000001, 1)
        total = oc.calculate_total(discount=1e-07)
        self.assertAlmostEqual(oc.calculate_shipping(oc.apply_discount(100.0000001, 1e-07)), 10.0)

    def test_M_01_zero_tax_rate(self):
        oc = OrderCalculator(tax_rate=0.0)
        oc.add_item('A', 10.0, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 20.0, places=2)

    def test_M_02_tax_rate_one(self):
        oc = OrderCalculator(tax_rate=1.0)
        oc.add_item('A', 10.0, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 40.0, places=2)

    def test_M_03_free_shipping_threshold_zero(self):
        oc = OrderCalculator(free_shipping_threshold=0.0)
        oc.add_item('A', 5.0, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 5.0 + 5.0 * 0.23, places=2)

    def test_M_04_shipping_cost_zero(self):
        oc = OrderCalculator(shipping_cost=0.0)
        oc.add_item('A', 5.0, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 5.0 + 5.0 * 0.23, places=2)

    def test_M_05_discount_integer_values(self):
        oc = OrderCalculator()
        oc.add_item('A', 10.0, 1)
        total0 = oc.calculate_total(discount=0)
        total1 = oc.calculate_total(discount=1)
        self.assertAlmostEqual(total0, 36.9, places=2)
        self.assertAlmostEqual(total1, 10.0, places=2)

    def test_M_06_quantity_boolean_true(self):
        oc = OrderCalculator()
        oc.add_item('Item', 5.0, True)
        self.assertEqual(oc.total_items(), 1)

    def test_M_07_quantity_boolean_false(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Item', 5.0, False)

    def test_M_08_name_with_whitespace(self):
        oc = OrderCalculator()
        oc.add_item('  Apple  ', 1.0, 1)
        self.assertIn('  Apple  ', oc.list_items())

    def test_M_09_very_small_discount(self):
        oc = OrderCalculator()
        oc.add_item('A', 100.0, 1)
        total = oc.calculate_total(discount=1e-09)
        discounted = oc.apply_discount(100.0, 1e-09)
        expected = discounted + oc.calculate_shipping(discounted) + oc.calculate_tax(discounted + oc.calculate_shipping(discounted))
        self.assertAlmostEqual(total, expected, places=6)

    def test_M_10_very_large_discount_close_to_one(self):
        oc = OrderCalculator()
        oc.add_item('A', 100.0, 1)
        total = oc.calculate_total(discount=0.999999)
        discounted = oc.apply_discount(100.0, 0.999999)
        expected = discounted + oc.calculate_shipping(discounted) + oc.calculate_tax(discounted + oc.calculate_shipping(discounted))
        self.assertAlmostEqual(total, expected, places=6)

    def test_M_11_repeated_add_remove_cycles(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0, 1)
        oc.remove_item('A')
        oc.add_item('A', 1.0, 1)
        oc.remove_item('A')
        self.assertTrue(oc.is_empty())