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

    def test_init_invalid_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(oc.total_items(), 2)
        self.assertListEqual(oc.list_items(), ['Apple'])

    def test_add_item_merge_same_name_price(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8, 1)
        oc.add_item('Banana', 0.8, 3)
        self.assertEqual(oc.total_items(), 4)
        self.assertListEqual(oc.list_items(), ['Banana'])

    def test_add_item_conflict_different_price(self):
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

    def test_add_item_invalid_types(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            oc.add_item('Cheese', '1.0', 1)
        with self.assertRaises(TypeError):
            oc.add_item('Cheese', 1.0, '2')

    def test_remove_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Juice', 3.0, 2)
        oc.remove_item('Juice')
        self.assertTrue(oc.is_empty())

    def test_remove_item_not_found(self):
        oc = OrderCalculator()
        oc.add_item('Soda', 1.0, 1)
        with self.assertRaises(ValueError):
            oc.remove_item('Water')

    def test_remove_item_invalid_type(self):
        oc = OrderCalculator()
        oc.add_item('Tea', 2.0, 1)
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_get_subtotal_success(self):
        oc = OrderCalculator()
        oc.add_item('ItemA', 10.0, 2)
        oc.add_item('ItemB', 5.5, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 25.5)

    def test_get_subtotal_empty_order(self):
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

    def test_apply_discount_invalid_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 0.2)

    def test_apply_discount_invalid_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, 1.5)

    def test_apply_discount_invalid_types(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            oc.apply_discount(100.0, '0.1')

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(50.0), oc.shipping_cost)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(oc.free_shipping_threshold), 0.0)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('100')

    def test_calculate_tax_normal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax([100])

    def test_calculate_total_no_discount_free_shipping(self):
        oc = OrderCalculator()
        oc.add_item('Prod1', 60.0, 1)
        oc.add_item('Prod2', 45.0, 1)
        total = oc.calculate_total()
        expected = 105.0 + oc.calculate_tax(105.0)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_and_shipping(self):
        oc = OrderCalculator()
        oc.add_item('Prod', 30.0, 2)
        total = oc.calculate_total(discount=0.1)
        shipping = oc.shipping_cost
        tax_base = 54 + shipping
        expected = 54 + shipping + oc.calculate_tax(tax_base)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount(self):
        oc = OrderCalculator()
        oc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-0.2)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=1.2)

    def test_calculate_total_invalid_discount_type(self):
        oc = OrderCalculator()
        oc.add_item('Item', 10.0, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount='0.1')

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0, 3)
        oc.add_item('B', 2.0, 2)
        self.assertEqual(oc.total_items(), 5)

    def test_clear_order_resets(self):
        oc = OrderCalculator()
        oc.add_item('X', 5.0, 1)
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
        oc.add_item('Z', 10.0, 1)
        self.assertFalse(oc.is_empty())
        oc.remove_item('Z')
        self.assertTrue(oc.is_empty())