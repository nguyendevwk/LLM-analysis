import unittest

from order_calculator import OrderCalculator


class OrderCalculatorTests(unittest.TestCase):
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
        self.assertEqual(calc.items, [])

    def test_init_accepts_int_values(self):
        calc = OrderCalculator(tax_rate=0, free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(calc.tax_rate, 0)
        self.assertEqual(calc.free_shipping_threshold, 50)
        self.assertEqual(calc.shipping_cost, 5)

    def test_init_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_init_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_invalid_tax_rate_type_string(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")

    def test_init_invalid_tax_rate_type_none(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate=None)

    def test_init_invalid_free_shipping_threshold_type_string(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    def test_init_invalid_free_shipping_threshold_type_none(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_invalid_shipping_cost_type_string(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    def test_init_invalid_shipping_cost_type_none(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_init_tax_rate_below_zero(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1.0)

    def test_add_item_default_quantity(self):
        self.calc.add_item("A", 10.0)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10.0)

    def test_add_item_with_quantity(self):
        self.calc.add_item("A", 10.0, 3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 30.0)

    def test_add_item_same_name_same_price_increases_quantity(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.add_item("A", 10.0, 3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 50.0)
        self.assertCountEqual(self.calc.list_items(), ["A"])

    def test_add_item_same_name_different_price_raises(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(ValueError):
            self.calc.add_item("A", 20.0)

    def test_add_item_invalid_name_type_int(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(1, 10.0)

    def test_add_item_invalid_name_type_none(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(None, 10.0)

    def test_add_item_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 10.0)

    def test_add_item_invalid_price_type_string(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", "10.0")

    def test_add_item_invalid_price_type_none(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", None)

    def test_add_item_zero_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("A", 0.0)

    def test_add_item_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("A", -1.0)

    def test_add_item_invalid_quantity_type_float(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", 10.0, 1.5)

    def test_add_item_invalid_quantity_type_string(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", 10.0, "1")

    def test_add_item_invalid_quantity_type_none(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("A", 10.0, None)

    def test_add_item_zero_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("A", 10.0, 0)

    def test_add_item_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("A", 10.0, -1)

    def test_add_item_accepts_int_price(self):
        self.calc.add_item("A", 10)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10.0)

    def test_remove_item(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.calc.remove_item("A")
        self.assertCountEqual(self.calc.list_items(), ["B"])
        self.assertEqual(self.calc.total_items(), 1)

    def test_remove_item_from_empty_raises(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("A")

    def test_remove_item_nonexistent_raises(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(ValueError):
            self.calc.remove_item("B")

    def test_remove_item_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("")

    def test_remove_item_invalid_type_int(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(1)

    def test_remove_item_invalid_type_none(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(None)

    def test_get_subtotal_empty_raises(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_get_subtotal_single_item(self):
        self.calc.add_item("A", 10.0, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 20.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item("A", 10.0, 1)
        self.calc.add_item("B", 20.0, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 50.0)

    def test_apply_discount_no_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_partial_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.25), 75.0)

    def test_apply_discount_zero_subtotal(self):
        self.assertAlmostEqual(self.calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_accepts_int_values(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 0), 100.0)

    def test_apply_discount_negative_subtotal_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-1.0, 0.0)

    def test_apply_discount_discount_below_zero_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_above_one_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.1)

    def test_apply_discount_invalid_subtotal_type_string(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100", 0.0)

    def test_apply_discount_invalid_subtotal_type_none(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(None, 0.0)

    def test_apply_discount_invalid_discount_type_string(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, "0.2")

    def test_apply_discount_invalid_discount_type_none(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, None)

    def test_calculate_shipping_below_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_equal_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(100.01), 0.0)

    def test_calculate_shipping_custom_threshold_below(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.calculate_shipping(49.99), 5.0)

    def test_calculate_shipping_custom_threshold_equal(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertAlmostEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertAlmostEqual(calc.calculate_shipping(0.0), 0.0)

    def test_calculate_shipping_accepts_int_value(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(99), 10.0)

    def test_calculate_shipping_invalid_type_string(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("100")

    def test_calculate_shipping_invalid_type_none(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping(None)

    def test_calculate_tax_default_rate(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_custom_rate(self):
        calc = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 10.0)

    def test_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_full_rate(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 100.0)

    def test_calculate_tax_accepts_int_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100), 23.0)

    def test_calculate_tax_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-1.0)

    def test_calculate_tax_invalid_type_string(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("100")

    def test_calculate_tax_invalid_type_none(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax(None)

    def test_calculate_total_empty_order_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_below_threshold_no_discount(self):
        self.calc.add_item("A", 10.0)
        self.assertAlmostEqual(self.calc.calculate_total(), 24.6)

    def test_calculate_total_equal_threshold_no_discount(self):
        self.calc.add_item("A", 100.0)
        self.assertAlmostEqual(self.calc.calculate_total(), 123.0)

    def test_calculate_total_above_threshold_no_discount(self):
        self.calc.add_item("A", 200.0)
        self.assertAlmostEqual(self.calc.calculate_total(), 246.0)

    def test_calculate_total_with_discount(self):
        self.calc.add_item("A", 100.0)
        self.assertAlmostEqual(self.calc.calculate_total(0.25), 104.55)

    def test_calculate_total_full_discount(self):
        self.calc.add_item("A", 100.0)
        self.assertAlmostEqual(self.calc.calculate_total(1.0), 12.3)

    def test_calculate_total_multiple_items(self):
        self.calc.add_item("A", 10.0, 1)
        self.calc.add_item("B", 20.0, 2)
        self.assertAlmostEqual(self.calc.calculate_total(), 73.8)

    def test_calculate_total_custom_configuration(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item("A", 40.0)
        self.assertAlmostEqual(calc.calculate_total(), 49.5)

    def test_calculate_total_zero_threshold(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=0.0, shipping_cost=5.0)
        calc.add_item("A", 10.0)
        self.assertAlmostEqual(calc.calculate_total(), 11.0)

    def test_calculate_total_zero_shipping_cost(self):
        calc = OrderCalculator(tax_rate=0.1, shipping_cost=0.0)
        calc.add_item("A", 10.0)
        self.assertAlmostEqual(calc.calculate_total(), 11.0)

    def test_calculate_total_accepts_int_discount(self):
        self.calc.add_item("A", 10.0)
        self.assertAlmostEqual(self.calc.calculate_total(0), 24.6)

    def test_calculate_total_invalid_discount_type_string(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total("0.1")

    def test_calculate_total_invalid_discount_type_none(self):
        self.calc.add_item("A", 10.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(None)

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

    def test_total_items_single_item(self):
        self.calc.add_item("A", 10.0, 2)
        self.assertEqual(self.calc.total_items(), 2)

    def test_total_items_multiple_items(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.add_item("B", 20.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_merge(self):
        self.calc.add_item("A", 10.0, 1)
        self.calc.add_item("A", 10.0, 2)
        self.assertEqual(self.calc.total_items(), 3)

    def test_clear_order_removes_items(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.list_items(), [])

    def test_clear_order_empty(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_multiple(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.assertCountEqual(self.calc.list_items(), ["A", "B"])

    def test_list_items_no_duplicates_after_merge(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("A", 10.0)
        self.assertCountEqual(self.calc.list_items(), ["A"])

    def test_list_items_after_remove(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.calc.remove_item("A")
        self.assertEqual(self.calc.list_items(), ["B"])

    def test_list_items_after_clear(self):
        self.calc.add_item("A", 10.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_new(self):
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


if __name__ == "__main__":
    unittest.main()