import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)

    def test_init_custom_valid(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0.0)
        self.assertEqual(oc.shipping_cost, 0.0)

    def test_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_init_wrong_type_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='big')

    def test_add_item_normal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(oc.total_items(), 2)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8)
        self.assertEqual(oc.total_items(), 1)
        self.assertCountEqual(oc.list_items(), ['Banana'])

    def test_add_item_same_name_same_price_increment(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_add_item_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_price_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Orange', 0.0, 1)

    def test_add_item_price_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Orange', -0.5, 1)

    def test_add_item_quantity_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 1.2, 0)

    def test_add_item_quantity_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 1.2, -3)

    def test_add_item_name_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_price_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', '1.5', 1)

    def test_add_item_quantity_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', 1.5, 2.5)

    def test_add_item_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Gadget', 0.01, 10000)
        self.assertEqual(oc.total_items(), 10000)
        self.assertAlmostEqual(oc.get_subtotal(), 100.0, places=2)

    def test_remove_item_existing_single(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_remove_item_existing_multiple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('Banana', 2.0, 2)
        oc.remove_item('Apple')
        self.assertFalse(oc.is_empty())
        self.assertCountEqual(oc.list_items(), ['Banana'])
        self.assertEqual(oc.total_items(), 2)

    def test_remove_item_nonexistent(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Cherry')

    def test_remove_item_name_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(42)

    def test_get_subtotal_normal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 3)
        oc.add_item('Banana', 1.5, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 9.0, places=2)

    def test_get_subtotal_single(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 5.0, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 5.0, places=2)

    def test_get_subtotal_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_typical(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100.0, 0.2), 80.0, places=2)

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50.0, 0.0), 50.0, places=2)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(75.0, 1.0), 0.0, places=2)

    def test_apply_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -0.1)

    def test_apply_discount_over_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, 1.5)

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 0.1)

    def test_apply_discount_subtotal_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)

    def test_apply_discount_discount_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100.0, '0.1')

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(99.99), 10.0, places=2)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(100.0), 0.0, places=2)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(150.0), 0.0, places=2)

    def test_calculate_shipping_custom_config(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(oc.calculate_shipping(40.0), 5.0, places=2)
        self.assertAlmostEqual(oc.calculate_shipping(60.0), 0.0, places=2)

    def test_calculate_shipping_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('abc')

    def test_calculate_shipping_negative_subtotal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(-5.0), 10.0, places=2)

    def test_calculate_tax_normal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(200.0), 46.0, places=2)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0, places=2)

    def test_calculate_tax_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-1.0)

    def test_calculate_tax_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax('200')

    def test_calculate_total_no_discount_shipping_applies(self):
        oc = OrderCalculator()
        oc.add_item('Item1', 30.0, 2)
        oc.add_item('Item2', 20.0, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, (80.0 + 10.0) * 1.23, places=2)

    def test_calculate_total_discount_below_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 30.0, 4)
        total = oc.calculate_total(0.25)
        discounted = 120.0 * 0.75
        expected = (discounted + 10.0) * 1.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_discount_above_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 30.0, 5)
        total = oc.calculate_total(0.0)
        expected = 150.0 * 1.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_discount_exact_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 50.0, 2)
        total = oc.calculate_total(0.0)
        expected = 100.0 * 1.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_full_discount(self):
        oc = OrderCalculator()
        oc.add_item('Item', 50.0, 1)
        total = oc.calculate_total(1.0)
        expected = (0.0 + 10.0) * 1.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_calculate_total_invalid_discount_negative(self):
        oc = OrderCalculator()
        oc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(-0.1)

    def test_calculate_total_invalid_discount_over_one(self):
        oc = OrderCalculator()
        oc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(1.5)

    def test_calculate_total_discount_wrong_type(self):
        oc = OrderCalculator()
        oc.add_item('Item', 10.0, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total('0.1')

    def test_calculate_total_custom_tax_shipping(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=7.0)
        oc.add_item('Item', 40.0, 1)
        total = oc.calculate_total()
        expected = (40.0 + 7.0) * 1.1
        self.assertAlmostEqual(total, expected, places=2)

    def test_total_items_multiple_adds(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 1.0, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 1.0, 3)
        oc.remove_item('Apple')
        self.assertEqual(oc.total_items(), 3)

    def test_total_items_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.clear_order()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_initially_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_clear_order_populated(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)
        self.assertEqual(oc.list_items(), [])

    def test_clear_order_already_empty(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_list_items_multiple_distinct(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('Banana', 1.0, 1)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana'])

    def test_list_items_duplicate_addition(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('Apple', 1.0, 2)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_list_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('Banana', 1.0, 1)
        oc.remove_item('Apple')
        self.assertCountEqual(oc.list_items(), ['Banana'])

    def test_list_items_empty_order(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_is_empty_new_instance(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_adding(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_removing_last(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_state_reset_add_remove_add(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.remove_item('Apple')
        oc.add_item('Apple', 2.0, 1)
        self.assertCountEqual(oc.list_items(), ['Apple'])
        self.assertAlmostEqual(oc.get_subtotal(), 2.0, places=2)

    def test_state_reset_add_clear_add(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        oc.clear_order()
        oc.add_item('Banana', 2.0, 2)
        self.assertCountEqual(oc.list_items(), ['Banana'])
        self.assertEqual(oc.total_items(), 2)

    def test_large_order_performance(self):
        oc = OrderCalculator()
        for i in range(100):
            oc.add_item(f'Item{i}', 1.0, 1)
        self.assertEqual(oc.total_items(), 100)
        self.assertAlmostEqual(oc.get_subtotal(), 100.0, places=2)

    def test_floating_point_rounding(self):
        oc = OrderCalculator()
        oc.add_item('Item', 0.1, 3)
        discounted = oc.apply_discount(oc.get_subtotal(), 0.33)
        self.assertAlmostEqual(discounted, 0.201, places=3)

    def test_discount_shipping_tax_ordering(self):
        oc = OrderCalculator()
        oc.add_item('Item', 80.0, 1)
        total = oc.calculate_total(0.1)
        expected = (80.0 * 0.9 + 10.0) * 1.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_shipping_negative_subtotal_no_exception(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(-0.1), 10.0, places=2)

    def test_calculate_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-0.5)

    def test_add_item_zero_price_rejected(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('ZeroPrice', 0.0, 1)

    def test_add_item_zero_quantity_rejected(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('ZeroQty', 1.0, 0)

    def test_add_item_whitespace_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('   ', 1.0, 1)

    def test_apply_discount_large_precision(self):
        oc = OrderCalculator()
        result = oc.apply_discount(1000.0, 0.9999)
        self.assertAlmostEqual(result, 0.1, places=2)

    def test_tax_rate_zero(self):
        oc = OrderCalculator(tax_rate=0.0)
        oc.add_item('Item', 100.0, 1)
        total = oc.calculate_total()
        expected = (100.0 + 10.0) * 1.0
        self.assertAlmostEqual(total, expected, places=2)

    def test_tax_rate_one(self):
        oc = OrderCalculator(tax_rate=1.0)
        oc.add_item('Item', 100.0, 1)
        total = oc.calculate_total()
        expected = (100.0 + 10.0) * 2.0
        self.assertAlmostEqual(total, expected, places=2)