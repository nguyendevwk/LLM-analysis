import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    # 1. __init__
    def test_init_default_parameters(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_init_custom_valid_parameters(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_out_of_range_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_out_of_range_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.23")

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    def test_init_tax_rate_zero_and_one(self):
        calc0 = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc0.tax_rate, 0.0)
        calc1 = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc1.tax_rate, 1.0)

    def test_init_threshold_zero_and_shipping_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(calc.free_shipping_threshold, 0)
        self.assertEqual(calc.shipping_cost, 0)

    # 2. add_item
    def test_add_item_basic(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.assertEqual(self.calc.total_items(), 2)

    def test_add_item_default_quantity(self):
        self.calc.add_item("Banana", 0.5)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_increment_same_name_price(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.add_item("Apple", 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item("Apple", 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 1.5, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 1.0, 1)

    def test_add_item_price_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 0, 1)

    def test_add_item_price_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", -2, 1)

    def test_add_item_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 1.0, 0)

    def test_add_item_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 1.0, -1)

    def test_add_item_name_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_price_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("Apple", "1.0", 1)

    def test_add_item_quantity_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("Apple", 1.0, 1.5)

    def test_add_item_price_as_int(self):
        self.calc.add_item("Apple", 2, 1)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_quantity_as_int(self):
        self.calc.add_item("Apple", 1.0, 4)
        self.assertEqual(self.calc.total_items(), 4)

    # 3. remove_item
    def test_remove_existing_item(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.remove_item("Apple")
        self.assertTrue(self.calc.is_empty())

    def test_remove_nonexistent_item(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("Orange")

    def test_remove_name_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_remove_from_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("Apple")

    # 4. get_subtotal
    def test_get_subtotal_with_items(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.add_item("Banana", 0.5, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.5, places=5)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_get_subtotal_after_removal(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.add_item("Banana", 0.5, 3)
        self.calc.remove_item("Apple")
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.5, places=5)

    # 5. apply_discount
    def test_apply_discount_no_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 0.0), 100, places=5)

    def test_apply_discount_full_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 1.0), 0, places=5)

    def test_apply_discount_half_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(200, 0.5), 100, places=5)

    def test_apply_discount_zero_subtotal(self):
        self.assertAlmostEqual(self.calc.apply_discount(0, 0.3), 0, places=5)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10, 0.2)

    def test_apply_discount_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, -0.1)

    def test_apply_discount_discount_above_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, 1.5)

    def test_apply_discount_wrong_type_subtotal(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100", 0.2)

    def test_apply_discount_wrong_type_discount(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, "0.2")

    # 6. calculate_shipping
    def test_calculate_shipping_free(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(120), 0.0, places=5)

    def test_calculate_shipping_paid(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(80), 10.0, places=5)

    def test_calculate_shipping_exact_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(100), 0.0, places=5)

    def test_calculate_shipping_negative_subtotal(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(-5), 10.0, places=5)

    def test_calculate_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("80")

    # 7. calculate_tax
    def test_calculate_tax_basic(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100), 23.0, places=5)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0), 0.0, places=5)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10)

    def test_calculate_tax_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("100")

    # 8. calculate_total
    def test_calculate_total_no_discount(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.add_item("Banana", 0.5, 3)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 16.605, places=5)

    def test_calculate_total_half_discount(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.add_item("Banana", 0.5, 3)
        total = self.calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 14.4525, places=5)

    def test_calculate_total_full_discount(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.add_item("Banana", 0.5, 3)
        total = self.calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 12.3, places=5)

    def test_calculate_total_full_discount_free_shipping(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=0, shipping_cost=10.0)
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Banana", 0.5, 3)
        total = calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 0.0, places=5)

    def test_calculate_total_discount_out_of_range_low(self):
        self.calc.add_item("Apple", 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-0.1)

    def test_calculate_total_discount_out_of_range_high(self):
        self.calc.add_item("Apple", 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.5)

    def test_calculate_total_wrong_type_discount(self):
        self.calc.add_item("Apple", 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total("0.2")

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_custom_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.1)
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Banana", 0.5, 3)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 14.85, places=5)

    def test_calculate_total_custom_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0)
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Banana", 0.5, 3)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 4.305, places=5)

    def test_calculate_total_custom_free_shipping_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0)
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Banana", 0.5, 3)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 4.305, places=5)

    def test_calculate_total_edge_threshold(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 10.0, 10)
        calc.add_item("Banana", 10.0, 10)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 123.0, places=5)

    def test_calculate_total_edge_threshold_below(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 9.999, 10)
        calc.add_item("Banana", 9.999, 10)
        total = calc.calculate_total(0.5)
        expected = 99.99 + 10 + (99.99 + 10) * 0.23
        self.assertAlmostEqual(total, expected, places=5)

    def test_calculate_total_edge_threshold_above(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 10.001, 10)
        calc.add_item("Banana", 10.001, 10)
        total = calc.calculate_total(0.5)
        expected = 100.01 + 0 + 100.01 * 0.23
        self.assertAlmostEqual(total, expected, places=5)

    # 9. total_items
    def test_total_items_multiple(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.add_item("Banana", 0.5, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_clear(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_after_removal(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.add_item("Banana", 0.5, 3)
        self.calc.remove_item("Apple")
        self.assertEqual(self.calc.total_items(), 3)

    # 10. clear_order
    def test_clear_order_resets_state(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_then_add_again(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.clear_order()
        self.calc.add_item("Banana", 0.5, 3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertIn("Banana", self.calc.list_items())

    # 11. list_items
    def test_list_items_unique_names(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.add_item("Banana", 0.5, 1)
        self.calc.add_item("Apple", 1.0, 1)
        items = self.calc.list_items()
        self.assertCountEqual(items, ["Apple", "Banana"])

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_after_clear(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    # 12. is_empty
    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_remove(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.add_item("Banana", 0.5, 1)
        self.calc.remove_item("Apple")
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_remove_all(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.add_item("Banana", 0.5, 1)
        self.calc.remove_item("Apple")
        self.calc.remove_item("Banana")
        self.assertTrue(self.calc.is_empty())

if __name__ == "__main__":
    unittest.main()