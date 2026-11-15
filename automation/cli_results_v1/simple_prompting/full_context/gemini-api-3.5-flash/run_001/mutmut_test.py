import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = OrderCalculator()

    def test_init_default_values(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_edge_values(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc.tax_rate, 0.0)
        calc_max_tax = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc_max_tax.tax_rate, 1.0)

    def test_init_type_error_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_type_error_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_type_error_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10.0])

    def test_init_value_error_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_value_error_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_init_value_error_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_value_error_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_add_item_success_default_quantity(self):
        self.calculator.add_item('Book', 15.0)
        self.assertEqual(self.calculator.items, [{'name': 'Book', 'price': 15.0, 'quantity': 1}])

    def test_add_item_success_custom_quantity(self):
        self.calculator.add_item('Pen', 2.0, 5)
        self.assertEqual(self.calculator.items, [{'name': 'Pen', 'price': 2.0, 'quantity': 5}])

    def test_add_item_existing_same_price_updates_quantity(self):
        self.calculator.add_item('Book', 15.0, 2)
        self.calculator.add_item('Book', 15.0, 3)
        self.assertEqual(len(self.calculator.items), 1)
        self.assertEqual(self.calculator.items[0]['quantity'], 5)

    def test_add_item_existing_different_price_raises_value_error(self):
        self.calculator.add_item('Book', 15.0)
        with self.assertRaises(ValueError):
            self.calculator.add_item('Book', 20.0)

    def test_add_item_type_error_name(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item(123, 10.0)

    def test_add_item_type_error_price(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('Book', '10.0')

    def test_add_item_type_error_quantity(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('Book', 10.0, 2.5)

    def test_add_item_value_error_empty_name(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('', 10.0)

    def test_add_item_value_error_zero_price(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Freebie', 0.0)

    def test_add_item_value_error_negative_price(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Faulty', -5.0)

    def test_add_item_value_error_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Book', 10.0, 0)

    def test_add_item_value_error_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Book', 10.0, -2)

    def test_remove_item_success(self):
        self.calculator.add_item('Book', 10.0)
        self.calculator.remove_item('Book')
        self.assertEqual(self.calculator.items, [])

    def test_remove_item_non_existent_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.remove_item('NonExistent')

    def test_remove_item_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.remove_item(None)

    def test_get_subtotal_success(self):
        self.calculator.add_item('Book', 10.0, 2)
        self.calculator.add_item('Pen', 5.0, 3)
        self.assertEqual(self.calculator.get_subtotal(), 35.0)

    def test_get_subtotal_empty_order_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.get_subtotal()

    def test_apply_discount_success(self):
        result = self.calculator.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_zero_discount(self):
        result = self.calculator.apply_discount(100.0, 0.0)
        self.assertEqual(result, 100.0)

    def test_apply_discount_full_discount(self):
        result = self.calculator.apply_discount(100.0, 1.0)
        self.assertEqual(result, 0.0)

    def test_apply_discount_type_error_subtotal(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount('100', 0.1)

    def test_apply_discount_type_error_discount(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount(100.0, '0.1')

    def test_apply_discount_value_error_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(-10.0, 0.1)

    def test_apply_discount_value_error_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, -0.1)

    def test_apply_discount_value_error_discount_greater_than_one(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, 1.5)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calculator.calculate_shipping(99.99)
        self.assertEqual(shipping, 10.0)

    def test_calculate_shipping_at_threshold(self):
        shipping = self.calculator.calculate_shipping(100.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calculator.calculate_shipping(150.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_shipping('50.0')

    def test_calculate_tax_success(self):
        tax = self.calculator.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero_amount(self):
        tax = self.calculator.calculate_tax(0.0)
        self.assertEqual(tax, 0.0)

    def test_calculate_tax_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_tax(None)

    def test_calculate_tax_value_error_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_tax(-10.0)

    def test_calculate_total_without_discount_with_shipping(self):
        self.calculator.add_item('Book', 50.0, 1)
        self.assertAlmostEqual(self.calculator.calculate_total(), 73.8)

    def test_calculate_total_with_discount_and_free_shipping(self):
        self.calculator.add_item('Gadget', 200.0, 1)
        self.assertAlmostEqual(self.calculator.calculate_total(discount=0.5), 123.0)

    def test_calculate_total_empty_order_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_total()

    def test_calculate_total_type_error_discount(self):
        self.calculator.add_item('Book', 50.0)
        with self.assertRaises(TypeError):
            self.calculator.calculate_total(discount='10%')

    def test_calculate_total_invalid_discount_raises_value_error(self):
        self.calculator.add_item('Book', 50.0)
        with self.assertRaises(ValueError):
            self.calculator.calculate_total(discount=2.0)

    def test_total_items_empty_order(self):
        self.assertEqual(self.calculator.total_items(), 0)

    def test_total_items_multiple_items(self):
        self.calculator.add_item('Book', 10.0, 2)
        self.calculator.add_item('Pen', 2.0, 5)
        self.assertEqual(self.calculator.total_items(), 7)

    def test_clear_order(self):
        self.calculator.add_item('Book', 10.0, 2)
        self.calculator.clear_order()
        self.assertEqual(self.calculator.items, [])
        self.assertTrue(self.calculator.is_empty())

    def test_list_items_empty(self):
        self.assertEqual(self.calculator.list_items(), [])

    def test_list_items_unique_names(self):
        self.calculator.add_item('Book', 10.0, 2)
        self.calculator.add_item('Pen', 2.0, 1)
        items_list = self.calculator.list_items()
        self.assertEqual(sorted(items_list), ['Book', 'Pen'])

    def test_is_empty_true(self):
        self.assertTrue(self.calculator.is_empty())

    def test_is_empty_false(self):
        self.calculator.add_item('Book', 10.0)
        self.assertFalse(self.calculator.is_empty())