import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    # Constructor tests
    def test_constructor_default(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_constructor_custom_boundary(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0.0)
        self.assertEqual(oc.shipping_cost, 0.0)

    def test_constructor_invalid_tax_rate_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_constructor_invalid_tax_rate_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_constructor_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_constructor_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_constructor_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_constructor_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_constructor_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    # add_item tests
    def test_add_item_single_valid(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertIn('Apple', oc.list_items())
        self.assertEqual(oc.total_items(), 2)
        self.assertAlmostEqual(oc.get_subtotal(), 3.0)

    def test_add_item_second_distinct(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 0.8, 3)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana'])
        self.assertEqual(oc.total_items(), 5)
        self.assertAlmostEqual(oc.get_subtotal(), 5.4)

    def test_add_item_aggregation(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 4)
        self.assertEqual(oc.total_items(), 6)
        self.assertAlmostEqual(oc.get_subtotal(), 9.0)

    def test_add_item_same_name_different_price_error(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0, 1)

    def test_add_item_empty_name_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_zero_price_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 0.0, 1)

    def test_add_item_negative_price_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', -1.0, 1)

    def test_add_item_quantity_less_than_one_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 1.0, 0)

    def test_add_item_quantity_non_int_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Pear', 1.0, 2.5)

    def test_add_item_name_wrong_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_price_wrong_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Pear', '1.0', 1)

    def test_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Grape', 2.0)
        self.assertEqual(oc.total_items(), 1)
        self.assertAlmostEqual(oc.get_subtotal(), 2.0)

    def test_add_item_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Mango', 0.5, 10_000)
        self.assertEqual(oc.total_items(), 10_000)
        self.assertAlmostEqual(oc.get_subtotal(), 5_000.0)

    # remove_item tests
    def test_remove_item_existing(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 0.8, 3)
        oc.remove_item('Banana')
        self.assertNotIn('Banana', oc.list_items())
        self.assertEqual(oc.total_items(), 2)
        self.assertAlmostEqual(oc.get_subtotal(), 3.0)

    def test_remove_item_nonexistent_error(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        with self.assertRaises(ValueError):
            oc.remove_item('Orange')

    def test_remove_item_name_wrong_type_error(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        with self.assertRaises(TypeError):
            oc.remove_item(None)

    def test_remove_item_only_item_results_empty(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)

    # get_subtotal tests
    def test_get_subtotal_normal_order(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 0.8, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 5.4)

    def test_get_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 6.0)

    def test_get_subtotal_empty_order_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_get_subtotal_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 0.8, 3)
        oc.remove_item('Banana')
        self.assertAlmostEqual(oc.get_subtotal(), 3.0)

    def test_get_subtotal_after_clear_error(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.clear_order()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    # apply_discount tests
    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_typical(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(200.0, 0.15), 170.0)

    def test_apply_discount_subtotal_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_negative_subtotal_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 0.1)

    def test_apply_discount_discount_negative_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_over_one_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, 1.2)

    def test_apply_discount_sub