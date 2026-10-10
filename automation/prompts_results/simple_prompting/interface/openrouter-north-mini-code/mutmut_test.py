import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_item_basic(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertEqual(self.calc.get_subtotal(), 2.0)

    def test_add_item_default_quantity(self):
        self.calc.add_item("Banana", 1.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertEqual(self.calc.get_subtotal(), 1.5)

    def test_add_item_quantity_zero(self):
        self.calc.add_item("Cherry", 5.0, 0)
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_add_item_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Bad", -10.0)

    def test_add_item_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Bad", 10.0, -1)

    def test_remove_item(self):
        self.calc.add_item("Apple", 1.0)
        self.calc.remove_item("Apple")
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    def test_remove_item_non_existent(self):
        self.calc.remove_item("NonExistent")
        self.assertTrue(self.calc.is_empty())

    def test_get_subtotal_empty(self):
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_get_subtotal(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0, 2)
        self.assertEqual(self.calc.get_subtotal(), 50.0)

    def test_apply_discount(self):
        self.assertEqual(self.calc.apply_discount(100.0, 0.1), 90.0)
        self.assertEqual(self.calc.apply_discount(100.0, 0.0), 100.0)
        self.assertEqual(self.calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_negative_discount_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)

    def test_calculate_shipping(self):
        self.assertEqual(self.calc.calculate_shipping(50.0), 10.0)
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_tax(self):
        self.assertEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-100.0)

    def test_calculate_total_empty(self):
        self.assertEqual(self.calc.calculate_total(), 0.0