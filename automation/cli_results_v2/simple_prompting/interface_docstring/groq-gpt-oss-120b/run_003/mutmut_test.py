import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)

    def test_init_custom_valid(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(oc.tax_rate, 0.1)
        self.assertEqual(oc.free_shipping_threshold, 50.0)
        self.assertEqual(oc.shipping_cost, 5.0)

    def test_init_invalid_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_normal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 3)
        self.assertEqual(oc.total_items(), 3)
        self.assertIn('Apple', oc.list_items())

    def test_add_item_merge_same(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.5, 2)
        oc.add_item('Banana', 0.5, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_add_item_conflict_price(self):
        oc = OrderCalculator()
        oc.add_item('Orange', 0.8, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Orange', 0.9, 1)

    def test_add_item_invalid_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0)

    def test_add_item_invalid_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Grape', 0)

    def test_add_item_invalid_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Kiwi', 1.0, 0)

    def test_add_item_wrong_types(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0)
        with self.assertRaises(TypeError):
            oc.add_item('Mango', '1.0')
        with self.assertRaises(TypeError):
            oc.add_item('Mango', 1.0, '2')

    def test_remove_item_existing(self):
        oc = OrderCalculator()
        oc.add_item('Peach', 2.0)
        oc.remove_item('Peach')
        self.assertTrue(oc.is_empty())

    def test_remove_item_nonexistent(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Nonexistent')

    def test_remove_item_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_get_subtotal_normal(self):
        oc = OrderCalculator()
        oc.add_item('ItemA', 10.0, 2)
        oc.add_item('ItemB', 5.0, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 25.0)

    def test_get_subtotal_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_normal(self):
        oc = OrderCalculator()
        result = oc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_edge_cases(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50.0, 0.0), 50.0)
        self.assertAlmostEqual(oc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_invalid(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10, 0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(10, -0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(10, 1.5)
        with self.assertRaises(TypeError):
            oc.apply_discount('10', 0.1)
        with self.assertRaises(TypeError):
            oc.apply_discount(10, '0.1')

    def test_calculate_shipping_free(self):
        oc = OrderCalculator(free_shipping_threshold=30.0, shipping_cost=7.0)
        self.assertAlmostEqual(oc.calculate_shipping(30.0), 0.0)
        self.assertAlmostEqual(oc.calculate_shipping(35.0), 0.0)

    def test_calculate_shipping_cost(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=12.5)
        self.assertAlmostEqual(oc.calculate_shipping(99.99), 12.5)

    def test_calculate_shipping_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('50')

    def test_calculate_tax_normal(self):
        oc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(oc.calculate_tax(50.0), 10.0)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_invalid(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5)
        with self.assertRaises(TypeError):
            oc.calculate_tax('5')

    def test_calculate_total_without_discount_shipping_applied(self):
        oc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=200.0, shipping_cost=20.0)
        oc.add_item('C', 50.0, 2)
        total = oc.calculate_total()
        subtotal = 100.0
        shipping = 20.0
        tax = (subtotal + shipping) * 0.15
        self.assertAlmostEqual(total, subtotal + shipping + tax)

    def test_calculate_total_invalid_discount(self):
        oc = OrderCalculator()
        oc.add_item('D', 10.0)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=1.2)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_total_items(self):
        oc = OrderCalculator()
        oc.add_item('X', 1.0, 4)
        oc.add_item('Y', 2.0, 3)
        self.assertEqual(oc.total_items(), 7)

    def test_clear_order(self):
        oc = OrderCalculator()
        oc.add_item('Z', 5.0, 2)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_list_items(self):
        oc = OrderCalculator()
        oc.add_item('Alpha', 1.0)
        oc.add_item('Beta', 2.0)
        oc.add_item('Alpha', 1.0, 2)
        self.assertCountEqual(oc.list_items(), ['Alpha', 'Beta'])

    def test_is_empty(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())
        oc.add_item('Gamma', 3.0)
        self.assertFalse(oc.is_empty())
        oc.remove_item('Gamma')
        self.assertTrue(oc.is_empty())