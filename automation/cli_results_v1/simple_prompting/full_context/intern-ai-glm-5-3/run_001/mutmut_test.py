import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = OrderCalculator()

    def test_init_with_defaults(self):
        self.assertEqual(self.calculator.tax_rate, 0.23)
        self.assertEqual(self.calculator.free_shipping_threshold, 100.0)
        self.assertEqual(self.calculator.shipping_cost, 10.0)
        self.assertEqual(self.calculator.items, [])

    def test_init_with_custom_values(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calculator.tax_rate, 0.1)
        self.assertEqual(calculator.free_shipping_threshold, 50.0)
        self.assertEqual(calculator.shipping_cost, 5.0)

    def test_init_with_integer_parameters(self):
        calculator = OrderCalculator(tax_rate=0, free_shipping_threshold=100, shipping_cost=10)
        self.assertEqual(calculator.tax_rate, 0)
        self.assertEqual(calculator.free_shipping_threshold, 100)
        self.assertEqual(calculator.shipping_cost, 10)

    def test_init_tax_rate_zero_is_allowed(self):
        calculator = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calculator.tax_rate, 0.0)

    def test_init_tax_rate_one_is_allowed(self):
        calculator = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calculator.tax_rate, 1.0)

    def test_init_tax_rate_above_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_init_negative_tax_rate_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_not_a_number_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_negative_free_shipping_threshold_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-0.01)

    def test_init_free_shipping_threshold_not_a_number_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_negative_shipping_cost_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-0.01)

    def test_init_shipping_cost_not_a_number_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_stores_item(self):
        self.calculator.add_item('apple', 1.5, 3)
        self.assertEqual(len(self.calculator.items), 1)
        self.assertEqual(self.calculator.items[0]['name'], 'apple')
        self.assertEqual(self.calculator.items[0]['price'], 1.5)
        self.assertEqual(self.calculator.items[0]['quantity'], 3)

    def test_add_item_default_quantity_is_one(self):
        self.calculator.add_item('apple', 1.5)
        self.assertEqual(self.calculator.items[0]['quantity'], 1)

    def test_add_item_accepts_integer_price(self):
        self.calculator.add_item('apple', 2, 2)
        self.assertEqual(self.calculator.items[0]['price'], 2)

    def test_add_item_same_name_same_price_increases_quantity(self):
        self.calculator.add_item('apple', 1.5, 2)
        self.calculator.add_item('apple', 1.5, 3)
        self.assertEqual(len(self.calculator.items), 1)
        self.assertEqual(self.calculator.items[0]['quantity'], 5)

    def test_add_item_same_name_different_price_raises_value_error(self):
        self.calculator.add_item('apple', 1.5)
        with self.assertRaises(ValueError):
            self.calculator.add_item('apple', 2.0)

    def test_add_item_empty_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('', 1.5)

    def test_add_item_name_not_a_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item(123, 1.5)

    def test_add_item_price_not_a_number_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('apple', '1.5')

    def test_add_item_zero_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('apple', 0)

    def test_add_item_negative_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('apple', -1.5)

    def test_add_item_quantity_not_an_integer_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('apple', 1.5, 2.5)

    def test_add_item_quantity_as_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('apple', 1.5, '2')

    def test_add_item_zero_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('apple', 1.5, 0)

    def test_add_item_negative_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('apple', 1.5, -1)

    def test_remove_item_removes_item(self):
        self.calculator.add_item('apple', 1.5)
        self.calculator.remove_item('apple')
        self.assertEqual(self.calculator.items, [])

    def test_remove_item_keeps_other_items(self):
        self.calculator.add_item('apple', 1.5)
        self.calculator.add_item('banana', 2.0)
        self.calculator.remove_item('apple')
        self.assertEqual(len(self.calculator.items), 1)
        self.assertEqual(self.calculator.items[0]['name'], 'banana')

    def test_remove_nonexistent_item_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.remove_item('apple')

    def test_remove_item_name_not_a_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.remove_item(123)

    def test_get_subtotal_single_item(self):
        self.calculator.add_item('apple', 1.5, 3)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 4.5)

    def test_get_subtotal_multiple_items(self):
        self.calculator.add_item('apple', 1.5, 2)
        self.calculator.add_item('banana', 2.0, 3)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 9.0)

    def test_get_subtotal_after_quantity_merge(self):
        self.calculator.add_item('apple', 1.5, 2)
        self.calculator.add_item('apple', 1.5, 3)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 7.5)

    def test_get_subtotal_empty_order_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.get_subtotal()

    def test_apply_discount_typical(self):
        self.assertAlmostEqual(self.calculator.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero_discount(self):
        self.assertAlmostEqual(self.calculator.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        self.assertAlmostEqual(self.calculator.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_zero_subtotal(self):
        self.assertAlmostEqual(self.calculator.apply_discount(0.0, 0.2), 0.0)

    def test_apply_discount_negative_subtotal_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(-1.0, 0.2)

    def test_apply_discount_discount_above_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, 1.1)

    def test_apply_discount_negative_discount_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, -0.1)

    def test_apply_discount_subtotal_not_a_number_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount('100', 0.2)

    def test_apply_discount_discount_not_a_number_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount(100.0, '0.2')

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calculator.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_at_threshold_is_free(self):
        self.assertEqual(self.calculator.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold_is_free(self):
        self.assertEqual(self.calculator.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_zero_subtotal(self):
        self.assertEqual(self.calculator.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_with_custom_parameters(self):
        calculator = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calculator.calculate_shipping(49.99), 5.0)
        self.assertEqual(calculator.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_zero_threshold_is_always_free(self):
        calculator = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calculator.calculate_shipping(0.0), 0.0)

    def test_calculate_shipping_not_a_number_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_shipping('100')

    def test_calculate_tax_typical(self):
        self.assertAlmostEqual(self.calculator.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        self.assertEqual(self.calculator.calculate_tax(0.0), 0.0)

    def test_calculate_tax_zero_rate(self):
        calculator = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calculator.calculate_tax(100.0), 0.0)

    def test_calculate_tax_full_rate(self):
        calculator = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calculator.calculate_tax(100.0), 100.0)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_tax(-1.0)

    def test_calculate_tax_not_a_number_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_tax('100')

    def test_calculate_total_below_threshold(self):
        self.calculator.add_item('apple', 10.0, 2)
        self.assertAlmostEqual(self.calculator.calculate_total(), 36.9)

    def test_calculate_total_above_threshold_free_shipping(self):
        self.calculator.add_item('apple', 60.0, 2)
        self.assertAlmostEqual(self.calculator.calculate_total(), 147.6)

    def test_calculate_total_with_discount_below_threshold(self):
        self.calculator.add_item('apple', 60.0, 2)
        self.assertAlmostEqual(self.calculator.calculate_total(0.2), 130.38)

    def test_calculate_total_with_discount_above_threshold(self):
        self.calculator.add_item('apple', 100.0, 2)
        self.assertAlmostEqual(self.calculator.calculate_total(0.2), 196.8)

    def test_calculate_total_discounted_subtotal_exactly_at_threshold(self):
        self.calculator.add_item('apple', 100.0, 2)
        self.assertAlmostEqual(self.calculator.calculate_total(0.5), 123.0)

    def test_calculate_total_full_discount(self):
        self.calculator.add_item('apple', 60.0, 2)
        self.assertAlmostEqual(self.calculator.calculate_total(1.0), 12.3)

    def test_calculate_total_multiple_items(self):
        self.calculator.add_item('apple', 1.5, 2)
        self.calculator.add_item('banana', 2.0, 3)
        self.assertAlmostEqual(self.calculator.calculate_total(), 23.37)

    def test_calculate_total_zero_tax_rate(self):
        calculator = OrderCalculator(tax_rate=0.0)
        calculator.add_item('apple', 10.0, 2)
        self.assertAlmostEqual(calculator.calculate_total(), 30.0)

    def test_calculate_total_empty_order_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_total()

    def test_calculate_total_discount_above_one_raises_value_error(self):
        self.calculator.add_item('apple', 10.0)
        with self.assertRaises(ValueError):
            self.calculator.calculate_total(1.5)

    def test_calculate_total_negative_discount_raises_value_error(self):
        self.calculator.add_item('apple', 10.0)
        with self.assertRaises(ValueError):
            self.calculator.calculate_total(-0.1)

    def test_calculate_total_discount_not_a_number_raises_type_error(self):
        self.calculator.add_item('apple', 10.0)
        with self.assertRaises(TypeError):
            self.calculator.calculate_total('0.2')

    def test_total_items_empty_order(self):
        self.assertEqual(self.calculator.total_items(), 0)

    def test_total_items_single_item(self):
        self.calculator.add_item('apple', 1.5, 3)
        self.assertEqual(self.calculator.total_items(), 3)

    def test_total_items_multiple_items(self):
        self.calculator.add_item('apple', 1.5, 2)
        self.calculator.add_item('banana', 2.0, 3)
        self.assertEqual(self.calculator.total_items(), 5)

    def test_total_items_after_quantity_merge(self):
        self.calculator.add_item('apple', 1.5, 2)
        self.calculator.add_item('apple', 1.5, 3)
        self.assertEqual(self.calculator.total_items(), 5)

    def test_clear_order_removes_all_items(self):
        self.calculator.add_item('apple', 1.5)
        self.calculator.add_item('banana', 2.0)
        self.calculator.clear_order()
        self.assertEqual(self.calculator.items, [])
        self.assertTrue(self.calculator.is_empty())

    def test_clear_order_on_empty_order(self):
        self.calculator.clear_order()
        self.assertTrue(self.calculator.is_empty())

    def test_clear_order_allows_adding_again(self):
        self.calculator.add_item('apple', 1.5)
        self.calculator.clear_order()
        self.calculator.add_item('banana', 2.0)
        self.assertEqual(self.calculator.total_items(), 1)

    def test_list_items_empty_order(self):
        self.assertEqual(self.calculator.list_items(), [])

    def test_list_items_returns_all_names(self):
        self.calculator.add_item('apple', 1.5)
        self.calculator.add_item('banana', 2.0)
        self.assertEqual(sorted(self.calculator.list_items()), ['apple', 'banana'])

    def test_list_items_contains_no_duplicates(self):
        self.calculator.add_item('apple', 1.5, 2)
        self.calculator.add_item('apple', 1.5, 3)
        self.assertEqual(self.calculator.list_items(), ['apple'])

    def test_is_empty_initially_true(self):
        self.assertTrue(self.calculator.is_empty())

    def test_is_empty_false_after_adding_item(self):
        self.calculator.add_item('apple', 1.5)
        self.assertFalse(self.calculator.is_empty())

    def test_is_empty_true_after_removing_item(self):
        self.calculator.add_item('apple', 1.5)
        self.calculator.remove_item('apple')
        self.assertTrue(self.calculator.is_empty())