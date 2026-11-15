import unittest

from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def test_init_defaults(self):
        calculator = OrderCalculator()
        self.assertEqual(calculator.tax_rate, 0.23)
        self.assertEqual(calculator.free_shipping_threshold, 100.0)
        self.assertEqual(calculator.shipping_cost, 10.0)
        self.assertEqual(calculator.items, [])

    def test_init_custom_values(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calculator.tax_rate, 0.1)
        self.assertEqual(calculator.free_shipping_threshold, 50.0)
        self.assertEqual(calculator.shipping_cost, 5.0)

    def test_init_accepts_int_values(self):
        calculator = OrderCalculator(tax_rate=0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(calculator.tax_rate, 0.0)
        self.assertEqual(calculator.free_shipping_threshold, 0.0)
        self.assertEqual(calculator.shipping_cost, 0.0)

    def test_init_tax_rate_one_is_valid(self):
        calculator = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calculator.tax_rate, 1.0)

    def test_init_tax_rate_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.1")

    def test_init_tax_rate_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate=None)

    def test_init_free_shipping_threshold_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100.0")

    def test_init_free_shipping_threshold_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_shipping_cost_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10.0")

    def test_init_shipping_cost_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_init_tax_rate_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_free_shipping_threshold_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_shipping_cost_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-10.0)

    def test_add_item_appends_new_item(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0, 3)
        self.assertEqual(calculator.items, [{"name": "Apple", "price": 2.0, "quantity": 3}])

    def test_add_item_default_quantity_is_one(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0)
        self.assertEqual(calculator.items[0]["quantity"], 1)

    def test_add_item_accepts_int_price(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2)
        self.assertEqual(calculator.items[0]["price"], 2)

    def test_add_item_increases_quantity_for_same_name_and_price(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0, 1)
        calculator.add_item("Apple", 2.0, 2)
        self.assertEqual(len(calculator.items), 1)
        self.assertEqual(calculator.items[0]["quantity"], 3)

    def test_add_item_same_name_different_price_raises_value_error(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0)
        with self.assertRaises(ValueError):
            calculator.add_item("Apple", 3.0)

    def test_add_item_empty_name_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item("", 1.0)

    def test_add_item_zero_price_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item("Apple", 0.0)

    def test_add_item_negative_price_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item("Apple", -1.0)

    def test_add_item_zero_quantity_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item("Apple", 1.0, 0)

    def test_add_item_negative_quantity_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item("Apple", 1.0, -1)

    def test_add_item_non_string_name_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.add_item(123, 1.0)

    def test_add_item_non_numeric_price_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.add_item("Apple", "1.0")

    def test_add_item_non_integer_quantity_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.add_item("Apple", 1.0, 1.0)

    def test_remove_item_removes_existing_item(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0)
        calculator.add_item("Banana", 3.0)
        calculator.remove_item("Apple")
        self.assertEqual(calculator.items, [{"name": "Banana", "price": 3.0, "quantity": 1}])

    def test_remove_item_non_string_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.remove_item(123)

    def test_remove_item_missing_item_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.remove_item("Apple")

    def test_remove_item_from_empty_order_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.remove_item("Apple")

    def test_get_subtotal_empty_order_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.get_subtotal()

    def test_get_subtotal_single_item(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0, 3)
        self.assertAlmostEqual(calculator.get_subtotal(), 6.0)

    def test_get_subtotal_multiple_items(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0, 3)
        calculator.add_item("Banana", 1.5, 2)
        self.assertAlmostEqual(calculator.get_subtotal(), 9.0)

    def test_apply_discount_no_discount(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_partial_discount(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_full_discount(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_zero_subtotal(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_accepts_int_inputs(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(100, 0), 100.0)

    def test_apply_discount_negative_subtotal_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.apply_discount(-1.0, 0.1)

    def test_apply_discount_discount_below_zero_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_above_one_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.apply_discount(100.0, 1.1)

    def test_apply_discount_non_numeric_subtotal_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.apply_discount("100.0", 0.1)

    def test_apply_discount_non_numeric_discount_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.apply_discount(100.0, "0.1")

    def test_calculate_shipping_below_threshold(self):
        calculator = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calculator.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_at_threshold(self):
        calculator = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calculator.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        calculator = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calculator.calculate_shipping(100.01), 0.0)

    def test_calculate_shipping_zero_subtotal(self):
        calculator = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calculator.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_custom_threshold_and_cost(self):
        calculator = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calculator.calculate_shipping(49.99), 5.0)

    def test_calculate_shipping_zero_threshold(self):
        calculator = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertEqual(calculator.calculate_shipping(0.0), 0.0)

    def test_calculate_shipping_non_numeric_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.calculate_shipping("100.0")

    def test_calculate_tax_zero_amount(self):
        calculator = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calculator.calculate_tax(0.0), 0.0)

    def test_calculate_tax_positive_amount(self):
        calculator = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calculator.calculate_tax(100.0), 23.0)

    def test_calculate_tax_custom_rate(self):
        calculator = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(calculator.calculate_tax(50.0), 5.0)

    def test_calculate_tax_zero_rate(self):
        calculator = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calculator.calculate_tax(100.0), 0.0)

    def test_calculate_tax_accepts_int_amount(self):
        calculator = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(calculator.calculate_tax(100), 10.0)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.calculate_tax(-1.0)

    def test_calculate_tax_non_numeric_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.calculate_tax("100.0")

    def test_calculate_total_empty_order_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.calculate_total()

    def test_calculate_total_no_discount_below_threshold(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calculator.add_item("Apple", 50.0)
        self.assertAlmostEqual(calculator.calculate_total(), 66.0)

    def test_calculate_total_no_discount_at_threshold(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calculator.add_item("Apple", 100.0)
        self.assertAlmostEqual(calculator.calculate_total(), 110.0)

    def test_calculate_total_no_discount_above_threshold(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calculator.add_item("Apple", 150.0)
        self.assertAlmostEqual(calculator.calculate_total(), 165.0)

    def test_calculate_total_with_discount_below_threshold(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calculator.add_item("Apple", 100.0)
        self.assertAlmostEqual(calculator.calculate_total(0.5), 66.0)

    def test_calculate_total_with_discount_at_threshold(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calculator.add_item("Apple", 200.0)
        self.assertAlmostEqual(calculator.calculate_total(0.5), 110.0)

    def test_calculate_total_with_full_discount(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calculator.add_item("Apple", 100.0)
        self.assertAlmostEqual(calculator.calculate_total(1.0), 11.0)

    def test_calculate_total_full_discount_zero_threshold(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=0.0, shipping_cost=10.0)
        calculator.add_item("Apple", 100.0)
        self.assertAlmostEqual(calculator.calculate_total(1.0), 0.0)

    def test_calculate_total_multiple_items(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calculator.add_item("Apple", 30.0)
        calculator.add_item("Banana", 40.0)
        self.assertAlmostEqual(calculator.calculate_total(), 88.0)

    def test_calculate_total_invalid_discount_type_raises_type_error(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 10.0)
        with self.assertRaises(TypeError):
            calculator.calculate_total("0.1")

    def test_calculate_total_invalid_discount_below_zero_raises_value_error(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 10.0)
        with self.assertRaises(ValueError):
            calculator.calculate_total(-0.1)

    def test_calculate_total_invalid_discount_above_one_raises_value_error(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 10.0)
        with self.assertRaises(ValueError):
            calculator.calculate_total(1.1)

    def test_total_items_empty_order(self):
        calculator = OrderCalculator()
        self.assertEqual(calculator.total_items(), 0)

    def test_total_items_single_item(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0, 3)
        self.assertEqual(calculator.total_items(), 3)

    def test_total_items_multiple_items(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0, 3)
        calculator.add_item("Banana", 1.0, 2)
        self.assertEqual(calculator.total_items(), 5)

    def test_total_items_after_duplicate_add(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0, 1)
        calculator.add_item("Apple", 2.0, 2)
        self.assertEqual(calculator.total_items(), 3)

    def test_total_items_after_remove_item(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0, 3)
        calculator.add_item("Banana", 1.0, 2)
        calculator.remove_item("Apple")
        self.assertEqual(calculator.total_items(), 2)

    def test_clear_order_removes_all_items(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0)
        calculator.add_item("Banana", 3.0)
        calculator.clear_order()
        self.assertEqual(calculator.items, [])

    def test_clear_order_empty_order(self):
        calculator = OrderCalculator()
        calculator.clear_order()
        self.assertEqual(calculator.items, [])

    def test_list_items_empty_order(self):
        calculator = OrderCalculator()
        self.assertEqual(calculator.list_items(), [])

    def test_list_items_returns_unique_names(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0)
        calculator.add_item("Banana", 3.0)
        calculator.add_item("Apple", 2.0)
        self.assertCountEqual(calculator.list_items(), ["Apple", "Banana"])

    def test_list_items_returns_list_type(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0)
        self.assertIsInstance(calculator.list_items(), list)

    def test_is_empty_true_for_empty_order(self):
        calculator = OrderCalculator()
        self.assertTrue(calculator.is_empty())

    def test_is_empty_false_after_add_item(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0)
        self.assertFalse(calculator.is_empty())

    def test_is_empty_true_after_clear(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0)
        calculator.clear_order()
        self.assertTrue(calculator.is_empty())

    def test_is_empty_true_after_remove_item(self):
        calculator = OrderCalculator()
        calculator.add_item("Apple", 2.0)
        calculator.remove_item("Apple")
        self.assertTrue(calculator.is_empty())


if __name__ == "__main__":
    unittest.main()