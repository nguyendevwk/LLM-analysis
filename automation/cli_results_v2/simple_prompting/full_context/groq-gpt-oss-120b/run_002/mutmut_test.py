import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

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
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_add_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(oc.total_items(), 2)
        self.assertIn('Apple', oc.list_items())

    def test_add_item_merge_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8, 1)
        oc.add_item('Banana', 0.8, 3)
        self.assertEqual(oc.total_items(), 4)

    def test_add_item_conflict_price(self):
        oc = OrderCalculator()
        oc.add_item('Milk', 2.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Milk', 2.5, 1)

    def test_add_item_invalid_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_invalid_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Bread', 0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Bread', -1, 1)

    def test_add_item_invalid_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Egg', 0.2, 0)

    def test_add_item_wrong_types(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            oc.add_item('Cheese', '1.0', 1)
        with self.assertRaises(TypeError):
            oc.add_item('Cheese', 1.0, 1.5)

    def test_remove_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Orange', 0.5, 5)
        oc.remove_item('Orange')
        self.assertTrue(oc.is_empty())

    def test_remove_item_not_found(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Nonexistent')

    def test_remove_item_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_get_subtotal_success(self):
        oc = OrderCalculator()
        oc.add_item('ItemA', 10, 2)
        oc.add_item('ItemB', 5, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 10 * 2 + 5 * 3)

    def test_get_subtotal_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_normal(self):
        oc = OrderCalculator()
        result = oc.apply_discount(200, 0.1)
        self.assertAlmostEqual(result, 180)

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50, 0.0), 50)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(80, 1.0), 0)

    def test_apply_discount_invalid_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, -0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(100, 1.5)

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10, 0.2)

    def test_apply_discount_wrong_types(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            oc.apply_discount(100, '0.1')

    def test_calculate_shipping_free(self):
        oc = OrderCalculator(free_shipping_threshold=50)
        self.assertEqual(oc.calculate_shipping(50), 0.0)
        self.assertEqual(oc.calculate_shipping(100), 0.0)

    def test_calculate_shipping_cost(self):
        oc = OrderCalculator(free_shipping_threshold=100, shipping_cost=15)
        self.assertEqual(oc.calculate_shipping(99.99), 15)

    def test_calculate_shipping_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('30')

    def test_calculate_tax_normal(self):
        oc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(oc.calculate_tax(100), 20)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_tax(0), 0)

    def test_calculate_tax_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5)

    def test_calculate_tax_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax(None)

    def test_calculate_total_no_discount_no_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=0)
        oc.add_item('A', 10, 2)
        total = oc.calculate_total()
        subtotal = 20
        tax = subtotal * oc.tax_rate
        self.assertAlmostEqual(total, subtotal + tax)

    def test_calculate_total_with_discount_and_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=100, shipping_cost=12)
        oc.add_item('B', 30, 2)
        total = oc.calculate_total(discount=0.1)
        shipping = 12
        tax = (54 + shipping) * oc.tax_rate
        expected = 54 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=50)
        oc.add_item('C', 25, 2)
        total = oc.calculate_total()
        tax = 50 * oc.tax_rate
        self.assertAlmostEqual(total, 50 + tax)

    def test_calculate_total_invalid_discount_type(self):
        oc = OrderCalculator()
        oc.add_item('D', 10, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount='0.1')

    def test_calculate_total_invalid_discount_value(self):
        oc = OrderCalculator()
        oc.add_item('E', 10, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-0.2)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=1.2)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('X', 1, 3)
        oc.add_item('Y', 2, 4)
        self.assertEqual(oc.total_items(), 7)

    def test_clear_order(self):
        oc = OrderCalculator()
        oc.add_item('Z', 5, 2)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.items, [])

    def test_list_items_unique(self):
        oc = OrderCalculator()
        oc.add_item('Alpha', 1, 1)
        oc.add_item('Beta', 2, 1)
        oc.add_item('Alpha', 1, 2)
        items = oc.list_items()
        self.assertCountEqual(items, ['Alpha', 'Beta'])

    def test_is_empty_true_false(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())
        oc.add_item('Gamma', 3, 1)
        self.assertFalse(oc.is_empty())