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

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_tax_rate_out_of_range_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_out_of_range_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_free_shipping_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='50')

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_numeric_int_accepted(self):
        calc = OrderCalculator(tax_rate=0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(calc.tax_rate, 0)
        self.assertEqual(calc.free_shipping_threshold, 0)
        self.assertEqual(calc.shipping_cost, 0)

    def test_add_item_basic(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(len(calc.items), 1)
        item = calc.items[0]
        self.assertEqual(item['name'], 'Apple')
        self.assertEqual(item['price'], 1.0)
        self.assertEqual(item['quantity'], 2)
        self.assertEqual(calc.total_items(), 2)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.5)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_merge_existing_same_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 4)

    def test_add_item_merge_int_float_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 5, 1)
        calc.add_item('Apple', 5.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 3)

    def test_add_item_new_item_after_merge(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 1)
        self.assertEqual(len(calc.items), 2)
        names = {item['name'] for item in calc.items}
        self.assertEqual(names, {'Apple', 'Banana'})
        self.assertEqual(calc.items[0]['quantity'], 3)
        self.assertEqual(calc.items[1]['quantity'], 1)

    def test_add_item_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError) as cm:
            calc.add_item('', 1.0)
        self.assertIn('Item name cannot be empty', str(cm.exception))

    def test_add_item_name_non_string(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_price_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', '10')

    def test_add_item_price_zero(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', 0.0)

    def test_add_item_price_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', -5.0)

    def test_add_item_quantity_non_int(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', 1.0, 2.5)

    def test_add_item_quantity_less_than_one(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item('Item', 1.0, -1)

    def test_add_item_conflicting_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        with self.assertRaises(ValueError) as cm:
            calc.add_item('Apple', 2.0)
        self.assertIn('Item with the same name but different price already exists', str(cm.exception))

    def test_add_item_conflicting_price_int_float(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 5)
        calc.add_item('Apple', 5.0)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_add_item_conflicting_price_float_precision(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.1 + 0.2)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 0.3)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.remove_item('Apple')
        self.assertEqual(calc.items, [])

    def test_remove_item_not_existing(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError) as cm:
            calc.remove_item('Orange')
        self.assertIn('does not exist', str(cm.exception))

    def test_remove_item_name_non_string(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_case_sensitivity(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0)
        with self.assertRaises(ValueError):
            calc.remove_item('Apple')

    def test_remove_item_after_partial_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 5)
        calc.remove_item('Apple')
        self.assertEqual(calc.items, [])

    def test_get_subtotal_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError) as cm:
            calc.get_subtotal()
        self.assertIn('Cannot calculate subtotal on empty order', str(cm.exception))

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Book', 10.0, 2)
        self.assertEqual(calc.get_subtotal(), 20.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 5.0, 3)
        calc.add_item('B', 2.5, 4)
        self.assertEqual(calc.get_subtotal(), 5.0 * 3 + 2.5 * 4)

    def test_get_subtotal_large_quantities(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 10 ** 6)
        self.assertEqual(calc.get_subtotal(), float(10 ** 6))

    def test_get_subtotal_float_precision(self):
        calc = OrderCalculator()
        calc.add_item('Item', 0.1, 3)
        calc.add_item('Item2', 0.2, 3)
        expected = 0.1 * 3 + 0.2 * 3
        self.assertAlmostEqual(calc.get_subtotal(), expected)

    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_subtotal_int(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(50, 0.1), 45.0)

    def test_apply_discount_subtotal_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_discount_out_of_range_low(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.01)

    def test_apply_discount_discount_out_of_range_high(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.1)

    def test_apply_discount_subtotal_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_discount_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.2')

    def test_apply_discount_subtotal_none(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(None, 0.1)

    def test_apply_discount_discount_none(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, None)

    def test_calculate_shipping_free(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_free_above(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_charged(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_exact_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_zero_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(-5.0), 10.0)

    def test_calculate_shipping_subtotal_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('50')

    def test_calculate_shipping_subtotal_none(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping(None)

    def test_calculate_shipping_custom_threshold_and_cost(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=7.5)
        self.assertEqual(calc.calculate_shipping(30.0), 7.5)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)
        self.assertEqual(calc.calculate_shipping(80.0), 0.0)

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_amount_int(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertEqual(calc.calculate_tax(50), 11.5)

    def test_calculate_tax_amount_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-10.0)

    def test_calculate_tax_amount_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_calculate_tax_amount_none(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax(None)

    def test_calculate_tax_custom_rate(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertEqual(calc.calculate_tax(200.0), 10.0)

    def test_calculate_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.calculate_tax(100.0), 100.0)

    def test_calculate_total_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('Item', 20.0, 2)
        total = calc.calculate_total()
        expected = 40.0 + 10.0 + (40.0 + 10.0) * 0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount(self):
        calc = OrderCalculator()
        calc.add_item('Item', 20.0, 2)
        total = calc.calculate_total(discount=0.1)
        discounted = 40.0 * 0.9
        shipping = 10.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Item', 60.0, 2)
        total = calc.calculate_total()
        discounted = 120.0
        shipping = 0.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_brings_under_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=5.0)
        calc.add_item('Item', 105.0, 1)
        total = calc.calculate_total(discount=0.05)
        discounted = 105.0 * 0.95
        shipping = 5.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_discount_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_total(discount='0.1')

    def test_calculate_total_discount_out_of_range_low(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.05)

    def test_calculate_total_discount_out_of_range_high(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.2)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 7)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 3)
        calc.add_item('B', 1.0, 5)
        self.assertEqual(calc.total_items(), 8)

    def test_total_items_after_add_remove(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 1.0, 3)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 10 ** 6)
        self.assertEqual(calc.total_items(), 10 ** 6)

    def test_clear_order_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_clear_order_returns_none(self):
        calc = OrderCalculator()
        result = calc.clear_order()
        self.assertIsNone(result)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_multiple_unique(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 1.0, 1)
        calc.add_item('Cherry', 1.0, 1)
        result = calc.list_items()
        self.assertEqual(sorted(result), ['Apple', 'Banana', 'Cherry'])

    def test_list_items_duplicate_names_different_price(self):
        calc = OrderCalculator()
        calc.items.append({'name': 'Item', 'price': 1.0, 'quantity': 1})
        calc.items.append({'name': 'Item', 'price': 2.0, 'quantity': 1})
        result = calc.list_items()
        self.assertEqual(result, ['Item'])

    def test_list_items_return_type(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        result = calc.list_items()
        self.assertIsInstance(result, list)
        for name in result:
            self.assertIsInstance(name, str)

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
        calc.add_item('Item', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_false_after_add_then_remove(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.remove_item('Item')
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_return_type(self):
        calc = OrderCalculator()
        self.assertIsInstance(calc.is_empty(), bool)