import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    def test_default_initialization(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(90.0), 10.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_add_item_typical(self):
        self.calc.add_item("apple", 1.5, 3)
        self.calc.add_item("banana", 0.5)
        self.assertEqual(self.calc.total_items(), 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.5 * 3 + 0.5)
        self.assertListEqual(sorted(self.calc.list_items()), ["apple", "banana"])

    def test_add_item_invalid_types(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item("item", "price", 1)
        with self.assertRaises(TypeError):
            self.calc.add_item("item", 1.0, "qty")

    def test_add_item_invalid_values(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("item", -1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("item", 1.0, 0)
        with self.assertRaises(ValueError):
            self.calc.add_item("item", 1.0, -2)

    def test_remove_item(self):
        self.calc.add_item("item", 2.0, 2)
        self.calc.remove_item("item")
        self.assertTrue(self.calc.is_empty())
        with self.assertRaises(Exception):
            self.calc.remove_item("item")

    def test_remove_item_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_empty(self):
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    def test_apply_discount(self):
        self.calc.add_item("item", 10.0, 1)
        subtotal = self.calc.get_subtotal()
        self.assertAlmostEqual(self.calc.apply_discount(subtotal, 2.0), subtotal - 2.0)
        self.assertAlmostEqual(self.calc.apply_discount(subtotal, subtotal + 5.0), 0.0)

    def test_calculate_tax(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200.0), 46.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_shipping(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(99.99), 10.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(150.0), 0.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_shipping(-5.0)

    def test_calculate_total_no_discount(self):
        self.calc.add_item("item", 20.0, 2)
        subtotal = self.calc.get_subtotal()
        shipping = self.calc.calculate_shipping(subtotal)
        tax = self.calc.calculate_tax(subtotal)
        expected_total = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected_total)

    def test_calculate_total_with_discount(self):
        self.calc.add_item("item", 50.0, 1)
        subtotal = self.calc.get_subtotal()
        discount = 10.0
        discounted_subtotal = self.calc.apply_discount(subtotal, discount)
        shipping = self.calc.calculate_shipping(discounted_subtotal)
        tax = self.calc.calculate_tax(discounted_subtotal)
        expected_total = discounted_subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(discount), expected_total)

    def test_calculate_total_discount_exceeds_subtotal(self):
        self.calc.add_item("item", 30.0, 1)
        subtotal = self.calc.get_subtotal()
        discount = subtotal + 20.0
        shipping = self.calc.calculate_shipping(0.0)
        tax = self.calc.calculate_tax(0.0)
        expected_total = shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(discount), expected_total)

    def test_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-5.0)

    def test_total_items_and_list_items(self):
        self.calc.add_item("a", 1.0, 2)
        self.calc.add_item("b", 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertListEqual(sorted(self.calc.list_items()), ["a", "b"])

    def test_is_empty_and_clear_order(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item("x", 5.0)
        self.assertFalse(self.calc.is_empty())
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertListEqual(self.calc.list_items(), [])

    def test_custom_initialization(self):
        custom_calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(custom_calc.calculate_tax(100.0), 10.0)
        self.assertAlmostEqual(custom_calc.calculate_shipping(49.99), 5.0)
        self.assertAlmostEqual(custom_calc.calculate_shipping(50.0), 0.0)

    def test_add_item_multiple_same_name(self):
        self.calc.add_item("dup", 5.0, 1)
        self.calc.add_item("dup", 5.0, 2)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5.0 * 3)

    def test_remove_item_partial_quantity(self):
        self.calc.add_item("partial", 3.0, 5)
        self.calc.remove_item("partial")
        self.assertTrue(self.calc.is_empty())

    def test_calculate_total_with_free_shipping(self):
        self.calc.add_item("expensive", 120.0, 1)
        subtotal = self.calc.get_subtotal()
        self.assertAlmostEqual(self.calc.calculate_shipping(subtotal), 0.0)
        expected_total = subtotal + self.calc.calculate_tax(subtotal)
        self.assertAlmostEqual(self.calc.calculate_total(), expected_total)

    def test_calculate_total_with_shipping_and_tax(self):
        self.calc.add_item("cheap", 10.0, 1)
        subtotal = self.calc.get_subtotal()
        shipping = self.calc.calculate_shipping(subtotal)
        tax = self.calc.calculate_tax(subtotal)
        expected_total = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected_total)

if __name__ == "__main__":
    unittest.main()