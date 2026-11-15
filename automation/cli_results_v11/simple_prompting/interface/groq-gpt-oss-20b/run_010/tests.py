import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_item_and_subtotal(self):
        self.calc.add_item("Apple", 1.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertEqual(self.calc.list_items(), ["Apple"])
        self.assertFalse(self.calc.is_empty())
        self.calc.add_item("Banana", 0.5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.0)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertEqual(self.calc.list_items(), ["Apple", "Banana"])

    def test_remove_item(self):
        self.calc.add_item("Apple", 1.0, 3)
        self.calc.add_item("Banana", 0.5, 2)
        self.calc.remove_item("Apple")
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertEqual(self.calc.list_items(), ["Banana"])
        self.assertFalse(self.calc.is_empty())
        self.calc.remove_item("Banana")
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.list_items(), [])
        self.assertTrue(self.calc.is_empty())

    def test_remove_nonexistent_item_raises(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item("Nonexistent")

    def test_clear_order(self):
        self.calc.add_item("Apple", 1.0, 3)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.list_items(), [])

    def test_apply_discount(self):
        subtotal = 10.0
        self.assertAlmostEqual(self.calc.apply_discount(subtotal, 2.0), 8.0)
        self.assertAlmostEqual(self.calc.apply_discount(subtotal, 10.0), 0.0)
        self.assertAlmostEqual(self.calc.apply_discount(subtotal, 12.0), 0.0)

    def test_apply_discount_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -1.0)

    def test_calculate_shipping(self):
        self.calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(99.99), 10.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(150.0), 0.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(-10.0), 10.0)

    def test_calculate_tax(self):
        self.calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_total(self):
        self.calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        self.calc.add_item("Apple", 10.0, 1)
        self.calc.add_item("Banana", 20.0, 1)
        subtotal = 30.0
        tax = subtotal * 0.23
        shipping = 10.0
        self.assertAlmostEqual(self.calc.calculate_total(0.0), subtotal + shipping + tax)
        self.assertAlmostEqual(self.calc.calculate_total(10.0), (subtotal - 10.0) + shipping + (subtotal - 10.0) * 0.23)
        self.assertAlmostEqual(self.calc.calculate_total(30.0), shipping)
        self.assertAlmostEqual(self.calc.calculate_total(40.0), shipping)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-5.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total("invalid")

    def test_total_items_and_list_items(self):
        self.calc.add_item("Apple", 1.0, 3)
        self.calc.add_item("Banana", 0.5, 2)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertEqual(self.calc.list_items(), ["Apple", "Banana"])

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item("Apple", 1.0, 1)
        self.assertFalse(self.calc.is_empty())
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_add_item_invalid_inputs(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", -1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 1.0, -1)
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 1.0, 0)
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item("Apple", "price", 1)

    def test_remove_item_invalid_inputs(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)


if __name__ == "__main__":
    unittest.main()