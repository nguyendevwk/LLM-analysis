import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_default_tax_rate(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_default_free_shipping_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0, places=6)
        self.assertAlmostEqual(self.calc.calculate_shipping(99.99), 10.0, places=6)

    def test_default_shipping_cost(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(50.0), 10.0, places=6)

    def test_add_item_basic(self):
        self.calc.add_item('apple', 1.5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertIn('apple', self.calc.list_items())

    def test_add_item_default_quantity(self):
        self.calc.add_item('banana', 0.5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.5)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_multiple_same_name(self):
        self.calc.add_item('apple', 1.5, 2)
        self.calc.add_item('apple', 1.5, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.5)
        self.assertEqual(self.calc.total_items(), 5)

    def test_remove_item(self):
        self.calc.add_item('apple', 1.5, 2)
        self.calc.remove_item('apple')
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.total_items(), 0)
        self.assertNotIn('apple', self.calc.list_items())

    def test_remove_nonexistent_item_raises(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('nonexistent')

    def test_get_subtotal(self):
        self.calc.add_item('apple', 1.0, 3)
        self.calc.add_item('banana', 2.0, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.0)

    def test_apply_discount(self):
        self.calc.add_item('apple', 1.5, 4)
        discounted = self.calc.apply_discount(6.0, 2.0)
        self.assertAlmostEqual(discounted, 4.0)
        discounted = self.calc.apply_discount(6.0, 10.0)
        self.assertAlmostEqual(discounted, 0.0)

    def test_calculate_shipping(self):
        self.calc.add_item('apple', 1.0, 101)
        discounted = self.calc.apply_discount(101.0, 0.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(discounted), 0.0)
        discounted = self.calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(self.calc.calculate_shipping(discounted), 10.0)

    def test_calculate_tax(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200.0), 46.0)

    def test_calculate_total(self):
        self.calc.add_item('apple', 1.5, 4)
        total = self.calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 5.0 + 10.0 + 1.15, places=6)

    def test_total_items(self):
        self.calc.add_item('apple', 1.0, 3)
        self.calc.add_item('banana', 2.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order(self):
        self.calc.add_item('apple', 1.0, 3)
        self.calc.clear_order()
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.total_items(), 0)
        self.assertTrue(self.calc.is_empty())

    def test_list_items(self):
        self.calc.add_item('apple', 1.0, 3)
        self.calc.add_item('banana', 2.0, 2)
        self.assertCountEqual(self.calc.list_items(), ['apple', 'banana'])

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('apple', 1.0, 1)
        self.assertFalse(self.calc.is_empty())
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('apple', -1.0, 1)

    def test_add_item_non_numeric_price(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('apple', '1.0', 1)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('apple', 1.0, 0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('apple', 1.0, -2)

    def test_remove_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -5.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-5.0)

    def test_calculate_total_discount_exceeds_subtotal(self):
        self.calc.add_item('apple', 1.0, 2)
        total = self.calc.calculate_total(discount=5.0)
        self.assertAlmostEqual(total, 10.0)

    def test_calculate_total_discount_exceeds_subtotal_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        calc.add_item('apple', 1.0, 2)
        total = calc.calculate_total(discount=5.0)
        self.assertAlmostEqual(total, 0.0)

    def test_calculate_total_discount_exceeds_subtotal_zero_shipping(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('apple', 1.0, 2)
        total = calc.calculate_total(discount=5.0)
        self.assertAlmostEqual(total, 0.0)

    def test_calculate_total_discount_exceeds_subtotal_zero_tax(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('apple', 1.0, 2)
        total = calc.calculate_total(discount=5.0)
        self.assertAlmostEqual(total, 10.0)

    def test_calculate_total_discount_exceeds_subtotal_all_zero(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        calc.add_item('apple', 1.0, 2)
        total = calc.calculate_total(discount=5.0)
        self.assertAlmostEqual(total, 0.0)