import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_init_custom_values(self):
        c = OrderCalculator(tax_rate=0.0, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(c.tax_rate, 0.0)
        self.assertEqual(c.free_shipping_threshold, 50.0)
        self.assertEqual(c.shipping_cost, 5.0)

    def test_init_negative_tax_rate_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_negative_free_shipping_threshold_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_negative_shipping_cost_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_add_item_single(self):
        self.calc.add_item('Apple', 2.5)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.5)

    def test_add_item_same_name_aggregates_quantity(self):
        self.calc.add_item('Apple', 2.0, quantity=1)
        self.calc.add_item('Apple', 2.0, quantity=3)
        self.assertEqual(self.calc.total_items(), 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 8.0)
        self.assertEqual(self.calc.list_items().count('Apple'), 1)

    def test_add_item_multiple_distinct(self):
        self.calc.add_item('Apple', 1.0, quantity=2)
        self.calc.add_item('Banana', 2.0, quantity=3)
        self.calc.add_item('Cherry', 3.0, quantity=1)
        self.assertCountEqual(self.calc.list_items(), ['Apple', 'Banana', 'Cherry'])
        self.assertEqual(self.calc.total_items(), 6)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0 * 2 + 2.0 * 3 + 3.0 * 1)

    def test_add_item_non_string_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 10.0)

    def test_add_item_empty_string_name_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 5.0)

    def test_add_item_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Banana', -5.0)

    def test_add_item_zero_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Banana', 0.0)

    def test_add_item_non_numeric_price_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Banana', 'free')

    def test_add_item_quantity_zero_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Banana', 1.0, quantity=0)

    def test_add_item_quantity_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Banana', 1.0, quantity=-2)

    def test_add_item_non_int_quantity_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Banana', 1.0, quantity=2.5)

    def test_remove_item_one_of_several(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Banana', 2.0)
        self.calc.add_item('Cherry', 3.0)
        self.calc.remove_item('Banana')
        self.assertCountEqual(self.calc.list_items(), ['Apple', 'Cherry'])
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0 + 3.0)

    def test_remove_item_non_string_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(42)

    def test_get_subtotal_after_adds_and_removes(self):
        self.calc.add_item('Apple', 2.0, quantity=2)
        self.calc.add_item('Banana', 3.0, quantity=1)
        self.calc.remove_item('Apple')
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_after_operations(self):
        self.calc.add_item('Apple', 1.0, quantity=3)
        self.calc.add_item('Banana', 2.0, quantity=2)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.total_items(), 2)

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_after_adds(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Banana', 2.0)
        self.assertCountEqual(self.calc.list_items(), ['Apple', 'Banana'])

    def test_list_items_after_removal(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Banana', 2.0)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.list_items(), ['Banana'])

    def test_is_empty_fresh(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('Apple', 1.0)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_clear_order_idempotent(self):
        self.calc.clear_order()
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_apply_discount_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -5.0)

    def test_apply_discount_negative_subtotal_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 5.0)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(75.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_at_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_custom_thresholds(self):
        c = OrderCalculator(free_shipping_threshold=20.0, shipping_cost=5.0)
        self.assertAlmostEqual(c.calculate_shipping(15.0), 5.0)
        self.assertAlmostEqual(c.calculate_shipping(20.0), 0.0)
        self.assertAlmostEqual(c.calculate_shipping(25.0), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        shipping = self.calc.calculate_shipping(-10.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_tax_positive_amount(self):
        tax = self.calc.calculate_tax(200.0)
        self.assertAlmostEqual(tax, 46.0)

    def test_calculate_tax_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_custom_rate(self):
        c = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(c.calculate_tax(100.0), 5.0)

    def test_calculate_tax_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-50.0)

    def test_calculate_total_no_discount_above_threshold(self):
        self.calc.add_item('Item', 60.0, quantity=2)
        total = self.calc.calculate_total()
        expected = 120.0 + 0.0 + 0.23 * 120.0
        self.assertAlmostEqual(total, expected)