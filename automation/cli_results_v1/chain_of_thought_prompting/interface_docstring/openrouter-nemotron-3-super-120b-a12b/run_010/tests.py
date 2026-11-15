import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def test_init_default_args(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom_valid_args(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)
        self.assertEqual(calc.items, [])

    def test_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_greater_than_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_non_numeric_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.23")

    def test_init_non_numeric_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    def test_init_non_numeric_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    def test_init_mixed_valid_invalid(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=0.2, free_shipping_threshold=50.0, shipping_cost=-5.0)

    def test_add_item_new_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]["name"], "Apple")
        self.assertEqual(calc.items[0]["price"], 1.0)
        self.assertEqual(calc.items[0]["quantity"], 2)

    def test_add_item_same_name_price_increments_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Apple", 1.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]["quantity"], 5)

    def test_add_item_quantity_default(self):
        calc = OrderCalculator()
        calc.add_item("Banana", 0.5)
        self.assertEqual(calc.items[0]["quantity"], 1)

    def test_add_item_empty_name_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("", 1.0)

    def test_add_item_price_zero_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 0.0)

    def test_add_item_price_negative_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Apple", -1.0)

    def test_add_item_quantity_zero_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 1.0, 0)

    def test_add_item_quantity_negative_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 1.0, -2)

    def test_add_item_same_name_different_price_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 1.5)

    def test_add_item_non_string_name_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_non_numeric_price_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Apple", "1.0")

    def test_add_item_non_integer_quantity_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Apple", 1.0, 2.5)

    def test_add_item_after_clear_order(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.clear_order()
        calc.add_item("Banana", 0.5, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]["name"], "Banana")
        self.assertEqual(calc.items[0]["quantity"], 2)

    def test_remove_item_existing_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.remove_item("Apple")
        self.assertEqual(calc.items, [])

    def test_remove_item_last_item_order_empty(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.remove_item("Apple")
        self.assertTrue(calc.is_empty())

    def test_remove_item_non_existent_name_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        with self.assertRaises(ValueError):
            calc.remove_item("Banana")

    def test_remove_item_non_string_name_raises_type_error(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_removes_entry_regardless_of_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 4)
        calc.remove_item("Apple")
        self.assertEqual(calc.items, [])

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Banana", 0.5, 3)
        self.assertEqual(calc.get_subtotal(), 2.0*1.0 + 3*0.5)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 5)
        self.assertEqual(calc.get_subtotal(), 5.0)

    def test_get_subtotal_fractional_prices(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 0.33, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 0.99)

    def test_get_subtotal_empty_order_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_after_clear_order_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_twenty_percent(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_hundred_percent(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_subtotal_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_negative_subtotal_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_discount_negative_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_greater_than_one_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.2)

    def test_apply_discount_non_numeric_inputs_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount("100", 0.1)
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, "0.1")

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_at_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(99.9), 10.0)

    def test_calculate_shipping_zero_subtotal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_non_numeric_input_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping("100")

    def test_calculate_shipping_negative_subtotal_returns_shipping_cost(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(-5.0), 10.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_normal_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_fractional_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(10.5), 2.415)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_non_numeric_amount_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax("100")

    def test_calculate_total_typical_order(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Banana", 0.5, 1)
        total = calc.calculate_total(discount=0.1)
        expected_subtotal = 2*1.0 + 1*0.5
        discounted = expected_subtotal * 0.9
        shipping = 10.0  # below threshold
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item("Expensive", 120.0, 1)
        total = calc.calculate_total(discount=0.0)
        expected_subtotal = 120.0
        shipping = 0.0  # free shipping
        tax = expected_subtotal * 0.23
        expected = expected_subtotal + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_no_discount_argument(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 1)
        total = calc.calculate_total()
        expected_subtotal = 10.0
        shipping = 10.0
        tax = (expected_subtotal + shipping) * 0.23
        expected = expected_subtotal + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_empty_order_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_discount_negative_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.1)

    def test_calculate_total_discount_greater_than_one_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.2)

    def test_calculate_total_discount_non_numeric_raises_type_error(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount="0.1")

    def test_calculate_total_negative_subtotal_raises_value_error(self):
        class Subcalc(OrderCalculator):
            def get_subtotal(self):
                return -5.0
        calc = Subcalc()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_uses_instance_parameters(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=200.0, shipping_cost=5.0)
        calc.add_item("Item", 50.0, 2)  # subtotal 100
        total = calc.calculate_total(discount=0.0)
        expected_subtotal = 100.0
        shipping = 5.0  # below threshold
        tax = (expected_subtotal + shipping) * 0.1
        expected = expected_subtotal + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_total_items_empty_order(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 7)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Banana", 0.5, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_clear_order(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_add_then_remove_some(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 4)
        calc.add_item("Banana", 0.5, 2)
        calc.remove_item("Apple")
        self.assertEqual(calc.total_items(), 2)

    def test_clear_order_non_empty_order(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.clear_order()
        self.assertEqual(calc.items, [])
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_already_empty_order(self):
        calc = OrderCalculator()
        calc.clear_order()  # should not raise
        self.assertEqual(calc.items, [])

    def test_clear_order_then_add_item_works_fresh(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.clear_order()
        calc.add_item("Banana", 2.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]["name"], "Banana")
        self.assertEqual(calc.items[0]["price"], 2.0)
        self.assertEqual(calc.items[0]["quantity"], 3)

    def test_list_items_empty_order(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_one_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        self.assertEqual(calc.list_items(), ["Apple"])

    def test_list_items_multiple_distinct_items(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.add_item("Banana", 0.5)
        calc.add_item("Cherry", 2.0)
        self.assertEqual(sorted(calc.list_items()), sorted(["Apple", "Banana", "Cherry"]))

    def test_list_items_same_item_added_multiple_times(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Apple", 1.0, 3)
        self.assertEqual(calc.list_items(), ["Apple"])

    def test_list_items_after_remove_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.add_item("Banana", 0.5)
        calc.remove_item("Apple")
        self.assertEqual(calc.list_items(), ["Banana"])

    def test_list_items_after_clear_order(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_is_empty_no_items(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_at_least_one_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_clear_order(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_removing_last_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.remove_item("Apple")
        self.assertTrue(calc.is_empty())