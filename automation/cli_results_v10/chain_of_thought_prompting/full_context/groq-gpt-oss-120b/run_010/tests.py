import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_01_constructor_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    def test_02_constructor_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0)
        self.assertEqual(calc.shipping_cost, 0)

    def test_03_constructor_tax_rate_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_04_constructor_tax_rate_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_05_constructor_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1)

    def test_06_constructor_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_07_constructor_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_08_constructor_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_09_constructor_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    def test_10_add_item_first(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 2)
        self.assertEqual(self.calc.total_items(), 2)

    def test_11_add_item_merge_same_name_price(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Apple', 1.5, 3)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 5)

    def test_12_add_item_conflict_different_price(self):
        self.calc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.0, 1)

    def test_13_add_item_default_quantity(self):
        self.calc.add_item('Banana', 0.8)
        self.assertEqual(self.calc.items[0]['quantity'], 1)

    def test_14_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_15_add_item_price_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', 0, 1)

    def test_16_add_item_price_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', -5, 1)

    def test_17_add_item_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', 1.0, 0)

    def test_18_add_item_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', 1.0, -3)

    def test_19_add_item_name_not_string(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_20_add_item_price_not_number(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Item', 'free', 1)

    def test_21_add_item_quantity_not_int(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Item', 1.0, 2.5)

    def test_22_add_item_large_quantity(self):
        self.calc.add_item('Bulk', 0.01, 10 ** 6)
        self.assertEqual(self.calc.total_items(), 10 ** 6)

    def test_23_add_item_price_many_decimals(self):
        self.calc.add_item('Gadget', 0.3333333, 3)
        self.assertAlmostEqual(self.calc.items[0]['price'], 0.3333333)

    def test_24_remove_item_existing(self):
        self.calc.add_item('Apple', 1.5, 1)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_25_remove_item_among_multiple(self):
        self.calc.add_item('Apple', 1.5, 1)
        self.calc.add_item('Banana', 0.8, 2)
        self.calc.remove_item('Apple')
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.items[0]['name'], 'Banana')

    def test_26_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_27_remove_item_name_not_string(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_28_remove_item_from_empty(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Anything')

    def test_29_remove_item_after_merge(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Apple', 1.5, 3)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_30_get_subtotal_multiple_items(self):
        self.calc.add_item('Apple', 2.0, 3)
        self.calc.add_item('Banana', 1.5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 9.0)

    def test_31_get_subtotal_single_item(self):
        self.calc.add_item('Orange', 4.25)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.25)

    def test_32_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_33_get_subtotal_floating_point(self):
        self.calc.add_item('Item', 0.1, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.3, places=7)

    def test_34_get_subtotal_large(self):
        self.calc.add_item('Expensive', 1000000.0, 1000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1000000000.0)

    def test_35_apply_discount_zero_percent(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 0.0), 100)

    def test_36_apply_discount_full(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 1.0), 0.0)

    def test_37_apply_discount_typical(self):
        self.assertAlmostEqual(self.calc.apply_discount(200, 0.2), 160.0)

    def test_38_apply_discount_boundary_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(50, 0.0), 50)

    def test_39_apply_discount_boundary_one(self):
        self.assertAlmostEqual(self.calc.apply_discount(50, 1.0), 0.0)

    def test_40_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, -0.1)

    def test_41_apply_discount_over_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, 1.5)

    def test_42_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10, 0.1)

    def test_43_apply_discount_subtotal_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('10', 0.1)

    def test_44_apply_discount_discount_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(10, None)

    def test_45_apply_discount_subtotal_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(0, 0.5), 0.0)

    def test_46_apply_discount_large_subtotal(self):
        self.assertAlmostEqual(self.calc.apply_discount(1000000000.0, 0.25), 750000000.0)

    def test_47_calculate_shipping_free_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150), 0.0)

    def test_48_calculate_shipping_just_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(99.99), 10.0)

    def test_49_calculate_shipping_zero_subtotal(self):
        self.assertEqual(self.calc.calculate_shipping(0), 10.0)

    def test_50_calculate_shipping_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('abc')

    def test_51_calculate_shipping_custom_config_free(self):
        calc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(calc.calculate_shipping(55), 0.0)

    def test_52_calculate_shipping_custom_config_below(self):
        calc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(calc.calculate_shipping(45), 5)

    def test_53_calculate_shipping_custom_threshold_exact(self):
        calc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(calc.calculate_shipping(50), 0.0)

    def test_54_calculate_shipping_large_subtotal(self):
        self.assertEqual(self.calc.calculate_shipping(1000000000.0), 0.0)

    def test_55_calculate_tax_positive_default(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100), 23.0)

    def test_56_calculate_tax_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0), 0.0)

    def test_57_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5)

    def test_58_calculate_tax_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax([10])

    def test_59_calculate_tax_custom_rate(self):
        calc = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(calc.calculate_tax(200), 20.0)

    def test_60_calculate_tax_large_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(1000000000000.0), 230000000000.0)

    def test_61_calculate_tax_many_decimals(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.3333333), 0.076666659, places=7)

    def test_62_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_63_calculate_total_single_below_threshold_no_discount(self):
        self.calc.add_item('Item', 40, 1)
        subtotal = 40
        shipping = 10.0
        tax = (subtotal + shipping) * 0.23
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected, places=5)

    def test_64_calculate_total_single_above_threshold_no_discount(self):
        self.calc.add_item('Item', 120, 1)
        subtotal = 120
        shipping = 0.0
        tax = subtotal * 0.23
        expected = subtotal + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected, places=5)

    def test_65_calculate_total_multiple_discount_below_threshold(self):
        self.calc.add_item('A', 30, 2)
        self.calc.add_item('B', 20, 1)
        discounted = 80 * 0.8
        shipping = 10.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.2), expected, places=5)

    def test_66_calculate_total_multiple_discount_above_threshold(self):
        self.calc.add_item('A', 60, 2)
        discounted = 120 * 0.9
        shipping = 0.0
        tax = discounted * 0.23
        expected = discounted + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.1), expected, places=5)

    def test_67_calculate_total_full_discount(self):
        self.calc.add_item('Item', 80, 1)
        discounted = 0.0
        shipping = 10.0
        tax = 0.0
        expected = shipping
        self.assertAlmostEqual(self.calc.calculate_total(1.0), expected, places=5)

    def test_68_calculate_total_invalid_discount_negative(self):
        self.calc.add_item('Item', 50, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-0.1)

    def test_69_calculate_total_invalid_discount_over_one(self):
        self.calc.add_item('Item', 50, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.5)

    def test_70_calculate_total_discount_not_number(self):
        self.calc.add_item('Item', 50, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.1')

    def test_71_calculate_total_negative_subtotal_guard(self):
        self.calc.add_item('Item', 10, 1)
        original = self.calc.get_subtotal
        self.calc.get_subtotal = lambda: -5
        with self.assertRaises(ValueError):
            self.calc.calculate_total()
        self.calc.get_subtotal = original

    def test_72_calculate_total_custom_config(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50, shipping_cost=7)
        calc.add_item('X', 30, 2)
        discounted = 60 * 0.9
        tax = discounted * 0.05
        expected = discounted + tax
        self.assertAlmostEqual(calc.calculate_total(0.1), expected, places=5)

    def test_73_calculate_total_floating_point_precision(self):
        self.calc.add_item('A', 0.1, 3)
        self.calc.add_item('B', 0.2, 2)
        discounted = 0.7 * 0.85
        shipping = 10.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.15), expected, places=5)

    def test_74_calculate_total_large_order(self):
        for i in range(1000):
            self.calc.add_item(f'Item{i}', 1.0, 1)
        subtotal = 1000.0
        discounted = subtotal * 0.9
        shipping = 0.0
        tax = discounted * 0.23
        expected = discounted + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.1), expected, places=5)

    def test_75_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_76_total_items_after_adding(self):
        self.calc.add_item('A', 1, 3)
        self.calc.add_item('B', 2, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_77_total_items_after_removing(self):
        self.calc.add_item('A', 1, 3)
        self.calc.add_item('B', 2, 2)
        self.calc.remove_item('A')
        self.assertEqual(self.calc.total_items(), 2)

    def test_78_total_items_after_clearing(self):
        self.calc.add_item('A', 1, 5)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_79_total_items_large_quantities(self):
        self.calc.add_item('Bulk', 0.01, 10 ** 7)
        self.assertEqual(self.calc.total_items(), 10 ** 7)

    def test_80_clear_order_with_items(self):
        self.calc.add_item('A', 1, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(len(self.calc.items), 0)

    def test_81_clear_order_already_empty(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_82_clear_order_after_many_operations(self):
        for i in range(10):
            self.calc.add_item(f'Item{i}', i + 1, i + 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    def test_83_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_84_list_items_distinct_names(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.add_item('Banana', 2, 1)
        self.calc.add_item('Cherry', 3, 1)
        result = set(self.calc.list_items())
        self.assertEqual(result, {'Apple', 'Banana', 'Cherry'})

    def test_85_list_items_duplicate_names(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.add_item('Apple', 1, 2)
        self.assertEqual(self.calc.list_items(), ['Apple'])

    def test_86_list_items_return_is_copy(self):
        self.calc.add_item('Apple', 1, 1)
        lst = self.calc.list_items()
        lst.append('Fake')
        self.assertNotIn('Fake', self.calc.list_items())

    def test_87_list_items_large_number(self):
        names = [f'Item{i}' for i in range(500)]
        for n in names:
            self.calc.add_item(n, 1, 1)
        self.assertEqual(len(self.calc.list_items()), 500)

    def test_88_is_empty_fresh(self):
        self.assertTrue(self.calc.is_empty())

    def test_89_is_empty_after_adding(self):
        self.calc.add_item('A', 1, 1)
        self.assertFalse(self.calc.is_empty())

    def test_90_is_empty_after_clearing(self):
        self.calc.add_item('A', 1, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_91_is_empty_after_failed_remove(self):
        self.calc.add_item('A', 1, 1)
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')
        self.assertFalse(self.calc.is_empty())

    def test_92_full_typical_flow(self):
        self.calc.add_item('Apple', 2.0, 3)
        self.calc.add_item('Apple', 2.0, 2)
        self.calc.add_item('Banana', 1.5, 2)
        self.assertEqual(self.calc.total_items(), 7)
        self.assertEqual(set(self.calc.list_items()), {'Apple', 'Banana'})
        subtotal = self.calc.get_subtotal()
        self.assertAlmostEqual(subtotal, 2.0 * 5 + 1.5 * 2)
        total1 = self.calc.calculate_total(0.15)
        discounted = subtotal * 0.85
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total1, expected, places=5)
        self.calc.remove_item('Banana')
        subtotal2 = self.calc.get_subtotal()
        total2 = self.calc.calculate_total()
        discounted2 = subtotal2
        shipping2 = self.calc.calculate_shipping(discounted2)
        tax2 = self.calc.calculate_tax(discounted2 + shipping2)
        expected2 = discounted2 + shipping2 + tax2
        self.assertAlmostEqual(total2, expected2, places=5)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_93_full_custom_config_workflow(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=30, shipping_cost=4)
        calc.add_item('X', 15, 1)
        calc.add_item('Y', 20, 1)
        subtotal = calc.get_subtotal()
        self.assertEqual(subtotal, 35)
        total_no_discount = calc.calculate_total()
        expected_no_discount = subtotal + subtotal * 0.05
        self.assertAlmostEqual(total_no_discount, expected_no_discount, places=5)
        total_discount = calc.calculate_total(0.2)
        shipping = 4
        discounted = subtotal * 0.8
        tax = (discounted + shipping) * 0.05
        expected_discount = discounted + shipping + tax
        self.assertAlmostEqual(total_discount, expected_discount, places=5)

    def test_94_full_stress_workflow(self):
        for i in range(200):
            self.calc.add_item(f'Item{i}', i + 1, i + 1)
        self.assertEqual(len(self.calc.items), 200)
        for i in range(100):
            self.calc.remove_item(f'Item{i}')
        self.assertEqual(len(self.calc.items), 100)
        total = self.calc.calculate_total(0.1)
        self.assertIsInstance(total, float)

    def test_95_mutability_of_items_list(self):
        self.calc.add_item('A', 1, 1)
        self.calc.items.append({'name': 'B', 'price': 2, 'quantity': 2})
        self.assertTrue(any((item['name'] == 'B' for item in self.calc.items)))
        self.assertAlmostEqual(self.calc.get_subtotal(), 1 + 2 * 2)

    def test_96_type_safety_of_tax_rate_attribute(self):
        self.calc.tax_rate = 'invalid'
        with self.assertRaises(TypeError):
            self.calc.calculate_tax(10)

    def test_97_state_isolation_between_tests(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('A', 1, 1)
        self.assertFalse(self.calc.is_empty())
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())