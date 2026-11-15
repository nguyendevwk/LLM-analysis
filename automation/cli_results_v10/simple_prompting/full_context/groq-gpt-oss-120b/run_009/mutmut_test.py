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

    def test_init_custom_parameters(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(oc.tax_rate, 0.1)
        self.assertEqual(oc.free_shipping_threshold, 50)
        self.assertEqual(oc.shipping_cost, 5)

    def test_init_invalid_tax_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_tax_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)
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

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Bread', '1.0', 1)

    def test_add_item_nonpositive_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Bread', 0, 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Egg', 0.2, 1.5)

    def test_add_item_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Egg', 0.2, 0)

    def test_remove_item_success(self):
        self.calc.add_item('Cheese', 3.0, 1)
        self.calc.remove_item('Cheese')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_success(self):
        self.calc.add_item('ItemA', 10, 2)
        self.calc.add_item('ItemB', 5, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10 * 2 + 5 * 3)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_normal(self):
        result = self.calc.apply_discount(200, 0.1)
        self.assertAlmostEqual(result, 180)

    def test_apply_discount_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 0.0), 100)

    def test_apply_discount_full(self):
        self.assertAlmostEqual(self.calc.apply_discount(50, 1.0), 0)

    def test_apply_discount_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, '0.1')

    def test_apply_discount_invalid_discount_value(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, 1.5)

    def test_apply_discount_invalid_subtotal_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10, 0.1)

    def test_calculate_shipping_free(self):
        self.calc.free_shipping_threshold = 50
        self.assertEqual(self.calc.calculate_shipping(60), 0.0)

    def test_calculate_shipping_cost(self):
        self.calc.free_shipping_threshold = 100
        self.assertEqual(self.calc.calculate_shipping(80), self.calc.shipping_cost)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('80')

    def test_calculate_tax_normal(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100), 23.0)

    def test_calculate_tax_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0), 0.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax(None)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5)

    def test_calculate_total_no_discount_no_shipping(self):
        self.calc.add_item('A', 60, 1)
        self.calc.add_item('B', 50, 1)
        total = self.calc.calculate_total()
        expected_subtotal = 110
        expected_discounted = 110
        expected_tax = expected_discounted * self.calc.tax_rate
        self.assertAlmostEqual(total, expected_discounted + expected_tax)

    def test_calculate_total_with_discount_and_shipping(self):
        self.calc.add_item('A', 30, 1)
        self.calc.add_item('B', 20, 1)
        total = self.calc.calculate_total(discount=0.1)
        discounted = 45
        shipping = self.calc.shipping_cost
        tax = (discounted + shipping) * self.calc.tax_rate
        self.assertAlmostEqual(total, discounted + shipping + tax)

    def test_calculate_total_invalid_discount_type(self):
        self.calc.add_item('A', 10, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_calculate_total_invalid_discount_value(self):
        self.calc.add_item('A', 10, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.2)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_total_items(self):
        self.calc.add_item('X', 5, 2)
        self.calc.add_item('Y', 3, 4)
        self.assertEqual(self.calc.total_items(), 6)

    def test_total_items_after_removal(self):
        self.calc.add_item('X', 5, 2)
        self.calc.add_item('Y', 3, 4)
        self.calc.remove_item('X')
        self.assertEqual(self.calc.total_items(), 4)

    def test_clear_order(self):
        self.calc.add_item('Z', 1, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.items, [])

    def test_list_items_unique(self):
        self.calc.add_item('Item1', 2, 1)
        self.calc.add_item('Item2', 3, 1)
        self.calc.add_item('Item1', 2, 2)
        names = self.calc.list_items()
        self.assertCountEqual(names, ['Item1', 'Item2'])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('Something', 1, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('Something', 1, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())