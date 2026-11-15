import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default_values(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_zero_values(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_non_numeric_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_non_numeric_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_non_numeric_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_extreme_small(self):
        calc = OrderCalculator(tax_rate=1e-12, free_shipping_threshold=1e-12, shipping_cost=1e-12)
        self.assertEqual(calc.tax_rate, 1e-12)
        self.assertEqual(calc.free_shipping_threshold, 1e-12)
        self.assertEqual(calc.shipping_cost, 1e-12)

    def test_add_item_single(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0, 1)
        self.assertEqual(calc.list_items(), ['apple'])
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 1.0)

    def test_add_item_multiple_quantity(self):
        calc = OrderCalculator()
        calc.add_item('banana', 0.5, 4)
        self.assertEqual(calc.list_items(), ['banana'])
        self.assertEqual(calc.total_items(), 4)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0)

    def test_add_same_item_twice(self):
        calc = OrderCalculator()
        calc.add_item('orange', 2.0, 2)
        calc.add_item('orange', 2.0, 3)
        self.assertEqual(calc.list_items(), ['orange'])
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 10.0)

    def test_add_item_zero_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('pear', 1.0, 0)

    def test_add_item_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('pear', 1.0, -1)

    def test_add_item_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_add_item_non_numeric_price(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('pear', '1.0', 1)

    def test_add_item_negative_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('pear', -1.0, 1)

    def test_add_item_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('item', 5.0, 1)
        calc.clear_order()
        calc.add_item('item2', 3.0, 2)
        self.assertEqual(calc.list_items(), ['item2'])
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 6.0)

    def test_add_item_floating_point_price(self):
        calc = OrderCalculator()
        calc.add_item('small', 0.1, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3)

    def test_remove_item_non_string_name(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 1)
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_preserves_other_items(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.add_item('b', 2.0, 1)
        calc.remove_item('a')
        self.assertEqual(calc.list_items(), ['b'])
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0)

    def test_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('item', 3.0, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 6.0)

    def test_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('a', 2.0, 2)
        calc.add_item('b', 3.0, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 7.0)

    def test_subtotal_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('a', 2.0, 2)
        calc.add_item('b', 3.0, 1)
        calc.remove_item('a')
        self.assertAlmostEqual(calc.get_subtotal(), 3.0)

    def test_subtotal_floating_point_precision(self):
        calc = OrderCalculator()
        calc.add_item('a', 0.1, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3, places=7)

    def test_subtotal_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('a', 1e+108, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 2e+108)

    def test_subtotal_zero_quantity_items(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('a', 1.0, 0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100.0, 0.0)
        self.assertAlmostEqual(result, 100.0)

    def test_apply_discount_over(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, 60.0)

    def test_apply_discount_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, -10.0)

    def test_apply_discount_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 10)
        with self.assertRaises(TypeError):
            calc.apply_discount(100, '10')

    def test_shipping_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(50.0), 10.0)

    def test_shipping_at_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(100.0), 0.0)

    def test_shipping_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(150.0), 0.0)

    def test_shipping_zero_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(0.0), 10.0)

    def test_shipping_negative_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(-10.0), 10.0)

    def test_shipping_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('100')

    def test_shipping_custom_threshold_and_cost(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=7.5)
        self.assertAlmostEqual(calc.calculate_shipping(30.0), 7.5)
        self.assertAlmostEqual(calc.calculate_shipping(60.0), 0.0)

    def test_shipping_floating_point_boundary(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(99.999999), 10.0)
        self.assertAlmostEqual(calc.calculate_shipping(100.000001), 0.0)

    def test_tax_normal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_tax_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_tax_custom_rate(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(calc.calculate_tax(200.0), 10.0)

    def test_tax_floating_point(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.1), 0.023, places=7)

    def test_tax_large_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(1e+108), 2.3e+107)

    def test_tax_after_clear(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_total_empty_with_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=5.0)

    def test_total_discount_over_subtotal(self):
        calc = OrderCalculator()
        calc.add_item('item', 30.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=40.0)

    def test_total_negative_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-5.0)

    def test_total_non_numeric_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='5')
        with self.assertRaises(TypeError):
            calc.calculate_total(discount=None)

    def test_total_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('a', 1e+108, 1)
        expected = 1e+108 + 10.0 + 1e+108 * 0.23
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_qty_one(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 1)
        self.assertEqual(calc.total_items(), 1)

    def test_total_items_single_qty_multiple(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 5)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_multiple_distinct(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 2)
        calc.add_item('b', 2.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 4)
        calc.add_item('b', 1.0, 2)
        calc.remove_item('a')
        self.assertEqual(calc.total_items(), 2)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 3)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_zero_quantity_items(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('item', 1.0, 0)

    def test_total_items_large_quantities(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, int(1000000.0))
        self.assertEqual(calc.total_items(), int(1000000.0))

    def test_total_items_negative_quantity_prevented(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('item', 1.0, -1)

    def test_clear_returns_none(self):
        calc = OrderCalculator()
        self.assertIsNone(calc.clear_order())

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 1)
        self.assertEqual(calc.list_items(), ['item'])

    def test_list_items_multiple_distinct(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.add_item('b', 2.0, 1)
        self.assertEqual(set(calc.list_items()), {'a', 'b'})
        self.assertEqual(len(calc.list_items()), 2)

    def test_list_items_duplicate_name(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 2)
        calc.add_item('item', 1.0, 3)
        self.assertEqual(calc.list_items(), ['item'])

    def test_list_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 2)
        calc.remove_item('item')
        self.assertEqual(calc.list_items(), [])

    def test_list_items_after_partial_removal(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 2)
        calc.remove_item('item')
        self.assertEqual(calc.list_items(), [])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('item', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_return_type_and_mutability(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 1)
        calc.add_item('b', 2.0, 1)
        lst = calc.list_items()
        self.assertIsInstance(lst, list)
        for x in lst:
            self.assertIsInstance(x, str)
        lst.append('c')
        self.assertNotIn('c', calc.list_items())

    def test_list_items_non_string_contents(self):
        calc = OrderCalculator()
        calc.add_item('valid', 1.0, 1)
        for item in calc.list_items():
            self.assertIsInstance(item, str)

    def test_is_empty_true_init(self):
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

    def test_is_empty_false_with_zero_quantity_items(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('item', 1.0, 0)

    def test_is_empty_return_type(self):
        calc = OrderCalculator()
        self.assertIsInstance(calc.is_empty(), bool)
        self.assertIn(calc.is_empty(), (True, False))