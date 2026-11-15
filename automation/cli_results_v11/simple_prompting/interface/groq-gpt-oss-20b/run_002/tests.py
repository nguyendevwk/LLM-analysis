import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    # ---------- add_item ----------
    def test_add_item_valid(self):
        self.calc.add_item("apple", 1.5, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertIn("apple", self.calc.list_items())

    def test_add_item_default_quantity(self):
        self.calc.add_item("banana", 0.5)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("orange", "1.0", 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("orange", 1.0, "2")

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("pear", 1.0, -3)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("pear", 1.0, 0)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("pear", -1.0, 1)

    # ---------- remove_item ----------
    def test_remove_item_existing(self):
        self.calc.add_item("apple", 1.0, 3)
        self.calc.remove_item("apple")
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item("nonexistent")

    def test_remove_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    # ---------- get_subtotal ----------
    def test_get_subtotal_empty(self):
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item("a", 2.0, 2)   # 4.0
        self.calc.add_item("b", 3.5, 1)   # 3.5
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.5)

    # ---------- apply_discount ----------
    def test_apply_discount_less_than_subtotal(self):
        subtotal = 10.0
        discount = 3.0
        result = self.calc.apply_discount(subtotal, discount)
        self.assertAlmostEqual(result, 7.0)

    def test_apply_discount_equal_to_subtotal(self):
        subtotal = 5.0
        discount = 5.0
        result = self.calc.apply_discount(subtotal, discount)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_greater_than_subtotal(self):
        subtotal = 4.0
        discount = 10.0
        result = self.calc.apply_discount(subtotal, discount)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -2.0)

    # ---------- calculate_shipping ----------
    def test_calculate_shipping_free(self):
        discounted_subtotal = 120.0
        shipping = self.calc.calculate_shipping(discounted_subtotal)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_nonfree(self):
        discounted_subtotal = 80.0
        shipping = self.calc.calculate_shipping(discounted_subtotal)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_at_threshold(self):
        discounted_subtotal = 100.0
        shipping = self.calc.calculate_shipping(discounted_subtotal)
        self.assertAlmostEqual(shipping, 0.0)

    # ---------- calculate_tax ----------
    def test_calculate_tax_positive_amount(self):
        amount = 100.0
        tax = self.calc.calculate_tax(amount)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    # ---------- calculate_total ----------
    def test_calculate_total_no_discount(self):
        self.calc.add_item("x", 50.0, 1)
        self.calc.add_item("y", 30.0, 1)
        # subtotal = 80.0, shipping = 10.0, tax = 23.0
        total = self.calc.calculate_total()
        expected = 80.0 + 10.0 + 23.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item("x", 50.0, 1)
        self.calc.add_item("y", 30.0, 1)
        # subtotal = 80.0, discount = 20.0 -> discounted = 60.0
        # shipping = 10.0, tax = 13.8
        total = self.calc.calculate_total(discount=20.0)
        expected = 60.0 + 10.0 + 13.8
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_exceeds_subtotal(self):
        self.calc.add_item("x", 10.0, 1)
        total = self.calc.calculate_total(discount=20.0)
        # discounted_subtotal = 0, shipping = 10.0, tax = 0
        expected = 10.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-5.0)

    # ---------- total_items ----------
    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_multiple(self):
        self.calc.add_item("a", 1.0, 2)
        self.calc.add_item("b", 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    # ---------- clear_order ----------
    def test_clear_order(self):
        self.calc.add_item("a", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.total_items(), 0)

    # ---------- list_items ----------
    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_multiple(self):
        self.calc.add_item("a", 1.0, 1)
        self.calc.add_item("b", 2.0, 1)
        self.assertEqual(self.calc.list_items(), ["a", "b"])

    # ---------- is_empty ----------
    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item("a", 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item("a", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    # ---------- edge cases ----------
    def test_add_item_duplicate_name_accumulates_quantity(self):
        self.calc.add_item("dup", 2.0, 1)
        self.calc.add_item("dup", 2.0, 2)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0)

    def test_remove_item_partial_quantity_not_supported(self):
        # Assuming remove_item removes entire entry
        self.calc.add_item("partial", 5.0, 3)
        self.calc.remove_item("partial")
        self.assertTrue(self.calc.is_empty())

    def test_calculate_total_no_items(self):
        total = self.calc.calculate_total()
        # No items: subtotal 0, shipping 0 (threshold not met), tax 0
        self.assertAlmostEqual(total, 0.0)

    def test_calculate_shipping_no_items(self):
        shipping = self.calc.calculate_shipping(0.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_tax_no_items(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)


if __name__ == "__main__":
    unittest.main()