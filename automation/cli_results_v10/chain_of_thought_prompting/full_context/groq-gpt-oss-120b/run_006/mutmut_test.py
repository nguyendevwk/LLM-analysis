import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_01_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_02_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(calc.tax_rate, 0)
        self.assertEqual(calc.free_shipping_threshold, 0)
        self.assertEqual(calc.shipping_cost, 0)

    def test_03_init_tax_int(self):
        calc = OrderCalculator(tax_rate=1)
        self.assertEqual(calc.tax_rate, 1)

    def test_04_init_tax_out_of_range_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_05_init_tax_out_of_range_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_06_init_tax_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_07_init_free_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_08_init_free_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_09_init_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_10_init_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    def test_11_add_item_new_default_quantity(self):
        self.calc.add_item('Apple', 1.5)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['name'], 'Apple')
        self.assertEqual(self.calc.items[0]['price'], 1.5)
        self.assertEqual(self.calc.items[0]['quantity'], 1)

    def test_12_add_item_new_explicit_quantity(self):
        self.calc.add_item('Banana', 2.0, 3)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 3)

    def test_13_add_item_increment_quantity(self):
        self.calc.add_item('Orange', 1.0, 2)
        self.calc.add_item('Orange', 1.0, 3)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 5)

    def test_14_add_item_same_name_different_price(self):
        self.calc.add_item('Grape', 1.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Grape', 2.0)

    def test_15_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0)

    def test_16_add_item_name_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_17_add_item_price_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', 0)

    def test_18_add_item_price_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', -1.0)

    def test_19_add_item_price_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Pear', '9.99')

    def test_20_add_item_price_int(self):
        self.calc.add_item('Kiwi', 5)
        self.assertEqual(self.calc.items[0]['price'], 5)

    def test_21_add_item_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Mango', 1.0, 0)

    def test_22_add_item_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Mango', 1.0, -2)

    def test_23_add_item_quantity_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Mango', 1.0, 2.5)

    def test_24_add_item_default_quantity(self):
        self.calc.add_item('Papaya', 3.0)
        self.assertEqual(self.calc.items[0]['quantity'], 1)

    def test_25_remove_item_single(self):
        self.calc.add_item('Lemon', 1.0)
        self.calc.remove_item('Lemon')
        self.assertEqual(len(self.calc.items), 0)

    def test_26_remove_item_multiple(self):
        self.calc.add_item('A', 1.0)
        self.calc.add_item('B', 2.0)
        self.calc.add_item('C', 3.0)
        self.calc.remove_item('B')
        names = [i['name'] for i in self.calc.items]
        self.assertCountEqual(names, ['A', 'C'])

    def test_27_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_28_remove_item_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(None)

    def test_29_get_subtotal_multiple_items(self):
        self.calc.add_item('X', 2.0, 2)
        self.calc.add_item('Y', 5.0, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 9.0)

    def test_30_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_31_apply_discount_no_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 0.0), 100.0)

    def test_32_apply_discount_half(self):
        self.assertAlmostEqual(self.calc.apply_discount(200, 0.5), 100.0)

    def test_33_apply_discount_full(self):
        self.assertAlmostEqual(self.calc.apply_discount(50, 1.0), 0.0)

    def test_34_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, -0.1)

    def test_35_apply_discount_over_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, 1.2)

    def test_36_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10, 0.1)

    def test_37_apply_discount_subtotal_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)

    def test_38_apply_discount_discount_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, [0.2])

    def test_39_apply_discount_subtotal_int(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 0.1), 90.0)

    def test_40_apply_discount_discount_int(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 0), 100.0)

    def test_41_calculate_shipping_above_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(150), 0.0)

    def test_42_calculate_shipping_at_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(100), 0.0)

    def test_43_calculate_shipping_below_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(99.99), 10.0)

    def test_44_calculate_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping(None)

    def test_45_calculate_shipping_zero_cost(self):
        calc = OrderCalculator(shipping_cost=0)
        self.assertAlmostEqual(calc.calculate_shipping(50), 0.0)

    def test_46_calculate_shipping_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0)
        self.assertAlmostEqual(calc.calculate_shipping(0), 0.0)
        self.assertAlmostEqual(calc.calculate_shipping(10), 0.0)

    def test_47_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0), 0.0)

    def test_48_calculate_tax_positive_default(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200), 46.0)

    def test_49_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0)
        self.assertAlmostEqual(calc.calculate_tax(123), 0.0)

    def test_50_calculate_tax_full_rate(self):
        calc = OrderCalculator(tax_rate=1)
        self.assertAlmostEqual(calc.calculate_tax(77), 77.0)

    def test_51_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5)

    def test_52_calculate_tax_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('50')

    def test_53_calculate_tax_amount_int(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200), 46.0)

    def test_54_calculate_total_typical(self):
        self.calc.add_item('Item1', 20.0, 2)
        self.calc.add_item('Item2', 15.0, 1)
        total = self.calc.calculate_total(0.1)
        self.assertAlmostEqual(total, 73.185, places=5)

    def test_55_calculate_total_free_shipping(self):
        self.calc.add_item('Expensive', 120.0, 1)
        total = self.calc.calculate_total(0.0)
        subtotal = 120.0
        tax = subtotal * 0.23
        expected = subtotal + tax
        self.assertAlmostEqual(total, expected, places=5)

    def test_56_calculate_total_full_discount(self):
        self.calc.add_item('Cheap', 5.0, 1)
        total = self.calc.calculate_total(1.0)
        shipping = 10.0
        tax = shipping * 0.23
        expected = shipping + tax
        self.assertAlmostEqual(total, expected, places=5)

    def test_57_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_58_calculate_total_discount_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.2')

    def test_59_calculate_total_discount_negative(self):
        self.calc.add_item('A', 10)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-0.1)

    def test_60_calculate_total_discount_over_one(self):
        self.calc.add_item('A', 10)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.5)

    def test_61_calculate_total_custom_no_shipping(self):
        calc = OrderCalculator(shipping_cost=0)
        calc.add_item('Item', 60, 2)
        total = calc.calculate_total(0.0)
        expected = 120.0 + 120.0 * 0.23
        self.assertAlmostEqual(total, expected, places=5)

    def test_62_calculate_total_custom_no_tax(self):
        calc = OrderCalculator(tax_rate=0)
        calc.add_item('Item', 30, 2)
        total = calc.calculate_total(0.0)
        expected = 60.0 + 10.0
        self.assertAlmostEqual(total, expected, places=5)

    def test_63_calculate_total_no_mutation(self):
        self.calc.add_item('A', 10, 2)
        before_items = list(self.calc.items)
        before_total_items = self.calc.total_items()
        before_list = self.calc.list_items()
        self.calc.calculate_total(0.1)
        self.assertEqual(self.calc.items, before_items)
        self.assertEqual(self.calc.total_items(), before_total_items)
        self.assertCountEqual(self.calc.list_items(), before_list)

    def test_64_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_65_total_items_after_add(self):
        self.calc.add_item('A', 1, 1)
        self.calc.add_item('B', 2, 3)
        self.assertEqual(self.calc.total_items(), 4)

    def test_66_total_items_after_remove(self):
        self.calc.add_item('A', 1, 2)
        self.calc.add_item('B', 1, 3)
        self.calc.remove_item('A')
        self.assertEqual(self.calc.total_items(), 3)

    def test_67_total_items_after_clear(self):
        self.calc.add_item('A', 1, 5)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_68_clear_order_non_empty(self):
        self.calc.add_item('A', 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    def test_69_clear_order_already_empty(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_70_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_71_list_items_duplicates(self):
        self.calc.add_item('apple', 1, 2)
        self.calc.add_item('banana', 2, 1)
        self.calc.add_item('apple', 1, 1)
        self.assertCountEqual(self.calc.list_items(), ['apple', 'banana'])

    def test_72_list_items_after_remove(self):
        self.calc.add_item('apple', 1)
        self.calc.add_item('banana', 2)
        self.calc.remove_item('apple')
        self.assertCountEqual(self.calc.list_items(), ['banana'])

    def test_73_list_items_after_clear(self):
        self.calc.add_item('apple', 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_74_is_empty_fresh(self):
        self.assertTrue(self.calc.is_empty())

    def test_75_is_empty_after_add(self):
        self.calc.add_item('A', 1)
        self.assertFalse(self.calc.is_empty())

    def test_76_is_empty_after_remove(self):
        self.calc.add_item('A', 1)
        self.calc.remove_item('A')
        self.assertTrue(self.calc.is_empty())

    def test_77_is_empty_after_clear(self):
        self.calc.add_item('A', 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_78_state_consistency_add_clear_add(self):
        self.calc.add_item('A', 1)
        self.calc.clear_order()
        self.calc.add_item('B', 2)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 1)
        self.assertCountEqual(self.calc.list_items(), ['B'])

    def test_79_state_consistency_remove_full_quantity(self):
        self.calc.add_item('A', 1, 4)
        self.calc.remove_item('A')
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    def test_80_state_consistency_sequence(self):
        self.calc.add_item('A', 1, 2)
        self.calc.add_item('B', 2, 3)
        self.calc.remove_item('A')
        self.calc.add_item('A', 1, 1)
        self.assertCountEqual(self.calc.list_items(), ['A', 'B'])
        self.assertEqual(self.calc.total_items(), 4)