import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default_values(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=7.5)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 7.5)

    def test_init_negative_tax_rate_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_greater_than_one(self):
        calc = OrderCalculator(tax_rate=1.5)
        self.assertEqual(calc.tax_rate, 1.5)

    def test_init_negative_free_shipping_threshold_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-20.0)

    def test_init_negative_shipping_cost_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_non_numeric_tax_rate_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_non_numeric_free_shipping_threshold_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_non_numeric_shipping_cost_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_single_qty_one(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.5, 1)
        self.assertEqual(calc.get_subtotal(), 1.5)
        self.assertEqual(calc.total_items(), 1)
        self.assertIn('apple', calc.list_items())

    def test_add_item_single_qty_greater_than_one(self):
        calc = OrderCalculator()
        calc.add_item('banana', 0.8, 3)
        self.assertEqual(calc.get_subtotal(), 2.4)
        self.assertEqual(calc.total_items(), 3)
        self.assertIn('banana', calc.list_items())

    def test_add_item_multiple_different_items(self):
        calc = OrderCalculator()
        calc.add_item('book', 12.0, 2)
        calc.add_item('pen', 1.5, 5)
        expected_subtotal = 12.0 * 2 + 1.5 * 5
        self.assertAlmostEqual(calc.get_subtotal(), expected_subtotal)
        self.assertEqual(calc.total_items(), 2 + 5)
        self.assertListEqual(calc.list_items(), ['book', 'pen'])

    def test_add_item_zero_price(self):
        calc = OrderCalculator()
        calc.add_item('freebie', 0.0, 2)
        self.assertEqual(calc.get_subtotal(), 0.0)
        self.assertEqual(calc.total_items(), 2)
        self.assertIn('freebie', calc.list_items())

    def test_add_item_zero_quantity_no_change(self):
        calc = OrderCalculator()
        calc.add_item('item', 10.0, 0)
        self.assertEqual(calc.get_subtotal(), 0.0)
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.list_items(), [])

    def test_add_item_duplicate_name_increases_quantity(self):
        calc = OrderCalculator()
        calc.add_item('widget', 5.0, 1)
        calc.add_item('widget', 5.0, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 5.0 * 3)
        self.assertEqual(calc.total_items(), 3)
        self.assertListEqual(calc.list_items(), ['widget'])

    def test_add_item_duplicate_name_different_price(self):
        calc = OrderCalculator()
        calc.add_item('widget', 5.0, 1)
        calc.add_item('widget', 7.0, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 5.0 * 1 + 7.0 * 2)
        self.assertEqual(calc.total_items(), 3)
        self.assertListEqual(calc.list_items(), ['widget'])

    def test_add_item_negative_price_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('bad', -3.0, 1)

    def test_add_item_negative_quantity_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('bad', 10.0, -2)

    def test_add_item_non_string_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 5.0, 1)

    def test_add_item_none_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(None, 5.0, 1)

    def test_add_item_non_numeric_price_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('item', 'five', 1)

    def test_add_item_non_int_quantity_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('item', 10.0, 2.5)

    def test_add_item_large_quantity(self):
        calc = OrderCalculator()
        qty = 10 ** 9
        price = 1e-06
        calc.add_item('tiny', price, qty)
        expected = price * qty
        self.assertAlmostEqual(calc.get_subtotal(), expected)
        self.assertEqual(calc.total_items(), qty)

    def test_add_item_unicode_name(self):
        calc = OrderCalculator()
        name = '🍰-Café & co.'
        calc.add_item(name, 3.14, 2)
        self.assertEqual(calc.get_subtotal(), 3.14 * 2)
        self.assertEqual(calc.total_items(), 2)
        self.assertListEqual(calc.list_items(), [name])

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('gadget', 12.0, 1)
        calc.remove_item('gadget')
        self.assertEqual(calc.get_subtotal(), 0.0)
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.list_items(), [])

    def test_remove_item_qty_greater_than_one(self):
        calc = OrderCalculator()
        calc.add_item('gadget', 12.0, 4)
        calc.remove_item('gadget')
        self.assertEqual(calc.get_subtotal(), 0.0)
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.list_items(), [])

    def test_remove_item_non_existent_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('nothing')

    def test_remove_item_after_multiple_adds_same_name(self):
        calc = OrderCalculator()
        calc.add_item('item', 5.0, 1)
        calc.add_item('item', 5.0, 1)
        calc.remove_item('item')
        self.assertAlmostEqual(calc.get_subtotal(), 5.0)
        self.assertEqual(calc.total_items(), 1)
        self.assertListEqual(calc.list_items(), ['item'])

    def test_remove_item_non_string_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_empty_string_name(self):
        calc = OrderCalculator()
        calc.add_item('', 5.0, 1)
        calc.remove_item('')
        self.assertEqual(calc.get_subtotal(), 0.0)
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.list_items(), [])

    def test_get_subtotal_empty_order(self):
        calc = OrderCalculator()
        self.assertEqual(calc.get_subtotal(), 0.0)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('book', 12.0, 2)
        self.assertEqual(calc.get_subtotal(), 24.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('a', 2.0, 3)
        calc.add_item('b', 3.5, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0 * 3 + 3.5 * 2)

    def test_get_subtotal_floating_point_precision(self):
        calc = OrderCalculator()
        calc.add_item('x', 0.1, 1)
        calc.add_item('y', 0.2, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3, places=7)

    def test_get_subtotal_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('big', 1e+100, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 2e+100)

    def test_get_subtotal_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('a', 5.0, 2)
        calc.add_item('b', 3.0, 1)
        calc.remove_item('a')
        self.assertEqual(calc.get_subtotal(), 3.0)

    def test_get_subtotal_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('a', 5.0, 2)
        calc.clear_order()
        self.assertEqual(calc.get_subtotal(), 0.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_typical(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(200.0, 0.15), 170.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_greater_than_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, 1.3)

    def test_apply_discount_negative_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, -0.2)

    def test_apply_discount_non_numeric_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_non_numeric_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.1')

    def test_apply_discount_small_numbers(self):
        calc = OrderCalculator()
        result = calc.apply_discount(1e-12, 0.5)
        self.assertAlmostEqual(result, 5e-13)

    def test_apply_discount_large_numbers(self):
        calc = OrderCalculator()
        result = calc.apply_discount(1000000000000.0, 1e-06)
        self.assertAlmostEqual(result, 1000000000000.0 * (1 - 1e-06))

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_at_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_negative_shipping_cost_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-3.0)

    def test_calculate_shipping_non_numeric_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('50')

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(-20.0), 10.0)

    def test_calculate_shipping_large_subtotal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(1e+100), 0.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_typical(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_fractional(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(1.2345), 0.283935)

    def test_calculate_tax_negative_amount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-10.0)

    def test_calculate_tax_non_numeric_amount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_calculate_tax_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_tax_rate_greater_than_one(self):
        calc = OrderCalculator(tax_rate=1.5)
        self.assertEqual(calc.calculate_tax(10.0), 15.0)

    def test_calculate_tax_large_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(1e+100), 2.3e+99)

    def test_calculate_total_empty_order_no_discount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_total(), 0.0)

    def test_calculate_total_items_above_threshold_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('item', 150.0, 1)
        expected = 150.0 + calc.calculate_tax(150.0)
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_items_below_threshold_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('item', 80.0, 1)
        shipping = calc.calculate_shipping(80.0)
        expected = 80.0 + shipping + calc.calculate_tax(80.0 + shipping)
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_with_discount_no_shipping_change(self):
        calc = OrderCalculator()
        calc.add_item('item', 120.0, 1)
        total = calc.calculate_total(discount=0.1)
        discounted = 120.0 * 0.9
        shipping = calc.calculate_shipping(discounted)
        expected = discounted + shipping + calc.calculate_tax(discounted + shipping)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_creates_shipping(self):
        calc = OrderCalculator()
        calc.add_item('item', 110.0, 1)
        total = calc.calculate_total(discount=0.2)
        discounted = 110.0 * 0.8
        shipping = calc.calculate_shipping(discounted)
        expected = discounted + shipping + calc.calculate_tax(discounted + shipping)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_removes_shipping(self):
        calc = OrderCalculator()
        calc.add_item('item', 90.0, 1)
        total = calc.calculate_total(discount=-0.1)
        discounted = 90.0 * 1.1
        shipping = calc.calculate_shipping(discounted)
        expected = discounted + shipping + calc.calculate_tax(discounted + shipping)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_full_discount(self):
        calc = OrderCalculator()
        calc.add_item('item', 100.0, 1)
        total = calc.calculate_total(discount=1.0)
        discounted = 0.0
        shipping = calc.calculate_shipping(discounted)
        expected = discounted + shipping + calc.calculate_tax(discounted + shipping)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_negative_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.5)

    def test_calculate_total_discount_greater_than_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.5)

    def test_calculate_total_non_numeric_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='0.1')

    def test_calculate_total_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('item', 50.0, 1)
        calc.clear_order()
        self.assertEqual(calc.calculate_total(), 0.0)

    def test_calculate_total_stress_many_items(self):
        calc = OrderCalculator()
        items = [('a', 2.5, 3), ('b', 4.0, 2), ('c', 0.99, 10)]
        for name, price, qty in items:
            calc.add_item(name, price, qty)
        subtotal = sum((p * q for _, p, q in items))
        discounted = calc.apply_discount(subtotal, 0.05)
        shipping = calc.calculate_shipping(discounted)
        tax = calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(discount=0.05), expected)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_qty_one(self):
        calc = OrderCalculator()
        calc.add_item('item', 5.0, 1)
        self.assertEqual(calc.total_items(), 1)

    def test_total_items_single_qty_n(self):
        calc = OrderCalculator()
        calc.add_item('item', 5.0, 7)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 2)
        calc.add_item('b', 2.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_zero_quantity_ignored(self):
        calc = OrderCalculator()
        calc.add_item('item', 5.0, 0)
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 4)
        calc.add_item('b', 2.0, 3)
        calc.remove_item('a')
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 5)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_large_quantities(self):
        calc = OrderCalculator()
        calc.add_item('x', 1.0, 10 ** 9)
        calc.add_item('y', 2.0, 10 ** 9)
        self.assertEqual(calc.total_items(), 2 * 10 ** 9)

    def test_clear_order_makes_empty(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.add_item('b', 2.0, 2)
        calc.clear_order()
        self.assertEqual(calc.get_subtotal(), 0.0)
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.list_items(), [])
        self.assertTrue(calc.is_empty())

    def test_clear_order_on_empty_is_noop(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertEqual(calc.get_subtotal(), 0.0)
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.list_items(), [])
        self.assertTrue(calc.is_empty())

    def test_clear_order_then_add_item(self):
        calc = OrderCalculator()
        calc.clear_order()
        calc.add_item('x', 3.0, 2)
        self.assertEqual(calc.get_subtotal(), 6.0)
        self.assertEqual(calc.total_items(), 2)
        self.assertListEqual(calc.list_items(), ['x'])

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('only', 5.0, 1)
        self.assertEqual(calc.list_items(), ['only'])

    def test_list_items_multiple_items_order_preserved(self):
        calc = OrderCalculator()
        calc.add_item('first', 1.0, 1)
        calc.add_item('second', 2.0, 1)
        calc.add_item('third', 3.0, 1)
        self.assertEqual(calc.list_items(), ['first', 'second', 'third'])

    def test_list_items_duplicate_names_single_entry(self):
        calc = OrderCalculator()
        calc.add_item('dup', 1.0, 2)
        calc.add_item('dup', 2.0, 3)
        self.assertEqual(calc.list_items(), ['dup'])

    def test_list_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.add_item('b', 2.0, 1)
        calc.remove_item('a')
        self.assertEqual(calc.list_items(), ['b'])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_unicode_names(self):
        calc = OrderCalculator()
        name1 = '😀'
        name2 = 'Café'
        calc.add_item(name1, 1.0, 1)
        calc.add_item(name2, 2.0, 1)
        self.assertListEqual(calc.list_items(), [name1, name2])

    def test_is_empty_true_initially(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_after_add(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_true_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_true_after_removal_of_last(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 2)
        calc.remove_item('item')
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_when_zero_quantity_items_present(self):
        calc = OrderCalculator()
        calc.add_item('item', 5.0, 0)
        self.assertFalse(calc.is_empty())