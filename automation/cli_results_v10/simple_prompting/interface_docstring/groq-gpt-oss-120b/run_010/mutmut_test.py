import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_tax_rate_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_basic(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_add_item_merge_same(self):
        self.calc.add_item('Banana', 0.5, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.5)

    def test_add_item_conflict_price(self):
        self.calc.add_item('Cherry', 2.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Cherry', 2.5, 1)

    def test_add_item_invalid_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_invalid_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Date', 0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Date', -1, 1)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Egg', 1.0, 0)

    def test_add_item_type_errors(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('Fig', '1.0', 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('Grape', 1.0, '2')

    def test_remove_item_existing(self):
        self.calc.add_item('Honey', 2.0, 2)
        self.calc.remove_item('Honey')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Ice')

    def test_remove_item_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_normal(self):
        result = self.calc.apply_discount(200.0, 0.1)
        self.assertAlmostEqual(result, 180.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(result, 50.0)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(80.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_invalid_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_invalid_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.5)

    def test_apply_discount_type_errors(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '0.1')

    def test_calculate_shipping_free(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_cost(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(80.0), self.calc.shipping_cost)

    def test_calculate_shipping_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('80')

    def test_calculate_tax_normal(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_invalid_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_basic(self):
        self.calc.add_item('ItemA', 30.0, 2)
        self.calc.add_item('ItemB', 20.0, 1)
        discount = 0.1
        shipping = self.calc.shipping_cost
        tax = (72 + shipping) * self.calc.tax_rate
        expected = 72 + shipping + tax
        total = self.calc.calculate_total(discount)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item('ItemC', 60.0, 2)
        discount = 0.0
        shipping = 0.0
        tax = (120 + shipping) * self.calc.tax_rate
        expected = 120 + shipping + tax
        total = self.calc.calculate_total(discount)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_invalid_discount(self):
        self.calc.add_item('ItemE', 10.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.5)

    def test_total_items_multiple(self):
        self.calc.add_item('ItemF', 5.0, 3)
        self.calc.add_item('ItemG', 2.0, 4)
        self.assertEqual(self.calc.total_items(), 7)

    def test_clear_order(self):
        self.calc.add_item('ItemH', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_uniqueness(self):
        self.calc.add_item('ItemI', 3.0, 1)
        self.calc.add_item('ItemI', 3.0, 2)
        self.calc.add_item('ItemJ', 4.0, 1)
        self.assertCountEqual(self.calc.list_items(), ['ItemI', 'ItemJ'])

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('ItemK', 2.0, 1)
        self.assertFalse(self.calc.is_empty())