import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_01_init_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertEqual(oc.items, [])

    def test_02_init_custom_values(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0)
        self.assertEqual(oc.shipping_cost, 0)

    def test_03_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_04_init_tax_rate_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_05_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_06_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_07_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=[100])

    def test_08_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_09_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost={'c': 10})

    def test_10_add_item_successful(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0], {'name': 'Apple', 'price': 1.5, 'quantity': 2})
        self.assertEqual(oc.total_items(), 2)

    def test_11_add_item_merges_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['quantity'], 5)

    def test_12_add_item_different_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.add_item('Banana', 0.8, 1)
        self.assertEqual(len(oc.items), 2)
        names = {i['name'] for i in oc.items}
        self.assertSetEqual(names, {'Apple', 'Banana'})

    def test_13_add_item_name_not_string(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_14_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_15_add_item_price_not_number(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', 'free', 1)

    def test_16_add_item_price_non_positive(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', -5, 1)

    def test_17_add_item_quantity_not_int(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', 1.0, 2.5)

    def test_18_add_item_quantity_less_than_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 1.0, 0)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 1.0, -1)

    def test_19_add_item_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0, 1)

    def test_20_add_item_very_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Gadget', 10.0, 10000)
        self.assertEqual(oc.total_items(), 10000)

    def test_21_add_item_high_precision_price(self):
        oc = OrderCalculator()
        oc.add_item('Widget', 0.3333333, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 0.3333333 * 3)

    def test_22_remove_existing_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_23_remove_one_of_many(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.add_item('Banana', 0.8, 1)
        oc.remove_item('Apple')
        self.assertFalse(oc.is_empty())
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['name'], 'Banana')

    def test_24_remove_last_item_becomes_empty(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_25_remove_item_name_not_string(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(None)

    def test_26_remove_item_nonexistent(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Nonexistent')

    def test_27_get_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 3)
        oc.add_item('Banana', 1.0, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 8.0)

    def test_28_get_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.5, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 2.5)

    def test_29_get_subtotal_floating_point(self):
        oc = OrderCalculator()
        oc.add_item('Item', 0.1, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 0.30000000000000004)

    def test_30_get_subtotal_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_31_apply_discount_twenty_percent(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0.2), 80.0)

    def test_32_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50, 0.0), 50.0)

    def test_33_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50, 1.0), 0.0)

    def test_34_apply_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(50, -0.1)

    def test_35_apply_discount_over_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(50, 1.5)

    def test_36_apply_discount_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(50, 'half')

    def test_37_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-5, 0.1)

    def test_38_apply_discount_subtotal_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount([100], 0.1)

    def test_39_apply_discount_large_subtotal(self):
        oc = OrderCalculator()
        result = oc.apply_discount(1000000000.0, 0.05)
        self.assertAlmostEqual(result, 950000000.0)

    def test_40_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(150), 0.0)

    def test_41_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(100), 0.0)

    def test_42_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(99.99), 10.0)

    def test_43_calculate_shipping_custom_parameters(self):
        oc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5.5)
        self.assertEqual(oc.calculate_shipping(30), 5.5)

    def test_44_calculate_shipping_non_numeric(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping(None)

    def test_45_calculate_shipping_negative_subtotal(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(-10), 10.0)

    def test_46_calculate_tax_default_rate(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(200), 46.0)

    def test_47_calculate_tax_zero_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0), 0.0)

    def test_48_calculate_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-1)

    def test_49_calculate_tax_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax('100')

    def test_50_calculate_tax_custom_rates(self):
        oc_zero = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(oc_zero.calculate_tax(123), 0.0)
        oc_full = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(oc_full.calculate_tax(123), 123.0)

    def test_51_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_52_calculate_total_no_discount_below_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 40, 2)
        subtotal = oc.get_subtotal()
        discounted = oc.apply_discount(subtotal, 0.0)
        shipping = oc.calculate_shipping(discounted)
        tax = oc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(oc.calculate_total(), expected)

    def test_53_calculate_total_no_discount_above_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 60, 2)
        subtotal = oc.get_subtotal()
        discounted = oc.apply_discount(subtotal, 0.0)
        shipping = oc.calculate_shipping(discounted)
        tax = oc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(oc.calculate_total(), expected)

    def test_54_calculate_total_partial_discount(self):
        oc = OrderCalculator()
        oc.add_item('Item', 50, 2)
        total = oc.calculate_total(0.15)
        discounted = 100 * 0.85
        shipping = oc.calculate_shipping(discounted)
        tax = oc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_55_calculate_total_full_discount_shipping_applied(self):
        oc = OrderCalculator()
        oc.add_item('Item', 30, 2)
        total = oc.calculate_total(1.0)
        discounted = 0.0
        shipping = oc.calculate_shipping(discounted)
        tax = oc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_56_calculate_total_discount_not_numeric(self):
        oc = OrderCalculator()
        oc.add_item('Item', 10, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total('0.1')

    def test_57_calculate_total_discount_out_of_range(self):
        oc = OrderCalculator()
        oc.add_item('Item', 10, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(-0.2)
        with self.assertRaises(ValueError):
            oc.calculate_total(1.2)

    def test_58_calculate_total_custom_constructor(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=0)
        oc.add_item('Item', 100, 1)
        total = oc.calculate_total(0.2)
        self.assertAlmostEqual(total, 80.0)

    def test_59_calculate_total_tax_includes_shipping(self):
        oc = OrderCalculator()
        oc.add_item('Item', 40, 2)
        discounted = oc.apply_discount(80, 0.1)
        shipping = oc.calculate_shipping(discounted)
        tax_on_discounted = oc.calculate_tax(72)
        tax_on_discounted_plus_shipping = oc.calculate_tax(72 + 10)
        self.assertGreater(tax_on_discounted_plus_shipping, tax_on_discounted)
        total = oc.calculate_total(0.1)
        expected = discounted + shipping + tax_on_discounted_plus_shipping
        self.assertAlmostEqual(total, expected)

    def test_60_calculate_total_large_numbers(self):
        oc = OrderCalculator()
        oc.add_item('Item', 1000000000.0, 1)
        total = oc.calculate_total(0.5)
        subtotal = 1000000000.0
        discounted = subtotal * 0.5
        shipping = oc.calculate_shipping(discounted)
        tax = oc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_61_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_62_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 3)
        oc.add_item('Banana', 1, 2)
        self.assertEqual(oc.total_items(), 5)

    def test_63_total_items_merged_quantities(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Apple', 1, 4)
        self.assertEqual(oc.total_items(), 6)

    def test_64_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 3)
        oc.add_item('Banana', 1, 2)
        oc.remove_item('Apple')
        self.assertEqual(oc.total_items(), 2)

    def test_65_clear_order_non_empty(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)
        self.assertEqual(oc.items, [])

    def test_66_clear_order_already_empty(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.items, [])

    def test_67_list_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_68_list_items_distinct_names(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.add_item('Banana', 1, 1)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana'])

    def test_69_list_items_duplicate_adds(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.add_item('Apple', 1, 2)
        self.assertEqual(oc.list_items(), ['Apple'])

    def test_70_list_items_same_name_different_price_direct(self):
        oc = OrderCalculator()
        oc.items.append({'name': 'Apple', 'price': 1.0, 'quantity': 1})
        oc.items.append({'name': 'Apple', 'price': 2.0, 'quantity': 1})
        self.assertEqual(oc.list_items(), ['Apple'])

    def test_71_is_empty_fresh(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_72_is_empty_after_adding(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        self.assertFalse(oc.is_empty())

    def test_73_is_empty_after_removing_only_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_74_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_75_full_workflow(self):
        oc = OrderCalculator()
        oc.add_item('A', 10, 2)
        oc.add_item('B', 5, 4)
        oc.add_item('C', 2, 5)
        oc.remove_item('B')
        subtotal = oc.get_subtotal()
        discounted = oc.apply_discount(subtotal, 0.1)
        shipping = oc.calculate_shipping(discounted)
        tax = oc.calculate_tax(discounted + shipping)
        total = oc.calculate_total(0.1)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_76_custom_parameters_no_tax_free_shipping(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=0)
        oc.add_item('Item', 100, 1)
        total = oc.calculate_total(0.2)
        self.assertAlmostEqual(total, 80.0)

    def test_77_consistency_list_items_total_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 3)
        oc.add_item('Banana', 1, 2)
        oc.add_item('Apple', 1, 1)
        oc.remove_item('Banana')
        self.assertCountEqual(oc.list_items(), ['Apple'])
        self.assertEqual(oc.total_items(), 4)