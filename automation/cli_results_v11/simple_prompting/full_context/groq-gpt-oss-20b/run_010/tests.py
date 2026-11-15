import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    # ---------- __init__ ----------
    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")

    def test_init_invalid_tax_rate_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    def test_init_invalid_free_shipping_threshold_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    def test_init_invalid_shipping_cost_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    # ---------- add_item ----------
    def test_add_item_new(self):
        self.calc.add_item("Apple", 1.5, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]["quantity"], 2)

    def test_add_item_increment(self):
        self.calc.add_item("Apple", 1.5, 2)
        self.calc.add_item("Apple", 1.5, 3)
        self.assertEqual(self.calc.items[0]["quantity"], 5)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item("Apple", 1.5, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 2.0, 1)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("Apple", "1.0", 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("Apple", 1.0, 1.5)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 1.0, 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", -1.0, 1)

    def test_add_item_zero_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 0.0, 1)

    def test_add_item_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 1.0, 0)

    # ---------- remove_item ----------
    def test_remove_item_existing(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.remove_item("Apple")
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("Banana")

    def test_remove_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    # ---------- get_subtotal ----------
    def test_get_subtotal_normal(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.add_item("Banana", 0.5, 4)
        subtotal = self.calc.get_subtotal()
        self.assertAlmostEqual(subtotal, 1.0 * 2 + 0.5 * 4)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    # ---------- apply_discount ----------
    def test_apply_discount_normal(self):
        result = self.calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(result, 50.0)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(75.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_invalid_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.5)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.2)

    def test_apply_discount_invalid_subtotal_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100", 0.2)

    def test_apply_discount_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, "0.2")

    # ---------- calculate_shipping ----------
    def test_calculate_shipping_free(self):
        shipping = self.calc.calculate_shipping(120.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_paid(self):
        shipping = self.calc.calculate_shipping(80.0)
        self.assertEqual(shipping, self.calc.shipping_cost)

    def test_calculate_shipping_exact_threshold(self):
        shipping = self.calc.calculate_shipping(self.calc.free_shipping_threshold)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("80")

    # ---------- calculate_tax ----------
    def test_calculate_tax_normal(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 100.0 * self.calc.tax_rate)

    def test_calculate_tax_zero(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("100")

    # ---------- calculate_total ----------
    def test_calculate_total_no_discount(self):
        self.calc.add_item("Apple", 10.0, 2)  # subtotal 20
        total = self.calc.calculate_total()
        expected = 20.0 + self.calc.shipping_cost + self.calc.calculate_tax(20.0 + self.calc.shipping_cost)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item("Apple", 10.0, 2)  # subtotal 20
        total = self.calc.calculate_total(discount=0.5)  # discounted 10
        shipping = self.calc.calculate_shipping(10.0)
        tax = self.calc.calculate_tax(10.0 + shipping)
        expected = 10.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item("Apple", 60.0, 2)  # subtotal 120
        total = self.calc.calculate_total(discount=0.0)
        shipping = self.calc.calculate_shipping(120.0)
        tax = self.calc.calculate_tax(120.0 + shipping)
        expected = 120.0 + shipping + tax
        self.assertAlmostEqual(total, expected)
        self.assertEqual(shipping, 0.0)

    def test_calculate_total_full_discount(self):
        self.calc.add_item("Apple", 10.0, 2)  # subtotal 20
        total = self.calc.calculate_total(discount=1.0)  # discounted 0
        shipping = self.calc.calculate_shipping(0.0)
        tax = self.calc.calculate_tax(0.0 + shipping)
        expected = 0.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount="0.2")

    def test_calculate_total_invalid_discount_value(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.5)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    # ---------- total_items ----------
    def test_total_items(self):
        self.calc.add_item("Apple", 1.0, 3)
        self.calc.add_item("Banana", 0.5, 2)
        self.assertEqual(self.calc.total_items(), 5)

    # ---------- clear_order ----------
    def test_clear_order(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(len(self.calc.items), 0)

    # ---------- list_items ----------
    def test_list_items(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.add_item("Banana", 0.5, 2)
        self.calc.add_item("Apple", 1.0, 3)
        items = self.calc.list_items()
        self.assertCountEqual(items, ["Apple", "Banana"])

    # ---------- is_empty ----------
    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.assertFalse(self.calc.is_empty())


if __name__ == "__main__":
    unittest.main()