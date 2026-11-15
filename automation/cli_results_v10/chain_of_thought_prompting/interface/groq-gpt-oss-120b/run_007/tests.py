import unittest
from decimal import Decimal
from order_calculator import OrderCalculator

class OrderCalculatorTest(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_init_custom_values(self):
        c = OrderCalculator(tax_rate=0.0, free_shipping_threshold=200.0, shipping_cost=5.5)
        self.assertEqual(c.tax_rate, 0.0)
        self.assertEqual(c.free_shipping_threshold, 200.0)
        self.assertEqual(c.shipping_cost, 5.5)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.05)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1.0)

    def test_add_item_single(self):
        self.calc.add_item('Apple', 1.2, 3)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.6)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Banana', 0.5)
        self.assertIn('Banana', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.5)

    def test_add_item_duplicate_cumulative(self):
        self.calc.add_item('Apple', 1.2, 2)
        self.calc.add_item('Apple', 1.2, 3)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', 0.8, 0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', 0.8, -1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', -0.8, 1)

    def test_add_item_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_non_numeric_price(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Grape', 'free', 1)

    def test_add_item_non_integer_quantity(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Grape', 1.0, 'two')

    def test_add_item_large_numbers(self):
        self.calc.add_item('GoldBar', 1000000000.0, 1000000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1000000000000000.0)

    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 1.2, 3)
        self.calc.remove_item('Apple')
        self.assertNotIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    def test_remove_item_after_duplicate_adds(self):
        self.calc.add_item('Apple', 1.2, 2)
        self.calc.add_item('Apple', 1.2, 2)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('NonExisting')

    def test_remove_item_empty_string(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('')

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_multiple_distinct(self):
        self.calc.add_item('Apple', 1.2, 1)
        self.calc.add_item('Banana', 0.5, 2)
        self.assertCountEqual(self.calc.list_items(), ['Apple', 'Banana'])

    def test_list_items_duplicate_names(self):
        self.calc.add_item('Apple', 1.2, 1)
        self.calc.add_item('Apple', 1.2, 2)
        self.assertEqual(self.calc.list_items(), ['Apple'])

    def test_clear_order(self):
        self.calc.add_item('Apple', 1.2, 1)
        self.calc.add_item('Banana', 0.5, 2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])
        self.assertEqual(self.calc.total_items(), 0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    def test_is_empty_fresh(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('Apple', 1.2, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('Apple', 1.2, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_mixed_quantities(self):
        self.calc.add_item('Apple', 1.2, 3)
        self.calc.add_item('Banana', 0.5, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_cumulative_duplicate(self):
        self.calc.add_item('Apple', 1.2, 2)
        self.calc.add_item('Apple', 1.2, 2)
        self.assertEqual(self.calc.total_items(), 4)

    def test_total_items_after_removal(self):
        self.calc.add_item('Apple', 1.2, 3)
        self.calc.add_item('Banana', 0.5, 2)
        self.calc.remove_item('Banana')
        self.assertEqual(self.calc.total_items(), 3)

    def test_get_subtotal_empty(self):
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    def test_get_subtotal_single_item(self):
        self.calc.add_item('Apple', 2.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.0)

    def test_apply_discount_typical(self):
        result = self.calc.apply_discount(200.0, 20.0)
        self.assertAlmostEqual(result, 180.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(150.0, 0.0)
        self.assertAlmostEqual(result, 150.0)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(50.0, 50.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_over(self):
        result = self.calc.apply_discount(30.0, 40.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -5.0)

    def test_apply_discount_non_numeric_subtotal(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('one hundred', 10.0)

    def test_apply_discount_non_numeric_discount(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, 'ten')

    def test_calculate_shipping_below_threshold(self):
        result = self.calc.calculate_shipping(90.0)
        self.assertAlmostEqual(result, 10.0)

    def test_calculate_shipping_at_threshold(self):
        result = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(result, 0.0)

    def test_calculate_shipping_above_threshold(self):
        result = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(result, 0.0)

    def test_calculate_shipping_custom(self):
        c = OrderCalculator(free_shipping_threshold=200.0, shipping_cost=5.0)
        self.assertAlmostEqual(c.calculate_shipping(150.0), 5.0)
        self.assertAlmostEqual(c.calculate_shipping(200.0), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_shipping(-10.0)

    def test_calculate_tax_default(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_custom_rate(self):
        c = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(c.calculate_tax(200.0), 10.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_non_numeric(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('hundred')

    def test_calculate_total_empty_no_discount(self):
        self.assertAlmostEqual(self.calc.calculate_total(), 0.0)

    def test_calculate_total_single_item_no_discount(self):
        self.calc.add_item('Book', 30.0, 2)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 86.1)

    def test_calculate_total_single_item_with_discount(self):
        self.calc.add_item('Book', 30.0, 2)
        total = self.calc.calculate_total(discount=10.0)
        self.assertAlmostEqual(total, 73.8)

    def test_calculate_total_discount_shipping_boundary(self):
        self.calc.add_item('Item', 60.0, 2)
        total1 = self.calc.calculate_total(discount=20.0)
        self.assertAlmostEqual(total1, 123.0)
        total2 = self.calc.calculate_total(discount=10.0)
        self.assertAlmostEqual(total2, 135.3)
        total3 = self.calc.calculate_total(discount=30.0)
        self.assertAlmostEqual(total3, 115.7)

    def test_calculate_total_discount_equals_subtotal(self):
        self.calc.add_item('Pen', 5.0, 2)
        total = self.calc.calculate_total(discount=10.0)
        self.assertAlmostEqual(total, 0.0)

    def test_calculate_total_custom_tax_and_shipping(self):
        c = OrderCalculator(tax_rate=0.0, shipping_cost=5.0, free_shipping_threshold=50.0)
        c.add_item('Item', 40.0, 1)
        total = c.calculate_total()
        self.assertAlmostEqual(total, 45.0)

    def test_calculate_total_never_free_shipping(self):
        c = OrderCalculator(free_shipping_threshold=1000.0)
        c.add_item('Item', 200.0, 1)
        total = c.calculate_total()
        self.assertAlmostEqual(total, 200.0 + 10.0 + 46.0)

    def test_calculate_total_non_numeric_discount(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='ten')

    def test_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-5.0)

    def test_calculate_total_floating_point_consistency(self):
        self.calc.add_item('Item', 0.1, 3)
        total = self.calc.calculate_total()
        manual = self.calc.apply_discount(self.calc.get_subtotal(), 0.0)
        manual += self.calc.calculate_shipping(manual)
        manual += self.calc.calculate_tax(manual)
        self.assertAlmostEqual(total, manual, places=7)

    def test_calculate_total_large_order(self):
        for i in range(100):
            self.calc.add_item(f'Item{i}', 1.0, 10)
        total = self.calc.calculate_total()
        subtotal = self.calc.get_subtotal()
        discounted = self.calc.apply_discount(subtotal, 0.0)
        shipping = self.calc.calculate_shipping(discounted)
        tax = self.calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_remove_item_after_clear(self):
        self.calc.clear_order()
        with self.assertRaises(KeyError):
            self.calc.remove_item('Anything')

    def test_add_item_after_clear(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.calc.add_item('Banana', 2.0, 2)
        self.assertIn('Banana', self.calc.list_items())
        self.assertNotIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 2)

    def test_list_items_order_independence(self):
        self.calc.add_item('B', 1.0, 1)
        self.calc.add_item('A', 1.0, 1)
        self.assertCountEqual(self.calc.list_items(), ['A', 'B'])

    def test_total_items_multiple_removals(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 1.0, 3)
        self.calc.add_item('C', 1.0, 4)
        self.calc.remove_item('B')
        self.assertEqual(self.calc.total_items(), 6)

    def test_apply_discount_fractional(self):
        result = self.calc.apply_discount(100.0, 12.34)
        self.assertAlmostEqual(result, 87.66)

    def test_calculate_shipping_float_subtotal(self):
        result = self.calc.calculate_shipping(99.99)
        self.assertAlmostEqual(result, 10.0)

    def test_calculate_tax_high_precision(self):
        self.assertAlmostEqual(self.calc.calculate_tax(123.456), 28.395, places=6)

    def test_add_item_whitespace_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('   ', 1.0, 1)

    def test_remove_item_case_sensitivity(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('apple', 1.0, 1)
        self.calc.remove_item('Apple')
        self.assertIn('apple', self.calc.list_items())
        self.assertNotIn('Apple', self.calc.list_items())

    def test_calculate_total_zero_shipping_cost(self):
        c = OrderCalculator(shipping_cost=0.0)
        c.add_item('Item', 40.0, 1)
        total = c.calculate_total()
        self.assertAlmostEqual(total, c.apply_discount(40.0, 0.0) + c.calculate_tax(40.0))

    def test_calculate_total_extreme_tax(self):
        c = OrderCalculator(tax_rate=1.5)
        c.add_item('Item', 100.0, 1)
        total = c.calculate_total()
        discounted = c.apply_discount(100.0, 0.0)
        shipping = c.calculate_shipping(discounted)
        tax = c.calculate_tax(discounted + shipping)
        self.assertAlmostEqual(total, discounted + shipping + tax)

    def test_apply_discount_decimal_input(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(Decimal('100'), Decimal('10'))

    def test_add_item_price_integer(self):
        self.calc.add_item('Pen', 5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10.0)

    def test_add_item_quantity_bool(self):
        self.calc.add_item('Pen', 1.0, True)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0)

    def test_calculate_total_cumulative_rounding(self):
        self.calc.add_item('Item', 0.3333, 3)
        total = self.calc.calculate_total()
        manual = self.calc.apply_discount(self.calc.get_subtotal(), 0.0)
        manual += self.calc.calculate_shipping(manual)
        manual += self.calc.calculate_tax(manual)
        self.assertAlmostEqual(total, manual, places=7)