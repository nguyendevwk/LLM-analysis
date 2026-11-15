import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_custom(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(oc.calculate_tax(1), 0.1, places=2)
        self.assertAlmostEqual(oc.calculate_shipping(49.99), 5.0, places=2)
        self.assertAlmostEqual(oc.calculate_shipping(50.0), 0.0, places=2)

    def test_init_invalid_negative_values(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_single(self):
        oc = OrderCalculator()
        oc.add_item('apple', 2.5, 3)
        self.assertEqual(oc.total_items(), 3)
        self.assertAlmostEqual(oc.get_subtotal(), 7.5, places=2)
        self.assertListEqual(oc.list_items(), ['apple'])
        self.assertFalse(oc.is_empty())

    def test_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('banana', 1.0)
        self.assertEqual(oc.total_items(), 1)
        self.assertAlmostEqual(oc.get_subtotal(), 1.0, places=2)

    def test_add_item_duplicate_name(self):
        oc = OrderCalculator()
        oc.add_item('apple', 2.0, 2)
        oc.add_item('apple', 2.0, 4)
        self.assertEqual(oc.total_items(), 6)
        self.assertAlmostEqual(oc.get_subtotal(), 12.0, places=2)

    def test_add_item_invalid_negative_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('orange', -1.0, 1)

    def test_add_item_invalid_zero_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('pear', 1.0, 0)

    def test_add_item_invalid_negative_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('pear', 1.0, -2)

    def test_remove_item_existing(self):
        oc = OrderCalculator()
        oc.add_item('apple', 2.0, 2)
        oc.add_item('banana', 1.0, 3)
        oc.remove_item('apple')
        self.assertFalse('apple' in oc.list_items())
        self.assertEqual(oc.total_items(), 3)
        self.assertAlmostEqual(oc.get_subtotal(), 3.0, places=2)

    def test_get_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('apple', 2.5, 2)
        oc.add_item('banana', 1.2, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 2.5 * 2 + 1.2 * 3, places=2)

    def test_apply_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(90.0), 10.0, places=2)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(100.0), 0.0, places=2)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(150.0), 0.0, places=2)

    def test_calculate_shipping_custom_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(oc.calculate_shipping(49.99), 5.0, places=2)
        self.assertAlmostEqual(oc.calculate_shipping(50.0), 0.0, places=2)

    def test_calculate_tax_positive(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(200.0), 46.0, places=2)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0, places=2)

    def test_calculate_tax_custom_rate(self):
        oc = OrderCalculator(tax_rate=0.08)
        self.assertAlmostEqual(oc.calculate_tax(100.0), 8.0, places=2)

    def test_calculate_total_no_discount_free_shipping(self):
        oc = OrderCalculator()
        oc.add_item('item', 60.0, 2)
        subtotal = oc.get_subtotal()
        shipping = oc.calculate_shipping(subtotal)
        tax = oc.calculate_tax(subtotal)
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(oc.calculate_total(), expected, places=2)

    def test_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 3)
        oc.add_item('banana', 2.0, 2)
        self.assertEqual(oc.total_items(), 5)

    def test_list_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 1)
        oc.add_item('banana', 2.0, 1)
        oc.add_item('cherry', 3.0, 1)
        self.assertSetEqual(set(oc.list_items()), {'apple', 'banana', 'cherry'})

    def test_list_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 1)
        oc.add_item('banana', 2.0, 1)
        oc.remove_item('apple')
        self.assertListEqual(oc.list_items(), ['banana'])

    def test_is_empty_fresh(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_add(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 1)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_edge_large_numbers(self):
        oc = OrderCalculator()
        oc.add_item('big', 1000000000.0, 1000)
        subtotal = oc.get_subtotal()
        self.assertAlmostEqual(subtotal, 1000000000000.0, places=2)
        total = oc.calculate_total()
        shipping = oc.calculate_shipping(subtotal)
        tax = oc.calculate_tax(subtotal)
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(total, expected, places=2)

    def test_edge_floating_point_rounding(self):
        oc = OrderCalculator()
        oc.add_item('tiny', 0.1, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 0.3, places=2)

    def test_edge_zero_quantity_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 1)
        oc.remove_item('apple')
        with self.assertRaises(ValueError):
            oc.add_item('apple', 1.0, 0)

    def test_edge_multiple_clear_calls(self):
        oc = OrderCalculator()
        oc.clear_order()
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)