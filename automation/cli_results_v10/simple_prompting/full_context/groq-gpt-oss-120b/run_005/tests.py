import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_init_custom_valid(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(oc.tax_rate, 0.1)
        self.assertEqual(oc.free_shipping_threshold, 50)
        self.assertEqual(oc.shipping_cost, 5)

    def test_init_invalid_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_init_invalid_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_new(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['name'], 'Apple')
        self.assertEqual(oc.items[0]['price'], 1.5)
        self.assertEqual(oc.items[0]['quantity'], 2)

    def test_add_item_merge(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.5, 3)
        oc.add_item('Banana', 0.5, 2)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['quantity'], 5)

    def test_add_item_conflict_price(self):
        oc = OrderCalculator()
        oc.add_item('Milk', 2.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Milk', 2.5, 1)

    def test_add_item_invalid_inputs(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            oc.add_item('Bread', '1.0', 1)
        with self.assertRaises(TypeError):
            oc.add_item('Bread', 1.0, 1.5)
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Egg', 0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Egg', -1, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Egg', 1.0, 0)

    def test_remove_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Cheese', 3.0, 1)
        oc.remove_item('Cheese')
        self.assertTrue(oc.is_empty())

    def test_remove_item_not_found(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Nonexistent')

    def test_remove_item_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_get_subtotal_normal(self):
        oc = OrderCalculator()
        oc.add_item('Item1', 10, 2)
        oc.add_item('Item2', 5, 3)
        self.assertEqual(oc.get_subtotal(), 10 * 2 + 5 * 3)

    def test_get_subtotal_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_normal(self):
        oc = OrderCalculator()
        result = oc.apply_discount(100, 0.2)
        self.assertEqual(result, 80)

    def test_apply_discount_bounds(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(50, 0), 50)
        self.assertEqual(oc.apply_discount(50, 1), 0)

    def test_apply_discount_invalid(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            oc.apply_discount(100, '0.1')
        with self.assertRaises(ValueError):
            oc.apply_discount(-10, 0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(100, -0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(100, 1.5)

    def test_calculate_shipping_free(self):
        oc = OrderCalculator(free_shipping_threshold=50)
        self.assertEqual(oc.calculate_shipping(60), 0.0)

    def test_calculate_shipping_cost(self):
        oc = OrderCalculator(free_shipping_threshold=100, shipping_cost=7)
        self.assertEqual(oc.calculate_shipping(80), 7)

    def test_calculate_shipping_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('100')

    def test_calculate_tax_normal(self):
        oc = OrderCalculator(tax_rate=0.2)
        self.assertEqual(oc.calculate_tax(100), 20)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_tax(0), 0)

    def test_calculate_tax_invalid(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax('100')
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5)

    def test_calculate_total_no_discount_no_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=0)
        oc.add_item('A', 10, 2)
        total = oc.calculate_total()
        subtotal = 20
        tax = subtotal * oc.tax_rate
        self.assertAlmostEqual(total, subtotal + tax)

    def test_calculate_total_with_discount_and_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=100, shipping_cost=5)
        oc.add_item('B', 30, 2)
        total = oc.calculate_total(discount=0.1)
        shipping = 5
        tax = (54 + shipping) * oc.tax_rate
        expected = 54 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_full(self):
        oc = OrderCalculator()
        oc.add_item('C', 20, 1)
        total = oc.calculate_total(discount=1.0)
        shipping = oc.shipping_cost
        tax = shipping * oc.tax_rate
        expected = shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount(self):
        oc = OrderCalculator()
        oc.add_item('D', 10, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount='0.1')
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=1.5)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_total_items(self):
        oc = OrderCalculator()
        oc.add_item('X', 1, 3)
        oc.add_item('Y', 2, 2)
        self.assertEqual(oc.total_items(), 5)

    def test_clear_order(self):
        oc = OrderCalculator()
        oc.add_item('Z', 5, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(len(oc.items), 0)

    def test_list_items_unique(self):
        oc = OrderCalculator()
        oc.add_item('Alpha', 1, 1)
        oc.add_item('Beta', 2, 1)
        oc.add_item('Alpha', 1, 2)
        names = oc.list_items()
        self.assertCountEqual(names, ['Alpha', 'Beta'])

    def test_is_empty(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())
        oc.add_item('Item', 1, 1)
        self.assertFalse(oc.is_empty())
        oc.clear_order()
        self.assertTrue(oc.is_empty())