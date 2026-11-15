import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    # Initialization Tests
    def test_init_invalid_params(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1)
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    # add_item Tests
    def test_add_item_success(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.calc.add_item("Apple", 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_invalid(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 10.0)
        with self.assertRaises(ValueError):
            self.calc.add_item("Banana", -5.0)
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 1.0, 1)
            self.calc.add_item("Apple", 2.0, 1)

    # remove_item Tests
    def test_remove_item(self):
        self.calc.add_item("Apple", 1.0)
        self.calc.remove_item("Apple")
        self.assertTrue(self.calc.is_empty())
        with self.assertRaises(ValueError):
            self.calc.remove_item("NonExistent")

    # get_subtotal Tests
    def test_get_subtotal(self):
        self.calc.add_item("A", 10.0, 2)
        self.calc.add_item("B", 5.0, 1)
        self.assertEqual(self.calc.get_subtotal(), 25.0)
        with self.assertRaises(ValueError):
            OrderCalculator().get_subtotal()

    # apply_discount Tests
    def test_apply_discount(self):
        self.assertEqual(self.calc.apply_discount(100.0, 0.2), 80.0)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.5)

    # calculate_shipping Tests
    def test_calculate_shipping(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)
        self.assertEqual(self.calc.calculate_shipping(50.0), 10.0)

    # calculate_tax Tests
    def test_calculate_tax(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    # calculate_total Tests
    def test_calculate_total(self):
        self.calc.add_item("Item", 100.0, 1)
        # Subtotal 100, Discount 0, Shipping 0 (threshold met), Tax 23%
        # 100 + 0 + 23 = 123
        self.assertAlmostEqual(self.calc.calculate_total(0.0), 123.0)

    # Utility Methods Tests
    def test_list_items(self):
        self.calc.add_item("A", 1.0)
        self.calc.add_item("B", 2.0)
        self.assertCountEqual(self.calc.list_items(), ["A", "B"])

    def test_clear_order(self):
        self.calc.add_item("A", 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item("A", 1.0)
        self.assertFalse(self.calc.is_empty())

if __name__ == "__main__":
    unittest.main()