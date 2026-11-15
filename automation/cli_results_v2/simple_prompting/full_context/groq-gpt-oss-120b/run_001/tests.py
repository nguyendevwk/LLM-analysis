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

    def test_add_item_merge_quantity(self):
        self.calc.add_item('Banana', 0.8, 1)
        self.calc.add_item('Banana', 0.8, 3)
        self.assertEqual(self.calc.total_items(), 4)

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

    def test_remove_item_not_exists(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_success(self):
        self.calc.add_item('ItemA', 10.0, 2)
        self.calc.add_item('ItemB', 5.0, 1)
        self.assertEqual(self.calc.get_subtotal(), 25.0)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_normal(self):
        result = self.calc.apply_discount(100.0, 0.2)
        self.assertEqual(result, 80.0)

    def test_apply_discount_zero(self):
        self.assertEqual(self.calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        self.assertEqual(self.calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_invalid_subtotal_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)

    def test_apply_discount_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, '0.1')

    def test_apply_discount_invalid_discount_range(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, 1.5)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10, 0.1)

    def test_calculate_shipping_free(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_cost(self):
        self.assertEqual(self.calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50')

    def test_calculate_tax_normal(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax([100])

    def test_calculate_total_no_discount_free_shipping(self):
        self.calc.add_item('Prod', 120.0, 1)
        total = self.calc.calculate_total()
        expected = 120.0 + self.calc.calculate_tax(120.0)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_and_shipping(self):
        self.calc.add_item('Prod', 80.0, 1)
        total = self.calc.calculate_total(discount=0.1)
        discounted = 80.0 * 0.9
        shipping = 10.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount_type(self):
        self.calc.add_item('Prod', 10.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_calculate_total_invalid_discount_range(self):
        self.calc.add_item('Prod', 10.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.2)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.2)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_total_items(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order(self):
        self.calc.add_item('X', 5.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.items, [])

    def test_list_items_unique(self):
        self.calc.add_item('Item1', 1.0, 1)
        self.calc.add_item('Item2', 2.0, 1)
        self.calc.add_item('Item1', 1.0, 2)
        names = self.calc.list_items()
        self.assertCountEqual(names, ['Item1', 'Item2'])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_adding(self):
        self.calc.add_item('Z', 1.0, 1)
        self.assertFalse(self.calc.is_empty())