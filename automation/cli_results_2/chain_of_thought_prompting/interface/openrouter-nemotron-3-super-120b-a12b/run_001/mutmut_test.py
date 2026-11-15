import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    def test_init_custom(self):
        calc = OrderCalculator(tax_rate=0.08, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.08)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_init_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_free_shipping_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_new(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 3)
        self.assertEqual(calc.total_items(), 3)
        self.assertAlmostEqual(calc.get_subtotal(), 1.5)

    def test_add_item_existing_increases_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 2)
        calc.add_item('Apple', 0.5, 3)
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 2.5)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.3)
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3)

    def test_add_item_name_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_add_item_price_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', '0.5', 1)

    def test_add_item_quantity_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 0.5, 1.5)

    def test_add_item_negative_price_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', -0.5, 1)

    def test_add_item_negative_quantity_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 0.5, -1)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 2)
        calc.add_item('Banana', 0.3, 1)
        calc.remove_item('Apple')
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3)
        self.assertListEqual(calc.list_items(), ['Banana'])

    def test_remove_item_last_item_empty(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 1)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_remove_item_name_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_normal(self):
        calc = OrderCalculator()
        calc.add_item('A', 2.0, 2)
        calc.add_item('B', 3.5, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 7.5)

    def test_get_subtotal_precision(self):
        calc = OrderCalculator()
        calc.add_item('X', 0.1, 3)
        calc.add_item('Y', 0.2, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 0.5)

    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.1), 90.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(80.0, 1.0), 0.0)

    def test_apply_discount_zero_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(0.0, 0.25), 0.0)

    def test_apply_discount_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.1')

    def test_apply_discount_negative_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.05)

    def test_apply_discount_over_one_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.5)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(80.0), 10.0)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(120.0), 0.0)

    def test_calculate_shipping_at_threshold(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_shipping(-10.0), 10.0)

    def test_calculate_shipping_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('80')

    def test_calculate_shipping_zero_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertAlmostEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_tax_normal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_calculate_total_no_discount_above_threshold(self):
        calc = OrderCalculator()
        calc.add_item('Book', 50.0, 2)
        calc.add_item('Pen', 5.0, 4)
        expected = 120.0 * (1 + 0.23)
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_with_discount(self):
        calc = OrderCalculator()
        calc.add_item('Book', 50.0, 3)
        calc.add_item('Pen', 10.0, 2)
        expected = 153.0 * (1 + 0.23)
        self.assertAlmostEqual(calc.calculate_total(0.1), expected)

    def test_calculate_total_shipping_applied(self):
        calc = OrderCalculator()
        calc.add_item('Cheap', 30.0, 2)
        expected = 70.0 * (1 + 0.23)
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_discount_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_total('0.1')

    def test_calculate_total_discount_out_of_range_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.2)

    def test_total_items_normal(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 2.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Neg', 1.0, -1)
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_list_items_normal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 1)
        calc.add_item('Apple', 1.0, 1)
        self.assertListEqual(sorted(calc.list_items()), ['Apple', 'Banana'])

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertListEqual(calc.list_items(), [])

    def test_list_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 1)
        calc.remove_item('A')
        self.assertListEqual(calc.list_items(), ['B'])

    def test_list_items_return_copy(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        lst = calc.list_items()
        lst.append('ShouldNotAffect')
        self.assertNotIn('ShouldNotAffect', calc.list_items())

    def test_is_empty_init_and_after_clear(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        calc.add_item('A', 1.0, 1)
        self.assertFalse(calc.is_empty())
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_add(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_remove_last(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.remove_item('A')
        self.assertTrue(calc.is_empty())

    def test_integration_full_workflow(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=5.0)
        calc.add_item('Book', 30.0, 2)
        calc.add_item('Pen', 5.0, 10)
        expected = 104.5 + 10.45
        self.assertAlmostEqual(calc.calculate_total(0.05), expected)

    def test_error_propagation_state_unchanged(self):
        calc = OrderCalculator()
        calc.add_item('Good', 10.0, 1)
        subtotal_before = calc.get_subtotal()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)
        self.assertAlmostEqual(calc.get_subtotal(), subtotal_before)
        self.assertEqual(calc.total_items(), 1)