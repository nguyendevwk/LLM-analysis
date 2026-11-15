import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
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
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertIn('Apple', self.calc.list_items())

    def test_add_item_increment_quantity(self):
        self.calc.add_item('Banana', 0.8, 1)
        self.calc.add_item('Banana', 0.8, 3)
        self.assertEqual(self.calc.total_items(), 4)

    def test_add_item_duplicate_different_price(self):
        self.calc.add_item('Milk', 2.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Milk', 2.5, 1)

    def test_add_item_invalid_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_invalid_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Bread', 0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Bread', -1, 1)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Egg', 0.2, 0)

    def test_add_item_type_errors(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('Cheese', '1.0', 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('Cheese', 1.0, '2')

    def test_remove_item_success(self):
        self.calc.add_item('Orange', 0.5, 2)
        self.calc.remove_item('Orange')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_not_found(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_success(self):
        self.calc.add_item('ItemA', 10.0, 2)
        self.calc.add_item('ItemB', 5.0, 1)
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

    def test_apply_discount_invalid_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_invalid_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, 1.5)

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
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_no_discount_free_shipping(self):
        self.calc.add_item('Prod1', 40.0, 2)
        self.calc.free_shipping_threshold = 70.0
        total = self.calc.calculate_total()
        expected_subtotal = 80.0
        expected_shipping = 0.0
        expected_tax = expected_subtotal * self.calc.tax_rate
        self.assertAlmostEqual(total, expected_subtotal + expected_shipping + expected_tax)

    def test_calculate_total_with_discount_and_shipping(self):
        self.calc.add_item('Prod2', 30.0, 1)
        self.calc.free_shipping_threshold = 100.0
        total = self.calc.calculate_total(discount=0.1)
        expected_subtotal = 27.0
        expected_shipping = self.calc.shipping_cost
        expected_tax = (expected_subtotal + expected_shipping) * self.calc.tax_rate
        self.assertAlmostEqual(total, expected_subtotal + expected_shipping + expected_tax)

    def test_calculate_total_invalid_discount(self):
        self.calc.add_item('Prod3', 10.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.2)

    def test_calculate_total_type_error(self):
        self.calc.add_item('Prod4', 5.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_total_items(self):
        self.calc.add_item('A', 1.0, 3)
        self.calc.add_item('B', 2.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_clear(self):
        self.calc.add_item('C', 1.0, 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order(self):
        self.calc.add_item('D', 2.0, 2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_unique(self):
        self.calc.add_item('E', 1.0, 1)
        self.calc.add_item('E', 1.0, 2)
        self.calc.add_item('F', 2.0, 1)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['E', 'F'])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('G', 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_remove(self):
        self.calc.add_item('H', 1.0, 1)
        self.calc.remove_item('H')
        self.assertTrue(self.calc.is_empty())