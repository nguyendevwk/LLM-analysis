import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def test_ctor_typical(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_ctor_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_ctor_tax_rate_low_boundary(self):
        calc = OrderCalculator(0.0, 100.0, 10.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_ctor_tax_rate_high_boundary(self):
        calc = OrderCalculator(1.0, 100.0, 10.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_ctor_tax_rate_below_zero(self):
        with self.assertRaises(ValueError):
            OrderCalculator(-0.01, 100.0, 10.0)

    def test_ctor_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(1.01, 100.0, 10.0)

    def test_ctor_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator("0.23", 100.0, 10.0)

    def test_ctor_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(0.23, -5.0, 10.0)

    def test_ctor_free_shipping_threshold_zero(self):
        calc = OrderCalculator(0.23, 0.0, 10.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_ctor_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(0.23, "100", 10.0)

    def test_ctor_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(0.23, 100.0, -2.0)

    def test_ctor_shipping_cost_zero(self):
        calc = OrderCalculator(0.23, 100.0, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_ctor_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(0.23, 100.0, None)

    def test_ctor_mixed_types(self):
        calc = OrderCalculator(23, 100, 10)
        self.assertEqual(calc.tax_rate, 23)
        self.assertEqual(calc.free_shipping_threshold, 100)
        self.assertEqual(calc.shipping_cost, 10)

    def test_add_item_typical(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 0.5, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]["name"], "Apple")
        self.assertEqual(calc.items[0]["price"], 0.5)
        self.assertEqual(calc.items[0]["quantity"], 3)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Banana", 0.8)
        self.assertEqual(calc.items[0]["quantity"], 1)

    def test_add_item_same_name_same_price_merge(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 0.5, 2)
        calc.add_item("Apple", 0.5, 4)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]["quantity"], 6)

    def test_add_item_same_name_different_price_error(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 0.5, 1)
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 0.6, 2)

    def test_add_item_empty_name_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("", 0.5, 1)

    def test_add_item_non_string_name_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 0.5, 1)

    def test_add_item_price_zero_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Item", 0, 1)

    def test_add_item_negative_price_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Item", -5.0, 1)

    def test_add_item_price_wrong_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Item", "10", 1)

    def test_add_item_quantity_less_than_one_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Item", 0.5, 0)
        with self.assertRaises(ValueError):
            calc.add_item("Item", 0.5, -2)

    def test_add_item_quantity_wrong_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Item", 0.5, 2.5)

    def test_add_item_multiple_different_items(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 1)
        calc.add_item("B", 2.0, 2)
        calc.add_item("C", 3.0, 3)
        self.assertEqual(len(calc.items), 3)
        names = {item["name"] for item in calc.items}
        self.assertEqual(names, {"A", "B", "C"})

    def test_add_item_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Big", 1.0, 10**6)
        self.assertEqual(calc.items[0]["quantity"], 10**6)

    def test_add_item_float_price(self):
        calc = OrderCalculator()
        calc.add_item("Precise", 0.999999, 1)
        self.assertEqual(calc.items[0]["price"], 0.999999)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item("ToRemove", 5.0, 2)
        calc.remove_item("ToRemove")
        self.assertEqual(calc.items, [])

    def test_remove_item_non_existing_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item("Ghost")

    def test_remove_item_wrong_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_after_quantity_merge(self):
        calc = OrderCalculator()
        calc.add_item("Same", 1.0, 3)
        calc.add_item("Same", 1.0, 2)
        calc.remove_item("Same")
        self.assertEqual(calc.items, [])

    def test_remove_item_case_sensitivity(self):
        calc = OrderCalculator()
        calc.add_item("Book", 10.0, 1)
        with self.assertRaises(ValueError):
            calc.remove_item("book")

    def test_remove_item_empty_string_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item("")

    def test_remove_item_after_clear_error(self):
        calc = OrderCalculator()
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.remove_item("Any")

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 2)
        self.assertEqual(calc.get_subtotal(), 20.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item("A", 4.0, 3)
        calc.add_item("B", 5.0, 2)
        self.assertEqual(calc.get_subtotal(), 4.0*3 + 5.0*2)

    def test_get_subtotal_empty_order_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_after_remove_all_error(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 1)
        calc.remove_item("A")
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item("Big", 1e6, 2e6)
        self.assertEqual(calc.get_subtotal(), 1e6 * 2e6)

    def test_get_subtotal_float_precision(self):
        calc = OrderCalculator()
        calc.add_item("A", 0.1, 1)
        calc.add_item("B", 0.2, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3, places=7)

    def test_apply_discount_typical(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero_discount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_out_of_range_low(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.01)

    def test_apply_discount_out_of_range_high(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.01)

    def test_apply_discount_negative_subtotal_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_subtotal_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_wrong_type_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount("100", 0.2)

    def test_apply_discount_wrong_type_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, "0.2")

    def test_apply_discount_integer_inputs_valid(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(50, 0), 50.0)

    def test_apply_discount_integer_discount_gt_one_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50, 10)

    def test_calculate_shipping_free_threshold_met(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_free_threshold_exact(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        self.assertEqual(calc.calculate_shipping(80.0), 10.0)

    def test_calculate_shipping_zero_shipping_cost(self):
        calc = OrderCalculator(0.23, 100.0, 0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_negative_input(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        self.assertEqual(calc.calculate_shipping(-5.0), 10.0)

    def test_calculate_shipping_wrong_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping("100")

    def test_calculate_shipping_discounted_subtotal_zero(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_threshold_zero(self):
        calc = OrderCalculator(0.23, 0.0, 10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_tax_typical(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        self.assertEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount_error(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_wrong_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax("100")

    def test_calculate_tax_rate_zero(self):
        calc = OrderCalculator(0.0, 100.0, 10.0)
        self.assertEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_rate_one(self):
        calc = OrderCalculator(1.0, 100.0, 10.0)
        self.assertEqual(calc.calculate_tax(100.0), 100.0)

    def test_calculate_tax_float_amount(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        self.assertAlmostEqual(calc.calculate_tax(33.33), 33.33 * 0.23, places=7)

    def test_calculate_total_no_discount(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        calc.add_item("Book", 50.0, 2)
        expected = 100.0 + 0.0 + 23.0
        self.assertEqual(calc.calculate_total(), expected)

    def test_calculate_total_with_discount(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        calc.add_item("Book", 50.0, 2)
        expected = 90.0 + 10.0 + 23.0
        self.assertEqual(calc.calculate_total(0.1), expected)

    def test_calculate_total_free_shipping_qualifies_after_discount(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        calc.add_item("Item", 100.0, 2)
        expected = 100.0 + 0.0 + 23.0
        self.assertEqual(calc.calculate_total(0.5), expected)

    def test_calculate_total_no_free_shipping_after_discount(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        calc.add_item("Item", 80.0, 1)
        expected = 72.0 + 10.0 + (0.23 * 82.0)
        self.assertAlmostEqual(calc.calculate_total(0.1), expected, places=7)

    def test_calculate_total_empty_order_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_invalid_discount_type_error(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total("0.1")

    def test_calculate_total_discount_out_of_range_error(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.2)
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)

    def test_calculate_total_tax_base_verification(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        calc.add_item("A", 50.0, 1)
        tax_expected = 60.0 * 0.23
        total_expected = 50.0 + 10.0 + tax_expected
        self.assertAlmostEqual(calc.calculate_total(), total_expected, places=7)

    def test_calculate_total_rounding_floating_point(self):
        calc = OrderCalculator(0.23, 100.0, 10.0)
        calc.add_item("A", 0.1, 3)
        expected = 0.3 + 10.0 + (10.3 * 0.23)
        self.assertAlmostEqual(calc.calculate_total(), expected, places=7)

    def test_calculate_total_zero_shipping_cost(self):
        calc = OrderCalculator(0.23, 100.0, 0.0)
        calc.add_item("A", 50.0, 1)
        expected = 50.0 + 0.0 + (50.0 * 0.23)
        self.assertEqual(calc.calculate_total(), expected)

    def test_calculate_total_zero_free_shipping_threshold(self):
        calc = OrderCalculator(0.23, 0.0, 10.0)
        calc.add_item("A", 50.0, 1)
        expected = 50.0 + 0.0 + (50.0 * 0.23)
        self.assertEqual(calc.calculate_total(), expected)

    def test_calculate_total_both_zero(self):
        calc = OrderCalculator(0.23, 0.0, 0.0)
        calc.add_item("A", 50.0, 1)
        expected = 50.0 + 0.0 + (50.0 * 0.23)
        self.assertEqual(calc.calculate_total(), expected)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item("Item", 1.0, 7)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 2)
        calc.add_item("B", 1.0, 5)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_after_add_remove(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 4)
        calc.add_item("B", 1.0, 3)
        calc.remove_item("A")
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Big", 1.0, 10**6)
        self.assertEqual(calc.total_items(), 10**6)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 5)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_non_empty_to_empty(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_reference_change(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 1)
        old_id = id(calc.items)
        calc.clear_order()
        new_id = id(calc.items)
        self.assertNotEqual(old_id, new_id)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        self.assertEqual(calc.list_items(), ["Apple"])

    def test_list_items_duplicate_name_same_price(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Apple", 1.0, 3)
        self.assertEqual(calc.list_items(), ["Apple"])

    def test_list_items_multiple_different_names(self):
        calc = OrderCalculator()
        calc.add_item("Book", 1.0, 1)
        calc.add_item("Pen", 1.0, 1)
        calc.add_item("Book", 1.0, 1)
        result = calc.list_items()
        self.assertCountEqual(result, ["Book", "Pen"])

    def test_list_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 1)
        calc.add_item("B", 1.0, 1)
        calc.remove_item("A")
        self.assertEqual(calc.list_items(), ["B"])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_case_sensitivity(self):
        calc = OrderCalculator()
        calc.add_item("book", 1.0, 1)
        calc.add_item("Book", 1.0, 1)
        result = calc.list_items()
        self.assertCountEqual(result, ["book", "Book"])

    def test_is_empty_true_when_empty(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_when_not_empty(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_add_then_remove_same_item(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 1)
        calc.remove_item("A")
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_sequence_resulting_zero(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 2)
        calc.add_item("B", 1.0, 3)
        calc.remove_item("A")
        calc.remove_item("B")
        self.assertTrue(calc.is_empty())