import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.tax_rate, 0.23)
        self.assertAlmostEqual(oc.free_shipping_threshold, 100.0)
        self.assertAlmostEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_tax_rate_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_shipping_params(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(oc.total_items(), 2)
        self.assertListEqual(oc.list_items(), ['Apple'])

    def test_add_item_merge_same(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8, 1)
        oc.add_item('Banana', 0.8, 3)
        self.assertEqual(oc.total_items(), 4)
        self.assertAlmostEqual(oc.get_subtotal(), 0.8 * 4)

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
            oc.add_item('Bread', 1.0, '2')
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Egg', 0.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Egg', -1.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Egg', 1.0, 0)

    def test_remove_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Cheese', 3.0, 2)
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

    def test_get_subtotal_success(self):
        oc = OrderCalculator()
        oc.add_item('ItemA', 10.0, 2)
        oc.add_item('ItemB', 5.5, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 10.0 * 2 + 5.5)

    def test_get_subtotal_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_success(self):
        oc = OrderCalculator()
        result = oc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_edge_cases(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(0.0, 0.0), 0.0)
        self.assertAlmostEqual(oc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_invalid_inputs(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            oc.apply_discount(100, '0.1')
        with self.assertRaises(ValueError):
            oc.apply_discount(-10, 0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(10, -0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(10, 1.5)

    def test_calculate_shipping_free(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=7.5)
        self.assertAlmostEqual(oc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_paid(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=12.0)
        self.assertAlmostEqual(oc.calculate_shipping(80.0), 12.0)

    def test_calculate_shipping_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('30')

    def test_calculate_tax_success(self):
        oc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(oc.calculate_tax(50.0), 10.0)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_invalid(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax(None)
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5.0)

    def test_calculate_total_no_discount_free_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=30.0, shipping_cost=5.0, tax_rate=0.1)
        oc.add_item('A', 10.0, 3)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 33.0)

    def test_calculate_total_with_discount_and_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=8.0, tax_rate=0.15)
        oc.add_item('B', 20.0, 2)
        total = oc.calculate_total(discount=0.25)
        self.assertAlmostEqual(total, 43.7, places=2)

    def test_calculate_total_invalid_discount(self):
        oc = OrderCalculator()
        oc.add_item('C', 5.0, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=1.5)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount='0.1')

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
        oc.add_item('Z', 3.0, 2)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)
        self.assertListEqual(oc.list_items(), [])

    def test_list_items_uniqueness(self):
        oc = OrderCalculator()
        oc.add_item('Alpha', 1.0, 1)
        oc.add_item('Beta', 2.0, 1)
        oc.add_item('Alpha', 1.0, 2)
        self.assertCountEqual(oc.list_items(), ['Alpha', 'Beta'])

    def test_is_empty(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())
        oc.add_item('Item', 1.0)
        self.assertFalse(oc.is_empty())
        oc.remove_item('Item')
        self.assertTrue(oc.is_empty())