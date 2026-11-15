import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_tax_rate_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_invalid_free_shipping_threshold_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_invalid_shipping_cost_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_success(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        self.assertIn('Apple', calc.list_items())
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 3.0)

    def test_add_item_merge_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.8, 1)
        calc.add_item('Banana', 0.8, 3)
        self.assertEqual(calc.total_items(), 4)
        self.assertAlmostEqual(calc.get_subtotal(), 0.8 * 4)

    def test_add_item_same_name_different_price(self):
        calc = OrderCalculator()
        calc.add_item('Milk', 2.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Milk', 2.5, 1)

    def test_add_item_invalid_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0, 1)

    def test_add_item_invalid_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Bread', 0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Bread', -1, 1)

    def test_add_item_invalid_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Egg', 0.2, 0)

    def test_add_item_invalid_types(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            calc.add_item('Cheese', '1.0', 1)
        with self.assertRaises(TypeError):
            calc.add_item('Cheese', 1.0, '2')

    def test_remove_item_success(self):
        calc = OrderCalculator()
        calc.add_item('Orange', 0.5, 4)
        calc.remove_item('Orange')
        self.assertTrue(calc.is_empty())

    def test_remove_item_nonexistent(self):
        calc = OrderCalculator()
        calc.add_item('Grapes', 2.0, 1)
        with self.assertRaises(ValueError):
            calc.remove_item('Apple')

    def test_remove_item_invalid_type(self):
        calc = OrderCalculator()
        calc.add_item('Pear', 1.0, 1)
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('ItemA', 10.0, 2)
        calc.add_item('ItemB', 5.0, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 10.0 * 2 + 5.0 * 3)

    def test_get_subtotal_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        result = calc.apply_discount(200.0, 0.1)
        self.assertAlmostEqual(result, 180.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(80.0, 1.0), 0.0)

    def test_apply_discount_invalid_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.2)

    def test_apply_discount_invalid_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.5)

    def test_apply_discount_invalid_types(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.1')

    def test_calculate_shipping_free(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=7.5)
        self.assertAlmostEqual(calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_cost(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=12.0)
        self.assertAlmostEqual(calc.calculate_shipping(80.0), 12.0)

    def test_calculate_shipping_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('30')

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(calc.calculate_tax(150.0), 30.0)

    def test_calculate_tax_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax([100])

    def test_calculate_total_no_discount_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=20.0, shipping_cost=5.0, tax_rate=0.1)
        calc.add_item('A', 10.0, 2)
        total = calc.calculate_total()
        expected = 20.0 + 0.0 + 2.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_and_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=8.0, tax_rate=0.15)
        calc.add_item('B', 30.0, 2)
        total = calc.calculate_total(discount=0.1)
        shipping = 8.0
        tax = (54.0 + shipping) * 0.15
        expected = 54.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount(self):
        calc = OrderCalculator()
        calc.add_item('C', 5.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.2)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.2)

    def test_calculate_total_invalid_discount_type(self):
        calc = OrderCalculator()
        calc.add_item('D', 5.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='0.1')

    def test_calculate_total_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_total_items(self):
        calc = OrderCalculator()
        calc.add_item('X', 1.0, 3)
        calc.add_item('Y', 2.0, 2)
        self.assertEqual(calc.total_items(), 5)

    def test_clear_order(self):
        calc = OrderCalculator()
        calc.add_item('Z', 4.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])

    def test_list_items_unique(self):
        calc = OrderCalculator()
        calc.add_item('Alpha', 1.0, 1)
        calc.add_item('Beta', 2.0, 1)
        calc.add_item('Alpha', 1.0, 2)
        items = calc.list_items()
        self.assertCountEqual(items, ['Alpha', 'Beta'])

    def test_is_empty_true(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false(self):
        calc = OrderCalculator()
        calc.add_item('Gamma', 3.0, 1)
        self.assertFalse(calc.is_empty())