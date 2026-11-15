import unittest
from unittest.mock import patch
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def test_constructor_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertEqual(oc.items, [])

    def test_constructor_custom_valid(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0)
        self.assertEqual(oc.shipping_cost, 0)

    def test_constructor_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")

    def test_constructor_tax_rate_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_constructor_free_shipping_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=[])

    def test_constructor_free_shipping_threshold_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_constructor_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost={})

    def test_constructor_shipping_cost_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_add_item_first_valid(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]["quantity"], 2)
        self.assertEqual(oc.total_items(), 2)

    def test_add_item_same_name_same_price(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Apple", 1.5, 3)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]["quantity"], 5)

    def test_add_item_different_name(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Banana", 0.8, 1)
        self.assertEqual(len(oc.items), 2)
        self.assertCountEqual(oc.list_items(), ["Apple", "Banana"])

    def test_add_item_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 1)
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 2.0, 1)

    def test_add_item_name_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_name_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("", 1.0, 1)

    def test_add_item_price_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("Apple", [], 1)

    def test_add_item_price_non_positive(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 0, 1)
        with self.assertRaises(ValueError):
            oc.add_item("Apple", -5, 1)

    def test_add_item_quantity_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("Apple", 1.0, 2.5)

    def test_add_item_quantity_less_than_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 1.0, 0)

    def test_add_item_large_numbers(self):
        oc = OrderCalculator()
        oc.add_item("Gold", 1e6, 10000)
        self.assertEqual(oc.get_subtotal(), 1e6 * 10000)

    def test_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0)
        self.assertEqual(oc.items[0]["quantity"], 1)

    def test_add_item_price_int(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5, 2)
        self.assertEqual(oc.items[0]["price"], 5)

    def test_add_item_tax_rate_one(self):
        oc = OrderCalculator(tax_rate=1.0)
        oc.add_item("Apple", 1.0, 1)
        self.assertEqual(oc.items[0]["price"], 1.0)

    def test_remove_item_existing(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 1)
        oc.remove_item("Apple")
        self.assertTrue(oc.is_empty())

    def test_remove_item_multiple(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 1)
        oc.add_item("Banana", 1.0, 1)
        oc.remove_item("Apple")
        self.assertFalse(oc.is_empty())
        self.assertEqual(oc.list_items(), ["Banana"])

    def test_remove_item_nonexistent(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 1)
        with self.assertRaises(ValueError):
            oc.remove_item("Orange")

    def test_remove_item_name_type_error(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 1)
        with self.assertRaises(TypeError):
            oc.remove_item(None)

    def test_remove_item_after_merge(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 2)
        oc.add_item("Apple", 1.0, 3)
        oc.remove_item("Apple")
        self.assertTrue(oc.is_empty())

    def test_remove_item_last_remaining(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 1)
        oc.remove_item("Apple")
        self.assertTrue(oc.is_empty())

    def test_get_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Banana", 0.8, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 5.9)

    def test_get_subtotal_after_merge(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Apple", 1.5, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 1.5 * 5)

    def test_get_subtotal_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_get_subtotal_floating_precision(self):
        oc = OrderCalculator()
        oc.add_item("Item", 0.3333, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 0.9999, places=4)

    def test_get_subtotal_large_price(self):
        oc = OrderCalculator()
        oc.add_item("Item", 1e5, 2)
        self.assertEqual(oc.get_subtotal(), 200000)

    def test_apply_discount_no_discount(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(100, 0.0), 100)

    def test_apply_discount_twenty_percent(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(50, 0.2), 40)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(200, 1.0), 0)

    def test_apply_discount_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100, "0.1")

    def test_apply_discount_out_of_range(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, -0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(100, 1.5)

    def test_apply_discount_subtotal_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount({}, 0.1)

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10, 0.1)

    def test_apply_discount_subtotal_int(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(200, 0.1), 180)

    def test_apply_discount_discount_int(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(200, 0), 200)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(150), 0.0)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(100), 0.0)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping([])

    def test_calculate_shipping_custom_cost(self):
        oc = OrderCalculator(shipping_cost=5)
        self.assertEqual(oc.calculate_shipping(50), 5)

    def test_calculate_shipping_always_free(self):
        oc = OrderCalculator(free_shipping_threshold=0)
        self.assertEqual(oc.calculate_shipping(0), 0.0)
        self.assertEqual(oc.calculate_shipping(10), 0.0)

    def test_calculate_shipping_high_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=1000, shipping_cost=7)
        self.assertEqual(oc.calculate_shipping(200), 7)

    def test_calculate_shipping_decimal_comparison(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(99.999999), 10.0)

    def test_calculate_tax_zero_amount(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_tax(0), 0)

    def test_calculate_tax_positive_default_rate(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(