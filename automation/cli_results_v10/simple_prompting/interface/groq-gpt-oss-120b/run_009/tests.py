import unittest
from order_calculator import OrderCalculator

class OrderCalculatorTest(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_initial_state(self):
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.list_items(), [])

    def test_add_item_and_subtotal(self):
        self.calc.add_item('apple', 2.0, 3)
        self.calc.add_item('banana', 1.5, 2)
        self.assertFalse(self.calc.is_empty())
        self.assertCountEqual(self.calc.list_items(), ['apple', 'banana'])
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 9.0)

    def test_remove_item(self):
        self.calc.add_item('apple', 2.0, 3)
        self.calc.add_item('banana', 1.5, 2)
        self.calc.remove_item('apple')
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)
        self.assertCountEqual(self.calc.list_items(), ['banana'])
        with self.assertRaises(KeyError):
            self.calc.remove_item('nonexistent')

    def test_apply_discount(self):
        subtotal = 50.0
        discounted = self.calc.apply_discount(subtotal, 5.0)
        self.assertAlmostEqual(discounted, 45.0)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(subtotal, -1.0)

    def test_calculate_shipping_free(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_paid(self):
        shipping = self.calc.calculate_shipping(80.0)
        self.assertAlmostEqual(shipping, 10.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_shipping(-10.0)

    def test_calculate_tax(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_total(self):
        self.calc.add_item('apple', 2.0, 3)
        self.calc.add_item('banana', 1.5, 2)
        total = self.calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 19.84, places=2)

    def test_clear_order(self):
        self.calc.add_item('apple', 2.0, 3)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.list_items(), [])

    def test_add_item_invalid_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('apple', 'free', 1)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('apple', 1.0, 'many')
        with self.assertRaises(ValueError):
            self.calc.add_item('apple', 1.0, 0)

    def test_custom_initialization(self):
        custom = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        custom.add_item('item', 20.0, 2)
        total = custom.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 49.0, places=2)