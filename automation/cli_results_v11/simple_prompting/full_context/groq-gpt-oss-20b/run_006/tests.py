import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    # Constructor validation
    def test_constructor_valid_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    def test_constructor_valid_custom(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_constructor_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")

    def test_constructor_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    def test_constructor_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    def test_constructor_tax_rate_out_of_range_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_constructor_tax_rate_out_of_range_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_constructor_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_constructor_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    # add_item tests
    def test_add_item_basic(self):
        self.calc.add_item("Apple", 1.5, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]["quantity"], 2)

    def test_add_item_default_quantity(self):
        self.calc.add_item("Banana", 0.5)
        self.assertEqual(self.calc.items[0]["quantity"], 1)

    def test_add_item_merge_same_name_and_price(self):
        self.calc.add_item("Orange", 0.8, 3)
        self.calc.add_item("Orange", 0.8, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]["quantity"], 5)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item("Grapes", 2.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("Grapes", 3.0, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 1.0, 1)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Pear", 1.0, 0)

    def test_add_item_zero_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Peach", 0.0, 1)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("Mango", "1.0", 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("Mango", 1.0, 1.5)

    # remove_item tests
    def test_remove_item_success(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.remove_item("Apple")
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_multiple(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.remove_item("Apple")
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_not_found(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("Nonexistent")

    def test_remove_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    # get_subtotal tests
    def test_get_subtotal_basic(self):
        self.calc.add_item("Apple", 1.0, 3)
        self.calc.add_item("Banana", 0.5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0 * 3 + 0.5 * 2)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    # apply_discount tests
    def test_apply_discount_basic(self):
        result = self.calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_zero_discount(self):
        result = self.calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(result, 50.0)

    def test_apply_discount_full_discount(self):
        result = self.calc.apply_discount(50.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, "0.1")

    def test_apply_discount_invalid_subtotal_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100.0", 0.1)

    def test_apply_discount_discount_out_of_range_low(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_out_of_range_high(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.5)

    # calculate_shipping tests
    def test_calculate_shipping_free(self):
        self.calc.free_shipping_threshold = 50.0
        self.assertEqual(self.calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_non_free(self):
        self.calc.free_shipping_threshold = 50.0
        self.calc.shipping_cost = 7.5
        self.assertEqual(self.calc.calculate_shipping(30.0), 7.5)

    def test_calculate_shipping_boundary(self):
        self.calc.free_shipping_threshold = 100.0
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("100.0")

    # calculate_tax tests
    def test_calculate_tax_basic(self):
        self.calc.tax_rate = 0.2
        self.assertAlmostEqual(self.calc.calculate_tax(50.0), 10.0)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("50.0")

    # calculate_total tests
    def test_calculate_total_no_discount(self):
        self.calc.add_item("Item1", 20.0, 2)  # subtotal 40
        total = self.calc.calculate_total()
        expected = 40.0 + 10.0 + 10.0 * 0.23  # shipping 10, tax 23%
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item("Item1", 50.0, 1)  # subtotal 50
        total = self.calc.calculate_total(discount=0.5)  # discounted 25
        expected = 25.0 + 10.0 + 10.0 * 0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item("Item1", 120.0, 1)  # subtotal 120
        total = self.calc.calculate_total(discount=0.0)
        expected = 120.0 + 0.0 + 120.0 * 0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_full_discount(self):
        self.calc.add_item("Item1", 30.0, 1)
        total = self.calc.calculate_total(discount=1.0)
        expected = 0.0 + 10.0 + 10.0 * 0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount="0.1")

    def test_calculate_total_invalid_discount_value_low(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)

    def test_calculate_total_invalid_discount_value_high(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.5)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    # total_items tests
    def test_total_items_basic(self):
        self.calc.add_item("A", 1.0, 2)
        self.calc.add_item("B", 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    # clear_order tests
    def test_clear_order(self):
        self.calc.add_item("A", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(len(self.calc.items), 0)

    # list_items tests
    def test_list_items_unique(self):
        self.calc.add_item("A", 1.0, 1)
        self.calc.add_item("B", 2.0, 1)
        self.calc.add_item("A", 1.0, 2)
        items = self.calc.list_items()
        self.assertCountEqual(items, ["A", "B"])

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    # is_empty tests
    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item("A", 1.0, 1)
        self.assertFalse(self.calc.is_empty())


if __name__ == "__main__":
    unittest.main()