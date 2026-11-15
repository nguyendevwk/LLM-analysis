import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_invalid_params(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1)
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")

    def test_add_item_valid(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.calc.add_item("Apple", 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_invalid(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 10.0)
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", -1.0)
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 10.0, 0)
        self.calc.add_item("Apple", 10.0)
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 15.0)

    def test_remove_item(self):
        self.calc.add_item("Apple", 1.0)
        self.calc.remove_item("Apple")
        self.assertTrue(self.calc.is_empty())
        with self.assertRaises(ValueError):
            self.calc.remove_item("NonExistent")

    def test_get_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()
        self.calc.add_item("A", 10.0, 2)
        self.assertEqual(self.calc.get_subtotal(), 20.0)

    def test_apply_discount(self):
        self.assertEqual(self.calc.apply_discount(100.0, 0.1), 90.0)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.5)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.1)

    def test_calculate_shipping(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)
        self.assertEqual(self.calc.calculate_shipping(50.0), 10.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("invalid")

    def test_calculate_tax(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-1.0)

    def test_calculate_total(self):
        self.calc.add_item("Item", 100.0, 1)
        # Subtotal 100, Discount 0, Shipping 0 (threshold met), Tax 23% of 100 = 123.0
        self.assertAlmostEqual(self.calc.calculate_total(0.0), 123.0)
        
        self.calc.clear_order()
        self.calc.add_item("Item", 50.0, 1)
        # Subtotal 50, Discount 0, Shipping 10, Tax 23% of 60 = 73.8
        self.assertAlmostEqual(self.calc.calculate_total(0.0), 73.8)

    def test_total_items(self):
        self.assertEqual(self.calc.total_items(), 0)
        self.calc.add_item("A", 1.0, 5)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order(self):
        self.calc.add_item("A", 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items(self):
        self.calc.add_item("A", 1.0)
        self.calc.add_item("B", 2.0)
        self.assertCountEqual(self.calc.list_items(), ["A", "B"])

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item("A", 1.0)
        self.assertFalse(self.calc.is_empty())

if __name__ == '__main__':
    unittest.main()