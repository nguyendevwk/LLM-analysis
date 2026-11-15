import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    # Constructor tests
    def test_constructor_defaults(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_constructor_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_constructor_tax_rate_lower_bound(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_constructor_tax_rate_upper_bound(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_constructor_tax_rate_below_zero(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_constructor_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_constructor_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_constructor_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_constructor_tax_rate_non_numeric(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_constructor_free_shipping_threshold_non_numeric(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_constructor_shipping_cost_non_numeric(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    # add_item tests
    def test_add_item_single(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        self.assertEqual(calc.total_items(), 1)
        self.assertListEqual(calc.list_items(), ['Apple'])

    def test_add_item_aggregate_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        calc.add_item('Apple', 1.5, 3)
        self.assertEqual(calc.total_items(), 5)
        self.assertEqual(calc.items[0]['quantity'], 5)

    def test_add_item_different_name(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.add_item('Banana', 0.8, 5)
        self.assertEqual(calc.total_items(), 6)
        self.assertCountEqual(calc.list_items(), ['Apple', 'Banana'])

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Cherry', 2.0)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_integer_price(self):
        calc = OrderCalculator()
        calc.add_item('Date', 3, 2)
        self.assertEqual(calc.items[0]['price'], 3)

    def test_add_item_zero_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Egg', 0.5, 0)

    def test_add_item_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Fig', 0.5, -1)

    def test_add_item_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0, 1)

    def test_add_item_price_not_positive(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Grape', 0, 1)

    def test_add_item_duplicate_name_different_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 2.0, 1)

    def test_add_item_name_non_string(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_add_item_price_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Honey', '1.0', 1)

    def test_add_item_quantity_non_int(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Ice', 1.0, 1.5)

    def test_add_item_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Jelly', 0.01, 10**6)
        self.assertEqual(calc.total_items(), 10**6)

    def test_add_item_price_many_decimals(self):
        calc = OrderCalculator()
        calc.add_item('Kiwi', 0.9999999, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.9999999, places=7)

    # remove_item tests
    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.add_item('Banana', 0.8)
        calc.remove_item('Apple')
        self.assertNotIn('Apple', calc.list_items())
        self.assertEqual(calc.total_items(), 1)

    def test_remove_item_nonexistent(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.8)
        with self.assertRaises(ValueError):
            calc.remove_item('Cherry')

    def test_remove_item_name_non_string(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(42)

    def test_remove_item_last_item(self):
        calc = OrderCalculator()
        calc.add_item('Date', 3)
        calc.remove_item('Date')
        self.assertTrue(calc.is_empty())

    def test_remove_item_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.add_item('Banana', 0.8)
        calc.add_item('Cherry', 2.0)
        calc.remove_item('Banana')
        self.assertCountEqual(calc.list_items(), ['Apple', 'Cherry'])
        self.assertEqual(calc.total_items(), 2)

    # get_subtotal tests
    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        calc.add_item('Banana', 0.8, 3)
        expected = 1.5 * 2 + 0.8 * 3
        self.assertAlmostEqual(calc.get_subtotal(), expected)

    def test_get_subtotal_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_single_item_quantity_one(self):
        calc = OrderCalculator()
        calc.add_item('Lemon', 2.5)
        self.assertAlmostEqual(calc.get_subtotal(), 2.5)

    def test_get_subtotal_floating_rounding(self):
        calc = OrderCalculator()
        calc.add_item('Mango', 0.1, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3, places=7)

    # apply_discount tests
    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100, 0.0), 100.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100, 1.0), 0.0)

    def test_apply_discount_typical(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(200, 0.2), 160.0)

    def test_apply_discount_discount_lower_bound(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50, 0.0), 50.0)

    def test_apply_discount_discount_upper_bound(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50, 1.0), 0.0)

    def test_apply_discount_negative_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50, -0.1)

    def test_apply_discount_discount_above_one(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50, 1.5)

    def test_apply_discount_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10, 0.1)

    def test_apply_discount_subtotal_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_discount_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100, None)

    def test_apply_discount_large_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(1e9, 0.15), 8.5e8)

    # calculate_shipping tests
    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_at_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_custom_values(self):
        calc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(calc.calculate_shipping(49.9), 5.