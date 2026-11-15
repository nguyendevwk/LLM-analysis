import unittest
from temp_upload import OrderCalculator, Item

class TestOrderCalculator(unittest.TestCase):

    def test_default_constructor_sets_correct_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_custom_constructor_stores_values(self):
        calc = OrderCalculator(tax_rate=0.10, free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(calc.tax_rate, 0.10)
        self.assertEqual(calc.free_shipping_threshold, 50)
        self.assertEqual(calc.shipping_cost, 5)

    def test_constructor_negative_values_raise(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_increases_total_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 3)
        self.assertEqual(calc.total_items(), 3)
        self.assertIn('Apple', calc.list_items())

    def test_add_item_defaults_quantity_to_one(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.8)
        self.assertEqual(calc.total_items(), 1)
        self.assertIn('Banana', calc.list_items())

    def test_add_duplicate_item_sums_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 5)
        self.assertEqual(calc.total_items(), 7)
        self.assertEqual(len(calc.list_items()), 1)

    def test_add_item_price_int_is_accepted(self):
        calc = OrderCalculator()
        calc.add_item('Pear', 2, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0, places=2)

    def test_add_item_non_string_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_add_item_negative_price_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Orange', -5.0, 1)

    def test_add_item_zero_price_is_accepted(self):
        calc = OrderCalculator()
        calc.add_item('Freebie', 0.0, 2)
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 0.0, places=2)

    def test_add_item_negative_quantity_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Grape', 1.0, -2)

    def test_add_item_zero_quantity_is_ignored(self):
        calc = OrderCalculator()
        calc.add_item('ZeroQty', 1.0, 0)
        self.assertEqual(calc.total_items(), 0)
        self.assertNotIn('ZeroQty', calc.list_items())

    def test_remove_existing_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())
        self.assertNotIn('Apple', calc.list_items())

    def test_remove_item_removes_merged_entry(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 4)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_remove_nonexistent_item_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(KeyError):
            calc.remove_item('Banana')

    def test_remove_item_from_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(KeyError):
            calc.remove_item('Apple')

    def test_get_subtotal_empty_order(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.get_subtotal(), 0.0, places=2)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Item', 2.5, 4)
        self.assertAlmostEqual(calc.get_subtotal(), 10.0, places=2)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 2.5, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 1.0*2 + 2.5*3, places=2)

    def test_get_subtotal_zero_price_and_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Free', 0.0, 5)
        calc.add_item('ZeroQty', 1.0, 0)
        self.assertAlmostEqual(calc.get_subtotal(), 0.0, places=2)

    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100.0, 10.0)
        self.assertAlmostEqual(result, 90.0, places=2)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100.0, 0.0)
        self.assertAlmostEqual(result, 100.0, places=2)

    def test_apply_discount_equal_subtotal(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100.0, 100.0)
        self.assertAlmostEqual(result, 0.0, places=2)

    def test_apply_discount_greater_than_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(80.0, 120.0)

    def test_apply_discount_negative_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(80.0), 10.0, places=2)

    def test_calculate_shipping_at_threshold(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(100.0), 0.0, places=2)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(150.0), 0.0, places=2)

    def test_calculate_shipping_custom_config(self):
        calc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        self.assertAlmostEqual(calc.calculate_shipping(40.0), 5.0, places=2)
        self.assertAlmostEqual(calc.calculate_shipping(60.0), 0.0, places=2)

    def test_calculate_shipping_negative_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_shipping(-10.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0, places=2)

    def test_calculate_tax_default_rate(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0, places=2)

    def test_calculate_tax_custom_rate(self):
        calc = OrderCalculator(tax_rate=0.10)
        self.assertAlmostEqual(calc.calculate_tax(200.0), 20.0, places=2)

    def test_calculate_tax_negative_amount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_total_empty_order_no_discount(self):
        calc = OrderCalculator()
        expected = calc.shipping_cost * (1 + calc.tax_rate)
        self.assertAlmostEqual(calc.calculate_total(), expected, places=2)

    def test_calculate_total_single_item_below_threshold_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('Item', 20.0, 2)
        expected = 40.0 + 10.0 + (50.0 * 0.23)
        self.assertAlmostEqual(calc.calculate_total(), expected, places=2)

    def test_calculate_total_single_item_below_threshold_with_discount(self):
        calc = OrderCalculator()
        calc.add_item('Item', 20.0, 2)
        expected = 35.0 + 10.0 + (45.0 * 0.23)
        self.assertAlmostEqual(calc.calculate_total(discount=5.0), expected, places=2)

    def test_calculate_total_above_threshold_discount_to_threshold(self):
        calc = OrderCalculator()
        calc.add_item('Item', 30.0, 4)  # subtotal 120
        expected = 100.0 + (100.0 * 0.23)
        self.assertAlmostEqual(calc.calculate_total(discount=20.0), expected, places=2)

    def test_calculate_total_above_threshold_discount_below_threshold(self):
        calc = OrderCalculator()
        calc.add_item('Item', 55.0, 2)  # subtotal 110
        expected = 95.0 + 10.0 + (105.0 * 0.23)
        self.assertAlmostEqual(calc.calculate_total(discount=15.0), expected, places=2)

    def test_calculate_total_discount_exceeds_subtotal_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 5)  # subtotal 50
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=60.0)

    def test_calculate_total_custom_configuration(self):
        calc = OrderCalculator(tax_rate=0.10, free_shipping_threshold=50, shipping_cost=5)
        calc.add_item('A', 15.0, 2)   # 30
        calc.add_item('B', 5.0, 3)    # 15 -> subtotal 45
        expected = 45.0 - 5.0 + 5.0 + ((40.0) * 0.10)
        self.assertAlmostEqual(calc.calculate_total(discount=5.0), expected, places=2)

    def test_total_items_empty_order(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_item_quantity_one(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        self.assertEqual(calc.total_items(), 1)

    def test_total_items_single_item_quantity_multiple(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 5)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 2.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 2.0, 3)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertAlmostEqual(calc.get_subtotal(), 0.0, places=2)
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_list_items_empty_order(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_multiple_distinct(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 1.0, 1)
        self.assertCountEqual(calc.list_items(), ['Apple', 'Banana'])

    def test_list_items_duplicate_name_merged(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_after_removal(self):