import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = OrderCalculator()

    def test_init_default_values(self):
        self.assertEqual(self.calculator.tax_rate, 0.23)
        self.assertEqual(self.calculator.free_shipping_threshold, 100.0)
        self.assertEqual(self.calculator.shipping_cost, 10.0)
        self.assertEqual(self.calculator.items, [])

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_boundary_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_boundary_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_boundary_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_init_boundary_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10.0])

    def test_init_tax_rate_below_zero(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-0.5)

    def test_add_item_typical(self):
        self.calculator.add_item('Book', 15.0, 2)
        self.assertEqual(len(self.calculator.items), 1)
        self.assertEqual(self.calculator.items[0], {'name': 'Book', 'price': 15.0, 'quantity': 2})

    def test_add_item_default_quantity(self):
        self.calculator.add_item('Pen', 2.5)
        self.assertEqual(self.calculator.items[0]['quantity'], 1)

    def test_add_item_increments_quantity_same_name_and_price(self):
        self.calculator.add_item('Notebook', 5.0, 2)
        self.calculator.add_item('Notebook', 5.0, 3)
        self.assertEqual(len(self.calculator.items), 1)
        self.assertEqual(self.calculator.items[0]['quantity'], 5)

    def test_add_item_same_name_different_price_raises_value_error(self):
        self.calculator.add_item('Notebook', 5.0, 1)
        with self.assertRaises(ValueError):
            self.calculator.add_item('Notebook', 6.0, 1)

    def test_add_item_empty_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('', 10.0, 1)

    def test_add_item_zero_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Item', 0.0, 1)

    def test_add_item_negative_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Item', -5.0, 1)

    def test_add_item_zero_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Item', 10.0, 0)

    def test_add_item_negative_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Item', 10.0, -1)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item(123, 10.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('Item', '10.0', 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('Item', 10.0, 1.5)

    def test_remove_item_typical(self):
        self.calculator.add_item('Book', 10.0, 1)
        self.calculator.add_item('Pen', 2.0, 1)
        self.calculator.remove_item('Book')
        self.assertEqual(len(self.calculator.items), 1)
        self.assertEqual(self.calculator.items[0]['name'], 'Pen')

    def test_remove_item_not_found_raises_value_error(self):
        self.calculator.add_item('Book', 10.0, 1)
        with self.assertRaises(ValueError):
            self.calculator.remove_item('Eraser')

    def test_remove_item_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calculator.remove_item(123)

    def test_get_subtotal_empty_order_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.get_subtotal()

    def test_get_subtotal_single_item(self):
        self.calculator.add_item('Book', 12.5, 2)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 25.0)

    def test_get_subtotal_multiple_items(self):
        self.calculator.add_item('Book', 10.0, 2)
        self.calculator.add_item('Pen', 5.0, 3)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 35.0)

    def test_apply_discount_typical(self):
        discounted = self.calculator.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(discounted, 80.0)

    def test_apply_discount_zero(self):
        discounted = self.calculator.apply_discount(100.0, 0.0)
        self.assertAlmostEqual(discounted, 100.0)

    def test_apply_discount_full(self):
        discounted = self.calculator.apply_discount(100.0, 1.0)
        self.assertAlmostEqual(discounted, 0.0)

    def test_apply_discount_zero_subtotal(self):
        discounted = self.calculator.apply_discount(0.0, 0.5)
        self.assertAlmostEqual(discounted, 0.0)

    def test_apply_discount_negative_subtotal_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(-10.0, 0.1)

    def test_apply_discount_negative_discount_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, -0.1)

    def test_apply_discount_exceeding_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, 1.01)

    def test_apply_discount_invalid_subtotal_type(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount('100', 0.1)

    def test_apply_discount_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount(100.0, '0.1')

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calculator.calculate_shipping(99.99)
        self.assertEqual(shipping, 10.0)

    def test_calculate_shipping_at_threshold(self):
        shipping = self.calculator.calculate_shipping(100.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calculator.calculate_shipping(150.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_zero_subtotal(self):
        shipping = self.calculator.calculate_shipping(0.0)
        self.assertEqual(shipping, 10.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_shipping('50')

    def test_calculate_tax_typical(self):
        tax = self.calculator.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero_amount(self):
        tax = self.calculator.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_tax(-10.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_tax('100')

    def test_calculate_total_empty_order_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_total()

    def test_calculate_total_without_discount_with_shipping(self):
        self.calculator.add_item('Book', 50.0, 1)
        expected_total = (50.0 + 10.0) * 1.23
        self.assertAlmostEqual(self.calculator.calculate_total(), expected_total)

    def test_calculate_total_without_discount_free_shipping(self):
        self.calculator.add_item('Shoes', 100.0, 1)
        expected_total = 100.0 * 1.23
        self.assertAlmostEqual(self.calculator.calculate_total(), expected_total)

    def test_calculate_total_with_discount_qualifies_for_shipping_charge(self):
        self.calculator.add_item('Jacket', 100.0, 1)
        expected_discounted = 80.0
        expected_shipping = 10.0
        expected_tax = (80.0 + 10.0) * 0.23
        expected_total = 80.0 + 10.0 + expected_tax
        self.assertAlmostEqual(self.calculator.calculate_total(discount=0.2), expected_total)

    def test_calculate_total_with_full_discount(self):
        self.calculator.add_item('Jacket', 100.0, 1)
        expected_shipping = 10.0
        expected_tax = 10.0 * 0.23
        expected_total = 10.0 + expected_tax
        self.assertAlmostEqual(self.calculator.calculate_total(discount=1.0), expected_total)

    def test_calculate_total_invalid_discount_value(self):
        self.calculator.add_item('Book', 20.0, 1)
        with self.assertRaises(ValueError):
            self.calculator.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calculator.calculate_total(discount=1.5)

    def test_calculate_total_invalid_discount_type(self):
        self.calculator.add_item('Book', 20.0, 1)
        with self.assertRaises(TypeError):
            self.calculator.calculate_total(discount='0.2')

    def test_total_items_empty_order(self):
        self.assertEqual(self.calculator.total_items(), 0)

    def test_total_items_multiple_entries(self):
        self.calculator.add_item('Pen', 1.5, 3)
        self.calculator.add_item('Book', 10.0, 2)
        self.assertEqual(self.calculator.total_items(), 5)

    def test_clear_order(self):
        self.calculator.add_item('Book', 10.0, 2)
        self.calculator.clear_order()
        self.assertEqual(self.calculator.items, [])
        self.assertTrue(self.calculator.is_empty())

    def test_list_items_empty(self):
        self.assertEqual(self.calculator.list_items(), [])

    def test_list_items_unique_names(self):
        self.calculator.add_item('Apple', 2.0, 3)
        self.calculator.add_item('Banana', 1.5, 2)
        items = self.calculator.list_items()
        self.assertEqual(len(items), 2)
        self.assertCountEqual(items, ['Apple', 'Banana'])

    def test_is_empty_true(self):
        self.assertTrue(self.calculator.is_empty())

    def test_is_empty_false(self):
        self.calculator.add_item('Book', 10.0, 1)
        self.assertFalse(self.calculator.is_empty())