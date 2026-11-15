import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50)
        self.assertEqual(calc.shipping_cost, 5)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_init_non_numeric_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.1')

    def test_init_non_numeric_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='50')

    def test_init_non_numeric_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='5')

    def test_add_item_single(self):
        calc = OrderCalculator()
        calc.add_item('book', 12.99, 2)
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 25.98, places=7)

    def test_add_item_explicit_quantity(self):
        calc = OrderCalculator()
        calc.add_item('pen', 1.5, 5)
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 7.5, places=7)

    def test_add_item_duplicate(self):
        calc = OrderCalculator()
        calc.add_item('apple', 0.5, 3)
        calc.add_item('apple', 0.5, 2)
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 2.5, places=7)

    def test_add_item_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_add_item_non_float_price(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('item', '1.0', 1)

    def test_add_item_non_int_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('item', 1.0, 1.5)

    def test_add_item_negative_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('item', -1.0, 1)

    def test_add_item_zero_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('item', 1.0, 0)

    def test_add_item_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('item', 1.0, -2)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('book', 10, 1)
        calc.remove_item('book')
        self.assertTrue(calc.is_empty())

    def test_remove_item_duplicate(self):
        calc = OrderCalculator()
        calc.add_item('book', 10, 1)
        calc.add_item('book', 10, 1)
        calc.remove_item('book')
        self.assertTrue(calc.is_empty())

    def test_remove_item_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_after_add(self):
        calc = OrderCalculator()
        calc.add_item('book', 12.99, 2)
        calc.add_item('pen', 1.5, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 12.99 * 2 + 1.5 * 3, places=7)

    def test_apply_discount_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -5.0)

    def test_apply_discount_non_numeric_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 5.0)

    def test_apply_discount_non_numeric_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '5')

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50, shipping_cost=10)
        shipping = calc.calculate_shipping(30.0)
        self.assertAlmostEqual(shipping, 10.0, places=7)

    def test_calculate_shipping_at_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50, shipping_cost=10)
        shipping = calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, 0.0, places=7)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50, shipping_cost=10)
        shipping = calc.calculate_shipping(60.0)
        self.assertAlmostEqual(shipping, 0.0, places=7)

    def test_calculate_shipping_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('30')

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.1)
        tax = calc.calculate_tax(200.0)
        self.assertAlmostEqual(tax, 20.0, places=7)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        tax = calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0, places=7)

    def test_calculate_tax_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-10.0)

    def test_calculate_tax_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('10')

    def test_calculate_total_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0)
        calc.add_item('book', 20.0, 1)
        total = calc.calculate_total()
        shipping = calc.calculate_shipping(calc.get_subtotal())
        expected = calc.get_subtotal() + shipping
        self.assertAlmostEqual(total, expected, places=7)

    def test_calculate_total_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0)
        calc.add_item('book', 20.0, 1)
        total = calc.calculate_total()
        tax = calc.calculate_tax(calc.get_subtotal())
        expected = calc.get_subtotal() + tax
        self.assertAlmostEqual(total, expected, places=7)

    def test_calculate_total_negative_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-5.0)

    def test_calculate_total_non_numeric_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='5')

    def test_total_items_after_add(self):
        calc = OrderCalculator()
        calc.add_item('book', 10, 2)
        calc.add_item('pen', 1, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_list_items_after_add(self):
        calc = OrderCalculator()
        calc.add_item('book', 10, 1)
        calc.add_item('pen', 1, 2)
        self.assertCountEqual(calc.list_items(), ['book', 'pen'])

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_is_empty_after_add(self):
        calc = OrderCalculator()
        calc.add_item('book', 10, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_clearing(self):
        calc = OrderCalculator()
        calc.add_item('book', 10, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_initial(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_interaction_duplicate_names(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1, 2)
        calc.add_item('apple', 1, 3)
        self.assertEqual(calc.list_items(), ['apple'])
        self.assertEqual(calc.total_items(), 5)

    def test_interaction_remove_after_duplicate(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1, 2)
        calc.add_item('apple', 1, 3)
        calc.remove_item('apple')
        self.assertTrue(calc.is_empty())

    def test_interaction_clear_and_add_new(self):
        calc = OrderCalculator()
        calc.add_item('book', 10, 1)
        calc.clear_order()
        calc.add_item('pen', 5, 2)
        self.assertEqual(calc.list_items(), ['pen'])
        self.assertEqual(calc.total_items(), 2)

    def test_edge_extreme_values(self):
        calc = OrderCalculator()
        calc.add_item('expensive', 1000000, 10000)
        subtotal = calc.get_subtotal()
        self.assertAlmostEqual(subtotal, 10000000000.0, places=7)
        total = calc.calculate_total()
        shipping = calc.calculate_shipping(subtotal)
        tax = calc.calculate_tax(subtotal)
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(total, expected, places=7)

    def test_edge_floating_point_precision(self):
        calc = OrderCalculator()
        calc.add_item('a', 0.1, 1)
        calc.add_item('b', 0.2, 1)
        subtotal = calc.get_subtotal()
        self.assertAlmostEqual(subtotal, 0.3, places=7)

    def test_edge_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0)
        calc.add_item('item', 10, 1)
        total = calc.calculate_total()
        tax = calc.calculate_tax(10)
        expected = 10 + tax
        self.assertAlmostEqual(total, expected, places=7)

    def test_edge_negative_after_clearing_tax(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5)

    def test_edge_large_number_of_items(self):
        calc = OrderCalculator()
        for i in range(10000):
            calc.add_item(f'item{i}', 1, 1)
        self.assertEqual(calc.total_items(), 10000)
        self.assertAlmostEqual(calc.get_subtotal(), 10000.0, places=7)
        total = calc.calculate_total()
        tax = calc.calculate_tax(10000.0)
        expected = 10000.0 + tax
        self.assertAlmostEqual(total, expected, places=7)

    def test_edge_list_items_order_after_add_remove(self):
        calc = OrderCalculator()
        calc.add_item('A', 1, 1)
        calc.add_item('B', 1, 1)
        calc.add_item('C', 1, 1)
        calc.remove_item('B')
        self.assertEqual(calc.list_items(), ['A', 'C'])

    def test_edge_immutability_of_list_items(self):
        calc = OrderCalculator()
        calc.add_item('item', 10, 1)
        items = calc.list_items()
        items.append('fake')
        self.assertEqual(calc.list_items(), ['item'])

    def test_edge_immutability_of_subtotal(self):
        calc = OrderCalculator()
        calc.add_item('item', 10, 1)
        subtotal = calc.get_subtotal()
        subtotal += 5
        self.assertAlmostEqual(calc.get_subtotal(), 10.0, places=7)
if __name__ == '__main__':
    unittest.main()