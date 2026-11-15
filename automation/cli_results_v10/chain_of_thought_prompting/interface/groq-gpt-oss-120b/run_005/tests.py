import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.tax_rate, 0.23)
        self.assertAlmostEqual(oc.free_shipping_threshold, 100.0)
        self.assertAlmostEqual(oc.shipping_cost, 10.0)

    def test_init_custom_values(self):
        oc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(oc.tax_rate, 0.05)
        self.assertAlmostEqual(oc.free_shipping_threshold, 50.0)
        self.assertAlmostEqual(oc.shipping_cost, 5.0)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_greater_than_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_non_numeric_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='high')

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_single_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.2)
        self.assertListEqual(oc.list_items(), ['Apple'])
        self.assertEqual(oc.total_items(), 1)
        self.assertAlmostEqual(oc.get_subtotal(), 1.2)

    def test_add_item_quantity_greater_than_one(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.5, quantity=4)
        self.assertListEqual(oc.list_items(), ['Banana'])
        self.assertEqual(oc.total_items(), 4)
        self.assertAlmostEqual(oc.get_subtotal(), 2.0)

    def test_add_item_same_name_aggregates_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Milk', 1.0, quantity=1)
        oc.add_item('Milk', 1.0, quantity=2)
        self.assertListEqual(oc.list_items(), ['Milk'])
        self.assertEqual(oc.total_items(), 3)
        self.assertAlmostEqual(oc.get_subtotal(), 3.0)

    def test_add_item_same_name_different_price_updates_price(self):
        oc = OrderCalculator()
        oc.add_item('Bread', 2.0, quantity=1)
        oc.add_item('Bread', 2.5, quantity=1)
        self.assertListEqual(oc.list_items(), ['Bread'])
        self.assertEqual(oc.total_items(), 2)
        self.assertAlmostEqual(oc.get_subtotal(), 5.0)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0)

    def test_add_item_non_string_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0)

    def test_add_item_negative_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Eggs', -0.99)

    def test_add_item_zero_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Eggs', 0.0)

    def test_add_item_non_numeric_price(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Eggs', 'free')

    def test_add_item_negative_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Cheese', 2.5, quantity=-3)

    def test_add_item_zero_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Cheese', 2.5, quantity=0)

    def test_add_item_non_int_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Cheese', 2.5, quantity=1.5)

    def test_remove_item_existing(self):
        oc = OrderCalculator()
        oc.add_item('Yogurt', 1.0)
        oc.remove_item('Yogurt')
        self.assertTrue(oc.is_empty())
        self.assertListEqual(oc.list_items(), [])
        self.assertAlmostEqual(oc.get_subtotal(), 0.0)

    def test_remove_item_one_of_several(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0)
        oc.add_item('B', 2.0)
        oc.remove_item('A')
        self.assertFalse(oc.is_empty())
        self.assertListEqual(oc.list_items(), ['B'])
        self.assertEqual(oc.total_items(), 1)
        self.assertAlmostEqual(oc.get_subtotal(), 2.0)

    def test_remove_item_nonexistent_raises(self):
        oc = OrderCalculator()
        with self.assertRaises(KeyError):
            oc.remove_item('Nonexistent')

    def test_remove_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('')

    def test_remove_item_non_string_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(42)

    def test_get_subtotal_empty_order(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.get_subtotal(), 0.0)

    def test_get_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('A', 3.0, quantity=2)
        oc.add_item('B', 5.0, quantity=1)
        self.assertAlmostEqual(oc.get_subtotal(), 11.0)

    def test_get_subtotal_floating_point_rounding(self):
        oc = OrderCalculator()
        oc.add_item('C', 0.1, quantity=3)
        self.assertAlmostEqual(oc.get_subtotal(), 0.3, places=7)

    def test_apply_discount_normal(self):
        oc = OrderCalculator()
        result = oc.apply_discount(100.0, 15.0)
        self.assertAlmostEqual(result, 85.0)

    def test_apply_discount_equal_to_subtotal(self):
        oc = OrderCalculator()
        result = oc.apply_discount(20.0, 20.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_greater_than_subtotal(self):
        oc = OrderCalculator()
        result = oc.apply_discount(30.0, 50.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(50.0, -5.0)

    def test_apply_discount_non_numeric_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('fifty', 5.0)

    def test_apply_discount_non_numeric_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(50.0, 'five')

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        cost = oc.calculate_shipping(80.0)
        self.assertAlmostEqual(cost, oc.shipping_cost)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        cost = oc.calculate_shipping(100.0)
        self.assertAlmostEqual(cost, 0.0)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        cost = oc.calculate_shipping(150.0)
        self.assertAlmostEqual(cost, 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        oc = OrderCalculator()
        cost = oc.calculate_shipping(-20.0)
        self.assertAlmostEqual(cost, oc.shipping_cost)

    def test_calculate_shipping_non_numeric_input(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('twenty')

    def test_calculate_tax_positive_amount(self):
        oc = OrderCalculator()
        tax = oc.calculate_tax(200.0)
        self.assertAlmostEqual(tax, 200.0 * oc.tax_rate)

    def test_calculate_tax_zero_amount(self):
        oc = OrderCalculator()
        tax = oc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative_amount(self):
        oc = OrderCalculator()
        tax = oc.calculate_tax(-50.0)
        self.assertAlmostEqual(tax, -50.0 * oc.tax_rate)

    def test_calculate_tax_non_numeric_input(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax([1, 2])

    def test_calculate_total_no_discount_below_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item1', 40.0)
        oc.add_item('Item2', 40.0)
        total = oc.calculate_total()
        expected = 80.0 + oc.shipping_cost + oc.calculate_tax(80.0)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_no_discount_above_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item1', 70.0)
        oc.add_item('Item2', 60.0)
        total = oc.calculate_total()
        expected = 130.0 + oc.calculate_tax(130.0)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_keeps_below_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 90.0)
        total = oc.calculate_total(discount=10.0)
        discounted = 80.0
        expected = discounted + oc.shipping_cost + oc.calculate_tax(discounted + oc.shipping_cost)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_exceeds_subtotal(self):
        oc = OrderCalculator()
        oc.add_item('Item', 30.0)
        total = oc.calculate_total(discount=50.0)
        discounted = 0.0
        expected = discounted + oc.shipping_cost + oc.calculate_tax(oc.shipping_cost)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_empty_order_no_discount(self):
        oc = OrderCalculator()
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 0.0)

    def test_calculate_total_empty_order_with_discount(self):
        oc = OrderCalculator()
        total = oc.calculate_total(discount=10.0)
        self.assertAlmostEqual(total, 0.0)

    def test_calculate_total_complex_scenario(self):
        oc = OrderCalculator()
        oc.add_item('A', 30.0, quantity=2)
        oc.add_item('B', 25.0, quantity=1)
        total = oc.calculate_total(discount=15.0)
        discounted = 85.0 - 15.0
        shipping = oc.shipping_cost
        tax = oc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_total_items_multiple_adds(self):
        oc = OrderCalculator()
        oc.add_item('X', 1.0, quantity=3)
        oc.add_item('Y', 2.0, quantity=2)
        self.assertEqual(oc.total_items(), 5)

    def test_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0, quantity=2)
        oc.add_item('B', 1.0, quantity=3)
        oc.remove_item('A')
        self.assertEqual(oc.total_items(), 3)

    def test_total_items_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0, quantity=2)
        oc.clear_order()
        self.assertEqual(oc.total_items(), 0)

    def test_clear_order_clears_populated_cart(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0)
        oc.add_item('B', 2.0)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertListEqual(oc.list_items(), [])
        self.assertAlmostEqual(oc.get_subtotal(), 0.0)
        self.assertEqual(oc.total_items(), 0)

    def test_clear_order_on_already_empty_cart(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertListEqual(oc.list_items(), [])
        self.assertAlmostEqual(oc.get_subtotal(), 0.0)

    def test_list_items_after_several_adds(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0)
        oc.add_item('B', 2.0)
        oc.add_item('C', 3.0)
        self.assertCountEqual(oc.list_items(), ['A', 'B', 'C'])

    def test_list_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0)
        oc.add_item('B', 2.0)
        oc.remove_item('A')
        self.assertListEqual(oc.list_items(), ['B'])

    def test_list_items_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0)
        oc.clear_order()
        self.assertListEqual(oc.list_items(), [])

    def test_is_empty_new_instance(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_adding_item(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_removing_only_item(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0)
        oc.remove_item('A')
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_failed_removal(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0)
        with self.assertRaises(KeyError):
            oc.remove_item('Nonexistent')
        self.assertFalse(oc.is_empty())

    def test_invalid_none_name_add_item(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(None, 1.0)

    def test_invalid_none_name_remove_item(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(None)

    def test_precision_multiple_decimal_places(self):
        oc = OrderCalculator()
        oc.add_item('D', 0.3333)
        oc.add_item('E', 0.6667)
        total = oc.calculate_total()
        expected_subtotal = 0.3333 + 0.6667
        discounted = expected_subtotal
        shipping = oc.shipping_cost if discounted < oc.free_shipping_threshold else 0.0
        tax = oc.calculate_tax(discounted + shipping)
        expected_total = discounted + shipping + tax
        self.assertAlmostEqual(total, expected_total, places=6)

    def test_shipping_boundary_just_below_threshold(self):
        oc = OrderCalculator()
        subtotal = oc.free_shipping_threshold - 0.01
        cost = oc.calculate_shipping(subtotal)
        self.assertAlmostEqual(cost, oc.shipping_cost)

    def test_shipping_boundary_just_above_threshold(self):
        oc = OrderCalculator()
        subtotal = oc.free_shipping_threshold + 0.01
        cost = oc.calculate_shipping(subtotal)
        self.assertAlmostEqual(cost, 0.0)

    def test_large_quantity_and_price(self):
        oc = OrderCalculator()
        oc.add_item('Expensive', 999.99, quantity=10000)
        self.assertEqual(oc.total_items(), 10000)
        self.assertAlmostEqual(oc.get_subtotal(), 999.99 * 10000)

    def test_repeated_clear_and_reuse(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0)
        oc.clear_order()
        oc.add_item('B', 2.0)
        self.assertFalse(oc.is_empty())
        self.assertListEqual(oc.list_items(), ['B'])
        self.assertEqual(oc.total_items(), 1)
        self.assertAlmostEqual(oc.get_subtotal(), 2.0)