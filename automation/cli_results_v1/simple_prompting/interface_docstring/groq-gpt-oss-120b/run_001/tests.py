import unittest
from temp_upload import OrderCalculator, Item

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_invalid_tax_rate_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_invalid_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_invalid_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertFalse(oc.is_empty())
        self.assertEqual(oc.total_items(), 2)
        self.assertListEqual(oc.list_items(), ['Apple'])
        self.assertAlmostEqual(oc.get_subtotal(), 3.0)

    def test_add_item_increment_quantity_same_name_price(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8, 1)
        oc.add_item('Banana', 0.8, 3)
        self.assertEqual(oc.total_items(), 4)
        self.assertAlmostEqual(oc.get_subtotal(), 0.8 * 4)

    def test_add_item_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Milk', 1.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Milk', 1.2, 1)

    def test_add_item_invalid_name_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_invalid_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Bread', 0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Bread', -2.5, 1)

    def test_add_item_invalid_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Egg', 0.2, 0)
        with self.assertRaises(ValueError):
            oc.add_item('Egg', 0.2, -3)

    def test_add_item_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            oc.add_item('Cheese', '1.0', 1)
        with self.assertRaises(TypeError):
            oc.add_item('Cheese', 1.0, '2')

    def test_remove_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Orange', 0.5, 5)
        oc.remove_item('Orange')
        self.assertTrue(oc.is_empty())

    def test_remove_item_not_exists(self):
        oc = OrderCalculator()
        oc.add_item('Grapes', 2.0, 1)
        with self.assertRaises(ValueError):
            oc.remove_item('Pineapple')

    def test_remove_item_invalid_type(self):
        oc = OrderCalculator()
        oc.add_item('Kiwi', 1.0, 1)
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_get_subtotal_success(self):
        oc = OrderCalculator()
        oc.add_item('ItemA', 10.0, 2)
        oc.add_item('ItemB', 5.5, 3)
        expected = 10.0 * 2 + 5.5 * 3
        self.assertAlmostEqual(oc.get_subtotal(), expected)

    def test_get_subtotal_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_success(self):
        oc = OrderCalculator()
        result = oc.apply_discount(200.0, 0.15)
        self.assertAlmostEqual(result, 170.0)

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(80.0, 1.0), 0.0)

    def test_apply_discount_invalid_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 0.1)

    def test_apply_discount_invalid_discount_range(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, 1.2)

    def test_apply_discount_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            oc.apply_discount(100.0, '0.1')

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

    def test_calculate_tax_success(self):
        oc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(oc.calculate_tax(150.0), 30.0)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_invalid_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax([100])

    def test_calculate_total_no_discount_free_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=30.0, shipping_cost=5.0, tax_rate=0.1)
        oc.add_item('Prod1', 15.0, 2)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 33.0)

    def test_calculate_total_with_discount_and_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=8.0, tax_rate=0.15)
        oc.add_item('Prod2', 20.0, 3)
        total = oc.calculate_total(discount=0.2)
        expected = 48.0 + 8.0 + 8.4
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount_range(self):
        oc = OrderCalculator()
        oc.add_item('Prod3', 10.0, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=1.5)

    def test_calculate_total_invalid_discount_type(self):
        oc = OrderCalculator()
        oc.add_item('Prod4', 5.0, 2)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount='0.1')

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_total_items_counts_correctly(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0, 2)
        oc.add_item('B', 2.0, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_clear_order_resets_state(self):
        oc = OrderCalculator()
        oc.add_item('X', 3.0, 4)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)
        self.assertListEqual(oc.list_items(), [])

    def test_list_items_unique_names(self):
        oc = OrderCalculator()
        oc.add_item('Item1', 1.0, 1)
        oc.add_item('Item2', 2.0, 1)
        oc.add_item('Item1', 1.0, 2)
        self.assertCountEqual(oc.list_items(), ['Item1', 'Item2'])

    def test_is_empty_true_and_false(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())
        oc.add_item('Z', 9.9, 1)
        self.assertFalse(oc.is_empty())