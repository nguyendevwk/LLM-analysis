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

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.08, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.08)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_negative_tax_rate_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.05)

    def test_init_negative_shipping_threshold_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_negative_shipping_cost_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_is_empty_on_new_order(self):
        self.assertTrue(self.calculator.is_empty())

    def test_is_empty_after_adding_item(self):
        self.calculator.add_item('Book', 15.0, 1)
        self.assertFalse(self.calculator.is_empty())

    def test_add_item_default_quantity(self):
        self.calculator.add_item('Book', 15.0)
        self.assertEqual(self.calculator.total_items(), 1)
        self.assertIn('Book', self.calculator.list_items())

    def test_add_item_custom_quantity(self):
        self.calculator.add_item('Pen', 2.0, 5)
        self.assertEqual(self.calculator.total_items(), 5)

    def test_add_existing_item_increments_quantity(self):
        self.calculator.add_item('Notebook', 10.0, 2)
        self.calculator.add_item('Notebook', 10.0, 3)
        self.assertEqual(self.calculator.total_items(), 5)
        self.assertEqual(len(self.calculator.list_items()), 1)

    def test_add_item_negative_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Invalid Item', -5.0, 1)

    def test_add_item_zero_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Zero Item', 10.0, 0)

    def test_add_item_negative_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Negative Item', 10.0, -2)

    def test_add_item_invalid_name_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item(12345, 10.0, 1)

    def test_add_item_invalid_price_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('Book', 'expensive', 1)

    def test_add_item_invalid_quantity_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('Book', 10.0, 'two')

    def test_remove_item_success(self):
        self.calculator.add_item('Apple', 1.0, 2)
        self.calculator.remove_item('Apple')
        self.assertTrue(self.calculator.is_empty())
        self.assertNotIn('Apple', self.calculator.list_items())

    def test_remove_nonexistent_item_raises_error(self):
        with self.assertRaises((KeyError, ValueError)):
            self.calculator.remove_item('Nonexistent')

    def test_remove_item_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.remove_item(None)

    def test_get_subtotal_multiple_items(self):
        self.calculator.add_item('Apple', 2.0, 3)
        self.calculator.add_item('Banana', 1.5, 2)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 9.0)

    def test_apply_discount_zero(self):
        result = self.calculator.apply_discount(100.0, 0.0)
        self.assertAlmostEqual(result, 100.0)

    def test_apply_discount_partial(self):
        result = self.calculator.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_full(self):
        result = self.calculator.apply_discount(100.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, -0.1)

    def test_apply_discount_greater_than_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, 1.5)

    def test_apply_discount_negative_subtotal_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(-50.0, 0.1)

    def test_apply_discount_invalid_types_raise_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            self.calculator.apply_discount(100.0, 'ten percent')

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calculator.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_at_threshold(self):
        shipping = self.calculator.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calculator.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_shipping('fifty')

    def test_calculate_tax_standard_rate(self):
        tax = self.calculator.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero_amount(self):
        tax = self.calculator.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_tax(-100.0)

    def test_calculate_tax_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_tax('one hundred')

    def test_calculate_total_above_threshold_free_shipping(self):
        self.calculator.add_item('Jacket', 200.0, 1)
        expected_total = 200.0 + 0.0 + 200.0 * 0.23
        self.assertAlmostEqual(self.calculator.calculate_total(), expected_total)

    def test_calculate_total_with_invalid_discount_raises_value_error(self):
        self.calculator.add_item('Book', 50.0, 1)
        with self.assertRaises(ValueError):
            self.calculator.calculate_total(discount=-0.5)

    def test_calculate_total_with_invalid_discount_type_raises_type_error(self):
        self.calculator.add_item('Book', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calculator.calculate_total(discount='20%')

    def test_total_items_empty(self):
        self.assertEqual(self.calculator.total_items(), 0)

    def test_total_items_multiple_entries(self):
        self.calculator.add_item('Item1', 10.0, 2)
        self.calculator.add_item('Item2', 20.0, 3)
        self.assertEqual(self.calculator.total_items(), 5)

    def test_list_items_empty(self):
        self.assertEqual(self.calculator.list_items(), [])

    def test_list_items_returns_correct_names(self):
        self.calculator.add_item('ItemA', 5.0, 1)
        self.calculator.add_item('ItemB', 10.0, 2)
        items = self.calculator.list_items()
        self.assertEqual(sorted(items), ['ItemA', 'ItemB'])