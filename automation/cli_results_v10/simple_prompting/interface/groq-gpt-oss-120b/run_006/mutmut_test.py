import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_default_initialization(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_add_single_item(self):
        self.calc.add_item('Apple', 1.5)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.5)

    def test_add_multiple_quantities(self):
        self.calc.add_item('Banana', 0.8, quantity=3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.4)

    def test_add_item_invalid_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_invalid_price(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Orange', 'free')

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', -1.0)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Grape', 0.5, quantity='many')

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Grape', 0.5, quantity=-2)

    def test_remove_existing_item(self):
        self.calc.add_item('Mango', 2.0, quantity=2)
        self.calc.remove_item('Mango')
        self.assertTrue(self.calc.is_empty())

    def test_subtotal_multiple_items(self):
        self.calc.add_item('ItemA', 10.0, quantity=2)
        self.calc.add_item('ItemB', 5.0, quantity=1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 25.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -5.0)

    def test_shipping_free_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_shipping_cost_below_threshold(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, self.calc.shipping_cost)

    def test_tax_calculation(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-10.0)

    def test_total_items_counts_correctly(self):
        self.calc.add_item('X', 1.0, quantity=4)
        self.calc.add_item('Y', 2.0, quantity=3)
        self.assertEqual(self.calc.total_items(), 7)

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_adding(self):
        self.calc.add_item('Item', 1.0)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_removal(self):
        self.calc.add_item('Item', 1.0)
        self.calc.remove_item('Item')
        self.assertTrue(self.calc.is_empty())