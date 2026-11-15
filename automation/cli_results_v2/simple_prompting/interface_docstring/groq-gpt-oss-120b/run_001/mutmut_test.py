import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

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

    def test_add_item_success(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertIn('Apple', self.calc.list_items())

    def test_add_item_increment_quantity(self):
        self.calc.add_item('Banana', 0.5, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item('Milk', 2.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Milk', 2.5, 1)

    def test_add_item_invalid_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0)

    def test_add_item_invalid_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Bread', 0)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Egg', 0.2, 0)

    def test_add_item_type_errors(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)
        with self.assertRaises(TypeError):
            self.calc.add_item('Cheese', '1.0')
        with self.assertRaises(TypeError):
            self.calc.add_item('Cheese', 1.0, '2')

    def test_remove_item_success(self):
        self.calc.add_item('Orange', 0.8, 4)
        self.calc.remove_item('Orange')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_success(self):
        self.calc.add_item('A', 10.0, 2)
        self.calc.add_item('B', 5.0, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 25.0)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_normal(self):
        result = self.calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(result, 50.0)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(30.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_invalid_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.5)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_type_errors(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '0.1')

    def test_calculate_shipping_free(self):
        self.calc.free_shipping_threshold = 50.0
        self.assertAlmostEqual(self.calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_cost(self):
        self.calc.free_shipping_threshold = 100.0
        self.assertAlmostEqual(self.calc.calculate_shipping(80.0), self.calc.shipping_cost)

    def test_calculate_shipping_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('80')

    def test_calculate_tax_normal(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200.0), 46.0)

    def test_calculate_tax_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax([100])

    def test_calculate_total_without_discount_free_shipping(self):
        self.calc.add_item('Item1', 60.0, 1)
        self.calc.add_item('Item2', 50.0, 1)
        total = self.calc.calculate_total()
        expected = 110.0 + self.calc.calculate_tax(110.0)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_and_shipping(self):
        self.calc.add_item('Item', 30.0, 2)
        total = self.calc.calculate_total(discount=0.1)
        shipping = self.calc.calculate_shipping(54.0)
        tax = self.calc.calculate_tax(54.0 + shipping)
        expected = 54.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_invalid_discount(self):
        self.calc.add_item('X', 10.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.2)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.2)

    def test_calculate_total_discount_type_error(self):
        self.calc.add_item('Y', 5.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_total_items_counts_correctly(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order_resets_state(self):
        self.calc.add_item('A', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    def test_list_items_unique_names(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 1)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['Apple', 'Banana'])

    def test_is_empty_initially(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_adding(self):
        self.calc.add_item('Item', 1.0)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clearing(self):
        self.calc.add_item('Item', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())