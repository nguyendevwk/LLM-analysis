import unittest

from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_tax_rate(self):
        self.assertEqual(self.calc.tax_rate, 0.23)

    def test_init_default_free_shipping_threshold(self):
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)

    def test_init_default_shipping_cost(self):
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_init_default_items_empty(self):
        self.assertEqual(self.calc.items, [])

    def test_init_custom_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.1)
        self.assertEqual(calc.tax_rate, 0.1)

    def test_init_custom_free_shipping_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0)
        self.assertEqual(calc.free_shipping_threshold, 50.0)

    def test_init_custom_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=5.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_accepts_int_tax_rate(self):
        calc = OrderCalculator(tax_rate=0)
        self.assertEqual(calc.tax_rate, 0)

    def test_init_accepts_int_free_shipping_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100)
        self.assertEqual(calc.free_shipping_threshold, 100)

    def test_init_accepts_int_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=10)
        self.assertEqual(calc.shipping_cost, 10)

    def test_init_tax_rate_zero_accepted(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_one_accepted(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_free_shipping_threshold_zero_accepted(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_init_shipping_cost_zero_accepted(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_tax_rate_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_negative_free_shipping_threshold_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_negative_shipping_cost_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1.0)

    def test_init_tax_rate_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.23")

    def test_init_tax_rate_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate=None)

    def test_init_free_shipping_threshold_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    def test_init_free_shipping_threshold_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_shipping_cost_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    def test_init_shipping_cost_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_add_item_default_quantity(self):
        self.calc.add_item("A", 10.0)
        self.assertEqual(self.calc.items, [{"name": "A", "price": 10.0, "quantity": 1}])

    def test_add_item_explicit_quantity(self):
        self.calc.add_item("A", 10.0, 3)
        self.assertEqual(self.calc.items, [{"name": "A", "price": 10.0, "quantity": 3}])

    def test_add_item_int_price(self):
        self.calc.add_item("A", 10)
        self.assertEqual(self.calc.items[0]["price"], 10)

    def test_add_item_whitespace_name_accepted(self):
        self.calc.add_item(" ", 10.0)
        self.assertEqual(self.calc.items[0]["name"], " ")

    def test_add_item_multiple_items(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.assertEqual(len(self.calc.items), 2)

    def test_add_item_same_name_and_price_increases_quantity(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("A", 10.0, 2)
        self.assertEqual(self.calc.items, [{"name": "A", "price": 10.0, "quantity": 3}])

    def test_add_item_same_name_and_price_default_quantity_increases_by_one(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.add_item("A", 10.0)
        self.assertEqual(self.calc.items[0]["quantity"], 3)

    def test_add_item_same_name_different_price_raises_value_error(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(ValueError):
            self.calc.add_item("A", 11.0)

    def test_add_item_same_name_different_price_does_not_modify_order(self):
        self.calc.add_item("A", 10.0, 2)
        with self.assertRaises(ValueError):
            self.calc.add_item("A", 11.0)
        self.assertEqual(self.calc.items, [{"name": "A", "price": 10.0, "quantity": 2}])

    def test_add_item_empty_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 10.0)

    def test_add_item_zero_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("A", 0)

    def test_add_item_negative_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("A", -1.0)

    def test_add_item_zero_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("A", 10.0, 0)

    def test_add_item_negative_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("A", 10.0, -1)

    def test_add_item_non_string_name_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 10.0)

    def test_add_item_none_name_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(None, 10.0)

    def test_add_item_non_number_price_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", "10")

    def test_add_item_none_price_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", None)

    def test_add_item_float_quantity_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", 10.0, 1.0)

    def test_add_item_none_quantity_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", 10.0, None)

    def test_remove_item_removes_item(self):
        self.calc.add_item("A", 10.0)
        self.calc.remove_item("A")
        self.assertEqual(self.calc.items, [])

    def test_remove_item_preserves_other_items(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.calc.remove_item("A")
        self.assertEqual(self.calc.items, [{"name": "B", "price": 20.0, "quantity": 1}])

    def test_remove_item_nonexistent_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("A")

    def test_remove_item_empty_order_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("A")

    def test_remove_item_empty_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("")

    def test_remove_item_non_string_name_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_remove_item_none_name_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(None)

    def test_remove_item_after_duplicate_add_removes_merged_item(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("A", 10.0, 2)
        self.calc.remove_item("A")
        self.assertEqual(self.calc.items, [])

    def test_remove_item_allows_readding(self):
        self.calc.add_item("A", 10.0)
        self.calc.remove_item("A")
        self.calc.add_item("A", 10.0)
        self.assertEqual(self.calc.items, [{"name": "A", "price": 10.0, "quantity": 1}])

    def test_get_subtotal_empty_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_get_subtotal_single_item(self):
        self.calc.add_item("A", 10.0, 2)
        self.assertEqual(self.calc.get_subtotal(), 20.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.add_item("B", 5.0, 3)
        self.assertEqual(self.calc.get_subtotal(), 35.0)

    def test_get_subtotal_int_price(self):
        self.calc.add_item("A", 10, 2)
        self.assertEqual(self.calc.get_subtotal(), 20)

    def test_get_subtotal_after_remove(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.add_item("B", 5.0, 3)
        self.calc.remove_item("A")
        self.assertEqual(self.calc.get_subtotal(), 15.0)

    def test_get_subtotal_after_duplicate_add(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("A", 10.0, 2)
        self.assertEqual(self.calc.get_subtotal(), 30.0)

    def test_get_subtotal_after_clear_raises_value_error(self):
        self.calc.add_item("A", 10.0)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_typical(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero_discount(self):
        self.assertEqual(self.calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        self.assertEqual(self.calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_zero_subtotal(self):
        self.assertEqual(self.calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_int_inputs(self):
        self.assertEqual(self.calc.apply_discount(100, 0), 100)

    def test_apply_discount_int_full_discount(self):
        self.assertEqual(self.calc.apply_discount(100, 1), 0)

    def test_apply_discount_negative_subtotal_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-1.0, 0.1)

    def test_apply_discount_discount_below_zero_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_above_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.1)

    def test_apply_discount_non_number_subtotal_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100", 0.1)

    def test_apply_discount_none_subtotal_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(None, 0.1)

    def test_apply_discount_non_number_discount_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, "0.1")

    def test_apply_discount_none_discount_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, None)

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.01), 0.0)

    def test_calculate_shipping_int_input(self):
        self.assertEqual(self.calc.calculate_shipping(99), 10.0)

    def test_calculate_shipping_custom_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(49.99), 5.0)

    def test_calculate_shipping_custom_threshold_at_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)

    def test_calculate_shipping_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(10.0), 0.0)

    def test_calculate_shipping_negative_subtotal_returns_shipping_cost(self):
        self.assertEqual(self.calc.calculate_shipping(-1.0), 10.0)

    def test_calculate_shipping_non_number_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("100")

    def test_calculate_shipping_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping(None)

    def test_calculate_tax_typical(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_full_tax_rate(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.calculate_tax(100.0), 100.0)

    def test_calculate_tax_int_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100), 23.0)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-1.0)

    def test_calculate_tax_non_number_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("100")

    def test_calculate_tax_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax(None)

    def test_calculate_total_empty_order_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_non_number_discount_raises_type_error(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total("0.1")

    def test_calculate_total_none_discount_raises_type_error(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(None)

    def test_calculate_total_discount_below_zero_raises_value_error(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-0.1)

    def test_calculate_total_discount_above_one_raises_value_error(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.1)

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

    def test_calculate_total_with_discount_qualifies_free_shipping(self):
        self.calc.add_item("A", 120.0)
        self.assertAlmostEqual(self.calc.calculate_total(0.1), 132.84)

    def test_calculate_total_full_discount(self):
        self.calc.add_item("A", 50.0)
        self.assertAlmostEqual(self.calc.calculate_total(1.0), 12.3)

    def test_calculate_total_int_discount(self):
        self.calc.add_item("A", 100.0)
        self.assertAlmostEqual(self.calc.calculate_total(0), 123.0)

    def test_calculate_total_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item("A", 50.0)
        self.assertAlmostEqual(calc.calculate_total(), 60.0)

    def test_calculate_total_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item("A", 50.0)
        self.assertAlmostEqual(calc.calculate_total(), 61.5)

    def test_calculate_total_custom_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.1)
        calc.add_item("A", 100.0)
        self.assertAlmostEqual(calc.calculate_total(), 110.0)

    def test_calculate_total_custom_shipping_and_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0, tax_rate=0.1)
        calc.add_item("A", 40.0)
        self.assertAlmostEqual(calc.calculate_total(), 49.5)

    def test_calculate_total_multiple_items(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.add_item("B", 5.0, 3)
        self.assertAlmostEqual(self.calc.calculate_total(), 55.35)

    def test_calculate_total_after_clear_raises_value_error(self):
        self.calc.add_item("A", 10.0)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_single_item(self):
        self.calc.add_item("A", 10.0, 3)
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_multiple_items(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.add_item("B", 20.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_duplicate_add(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("A", 10.0, 2)
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_after_remove(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.add_item("B", 20.0, 3)
        self.calc.remove_item("A")
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_after_remove_all(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.remove_item("A")
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_after_clear(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_empty(self):
        self.calc.clear_order()
        self.assertEqual(self.calc.items, [])

    def test_clear_order_removes_items(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.items, [])

    def test_clear_order_resets_total_items(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_resets_list_items(self):
        self.calc.add_item("A", 10.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_clear_order_makes_order_empty(self):
        self.calc.add_item("A", 10.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_clear_order_preserves_configuration(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item("A", 10.0)
        calc.clear_order()
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_single_item(self):
        self.calc.add_item("A", 10.0)
        self.assertEqual(self.calc.list_items(), ["A"])

    def test_list_items_multiple_items(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.assertEqual(sorted(self.calc.list_items()), ["A", "B"])

    def test_list_items_duplicate_same_name(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("A", 10.0, 2)
        self.assertEqual(self.calc.list_items(), ["A"])

    def test_list_items_after_remove(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.calc.remove_item("A")
        self.assertEqual(self.calc.list_items(), ["B"])

    def test_list_items_after_remove_all(self):
        self.calc.add_item("A", 10.0)
        self.calc.remove_item("A")
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_after_clear(self):
        self.calc.add_item("A", 10.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_new_order(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item("A", 10.0)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_remove(self):
        self.calc.add_item("A", 10.0)
        self.calc.remove_item("A")
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item("A", 10.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_with_multiple_items(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.assertFalse(self.calc.is_empty())


if __name__ == "__main__":
    unittest.main()