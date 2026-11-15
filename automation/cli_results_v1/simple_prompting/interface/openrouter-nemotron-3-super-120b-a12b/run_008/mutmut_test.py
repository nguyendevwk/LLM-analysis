import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)

    def test_init_creates_instance(self):
        self.assertIsInstance(self.calc, OrderCalculator)

    def test_add_item_single_quantity_updates_subtotal(self):
        self.calc.add_item('apple', 10.0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10.0)

    def test_add_item_with_quantity_updates_subtotal(self):
        self.calc.add_item('banana', 3.0, quantity=4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 12.0)

    def test_add_multiple_items_sums_subtotal(self):
        self.calc.add_item('book', 12.5, quantity=2)
        self.calc.add_item('pen', 1.5, quantity=5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 12.5 * 2 + 1.5 * 5)

    def test_remove_item_non_string_name_raises(self):
        self.calc.add_item('valid', 2.0)
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_returns_float(self):
        self.calc.add_item('a', 1.0)
        self.assertIsInstance(self.calc.get_subtotal(), float)

    def test_total_items_returns_sum_of_quantities(self):
        self.calc.add_item('x', 1.0, quantity=2)
        self.calc.add_item('y', 2.0, quantity=3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_zero_when_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_is_empty_true_initially(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false_after_add(self):
        self.calc.add_item('z', 1.0)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_true_after_clear(self):
        self.calc.add_item('z', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items_returns_unique_names(self):
        self.calc.add_item('apple', 1.0, quantity=2)
        self.calc.add_item('banana', 2.0)
        self.calc.add_item('apple', 1.0, quantity=1)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['apple', 'banana'])

    def test_list_items_returns_list_of_strings(self):
        self.calc.add_item('only', 5.0)
        result = self.calc.list_items()
        self.assertIsInstance(result, list)
        self.assertTrue(all((isinstance(i, str) for i in result)))

    def test_apply_discount_zero_discount_returns_subtotal(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_invalid_subtotal_type_raises(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('not a number', 5.0)

    def test_apply_discount_invalid_discount_type_raises(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(50.0, '5')

    def test_calculate_shipping_below_threshold_returns_cost(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(40.0), self.calc.shipping_cost)

    def test_calculate_shipping_at_threshold_returns_zero(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_above_threshold_returns_zero(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(80.0), 0.0)

    def test_calculate_shipping_invalid_type_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('40')

    def test_calculate_tax_returns_amount_times_rate(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200.0), 200.0 * self.calc.tax_rate)

    def test_calculate_tax_zero_amount_returns_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_invalid_type_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_no_discount_no_shipping(self):
        self.calc.add_item('item', 40.0)
        subtotal = self.calc.get_subtotal()
        shipping = self.calc.calculate_shipping(subtotal)
        tax = self.calc.calculate_tax(subtotal + shipping)
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_free_shipping_when_discounted_subtotal_meets_threshold(self):
        self.calc.add_item('item', 80.0)
        discount = 0.0
        discounted = self.calc.apply_discount(self.calc.get_subtotal(), discount)
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(discount), expected)

    def test_calculate_total_invalid_discount_type_raises(self):
        self.calc.add_item('item', 10.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total('5')

    def test_add_item_invalid_name_type_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 5.0)

    def test_add_item_invalid_price_type_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('item', '5.0')

    def test_add_item_invalid_quantity_type_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('item', 5.0, quantity='2')