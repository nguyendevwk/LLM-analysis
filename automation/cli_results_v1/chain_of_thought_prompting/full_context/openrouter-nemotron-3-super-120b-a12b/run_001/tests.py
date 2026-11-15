import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.07, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.07)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_mixed_int_float(self):
        calc = OrderCalculator(tax_rate=0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(calc.tax_rate, 0)
        self.assertEqual(calc.free_shipping_threshold, 0)
        self.assertEqual(calc.shipping_cost, 0)

    def test_init_tax_rate_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_over_one_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_init_tax_rate_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_free_shipping_threshold_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_free_shipping_threshold_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_shipping_cost_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_first_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 3)
        self.assertEqual(len(calc.items), 1)
        item = calc.items[0]
        self.assertEqual(item['name'], 'Apple')
        self.assertEqual(item['price'], 0.5)
        self.assertEqual(item['quantity'], 3)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.3)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_increase_quantity(self):
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
            calc.add_item('Item', -2.0, 1)

    def test_add_item_price_wrong_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', '5', 1)

    def test_add_item_quantity_less_than_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Item', 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item('Item', 1.0, -3)

    def test_add_item_quantity_not_int_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', 1.0, 2.5)

    def test_add_item_many_distinct(self):
        calc = OrderCalculator()
        names = ['A', 'B', 'C']
        prices = [1.0, 2.0, 3.0]
        for n, p in zip(names, prices):
            calc.add_item(n, p, 1)
        self.assertEqual(len(calc.items), 3)
        for i, (n, p) in enumerate(zip(names, prices)):
            self.assertEqual(calc.items[i]['name'], n)
            self.assertEqual(calc.items[i]['price'], p)
            self.assertEqual(calc.items[i]['quantity'], 1)

    def test_add_item_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        calc.add_item('Item2', 2.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'Item2')
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_remove_item_existing_single(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 2)
        calc.remove_item('Apple')
        self.assertEqual(calc.items, [])

    def test_remove_item_one_from_multi(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 1)
        calc.add_item('Banana', 0.3, 2)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'Banana')

    def test_remove_item_quantity_greater_than_one(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 3)
        calc.remove_item('Apple')
        self.assertEqual(calc.items, [])

    def test_remove_item_nonexistent_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Pear')

    def test_remove_item_name_not_string_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(42)

    def test_remove_item_after_cleared_raises(self):
        calc = OrderCalculator()
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.remove_item('Any')

    def test_remove_item_aggregated_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 2)
        calc.add_item('Apple', 0.5, 3)
        calc.remove_item('Apple')
        self.assertEqual(calc.items, [])

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Book', 10.0, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 20.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 5.0, 2)
        calc.add_item('B', 3.0, 4)
        self.assertAlmostEqual(calc.get_subtotal(), 22.0)

    def test_get_subtotal_fractional(self):
        calc = OrderCalculator()
        calc.add_item('C', 1.25, 4)
        self.assertAlmostEqual(calc.get_subtotal(), 5.0)

    def test_get_subtotal_empty_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_after_add_remove_all_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.remove_item('Item')
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_return_type_float(self):
        calc = OrderCalculator()
        calc.add_item('Item', 5, 2)
        result = calc.get_subtotal()
        self.assertIsInstance(result, float)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_typical(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_fractional(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(33.33, 0.1), 30.0, places=2)

    def test_apply_discount_negative_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-5.0, 0.1)

    def test_apply_discount_negative_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, -0.05)

    def test_apply_discount_over_one_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, 1.2)

    def test_apply_discount_subtotal_not_number_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_discount_not_number_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100, '0.1')

    def test_apply_discount_subtotal_int(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100, 0.1), 90.0)

    def test_apply_discount_discount_int_out_of_range_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 2)

    def test_calculate_shipping_free_when_at_or_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_free_when_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_charged_when_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_threshold_zero_always_free(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_cost_zero_always_free(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_input_not_number_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('50')

    def test_calculate_shipping_input_int(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(50), 10.0)

    def test_calculate_shipping_uses_instance_attributes(self):
        calc = OrderCalculator(free_shipping_threshold=75.0, shipping_cost=7.5)
        self.assertEqual(calc.calculate_shipping(74.9), 7.5)
        self.assertEqual(calc.calculate_shipping(75.0), 0.0)

    def test_calculate_tax_typical(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(50.0), 0.0)

    def test_calculate_tax_max_rate(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.calculate_tax(30.0), 30.0)

    def test_calculate_tax_fractional_amount(self):
        calc = OrderCalculator(tax_rate=0.07)
        self.assertAlmostEqual(calc.calculate_tax(33.33), 2.3331, places=4)

    def test_calculate_tax_negative_amount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_amount_not_number_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('10')

    def test_calculate_tax_amount_int(self):
        calc = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(calc.calculate_tax(10), 1.0)

    def test_calculate_tax_uses_instance_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(calc.calculate_tax(200.0), 10.0)

    def test_calculate_total_no_discount_shipping_charged(self):
        calc = OrderCalculator()
        calc.add_item('Item', 50.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), 73.8)

    def test_calculate_total_discount_triggers_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0, tax_rate=0.23)
        calc.add_item('Item', 100.0, 1)
        self.assertAlmostEqual(calc.calculate_total(0.0), 123.0)

    def test_calculate_total_discount_and_shipping_charged(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0, tax_rate=0.23)
        calc.add_item('Item', 80.0, 1)
        self.assertAlmostEqual(calc.calculate_total(0.1), 100.86, places=2)

    def test_calculate_total_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_discount_not_number_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total('0.1')

    def test_calculate_total_discount_out_of_range_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.5)

    def test_calculate_total_negative_subtotal_forced_raises(self):
        calc = OrderCalculator()
        calc.items = [{'name': 'Item', 'price': -5.0, 'quantity': 1}]
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_tax_base_verification(self):
        calc = OrderCalculator(free_shipping_threshold=200.0, shipping_cost=10.0, tax_rate=0.23)
        calc.add_item('Item', 10.0, 10)
        self.assertAlmostEqual(calc.calculate_total(), 135.3)

    def test_calculate_total_default_discount(self):
        calc = OrderCalculator()
        calc.add_item('Item', 50.0, 1)
        self.assertAlmostEqual(calc.calculate_total(), calc.calculate_total(0.0))

    def test_calculate_total_return_type_float(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        result = calc.calculate_total()
        self.assertIsInstance(result, float)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 5)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 1.0, 3)
        calc.add_item('C', 1.0, 10)
        self.assertEqual(calc.total_items(), 15)

    def test_total_items_after_remove(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 4)
        calc.add_item('B', 1.0, 6)
        calc.remove_item('A')
        self.assertEqual(calc.total_items(), 6)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 3)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_return_type_int(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 7)
        self.assertIsInstance(calc.total_items(), int)

    def test_clear_order_clears(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_clear_order_on_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertEqual(calc.items, [])

    def test_clear_order_subsequent_operations(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        calc.add_item('B', 2.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'B')
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_clear_order_returns_none(self):
        calc = OrderCalculator()
        self.assertIsNone(calc.clear_order())

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(sorted(calc.list_items()), ['Apple'])

    def test_list_items_multiple_distinct(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 1.0, 1)
        calc.add_item('Cherry', 1.0, 1)
        self.assertEqual(sorted(calc.list_items()), ['Apple', 'Banana', 'Cherry'])

    def test_list_items_duplicate_name_single_entry(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_same_name_diff_price_forced(self):
        calc = OrderCalculator()
        calc.items = [{'name': 'Apple', 'price': 1.0, 'quantity': 1}, {'name': 'Apple', 'price': 2.0, 'quantity': 1}]
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_return_type_list_of_strings(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 1)
        result = calc.list_items()
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item, str)

    def test_is_empty_true(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_clear_true(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_return_type_bool(self):
        calc = OrderCalculator()
        self.assertIsInstance(calc.is_empty(), bool)