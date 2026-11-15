import unittest
import types
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    # Constructor tests
    def test_constructor_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_constructor_custom_valid(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0.0)
        self.assertEqual(oc.shipping_cost, 0.0)

    def test_constructor_tax_upper_bound(self):
        oc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(oc.tax_rate, 1.0)

    def test_constructor_tax_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_constructor_tax_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_constructor_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_constructor_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_constructor_tax_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_constructor_free_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_constructor_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    # add_item tests
    def test_add_item_simple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(oc.total_items(), 2)

    def test_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8)
        self.assertEqual(oc.total_items(), 1)

    def test_add_item_merge_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_add_item_same_name_different_price_error(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0, 1)

    def test_add_item_empty_name_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_price_zero_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Orange', 0, 1)

    def test_add_item_price_negative_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Orange', -0.5, 1)

    def test_add_item_quantity_zero_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 1.2, 0)

    def test_add_item_quantity_negative_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 1.2, -3)

    def test_add_item_name_wrong_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_price_wrong_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Mango', '1.0', 1)

    def test_add_item_quantity_wrong_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Mango', 1.0, 1.5)

    def test_add_item_merge_list_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.list_items(), ['Apple'])

    def test_add_item_merge_total_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.total_items(), 5)

    # remove_item tests
    def test_remove_item_existing(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_remove_item_multiple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('Banana', 2.0, 1)
        oc.remove_item('Apple')
        self.assertFalse(oc.is_empty())
        self.assertEqual(oc.list_items(), ['Banana'])

    def test_remove_item_nonexistent_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Cherry')

    def test_remove_item_name_wrong_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_remove_item_last_item_is_empty(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    # get_subtotal tests
    def test_get_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 3)
        oc.add_item('Banana', 1.5, 2)
        self.assertEqual(oc.get_subtotal(), 9.0)

    def test_get_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Kiwi', 5.0)
        self.assertEqual(oc.get_subtotal(), 5.0)

    def test_get_subtotal_empty_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_get_subtotal_floating_precision(self):
        oc = OrderCalculator()
        oc.add_item('Item', 0.1, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 0.3, places=7)

    def test_get_subtotal_no_side_effect(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 1)
        first = oc.get_subtotal()
        second = oc.get_subtotal()
        self.assertEqual(first, second)

    # apply_discount tests
    def test_apply_discount_no_discount(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_twenty_percent(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(200.0, 0.2), 160.0)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_zero_subtotal(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_negative_subtotal_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 0.1)

    def test_apply_discount_discount_negative_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_over_one_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, 1.5)

    def test_apply_discount_subtotal_wrong_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)

    def test_apply_discount_discount_wrong_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100.0, '0.1')

    def test_apply_discount_floating_precision(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(99.99, 0.15), 84.9915, places=7)

    # calculate_shipping tests
    def test_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(90.0), 10.0)

    def test_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(100.0), 0.0)

    def test_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertEqual