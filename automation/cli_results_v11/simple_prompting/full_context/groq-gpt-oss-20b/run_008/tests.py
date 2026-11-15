import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    # ---------- __init__ ----------
    def test_init_default_values(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

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
    def test_add_item_normal(self):
        self.calc.add_item("Apple", 1.0, 3)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]["quantity"], 3)

    def test_add_item_increment_quantity(self):
        self.calc.add_item("Apple", 1.0, 3)
        self.calc.add_item("Apple", 1.0, 2)
        self.assertEqual(self.calc.items[0]["quantity"], 5)

    def test_add_item_duplicate_name_different_price(self):
        self.calc.add_item("Apple", 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 2.0, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 1.0, 1)

    def test_add_item_invalid_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", -1, 1)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 1.0, 0)
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 1.0, -1)

    def test_add_item_invalid_types(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item("Apple", "1.0", 1)
        with self.assertRaises(TypeError):
            self.calc.add_item("Apple", 1.0, 1.5)

    # ---------- remove_item ----------
    def test_remove_item_existing(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.add_item("Banana", 0.5, 2)
        self.calc.remove_item("Apple")
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]["name"], "Banana")

    def test_remove_item_non_existing(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("NonExistent")

    def test_remove_item_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    # ---------- get_subtotal ----------
    def test_get_subtotal_normal(self):
        self.calc.add_item("Apple", 1.0, 3)
        self.calc.add_item("Banana", 0.5, 4)
        expected = 1.0 * 3 + 0.5 * 4
        self.assertAlmostEqual(self.calc.get_subtotal(), expected)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    # ---------- apply_discount ----------
    def test_apply_discount_normal(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.2)

    def test_apply_discount_invalid_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.1)

    def test_apply_discount_invalid_types(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100", 0.2)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, "0.2")

    # ---------- calculate_shipping ----------
    def test_calculate_shipping_free(self):
        self.assertEqual(self.calc.calculate_shipping(120.0), 0.0)

    def test_calculate_shipping_paid(self):
        self.assertEqual(self.calc.calculate_shipping(80.0), self.calc.shipping_cost)

    def test_calculate_shipping_boundary(self):
        self.assertEqual(self.calc.calculate_shipping(self.calc.free_shipping_threshold), 0.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("80")

    # ---------- calculate_tax ----------
    def test_calculate_tax_normal(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("100")

    # ---------- calculate_total ----------
    def test_calculate_total_no_discount_free_shipping(self):
        self.calc.add_item("Item", 50.0, 2)  # subtotal 100
        total = self.calc.calculate_total(discount=0.0)
        expected = 100.0 + 0.0 + self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_and_shipping(self):
        self.calc.add_item("Apple", 50.0, 1)
        self.calc.add_item("Banana", 30.0, 2)  # subtotal 110
        total = self.calc.calculate_total(discount=0.2)
        discounted = 110.0 * 0.8  # 88
        shipping = self.calc.shipping_cost  # 10
        tax = discounted + shipping
        tax = self.calc.calculate_tax(tax)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_full_discount(self):
        self.calc.add_item("Item", 100.0, 1)
        total = self.calc.calculate_total(discount=1.0)
        discounted = 0.0
        shipping = self.calc.shipping_cost
        tax = self.calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_invalid_discount(self):
        self.calc.add_item("Item", 10.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.1)

    def test_calculate_total_invalid_type(self):
        self.calc.add_item("Item", 10.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount="0.2")

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
    def test_list_items_unique(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.add_item("Banana", 0.5, 1)
        self.calc.add_item("Apple", 1.0, 2)
        items = self.calc.list_items()
        self.assertCountEqual(items, ["Apple", "Banana"])

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    # ---------- is_empty ----------
    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())


if __name__ == "__main__":
    unittest.main()