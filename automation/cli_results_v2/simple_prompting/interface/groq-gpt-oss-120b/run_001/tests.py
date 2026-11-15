import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_initial_state_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.list_items(), [])

    def test_add_item_updates_subtotal_and_items(self):
        self.calc.add_item('Apple', 2.5, 3)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.5)
        self.assertIn('Apple', self.calc.list_items())

    def test_add_multiple_items_and_total_items(self):
        self.calc.add_item('Apple', 2.0, 2)
        self.calc.add_item('Banana', 1.0, 5)
        self.assertEqual(self.calc.total_items(), 7)
        self.assertAlmostEqual(self.calc.get_subtotal(), 9.0)

    def test_remove_item_decreases_subtotal_and_items(self):
        self.calc.add_item('Apple', 2.0, 2)
        self.calc.add_item('Banana', 1.0, 3)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)
        self.assertNotIn('Apple', self.calc.list_items())

    def test_remove_nonexistent_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('Nonexistent')

    def test_add_item_invalid_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', -1.0, 1)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.0, 'two')

    def test_add_item_zero_quantity(self):
        self.calc.add_item('Apple', 2.0, 0)
        self.assertEqual(self.calc.total_items(), 0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertNotIn('Apple', self.calc.list_items())

    def test_apply_discount_typical(self):
        result = self.calc.apply_discount(100.0, 15.0)
        self.assertAlmostEqual(result, 85.0)

    def test_apply_discount_exceeds_subtotal(self):
        result = self.calc.apply_discount(10.0, 20.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_invalid_types(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 10.0)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '10')

    def test_calculate_shipping_free_when_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_cost_when_below_threshold(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, self.calc.shipping_cost)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('fifty')

    def test_calculate_tax(self):
        tax = self.calc.calculate_tax(200.0)
        self.assertAlmostEqual(tax, 200.0 * self.calc.tax_rate)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax(None)

    def test_calculate_total_without_discount(self):
        self.calc.add_item('Apple', 10.0, 2)
        total = self.calc.calculate_total()
        expected_subtotal = 20.0
        expected_shipping = self.calc.calculate_shipping(expected_subtotal)
        expected_tax = self.calc.calculate_tax(expected_subtotal)
        self.assertAlmostEqual(total, expected_subtotal + expected_shipping + expected_tax)

    def test_calculate_total_with_discount_and_free_shipping(self):
        self.calc.add_item('Item', 60.0, 2)
        total = self.calc.calculate_total(discount=20.0)
        discounted = self.calc.apply_discount(120.0, 20.0)
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted)
        self.assertAlmostEqual(total, discounted + shipping + tax)

    def test_total_items_counts_quantities(self):
        self.calc.add_item('A', 1.0, 1)
        self.calc.add_item('B', 2.0, 4)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order_resets_state(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_list_items_returns_names(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Banana', 2.0, 2)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['Apple', 'Banana'])

    def test_is_empty_true_false(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('Apple', 1.0, 1)
        self.assertFalse(self.calc.is_empty())