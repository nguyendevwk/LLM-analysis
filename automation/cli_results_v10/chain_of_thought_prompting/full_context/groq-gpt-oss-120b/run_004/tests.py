import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_01_constructor_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_02_constructor_zero_values(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_03_constructor_tax_rate_type_error(self):
        with self.assertRaisesRegex(TypeError, 'Tax rate must be a float or int.'):
            OrderCalculator(tax_rate='0.2')

    def test_04_constructor_tax_rate_negative(self):
        with self.assertRaisesRegex(ValueError, 'Tax rate must be between 0.0 and 1.0.'):
            OrderCalculator(tax_rate=-0.1)

    def test_05_constructor_tax_rate_over_one(self):
        with self.assertRaisesRegex(ValueError, 'Tax rate must be between 0.0 and 1.0.'):
            OrderCalculator(tax_rate=1.5)

    def test_06_constructor_free_shipping_threshold_type_error(self):
        with self.assertRaisesRegex(TypeError, 'Free shipping threshold must be a float or int.'):
            OrderCalculator(free_shipping_threshold='100')

    def test_07_constructor_free_shipping_threshold_negative(self):
        with self.assertRaisesRegex(ValueError, 'Free shipping threshold cannot be negative.'):
            OrderCalculator(free_shipping_threshold=-5)

    def test_08_constructor_shipping_cost_type_error(self):
        with self.assertRaisesRegex(TypeError, 'Shipping cost must be a float or int.'):
            OrderCalculator(shipping_cost=None)

    def test_09_constructor_shipping_cost_negative(self):
        with self.assertRaisesRegex(ValueError, 'Shipping cost cannot be negative.'):
            OrderCalculator(shipping_cost=-1)

    def test_10_add_item_normal(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(self.calc.items, [{'name': 'Apple', 'price': 1.5, 'quantity': 2}])

    def test_11_add_item_default_quantity(self):
        self.calc.add_item('Banana', 0.8)
        self.assertEqual(self.calc.items[0]['quantity'], 1)

    def test_12_add_item_merge_duplicate(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Apple', 1.5, 3)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 5)

    def test_13_add_item_conflict_price(self):
        self.calc.add_item('Apple', 1.5, 2)
        with self.assertRaisesRegex(ValueError, 'Item with the same name but different price already exists.'):
            self.calc.add_item('Apple', 2.0, 1)

    def test_14_add_item_empty_name(self):
        with self.assertRaisesRegex(ValueError, 'Item name cannot be empty.'):
            self.calc.add_item('', 1.0, 1)

    def test_15_add_item_name_not_string(self):
        with self.assertRaisesRegex(TypeError, 'Item name must be a string.'):
            self.calc.add_item(123, 1.0, 1)

    def test_16_add_item_price_non_positive(self):
        with self.assertRaisesRegex(ValueError, 'Price must be greater than 0.'):
            self.calc.add_item('Pear', 0, 1)

    def test_17_add_item_price_not_numeric(self):
        with self.assertRaisesRegex(TypeError, 'Price must be a number.'):
            self.calc.add_item('Pear', 'free', 1)

    def test_18_add_item_quantity_less_than_one(self):
        with self.assertRaisesRegex(ValueError, 'Quantity must be at least 1.'):
            self.calc.add_item('Pear', 1.0, 0)

    def test_19_add_item_quantity_not_int(self):
        with self.assertRaisesRegex(TypeError, 'Quantity must be an integer.'):
            self.calc.add_item('Pear', 1.0, 2.5)

    def test_20_remove_item_success(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.items, [])

    def test_21_remove_item_nonexistent(self):
        with self.assertRaisesRegex(ValueError, "Item with name 'Orange' does not exist in the order."):
            self.calc.remove_item('Orange')

    def test_22_remove_item_name_not_string(self):
        with self.assertRaisesRegex(TypeError, 'Item name must be a string.'):
            self.calc.remove_item(42)

    def test_23_get_subtotal_normal(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 0.8, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5.9)

    def test_24_get_subtotal_empty(self):
        with self.assertRaisesRegex(ValueError, 'Cannot calculate subtotal on empty order.'):
            self.calc.get_subtotal()

    def test_25_apply_discount_typical(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 0.2), 80.0)

    def test_26_apply_discount_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(50, 0.0), 50.0)

    def test_27_apply_discount_full(self):
        self.assertAlmostEqual(self.calc.apply_discount(30, 1.0), 0.0)

    def test_28_apply_discount_negative(self):
        with self.assertRaisesRegex(ValueError, 'Discount must be between 0.0 and 1.0.'):
            self.calc.apply_discount(10, -0.1)

    def test_29_apply_discount_over_one(self):
        with self.assertRaisesRegex(ValueError, 'Discount must be between 0.0 and 1.0.'):
            self.calc.apply_discount(10, 1.5)

    def test_30_apply_discount_negative_subtotal(self):
        with self.assertRaisesRegex(ValueError, 'Cannot apply discount on negative subtotal.'):
            self.calc.apply_discount(-5, 0.1)

    def test_31_apply_discount_subtotal_not_numeric(self):
        with self.assertRaisesRegex(TypeError, 'Subtotal must be a number.'):
            self.calc.apply_discount('ten', 0.1)

    def test_32_apply_discount_discount_not_numeric(self):
        with self.assertRaisesRegex(TypeError, 'Discount must be a number.'):
            self.calc.apply_discount(100, 'half')

    def test_33_calculate_shipping_free(self):
        self.assertEqual(self.calc.calculate_shipping(150), 0.0)

    def test_34_calculate_shipping_charged(self):
        self.assertEqual(self.calc.calculate_shipping(80), 10.0)

    def test_35_calculate_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0, shipping_cost=5)
        self.assertEqual(calc.calculate_shipping(0), 0.0)

    def test_36_calculate_shipping_not_numeric(self):
        with self.assertRaisesRegex(TypeError, 'Discounted subtotal must be a number.'):
            self.calc.calculate_shipping('high')

    def test_37_calculate_tax_normal(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200), 46.0)

    def test_38_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0)
        self.assertAlmostEqual(calc.calculate_tax(123), 0.0)

    def test_39_calculate_tax_full_rate(self):
        calc = OrderCalculator(tax_rate=1)
        self.assertAlmostEqual(calc.calculate_tax(50), 50.0)

    def test_40_calculate_tax_negative_amount(self):
        with self.assertRaisesRegex(ValueError, 'Cannot calculate tax on negative amount.'):
            self.calc.calculate_tax(-10)

    def test_41_calculate_tax_not_numeric(self):
        with self.assertRaisesRegex(TypeError, 'Amount must be a number.'):
            self.calc.calculate_tax(None)

    def test_42_calculate_total_happy_path(self):
        self.calc.add_item('Apple', 1.5, 2)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 15.99, places=2)

    def test_43_calculate_total_discount_shipping_charged(self):
        self.calc.add_item('ItemA', 40, 2)
        total = self.calc.calculate_total(0.25)
        self.assertAlmostEqual(total, 86.1, places=2)

    def test_44_calculate_total_discount_below_threshold(self):
        self.calc.add_item('ItemA', 40, 3)
        total = self.calc.calculate_total(0.2)
        self.assertAlmostEqual(total, 130.38, places=2)

    def test_45_calculate_total_at_threshold(self):
        self.calc.add_item('ItemA', 50, 2)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 123.0, places=2)

    def test_46_calculate_total_full_discount(self):
        self.calc.add_item('Gadget', 10, 1)
        total = self.calc.calculate_total(1.0)
        expected = 10 * (1 + self.calc.tax_rate)
        self.assertAlmostEqual(total, expected, places=2)

    def test_47_calculate_total_empty_order(self):
        with self.assertRaisesRegex(ValueError, 'Cannot calculate subtotal on empty order.'):
            self.calc.calculate_total()

    def test_48_calculate_total_discount_not_numeric(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaisesRegex(TypeError, 'Discount must be a number.'):
            self.calc.calculate_total('half')

    def test_49_calculate_total_discount_out_of_range(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaisesRegex(ValueError, 'Discount must be between 0.0 and 1.0.'):
            self.calc.calculate_total(1.5)

    def test_50_calculate_total_discount_negative(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaisesRegex(ValueError, 'Discount must be between 0.0 and 1.0.'):
            self.calc.calculate_total(-0.2)

    def test_51_total_items_aggregation(self):
        self.calc.add_item('Apple', 1, 2)
        self.calc.add_item('Apple', 1, 3)
        self.calc.add_item('Banana', 1, 1)
        self.assertEqual(self.calc.total_items(), 6)

    def test_52_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_53_list_items_unique(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.add_item('Apple', 1, 2)
        self.calc.add_item('Banana', 0.5, 1)
        self.assertCountEqual(self.calc.list_items(), ['Apple', 'Banana'])

    def test_54_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_55_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_56_is_empty_after_add(self):
        self.calc.add_item('Apple', 1, 1)
        self.assertFalse(self.calc.is_empty())

    def test_57_is_empty_after_clear(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_58_clear_order_normal(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.add_item('Banana', 1, 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.items, [])

    def test_59_clear_order_idempotent(self):
        self.calc.clear_order()
        self.assertEqual(self.calc.items, [])

    def test_60_add_remove_is_empty(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_61_clear_after_multiple_adds(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.add_item('Banana', 1, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_62_calculate_total_custom_config(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50, shipping_cost=5)
        calc.add_item('Item', 30, 2)
        total = calc.calculate_total()
        expected = 60 + 0 + 60 * 0.05
        self.assertAlmostEqual(total, expected, places=2)

    def test_63_calculate_total_rounding(self):
        self.calc.add_item('Item', 0.3333, 3)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 0.9999 + 10 + (0.9999 + 10) * 0.23, places=4)

    def test_64_apply_discount_integer_inputs(self):
        self.assertEqual(self.calc.apply_discount(100, 0), 100)
        self.assertEqual(self.calc.apply_discount(100, 1), 0)

    def test_65_calculate_shipping_integer_input(self):
        self.assertEqual(self.calc.calculate_shipping(80), 10)

    def test_66_calculate_tax_integer_input(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200), 46.0)

    def test_67_add_item_price_as_int(self):
        self.calc.add_item('Gadget', 5, 2)
        self.assertEqual(self.calc.items[0]['price'], 5)

    def test_68_add_item_large_quantity(self):
        self.calc.add_item('Bulk', 0.01, 10000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 100.0)

    def test_69_calculate_total_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0)
        calc.add_item('Item', 20, 1)
        total = calc.calculate_total()
        expected = 20 + 0 + 20 * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_70_calculate_total_always_charged_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=1000000, shipping_cost=7)
        calc.add_item('Item', 50, 1)
        total = calc.calculate_total()
        expected = 50 + 7 + (50 + 7) * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_71_remove_item_after_merge(self):
        self.calc.add_item('Apple', 1, 2)
        self.calc.add_item('Apple', 1, 3)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.items, [])

    def test_72_list_items_after_removal(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.add_item('Banana', 1, 1)
        self.calc.remove_item('Apple')
        self.assertCountEqual(self.calc.list_items(), ['Banana'])

    def test_73_total_items_after_removal(self):
        self.calc.add_item('Apple', 1, 3)
        self.calc.add_item('Banana', 1, 2)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.total_items(), 2)

    def test_74_calculate_total_discount_to_threshold(self):
        self.calc.add_item('Item', 125, 1)
        total = self.calc.calculate_total(0.2)
        expected = 100 + 0 + 100 * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_75_calculate_total_discount_just_below_threshold(self):
        self.calc.add_item('Item', 125, 1)
        total = self.calc.calculate_total(0.199)
        discounted = 125 * (1 - 0.199)
        expected = discounted + 10 + (discounted + 10) * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_76_apply_discount_rounding_issue(self):
        result = self.calc.apply_discount(0.1, 0.3333333333)
        expected = 0.1 * (1 - 0.3333333333)
        self.assertAlmostEqual(result, expected, places=9)

    def test_77_calculate_tax_large_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(1000000000000.0), 1000000000000.0 * 0.23)

    def test_78_add_item_long_name(self):
        long_name = 'x' * 10000
        self.calc.add_item(long_name, 1.0, 1)
        self.assertEqual(self.calc.items[0]['name'], long_name)

    def test_79_add_item_whitespace_name(self):
        self.calc.add_item('   ', 1.0, 1)
        self.assertEqual(self.calc.items[0]['name'], '   ')

    def test_80_remove_item_case_sensitivity(self):
        self.calc.add_item('Apple', 1, 1)
        with self.assertRaisesRegex(ValueError, "Item with name 'apple' does not exist in the order."):
            self.calc.remove_item('apple')