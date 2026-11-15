import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_constructor_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    def test_constructor_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0)
        self.assertEqual(calc.shipping_cost, 0)

    def test_constructor_invalid_tax_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_constructor_invalid_tax_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_constructor_invalid_tax_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_constructor_invalid_free_shipping_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_constructor_invalid_free_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1)

    def test_constructor_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_constructor_invalid_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_normal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.8)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_merge_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        calc.add_item('Apple', 1.5, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 5)

    def test_add_item_price_conflict(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 2.0)

    def test_add_item_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0, 1)

    def test_add_item_name_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_add_item_price_zero(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Orange', 0, 1)

    def test_add_item_price_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Orange', -0.5, 1)

    def test_add_item_price_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Orange', 'free', 1)

    def test_add_item_quantity_zero(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Pear', 1.0, 0)

    def test_add_item_quantity_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Pear', 1.0, -3)

    def test_add_item_quantity_float_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Pear', 1.0, 2.5)

    def test_add_item_quantity_bool(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, True)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('Gadget', 1000000000.0, 1000000)
        self.assertEqual(calc.items[0]['price'], 1000000000.0)
        self.assertEqual(calc.items[0]['quantity'], 1000000)

    def test_remove_item_normal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_remove_item_nonexistent(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Nonexistent')

    def test_remove_item_name_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(42)

    def test_remove_item_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.add_item('Banana', 0.8)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'Banana')

    def test_remove_item_idempotent_second_call_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        calc.remove_item('Apple')
        with self.assertRaises(ValueError):
            calc.remove_item('Apple')

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2, 3)
        calc.add_item('Banana', 1, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 8.0)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Milk', 1.25, 4)
        self.assertAlmostEqual(calc.get_subtotal(), 5.0)

    def test_get_subtotal_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_large_values(self):
        calc = OrderCalculator()
        calc.add_item('Gadget', 1000000000.0, 1000000)
        self.assertAlmostEqual(calc.get_subtotal(), 1000000000000000.0)

    def test_apply_discount_zero_percent(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_percent(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_typical(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(200.0, 0.2), 160.0)

    def test_apply_discount_negative_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_over_one(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.5)

    def test_apply_discount_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_subtotal_type_invalid(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('ten', 0.1)

    def test_apply_discount_discount_type_invalid(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(10.0, 'half')

    def test_apply_discount_large_numbers(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(1000000000000.0, 0.25), 750000000000.0)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_at_threshold(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('fifty')

    def test_calculate_shipping_custom_pay(self):
        calc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        self.assertAlmostEqual(calc.calculate_shipping(49.9), 5)

    def test_calculate_shipping_custom_free(self):
        calc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        self.assertAlmostEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_large_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(1000000000.0), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(-10), 10.0)

    def test_calculate_tax_default(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0)
        self.assertAlmostEqual(calc.calculate_tax(200), 0.0)

    def test_calculate_tax_full_rate(self):
        calc = OrderCalculator(tax_rate=1)
        self.assertAlmostEqual(calc.calculate_tax(50), 50.0)

    def test_calculate_tax_negative_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax(None)

    def test_calculate_tax_large_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(1000000000000.0), 230000000000.0)

    def test_calculate_total_no_discount_shipping_applied(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 30, 2)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 86.1)

    def test_calculate_total_no_discount_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item('Laptop', 120, 1)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 147.6)

    def test_calculate_total_discount_20_shipping_applied(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 30, 2)
        total = calc.calculate_total(0.2)
        self.assertAlmostEqual(total, 71.34)

    def test_calculate_total_discount_50_shipping_applied(self):
        calc = OrderCalculator()
        calc.add_item('Book', 80, 1)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 61.5)

    def test_calculate_total_discount_100(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 30, 2)
        total = calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 12.3)

    def test_calculate_total_discount_negative(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 30, 2)
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)

    def test_calculate_total_discount_over_one(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 30, 2)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.5)

    def test_calculate_total_discount_non_numeric(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 30, 2)
        with self.assertRaises(TypeError):
            calc.calculate_total('half')

    def test_calculate_total_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_custom_configuration(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=7)
        calc.add_item('Item', 30, 2)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 66.0)

    def test_calculate_total_negative_subtotal_guard(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 30, 2)
        calc.get_subtotal = lambda: -5
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_rounding_tolerance(self):
        calc = OrderCalculator()
        calc.add_item('Item', 33.33, 1)
        total = calc.calculate_total(0.33)
        expected_subtotal = 33.33
        discounted = expected_subtotal * (1 - 0.33)
        shipping = 10.0
        tax = (discounted + shipping) * 0.23
        expected_total = discounted + shipping + tax
        self.assertAlmostEqual(total, expected_total, places=7)

    def test_total_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1, 3)
        calc.add_item('Banana', 2, 2)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_single(self):
        calc = OrderCalculator()
        calc.add_item('Milk', 1, 1)
        self.assertEqual(calc.total_items(), 1)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1, 3)
        calc.add_item('Banana', 2, 2)
        calc.remove_item('Apple')
        self.assertEqual(calc.total_items(), 2)

    def test_clear_order_normal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1, 1)
        calc.add_item('Banana', 2, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(len(calc.items), 0)
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_idempotent(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_list_items_unique_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1, 1)
        calc.add_item('Banana', 2, 1)
        calc.add_item('Apple', 1, 2)
        self.assertEqual(set(calc.list_items()), {'Apple', 'Banana'})

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_immutability(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1, 1)
        lst = calc.list_items()
        lst.append('X')
        self.assertNotIn('X', calc.list_items())

    def test_list_items_order_independence(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1, 1)
        calc.add_item('Banana', 2, 1)
        result = calc.list_items()
        self.assertEqual(set(result), {'Apple', 'Banana'})

    def test_is_empty_fresh(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_adding(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_clearing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_removing_last(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1, 1)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_add_item_boolean_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, True)
        self.assertEqual(calc.items[0]['quantity'], 1)

    def test_add_item_quantity_float_invalid(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Item', 1.0, 1.0)

    def test_large_price_quantity_arithmetic(self):
        calc = OrderCalculator()
        calc.add_item('Gadget', 1000000000.0, 1000000)
        self.assertAlmostEqual(calc.get_subtotal(), 1000000000000000.0)
        self.assertAlmostEqual(calc.calculate_tax(calc.get_subtotal()), 230000000000000.0)

    def test_list_items_returns_new_list_each_call(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1, 1)
        first = calc.list_items()
        second = calc.list_items()
        self.assertIsNot(first, second)

    def test_calculate_total_after_clear_order_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1, 1)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_zero_shipping_cost_always_zero(self):
        calc = OrderCalculator(shipping_cost=0, free_shipping_threshold=200)
        calc.add_item('Item', 50, 1)
        self.assertAlmostEqual(calc.calculate_shipping(50), 0.0)

    def test_tax_rate_integer_acceptance(self):
        calc = OrderCalculator(tax_rate=1)
        self.assertAlmostEqual(calc.calculate_tax(50), 50.0)