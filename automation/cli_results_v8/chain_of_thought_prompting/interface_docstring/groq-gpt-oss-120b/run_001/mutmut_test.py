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
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0.0)
        self.assertEqual(oc.shipping_cost, 0.0)

    def test_init_invalid_tax_rate_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_invalid_tax_rate_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_invalid_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_init_type_error_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_type_error_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_type_error_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    def test_add_item_basic(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(oc.total_items(), 2)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_add_item_quantity_default(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8)
        self.assertEqual(oc.total_items(), 1)
        self.assertCountEqual(oc.list_items(), ['Banana'])

    def test_add_item_quantity_aggregation(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.total_items(), 5)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_add_item_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Widget', 0.01, 10000)
        self.assertEqual(oc.total_items(), 10000)

    def test_add_item_price_many_decimals(self):
        oc = OrderCalculator()
        oc.add_item('Gadget', 0.333333, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 0.999999, places=6)

    def test_add_item_conflicting_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0, 1)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_name_not_string(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_price_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Banana', 0.0, 1)

    def test_add_item_price_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Banana', -0.5, 1)

    def test_add_item_price_not_numeric(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', '1.5', 1)

    def test_add_item_quantity_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Banana', 0.8, 0)

    def test_add_item_quantity_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Banana', 0.8, -3)

    def test_add_item_quantity_not_int(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', 1.5, 2.5)

    def test_add_item_quantity_boolean(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, True)
        self.assertEqual(oc.total_items(), 1)

    def test_add_item_none_argument(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(None, 1.0, 1)

    def test_remove_existing_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_remove_one_of_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Banana', 0.8, 3)
        oc.remove_item('Banana')
        self.assertCountEqual(oc.list_items(), ['Apple'])
        self.assertEqual(oc.total_items(), 2)

    def test_remove_nonexistent_raises(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            oc.remove_item('Orange')

    def test_remove_name_not_string(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_remove_after_clear(self):
        oc = OrderCalculator()
        oc.clear_order()
        with self.assertRaises(ValueError):
            oc.remove_item('Anything')

    def test_get_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Gadget', 99.99, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 99.99)

    def test_get_subtotal_large_numbers(self):
        oc = OrderCalculator()
        oc.add_item('Bulk', 1000000.0, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 2000000.0)

    def test_get_subtotal_empty_raises(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_no_discount(self):
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

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 0.1)

    def test_apply_discount_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -0.01)

    def test_apply_discount_discount_over_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, 1.5)

    def test_apply_discount_subtotal_not_numeric(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)

    def test_apply_discount_discount_not_numeric(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100.0, '0.1')

    def test_apply_discount_discount_boolean(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100.0, True), 0.0)

    def test_apply_discount_very_small(self):
        oc = OrderCalculator()
        result = oc.apply_discount(100.0, 1e-09)
        self.assertAlmostEqual(result, 100.0 - 1e-07, places=7)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_custom_below(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(oc.calculate_shipping(49.99), 5.0)

    def test_calculate_shipping_custom_at(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(oc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(-5.0), 10.0)

    def test_calculate_shipping_non_numeric(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('100')

    def test_calculate_shipping_very_large(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(1000000000.0), 0.0)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_positive_default(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(200.0), 46.0)

    def test_calculate_tax_custom_rate(self):
        oc = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(oc.calculate_tax(50.0), 5.0)

    def test_calculate_tax_very_small(self):
        oc = OrderCalculator()