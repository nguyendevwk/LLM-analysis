import unittest
from decimal import Decimal
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.oc = OrderCalculator()

    # Constructor tests
    def test_constructor_default(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_constructor_custom_valid(self):
        oc = OrderCalculator(tax_rate=0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(oc.tax_rate, 0)
        self.assertEqual(oc.free_shipping_threshold, 0)
        self.assertEqual(oc.shipping_cost, 0)

    def test_constructor_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_constructor_tax_rate_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_constructor_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_constructor_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_constructor_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_constructor_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_constructor_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    # add_item tests
    def test_add_item_normal(self):
        self.oc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(self.oc.items), 1)
        self.assertEqual(self.oc.items[0]['quantity'], 2)
        self.assertEqual(self.oc.total_items(), 2)

    def test_add_item_default_quantity(self):
        self.oc.add_item('Banana', 0.8)
        self.assertEqual(self.oc.items[0]['quantity'], 1)

    def test_add_item_merge_quantity(self):
        self.oc.add_item('Apple', 1.5, 2)
        self.oc.add_item('Apple', 1.5, 3)
        self.assertEqual(len(self.oc.items), 1)
        self.assertEqual(self.oc.items[0]['quantity'], 5)

    def test_add_item_same_name_different_price(self):
        self.oc.add_item('Apple', 1.5, 2)
        with self.assertRaises(ValueError):
            self.oc.add_item('Apple', 2.0, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.oc.add_item('', 1.0, 1)

    def test_add_item_name_wrong_type(self):
        with self.assertRaises(TypeError):
            self.oc.add_item(123, 1.0, 1)

    def test_add_item_price_zero(self):
        with self.assertRaises(ValueError):
            self.oc.add_item('Pear', 0, 1)

    def test_add_item_price_negative(self):
        with self.assertRaises(ValueError):
            self.oc.add_item('Pear', -1, 1)

    def test_add_item_price_wrong_type(self):
        with self.assertRaises(TypeError):
            self.oc.add_item('Pear', 'free', 1)

    def test_add_item_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.oc.add_item('Pear', 1.0, 0)

    def test_add_item_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.oc.add_item('Pear', 1.0, -3)

    def test_add_item_quantity_wrong_type(self):
        with self.assertRaises(TypeError):
            self.oc.add_item('Pear', 1.0, 2.5)

    def test_add_item_large_quantity(self):
        self.oc.add_item('Gadget', 9.99, 10000)
        self.assertEqual(self.oc.items[0]['quantity'], 10000)

    def test_add_item_price_int(self):
        self.oc.add_item('Widget', 5, 1)
        self.assertEqual(self.oc.items[0]['price'], 5)

    def test_add_item_name_whitespace(self):
        self.oc.add_item('   ', 1.0, 1)
        self.assertEqual(self.oc.items[0]['name'], '   ')

    # remove_item tests
    def test_remove_item_existing(self):
        self.oc.add_item('Apple', 1.5, 2)
        self.oc.add_item('Banana', 0.8, 3)
        self.oc.remove_item('Apple')
        self.assertFalse(any(i['name'] == 'Apple' for i in self.oc.items))
        self.assertTrue(any(i['name'] == 'Banana' for i in self.oc.items))

    def test_remove_item_nonexistent(self):
        self.oc.add_item('Banana', 0.8, 1)
        with self.assertRaises(ValueError):
            self.oc.remove_item('Apple')

    def test_remove_item_name_wrong_type(self):
        with self.assertRaises(TypeError):
            self.oc.remove_item(123)

    def test_remove_item_from_empty(self):
        with self.assertRaises(ValueError):
            self.oc.remove_item('Anything')

    def test_remove_item_multiple_entries_direct(self):
        self.oc.items = [
            {'name': 'Apple', 'price': 1.5, 'quantity': 2},
            {'name': 'Apple', 'price': 2.0, 'quantity': 1},
        ]
        self.oc.remove_item('Apple')
        self.assertFalse(any(i['name'] == 'Apple' for i in self.oc.items))

    # get_subtotal tests
    def test_get_subtotal_multiple_items(self):
        self.oc.add_item('Apple', 1.5, 2)
        self.oc.add_item('Banana', 0.8, 3)
        self.assertAlmostEqual(self.oc.get_subtotal(), 5.9)

    def test_get_subtotal_single_item(self):
        self.oc.add_item('X', 10, 1)
        self.assertAlmostEqual(self.oc.get_subtotal(), 10.0)

    def test_get_subtotal_floating_point_precision(self):
        self.oc.add_item('A', 0.1, 3)
        self.assertAlmostEqual(self.oc.get_subtotal(), 0.3)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.oc.get_subtotal()

    # apply_discount tests
    def test_apply_discount_no_discount(self):
        self.assertAlmostEqual(self.oc.apply_discount(100, 0), 100.0)

    def test_apply_discount_full(self):
        self.assertAlmostEqual(self.oc.apply_discount(100, 1), 0.0)

    def test_apply_discount_typical(self):
        self.assertAlmostEqual(self.oc.apply_discount(200, 0.2), 160.0)

    def test_apply_discount_lower_bound(self):
        self.assertAlmostEqual(self.oc.apply_discount(50, 0.0), 50.0)

    def test_apply_discount_upper_bound(self):
        self.assertAlmostEqual(self.oc.apply_discount(50, 1.0), 0.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.oc.apply_discount(50, -0.1)

    def test_apply_discount_over_one(self):
        with self.assertRaises(ValueError):
            self.oc.apply_discount(50, 1.5)

    def test_apply_discount_discount_wrong_type(self):
        with self.assertRaises(TypeError):
            self.oc.apply_discount(10, '0.1')

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.oc.apply_discount(-10, 0.1)

    def test_apply_discount_subtotal_wrong_type(self):
        with self.assertRaises(TypeError):
            self.oc.apply_discount('ten', 0.1)

    def test_apply_discount_zero_subtotal(self):
        self.assertAlmostEqual(self.oc.apply_discount(0, 0.5), 0.0)

    def test_apply_discount_large_subtotal(self):
        self.assertAlmostEqual(self.oc.apply_discount(1_000_000, 0.01), 990_000.0)

    # calculate_shipping tests
    def test_calculate_shipping_below_threshold(self):
        self.assertAlmostEqual(self.oc.calculate_shipping(90), 10.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertAlmostEqual(self.oc.calculate_shipping(100), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertAlmostEqual(self.oc.calculate_shipping(150), 0.0)

    def test_calculate_shipping_custom_zero_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=0)
        self.assertAlmostEqual(oc.calculate_shipping(5), 0.0)

    def test_calculate_shipping_custom_zero_cost(self):
        oc = OrderCalculator(shipping_cost=0)
        self.assertAlmostEqual(oc.calculate_shipping(50), 0.0)

    def test_calculate_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            self.oc.calculate_shipping('fifty')

    def test_calculate_shipping_negative_subtotal(self):
        self.assertAlmostEqual(self.oc.calculate_shipping(-5), 10.0)

    def test_calculate_shipping_large_subtotal(self):
        self.assertAlmostEqual(self.oc.calculate_shipping(1_000_000_000), 0.0)

    # calculate_tax tests
    def test_calculate_tax_normal(self):
        self.assertAlmostEqual(self.oc.calculate_tax(100), 23.0)

    def test_calculate_tax_zero(self):
        self.assertAlmostEqual(self.oc.calculate_tax(0), 0.0)

    def test_calculate_tax_custom_rate(self):
        oc = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(oc.calculate_tax(50), 5.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.oc.calculate_tax(-10)

    def test_calculate_tax_wrong_type(self):
        with self.assertRaises(TypeError):
            self.oc.calculate_tax('ten')

    def test_calculate_tax_large_amount(self):
        self.assertAlmostEqual(self.oc.calculate_tax(1_000_000_000), 230_000_000.0)

    def test_calculate_tax_rate_zero(self):
        oc = OrderCalculator(tax_rate=0)
        self.assertAlmostEqual(oc.calculate_tax(123), 0.0)

    def test_calculate_tax_rate_one(self):
        oc = OrderCalculator(tax_rate=1)
        self.assertAlmostEqual(oc.calculate_tax(45), 45.0)

    # calculate_total tests
    def test_calculate_total_simple_no_discount(self):
        self.oc.add_item('Apple', 10, 2)
        total = self.oc.calculate_total()
        self.assertAlmostEqual(total, 34.6)

    def test_calculate_total_discount_below_threshold(self):
        self.oc.add_item('A', 30, 2)  # subtotal 60
        total = self.oc.calculate_total(0.1)  # discounted 54
        self.assertAlmostEqual(total, 78.72)

    def test_calculate_total_discount_still_below_threshold(self):
        self.oc.add_item('B', 60, 2)  # subtotal 