import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def test_01_default_construction(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_02_valid_custom_values(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0)
        self.assertEqual(oc.shipping_cost, 0)

    def test_03_init_type_error_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_04_init_range_error_tax_rate_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_05_init_range_error_tax_rate_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_06_init_type_error_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_07_init_value_error_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1)

    def test_08_init_type_error_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_09_init_value_error_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_10_add_item_simple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['name'], 'Apple')
        self.assertEqual(oc.items[0]['price'], 1.5)
        self.assertEqual(oc.items[0]['quantity'], 2)

    def test_11_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8)
        self.assertEqual(oc.items[0]['quantity'], 1)

    def test_12_add_item_aggregation_same_name_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['quantity'], 5)

    def test_13_add_item_conflict_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0, 1)

    def test_14_add_item_type_error_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_15_add_item_value_error_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_16_add_item_type_error_price(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', '1.5', 1)

    def test_17_add_item_value_error_price_nonpositive(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', -1, 1)

    def test_18_add_item_type_error_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', 1.5, 2.5)

    def test_19_add_item_value_error_quantity_low(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 1.5, 0)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 1.5, -3)

    def test_20_remove_item_successful(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_21_remove_item_after_aggregation(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Apple', 1.0, 3)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_22_remove_item_nonexistent(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Banana')

    def test_23_remove_item_type_error_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_24_get_subtotal_normal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 3)
        oc.add_item('Banana', 1.0, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 8.0)

    def test_25_get_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 5.5, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 5.5)

    def test_26_get_subtotal_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_27_apply_discount_no_discount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100.0, 0.0), 100.0)

    def test_28_apply_discount_half(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(200.0, 0.5), 100.0)

    def test_29_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50.0, 1.0), 0.0)

    def test_30_apply_discount_type_error_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100.0, '0.2')

    def test_31_apply_discount_type_error_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)

    def test_32_apply_discount_out_of_range_low(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -0.1)

    def test_33_apply_discount_out_of_range_high(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, 1.2)

    def test_34_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10, 0.1)

    def test_35_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(90.0), 10.0)

    def test_36_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(100.0), 0.0)

    def test_37_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(150.0), 0.0)

    def test_38_calculate_shipping_custom_below(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(oc.calculate_shipping(49.99), 5.0)

    def test_39_calculate_shipping_custom_at_or_above(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(oc.calculate_shipping(50.0), 0.0)

    def test_40_calculate_shipping_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('30')

    def test_41_calculate_tax_standard(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(100.0), 23.0)

    def test_42_calculate_tax_zero(self):
        oc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(oc.calculate_tax(123.45), 0.0)

    def test_43_calculate_tax_full(self):
        oc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(oc.calculate_tax(10), 10.0)

    def test_44_calculate_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5)

    def test_45_calculate_tax_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax('10')

    def test_46_calculate_total_simple_shipping_charged(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 2)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 61.5)

    def test_47_calculate_total_discount_below_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 30, 2)
        total = oc.calculate_total(0.5)
        self.assertAlmostEqual(total, 49.2)

    def test_48_calculate_total_discount_not_free_shipping(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 120, 1)
        total = oc.calculate_total(0.2)
        self.assertAlmostEqual(total, 130.38, places=2)

    def test_49_calculate_total_discount_exact_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 100, 1)
        total = oc.calculate_total(0.0)
        self.assertAlmostEqual(total, 123.0)

    def test_50_calculate_total_full_discount(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20, 1)
        total = oc.calculate_total(1.0)
        self.assertAlmostEqual(total, 12.3)

    def test_51_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_52_calculate_total_invalid_discount_type(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 10, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total('0.1')

    def test_53_calculate_total_discount_out_of_range_low(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 10, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(-0.1)

    def test_54_calculate_total_discount_out_of_range_high(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 10, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(1.5)

    def test_55_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_56_total_items_multiple_distinct(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Banana', 1, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_57_total_items_aggregation(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Apple', 1, 4)
        self.assertEqual(oc.total_items(), 6)

    def test_58_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Banana', 1, 3)
        oc.remove_item('Apple')
        self.assertEqual(oc.total_items(), 3)

    def test_59_total_items_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.clear_order()
        self.assertEqual(oc.total_items(), 0)

    def test_60_clear_order_resets(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(len(oc.items), 0)

    def test_61_list_items_unique_names(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Apple', 1, 1)
        oc.add_item('Banana', 2, 1)
        items =