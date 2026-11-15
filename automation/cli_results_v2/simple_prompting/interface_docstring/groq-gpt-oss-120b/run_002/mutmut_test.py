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
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_normal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(oc.total_items(), 2)
        self.assertListEqual(oc.list_items(), ['Apple'])

    def test_add_item_increment_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8, 1)
        oc.add_item('Banana', 0.8, 3)
        self.assertEqual(oc.total_items(), 4)
        self.assertAlmostEqual(oc.get_subtotal(), 0.8 * 4)

    def test_add_item_conflicting_price(self):
        oc = OrderCalculator()
        oc.add_item('Milk', 2.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Milk', 2.5, 1)

    def test_add_item_invalid_inputs(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            oc.add_item('Egg', '1.0', 1)
        with self.assertRaises(TypeError):
            oc.add_item('Egg', 1.0, '2')
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Egg', 0.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Egg', -1.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Egg', 1.0, 0)

    def test_remove_item_existing(self):
        oc = OrderCalculator()
        oc.add_item('Bread', 2.5, 2)
        oc.remove_item('Bread')
        self.assertTrue(oc.is_empty())

    def test_remove_item_nonexistent(self):
        oc = OrderCalculator()
        oc.add_item('Cheese', 3.0, 1)
        with self.assertRaises(ValueError):
            oc.remove_item('Ham')

    def test_remove_item_invalid_type(self):
        oc = OrderCalculator()
        oc.add_item('Yogurt', 1.2, 1)
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_get_subtotal_normal(self):
        oc = OrderCalculator()
        oc.add_item('ItemA', 10.0, 1)
        oc.add_item('ItemB', 5.0, 3)
        expected = 10.0 * 1 + 5.0 * 3
        self.assertAlmostEqual(oc.get_subtotal(), expected)

    def test_get_subtotal_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_normal(self):
        oc = OrderCalculator()
        result = oc.apply_discount(200.0, 0.1)
        self.assertAlmostEqual(result, 180.0)

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(80.0, 1.0), 0.0)

    def test_apply_discount_invalid_values(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(10.0, -0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(10.0, 1.5)

    def test_apply_discount_invalid_types(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            oc.apply_discount(100, '0.1')

    def test_calculate_shipping_free(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=7.5)
        self.assertAlmostEqual(oc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_cost(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=12.0)
        self.assertAlmostEqual(oc.calculate_shipping(80.0), 12.0)

    def test_calculate_shipping_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('30')

    def test_calculate_tax_normal(self):
        oc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(oc.calculate_tax(100.0), 20.0)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax([100])

    def test_calculate_total_without_discount_free_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=30.0, shipping_cost=5.0, tax_rate=0.1)
        oc.add_item('A', 10.0, 2)
        oc.add_item('B', 15.0, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 38.5)

    def test_calculate_total_with_discount_and_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=8.0, tax_rate=0.15)
        oc.add_item('X', 20.0, 2)
        oc.add_item('Y', 30.0, 1)
        total = oc.calculate_total(discount=0.1)
        self.assertAlmostEqual(total, 81.65, places=2)

    def test_calculate_total_invalid_discount(self):
        oc = OrderCalculator()
        oc.add_item('Z', 10.0, 1)
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
        oc.add_item('Item1', 5.0, 3)
        oc.add_item('Item2', 2.0, 2)
        self.assertEqual(oc.total_items(), 5)

    def test_clear_order(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)
        self.assertListEqual(oc.list_items(), [])

    def test_list_items_unique(self):
        oc = OrderCalculator()
        oc.add_item('Alpha', 1.0, 1)
        oc.add_item('Beta', 2.0, 1)
        oc.add_item('Alpha', 1.0, 2)
        self.assertCountEqual(oc.list_items(), ['Alpha', 'Beta'])

    def test_is_empty_initial_and_after_operations(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())
        oc.add_item('Item', 1.0, 1)
        self.assertFalse(oc.is_empty())
        oc.remove_item('Item')
        self.assertTrue(oc.is_empty())