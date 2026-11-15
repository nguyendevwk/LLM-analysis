import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.tax_rate, 0.23)
        self.assertAlmostEqual(calc.free_shipping_threshold, 100.0)
        self.assertAlmostEqual(calc.shipping_cost, 10.0)

    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.tax_rate, 0.1)
        self.assertAlmostEqual(calc.free_shipping_threshold, 50.0)
        self.assertAlmostEqual(calc.shipping_cost, 5.0)

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_tax_rate_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_typical(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.total_items(), 3)
        self.assertIn('Apple', calc.list_items())

    def test_add_item_merge_same_name_price(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.5, 2)
        calc.add_item('Banana', 0.5, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_add_item_same_name_different_price(self):
        calc = OrderCalculator()
        calc.add_item('Orange', 0.8, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Orange', 0.9, 1)

    def test_add_item_invalid_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    def test_add_item_invalid_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Grapes', 0)

    def test_add_item_invalid_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Mango', 2.0, 0)

    def test_add_item_type_errors(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)
        with self.assertRaises(TypeError):
            calc.add_item('Peach', '1.0')
        with self.assertRaises(TypeError):
            calc.add_item('Peach', 1.0, '2')

    def test_remove_item_typical(self):
        calc = OrderCalculator()
        calc.add_item('Kiwi', 1.5, 2)
        calc.remove_item('Kiwi')
        self.assertTrue(calc.is_empty())

    def test_remove_item_not_exists(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Nonexistent')

    def test_remove_item_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_typical(self):
        calc = OrderCalculator()
        calc.add_item('ItemA', 10.0, 2)
        calc.add_item('ItemB', 5.0, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 10.0 * 2 + 5.0 * 3)

    def test_get_subtotal_empty(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_typical(self):
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
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_invalid_discount_range(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.5)

    def test_apply_discount_type_errors(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            calc.apply_discount(100, '0.1')

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(80.0), calc.shipping_cost)

    def test_calculate_shipping_at_threshold(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(calc.free_shipping_threshold), 0.0)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('100')

    def test_calculate_tax_typical(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100.0), 100.0 * calc.tax_rate)

    def test_calculate_tax_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax(None)

    def test_calculate_total_typical_with_shipping_and_tax(self):
        calc = OrderCalculator()
        calc.add_item('A', 30.0, 2)
        calc.add_item('B', 20.0, 3)
        total = calc.calculate_total(discount=0.2)
        expected_shipping = calc.shipping_cost
        expected_tax = (96 + expected_shipping) * calc.tax_rate
        expected_total = 96 + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('C', 50.0, 3)
        total = calc.calculate_total()
        expected_shipping = 0.0
        expected_tax = (150 + expected_shipping) * calc.tax_rate
        expected_total = 150 + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_full_discount(self):
        calc = OrderCalculator()
        calc.add_item('D', 40.0, 2)
        total = calc.calculate_total(discount=1.0)
        expected_shipping = calc.shipping_cost
        expected_tax = (0 + expected_shipping) * calc.tax_rate
        expected_total = 0 + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_invalid_discount(self):
        calc = OrderCalculator()
        calc.add_item('E', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.2)

    def test_calculate_total_discount_type_error(self):
        calc = OrderCalculator()
        calc.add_item('F', 5.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='0.1')

    def test_total_items(self):
        calc = OrderCalculator()
        calc.add_item('G', 2.0, 4)
        calc.add_item('H', 3.0, 1)
        self.assertEqual(calc.total_items(), 5)

    def test_clear_order(self):
        calc = OrderCalculator()
        calc.add_item('I', 1.0, 2)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.total_items(), 0)

    def test_list_items_unique(self):
        calc = OrderCalculator()
        calc.add_item('J', 1.0, 1)
        calc.add_item('J', 1.0, 2)
        calc.add_item('K', 2.0, 1)
        items = calc.list_items()
        self.assertCountEqual(items, ['J', 'K'])

    def test_is_empty_true(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false(self):
        calc = OrderCalculator()
        calc.add_item('L', 5.0, 1)
        self.assertFalse(calc.is_empty())