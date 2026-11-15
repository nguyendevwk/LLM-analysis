import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    # 1. __init__
    def test_init_default(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)

    def test_init_custom(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(oc.tax_rate, 0.1)
        self.assertEqual(oc.free_shipping_threshold, 50.0)
        self.assertEqual(oc.shipping_cost, 5.0)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_non_numeric_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.1")

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_edge_tax_rate(self):
        oc_zero = OrderCalculator(tax_rate=0.0)
        self.assertEqual(oc_zero.tax_rate, 0.0)
        oc_one = OrderCalculator(tax_rate=1.0)
        self.assertEqual(oc_one.tax_rate, 1.0)

    # 2. add_item
    def test_add_single_item(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.5, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 3.0)
        self.assertEqual(oc.total_items(), 2)
        self.assertListEqual(oc.list_items(), ["apple"])

    def test_add_multiple_distinct_items(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 1)
        oc.add_item("banana", 2.0, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 5.0)
        self.assertEqual(oc.total_items(), 3)
        self.assertCountEqual(oc.list_items(), ["apple", "banana"])

    def test_add_same_name_same_price(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 1)
        oc.add_item("apple", 1.0, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 4.0)
        self.assertEqual(oc.total_items(), 4)
        self.assertListEqual(oc.list_items(), ["apple"])

    def test_add_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 1)
        oc.add_item("apple", 2.0, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 6.0)
        self.assertEqual(oc.total_items(), 3)
        self.assertListEqual(oc.list_items(), ["apple"])

    def test_add_zero_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("apple", 1.0, 0)

    def test_add_negative_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("apple", 1.0, -2)

    def test_add_non_int_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("apple", 1.0, 2.5)

    def test_add_negative_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("apple", -1.0, 1)

    def test_add_non_float_price(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("apple", "1.0", 1)

    def test_add_non_string_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_zero_price(self):
        oc = OrderCalculator()
        oc.add_item("freebie", 0.0, 5)
        self.assertAlmostEqual(oc.get_subtotal(), 0.0)
        self.assertEqual(oc.total_items(), 5)
        self.assertListEqual(oc.list_items(), ["freebie"])

    def test_add_large_price_quantity(self):
        oc = OrderCalculator()
        oc.add_item("expensive", 1e9, 1e6)
        self.assertAlmostEqual(oc.get_subtotal(), 1e15)
        self.assertEqual(oc.total_items(), int(1e6))
        self.assertListEqual(oc.list_items(), ["expensive"])

    # 3. remove_item
    def test_remove_existing_item(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 2)
        oc.remove_item("apple")
        self.assertAlmostEqual(oc.get_subtotal(), 0.0)
        self.assertEqual(oc.total_items(), 0)
        self.assertListEqual(oc.list_items(), [])

    def test_remove_item_multiple_times(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 3)
        oc.remove_item("apple")
        self.assertAlmostEqual(oc.get_subtotal(), 0.0)
        self.assertEqual(oc.total_items(), 0)
        self.assertListEqual(oc.list_items(), [])

    def test_remove_non_existent_item(self):
        oc = OrderCalculator()
        with self.assertRaises(KeyError):
            oc.remove_item("banana")

    def test_remove_non_string_name(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 1)
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_remove_from_empty_cart(self):
        oc = OrderCalculator()
        with self.assertRaises(KeyError):
            oc.remove_item("apple")

    # 4. get_subtotal
    def test_get_subtotal_empty_cart(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.get_subtotal(), 0.0)

    def test_get_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.5, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 3.0)

    def test_get_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 1)
        oc.add_item("banana", 2.0, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 5.0)

    def test_get_subtotal_after_add_remove(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 1)
        oc.add_item("banana", 2.0, 2)
        oc.remove_item("apple")
        self.assertAlmostEqual(oc.get_subtotal(), 4.0)

    # 5. apply_discount
    def test_apply_discount_less_than_subtotal(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 3)
        subtotal = oc.get_subtotal()
        discounted = oc.apply_discount(subtotal, 1.0)
        self.assertAlmostEqual(discounted, subtotal - 1.0)

    def test_apply_discount_equal_to_subtotal(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 3)
        subtotal = oc.get_subtotal()
        discounted = oc.apply_discount(subtotal, subtotal)
        self.assertAlmostEqual(discounted, 0.0)

    def test_apply_discount_greater_than_subtotal(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 3)
        subtotal = oc.get_subtotal()
        discounted = oc.apply_discount(subtotal, subtotal + 5.0)
        self.assertAlmostEqual(discounted, 0.0)

    def test_apply_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(10.0, -1.0)

    def test_apply_discount_non_numeric(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(10.0, "5")

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 2)
        subtotal = oc.get_subtotal()
        discounted = oc.apply_discount(subtotal, 0.0)
        self.assertAlmostEqual(discounted, subtotal)

    # 6. calculate_shipping
    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        discounted_subtotal = 60.0
        shipping = oc.calculate_shipping(discounted_subtotal)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        discounted_subtotal = 40.0
        shipping = oc.calculate_shipping(discounted_subtotal)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_exact_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        discounted_subtotal = 50.0
        shipping = oc.calculate_shipping(discounted_subtotal)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        shipping = oc.calculate_shipping(-5.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_non_numeric(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping("10")

    def test_calculate_shipping_threshold_zero(self):
        oc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        shipping = oc.calculate_shipping(5.0)
        self.assertAlmostEqual(shipping, 0.0)

    # 7. calculate_tax
    def test_calculate_tax_positive_amount(self):
        oc = OrderCalculator(tax_rate=0.2)
        tax = oc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 20.0)

    def test_calculate_tax_zero_amount(self):
        oc = OrderCalculator()
        tax = oc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-10.0)

    def test_calculate_tax_non_numeric(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax("10")

    def test_calculate_tax_zero_rate(self):
        oc = OrderCalculator(tax_rate=0.0)
        tax = oc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 0.0)

    # 8. calculate_total
    def test_calculate_total_no_discount(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        oc.add_item("apple", 50.0, 1)
        total = oc.calculate_total()
        expected = 50.0 + 10.0 + (60.0 * 0.1)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_less_than_subtotal(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        oc.add_item("apple", 80.0, 1)
        total = oc.calculate_total(discount=20.0)
        expected = 60.0 + 10.0 + (70.0 * 0.1)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_equal_to_subtotal(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        oc.add_item("apple", 80.0, 1)
        total = oc.calculate_total(discount=80.0)
        expected = 10.0 + (10.0 * 0.1)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_greater_than_subtotal(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        oc.add_item("apple", 30.0, 1)
        total = oc.calculate_total(discount=50.0)
        expected = 10.0 + (10.0 * 0.1)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_greater_threshold(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=10.0)
        oc.add_item("apple", 60.0, 1)
        total = oc.calculate_total(discount=70.0)
        expected = 0.0 + (0.0 * 0.1)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_negative_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-5.0)

    def test_calculate_total_non_numeric_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_total(discount="5")

    def test_calculate_total_custom_values(self):
        oc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=200.0, shipping_cost=20.0)
        oc.add_item("apple", 150.0, 1)
        total = oc.calculate_total(discount=30.0)
        expected = 120.0 + 20.0 + (140.0 * 0.15)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_large_discount_free_shipping(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        oc.add_item("apple", 200.0, 1)
        total = oc.calculate_total(discount=250.0)
        expected = 0.0 + (0.0 * 0.1)
        self.assertAlmostEqual(total, expected)

    # 9. total_items
    def test_total_items_empty_cart(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_single_item(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 3)
        self.assertEqual(oc.total_items(), 3)

    def test_total_items_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 2)
        oc.add_item("banana", 2.0, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_total_items_after_add_remove(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 2)
        oc.add_item("banana", 2.0, 3)
        oc.remove_item("apple")
        self.assertEqual(oc.total_items(), 3)

    # 10. clear_order
    def test_clear_non_empty_cart(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 2)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertAlmostEqual(oc.get_subtotal(), 0.0)
        self.assertEqual(oc.total_items(), 0)
        self.assertListEqual(oc.list_items(), [])

    def test_clear_already_empty_cart(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    # 11. list_items
    def test_list_items_empty_cart(self):
        oc = OrderCalculator()
        self.assertListEqual(oc.list_items(), [])

    def test_list_items_single_item(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 1)
        self.assertListEqual(oc.list_items(), ["apple"])

    def test_list_items_multiple_distinct(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 1)
        oc.add_item("banana", 2.0, 1)
        self.assertCountEqual(oc.list_items(), ["apple", "banana"])

    def test_list_items_duplicate_names_once(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 1)
        oc.add_item("apple", 2.0, 2)
        self.assertListEqual(oc.list_items(), ["apple"])

    def test_list_items_after_removal_or_clear(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 1)
        oc.remove_item("apple")
        self.assertListEqual(oc.list_items(), [])
        oc.add_item("banana", 2.0, 1)
        oc.clear_order()
        self.assertListEqual(oc.list_items(), [])

    # 12. is_empty
    def test_is_empty_new_cart(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_adding(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 1)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_removing_all(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 1)
        oc.remove_item("apple")
        self.assertTrue(oc.is_empty())

    # 13. Interaction
    def test_add_remove_subtotal(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 2)
        oc.remove_item("apple")
        self.assertAlmostEqual(oc.get_subtotal(), 0.0)

    def test_add_discount_total(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        oc.add_item("apple", 80.0, 1)
        total = oc.calculate_total(discount=20.0)
        expected = 60.0 + 10.0 + (70.0 * 0.1)
        self.assertAlmostEqual(total, expected)

    def test_add_clear_is_empty_list_items(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertListEqual(oc.list_items(), [])

    def test_add_list_remove_list_again(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 1)
        oc.add_item("banana", 2.0, 1)
        self.assertCountEqual(oc.list_items(), ["apple", "banana"])
        oc.remove_item("apple")
        self.assertListEqual(oc.list_items(), ["banana"])

    def test_add_total_items_remove_recompute(self):
        oc = OrderCalculator()
        oc.add_item("apple", 1.0, 3)
        oc.add_item("banana", 2.0, 2)
        self.assertEqual(oc.total_items(), 5)
        oc.remove_item("banana")
        self.assertEqual(oc.total_items(), 3)

    def test_add_total_with_custom_tax_rate(self):
        oc = OrderCalculator(tax_rate=0.2, free_shipping_threshold=100.0, shipping_cost=10.0)
        oc.add_item("apple", 50.0, 1)
        total = oc.calculate_total()
        expected = 50.0 + 10.0 + (60.0 * 0.2)
        self.assertAlmostEqual(total, expected)

    # 14. Edge large numbers
    def test_large_numbers(self):
        oc = OrderCalculator()
        oc.add_item("expensive", 1e12, 1e6)
        subtotal = oc.get_subtotal()
        self.assertAlmostEqual(subtotal, 1e18)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, subtotal + oc.shipping_cost + (subtotal + oc.shipping_cost) * oc.tax_rate)

    # 15. Edge floating-point precision
    def test_floating_point_precision(self):
        oc = OrderCalculator(tax_rate=0.1)
        oc.add_item("item", 0.1, 1)
        oc.add_item("item", 0.2, 1)
        subtotal = oc.get_subtotal()
        self.assertAlmostEqual(subtotal, 0.3, places=7)
        total = oc.calculate_total()
        expected = 0.3 + oc.shipping_cost + (0.3 + oc.shipping_cost) * 0.1
        self.assertAlmostEqual(total, expected, places=7)

if __name__ == "__main__":
    unittest.main()