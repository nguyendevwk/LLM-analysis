import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_01_default_init(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertEqual(oc.items, [])

    def test_02_custom_valid_init(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=5)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0)
        self.assertEqual(oc.shipping_cost, 5)

    def test_03_invalid_tax_type(self):
        with self.assertRaisesRegex(TypeError, 'Tax rate must be a float or int.'):
            OrderCalculator(tax_rate='0.23')

    def test_04_invalid_tax_range_low(self):
        with self.assertRaisesRegex(ValueError, 'Tax rate must be between 0.0 and 1.0.'):
            OrderCalculator(tax_rate=-0.01)

    def test_05_invalid_tax_range_high(self):
        with self.assertRaisesRegex(ValueError, 'Tax rate must be between 0.0 and 1.0.'):
            OrderCalculator(tax_rate=1.01)

    def test_06_invalid_threshold_type(self):
        with self.assertRaisesRegex(TypeError, 'Free shipping threshold must be a float or int.'):
            OrderCalculator(free_shipping_threshold='100')

    def test_07_negative_threshold(self):
        with self.assertRaisesRegex(ValueError, 'Free shipping threshold cannot be negative.'):
            OrderCalculator(free_shipping_threshold=-5)

    def test_08_invalid_shipping_cost_type(self):
        with self.assertRaisesRegex(TypeError, 'Shipping cost must be a float or int.'):
            OrderCalculator(shipping_cost=None)

    def test_09_negative_shipping_cost(self):
        with self.assertRaisesRegex(ValueError, 'Shipping cost cannot be negative.'):
            OrderCalculator(shipping_cost=-1)

    def test_10_add_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['name'], 'Apple')
        self.assertEqual(oc.items[0]['price'], 1.5)
        self.assertEqual(oc.items[0]['quantity'], 2)
        self.assertEqual(oc.total_items(), 2)

    def test_11_add_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8)
        self.assertEqual(oc.items[0]['quantity'], 1)

    def test_12_add_same_name_price_increments_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['quantity'], 5)

    def test_13_add_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5)
        with self.assertRaisesRegex(ValueError, 'Item with the same name but different price already exists.'):
            oc.add_item('Apple', 2.0)

    def test_14_invalid_name_type(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Item name must be a string.'):
            oc.add_item(123, 1.0)

    def test_15_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Item name cannot be empty.'):
            oc.add_item('', 1.0)

    def test_16_invalid_price_type(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Price must be a number.'):
            oc.add_item('Apple', '1.5')

    def test_17_nonpositive_price_zero(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Price must be greater than 0.'):
            oc.add_item('Apple', 0)

    def test_18_nonpositive_price_negative(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Price must be greater than 0.'):
            oc.add_item('Apple', -2)

    def test_19_invalid_quantity_type(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Quantity must be an integer.'):
            oc.add_item('Apple', 1.5, 2.5)

    def test_20_quantity_less_than_one(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Quantity must be at least 1.'):
            oc.add_item('Apple', 1.5, 0)

    def test_21_remove_existing_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 2.0, 3)
        oc.remove_item('Apple')
        self.assertFalse(any((i['name'] == 'Apple' for i in oc.items)))
        self.assertEqual(oc.total_items(), 3)

    def test_22_invalid_name_type_remove(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Item name must be a string.'):
            oc.remove_item(123)

    def test_23_remove_nonexistent_item(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, "Item with name 'Banana' does not exist in the order."):
            oc.remove_item('Banana')

    def test_24_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 3)
        oc.add_item('Banana', 1.0, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 8.0)

    def test_25_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 5.0)
        self.assertAlmostEqual(oc.get_subtotal(), 5.0)

    def test_26_subtotal_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Cannot calculate subtotal on empty order.'):
            oc.get_subtotal()

    def test_27_apply_valid_discount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0.2), 80.0)

    def test_28_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50, 0.0), 50.0)

    def test_29_discount_one_hundred_percent(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(30, 1.0), 0.0)

    def test_30_discount_out_of_range_low(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Discount must be between 0.0 and 1.0.'):
            oc.apply_discount(100, -0.01)

    def test_31_discount_out_of_range_high(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Discount must be between 0.0 and 1.0.'):
            oc.apply_discount(100, 1.01)

    def test_32_invalid_subtotal_type(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Subtotal must be a number.'):
            oc.apply_discount('100', 0.1)

    def test_33_invalid_discount_type(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Discount must be a number.'):
            oc.apply_discount(100, None)

    def test_34_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Cannot apply discount on negative subtotal.'):
            oc.apply_discount(-10, 0.1)

    def test_35_shipping_free_when_above_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(150), 0.0)

    def test_36_shipping_free_when_exactly_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(100.0), 0.0)

    def test_37_shipping_charged_when_below_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(99.99), 10.0)

    def test_38_custom_shipping_cost(self):
        oc = OrderCalculator(shipping_cost=7.5)
        self.assertEqual(oc.calculate_shipping(50), 7.5)

    def test_39_invalid_type_shipping(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Discounted subtotal must be a number.'):
            oc.calculate_shipping('50')

    def test_40_negative_subtotal_shipping(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(-5), 10.0)

    def test_41_tax_normal_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(100), 23.0)

    def test_42_tax_zero_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0), 0.0)

    def test_43_tax_custom_rate_zero(self):
        oc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(oc.calculate_tax(50), 0.0)

    def test_44_tax_custom_rate_one(self):
        oc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(oc.calculate_tax(42), 42.0)

    def test_45_invalid_amount_type_tax(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Amount must be a number.'):
            oc.calculate_tax([100])

    def test_46_negative_amount_tax(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Cannot calculate tax on negative amount.'):
            oc.calculate_tax(-1)

    def test_47_total_no_discount_no_shipping(self):
        oc = OrderCalculator()
        oc.add_item('A', 40, 1)
        oc.add_item('B', 30, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 98.4)

    def test_48_total_no_discount_free_shipping(self):
        oc = OrderCalculator()
        oc.add_item('A', 60, 1)
        oc.add_item('B', 50, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 135.3)

    def test_49_total_with_discount_shipping_charged(self):
        oc = OrderCalculator()
        oc.add_item('A', 60, 1)
        oc.add_item('B', 50, 1)
        total = oc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 120.54)

    def test_50_total_with_discount_and_free_shipping(self):
        oc = OrderCalculator()
        oc.add_item('A', 70, 1)
        oc.add_item('B', 50, 1)
        total = oc.calculate_total(discount=0.25)
        self.assertAlmostEqual(total, 123.0)

    def test_51_total_discount_boundary_zero(self):
        oc = OrderCalculator()
        oc.add_item('A', 40, 1)
        oc.add_item('B', 30, 1)
        total = oc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 98.4)

    def test_52_total_discount_boundary_one(self):
        oc = OrderCalculator()
        oc.add_item('A', 40, 1)
        total = oc.calculate_total(discount=1.0)
        expected = oc.shipping_cost + oc.shipping_cost * oc.tax_rate
        self.assertAlmostEqual(total, expected)

    def test_53_total_invalid_discount_type(self):
        oc = OrderCalculator()
        oc.add_item('A', 10, 1)
        with self.assertRaisesRegex(TypeError, 'Discount must be a number.'):
            oc.calculate_total(discount='0.1')

    def test_54_total_invalid_discount_range_low(self):
        oc = OrderCalculator()
        oc.add_item('A', 10, 1)
        with self.assertRaisesRegex(ValueError, 'Discount must be between 0.0 and 1.0.'):
            oc.calculate_total(discount=-0.1)

    def test_55_total_invalid_discount_range_high(self):
        oc = OrderCalculator()
        oc.add_item('A', 10, 1)
        with self.assertRaisesRegex(ValueError, 'Discount must be between 0.0 and 1.0.'):
            oc.calculate_total(discount=1.5)

    def test_56_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Cannot calculate subtotal on empty order.'):
            oc.calculate_total()

    def test_57_total_items_after_additions(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 2)
        oc.add_item('B', 1, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_58_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 2)
        oc.add_item('B', 1, 3)
        oc.remove_item('A')
        self.assertEqual(oc.total_items(), 3)

    def test_59_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_60_clear_order_resets_state(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 2)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.items, [])
        self.assertEqual(oc.total_items(), 0)

    def test_61_list_items_unique_names(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Apple', 1, 3)
        oc.add_item('Banana', 2, 1)
        names = oc.list_items()
        self.assertCountEqual(names, ['Apple', 'Banana'])

    def test_62_list_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Banana', 2, 1)
        oc.remove_item('Apple')
        self.assertCountEqual(oc.list_items(), ['Banana'])

    def test_63_list_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_64_is_empty_initial(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_65_is_empty_after_add(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 1)
        self.assertFalse(oc.is_empty())

    def test_66_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_67_interaction_add_remove_total(self):
        oc = OrderCalculator()
        oc.add_item('A', 10, 2)
        oc.add_item('B', 5, 1)
        oc.remove_item('A')
        total = oc.calculate_total()
        expected = 5 + oc.shipping_cost + (5 + oc.shipping_cost) * oc.tax_rate
        self.assertAlmostEqual(total, expected)

    def test_68_interaction_clear_subtotal_error(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 1)
        oc.clear_order()
        with self.assertRaisesRegex(ValueError, 'Cannot calculate subtotal on empty order.'):
            oc.get_subtotal()

    def test_69_boundary_tax_rate_one(self):
        oc = OrderCalculator(tax_rate=1.0)
        oc.add_item('A', 10, 1)
        total = oc.calculate_total()
        expected = 10 + oc.shipping_cost + (10 + oc.shipping_cost) * 1.0
        self.assertAlmostEqual(total, expected)

    def test_70_boundary_tax_rate_zero(self):
        oc = OrderCalculator(tax_rate=0.0)
        oc.add_item('A', 10, 1)
        total = oc.calculate_total()
        expected = 10 + oc.shipping_cost
        self.assertAlmostEqual(total, expected)

    def test_71_boundary_free_shipping_threshold_zero(self):
        oc = OrderCalculator(free_shipping_threshold=0)
        oc.add_item('A', 20, 1)
        total = oc.calculate_total()
        expected = 20 + 20 * oc.tax_rate
        self.assertAlmostEqual(total, expected)

    def test_73_boundary_shipping_cost_zero(self):
        oc = OrderCalculator(shipping_cost=0)
        oc.add_item('A', 30, 1)
        total = oc.calculate_total()
        expected = 30 + 30 * oc.tax_rate
        self.assertAlmostEqual(total, expected)

    def test_74_edge_large_quantities_prices(self):
        oc = OrderCalculator()
        oc.add_item('Expensive', 1000000, 1000)
        self.assertAlmostEqual(oc.get_subtotal(), 1000000000)
        total = oc.calculate_total()
        discounted = 1000000000
        shipping = 0 if discounted >= oc.free_shipping_threshold else oc.shipping_cost
        tax = (discounted + shipping) * oc.tax_rate
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_75_edge_floating_point_rounding(self):
        oc = OrderCalculator()
        oc.add_item('Tiny', 0.1, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 0.3)
        total = oc.calculate_total()
        discounted = 0.3
        shipping = oc.shipping_cost if discounted < oc.free_shipping_threshold else 0
        tax = (discounted + shipping) * oc.tax_rate
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_76_edge_duplicate_names_same_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('Apple', 1.0, 1)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['quantity'], 2)

    def test_77_edge_list_items_returns_new_list(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        names = oc.list_items()
        names.append('X')
        self.assertNotIn('X', oc.list_items())

    def test_78_edge_remove_item_all(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Apple', 1, 3)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_79_edge_add_item_integer_price(self):
        oc = OrderCalculator()
        oc.add_item('Gadget', 5, 2)
        self.assertEqual(oc.items[0]['price'], 5)

    def test_80_edge_apply_discount_integer_discount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 1), 0.0)

    def test_81_edge_calculate_shipping_integer_subtotal(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(100), 0.0)

    def test_82_edge_calculate_tax_integer_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(50), 11.5)

    def test_84_edge_remove_item_twice(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.remove_item('Apple')
        with self.assertRaisesRegex(ValueError, "Item with name 'Apple' does not exist in the order."):
            oc.remove_item('Apple')

    def test_85_edge_add_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.clear_order()
        oc.add_item('Banana', 2, 2)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['name'], 'Banana')

    def test_86_edge_case_sensitive_names(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1, 1)
        oc.add_item('Apple', 1, 1)
        self.assertCountEqual(oc.list_items(), ['apple', 'Apple'])

    def test_87_edge_is_empty_after_removing_last(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_88_edge_total_items_after_removing_all(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 3)
        oc.remove_item('Apple')
        self.assertEqual(oc.total_items(), 0)

    def test_89_edge_total_exact_threshold_after_discount(self):
        oc = OrderCalculator()
        oc.add_item('Item', 125, 1)
        total = oc.calculate_total(discount=0.2)
        discounted = 100.0
        shipping = 0.0
        tax = discounted * oc.tax_rate
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_90_edge_total_just_below_threshold_after_discount(self):
        oc = OrderCalculator()
        oc.add_item('Item', 124.999, 1)
        total = oc.calculate_total(discount=0.2)
        discounted = 124.999 * 0.8
        shipping = oc.shipping_cost
        tax = (discounted + shipping) * oc.tax_rate
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)