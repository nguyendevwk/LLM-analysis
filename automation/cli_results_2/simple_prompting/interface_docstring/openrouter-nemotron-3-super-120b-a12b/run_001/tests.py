import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_valid_defaults(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_init_tax_rate_bounds_valid(self):
        OrderCalculator(tax_rate=0.0)
        OrderCalculator(tax_rate=1.0)

    def test_init_tax_rate_invalid_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_invalid_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_type_errors(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_typical(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertIn('Apple', self.calc.list_items())

    def test_add_item_merge_same_name_price(self):
        self.calc.add_item('Banana', 0.5, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0)

    def test_add_item_price_non_positive(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', 0.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', -1.0)

    def test_add_item_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', 1.0, 0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', 1.0, -1)

    def test_add_item_type_errors(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)
        with self.assertRaises(TypeError):
            self.calc.add_item('Pear', '1.0')
        with self.assertRaises(TypeError):
            self.calc.add_item('Pear', 1.0, '2')

    def test_add_item_same_name_different_price(self):
        self.calc.add_item('Pear', 1.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Pear', 1.5)

    def test_remove_item_existing(self):
        self.calc.add_item('Orange', 2.0)
        self.calc.remove_item('Orange')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Ghost')

    def test_remove_item_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_typical(self):
        self.calc.add_item('A', 10.0, 2)
        self.calc.add_item('B', 5.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 35.0)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_typical(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_invalid_discount_low(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)

    def test_apply_discount_invalid_discount_high(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.1)

    def test_apply_discount_type_errors(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, '0.1')

    def test_calculate_shipping_free_when_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_free_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_charged_when_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(99.9), 10.0)

    def test_calculate_shipping_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('100')

    def test_calculate_tax_typical(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200.0), 46.0)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_typical(self):
        self.calc.add_item('Item1', 10.0, 2)
        self.calc.add_item('Item2', 30.0, 1)
        total = self.calc.calculate_total(discount=0.1)
        expected_subtotal = 2 * 10.0 + 1 * 30.0
        discounted = expected_subtotal * (1 - 0.1)
        shipping = 10.0 if discounted < 100.0 else 0.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_no_discount(self):
        self.calc.add_item('Item', 50.0)
        total = self.calc.calculate_total()
        expected_subtotal = 50.0
        shipping = 10.0 if expected_subtotal < 100.0 else 0.0
        tax = (expected_subtotal + shipping) * 0.23
        expected = expected_subtotal + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item('Item', 120.0)
        total = self.calc.calculate_total()
        expected_subtotal = 120.0
        shipping = 0.0
        tax = expected_subtotal * 0.23
        expected = expected_subtotal + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_invalid_discount(self):
        self.calc.add_item('Item', 10.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.1)

    def test_calculate_total_type_error(self):
        self.calc.add_item('Item', 10.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_total_items_typical(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order(self):
        self.calc.add_item('A', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])
        self.assertEqual(self.calc.total_items(), 0)

    def test_list_items(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Banana', 2.0)
        self.calc.add_item('Apple', 1.0, 2)
        items = self.calc.list_items()
        self.assertEqual(set(items), {'Apple', 'Banana'})
        self.assertEqual(len(items), 2)

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('Item', 1.0)
        self.assertFalse(self.calc.is_empty())
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())