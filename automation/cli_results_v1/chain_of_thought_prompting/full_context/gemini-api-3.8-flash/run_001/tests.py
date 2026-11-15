import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_values(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom_valid_values(self):
        calc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(calc.tax_rate, 0.15)
        self.assertEqual(calc.free_shipping_threshold, 50)
        self.assertEqual(calc.shipping_cost, 5)

    def test_init_boundary_tax_rates(self):
        calc_zero = OrderCalculator(tax_rate=0.0)
        calc_one = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc_zero.tax_rate, 0.0)
        self.assertEqual(calc_one.tax_rate, 1.0)

    def test_init_boundary_thresholds_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_invalid_type_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_invalid_type_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_invalid_type_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10.0])

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_greater_than_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-0.01)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Apple', 2.5)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0], {'name': 'Apple', 'price': 2.5, 'quantity': 1})

    def test_add_item_explicit_quantity(self):
        self.calc.add_item('Banana', 1.5, 3)
        self.assertEqual(self.calc.items[0], {'name': 'Banana', 'price': 1.5, 'quantity': 3})

    def test_add_multiple_distinct_items(self):
        self.calc.add_item('Apple', 2.0, 1)
        self.calc.add_item('Orange', 3.0, 2)
        self.assertEqual(len(self.calc.items), 2)
        self.assertEqual(self.calc.items[1]['name'], 'Orange')

    def test_add_item_existing_increments_quantity(self):
        self.calc.add_item('Apple', 2.0, 2)
        self.calc.add_item('Apple', 2.0, 3)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 5)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 10.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', '10.0', 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 10.0, 1.5)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 10.0, 1)

    def test_add_item_zero_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Freebie', 0.0, 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Faulty', -5.0, 1)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.0, 0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.0, -2)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item('Apple', 2.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 3.0, 1)

    def test_remove_existing_item(self):
        self.calc.add_item('Apple', 2.0, 1)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.items, [])

    def test_remove_item_from_multiple(self):
        self.calc.add_item('Apple', 2.0, 1)
        self.calc.add_item('Banana', 3.0, 1)
        self.calc.remove_item('Apple')
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['name'], 'Banana')

    def test_remove_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_remove_nonexistent_item_from_populated_order(self):
        self.calc.add_item('Apple', 2.0, 1)
        with self.assertRaises(ValueError):
            self.calc.remove_item('Banana')

    def test_remove_item_from_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Apple')

    def test_get_subtotal_single_item(self):
        self.calc.add_item('Book', 15.0, 2)
        self.assertEqual(self.calc.get_subtotal(), 30.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('Book', 15.0, 2)
        self.calc.add_item('Pen', 2.5, 4)
        self.assertEqual(self.calc.get_subtotal(), 40.0)

    def test_get_subtotal_float_precision(self):
        self.calc.add_item('Item', 19.99, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 59.97, places=5)

    def test_get_subtotal_empty_order_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_typical(self):
        result = self.calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_zero_discount(self):
        result = self.calc.apply_discount(100.0, 0.0)
        self.assertEqual(result, 100.0)

    def test_apply_discount_full_discount(self):
        result = self.calc.apply_discount(100.0, 1.0)
        self.assertEqual(result, 0.0)

    def test_apply_discount_zero_subtotal(self):
        result = self.calc.apply_discount(0.0, 0.5)
        self.assertEqual(result, 0.0)

    def test_apply_discount_invalid_subtotal_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)

    def test_apply_discount_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '0.1')

    def test_apply_discount_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.05)

    def test_apply_discount_discount_greater_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.05)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.1)

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.01), 0.0)

    def test_calculate_shipping_exactly_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_zero_subtotal(self):
        self.assertEqual(self.calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_configured_zero_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(10.0), 0.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50.0')

    def test_calculate_tax_standard(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_zero_amount(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_tax_invalid_amount_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_without_discount_below_threshold(self):
        self.calc.add_item('Item', 50.0, 1)
        expected = (50.0 + 10.0) * 1.23
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_without_discount_above_threshold(self):
        self.calc.add_item('Item', 150.0, 1)
        expected = 150.0 * 1.23
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('Item', 200.0, 1)
        discounted_subtotal = 160.0
        expected = discounted_subtotal * 1.23
        self.assertAlmostEqual(self.calc.calculate_total(discount=0.2), expected)

    def test_calculate_total_discount_crosses_below_threshold(self):
        self.calc.add_item('Item', 120.0, 1)
        discounted_subtotal = 96.0
        expected = (discounted_subtotal + 10.0) * 1.23
        self.assertAlmostEqual(self.calc.calculate_total(discount=0.2), expected)

    def test_calculate_total_full_discount(self):
        self.calc.add_item('Item', 50.0, 1)
        expected = 10.0 * 1.23
        self.assertAlmostEqual(self.calc.calculate_total(discount=1.0), expected)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_invalid_discount_type(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_calculate_total_invalid_discount_range(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.5)

    def test_total_items_empty_order(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_single_item(self):
        self.calc.add_item('Item', 10.0, 4)
        self.assertEqual(self.calc.total_items(), 4)

    def test_total_items_multiple_items(self):
        self.calc.add_item('Item1', 10.0, 2)
        self.calc.add_item('Item2', 20.0, 5)
        self.assertEqual(self.calc.total_items(), 7)

    def test_clear_order_populated(self):
        self.calc.add_item('Item', 10.0, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.items, [])

    def test_clear_order_already_empty(self):
        self.calc.clear_order()
        self.assertEqual(self.calc.items, [])

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_populated(self):
        self.calc.add_item('Item1', 10.0, 1)
        self.calc.add_item('Item2', 20.0, 2)
        self.assertEqual(sorted(self.calc.list_items()), ['Item1', 'Item2'])

    def test_is_empty_new_order(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_populated_order(self):
        self.calc.add_item('Item', 10.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clearing_and_removing(self):
        self.calc.add_item('Item', 10.0, 1)
        self.calc.remove_item('Item')
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('Item2', 15.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())