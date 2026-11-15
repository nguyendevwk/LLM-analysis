import unittest
from order_calculator import OrderCalculator
from decimal import Decimal
import numpy as np

class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    # 1
    def test_01_default_constructor(self):
        self.assertTrue(self.calc.is_empty())
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    # 2
    def test_02_custom_constructor(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertTrue(calc.is_empty())
        self.assertAlmostEqual(calc.get_subtotal(), 0.0)

    # 3
    def test_03_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    # 4
    def test_04_tax_rate_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    # 5
    def test_05_non_numeric_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.23")

    # 6
    def test_06_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    # 7
    def test_07_non_numeric_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    # 8
    def test_08_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    # 9
    def test_09_non_numeric_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    # 10
    def test_10_tax_rate_zero_and_one(self):
        calc0 = OrderCalculator(tax_rate=0.0)
        calc1 = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc0.calculate_tax(100.0), 0.0)
        self.assertAlmostEqual(calc1.calculate_tax(100.0), 100.0)

    # 11
    def test_11_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.calc.add_item("item", 10.0, 1)
        self.assertAlmostEqual(calc.calculate_shipping(10.0), 0.0)

    # 12
    def test_12_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.calc.add_item("item", 10.0, 1)
        self.assertAlmostEqual(calc.calculate_shipping(10.0), 0.0)

    # 13
    def test_13_add_item_default_quantity(self):
        self.calc.add_item("apple", 2.5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.5)
        self.assertEqual(self.calc.total_items(), 1)

    # 14
    def test_14_add_item_explicit_quantity(self):
        self.calc.add_item("banana", 1.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)
        self.assertEqual(self.calc.total_items(), 3)

    # 15
    def test_15_add_item_free_price(self):
        self.calc.add_item("freebie", 0.0, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.total_items(), 2)

    # 16
    def test_16_add_item_empty_name(self):
        self.calc.add_item("", 5.0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5.0)
        self.assertEqual(self.calc.total_items(), 1)

    # 17
    def test_17_add_duplicate_item(self):
        self.calc.add_item("item", 3.0, 1)
        self.calc.add_item("item", 3.0, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 9.0)
        self.assertEqual(self.calc.total_items(), 3)

    # 18
    def test_18_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("bad", -1.0)

    # 19
    def test_19_non_numeric_price(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("bad", "1.0")

    # 20
    def test_20_non_positive_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("bad", 1.0, 0)
        with self.assertRaises(ValueError):
            self.calc.add_item("bad", 1.0, -2)

    # 21
    def test_21_non_int_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("bad", 1.0, 1.5)

    # 22
    def test_22_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    # 23
    def test_23_remove_existing_item(self):
        self.calc.add_item("item", 2.0)
        self.calc.remove_item("item")
        self.assertTrue(self.calc.is_empty())

    # 24
    def test_24_remove_only_item(self):
        self.calc.add_item("solo", 5.0)
        self.calc.remove_item("solo")
        self.assertTrue(self.calc.is_empty())

    # 25
    def test_25_remove_multiple_quantity_item(self):
        self.calc.add_item("multi", 1.0, 5)
        self.calc.remove_item("multi")
        self.assertTrue(self.calc.is_empty())

    # 26
    def test_26_remove_nonexistent_item(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item("ghost")

    # 27
    def test_27_remove_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    # 28
    def test_28_remove_after_clear(self):
        self.calc.add_item("item", 1.0)
        self.calc.clear_order()
        with self.assertRaises(KeyError):
            self.calc.remove_item("item")

    # 29
    def test_29_get_subtotal_empty(self):
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    # 30
    def test_30_get_subtotal_single_item(self):
        self.calc.add_item("single", 4.5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 9.0)

    # 31
    def test_31_get_subtotal_multiple_items(self):
        self.calc.add_item("a", 1.0, 2)
        self.calc.add_item("b", 2.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0*2 + 2.0*3)

    # 32
    def test_32_get_subtotal_large_values(self):
        self.calc.add_item("big", 1e12, 1e6)
        subtotal = self.calc.get_subtotal()
        self.assertTrue(subtotal > 0.0)

    # 33
    def test_33_get_subtotal_precision(self):
        self.calc.add_item("precise", 0.1, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.3, places=7)

    # 34
    def test_34_apply_discount_normal(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 20.0), 80.0)

    # 35
    def test_35_apply_discount_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 0.0), 50.0)

    # 36
    def test_36_apply_discount_equal(self):
        self.assertAlmostEqual(self.calc.apply_discount(30.0, 30.0), 0.0)

    # 37
    def test_37_apply_discount_over(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, 20.0)

    # 38
    def test_38_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -5.0)

    # 39
    def test_39_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 5.0)

    # 40
    def test_40_apply_discount_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("10", 5.0)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(10.0, "5")

    # 41
    def test_41_apply_discount_small(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.0001), 99.9999, places=7)

    # 42
    def test_42_calculate_shipping_below_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(50.0), 10.0)

    # 43
    def test_43_calculate_shipping_at_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0)

    # 44
    def test_44_calculate_shipping_above_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(150.0), 0.0)

    # 45
    def test_45_calculate_shipping_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_shipping(-5.0)

    # 46
    def test_46_calculate_shipping_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("10")

    # 47
    def test_47_calculate_tax_positive(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200.0), 46.0)

    # 48
    def test_48_calculate_tax_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    # 49
    def test_49_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    # 50
    def test_50_calculate_tax_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("10")

    # 51
    def test_51_calculate_total_empty(self):
        self.assertAlmostEqual(self.calc.calculate_total(), 0.0)

    # 52
    def test_52_calculate_total_no_discount(self):
        self.calc.add_item("item", 20.0, 2)
        subtotal = 40.0
        shipping = 10.0
        tax = subtotal * 0.23
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    # 53
    def test_53_calculate_total_with_discount(self):
        self.calc.add_item("item", 50.0, 1)
        discounted = 30.0
        shipping = 10.0
        tax = discounted * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(discount=20.0), expected)

    # 54
    def test_54_calculate_total_full_discount(self):
        self.calc.add_item("item", 30.0, 1)
        shipping = 10.0
        tax = 0.0
        expected = shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(discount=30.0), expected)

    # 55
    def test_55_calculate_total_zero_subtotal(self):
        self.calc.add_item("item", 10.0, 1)
        expected = 10.0 * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(discount=10.0), expected)

    # 56
    def test_56_calculate_total_free_shipping(self):
        self.calc.add_item("expensive", 120.0, 1)
        expected = 120.0 + 120.0 * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    # 57
    def test_57_calculate_total_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item("item", 20.0, 1)
        expected = 20.0 + 10.0
        self.assertAlmostEqual(calc.calculate_total(), expected)

    # 58
    def test_58_calculate_total_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item("item", 20.0, 1)
        expected = 20.0 + 20.0 * 0.23
        self.assertAlmostEqual(calc.calculate_total(), expected)

    # 59
    def test_59_calculate_total_negative_discount(self):
        self.calc.add_item("item", 10.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-5.0)

    # 60
    def test_60_calculate_total_discount_over_subtotal(self):
        self.calc.add_item("item", 10.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=15.0)

    # 61
    def test_61_calculate_total_non_numeric_discount(self):
        self.calc.add_item("item", 10.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount="5")

    # 62
    def test_62_calculate_total_zero_discount_free_shipping(self):
        self.calc.add_item("expensive", 120.0, 1)
        self.assertAlmostEqual(self.calc.calculate_total(discount=0.0), 120.0 + 120.0 * 0.23)

    # 63
    def test_63_calculate_total_zero_discount_shipping(self):
        self.calc.add_item("cheap", 5.0, 1)
        expected = 5.0 + 10.0 + 5.0 * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(discount=0.0), expected)

    # 64
    def test_64_calculate_total_full_discount_free_shipping(self):
        self.calc.add_item("expensive", 120.0, 1)
        expected = 120.0 * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(discount=120.0), expected)

    # 65
    def test_65_calculate_total_full_discount_shipping(self):
        self.calc.add_item("cheap", 5.0, 1)
        expected = 10.0 + 5.0 * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(discount=5.0), expected)

    # 66
    def test_66_calculate_total_partial_discount_free_shipping(self):
        self.calc.add_item("expensive", 120.0, 1)
        discounted = 100.0
        tax = discounted * 0.23
        expected = discounted + tax
        self.assertAlmostEqual(self.calc.calculate_total(discount=20.0), expected)

    # 67
    def test_67_calculate_total_partial_discount_shipping(self):
        self.calc.add_item("cheap", 5.0, 1)
        discounted = 3.0
        tax = discounted * 0.23
        expected = discounted + 10.0 + tax
        self.assertAlmostEqual(self.calc.calculate_total(discount=2.0), expected)

    # 68
    def test_68_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    # 69
    def test_69_total_items_multiple(self):
        self.calc.add_item("a", 1.0, 2)
        self.calc.add_item("b", 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    # 70
    def test_70_total_items_after_clear(self):
        self.calc.add_item("a", 1.0, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    # 71
    def test_71_clear_order_after_items(self):
        self.calc.add_item("item", 5.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    # 72
    def test_72_clear_order_is_empty(self):
        self.calc.add_item("item", 5.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    # 73
    def test_73_clear_order_subtotal_zero(self):
        self.calc.add_item("item", 5.0, 1)
        self.calc.clear_order()
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    # 74
    def test_74_clear_order_total_items_zero(self):
        self.calc.add_item("item", 5.0, 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    # 75
    def test_75_clear_order_list_items_empty(self):
        self.calc.add_item("item", 5.0, 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    # 76
    def test_76_clear_order_total_zero(self):
        self.calc.add_item("item", 5.0, 1)
        self.calc.clear_order()
        self.assertAlmostEqual(self.calc.calculate_total(), 0.0)

    # 77
    def test_77_clear_order_multiple_times(self):
        self.calc.clear_order()
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    # 78
    def test_78_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    # 79
    def test_79_list_items_after_add(self):
        self.calc.add_item("x", 1.0)
        self.calc.add_item("y", 2.0)
        items = self.calc.list_items()
        self.assertIn("x", items)
        self.assertIn("y", items)
        self.assertEqual(len(items), 2)

    # 80
    def test_80_list_items_unique(self):
        self.calc.add_item("dup", 1.0, 2)
        self.calc.add_item("dup", 1.0, 3)
        items = self.calc.list_items()
        self.assertEqual(items.count("dup"), 1)

    # 81
    def test_81_list_items_order_unspecified(self):
        self.calc.add_item("a", 1.0)
        self.calc.add_item("b", 2.0)
        items = self.calc.list_items()
        self.assertCountEqual(items, ["a", "b"])

    # 82
    def test_82_list_items_after_clear(self):
        self.calc.add_item("item", 1.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    # 83
    def test_83_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    # 84
    def test_84_is_empty_false_after_add(self):
        self.calc.add_item("item", 1.0)
        self.assertFalse(self.calc.is_empty())

    # 85
    def test_85_is_empty_true_after_clear(self):
        self.calc.add_item("item", 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    # 86
    def test_86_is_empty_after_remove_all(self):
        self.calc.add_item("item", 1.0)
        self.calc.remove_item("item")
        self.assertTrue(self.calc.is_empty())

    # 87
    def test_87_add_remove_integration(self):
        self.calc.add_item("item", 5.0)
        self.calc.remove_item("item")
        self.assertTrue(self.calc.is_empty())
        self.assertAlmostEqual(self.calc.calculate_total(), 0.0)

    # 88
    def test_88_add_total_items_integration(self):
        self.calc.add_item("a", 1.0, 2)
        self.calc.add_item("b", 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    # 89
    def test_89_add_get_subtotal_integration(self):
        self.calc.add_item("a", 1.0, 2)
        self.calc.add_item("b", 2.0, 3)
        expected = 1.0*2 + 2.0*3
        self.assertAlmostEqual(self.calc.get_subtotal(), expected)

    # 90
    def test_90_add_calculate_total_integration(self):
        self.calc.add_item("item", 50.0, 1)
        expected = 50.0 + 10.0 + 50.0 * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    # 91
    def test_91_add_calculate_shipping_below_threshold_integration(self):
        self.calc.add_item("cheap", 30.0, 1)
        self.assertAlmostEqual(self.calc.calculate_shipping(30.0), 10.0)

    # 92
    def test_92_add_calculate_shipping_at_threshold_integration(self):
        self.calc.add_item("expensive", 100.0, 1)
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0)

    # 93
    def test_93_add_calculate_tax_integration(self):
        self.calc.add_item("item", 100.0, 1)
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    # 94
    def test_94_add_apply_discount_zero_subtotal_integration(self):
        self.calc.add_item("item", 10.0, 1)
        self.assertAlmostEqual(self.calc.apply_discount(10.0, 10.0), 0.0)

    # 95
    def test_95_add_apply_discount_zero_subtotal_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item("item", 10.0, 1)
        self.assertAlmostEqual(calc.calculate_shipping(0.0), 0.0)

    # 96
    def test_96_add_apply_discount_equal_subtotal_integration(self):
        self.calc.add_item("item", 20.0, 1)
        self.assertAlmostEqual(self.calc.apply_discount(20.0, 20.0), 0.0)

    # 97
    def test_97_add_remove_calculate_total_integration(self):
        self.calc.add_item("a", 10.0, 1)
        self.calc.add_item("b", 20.0, 1)
        self.calc.remove_item("a")
        expected = 20.0 + 10.0 + 20.0 * 0.23
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    # 98
    def test_98_add_remove_total_items_integration(self):
        self.calc.add_item("a", 1.0, 2)
        self.calc.add_item("b", 2.0, 3)
        self.calc.remove_item("a")
        self.assertEqual(self.calc.total_items(), 3)

    # 99
    def test_99_add_list_items_integration(self):
        self.calc.add_item("dup", 1.0, 2)
        self.calc.add_item("dup", 1.0, 3)
        items = self.calc.list_items()
        self.assertEqual(items.count("dup"), 1)

    # 100
    def test_100_add_clear_total_integration(self):
        self.calc.add_item("item", 10.0, 1)
        self.calc.clear_order()
        self.assertAlmostEqual(self.calc.calculate_total(), 0.0)

    # 101
    def test_101_calculate_total_large_values(self):
        self.calc.add_item("big", 1e12, 1)
        total = self.calc.calculate_total()
        self.assertTrue(total > 0.0)

    # 102
    def test_102_calculate_total_small_values(self):
        self.calc.add_item("tiny", 1e-6, 1)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 1e-6 + 1e-6 * 0.23 + 10.0, places=9)

    # 103
    def test_103_calculate_total_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item("item", 10.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 10.0 + 10.0)

    # 104
    def test_104_calculate_total_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item("item", 10.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 10.0 + 10.0 * 0.23)

    # 105
    def test_105_calculate_total_free_shipping_always(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item("item", 10.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 10.0 + 10.0 * 0.23)

    # 106
    def test_106_calculate_total_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        calc.add_item("item", 10.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 10.0 + 10.0 + 10.0)

    # 107
    def test_107_calculate_total_high_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=1e9)
        calc.add_item("item", 10.0, 1)
        self.assertAlmostEqual(calc.calculate_shipping(10.0), 10.0)

    # 108
    def test_108_calculate_total_high_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=1e9)
        calc.add_item("item", 10.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 10.0 + 1e9 + 10.0 * 0.23)

    # 109
    def test_109_add_item_large_price_quantity(self):
        self.calc.add_item("mega", 1e9, 1e6)
        subtotal = self.calc.get_subtotal()
        self.assertTrue(subtotal > 0.0)

    # 110
    def test_110_add_item_small_price(self):
        self.calc.add_item("nano", 1e-9, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1e-9, places=12)

    # 111
    def test_111_add_item_default_quantity(self):
        self.calc.add_item("default", 5.0)
        self.assertEqual(self.calc.total_items(), 1)

    # 112
    def test_112_add_item_increment_quantity(self):
        self.calc.add_item("dup", 1.0, 1)
        self.calc.add_item("dup", 1.0, 1)
        self.assertEqual(self.calc.total_items(), 2)

    # 113
    def test_113_remove_multiple_quantity_item(self):
        self.calc.add_item("multi", 1.0, 5)
        self.calc.remove_item("multi")
        self.assertTrue(self.calc.is_empty())

    # 114
    def test_114_remove_nonexistent_item(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item("ghost")

    # 115
    def test_115_remove_after_clear(self):
        self.calc.add_item("item", 1.0)
        self.calc.clear_order()
        with self.assertRaises(KeyError):
            self.calc.remove_item("item")

    # 116
    def test_116_remove_empty_string_name(self):
        self.calc.add_item("", 1.0)
        self.calc.remove_item("")
        self.assertTrue(self.calc.is_empty())

    # 117
    def test_117_remove_case_sensitive(self):
        self.calc.add_item("Item", 1.0)
        with self.assertRaises(KeyError):
            self.calc.remove_item("item")

    # 118
    def test_118_list_items_copy(self):
        self.calc.add_item("item", 1.0)
        items = self.calc.list_items()
        items.append("fake")
        self.assertNotIn("fake", self.calc.list_items())

    # 119
    def test_119_list_items_independent(self):
        self.calc.add_item("item", 1.0)
        items = self.calc.list_items()
        items.pop()
        self.assertEqual(len(self.calc.list_items()), 1)

    # 120
    def test_120_total_items_integer(self):
        self.calc.add_item("item", 1.0, 1)
        self.assertIsInstance(self.calc.total_items(), int)

    # 121
    def test_121_total_items_after_multiple_adds(self):
        self.calc.add_item("a", 1.0, 2)
        self.calc.add_item("b", 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    # 122
    def test_122_is_empty_after_add_remove(self):
        self.calc.add_item("item", 1.0)
        self.calc.remove_item("item")
        self.assertTrue(self.calc.is_empty())

    # 123
    def test_123_is_empty_before_remove(self):
        self.calc.add_item("item", 1.0)
        self.assertFalse(self.calc.is_empty())

    # 124
    def test_124_clear_order_on_empty(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    # 125
    def test_125_clear_then_add(self):
        self.calc.clear_order()
        self.calc.add_item("item", 1.0)
        self.assertFalse(self.calc.is_empty())

    # 126
    def test_126_calculate_total_no_state_change(self):
        self.calc.add_item("item", 10.0)
        total1 = self.calc.calculate_total()
        total2 = self.calc.calculate_total()
        self.assertAlmostEqual(total1, total2)

    # 127
    def test_127_calculate_total_idempotent(self):
        self.calc.add_item("item", 10.0)
        total1 = self.calc.calculate_total()
        total2 = self.calc.calculate_total()
        self.assertAlmostEqual(total1, total2)

    # 128
    def test_128_calculate_total_precision(self):
        self.calc.add_item("precise", 0.1, 3)
        self.assertAlmostEqual(self.calc.calculate_total(), 0.3 + 10.0 + 0.3 * 0.23, places=7)

    # 129
    def test_129_calculate_total_small_positive_subtotal(self):
        self.calc.add_item("tiny", 1e-12, 1)
        self.assertAlmostEqual(self.calc.calculate_total(), 1e-12 + 10.0 + 1e-12 * 0.23, places=15)

    # 130
    def test_130_calculate_total_zero_subtotal(self):
        self.calc.add_item("zero", 0.0, 1)
        self.assertAlmostEqual(self.calc.calculate_total(), 0.0 + 10.0 + 0.0 * 0.23)

    # 131
    def test_131_calculate_total_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1e12)

    # 132
    def test_132_calculate_total_non_numeric_discount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount="5")

    # 133
    def test_133_calculate_total_string_discount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount="5")

    # 134
    def test_134_calculate_total_none_discount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=None)

    # 135
    def test_135_calculate_total_invalid_discount_range(self):
        self.calc.add_item("item", 10.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-5.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=15.0)

    # 136
    def test_136_calculate_total_integer_discount(self):
        self.calc.add_item("item", 10.0)
        self.assertAlmostEqual(self.calc.calculate_total(discount=5), 10.0 - 5.0 + 10.0 + (10.0 - 5.0) * 0.23)

    # 137
    def test_137_calculate_total_decimal_discount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=Decimal('5'))

    # 138
    def test_138_calculate_total_numpy_float_discount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=np.float64(5.0))

    # 139
    def test_139_calculate_total_string_of_number_discount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount="5.0")

    # 140
    def test_140_calculate_total_boolean_discount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=True)

    # 141
    def test_141_calculate_total_list_discount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=[5])

    # 142
    def test_142_calculate_total_dict_discount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount={"discount":5})

    # 143
    def test_143_calculate_total_tuple_discount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=(5,))

    # 144
    def test_144_calculate_total_set_discount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount={5})

    # 145
    def test_145_calculate_total_custom_object_discount(self):
        class Dummy: pass
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=Dummy())

    # 146
    def test_146_calculate_total_nan_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=float('nan'))

    # 147
    def test_147_calculate_total_inf_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=float('inf'))

    # 148
    def test_148_calculate_total_neg_inf_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=float('-inf'))

    # 149
    def test_149_calculate_total_decimal_nan_discount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=Decimal('NaN'))

    # 150
    def test_150_calculate_total_decimal_inf_discount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=Decimal('Infinity'))

if __name__ == "__main__":
    unittest.main()