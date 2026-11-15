import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    def test_default_initialization(self):
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_add_item_basic(self):
        self.calc.add_item("apple", 1.5)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 1)
        self.assertIn("apple", self.calc.list_items())
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.5)

    def test_add_item_multiple_quantities(self):
        self.calc.add_item("banana", 0.5, quantity=3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.5)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("orange", "1.0")

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("orange", 1.0, quantity="2")

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("pear", -2.0)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("pear", 2.0, quantity=0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("pear", 2.0, quantity=-1)

    def test_remove_item_existing(self):
        self.calc.add_item("grape", 2.0)
        self.calc.remove_item("grape")
        self.assertFalse("grape" in self.calc.list_items())
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        # Should not raise an exception
        try:
            self.calc.remove_item("nonexistent")
        except Exception as e:
            self.fail(f"remove_item raised an exception on nonexistent item: {e}")

    def test_remove_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_empty(self):
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    def test_get_subtotal_with_items(self):
        self.calc.add_item("item1", 10.0, quantity=2)
        self.calc.add_item("item2", 5.0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 25.0)

    def test_apply_discount_valid(self):
        subtotal = 50.0
        discounted = self.calc.apply_discount(subtotal, 5.0)
        self.assertAlmostEqual(discounted, 45.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        discounted_subtotal = 50.0
        shipping = self.calc.calculate_shipping(discounted_subtotal)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_above_threshold(self):
        discounted_subtotal = 150.0
        shipping = self.calc.calculate_shipping(discounted_subtotal)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_tax(self):
        amount = 100.0
        tax = self.calc.calculate_tax(amount)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_total_no_discount(self):
        self.calc.add_item("item", 20.0, quantity=2)  # subtotal 40
        total = self.calc.calculate_total()
        expected = 40.0 + 10.0 + 9.2  # shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item("item", 20.0, quantity=2)  # subtotal 40
        total = self.calc.calculate_total(discount=5.0)
        discounted = 35.0
        expected = discounted + 10.0 + 8.05
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_greater_than_subtotal(self):
        self.calc.add_item("item", 10.0, quantity=1)  # subtotal 10
        total = self.calc.calculate_total(discount=15.0)
        discounted = -5.0
        expected = discounted + 10.0 + -1.15
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-5.0)

    def test_total_items(self):
        self.calc.add_item("a", 1.0, quantity=3)
        self.calc.add_item("b", 2.0, quantity=2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order(self):
        self.calc.add_item("x", 5.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items(self):
        self.calc.add_item("first", 1.0)
        self.calc.add_item("second", 2.0)
        items = self.calc.list_items()
        self.assertIn("first", items)
        self.assertIn("second", items)
        self.assertEqual(len(items), 2)

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item("item", 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_total_items_zero(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_get_subtotal_zero_price(self):
        self.calc.add_item("free", 0.0, quantity=5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    def test_add_item_zero_price_allowed(self):
        self.calc.add_item("free", 0.0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertIn("free", self.calc.list_items())


if __name__ == "__main__":
    unittest.main()