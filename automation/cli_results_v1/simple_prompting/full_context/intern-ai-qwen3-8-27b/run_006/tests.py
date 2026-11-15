import unittest

from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_accepts_int_values(self):
        calc = OrderCalculator(0, 0, 0)
        self.assertEqual(calc.tax_rate, 0)
        self.assertEqual(calc.free_shipping_threshold, 0)
        self.assertEqual(calc.shipping_cost, 0)

    def test_init_tax_rate_string_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator("0.1")

    def test_init_tax_rate_none_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(None)

    def test_init_tax_rate_list_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator([0.1])

    def test_init_threshold_string_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(0.1, "100.0")

    def test_init_threshold_none_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(0.1, None)

    def test_init_threshold_list_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(0.1, [100.0])

    def test_init_shipping_string_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(0.1, 100.0, "10.0")

    def test_init_shipping_none_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(0.1, 100.0, None)

    def test_init_shipping_list_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(0.1, 100.0, [10.0])

    def test_init_tax_rate_below_zero_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(-0.1)

    def test_init_tax_rate_above_one_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(1.1)

    def test_init_threshold_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(0.1, -1.0)

    def test_init_shipping_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(0.1, 100.0, -1.0)

    def test_init_tax_rate_zero_ok(self):
        calc = OrderCalculator(0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_one_ok(self):
        calc = OrderCalculator(1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_threshold_zero_ok(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_init_shipping_zero_ok(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_add_item_single(self):
        self.calc.add_item("A", 10.0)
        self.assertEqual(self.calc.items, [{"name": "A", "price": 10.0, "quantity": 1}])

    def test_add_item_default_quantity(self):
        self.calc.add_item("A", 10.0)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_explicit_quantity(self):
        self.calc.add_item("A", 10.0, 3)
        self.assertEqual(self.calc.items[0]["quantity"], 3)

    def test_add_item_int_price(self):
        self.calc.add_item("A", 10, 2)
        self.assertEqual(self.calc.items[0]["price"], 10)

    def test_add_item_same_name_price_increases_quantity(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("A", 10.0, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]["quantity"], 3)

    def test_add_item_same_name_default_quantity_increases(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("A", 10.0)
        self.assertEqual(self.calc.items[0]["quantity"], 2)

    def test_add_item_same_name_different_price_raises(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(ValueError):
            self.calc.add_item("A", 20.0)

    def test_add_item_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 10.0)

    def test_add_item_whitespace_name_allowed(self):
        self.calc.add_item(" ", 10.0)
        self.assertEqual(self.calc.list_items(), [" "])

    def test_add_item_zero_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("A", 0)

    def test_add_item_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("A", -1)

    def test_add_item_zero_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("A", 10.0, 0)

    def test_add_item_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("A", 10.0, -1)

    def test_add_item_name_not_string_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 10.0)

    def test_add_item_name_none_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(None, 10.0)

    def test_add_item_name_list_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(["A"], 10.0)

    def test_add_item_price_not_number_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", "10.0")

    def test_add_item_price_none_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", None)

    def test_add_item_price_list_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", [10.0])

    def test_add_item_quantity_not_int_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", 10.0, 1.0)

    def test_add_item_quantity_none_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", 10.0, None)

    def test_add_item_quantity_list_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", 10.0, [1])

    def test_remove_item_existing(self):
        self.calc.add_item("A", 10.0)
        self.calc.remove_item("A")
        self.assertEqual(self.calc.items, [])

    def test_remove_item_one_of_multiple(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.calc.remove_item("A")
        self.assertEqual(self.calc.list_items(), ["B"])

    def test_remove_item_nonexistent_raises(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("A")

    def test_remove_item_empty_order_raises(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("A")

    def test_remove_item_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("")

    def test_remove_item_name_not_string_raises(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_remove_item_name_none_raises(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(None)

    def test_remove_item_name_list_raises(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(["A"])

    def test_get_subtotal_empty_raises(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_get_subtotal_single_item(self):
        self.calc.add_item("A", 10.0, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 20.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.add_item("B", 5.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 35.0)

    def test_get_subtotal_int_price(self):
        self.calc.add_item("A", 10, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 20.0)

    def test_get_subtotal_after_remove(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.calc.remove_item("A")
        self.assertAlmostEqual(self.calc.get_subtotal(), 20.0)

    def test_get_subtotal_after_clear(self):
        self.calc.add_item("A", 10.0)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_typical(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_zero_subtotal(self):
        self.assertAlmostEqual(self.calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_int_values(self):
        self.assertEqual(self.calc.apply_discount(100, 0), 100)

    def test_apply_discount_negative_subtotal_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-1.0, 0.1)

    def test_apply_discount_discount_below_zero_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_above_one_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.1)

    def test_apply_discount_subtotal_not_number_raises(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100.0", 0.1)

    def test_apply_discount_subtotal_none_raises(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(None, 0.1)

    def test_apply_discount_subtotal_list_raises(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount([100.0], 0.1)

    def test_apply_discount_discount_not_number_raises(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, "0.1")

    def test_apply_discount_discount_none_raises(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, None)

    def test_apply_discount_discount_list_raises(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, [0.1])

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.01), 0.0)

    def test_calculate_shipping_zero_subtotal(self):
        self.assertEqual(self.calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_custom_threshold_at_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_custom_threshold_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(49.99), 5.0)

    def test_calculate_shipping_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)

    def test_calculate_shipping_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)

    def test_calculate_shipping_not_number_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("100.0")

    def test_calculate_shipping_none_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping(None)

    def test_calculate_shipping_list_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping([100.0])

    def test_calculate_tax_typical(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_full_rate(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 100.0)

    def test_calculate_tax_int_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100), 23.0)

    def test_calculate_tax_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-1.0)

    def test_calculate_tax_not_number_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("100.0")

    def test_calculate_tax_none_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax(None)

    def test_calculate_tax_list_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax([100.0])

    def test_calculate_total_empty_order_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_empty_order_invalid_discount_type_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total("0.1")

    def test_calculate_total_negative_subtotal_raises(self):
        self.calc.items = [{"name": "A", "price": -1.0, "quantity": 1}]
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_no_discount_below_threshold(self):
        self.calc.add_item("A", 50.0)
        self.assertAlmostEqual(self.calc.calculate_total(), 73.8)

    def test_calculate_total_no_discount_at_threshold(self):
        self.calc.add_item("A", 100.0)
        self.assertAlmostEqual(self.calc.calculate_total(), 123.0)

    def test_calculate_total_no_discount_above_threshold(self):
        self.calc.add_item("A", 150.0)
        self.assertAlmostEqual(self.calc.calculate_total(), 184.5)

    def test_calculate_total_with_discount_below_threshold(self):
        self.calc.add_item("A", 100.0)
        self.assertAlmostEqual(self.calc.calculate_total(0.5), 73.8)

    def test_calculate_total_with_discount_at_threshold(self):
        self.calc.add_item("A", 200.0)
        self.assertAlmostEqual(self.calc.calculate_total(0.5), 123.0)

    def test_calculate_total_with_discount_above_threshold(self):
        self.calc.add_item("A", 200.0)
        self.assertAlmostEqual(self.calc.calculate_total(0.25), 184.5)

    def test_calculate_total_full_discount_below_threshold(self):
        self.calc.add_item("A", 100.0)
        self.assertAlmostEqual(self.calc.calculate_total(1.0), 12.3)

    def test_calculate_total_full_discount_zero_threshold(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=0.0, shipping_cost=10.0)
        calc.add_item("A", 100.0)
        self.assertAlmostEqual(calc.calculate_total(1.0), 0.0)

    def test_calculate_total_zero_shipping(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item("A", 50.0)
        self.assertAlmostEqual(calc.calculate_total(), 61.5)

    def test_calculate_total_zero_tax(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item("A", 50.0)
        self.assertAlmostEqual(calc.calculate_total(), 60.0)

    def test_calculate_total_multiple_items(self):
        self.calc.add_item("A", 50.0)
        self.calc.add_item("B", 60.0)
        self.assertAlmostEqual(self.calc.calculate_total(), 135.3)

    def test_calculate_total_int_discount(self):
        self.calc.add_item("A", 100.0)
        self.assertAlmostEqual(self.calc.calculate_total(0), 123.0)

    def test_calculate_total_int_full_discount(self):
        self.calc.add_item("A", 100.0)
        self.assertAlmostEqual(self.calc.calculate_total(1), 12.3)

    def test_calculate_total_discount_not_number_raises(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total("0.1")

    def test_calculate_total_discount_none_raises(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(None)

    def test_calculate_total_discount_list_raises(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total([0.1])

    def test_calculate_total_discount_below_zero_raises(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-0.1)

    def test_calculate_total_discount_above_one_raises(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.1)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_single(self):
        self.calc.add_item("A", 10.0, 3)
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_multiple(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.add_item("B", 20.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_remove(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.add_item("B", 20.0, 3)
        self.calc.remove_item("A")
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_after_clear(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_same_name_increases(self):
        self.calc.add_item("A", 10.0, 1)
        self.calc.add_item("A", 10.0, 2)
        self.assertEqual(self.calc.total_items(), 3)

    def test_clear_order_removes_items(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.items, [])

    def test_clear_order_empty(self):
        self.calc.clear_order()
        self.assertEqual(self.calc.items, [])

    def test_clear_order_resets_total_items(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_resets_is_empty(self):
        self.calc.add_item("A", 10.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_single(self):
        self.calc.add_item("A", 10.0)
        self.assertEqual(self.calc.list_items(), ["A"])

    def test_list_items_multiple(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.assertCountEqual(self.calc.list_items(), ["A", "B"])

    def test_list_items_unique_after_same_name(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("A", 10.0)
        self.assertEqual(self.calc.list_items(), ["A"])

    def test_list_items_after_remove(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.calc.remove_item("A")
        self.assertEqual(self.calc.list_items(), ["B"])

    def test_list_items_after_clear(self):
        self.calc.add_item("A", 10.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item("A", 10.0)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item("A", 10.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_remove_all(self):
        self.calc.add_item("A", 10.0)
        self.calc.remove_item("A")
        self.assertTrue(self.calc.is_empty())


if __name__ == "__main__":
    unittest.main()