import unittest
from unittest.mock import patch
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_tax_rate_out_of_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate=None)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    def test_add_item_new_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 3)
        self.assertEqual(len(calc.items), 1)
        item = calc.items[0]
        self.assertEqual(item['name'], 'Apple')
        self.assertEqual(item['price'], 0.5)
        self.assertEqual(item['quantity'], 3)

    def test_add_item_same_name_price_increment(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 2)
        calc.add_item('Apple', 0.5, 4)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 6)

    def test_add_item_same_name_diff_price_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 0.6, 1)

    def test_add_item_empty_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0, 1)

    def test_add_item_name_not_string_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_add_item_price_nonpositive_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', 0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Item', -5.0, 1)

    def test_add_item_price_not_number_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', '5', 1)

    def test_add_item_quantity_less_than_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item('Item', 1.0, -2)

    def test_add_item_quantity_not_int_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', 1.0, 2.5)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.3)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_remove_item_existing_item(self):
        calc = OrderCalculator()
        calc.add_item('Orange', 1.0, 2)
        calc.remove_item('Orange')
        self.assertEqual(calc.items, [])

    def test_remove_item_nonexistent_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Ghost')

    def test_remove_item_name_not_string_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(42)

    def test_remove_item_one_of_many(self):
        calc = OrderCalculator()
        calc.add_item('A', 1, 1)
        calc.add_item('B', 2, 1)
        calc.add_item('C', 3, 1)
        calc.remove_item('B')
        self.assertEqual(len(calc.items), 2)
        names = {item['name'] for item in calc.items}
        self.assertEqual(names, {'A', 'C'})

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Pen', 2.0, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 6.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 10.0, 2)
        calc.add_item('B', 5.0, 4)
        self.assertAlmostEqual(calc.get_subtotal(), 40.0)

    def test_get_subtotal_fractional(self):
        calc = OrderCalculator()
        calc.add_item('C', 3.33, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 9.99)

    def test_get_subtotal_empty_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_half(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(200.0, 0.5), 100.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(150.0, 1.0), 0.0)

    def test_apply_discount_fractional(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(83.25, 0.07), 83.25 * 0.93)

    def test_apply_discount_negative_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_negative_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, -0.2)

    def test_apply_discount_discount_over_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, 1.3)

    def test_apply_discount_subtotal_not_number_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_discount_not_number_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.2')

    def test_calculate_shipping_free_when_at_or_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_cost_when_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_cost_when_below_threshold_epsilon(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0 - 1e-09), 10.0)

    def test_calculate_shipping_not_number_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('50')

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(-5.0), 10.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_positive_default_rate(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_fractional_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(33.33), 33.33 * 0.23)

    def test_calculate_tax_custom_rate(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(calc.calculate_tax(200.0), 10.0)

    def test_calculate_tax_negative_amount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-10.0)

    def test_calculate_tax_amount_not_number_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('50')

    def test_calculate_total_no_discount_shipping_applied(self):
        calc = OrderCalculator()
        calc.add_item('Item', 20.0, 2)
        self.assertAlmostEqual(calc.calculate_total(), 61.5)

    def test_calculate_total_no_discount_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Item', 60.0, 2)
        self.assertAlmostEqual(calc.calculate_total(), 147.6)

    def test_calculate_total_discount_below_threshold_shipping_applied(self):
        calc = OrderCalculator()
        calc.add_item('Item', 80.0, 2)
        self.assertAlmostEqual(calc.calculate_total(discount=0.5), 110.7)

    def test_calculate_total_discount_above_threshold_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Item', 80.0, 2)
        self.assertAlmostEqual(calc.calculate_total(discount=0.1), 177.12)

    def test_calculate_total_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_discount_not_number_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='0.2')

    def test_calculate_total_discount_out_of_range_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.2)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.1)

    def test_calculate_total_negative_subtotal_mocked_raises(self):
        calc = OrderCalculator()
        with patch.object(calc, 'get_subtotal', return_value=-5.0):
            with self.assertRaises(ValueError):
                calc.calculate_total()

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('A', 5.0, 3)
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 2.0, 5)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_same_name_price_increment(self):
        calc = OrderCalculator()
        calc.add_item('C', 1.0, 1)
        calc.add_item('C', 1.0, 4)
        self.assertEqual(calc.total_items(), 5)

    def test_clear_order_empties_items(self):
        calc = OrderCalculator()
        calc.add_item('X', 1.0, 1)
        calc.add_item('Y', 2.0, 2)
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_clear_order_is_empty_true(self):
        calc = OrderCalculator()
        calc.add_item('X', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_list_items_empty(self):
        calc = OrderCalculator()
        calc.add_item('X', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_clear_order_total_items_zero(self):
        calc = OrderCalculator()
        calc.add_item('X', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('X', 1.0, 1)
        self.assertEqual(calc.list_items(), ['X'])

    def test_list_items_multiple_distinct(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 2.0, 1)
        calc.add_item('C', 3.0, 1)
        result = calc.list_items()
        self.assertEqual(len(result), 3)
        self.assertSetEqual(set(result), {'A', 'B', 'C'})

    def test_list_items_duplicate_names_once(self):
        calc = OrderCalculator()
        calc.add_item('D', 2.0, 2)
        calc.add_item('D', 2.0, 3)
        self.assertEqual(calc.list_items(), ['D'])

    def test_list_items_duplicate_name_diff_price_raises_and_list_unaffected(self):
        calc = OrderCalculator()
        calc.add_item('D', 2.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('D', 3.0, 1)
        self.assertEqual(calc.list_items(), ['D'])

    def test_is_empty_true_when_empty(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_when_nonempty(self):
        calc = OrderCalculator()
        calc.add_item('Any', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_true_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Any', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())