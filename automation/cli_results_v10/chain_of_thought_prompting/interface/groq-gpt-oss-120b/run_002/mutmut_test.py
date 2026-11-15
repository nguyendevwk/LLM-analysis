import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)

    def test_init_custom_config(self):
        oc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(oc.tax_rate, 0.05)
        self.assertEqual(oc.free_shipping_threshold, 50.0)
        self.assertEqual(oc.shipping_cost, 5.0)

    def test_init_zero_values(self):
        oc = OrderCalculator(tax_rate=0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(oc.tax_rate, 0)
        self.assertEqual(oc.free_shipping_threshold, 0)
        self.assertEqual(oc.shipping_cost, 0)

    def test_init_boundary_tax_rate(self):
        oc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(oc.tax_rate, 1.0)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_greater_than_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_single(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 1)
        self.assertCountEqual(oc.list_items(), ['Apple'])
        self.assertEqual(oc.total_items(), 1)
        self.assertAlmostEqual(oc.get_subtotal(), 2.0, places=2)

    def test_add_item_explicit_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 1.5, 3)
        self.assertCountEqual(oc.list_items(), ['Banana'])
        self.assertEqual(oc.total_items(), 3)
        self.assertAlmostEqual(oc.get_subtotal(), 4.5, places=2)

    def test_add_item_duplicate_name(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 2)
        oc.add_item('Apple', 2.0, 3)
        self.assertCountEqual(oc.list_items(), ['Apple'])
        self.assertEqual(oc.total_items(), 5)
        self.assertAlmostEqual(oc.get_subtotal(), 10.0, places=2)

    def test_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Pear', 1.0)
        self.assertEqual(oc.total_items(), 1)

    def test_add_item_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Grape', 0.1, 10000)
        self.assertEqual(oc.total_items(), 10000)
        self.assertAlmostEqual(oc.get_subtotal(), 1000.0, places=2)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_negative_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Orange', -5.0, 1)

    def test_add_item_negative_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Mango', 1.0, -2)

    def test_add_item_zero_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Mango', 1.0, 0)

    def test_remove_item_existing(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 1)
        oc.add_item('Banana', 1.5, 2)
        oc.remove_item('Apple')
        self.assertCountEqual(oc.list_items(), ['Banana'])
        self.assertEqual(oc.total_items(), 2)
        self.assertAlmostEqual(oc.get_subtotal(), 3.0, places=2)

    def test_get_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 2)
        oc.add_item('Banana', 1.5, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 2.0 * 2 + 1.5 * 3, places=2)

    def test_apply_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        result = oc.calculate_shipping(75.0)
        self.assertAlmostEqual(result, 10.0, places=2)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        result = oc.calculate_shipping(100.0)
        self.assertAlmostEqual(result, 0.0, places=2)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        result = oc.calculate_shipping(150.0)
        self.assertAlmostEqual(result, 0.0, places=2)

    def test_calculate_shipping_zero_subtotal(self):
        oc = OrderCalculator()
        result = oc.calculate_shipping(0.0)
        self.assertAlmostEqual(result, 10.0, places=2)

    def test_calculate_tax_positive_amount(self):
        oc = OrderCalculator()
        result = oc.calculate_tax(200.0)
        self.assertAlmostEqual(result, 46.0, places=2)

    def test_calculate_tax_zero_amount(self):
        oc = OrderCalculator()
        result = oc.calculate_tax(0.0)
        self.assertAlmostEqual(result, 0.0, places=2)

    def test_calculate_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5.0)

    def test_calculate_total_no_discount_below_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item1', 40.0, 2)
        total = oc.calculate_total()
        shipping = 10.0
        tax = (80.0 + shipping) * 0.23
        expected = 80.0 + shipping + tax
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_discount_free_shipping_exact(self):
        oc = OrderCalculator()
        oc.add_item('Item1', 100.0, 1)
        total = oc.calculate_total(discount=0.0)
        shipping = 0.0
        tax = (100.0 + shipping) * 0.23
        expected = 100.0 + shipping + tax
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_negative_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-5.0)

    def test_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 1.0, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_list_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.add_item('Banana', 2.0)
        oc.add_item('Cherry', 3.0)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana', 'Cherry'])

    def test_list_items_duplicate_additions(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('Apple', 1.0, 2)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_list_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_is_empty_fresh(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_add(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_add_remove_add_sequence(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.remove_item('Apple')
        oc.add_item('Apple', 1.0, 3)
        self.assertEqual(oc.total_items(), 3)
        self.assertAlmostEqual(oc.get_subtotal(), 3.0, places=2)

    def test_zero_shipping_cost(self):
        oc = OrderCalculator(shipping_cost=0.0)
        oc.add_item('Item', 20.0, 1)
        total = oc.calculate_total()
        discounted = 20.0
        shipping = 0.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected, places=2)

    def test_zero_free_shipping_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=0.0)
        oc.add_item('Item', 10.0, 1)
        shipping = oc.calculate_shipping(10.0)
        self.assertAlmostEqual(shipping, 0.0, places=2)

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 5.0)

    def test_rounding_consistency_across_methods(self):
        oc = OrderCalculator()
        oc.add_item('Item', 33.33, 3)
        subtotal = oc.get_subtotal()
        discounted = oc.apply_discount(subtotal, 0.0)
        shipping = oc.calculate_shipping(discounted)
        tax = oc.calculate_tax(discounted + shipping)
        total = oc.calculate_total()
        self.assertAlmostEqual(discounted + shipping + tax, total, places=2)