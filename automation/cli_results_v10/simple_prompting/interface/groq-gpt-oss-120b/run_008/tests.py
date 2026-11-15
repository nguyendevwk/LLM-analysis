import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_add_item_updates_subtotal(self):
        self.calc.add_item('apple', 2.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0)

    def test_add_item_default_quantity(self):
        self.calc.add_item('banana', 1.5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.5)

    def test_remove_item_decreases_subtotal(self):
        self.calc.add_item('apple', 2.0, 2)
        self.calc.add_item('orange', 3.0, 1)
        self.calc.remove_item('apple')
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_remove_nonexistent_item_raises(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('nonexistent')

    def test_total_items_counts_quantities(self):
        self.calc.add_item('apple', 2.0, 2)
        self.calc.add_item('banana', 1.0, 5)
        self.assertEqual(self.calc.total_items(), 7)

    def test_clear_order_resets_state(self):
        self.calc.add_item('apple', 2.0, 2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_list_items_returns_names(self):
        self.calc.add_item('apple', 2.0)
        self.calc.add_item('banana', 1.0)
        self.assertCountEqual(self.calc.list_items(), ['apple', 'banana'])

    def test_is_empty_initially(self):
        self.assertTrue(self.calc.is_empty())

    def test_apply_discount_subtracts_amount(self):
        result = self.calc.apply_discount(100.0, 10.0)
        self.assertAlmostEqual(result, 90.0)

    def test_apply_discount_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_shipping(-10.0)

    def test_calculate_tax_applies_rate(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_total_without_discount(self):
        self.calc.add_item('apple', 30.0, 2)
        total = self.calc.calculate_total()
        expected = 60.0 + self.calc.calculate_tax(60.0) + self.calc.calculate_shipping(60.0)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('apple', 50.0)
        total = self.calc.calculate_total(discount=5.0)
        discounted = self.calc.apply_discount(50.0, 5.0)
        expected = discounted + self.calc.calculate_tax(discounted) + self.calc.calculate_shipping(discounted)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_exceeds_subtotal_raises(self):
        self.calc.add_item('apple', 10.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=20.0)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 10.0)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('apple', 'ten')

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('apple', -1.0)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('apple', 1.0, 'two')

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('apple', 1.0, -3)