import unittest

from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def test_init_default_tax_rate(self):
        calculator = OrderCalculator()
        self.assertEqual(calculator.tax_rate, 0.23)

    def test_init_default_free_shipping_threshold(self):
        calculator = OrderCalculator()
        self.assertEqual(calculator.free_shipping_threshold, 100.0)

    def test_init_default_shipping_cost(self):
        calculator = OrderCalculator()
        self.assertEqual(calculator.shipping_cost, 10.0)

    def test_init_default_items_empty(self):
        calculator = OrderCalculator()
        self.assertEqual(calculator.items, [])

    def test_init_custom_tax_rate(self):
        calculator = OrderCalculator(tax_rate=0.1)
        self.assertEqual(calculator.tax_rate, 0.1)

    def test_init_custom_free_shipping_threshold(self):
        calculator = OrderCalculator(free_shipping_threshold=50.0)
        self.assertEqual(calculator.free_shipping_threshold, 50.0)

    def test_init_custom_shipping_cost(self):
        calculator = OrderCalculator(shipping_cost=5.0)
        self.assertEqual(calculator.shipping_cost, 5.0)

    def test_init_accepts_int_values(self):
        calculator = OrderCalculator(tax_rate=0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(calculator.tax_rate, 0)
        self.assertEqual(calculator.free_shipping_threshold, 0)
        self.assertEqual(calculator.shipping_cost, 0)

    def test_init_tax_rate_below_zero_raises_value_error(self):
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

    def test_init_invalid_tax_rate_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.23")

    def test_init_invalid_free_shipping_threshold_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    def test_init_invalid_shipping_cost_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    def test_add_item_single(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0)
        self.assertEqual(calculator.items, [{"name": "A", "price": 10.0, "quantity": 1}])

    def test_add_item_explicit_quantity(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0, 3)
        self.assertEqual(calculator.items, [{"name": "A", "price": 10.0, "quantity": 3}])

    def test_add_item_int_price(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10)
        self.assertEqual(calculator.items, [{"name": "A", "price": 10, "quantity": 1}])

    def test_add_item_whitespace_name_is_valid(self):
        calculator = OrderCalculator()
        calculator.add_item(" ", 10.0)
        self.assertEqual(calculator.items, [{"name": " ", "price": 10.0, "quantity": 1}])

    def test_add_item_same_name_and_price_increases_quantity(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0)
        calculator.add_item("A", 10.0, 2)
        self.assertEqual(calculator.items, [{"name": "A", "price": 10.0, "quantity": 3}])

    def test_add_item_same_name_and_numeric_equivalent_price_increases_quantity(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10)
        calculator.add_item("A", 10.0, 2)
        self.assertEqual(calculator.items, [{"name": "A", "price": 10, "quantity": 3}])

    def test_add_item_same_name_different_price_raises_value_error(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0)
        with self.assertRaises(ValueError):
            calculator.add_item("A", 11.0)

    def test_add_item_empty_name_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item("", 10.0)

    def test_add_item_zero_price_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item("A", 0.0)

    def test_add_item_negative_price_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item("A", -1.0)

    def test_add_item_zero_quantity_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item("A", 10.0, 0)

    def test_add_item_negative_quantity_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item("A", 10.0, -1)

    def test_add_item_invalid_name_type_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.add_item(123, 10.0)

    def test_add_item_invalid_price_type_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.add_item("A", "10.0")

    def test_add_item_invalid_quantity_type_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.add_item("A", 10.0, 1.5)

    def test_remove_item_existing(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0)
        calculator.add_item("B", 20.0)
        calculator.remove_item("A")
        self.assertEqual(calculator.items, [{"name": "B", "price": 20.0, "quantity": 1}])

    def test_remove_item_nonexistent_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.remove_item("A")

    def test_remove_item_empty_name_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.remove_item("")

    def test_remove_item_invalid_type_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.remove_item(123)

    def test_get_subtotal_empty_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.get_subtotal()

    def test_get_subtotal_single_item(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0, 2)
        self.assertAlmostEqual(calculator.get_subtotal(), 20.0)

    def test_get_subtotal_multiple_items(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0, 2)
        calculator.add_item("B", 5.0, 3)
        self.assertAlmostEqual(calculator.get_subtotal(), 35.0)

    def test_get_subtotal_int_prices(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10, 2)
        calculator.add_item("B", 5, 3)
        self.assertEqual(calculator.get_subtotal(), 35)

    def test_apply_discount_typical(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero_discount(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_zero_subtotal(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_int_inputs(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(100, 1), 0.0)

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

    def test_apply_discount_invalid_subtotal_type_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.apply_discount("100.0", 0.1)

    def test_apply_discount_invalid_discount_type_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.apply_discount(100.0, "0.1")

    def test_calculate_shipping_below_threshold(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_at_threshold(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.calculate_shipping(100.01), 0.0)

    def test_calculate_shipping_int_input(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.calculate_shipping(99), 10.0)

    def test_calculate_shipping_custom_threshold_below(self):
        calculator = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calculator.calculate_shipping(49.99), 5.0)

    def test_calculate_shipping_custom_threshold_at(self):
        calculator = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calculator.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_zero_threshold(self):
        calculator = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertAlmostEqual(calculator.calculate_shipping(0.0), 0.0)

    def test_calculate_shipping_invalid_type_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.calculate_shipping("100.0")

    def test_calculate_tax_typical(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.calculate_tax(0.0), 0.0)

    def test_calculate_tax_zero_rate(self):
        calculator = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calculator.calculate_tax(100.0), 0.0)

    def test_calculate_tax_full_rate(self):
        calculator = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calculator.calculate_tax(100.0), 100.0)

    def test_calculate_tax_int_amount(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.calculate_tax(100), 23.0)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.calculate_tax(-1.0)

    def test_calculate_tax_invalid_type_raises_type_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.calculate_tax("100.0")

    def test_calculate_total_no_discount_below_threshold(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0)
        self.assertAlmostEqual(calculator.calculate_total(), 22.3)

    def test_calculate_total_no_discount_at_threshold(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 100.0)
        self.assertAlmostEqual(calculator.calculate_total(), 123.0)

    def test_calculate_total_discount_below_threshold(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 100.0)
        self.assertAlmostEqual(calculator.calculate_total(discount=0.5), 73.8)

    def test_calculate_total_discount_reaches_free_shipping(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 150.0)
        self.assertAlmostEqual(calculator.calculate_total(discount=0.3), 129.15)

    def test_calculate_total_full_discount(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 100.0)
        self.assertAlmostEqual(calculator.calculate_total(discount=1.0), 12.3)

    def test_calculate_total_int_discount(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 100.0)
        self.assertAlmostEqual(calculator.calculate_total(discount=0), 123.0)

    def test_calculate_total_uses_custom_shipping_and_threshold(self):
        calculator = OrderCalculator(tax_rate=0.0, free_shipping_threshold=50.0, shipping_cost=5.0)
        calculator.add_item("A", 40.0)
        self.assertAlmostEqual(calculator.calculate_total(), 45.0)

    def test_calculate_total_uses_custom_free_shipping_threshold(self):
        calculator = OrderCalculator(tax_rate=0.0, free_shipping_threshold=50.0, shipping_cost=5.0)
        calculator.add_item("A", 50.0)
        self.assertAlmostEqual(calculator.calculate_total(), 50.0)

    def test_calculate_total_zero_tax_and_shipping(self):
        calculator = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        calculator.add_item("A", 10.0)
        self.assertAlmostEqual(calculator.calculate_total(), 10.0)

    def test_calculate_total_empty_order_raises_value_error(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.calculate_total()

    def test_calculate_total_invalid_discount_type_raises_type_error(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0)
        with self.assertRaises(TypeError):
            calculator.calculate_total(discount="0.1")

    def test_calculate_total_discount_below_zero_raises_value_error(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0)
        with self.assertRaises(ValueError):
            calculator.calculate_total(discount=-0.1)

    def test_calculate_total_discount_above_one_raises_value_error(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0)
        with self.assertRaises(ValueError):
            calculator.calculate_total(discount=1.1)

    def test_total_items_empty(self):
        calculator = OrderCalculator()
        self.assertEqual(calculator.total_items(), 0)

    def test_total_items_single(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0, 3)
        self.assertEqual(calculator.total_items(), 3)

    def test_total_items_multiple(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0, 2)
        calculator.add_item("B", 20.0, 3)
        self.assertEqual(calculator.total_items(), 5)

    def test_clear_order_removes_items(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0)
        calculator.add_item("B", 20.0)
        calculator.clear_order()
        self.assertEqual(calculator.items, [])

    def test_clear_order_empty_order(self):
        calculator = OrderCalculator()
        calculator.clear_order()
        self.assertEqual(calculator.items, [])

    def test_clear_order_resets_total_items(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0, 2)
        calculator.clear_order()
        self.assertEqual(calculator.total_items(), 0)

    def test_clear_order_makes_order_empty(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0)
        calculator.clear_order()
        self.assertTrue(calculator.is_empty())

    def test_list_items_empty(self):
        calculator = OrderCalculator()
        self.assertEqual(calculator.list_items(), [])

    def test_list_items_unique_names(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0)
        calculator.add_item("B", 20.0)
        calculator.add_item("A", 10.0)
        self.assertCountEqual(calculator.list_items(), ["A", "B"])

    def test_is_empty_true_when_no_items(self):
        calculator = OrderCalculator()
        self.assertTrue(calculator.is_empty())

    def test_is_empty_false_after_add_item(self):
        calculator = OrderCalculator()
        calculator.add_item("A", 10.0)
        self.assertFalse(calculator.is_empty())


if __name__ == "__main__":
    unittest.main()