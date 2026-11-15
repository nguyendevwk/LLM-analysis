import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    # 1. Constructor
    def test_init_defaults(self):
        self.assertAlmostEqual(self.calc.tax_rate, 0.23)
        self.assertAlmostEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertAlmostEqual(self.calc.shipping_cost, 10.0)

    def test_init_custom_values(self):
        c = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(c.tax_rate, 0.05)
        self.assertAlmostEqual(c.free_shipping_threshold, 50.0)
        self.assertAlmostEqual(c.shipping_cost, 5.0)

    def test_init_invalid_type(self):
        with self.assertRaises((TypeError, ValueError)):
            OrderCalculator(tax_rate='high')

    def test_init_negative_values(self):
        with self.assertRaises((TypeError, ValueError)):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises((TypeError, ValueError)):
            OrderCalculator(free_shipping_threshold=-10)
        with self.assertRaises((TypeError, ValueError)):
            OrderCalculator(shipping_cost=-5)

    def test_init_zero_values(self):
        c = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertAlmostEqual(c.tax_rate, 0.0)
        self.assertAlmostEqual(c.free_shipping_threshold, 0.0)
        self.assertAlmostEqual(c.shipping_cost, 0.0)

    # 2. add_item
    def test_add_item_new(self):
        self.calc.add_item('Apple', 1.20, 3)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3 * 1.20)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Banana', 0.50)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.50)

    def test_add_item_duplicate_aggregates_quantity(self):
        self.calc.add_item('Apple', 1.00, 2)
        self.calc.add_item('Apple', 1.00, 5)
        self.assertEqual(self.calc.total_items(), 7)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7 * 1.00)

    def test_add_item_duplicate_price_change(self):
        self.calc.add_item('Apple', 1.00, 2)
        self.calc.add_item('Apple', 1.10, 3)
        self.assertEqual(self.calc.total_items(), 5)
        # price should remain the first one
        self.assertAlmostEqual(self.calc.get_subtotal(), 5 * 1.00)

    def test_add_item_invalid_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Banana', -0.5, 1)

    def test_add_item_zero_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Banana', 0.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Banana', 'free', 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Banana', 0.5, 2.5)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Banana', 0.5, 0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Banana', 0.5, -3)

    def test_add_item_large_quantity(self):
        self.calc.add_item('Gadget', 2.0, 10_000)
        self.assertEqual(self.calc.total_items(), 10_000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 20_000.0)

    def test_add_item_large_price(self):
        self.calc.add_item('Car', 1_000_000.0, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1_000_000.0)

    def test_add_item_high_precision_price(self):
        self.calc.add_item('Widget', 0.3333333, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.9999999, places=7)

    # 3. remove_item
    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.calc.remove_item('Apple')
        self.assertNotIn('Apple', self.calc.list_items())
        self.assertIn('Banana', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 3)

    def test_remove_item_only_item(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_remove_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_remove_item_nonexistent(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('NonExisting')

    def test_remove_item_after_clear(self):
        self.calc.clear_order()
        with self.assertRaises(KeyError):
            self.calc.remove_item('Anything')

    # 4. get_subtotal
    def test_get_subtotal_empty(self):
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('A', 2.0, 2)
        self.calc.add_item('B', 3.5, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2*2.0 + 3.5)

    def test_get_subtotal_after_removal(self):
        self.calc.add_item('A', 2.0, 2)
        self.calc.add_item('B', 3.5, 1)
        self.calc.remove_item('A')
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.5)

    def test_get_subtotal_floating_point(self):
        self.calc.add_item('X', 0.1, 1)
        self.calc.add_item('Y', 0.2, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.3, places=7)

    def test_get_subtotal_large_numbers(self):
        self.calc.add_item('Big', 1_000_000.0, 10_000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10_000_000_000.0)

    # 5. apply_discount
    def test_apply_discount_normal(self):
        result = self.calc.apply_discount(200.0, 20.0)
        self.assertAlmostEqual(result, 180.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(150.0, 0.0)
        self.assertAlmostEqual(result, 150.0)

    def test_apply_discount_equal(self):
        result = self.calc.apply_discount(75.0, 75.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_exceeds_subtotal(self):
        result = self.calc.apply_discount(50.0, 60.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -5.0)

    def test_apply_discount_invalid_subtotal_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 10.0)

    def test_apply_discount_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '10')

    def test_apply_discount_small_floating(self):
        result = self.calc.apply_discount(0.3, 0.1)
        self.assertAlmostEqual(result, 0.2, places=7)

    def test_apply_discount_large_numbers(self):
        result = self.calc.apply_discount(1e9, 9.99e8)
        self.assertAlmostEqual(result, 1e7)

    # 6. calculate_shipping
    def test_calculate_shipping_below_threshold(self):
        cost = self.calc.calculate_shipping(80.0)
        self.assertAlmostEqual(cost, 10.0)

    def test_calculate_shipping_at_threshold(self):
        cost = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(cost, 0.0)

    def test_calculate_shipping_above_threshold(self):
        cost = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(cost, 0.0)

    def test_calculate_shipping_custom_parameters(self):
        c = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=7.5)
        self.assertAlmostEqual(c.calculate_shipping(30.0), 7.5)
        self.assertAlmostEqual(c.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_shipping(-10.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50')

    def test_calculate_shipping_very_large(self):
        cost = self.calc.calculate_shipping(1e12)
        self.assertAlmostEqual(cost, 0.0)

    def test_calculate_shipping_just_below_threshold(self):
        cost = self.calc.calculate_shipping(99.9999999)
        self.assertAlmostEqual(cost, 10.0)

    # 7. calculate_tax
    def test_calculate_tax_positive(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_custom_rate(self):
        c = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(c.calculate_tax(200.0), 10.0)

    def test_calculate_tax_rate_zero(self):
        c = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(c.calculate_tax(123.45), 0.0)

    def test_calculate_tax_rate_full(self):
        c = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(c.calculate_tax(80.0), 80.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_tax_floating_point(self):
        tax = self.calc.calculate_tax(0.3333333)
        self.assertAlmostEqual(tax, 0.076666659, places=7)

    # 8. calculate_total
    def test_calculate_total_empty_no_discount(self):
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 0.0)

    def test_calculate_total_empty_with_discount(self):
        total = self.calc.calculate_total(10.0)
        self.assertAlmostEqual(total, 0.0)

    def test_calculate_total_below_threshold_no