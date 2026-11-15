import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)

    def test_init_custom(self):
        oc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(oc.tax_rate, 0.05)
        self.assertEqual(oc.free_shipping_threshold, 50.0)
        self.assertEqual(oc.shipping_cost, 5.0)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_single(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.2)
        self.assertIn('Apple', oc.list_items())
        self.assertEqual(oc.total_items(), 1)

    def test_add_item_multiple_distinct(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 0.5, 3)
        items = oc.list_items()
        self.assertIn('Apple', items)
        self.assertIn('Banana', items)
        self.assertEqual(oc.total_items(), 5)

    def test_add_item_duplicate_name_accumulate(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Apple', 1.0, 3)
        self.assertEqual(oc.total_items(), 5)
        self.assertEqual(oc.list_items().count('Apple'), 1)

    def test_add_item_duplicate_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.total_items(), 5)
        self.assertAlmostEqual(oc.get_subtotal(), 5.0, places=2)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0)

    def test_add_item_non_string_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(None, 1.0)

    def test_add_item_negative_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Apple', -0.99)

    def test_add_item_zero_price(self):
        oc = OrderCalculator()
        oc.add_item('FreeItem', 0.0, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 0.0, places=2)

    def test_add_item_negative_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 1.0, -2)

    def test_add_item_zero_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 1.0, 0)

    def test_add_item_non_int_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', 1.0, 2.5)

    def test_remove_item_existing(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.list_items(), [])
        self.assertAlmostEqual(oc.get_subtotal(), 0.0, places=2)

    def test_remove_item_one_of_several(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.add_item('Banana', 0.5)
        oc.remove_item('Apple')
        self.assertFalse(oc.is_empty())
        self.assertEqual(oc.list_items(), ['Banana'])

    def test_remove_item_nonexistent(self):
        oc = OrderCalculator()
        with self.assertRaises(KeyError):
            oc.remove_item('Cherry')

    def test_remove_item_empty_string(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('')

    def test_get_subtotal_empty(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.get_subtotal(), 0.0, places=2)

    def test_get_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.5, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 5.0, places=2)

    def test_get_subtotal_multiple_items_accumulated(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Apple', 1.0, 3)
        oc.add_item('Banana', 0.5, 4)
        self.assertAlmostEqual(oc.get_subtotal(), 7.0, places=2)

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50.0, 0.0), 50.0, places=2)

    def test_apply_discount_smaller(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100.0, 15.0), 85.0, places=2)

    def test_apply_discount_equal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(30.0, 30.0), 0.0, places=2)

    def test_apply_discount_larger_clamp(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(20.0, 50.0), 0.0, places=2)

    def test_apply_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -5.0)

    def test_apply_discount_non_numeric(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100.0, 'ten')

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(80.0), 10.0, places=2)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(100.0), 0.0, places=2)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(150.0), 0.0, places=2)

    def test_calculate_shipping_negative_subtotal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(-5.0), 10.0, places=2)

    def test_calculate_shipping_zero_subtotal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(0.0), 10.0, places=2)

    def test_calculate_tax_positive(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(100.0), 23.0, places=2)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0, places=2)

    def test_calculate_tax_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-10.0)

    def test_calculate_tax_non_numeric(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax('ten')

    def test_calculate_total_no_discount_below_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 40.0, 2)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 108.4, places=2)

    def test_calculate_total_no_discount_above_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 60.0, 2)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 147.6, places=2)

    def test_calculate_total_discount_below_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 35.0, 3)
        total = oc.calculate_total(discount=10.0)
        self.assertAlmostEqual(total, 126.85, places=2)

    def test_calculate_total_discount_to_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 30.0, 4)
        total = oc.calculate_total(discount=20.0)
        self.assertAlmostEqual(total, 123.0, places=2)

    def test_calculate_total_discount_to_zero(self):
        oc = OrderCalculator()
        oc.add_item('Item', 15.0, 2)
        total = oc.calculate_total(discount=30.0)
        self.assertAlmostEqual(total, 10.0, places=2)

    def test_calculate_total_discount_over_subtotal(self):
        oc = OrderCalculator()
        oc.add_item('Item', 15.0, 2)
        total = oc.calculate_total(discount=50.0)
        self.assertAlmostEqual(total, 10.0, places=2)

    def test_calculate_total_negative_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-5.0)

    def test_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_after_adding(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 0.5, 3)
        oc.add_item('Apple', 1.0, 1)
        self.assertEqual(oc.total_items(), 6)

    def test_total_items_after_removing(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 0.5, 3)
        oc.remove_item('Apple')
        self.assertEqual(oc.total_items(), 3)

    def test_clear_order_populated(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 0.5, 3)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.list_items(), [])
        self.assertAlmostEqual(oc.get_subtotal(), 0.0, places=2)
        self.assertEqual(oc.total_items(), 0)

    def test_clear_order_already_empty(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_list_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_list_items_distinct(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.add_item('Banana', 0.5)
        self.assertEqual(oc.list_items(), ['Apple', 'Banana'])

    def test_list_items_duplicate_name(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Apple', 1.0, 3)
        self.assertEqual(oc.list_items(), ['Apple'])

    def test_list_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.add_item('Banana', 0.5)
        oc.remove_item('Apple')
        self.assertEqual(oc.list_items(), ['Banana'])

    def test_is_empty_fresh(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_adding(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_removing_last(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_total_consistency_with_components(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 10.0, 3)
        oc.add_item('Banana', 5.0, 2)
        subtotal = oc.get_subtotal()
        discounted = oc.apply_discount(subtotal, 5.0)
        shipping = oc.calculate_shipping(discounted)
        tax = oc.calculate_tax(discounted)
        total = oc.calculate_total(discount=5.0)
        self.assertAlmostEqual(total, discounted + shipping + tax, places=2)

    def test_sequence_operations_consistency(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 10.0, 2)
        oc.add_item('Banana', 5.0, 1)
        oc.remove_item('Apple')
        oc.add_item('Cherry', 20.0, 1)
        total = oc.calculate_total(discount=5.0)
        subtotal = oc.get_subtotal()
        discounted = oc.apply_discount(subtotal, 5.0)
        shipping = oc.calculate_shipping(discounted)
        tax = oc.calculate_tax(discounted)
        self.assertAlmostEqual(total, discounted + shipping + tax, places=2)

    def test_large_quantity_and_price(self):
        oc = OrderCalculator()
        oc.add_item('Expensive', 9999.99, 1000)
        subtotal = oc.get_subtotal()
        self.assertAlmostEqual(subtotal, 9999990.0, places=2)

    def test_floating_point_rounding_edge(self):
        oc = OrderCalculator()
        oc.add_item('Weird', 0.3333, 3)
        subtotal = oc.get_subtotal()
        self.assertAlmostEqual(subtotal, 0.9999, places=4)

    def test_custom_free_shipping_threshold_zero(self):
        oc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=5.0)
        oc.add_item('Item', 10.0)
        self.assertAlmostEqual(oc.calculate_shipping(oc.get_subtotal()), 0.0, places=2)

    def test_custom_tax_rate_zero(self):
        oc = OrderCalculator(tax_rate=0.0)
        oc.add_item('Item', 100.0)
        self.assertAlmostEqual(oc.calculate_tax(oc.get_subtotal()), 0.0, places=2)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, oc.get_subtotal() + oc.calculate_shipping(oc.get_subtotal()), places=2)

    def test_custom_shipping_cost_zero(self):
        oc = OrderCalculator(shipping_cost=0.0)
        oc.add_item('Item', 50.0)
        self.assertAlmostEqual(oc.calculate_shipping(oc.get_subtotal()), 0.0, places=2)

    def test_custom_parameters_combination(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=7.5)
        oc.add_item('Item', 15.0, 3)
        total = oc.calculate_total(discount=5.0)
        discounted = oc.apply_discount(45.0, 5.0)
        shipping = oc.calculate_shipping(discounted)
        tax = oc.calculate_tax(discounted)
        self.assertAlmostEqual(shipping, 7.5, places=2)
        self.assertAlmostEqual(tax, 4.0, places=2)
        self.assertAlmostEqual(total, discounted + shipping + tax, places=2)