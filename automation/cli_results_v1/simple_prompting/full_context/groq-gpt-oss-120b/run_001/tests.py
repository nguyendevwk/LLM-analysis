import unittest
from temp_upload import OrderCalculator, Item

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

    def test_init_negative_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_success(self):
        self.calc.add_item('Apple', 1.5, 3)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['name'], 'Apple')
        self.assertEqual(self.calc.items[0]['price'], 1.5)
        self.assertEqual(self.calc.items[0]['quantity'], 3)

    def test_add_item_increment_quantity(self):
        self.calc.add_item('Banana', 0.8, 2)
        self.calc.add_item('Banana', 0.8, 5)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 7)

    def test_add_item_different_price_same_name(self):
        self.calc.add_item('Milk', 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Milk', 1.2, 1)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Bread', '1.0', 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Bread', -1.0, 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Egg', 0.2, 2.5)

    def test_add_item_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Egg', 0.2, 0)

    def test_remove_item_success(self):
        self.calc.add_item('Cheese', 2.5, 1)
        self.calc.remove_item('Cheese')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_success(self):
        self.calc.add_item('ItemA', 10.0, 2)
        self.calc.add_item('ItemB', 5.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10.0 * 2 + 5.0 * 3)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_success(self):
        result = self.calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_no_discount(self):
        result = self.calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(result, 50.0)

    def test_apply_discount_full_discount(self):
        result = self.calc.apply_discount(30.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

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
        self.calc.free_shipping_threshold = 50.0
        cost = self.calc.calculate_shipping(60.0)
        self.assertEqual(cost, 0.0)

    def test_calculate_shipping_cost(self):
        self.calc.free_shipping_threshold = 100.0
        cost = self.calc.calculate_shipping(80.0)
        self.assertEqual(cost, self.calc.shipping_cost)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('80')

    def test_calculate_tax_success(self):
        tax = self.calc.calculate_tax(200.0)
        self.assertAlmostEqual(tax, 200.0 * self.calc.tax_rate)

    def test_calculate_tax_zero(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertEqual(tax, 0.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax([100])

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5)

    def test_calculate_total_no_discount_free_shipping(self):
        self.calc.free_shipping_threshold = 0.0
        self.calc.add_item('Prod', 20.0, 2)
        total = self.calc.calculate_total()
        expected = 40.0 + self.calc.calculate_tax(40.0)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_and_shipping(self):
        self.calc.free_shipping_threshold = 100.0
        self.calc.add_item('Prod', 30.0, 2)
        total = self.calc.calculate_total(discount=0.1)
        shipping = self.calc.shipping_cost
        tax = self.calc.calculate_tax(54 + shipping)
        expected = 54 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount_type(self):
        self.calc.add_item('Prod', 10.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_calculate_total_invalid_discount_range(self):
        self.calc.add_item('Prod', 10.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.2)

    def test_total_items(self):
        self.calc.add_item('A', 1.0, 3)
        self.calc.add_item('B', 2.0, 5)
        self.assertEqual(self.calc.total_items(), 8)

    def test_clear_order(self):
        self.calc.add_item('X', 5.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.items, [])

    def test_list_items_unique(self):
        self.calc.add_item('Alpha', 1.0, 1)
        self.calc.add_item('Beta', 2.0, 1)
        self.calc.add_item('Alpha', 1.0, 2)
        names = self.calc.list_items()
        self.assertCountEqual(names, ['Alpha', 'Beta'])

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('Item', 1.0, 1)
        self.assertFalse(self.calc.is_empty())