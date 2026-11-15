import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
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

    def test_init_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_tax_rate_non_numeric(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='invalid')

    def test_init_free_shipping_threshold_non_numeric(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='invalid')

    def test_init_shipping_cost_non_numeric(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='invalid')

    def test_add_item_first(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 3)
        self.assertEqual(calc.list_items(), ['Apple'])
        self.assertEqual(calc.total_items(), 3)
        self.assertAlmostEqual(calc.get_subtotal(), 1.5)

    def test_add_item_second_distinct(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 2)
        calc.add_item('Banana', 0.3, 4)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})
        self.assertEqual(calc.total_items(), 6)
        self.assertAlmostEqual(calc.get_subtotal(), 0.5 * 2 + 0.3 * 4)

    def test_add_item_same_name_price_increase_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 2)
        calc.add_item('Apple', 0.5, 3)
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 0.5 * 5)

    def test_add_item_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0, 1)

    def test_add_item_name_not_string(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_add_item_price_non_positive(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', 0.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Item', -1.0, 1)

    def test_add_item_price_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', 'price', 1)

    def test_add_item_quantity_less_than_one(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item('Item', 1.0, -1)

    def test_add_item_quantity_not_int(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', 1.0, 1.5)
        with self.assertRaises(TypeError):
            calc.add_item('Item', 1.0, 'two')

    def test_add_item_same_name_different_price(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Item', 2.0, 1)
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 1.0)

    def test_add_item_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1000000)
        self.assertEqual(calc.total_items(), 1000000)
        self.assertAlmostEqual(calc.get_subtotal(), 1000000.0)

    def test_add_item_very_small_price(self):
        calc = OrderCalculator()
        calc.add_item('Item', 0.0001, 10000)
        self.assertAlmostEqual(calc.get_subtotal(), 0.0001 * 10000)

    def test_remove_item_existing_single(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.remove_item('Item')
        self.assertTrue(calc.is_empty())

    def test_remove_item_quantity_greater_than_one(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 5)
        calc.remove_item('Item')
        self.assertTrue(calc.is_empty())

    def test_remove_item_after_multiple_adds(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 2)
        calc.add_item('Item', 1.0, 3)
        calc.remove_item('Item')
        self.assertTrue(calc.is_empty())

    def test_remove_item_non_existent(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Nonexistent')

    def test_remove_item_name_not_string(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_from_empty(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Item')

    def test_get_subtotal_normal(self):
        calc = OrderCalculator()
        calc.add_item('A', 2.0, 3)
        calc.add_item('B', 1.5, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0 * 3 + 1.5 * 2)

    def test_get_subtotal_empty(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_many_items(self):
        calc = OrderCalculator()
        for i in range(100):
            calc.add_item(f'Item{i}', 1.0, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 100.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_twenty_percent(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_one_hundred_percent(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_subtotal_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_subtotal_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_discount_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_above_one(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.2)

    def test_apply_discount_subtotal_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_discount_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.1')

    def test_apply_discount_floating_point(self):
        calc = OrderCalculator()
        result = calc.apply_discount(0.1, 0.3333333333)
        expected = 0.1 * (1 - 0.3333333333)
        self.assertAlmostEqual(result, expected)

    def test_apply_discount_large_numbers(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(1000000000.0, 1e-06), 1000000000.0 * (1 - 1e-06))

    def test_calculate_shipping_free(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_charged(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_boundary_below(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0 - 1e-09), 10.0)

    def test_calculate_shipping_boundary_above(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0 + 1e-09), 0.0)

    def test_calculate_shipping_zero_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_input_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('100')

    def test_calculate_shipping_large_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(1000000000.0), 0.0)

    def test_calculate_shipping_free_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_zero_cost(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-1.0)

    def test_calculate_tax_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_calculate_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 100.0)

    def test_calculate_tax_large_amount(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(1000000000000.0), 0.23 * 1000000000000.0)

    def test_calculate_tax_small_amount(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(1e-10), 0.23 * 1e-10)

    def test_calculate_total_normal(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Book', 50.0, 1)
        total = calc.calculate_total(discount=0.1)
        expected = (50.0 * (1 - 0.1) + 10.0) * (1 + 0.23)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Item', 60.0, 2)
        total = calc.calculate_total(discount=0.0)
        expected = 120.0 * (1 + 0.23)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_default_discount(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Item', 50.0, 1)
        total = calc.calculate_total()
        expected = (50.0 + 10.0) * (1 + 0.23)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_one_hundred_percent(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Item', 50.0, 1)
        total = calc.calculate_total(discount=1.0)
        expected = (0.0 + 10.0) * (1 + 0.23)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_invalid_discount_negative(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.1)

    def test_calculate_total_invalid_discount_above_one(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.2)

    def test_calculate_total_discount_non_numeric(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='0.1')

    def test_calculate_total_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Item', 50.0, 1)
        total = calc.calculate_total(discount=0.1)
        expected = 50.0 * (1 - 0.1) + 10.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_shipping_cost_zero(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=0.0)
        calc.add_item('Item', 50.0, 1)
        total = calc.calculate_total(discount=0.1)
        expected = 50.0 * (1 - 0.1) * (1 + 0.23)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping_and_zero_cost(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=0.0, shipping_cost=0.0)
        calc.add_item('Item', 50.0, 1)
        total = calc.calculate_total(discount=0.1)
        expected = 50.0 * (1 - 0.1) * (1 + 0.23)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_large_order(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=1000.0, shipping_cost=10.0)
        for i in range(100):
            calc.add_item(f'Item{i}', 10.0, 1)
        total = calc.calculate_total(discount=0.05)
        expected = (1000.0 * (1 - 0.05) + 10.0) * (1 + 0.23)
        self.assertAlmostEqual(total, expected)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_one_item(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 5)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_remove(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 4)
        calc.add_item('B', 1.0, 2)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 2)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 3)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_large_quantities(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1000000)
        calc.add_item('Item2', 1.0, 2000000)
        self.assertEqual(calc.total_items(), 3000000)

    def test_clear_order_with_items(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_internal_list_identity(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        old_id = id(calc.items)
        calc.clear_order()
        self.assertNotEqual(id(calc.items), old_id)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_one_item(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        self.assertEqual(calc.list_items(), ['Item'])

    def test_list_items_multiple_distinct(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 1)
        calc.add_item('C', 1.0, 1)
        self.assertEqual(set(calc.list_items()), {'A', 'B', 'C'})

    def test_list_items_same_name_price_no_duplicate(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.add_item('Item', 1.0, 2)
        self.assertEqual(calc.list_items(), ['Item'])

    def test_list_items_after_remove(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.remove_item('Item')
        self.assertEqual(calc.list_items(), [])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_is_empty_true_initially(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_after_add(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_true_after_remove_last(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.remove_item('Item')
        self.assertTrue(calc.is_empty())

    def test_is_empty_true_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_until_last_removed(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 1)
        self.assertFalse(calc.is_empty())
        calc.remove_item('A')
        self.assertFalse(calc.is_empty())
        calc.remove_item('B')
        self.assertTrue(calc.is_empty())