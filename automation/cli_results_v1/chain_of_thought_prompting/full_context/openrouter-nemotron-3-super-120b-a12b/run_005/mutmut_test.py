import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_valid_custom(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_init_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_tax_rate_below_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_above_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_init_tax_rate_non_numeric(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_free_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_free_shipping_non_numeric(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2)

    def test_init_shipping_cost_non_numeric(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_basic(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(len(calc.items), 1)
        item = calc.items[0]
        self.assertEqual(item['name'], 'Apple')
        self.assertEqual(item['price'], 1.0)
        self.assertEqual(item['quantity'], 2)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.5)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_increase_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 5)

    def test_add_item_quantity_one(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Item', 2.0, 1000000)
        self.assertEqual(calc.items[0]['quantity'], 1000000)

    def test_add_item_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    def test_add_item_name_not_string(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_price_zero_or_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', 0.0)
        with self.assertRaises(ValueError):
            calc.add_item('Item', -5.0)

    def test_add_item_price_not_number(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', '5')

    def test_add_item_quantity_less_than_one(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item('Item', 1.0, -1)

    def test_add_item_quantity_not_int(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', 1.0, 2.5)

    def test_add_item_same_name_diff_price(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Item', 12.0, 1)

    def test_add_item_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        calc.add_item('B', 2.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'B')
        self.assertEqual(calc.items[0]['quantity'], 3)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('ToRemove', 5.0, 2)
        calc.remove_item('ToRemove')
        self.assertEqual(calc.items, [])

    def test_remove_item_existing_with_quantity(self):
        calc = OrderCalculator()
        calc.add_item('ToRemove', 5.0, 10)
        calc.remove_item('ToRemove')
        self.assertEqual(len(calc.items), 0)

    def test_remove_item_only_item(self):
        calc = OrderCalculator()
        calc.add_item('Only', 1.0, 1)
        calc.remove_item('Only')
        self.assertTrue(calc.is_empty())

    def test_remove_item_name_not_string(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_not_existing(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Nonexistent')

    def test_remove_item_after_multiple_adds_same_name(self):
        calc = OrderCalculator()
        calc.add_item('Same', 1.0, 2)
        calc.add_item('Same', 1.0, 3)
        calc.remove_item('Same')
        self.assertEqual(calc.items, [])

    def test_get_subtotal_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('A', 2.0, 3)
        calc.add_item('B', 4.0, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 10.0)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Single', 2.5, 4)
        self.assertAlmostEqual(calc.get_subtotal(), 10.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 2.0, 2)
        calc.add_item('C', 3.0, 3)
        expected = 1 * 1 + 2 * 2 + 3 * 3
        self.assertAlmostEqual(calc.get_subtotal(), expected)

    def test_get_subtotal_float_precision(self):
        calc = OrderCalculator()
        calc.add_item('A', 0.1, 1)
        calc.add_item('B', 0.2, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3)

    def test_get_subtotal_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_partial(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_subtotal_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_int_inputs(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100, 0), 100.0)
        self.assertAlmostEqual(calc.apply_discount(100, 1), 0.0)

    def test_apply_discount_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-5.0, 0.1)

    def test_apply_discount_out_of_range_low(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)

    def test_apply_discount_out_of_range_high(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.2)

    def test_apply_discount_non_numeric_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_non_numeric_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.2')

    def test_shipping_free_at_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_shipping_free_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(60.0), 0.0)

    def test_shipping_charged_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(40.0), 10.0)

    def test_shipping_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)
        self.assertEqual(calc.calculate_shipping(5.0), 0.0)

    def test_shipping_zero_cost(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_shipping_non_numeric_input(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('10')

    def test_shipping_negative_input(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(-10.0), 10.0)

    def test_shipping_uses_instance_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=30.0, shipping_cost=7.0)
        self.assertEqual(calc.calculate_shipping(20.0), 7.0)
        self.assertEqual(calc.calculate_shipping(30.0), 0.0)
        self.assertEqual(calc.calculate_shipping(40.0), 0.0)

    def test_tax_zero_amount(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_tax_positive_amount(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_tax_max_rate(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc.calculate_tax(50.0), 50.0)

    def test_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(123.45), 0.0)

    def test_tax_negative_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_tax_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_tax_uses_instance_rate(self):
        calc = OrderCalculator(tax_rate=0.07)
        self.assertAlmostEqual(calc.calculate_tax(200.0), 14.0)

    def test_total_no_discount(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Book', 50.0, 2)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 110.0)

    def test_total_with_discount(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Book', 50.0, 2)
        total = calc.calculate_total(discount=0.1)
        self.assertAlmostEqual(total, 110.0)

    def test_total_free_shipping_due_to_discount(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Item', 200.0, 1)
        total = calc.calculate_total(discount=0.5)
        self.assertAlmostEqual(total, 100.0)

    def test_total_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_total_invalid_discount_type(self):
        calc = OrderCalculator()
        calc.add_item('A', 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='0.1')

    def test_total_discount_out_of_range(self):
        calc = OrderCalculator()
        calc.add_item('A', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.2)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.2)

    def test_total_custom_tax_shipping(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=0.0, shipping_cost=7.0)
        calc.add_item('A', 10.0, 2)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 21.0)

    def test_total_floating_point(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('A', 1.0 / 3, 3)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 11.0)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 7)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 2.0, 3)
        calc.add_item('C', 3.0, 5)
        self.assertEqual(calc.total_items(), 2 + 3 + 5)

    def test_total_items_after_add_remove_cycles(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 2)
        self.assertEqual(calc.total_items(), 3)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 2)
        calc.add_item('A', 1.0, 4)
        self.assertEqual(calc.total_items(), 6)
        calc.remove_item('B')
        self.assertEqual(calc.total_items(), 4)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 5)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_clear_order_preserves_config(self):
        calc = OrderCalculator(tax_rate=0.5, free_shipping_threshold=200.0, shipping_cost=20.0)
        calc.add_item('A', 10.0, 1)
        calc.clear_order()
        self.assertEqual(calc.tax_rate, 0.5)
        self.assertEqual(calc.free_shipping_threshold, 200.0)
        self.assertEqual(calc.shipping_cost, 20.0)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_duplicate_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        names = calc.list_items()
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0], 'Apple')

    def test_list_items_distinct_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 1)
        calc.add_item('Cherry', 3.0, 1)
        names = set(calc.list_items())
        self.assertEqual(names, {'Apple', 'Banana', 'Cherry'})

    def test_list_items_after_remove(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 1)
        calc.remove_item('A')
        self.assertEqual(calc.list_items(), ['B'])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_is_empty_true(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_after_add(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_true_after_remove_all(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.remove_item('A')
        self.assertTrue(calc.is_empty())

    def test_is_empty_true_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_after_clear_then_add(self):
        calc = OrderCalculator()
        calc.clear_order()
        calc.add_item('A', 1.0, 1)
        self.assertFalse(calc.is_empty())