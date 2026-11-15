import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = OrderCalculator()

    def test_init_default_values(self):
        self.assertEqual(self.calculator.tax_rate, 0.23)
        self.assertEqual(self.calculator.free_shipping_threshold, 100.0)
        self.assertEqual(self.calculator.shipping_cost, 10.0)
        self.assertEqual(self.calculator.items, [])

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_tax_rate_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_tax_rate_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.23")

    def test_init_free_shipping_threshold_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_init_free_shipping_threshold_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    def test_init_shipping_cost_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1.0)

    def test_init_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_shipping_cost_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    def test_add_item_basic(self):
        self.calculator.add_item("Apple", 1.5, 2)
        self.assertEqual(len(self.calculator.items), 1)
        self.assertEqual(self.calculator.items[0]["name"], "Apple")
        self.assertEqual(self.calculator.items[0]["price"], 1.5)
        self.assertEqual(self.calculator.items[0]["quantity"], 2)

    def test_add_item_default_quantity(self):
        self.calculator.add_item("Banana", 0.5)
        self.assertEqual(self.calculator.items[0]["quantity"], 1)

    def test_add_item_same_name_and_price_increments_quantity(self):
        self.calculator.add_item("Apple", 1.5, 2)
        self.calculator.add_item("Apple", 1.5, 3)
        self.assertEqual(len(self.calculator.items), 1)
        self.assertEqual(self.calculator.items[0]["quantity"], 5)

    def test_add_item_same_name_different_price_raises_value_error(self):
        self.calculator.add_item("Apple", 1.5)
        with self.assertRaises(ValueError):
            self.calculator.add_item("Apple", 2.0)

    def test_add_item_empty_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item("", 1.0)

    def test_add_item_zero_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item("Apple", 0.0)

    def test_add_item_negative_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item("Apple", -1.0)

    def test_add_item_zero_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item("Apple", 1.0, 0)

    def test_add_item_negative_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item("Apple", 1.0, -1)

    def test_add_item_non_string_name_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item(123, 1.0)

    def test_add_item_non_numeric_price_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item("Apple", "1.0")

    def test_add_item_non_integer_quantity_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item("Apple", 1.0, 1.5)

    def test_remove_item_existing(self):
        self.calculator.add_item("Apple", 1.5)
        self.calculator.remove_item("Apple")
        self.assertEqual(self.calculator.items, [])

    def test_remove_item_nonexistent_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.remove_item("Nonexistent")

    def test_remove_item_non_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.remove_item(123)

    def test_get_subtotal_single_item(self):
        self.calculator.add_item("Apple", 1.5, 2)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 3.0)

    def test_get_subtotal_multiple_items(self):
        self.calculator.add_item("Apple", 1.5, 2)
        self.calculator.add_item("Banana", 0.5, 4)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 5.0)

    def test_get_subtotal_empty_order_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.get_subtotal()

    def test_apply_discount_zero_discount(self):
        self.assertAlmostEqual(self.calculator.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        self.assertAlmostEqual(self.calculator.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_partial_discount(self):
        self.assertAlmostEqual(self.calculator.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_negative_subtotal_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(-10.0, 0.1)

    def test_apply_discount_negative_discount_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_above_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, 1.1)

    def test_apply_discount_non_numeric_subtotal_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount("100", 0.1)

    def test_apply_discount_non_numeric_discount_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount(100.0, "0.1")

    def test_calculate_shipping_above_threshold(self):
        self.assertAlmostEqual(self.calculator.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_below_threshold(self):
        self.assertAlmostEqual(self.calculator.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_exactly_at_threshold(self):
        self.assertAlmostEqual(self.calculator.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_zero(self):
        self.assertAlmostEqual(self.calculator.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_non_numeric_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_shipping("100")

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calculator.calculate_tax(0.0), 0.0)

    def test_calculate_tax_positive_amount(self):
        self.assertAlmostEqual(self.calculator.calculate_tax(100.0), 23.0)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_tax(-1.0)

    def test_calculate_tax_non_numeric_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_tax("100")

    def test_calculate_total_no_discount_below_threshold(self):
        self.calculator.add_item("Apple", 10.0, 1)
        total = self.calculator.calculate_total()
        expected_subtotal = 10.0
        expected_shipping = 10.0
        expected_tax = (expected_subtotal + expected_shipping)