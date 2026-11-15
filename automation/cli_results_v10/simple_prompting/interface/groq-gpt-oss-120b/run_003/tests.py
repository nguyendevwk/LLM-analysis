import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_default_initialization(self):
        self.assertAlmostEqual(self.calc.tax_rate, 0.23)
        self.assertAlmostEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertAlmostEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_add_item_basic(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertIn('Apple', self.calc.list_items())
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_add_item_duplicate_name_increments_quantity(self):
        self.calc.add_item('Banana', 0.5, 1)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertEqual(self.calc.total_items(), 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Orange', 'free', 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', -1.0, 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Grape', 0.2, 'many')

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Grape', 0.2, 0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Grape', 0.2, -5)

    def test_remove_item_existing(self):
        self.calc.add_item('Mango', 2.0, 1)
        self.calc.remove_item('Mango')
        self.assertTrue(self.calc.is_empty())
        self.assertNotIn('Mango', self.calc.list_items())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('Nonexistent')

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('ItemA', 10.0, 1)
        self.calc.add_item('ItemB', 5.0, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 20.0)

    def test_apply_discount_normal(self):
        subtotal = 100.0
        discounted = self.calc.apply_discount(subtotal, 15.0)
        self.assertAlmostEqual(discounted, 85.0)

    def test_apply_discount_exceeds_subtotal(self):
        subtotal = 30.0
        discounted = self.calc.apply_discount(subtotal, 50.0)
        self.assertAlmostEqual(discounted, 0.0)

    def test_apply_discount_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -10.0)

    def test_apply_discount_invalid_types(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 10)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(80.0)
        self.assertAlmostEqual(shipping, self.calc.shipping_cost)

    def test_calculate_shipping_at_threshold(self):
        shipping = self.calc.calculate_shipping(self.calc.free_shipping_threshold)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_shipping(-5.0)

    def test_calculate_tax_normal(self):
        tax = self.calc.calculate_tax(200.0)
        self.assertAlmostEqual(tax, 200.0 * self.calc.tax_rate)

    def test_calculate_tax_zero(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_total_no_discount(self):
        self.calc.add_item('A', 20.0, 2)
        total = self.calc.calculate_total()
        expected_shipping = self.calc.calculate_shipping(40.0)
        expected_tax = self.calc.calculate_tax(40.0 + expected_shipping)
        self.assertAlmostEqual(total, 40.0 + expected_shipping + expected_tax)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('B', 50.0, 1)
        total = self.calc.calculate_total(discount=10.0)
        discounted = self.calc.apply_discount(50.0, 10.0)
        expected_shipping = self.calc.calculate_shipping(discounted)
        expected_tax = self.calc.calculate_tax(discounted + expected_shipping)
        self.assertAlmostEqual(total, discounted + expected_shipping + expected_tax)

    def test_calculate_total_empty_order(self):
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 0.0)

    def test_calculate_total_invalid_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-5.0)

    def test_total_items_counts_correctly(self):
        self.calc.add_item('X', 1.0, 3)
        self.calc.add_item('Y', 2.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order_resets_state(self):
        self.calc.add_item('Z', 5.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_list_items_returns_names(self):
        names = ['Alpha', 'Beta', 'Gamma']
        for n in names:
            self.calc.add_item(n, 1.0, 1)
        self.assertCountEqual(self.calc.list_items(), names)

    def test_is_empty_true_when_no_items(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false_when_items_present(self):
        self.calc.add_item('Delta', 3.0, 1)
        self.assertFalse(self.calc.is_empty())