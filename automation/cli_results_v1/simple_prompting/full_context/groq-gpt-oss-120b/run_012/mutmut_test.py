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

    def test_init_custom_valid(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(oc.tax_rate, 0.1)
        self.assertEqual(oc.free_shipping_threshold, 50)
        self.assertEqual(oc.shipping_cost, 5)

    def test_init_invalid_tax_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_tax_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_free_shipping_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_invalid_free_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_invalid_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_success(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 2)

    def test_add_item_increment_quantity(self):
        self.calc.add_item('Banana', 0.8, 1)
        self.calc.add_item('Banana', 0.8, 3)
        self.assertEqual(self.calc.items[0]['quantity'], 4)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item('Milk', 2.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Milk', 2.5, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Bread', 0, 1)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Egg', 0.2, 0)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Cheese', '1.0', 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Butter', 1.0, 1.5)

    def test_remove_item_success(self):
        self.calc.add_item('Orange', 0.5, 5)
        self.calc.remove_item('Orange')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_success(self):
        self.calc.add_item('Item1', 10, 2)
        self.calc.add_item('Item2', 5, 3)
        self.assertEqual(self.calc.get_subtotal(), 10 * 2 + 5 * 3)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_typical(self):
        result = self.calc.apply_discount(200, 0.1)
        self.assertAlmostEqual(result, 180)

    def test_apply_discount_zero(self):
        self.assertEqual(self.calc.apply_discount(100, 0.0), 100)

    def test_apply_discount_full(self):
        self.assertEqual(self.calc.apply_discount(50, 1.0), 0)

    def test_apply_discount_invalid_discount_low(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, -0.1)

    def test_apply_discount_invalid_discount_high(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, 1.5)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10, 0.2)

    def test_apply_discount_invalid_subtotal_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)

    def test_apply_discount_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, '0.1')

    def test_calculate_shipping_free(self):
        self.calc.free_shipping_threshold = 50
        self.assertEqual(self.calc.calculate_shipping(50), 0.0)
        self.assertEqual(self.calc.calculate_shipping(60), 0.0)

    def test_calculate_shipping_cost(self):
        self.calc.free_shipping_threshold = 100
        self.calc.shipping_cost = 15
        self.assertEqual(self.calc.calculate_shipping(99.99), 15)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('100')

    def test_calculate_tax_typical(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200), 200 * self.calc.tax_rate)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0), 0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax(None)

    def test_calculate_total_with_discount_and_shipping(self):
        self.calc.add_item('C', 30, 2)
        total = self.calc.calculate_total(discount=0.1)
        expected = 54 + self.calc.shipping_cost + (54 + self.calc.shipping_cost) * self.calc.tax_rate
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount_type(self):
        self.calc.add_item('D', 10, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_calculate_total_invalid_discount_range(self):
        self.calc.add_item('E', 10, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.5)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_total_items(self):
        self.calc.add_item('X', 5, 3)
        self.calc.add_item('Y', 2, 4)
        self.assertEqual(self.calc.total_items(), 7)

    def test_clear_order(self):
        self.calc.add_item('Z', 1, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(len(self.calc.items), 0)

    def test_list_items_unique(self):
        self.calc.add_item('Alpha', 1, 1)
        self.calc.add_item('Beta', 2, 1)
        self.calc.add_item('Alpha', 1, 2)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['Alpha', 'Beta'])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_adding(self):
        self.calc.add_item('Gamma', 3, 1)
        self.assertFalse(self.calc.is_empty())