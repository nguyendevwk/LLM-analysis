import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_01_init_defaults(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)
        self.assertEqual(calc.calculate_shipping(80.0), 10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_02_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 0.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_03_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_04_init_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_05_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_06_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_07_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_08_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_09_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[5])

    def test_10_init_mixed_invalid_first_fails(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=0.5, free_shipping_threshold=-1, shipping_cost=5)

    def test_11_add_item_first_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        self.assertEqual(calc.total_items(), 1)
        self.assertEqual(calc.list_items(), ['Apple'])
        self.assertAlmostEqual(calc.get_subtotal(), 1.0)

    def test_12_add_item_explicit_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.5, 3)
        self.assertEqual(calc.total_items(), 3)
        self.assertAlmostEqual(calc.get_subtotal(), 1.5)

    def test_13_add_item_same_name_price_increments_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(calc.total_items(), 3)
        self.assertAlmostEqual(calc.get_subtotal(), 3.0)

    def test_14_add_item_same_name_different_price_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.5)

    def test_15_add_item_empty_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    def test_16_add_item_name_not_string_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_17_add_item_price_non_positive_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', 0.0)
        with self.assertRaises(ValueError):
            calc.add_item('Item', -2.0)

    def test_18_add_item_price_wrong_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', '5.0')

    def test_19_add_item_quantity_less_than_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item('Item', 1.0, -3)

    def test_20_add_item_quantity_wrong_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', 1.0, 2.5)

    def test_21_add_item_after_clear_order(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        calc.add_item('B', 2.0, 1)
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0)

    def test_22_remove_item_existing_quantity_one(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_23_remove_item_existing_quantity_more_than_one(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 4)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_24_remove_item_non_existent_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Pear')

    def test_25_remove_item_name_not_string_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(5)

    def test_26_remove_item_then_re_add_same_name(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(calc.total_items(), 1)

    def test_27_remove_item_leaves_others_intact(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 2)
        calc.remove_item('Apple')
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 4.0)
        self.assertEqual(calc.list_items(), ['Banana'])

    def test_28_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 6.0)

    def test_29_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 2)
        calc.add_item('Banana', 1.5, 4)
        self.assertAlmostEqual(calc.get_subtotal(), 10.0)

    def test_30_get_subtotal_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_32_apply_discount_zero_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_33_apply_discount_twenty_percent(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50.0, 0.2), 40.0)

    def test_34_apply_discount_full_discount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(30.0, 1.0), 0.0)

    def test_35_apply_discount_fractional(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(10.0, 0.33), 6.7, places=5)

    def test_36_apply_discount_negative_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-5.0, 0.1)

    def test_37_apply_discount_discount_negative_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(10.0, -0.1)

    def test_38_apply_discount_discount_above_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(10.0, 1.5)

    def test_39_apply_discount_subtotal_wrong_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('10', 0.1)

    def test_40_apply_discount_discount_wrong_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(10.0, None)

    def test_41_apply_discount_zero_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(0.0, 0.5), 0.0)

    def test_42_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(80.0), 10.0)

    def test_43_calculate_shipping_at_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_44_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_45_calculate_shipping_zero_subtotal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(0.0), 10.0)

    def test_46_calculate_shipping_custom_threshold_cost(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(49.9), 5.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_47_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(-10.0), 10.0)

    def test_48_calculate_shipping_non_numeric_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('50')

    def test_49_calculate_shipping_none_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping(None)

    def test_50_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_51_calculate_tax_positive_default_rate(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_52_calculate_tax_fractional_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(15.5), 15.5 * 0.23, places=5)

    def test_53_calculate_tax_custom_rate(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(calc.calculate_tax(200.0), 10.0)

    def test_54_calculate_tax_negative_amount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-1.0)

    def test_55_calculate_tax_non_numeric_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('10')

    def test_56_calculate_tax_none_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax(None)

    def test_57_calculate_total_no_discount_shipping_applied(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 2)
        self.assertAlmostEqual(calc.calculate_total(), 36.9, places=2)

    def test_58_calculate_total_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Item', 60.0, 2)
        self.assertAlmostEqual(calc.calculate_total(), 147.6, places=2)

    def test_59_calculate_total_ten_percent_discount_still_below_threshold(self):
        calc = OrderCalculator()
        calc.add_item('Item', 40.0, 2)
        self.assertAlmostEqual(calc.calculate_total(discount=0.1), 100.86, places=2)

    def test_60_calculate_total_discount_above_threshold(self):
        calc = OrderCalculator()
        calc.add_item('Item', 150.0, 1)
        self.assertAlmostEqual(calc.calculate_total(discount=0.1), 166.05, places=2)

    def test_61_calculate_total_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_62_calculate_total_discount_negative_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.05)

    def test_63_calculate_total_discount_above_one_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.2)

    def test_64_calculate_total_discount_wrong_type_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='0.1')

    def test_65_calculate_total_discount_one_free_items(self):
        calc = OrderCalculator()
        calc.add_item('Item', 50.0, 1)
        self.assertAlmostEqual(calc.calculate_total(discount=1.0), 12.3, places=2)

    def test_66_calculate_total_zero_discount_shipping_free(self):
        calc = OrderCalculator()
        calc.add_item('Item', 110.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 135.3, places=2)

    def test_67_calculate_total_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 5.0, 2)
        calc.add_item('B', 3.0, 4)
        self.assertAlmostEqual(calc.calculate_total(discount=0.05), 38.007, places=3)

    def test_68_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_69_total_items_single_item_qty_one(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        self.assertEqual(calc.total_items(), 1)

    def test_70_total_items_single_item_qty_more_than_one(self):
        calc = OrderCalculator()
        calc.add_item('Item', 2.0, 5)
        self.assertEqual(calc.total_items(), 5)

    def test_71_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 3.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_72_total_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 2.0, 3)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 3)

    def test_73_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_74_clear_order_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 2.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)

    def test_75_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_76_clear_order_then_add_again(self):
        calc = OrderCalculator()
        calc.clear_order()
        calc.add_item('New', 5.0, 1)
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 5.0)

    def test_77_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_78_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_79_list_items_multiple_distinct(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 1)
        items = set(calc.list_items())
        self.assertEqual(items, {'Apple', 'Banana'})

    def test_80_list_items_no_duplicate_on_same_name_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_81_list_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 1)
        calc.remove_item('Apple')
        self.assertEqual(calc.list_items(), ['Banana'])

    def test_82_list_items_returned_list_is_copy(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        lst = calc.list_items()
        lst.append('dummy')
        self.assertNotIn('dummy', calc.list_items())

    def test_83_is_empty_empty(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_84_is_empty_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_85_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_86_is_empty_after_removing_last(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 1)
        calc.remove_item('A')
        calc.remove_item('B')
        self.assertTrue(calc.is_empty())

    def test_87_is_empty_add_then_remove_same(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.remove_item('Item')
        self.assertTrue(calc.is_empty())