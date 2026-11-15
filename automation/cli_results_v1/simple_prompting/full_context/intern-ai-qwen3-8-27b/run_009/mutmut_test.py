import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = OrderCalculator()

    def test_init_default_items(self):
        self.assertEqual(OrderCalculator().items, [])

    def test_init_default_tax_rate(self):
        self.assertEqual(OrderCalculator().tax_rate, 0.23)

    def test_init_default_free_shipping_threshold(self):
        self.assertEqual(OrderCalculator().free_shipping_threshold, 100.0)

    def test_init_default_shipping_cost(self):
        self.assertEqual(OrderCalculator().shipping_cost, 10.0)

    def test_init_custom_tax_rate(self):
        calculator = OrderCalculator(tax_rate=0.1)
        self.assertEqual(calculator.tax_rate, 0.1)

    def test_init_custom_free_shipping_threshold(self):
        calculator = OrderCalculator(free_shipping_threshold=50.0)
        self.assertEqual(calculator.free_shipping_threshold, 50.0)

    def test_init_custom_shipping_cost(self):
        calculator = OrderCalculator(shipping_cost=5.0)
        self.assertEqual(calculator.shipping_cost, 5.0)

    def test_init_accepts_int_tax_rate(self):
        calculator = OrderCalculator(tax_rate=1)
        self.assertEqual(calculator.tax_rate, 1)

    def test_init_accepts_int_free_shipping_threshold(self):
        calculator = OrderCalculator(free_shipping_threshold=100)
        self.assertEqual(calculator.free_shipping_threshold, 100)

    def test_init_accepts_int_shipping_cost(self):
        calculator = OrderCalculator(shipping_cost=10)
        self.assertEqual(calculator.shipping_cost, 10)

    def test_init_accepts_zero_tax_rate(self):
        calculator = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calculator.tax_rate, 0.0)

    def test_init_accepts_one_tax_rate(self):
        calculator = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calculator.tax_rate, 1.0)

    def test_init_accepts_zero_free_shipping_threshold(self):
        calculator = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calculator.free_shipping_threshold, 0.0)

    def test_init_accepts_zero_shipping_cost(self):
        calculator = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calculator.shipping_cost, 0.0)

    def test_init_rejects_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_rejects_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_rejects_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_rejects_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1.0)

    def test_init_rejects_string_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.1')

    def test_init_rejects_none_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate=None)

    def test_init_rejects_string_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_rejects_none_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_rejects_string_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_rejects_none_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_add_item_adds_new_item(self):
        self.calculator.add_item('A', 10.0)
        self.assertEqual(self.calculator.items, [{'name': 'A', 'price': 10.0, 'quantity': 1}])

    def test_add_item_stores_explicit_quantity(self):
        self.calculator.add_item('A', 10.0, 3)
        self.assertEqual(self.calculator.items, [{'name': 'A', 'price': 10.0, 'quantity': 3}])

    def test_add_item_accepts_int_price(self):
        self.calculator.add_item('A', 10)
        self.assertEqual(self.calculator.items, [{'name': 'A', 'price': 10, 'quantity': 1}])

    def test_add_item_accepts_int_quantity(self):
        self.calculator.add_item('A', 10.0, 2)
        self.assertEqual(self.calculator.items, [{'name': 'A', 'price': 10.0, 'quantity': 2}])

    def test_add_item_multiple_items(self):
        self.calculator.add_item('A', 10.0)
        self.calculator.add_item('B', 5.0)
        self.assertEqual(len(self.calculator.items), 2)

    def test_add_item_increases_quantity_for_same_name_and_price(self):
        self.calculator.add_item('A', 10.0, 2)
        self.calculator.add_item('A', 10.0, 3)
        self.assertEqual(self.calculator.items, [{'name': 'A', 'price': 10.0, 'quantity': 5}])

    def test_add_item_increases_quantity_for_int_float_price_match(self):
        self.calculator.add_item('A', 10, 1)
        self.calculator.add_item('A', 10.0, 2)
        self.assertEqual(self.calculator.items, [{'name': 'A', 'price': 10, 'quantity': 3}])

    def test_add_item_rejects_same_name_different_price(self):
        self.calculator.add_item('A', 10.0)
        with self.assertRaises(ValueError):
            self.calculator.add_item('A', 11.0)

    def test_add_item_same_name_different_price_does_not_modify_order(self):
        self.calculator.add_item('A', 10.0)
        with self.assertRaises(ValueError):
            self.calculator.add_item('A', 11.0)
        self.assertEqual(self.calculator.items, [{'name': 'A', 'price': 10.0, 'quantity': 1}])

    def test_add_item_rejects_empty_name(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('', 10.0)

    def test_add_item_rejects_zero_price(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('A', 0.0)

    def test_add_item_rejects_negative_price(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('A', -1.0)

    def test_add_item_rejects_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('A', 10.0, 0)

    def test_add_item_rejects_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('A', 10.0, -1)

    def test_add_item_rejects_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item(123, 10.0)

    def test_add_item_rejects_none_name(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item(None, 10.0)

    def test_add_item_rejects_non_numeric_price(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('A', '10.0')

    def test_add_item_rejects_none_price(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('A', None)

    def test_add_item_rejects_non_integer_quantity(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('A', 10.0, 1.0)

    def test_add_item_rejects_none_quantity(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('A', 10.0, None)

    def test_remove_item_removes_existing_item(self):
        self.calculator.add_item('A', 10.0)
        self.calculator.add_item('B', 5.0)
        self.calculator.remove_item('A')
        self.assertEqual(self.calculator.items, [{'name': 'B', 'price': 5.0, 'quantity': 1}])

    def test_remove_item_removes_only_item(self):
        self.calculator.add_item('A', 10.0)
        self.calculator.remove_item('A')
        self.assertEqual(self.calculator.items, [])

    def test_remove_item_rejects_nonexistent_item(self):
        self.calculator.add_item('A', 10.0)
        with self.assertRaises(ValueError):
            self.calculator.remove_item('B')

    def test_remove_item_nonexistent_does_not_modify_order(self):
        self.calculator.add_item('A', 10.0)
        with self.assertRaises(ValueError):
            self.calculator.remove_item('B')
        self.assertEqual(self.calculator.items, [{'name': 'A', 'price': 10.0, 'quantity': 1}])

    def test_remove_item_rejects_empty_order(self):
        with self.assertRaises(ValueError):
            self.calculator.remove_item('A')

    def test_remove_item_rejects_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calculator.remove_item(123)

    def test_remove_item_rejects_none_name(self):
        with self.assertRaises(TypeError):
            self.calculator.remove_item(None)

    def test_get_subtotal_empty_order_raises(self):
        with self.assertRaises(ValueError):
            self.calculator.get_subtotal()

    def test_get_subtotal_single_item(self):
        self.calculator.add_item('A', 10.0, 3)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 30.0)

    def test_get_subtotal_multiple_items(self):
        self.calculator.add_item('A', 10.0, 2)
        self.calculator.add_item('B', 5.0, 3)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 35.0)

    def test_get_subtotal_after_duplicate_add(self):
        self.calculator.add_item('A', 10.0, 2)
        self.calculator.add_item('A', 10.0, 3)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 50.0)

    def test_apply_discount_no_discount(self):
        self.assertAlmostEqual(self.calculator.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        self.assertAlmostEqual(self.calculator.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_partial_discount(self):
        self.assertAlmostEqual(self.calculator.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero_subtotal(self):
        self.assertAlmostEqual(self.calculator.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_accepts_int_subtotal(self):
        self.assertAlmostEqual(self.calculator.apply_discount(100, 0.5), 50.0)

    def test_apply_discount_accepts_int_discount(self):
        self.assertAlmostEqual(self.calculator.apply_discount(100.0, 1), 0.0)

    def test_apply_discount_rejects_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(-1.0, 0.1)

    def test_apply_discount_rejects_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, -0.1)

    def test_apply_discount_rejects_discount_above_one(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, 1.1)

    def test_apply_discount_rejects_non_numeric_subtotal(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount('100.0', 0.1)

    def test_apply_discount_rejects_none_subtotal(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount(None, 0.1)

    def test_apply_discount_rejects_non_numeric_discount(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount(100.0, '0.1')

    def test_apply_discount_rejects_none_discount(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount(100.0, None)

    def test_calculate_shipping_below_threshold(self):
        self.assertAlmostEqual(self.calculator.calculate_shipping(99.0), 10.0)

    def test_calculate_shipping_equal_threshold(self):
        self.assertAlmostEqual(self.calculator.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertAlmostEqual(self.calculator.calculate_shipping(101.0), 0.0)

    def test_calculate_shipping_custom_threshold_below(self):
        calculator = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calculator.calculate_shipping(49.0), 5.0)

    def test_calculate_shipping_custom_threshold_equal(self):
        calculator = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calculator.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_zero_threshold(self):
        calculator = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertAlmostEqual(calculator.calculate_shipping(0.0), 0.0)

    def test_calculate_shipping_custom_shipping_cost(self):
        calculator = OrderCalculator(shipping_cost=5.0)
        self.assertAlmostEqual(calculator.calculate_shipping(0.0), 5.0)

    def test_calculate_shipping_accepts_int_subtotal(self):
        self.assertAlmostEqual(self.calculator.calculate_shipping(99), 10.0)

    def test_calculate_shipping_rejects_non_numeric_subtotal(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_shipping('100.0')

    def test_calculate_shipping_rejects_none_subtotal(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_shipping(None)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calculator.calculate_tax(0.0), 0.0)

    def test_calculate_tax_default_rate(self):
        self.assertAlmostEqual(self.calculator.calculate_tax(100.0), 23.0)

    def test_calculate_tax_custom_rate(self):
        calculator = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(calculator.calculate_tax(100.0), 10.0)

    def test_calculate_tax_zero_rate(self):
        calculator = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calculator.calculate_tax(100.0), 0.0)

    def test_calculate_tax_full_rate(self):
        calculator = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calculator.calculate_tax(100.0), 100.0)

    def test_calculate_tax_accepts_int_amount(self):
        self.assertAlmostEqual(self.calculator.calculate_tax(100), 23.0)

    def test_calculate_tax_rejects_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_tax(-1.0)

    def test_calculate_tax_rejects_non_numeric_amount(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_tax('100.0')

    def test_calculate_tax_rejects_none_amount(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_tax(None)

    def test_calculate_total_empty_order_raises(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_total()

    def test_calculate_total_no_discount_below_threshold(self):
        self.calculator.add_item('A', 10.0)
        self.assertAlmostEqual(self.calculator.calculate_total(), 24.6)

    def test_calculate_total_no_discount_equal_threshold(self):
        self.calculator.add_item('A', 100.0)
        self.assertAlmostEqual(self.calculator.calculate_total(), 123.0)

    def test_calculate_total_no_discount_above_threshold(self):
        self.calculator.add_item('A', 100.0, 2)
        self.assertAlmostEqual(self.calculator.calculate_total(), 246.0)

    def test_calculate_total_with_discount_below_threshold(self):
        self.calculator.add_item('A', 100.0)
        self.assertAlmostEqual(self.calculator.calculate_total(discount=0.5), 73.8)

    def test_calculate_total_with_discount_equal_threshold(self):
        self.calculator.add_item('A', 125.0)
        self.assertAlmostEqual(self.calculator.calculate_total(discount=0.2), 123.0)

    def test_calculate_total_full_discount(self):
        self.calculator.add_item('A', 100.0)
        self.assertAlmostEqual(self.calculator.calculate_total(discount=1.0), 12.3)

    def test_calculate_total_multiple_items(self):
        self.calculator.add_item('A', 10.0, 2)
        self.calculator.add_item('B', 5.0, 3)
        self.assertAlmostEqual(self.calculator.calculate_total(), 55.35)

    def test_calculate_total_custom_parameters(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calculator.add_item('A', 10.0)
        self.assertAlmostEqual(calculator.calculate_total(), 16.5)

    def test_calculate_total_zero_tax(self):
        calculator = OrderCalculator(tax_rate=0.0)
        calculator.add_item('A', 10.0)
        self.assertAlmostEqual(calculator.calculate_total(), 20.0)

    def test_calculate_total_full_tax(self):
        calculator = OrderCalculator(tax_rate=1.0)
        calculator.add_item('A', 10.0)
        self.assertAlmostEqual(calculator.calculate_total(), 40.0)

    def test_calculate_total_zero_shipping_cost(self):
        calculator = OrderCalculator(shipping_cost=0.0)
        calculator.add_item('A', 10.0)
        self.assertAlmostEqual(calculator.calculate_total(), 12.3)

    def test_calculate_total_zero_threshold(self):
        calculator = OrderCalculator(free_shipping_threshold=0.0)
        calculator.add_item('A', 10.0)
        self.assertAlmostEqual(calculator.calculate_total(), 12.3)

    def test_calculate_total_full_discount_zero_threshold(self):
        calculator = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        calculator.add_item('A', 100.0)
        self.assertAlmostEqual(calculator.calculate_total(discount=1.0), 0.0)

    def test_calculate_total_accepts_int_discount(self):
        self.calculator.add_item('A', 100.0)
        self.assertAlmostEqual(self.calculator.calculate_total(discount=1), 12.3)

    def test_calculate_total_rejects_negative_discount(self):
        self.calculator.add_item('A', 10.0)
        with self.assertRaises(ValueError):
            self.calculator.calculate_total(discount=-0.1)

    def test_calculate_total_rejects_discount_above_one(self):
        self.calculator.add_item('A', 10.0)
        with self.assertRaises(ValueError):
            self.calculator.calculate_total(discount=1.1)

    def test_calculate_total_rejects_non_numeric_discount(self):
        self.calculator.add_item('A', 10.0)
        with self.assertRaises(TypeError):
            self.calculator.calculate_total(discount='0.1')

    def test_calculate_total_rejects_none_discount(self):
        self.calculator.add_item('A', 10.0)
        with self.assertRaises(TypeError):
            self.calculator.calculate_total(discount=None)

    def test_total_items_empty(self):
        self.assertEqual(self.calculator.total_items(), 0)

    def test_total_items_single_item(self):
        self.calculator.add_item('A', 10.0, 3)
        self.assertEqual(self.calculator.total_items(), 3)

    def test_total_items_multiple_items(self):
        self.calculator.add_item('A', 10.0, 2)
        self.calculator.add_item('B', 5.0, 3)
        self.assertEqual(self.calculator.total_items(), 5)

    def test_total_items_after_duplicate_add(self):
        self.calculator.add_item('A', 10.0, 2)
        self.calculator.add_item('A', 10.0, 3)
        self.assertEqual(self.calculator.total_items(), 5)

    def test_total_items_after_clear(self):
        self.calculator.add_item('A', 10.0, 2)
        self.calculator.clear_order()
        self.assertEqual(self.calculator.total_items(), 0)

    def test_clear_order_empty(self):
        self.calculator.clear_order()
        self.assertEqual(self.calculator.items, [])

    def test_clear_order_removes_items(self):
        self.calculator.add_item('A', 10.0)
        self.calculator.add_item('B', 5.0)
        self.calculator.clear_order()
        self.assertEqual(self.calculator.items, [])

    def test_clear_order_allows_adding_new_items(self):
        self.calculator.add_item('A', 10.0)
        self.calculator.clear_order()
        self.calculator.add_item('B', 5.0)
        self.assertEqual(self.calculator.items, [{'name': 'B', 'price': 5.0, 'quantity': 1}])

    def test_list_items_empty(self):
        self.assertEqual(self.calculator.list_items(), [])

    def test_list_items_single(self):
        self.calculator.add_item('A', 10.0)
        self.assertCountEqual(self.calculator.list_items(), ['A'])

    def test_list_items_multiple(self):
        self.calculator.add_item('A', 10.0)
        self.calculator.add_item('B', 5.0)
        self.assertCountEqual(self.calculator.list_items(), ['A', 'B'])

    def test_list_items_duplicate_names(self):
        self.calculator.add_item('A', 10.0, 2)
        self.calculator.add_item('A', 10.0, 3)
        self.assertCountEqual(self.calculator.list_items(), ['A'])

    def test_list_items_after_clear(self):
        self.calculator.add_item('A', 10.0)
        self.calculator.clear_order()
        self.assertEqual(self.calculator.list_items(), [])

    def test_is_empty_new(self):
        self.assertTrue(self.calculator.is_empty())

    def test_is_empty_after_add(self):
        self.calculator.add_item('A', 10.0)
        self.assertFalse(self.calculator.is_empty())

    def test_is_empty_after_remove(self):
        self.calculator.add_item('A', 10.0)
        self.calculator.remove_item('A')
        self.assertTrue(self.calculator.is_empty())

    def test_is_empty_after_clear(self):
        self.calculator.add_item('A', 10.0)
        self.calculator.clear_order()
        self.assertTrue(self.calculator.is_empty())
if __name__ == '__main__':
    unittest.main()