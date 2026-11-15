import unittest
from order_calculator import OrderCalculator

class OrderCalculatorTests(unittest.TestCase):

    def test_init_defaults(self):
        calculator = OrderCalculator()
        self.assertEqual(calculator.tax_rate, 0.23)
        self.assertEqual(calculator.free_shipping_threshold, 100.0)
        self.assertEqual(calculator.shipping_cost, 10.0)
        self.assertEqual(calculator.items, [])

    def test_init_custom_values(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calculator.tax_rate, 0.1)
        self.assertEqual(calculator.free_shipping_threshold, 50.0)
        self.assertEqual(calculator.shipping_cost, 5.0)

    def test_init_int_values(self):
        calculator = OrderCalculator(tax_rate=0, free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(calculator.tax_rate, 0)
        self.assertEqual(calculator.free_shipping_threshold, 50)
        self.assertEqual(calculator.shipping_cost, 5)

    def test_init_zero_values(self):
        calculator = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calculator.tax_rate, 0.0)
        self.assertEqual(calculator.free_shipping_threshold, 0.0)
        self.assertEqual(calculator.shipping_cost, 0.0)

    def test_init_tax_rate_zero(self):
        calculator = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calculator.tax_rate, 0.0)

    def test_init_tax_rate_one(self):
        calculator = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calculator.tax_rate, 1.0)

    def test_init_threshold_zero(self):
        calculator = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calculator.free_shipping_threshold, 0.0)

    def test_init_shipping_zero(self):
        calculator = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calculator.shipping_cost, 0.0)

    def test_init_tax_rate_too_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_too_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_negative_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_negative_shipping(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1.0)

    def test_init_invalid_tax_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_invalid_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_invalid_shipping_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_invalid_tax_type_none(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate=None)

    def test_init_invalid_threshold_type_none(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_invalid_shipping_type_none(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_add_item_default_quantity(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        self.assertEqual(calculator.items, [{'name': 'Apple', 'price': 2.0, 'quantity': 1}])

    def test_add_item_explicit_quantity(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0, 3)
        self.assertEqual(calculator.items, [{'name': 'Apple', 'price': 2.0, 'quantity': 3}])

    def test_add_item_int_price(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2)
        self.assertEqual(calculator.items, [{'name': 'Apple', 'price': 2, 'quantity': 1}])

    def test_add_item_multiple_items(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        calculator.add_item('Banana', 3.0, 2)
        self.assertEqual(calculator.items, [{'name': 'Apple', 'price': 2.0, 'quantity': 1}, {'name': 'Banana', 'price': 3.0, 'quantity': 2}])

    def test_add_item_same_name_and_price_increases_quantity(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0, 2)
        calculator.add_item('Apple', 2.0, 3)
        self.assertEqual(calculator.items, [{'name': 'Apple', 'price': 2.0, 'quantity': 5}])

    def test_add_item_same_name_different_price_raises(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        with self.assertRaises(ValueError):
            calculator.add_item('Apple', 3.0)

    def test_add_item_same_name_different_price_does_not_modify_existing(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0, 1)
        with self.assertRaises(ValueError):
            calculator.add_item('Apple', 3.0, 2)
        self.assertEqual(calculator.items, [{'name': 'Apple', 'price': 2.0, 'quantity': 1}])

    def test_add_item_empty_name_raises(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item('', 1.0)

    def test_add_item_zero_price_raises(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item('Apple', 0.0)

    def test_add_item_negative_price_raises(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item('Apple', -1.0)

    def test_add_item_zero_quantity_raises(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item('Apple', 1.0, 0)

    def test_add_item_negative_quantity_raises(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.add_item('Apple', 1.0, -1)

    def test_add_item_invalid_name_type(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.add_item(123, 1.0)

    def test_add_item_invalid_price_type(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.add_item('Apple', '1.0')

    def test_add_item_invalid_quantity_type(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.add_item('Apple', 1.0, 1.0)

    def test_add_item_invalid_name_type_none(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.add_item(None, 1.0)

    def test_add_item_invalid_price_type_none(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.add_item('Apple', None)

    def test_add_item_invalid_quantity_type_none(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.add_item('Apple', 1.0, None)

    def test_remove_item_removes_existing(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        calculator.remove_item('Apple')
        self.assertEqual(calculator.items, [])

    def test_remove_item_nonexistent_raises(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        with self.assertRaises(ValueError):
            calculator.remove_item('Banana')

    def test_remove_item_empty_order_raises(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.remove_item('Apple')

    def test_remove_item_invalid_type(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.remove_item(123)

    def test_remove_item_invalid_type_none(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.remove_item(None)

    def test_remove_item_keeps_other_items(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        calculator.add_item('Banana', 3.0)
        calculator.remove_item('Apple')
        self.assertEqual(calculator.items, [{'name': 'Banana', 'price': 3.0, 'quantity': 1}])

    def test_get_subtotal_empty_raises(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.get_subtotal()

    def test_get_subtotal_single_item(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0, 3)
        self.assertAlmostEqual(calculator.get_subtotal(), 6.0)

    def test_get_subtotal_multiple_items(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0, 3)
        calculator.add_item('Banana', 5.0, 2)
        self.assertAlmostEqual(calculator.get_subtotal(), 16.0)

    def test_get_subtotal_after_quantity_update(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0, 1)
        calculator.add_item('Apple', 2.0, 2)
        self.assertAlmostEqual(calculator.get_subtotal(), 6.0)

    def test_apply_discount_typical(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero_discount(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full_discount(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_zero_subtotal(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_int_inputs(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.apply_discount(100, 0), 100.0)

    def test_apply_discount_negative_subtotal_raises(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.apply_discount(-1.0, 0.1)

    def test_apply_discount_discount_below_zero_raises(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_above_one_raises(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.apply_discount(100.0, 1.1)

    def test_apply_discount_invalid_subtotal_type(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.apply_discount('100', 0.1)

    def test_apply_discount_invalid_discount_type(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.apply_discount(100.0, '0.1')

    def test_apply_discount_invalid_subtotal_type_none(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.apply_discount(None, 0.1)

    def test_apply_discount_invalid_discount_type_none(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.apply_discount(100.0, None)

    def test_calculate_shipping_below_threshold(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_at_threshold(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.calculate_shipping(100.01), 0.0)

    def test_calculate_shipping_custom_threshold_below(self):
        calculator = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertAlmostEqual(calculator.calculate_shipping(49.99), 10.0)

    def test_calculate_shipping_custom_threshold_at(self):
        calculator = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertAlmostEqual(calculator.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_zero_threshold(self):
        calculator = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertAlmostEqual(calculator.calculate_shipping(0.0), 0.0)

    def test_calculate_shipping_custom_shipping_cost(self):
        calculator = OrderCalculator(shipping_cost=15.0)
        self.assertAlmostEqual(calculator.calculate_shipping(10.0), 15.0)

    def test_calculate_shipping_int_input(self):
        calculator = OrderCalculator()
        self.assertAlmostEqual(calculator.calculate_shipping(50), 10.0)

    def test_calculate_shipping_invalid_type(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.calculate_shipping('100')

    def test_calculate_shipping_invalid_type_none(self):
        calculator = OrderCalculator()
        with self.assertRaises(TypeError):
            calculator.calculate_shipping(None)

    def test_calculate_tax_typical(self):
        calculator = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(calculator.calculate_tax(100.0), 20.0)

    def test_calculate_tax_zero_amount(self):
        calculator = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(calculator.calculate_tax(0.0), 0.0)

    def test_calculate_tax_zero_rate(self):
        calculator = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calculator.calculate_tax(100.0), 0.0)

    def test_calculate_tax_full_rate(self):
        calculator = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calculator.calculate_tax(100.0), 100.0)

    def test_calculate_tax_int_amount(self):
        calculator = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(calculator.calculate_tax(100), 10.0)

    def test_calculate_tax_negative_amount_raises(self):
        calculator = OrderCalculator(tax_rate=0.2)
        with self.assertRaises(ValueError):
            calculator.calculate_tax(-1.0)

    def test_calculate_tax_invalid_type(self):
        calculator = OrderCalculator(tax_rate=0.2)
        with self.assertRaises(TypeError):
            calculator.calculate_tax('100')

    def test_calculate_tax_invalid_type_none(self):
        calculator = OrderCalculator(tax_rate=0.2)
        with self.assertRaises(TypeError):
            calculator.calculate_tax(None)

    def test_calculate_total_empty_order_raises(self):
        calculator = OrderCalculator()
        with self.assertRaises(ValueError):
            calculator.calculate_total()

    def test_calculate_total_invalid_discount_type(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 10.0)
        with self.assertRaises(TypeError):
            calculator.calculate_total('0.1')

    def test_calculate_total_invalid_discount_type_none(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 10.0)
        with self.assertRaises(TypeError):
            calculator.calculate_total(None)

    def test_calculate_total_invalid_discount_below_zero(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 10.0)
        with self.assertRaises(ValueError):
            calculator.calculate_total(-0.1)

    def test_calculate_total_invalid_discount_above_one(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 10.0)
        with self.assertRaises(ValueError):
            calculator.calculate_total(1.1)

    def test_calculate_total_no_discount_below_threshold(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calculator.add_item('Apple', 50.0)
        self.assertAlmostEqual(calculator.calculate_total(), 66.0)

    def test_calculate_total_no_discount_above_threshold(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calculator.add_item('Apple', 100.0)
        self.assertAlmostEqual(calculator.calculate_total(), 110.0)

    def test_calculate_total_with_discount_below_threshold(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calculator.add_item('Apple', 100.0)
        self.assertAlmostEqual(calculator.calculate_total(0.5), 66.0)

    def test_calculate_total_with_discount_above_threshold(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calculator.add_item('Apple', 200.0)
        self.assertAlmostEqual(calculator.calculate_total(0.5), 110.0)

    def test_calculate_total_full_discount_charges_shipping(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calculator.add_item('Apple', 100.0)
        self.assertAlmostEqual(calculator.calculate_total(1.0), 11.0)

    def test_calculate_total_zero_tax(self):
        calculator = OrderCalculator(tax_rate=0.0, free_shipping_threshold=100.0, shipping_cost=10.0)
        calculator.add_item('Apple', 50.0)
        self.assertAlmostEqual(calculator.calculate_total(), 60.0)

    def test_calculate_total_zero_shipping(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=0.0)
        calculator.add_item('Apple', 50.0)
        self.assertAlmostEqual(calculator.calculate_total(), 55.0)

    def test_calculate_total_default_discount(self):
        calculator = OrderCalculator(tax_rate=0.0, free_shipping_threshold=100.0, shipping_cost=0.0)
        calculator.add_item('Apple', 50.0)
        self.assertAlmostEqual(calculator.calculate_total(), 50.0)

    def test_calculate_total_multiple_items(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calculator.add_item('Apple', 30.0, 2)
        calculator.add_item('Banana', 20.0, 1)
        self.assertAlmostEqual(calculator.calculate_total(), 99.0)

    def test_calculate_total_int_discount(self):
        calculator = OrderCalculator(tax_rate=0.0, free_shipping_threshold=100.0, shipping_cost=0.0)
        calculator.add_item('Apple', 100.0)
        self.assertAlmostEqual(calculator.calculate_total(0), 100.0)

    def test_calculate_total_after_clear_raises(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 10.0)
        calculator.clear_order()
        with self.assertRaises(ValueError):
            calculator.calculate_total()

    def test_calculate_total_negative_subtotal_raises(self):
        calculator = OrderCalculator()
        calculator.items = [{'name': 'Apple', 'price': -1.0, 'quantity': 1}]
        with self.assertRaises(ValueError):
            calculator.calculate_total()

    def test_total_items_empty(self):
        calculator = OrderCalculator()
        self.assertEqual(calculator.total_items(), 0)

    def test_total_items_single_default(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        self.assertEqual(calculator.total_items(), 1)

    def test_total_items_multiple_quantities(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0, 2)
        calculator.add_item('Banana', 3.0, 3)
        self.assertEqual(calculator.total_items(), 5)

    def test_total_items_after_add_same_name(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0, 2)
        calculator.add_item('Apple', 2.0, 3)
        self.assertEqual(calculator.total_items(), 5)

    def test_total_items_after_remove(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0, 2)
        calculator.add_item('Banana', 3.0, 3)
        calculator.remove_item('Apple')
        self.assertEqual(calculator.total_items(), 3)

    def test_total_items_after_clear(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0, 2)
        calculator.clear_order()
        self.assertEqual(calculator.total_items(), 0)

    def test_total_items_returns_int(self):
        calculator = OrderCalculator()
        self.assertIsInstance(calculator.total_items(), int)

    def test_clear_order_removes_items(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        calculator.add_item('Banana', 3.0)
        calculator.clear_order()
        self.assertEqual(calculator.items, [])

    def test_clear_order_empty_order(self):
        calculator = OrderCalculator()
        calculator.clear_order()
        self.assertEqual(calculator.items, [])

    def test_clear_order_allows_new_items(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        calculator.clear_order()
        calculator.add_item('Banana', 3.0)
        self.assertEqual(calculator.items, [{'name': 'Banana', 'price': 3.0, 'quantity': 1}])

    def test_clear_order_keeps_configuration(self):
        calculator = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calculator.add_item('Apple', 2.0)
        calculator.clear_order()
        self.assertEqual(calculator.tax_rate, 0.1)
        self.assertEqual(calculator.free_shipping_threshold, 50.0)
        self.assertEqual(calculator.shipping_cost, 5.0)

    def test_list_items_empty(self):
        calculator = OrderCalculator()
        self.assertEqual(calculator.list_items(), [])

    def test_list_items_single(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        self.assertEqual(calculator.list_items(), ['Apple'])

    def test_list_items_multiple_unique(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        calculator.add_item('Banana', 3.0)
        calculator.add_item('Cherry', 4.0)
        self.assertCountEqual(calculator.list_items(), ['Apple', 'Banana', 'Cherry'])

    def test_list_items_after_remove(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        calculator.add_item('Banana', 3.0)
        calculator.remove_item('Apple')
        self.assertEqual(calculator.list_items(), ['Banana'])

    def test_list_items_after_clear(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        calculator.clear_order()
        self.assertEqual(calculator.list_items(), [])

    def test_list_items_no_duplicates(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        calculator.add_item('Apple', 2.0)
        self.assertEqual(calculator.list_items(), ['Apple'])

    def test_is_empty_new(self):
        calculator = OrderCalculator()
        self.assertTrue(calculator.is_empty())

    def test_is_empty_after_add(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        self.assertFalse(calculator.is_empty())

    def test_is_empty_after_remove(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        calculator.remove_item('Apple')
        self.assertTrue(calculator.is_empty())

    def test_is_empty_after_clear(self):
        calculator = OrderCalculator()
        calculator.add_item('Apple', 2.0)
        calculator.clear_order()
        self.assertTrue(calculator.is_empty())
if __name__ == '__main__':
    unittest.main()