import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)

    def test_init_default_values(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_add_item_typical(self):
        self.calc.add_item('apple', 1.0, 2)
        self.assertEqual(self.calc.get_subtotal(), 2.0)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertIn('apple', self.calc.list_items())

    def test_add_item_update_quantity(self):
        self.calc.add_item('book', 10.0, 1)
        self.calc.add_item('book', 10.0, 3)
        self.assertEqual(self.calc.get_subtotal(), 40.0)
        self.assertEqual(self.calc.total_items(), 4)

    def test_add_item_zero_quantity(self):
        self.calc.add_item('pen', 2.0, 0)
        self.assertEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.total_items(), 0)

    def test_add_item_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('bad', -5.0, 1)

    def test_add_item_non_int_quantity_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('pen', 2.0, 1.5)

    def test_add_item_non_string_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 2.0, 1)

    def test_remove_item_existing(self):
        self.calc.add_item('hat', 20.0, 1)
        self.calc.remove_item('hat')
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_remove_item_nonexistent_raises(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('missing')

    def test_get_subtotal_empty(self):
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('a', 5.0, 2)
        self.calc.add_item('b', 3.0, 1)
        self.assertEqual(self.calc.get_subtotal(), 13.0)

    def test_apply_discount_typical(self):
        self.assertEqual(self.calc.apply_discount(100.0, 10.0), 90.0)

    def test_apply_discount_zero(self):
        self.assertEqual(self.calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_negative(self):
        self.assertEqual(self.calc.apply_discount(30.0, -5.0), 35.0)

    def test_apply_discount_exceeds_subtotal(self):
        self.assertEqual(self.calc.apply_discount(20.0, 25.0), -5.0)

    def test_calculate_shipping_free_threshold(self):
        self.calc.add_item('expensive', 150.0, 1)
        discounted = self.calc.apply_discount(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.calculate_shipping(discounted), 0.0)

    def test_calculate_shipping_below_threshold(self):
        self.calc.add_item('cheap', 10.0, 1)
        discounted = self.calc.apply_discount(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.calculate_shipping(discounted), 10.0)

    def test_calculate_shipping_zero_amount(self):
        self.assertEqual(self.calc.calculate_shipping(0.0), 10.0)

    def test_calculate_tax(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        self.assertAlmostEqual(self.calc.calculate_tax(-10.0), -2.3)

    def test_calculate_total_no_discount_free_shipping(self):
        self.calc.add_item('item', 120.0, 1)
        total = self.calc.calculate_total()
        expected_subtotal = 120.0
        expected_discounted = expected_subtotal
        expected_shipping = 0.0
        expected_tax = expected_discounted * 0.23
        expected_total = expected_discounted + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('item', 80.0, 1)
        total = self.calc.calculate_total(discount=10.0)
        expected_subtotal = 80.0
        expected_discounted = self.calc.apply_discount(expected_subtotal, 10.0)
        expected_shipping = self.calc.calculate_shipping(expected_discounted)
        expected_tax = self.calc.calculate_tax(expected_discounted)
        expected_total = expected_discounted + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_discount_exceeds_subtotal(self):
        self.calc.add_item('item', 5.0, 1)
        total = self.calc.calculate_total(discount=10.0)
        expected_subtotal = 5.0
        expected_discounted = self.calc.apply_discount(expected_subtotal, 10.0)
        expected_shipping = self.calc.calculate_shipping(expected_discounted)
        expected_tax = self.calc.calculate_tax(expected_discounted)
        expected_total = expected_discounted + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_total_items(self):
        self.calc.add_item('a', 1.0, 2)
        self.calc.add_item('b', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order(self):
        self.calc.add_item('x', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items(self):
        self.calc.add_item('z', 1.0, 1)
        self.calc.add_item('a', 2.0, 1)
        self.calc.add_item('m', 3.0, 1)
        self.assertEqual(self.calc.list_items(), ['z', 'a', 'm'])

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('something', 1.0, 1)
        self.assertFalse(self.calc.is_empty())