import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def test_01_default_construction(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_02_custom_valid_parameters(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0.0)
        self.assertEqual(oc.shipping_cost, 0.0)

    def test_03_tax_rate_lower_bound(self):
        oc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(oc.tax_rate, 0.0)

    def test_04_tax_rate_upper_bound(self):
        oc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(oc.tax_rate, 1.0)

    def test_05_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_06_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_07_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_08_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_09_parameter_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_10_all_parameters_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='a', free_shipping_threshold='b', shipping_cost=None)

    def test_11_add_single_valid_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(oc.total_items(), 2)
        self.assertIn('Apple', oc.list_items())

    def test_12_add_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8)
        self.assertEqual(oc.total_items(), 1)
        self.assertIn('Banana', oc.list_items())

    def test_13_merge_same_name_same_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_14_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0, 1)

    def test_15_add_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0)

    def test_16_add_whitespace_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('   ', 1.0)

    def test_17_add_zero_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 0.0)

    def test_18_add_negative_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', -0.5)

    def test_19_quantity_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 1.0, 0)

    def test_20_quantity_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 1.0, -3)

    def test_21_name_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0)

    def test_22_price_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Kiwi', '1.0')

    def test_23_quantity_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Kiwi', 1.0, 2.5)

    def test_24_very_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Gadget', 99.99, 10**6)
        self.assertEqual(oc.total_items(), 10**6)

    def test_25_high_precision_price(self):
        oc = OrderCalculator()
        oc.add_item('Gold', 1234.56789, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 1234.56789, places=7)

    def test_26_remove_existing_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_27_remove_nonexistent_item(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('NonExisting')

    def test_28_remove_name_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(42)

    def test_29_remove_until_empty(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_30_is_empty_fresh(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_31_is_empty_after_add(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        self.assertFalse(oc.is_empty())

    def test_32_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_33_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 1.0, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_34_list_items_no_duplicates(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.add_item('Banana', 1.0)
        oc.add_item('Apple', 1.0, 2)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana'])

    def test_35_list_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_36_clear_order(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 1.0, 3)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)
        self.assertEqual(oc.list_items(), [])

    def test_37_clear_and_readd(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.clear_order()
        oc.add_item('Apple', 1.0, 1)
        self.assertEqual(oc.total_items(), 1)

    def test_38_get_subtotal_normal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 0.8, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 3.8, places=7)

    def test_39_get_subtotal_floating(self):
        oc = OrderCalculator()
        oc.add_item('Item', 0.1, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 0.30000000000000004, places=15)

    def test_40_get_subtotal_large_numbers(self):
        oc = OrderCalculator()
        oc.add_item('Big', 1e6, 1000)
        self.assertAlmostEqual(oc.get_subtotal(), 1e9, places=5)

    def test_41_get_subtotal_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_42_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(100.0, 0.0), 100.0)

    def test_43_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(100.0, 1.0), 0.0)

    def test_44_apply_discount_typical(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(200.0, 0.15), 170.0, places=7)

    def test_45_apply_discount_below_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -1e-12)

    def test_46_apply_discount_above_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, 1.0000001)

    def test_47_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-5.0, 0.1)

    def test_48_apply_discount_subtotal_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)

    def test_49_apply_discount_discount_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100.0, '0.1')

    def test_50_apply_discount_integer_out_of_range(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, 20)

    def test_51_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(99.99), 10.0)

    def test_52_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(100.0), 0.0)

    def test_53_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(150.0), 0.0)

    def test_54_calculate_shipping_zero(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(0.0), 10.0)

    def test_55_calculate_shipping_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('50')

    def test_56_calculate_shipping_custom_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5.5)
        self.assertEqual(oc.calculate_shipping(49.9), 5.5)

    def test_57_calculate_shipping_custom_above(self):
        oc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5.5)
        self.assertEqual(oc.calculate_shipping(50.0), 0.0)

    def test_58_calculate_shipping_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_shipping(-1.0)

    def test_59_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_tax(0.0), 0.0)

    def test_60_calculate_tax_positive(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(100.0), 23.0, places=7)

    def test_61_calculate_tax_custom_rate(self):
        oc = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(oc.calculate_tax(200), 10.0, places=7)

    def test_62_calculate_tax_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5.0)

    def test_63_calculate_tax_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax('100')

    def test_64_calculate_tax_large_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(1e9), 1e9 * 0.23, places=5)

    def test_65_calculate_total_simple_no_discount_shipping(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 20.0, 2)
        total = oc.calculate_total(0