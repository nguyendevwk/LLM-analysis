import unittest
from order_calculator import OrderCalculator

class OrderCalculatorTest(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_invalid_tax_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_tax_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_success(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 3)

    def test_add_item_merge_quantity(self):
        self.calc.add_item('Banana', 0.5, 2)
        self.calc.add_item('Banana', 0.5, 4)
        self.assertEqual(self.calc.total_items(), 6)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item('Milk', 1.2)
        with self.assertRaises(ValueError):
            self.calc.add_item('Milk', 1.5)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Bread', -2.0)

    def test_add_item_zero_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Bread', 0)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Egg', 0.2, 0)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Cheese', '1.0')

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Cheese', 1.0, 2.5)

    def test_remove_item_success(self):
        self.calc.add_item('Orange', 0.8)
        self.calc.remove_item('Orange')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_not_found(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_success(self):
        self.calc.add_item('A', 2.0, 2)
        self.calc.add_item('B', 3.0, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.0)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_normal(self):
        result = self.calc.apply_discount(100, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(50, 0.0)
        self.assertAlmostEqual(result, 50.0)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(30, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_invalid_discount_high(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, 1.5)

    def test_apply_discount_invalid_discount_low(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, -0.1)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10, 0.1)

    def test_apply_discount_invalid_subtotal_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)

    def test_apply_discount_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, '0.1')

    def test_calculate_shipping_free(self):
        self.calc.free_shipping_threshold = 50
        cost = self.calc.calculate_shipping(50)
        self.assertEqual(cost, 0.0)

    def test_calculate_shipping_paid(self):
        self.calc.free_shipping_threshold = 100
        cost = self.calc.calculate_shipping(99.99)
        self.assertEqual(cost, self.calc.shipping_cost)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('10')

    def test_calculate_tax_normal(self):
        tax = self.calc.calculate_tax(200)
        self.assertAlmostEqual(tax, 200 * self.calc.tax_rate)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0), 0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax([100])

    def test_calculate_total_no_discount_no_shipping(self):
        self.calc.free_shipping_threshold = 0
        self.calc.add_item('X', 10, 2)
        total = self.calc.calculate_total()
        expected = 20 + self.calc.calculate_tax(20)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_and_shipping(self):
        self.calc.free_shipping_threshold = 100
        self.calc.add_item('Y', 30, 2)
        total = self.calc.calculate_total(discount=0.1)
        shipping = self.calc.shipping_cost
        tax = self.calc.calculate_tax(54 + shipping)
        expected = 54 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_full(self):
        self.calc.add_item('Z', 40, 1)
        total = self.calc.calculate_total(discount=1.0)
        shipping = self.calc.shipping_cost
        tax = self.calc.calculate_tax(shipping)
        expected = shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_invalid_discount_type(self):
        self.calc.add_item('A', 10)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.2')

    def test_calculate_total_invalid_discount_range(self):
        self.calc.add_item('A', 10)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.2)

    def test_total_items_counts_correctly(self):
        self.calc.add_item('Item1', 5, 3)
        self.calc.add_item('Item2', 2, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order_resets(self):
        self.calc.add_item('A', 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.items, [])

    def test_list_items_unique_names(self):
        self.calc.add_item('Apple', 1)
        self.calc.add_item('Apple', 1, 2)
        self.calc.add_item('Banana', 0.5)
        names = self.calc.list_items()
        self.assertCountEqual(names, ['Apple', 'Banana'])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_adding(self):
        self.calc.add_item('A', 1)
        self.assertFalse(self.calc.is_empty())