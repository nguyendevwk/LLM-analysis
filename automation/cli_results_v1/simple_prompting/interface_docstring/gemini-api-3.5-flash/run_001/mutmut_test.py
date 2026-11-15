import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = OrderCalculator()

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_init_custom_valid_parameters(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertTrue(calc.is_empty())

    def test_init_tax_rate_below_zero_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_above_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_init_negative_free_shipping_threshold_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_negative_shipping_cost_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_invalid_tax_rate_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_invalid_threshold_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_invalid_shipping_cost_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_add_item_success(self):
        self.calculator.add_item('Book', 15.0, 2)
        self.assertEqual(self.calculator.total_items(), 2)

    def test_add_item_default_quantity(self):
        self.calculator.add_item('Pen', 2.0)
        self.assertEqual(self.calculator.total_items(), 1)

    def test_add_item_same_name_same_price_increases_quantity(self):
        self.calculator.add_item('Book', 15.0, 2)
        self.calculator.add_item('Book', 15.0, 3)
        self.assertEqual(self.calculator.total_items(), 5)

    def test_add_item_same_name_different_price_raises_value_error(self):
        self.calculator.add_item('Book', 15.0, 1)
        with self.assertRaises(ValueError):
            self.calculator.add_item('Book', 20.0, 1)

    def test_add_item_empty_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('', 10.0, 1)

    def test_add_item_zero_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Freebie', 0.0, 1)

    def test_add_item_negative_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Defect', -5.0, 1)

    def test_add_item_zero_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Item', 10.0, 0)

    def test_add_item_negative_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Item', 10.0, -1)

    def test_add_item_invalid_name_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item(123, 10.0, 1)

    def test_add_item_invalid_price_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('Item', '10.0', 1)

    def test_add_item_invalid_quantity_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('Item', 10.0, '1')

    def test_remove_item_success(self):
        self.calculator.add_item('Book', 15.0, 2)
        self.calculator.remove_item('Book')
        self.assertTrue(self.calculator.is_empty())

    def test_remove_item_non_existent_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.remove_item('NonExistent')

    def test_remove_item_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.remove_item(123)

    def test_get_subtotal_single_item(self):
        self.calculator.add_item('Book', 15.0, 2)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 30.0)

    def test_get_subtotal_multiple_items(self):
        self.calculator.add_item('Book', 15.0, 2)
        self.calculator.add_item('Pen', 2.5, 4)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 40.0)

    def test_get_subtotal_empty_order_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.get_subtotal()

    def test_apply_discount_valid(self):
        result = self.calculator.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_zero_discount(self):
        result = self.calculator.apply_discount(100.0, 0.0)
        self.assertAlmostEqual(result, 100.0)

    def test_apply_discount_full_discount(self):
        result = self.calculator.apply_discount(100.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_zero_subtotal(self):
        result = self.calculator.apply_discount(0.0, 0.5)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative_subtotal_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(-10.0, 0.2)

    def test_apply_discount_negative_discount_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, -0.1)

    def test_apply_discount_greater_than_one_discount_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, 1.1)

    def test_apply_discount_invalid_subtotal_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount('100', 0.2)

    def test_apply_discount_invalid_discount_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount(100.0, '0.2')

    def test_calculate_shipping_below_threshold(self):
        cost = self.calculator.calculate_shipping(99.9)
        self.assertAlmostEqual(cost, 10.0)

    def test_calculate_shipping_at_threshold(self):
        cost = self.calculator.calculate_shipping(100.0)
        self.assertAlmostEqual(cost, 0.0)

    def test_calculate_shipping_above_threshold(self):
        cost = self.calculator.calculate_shipping(150.0)
        self.assertAlmostEqual(cost, 0.0)

    def test_calculate_shipping_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_shipping('50.0')

    def test_calculate_tax_valid_amount(self):
        tax = self.calculator.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero_amount(self):
        tax = self.calculator.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_tax(-50.0)

    def test_calculate_tax_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_tax('100')

    def test_calculate_total_without_discount(self):
        self.calculator.add_item('Item1', 50.0, 1)
        total = self.calculator.calculate_total(0.0)
        self.assertAlmostEqual(total, 73.8)

    def test_calculate_total_with_discount_qualifying_free_shipping(self):
        self.calculator.add_item('Item1', 200.0, 1)
        total = self.calculator.calculate_total(0.25)
        self.assertAlmostEqual(total, 184.5)

    def test_calculate_total_empty_order_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_total()

    def test_calculate_total_invalid_discount_value_raises_value_error(self):
        self.calculator.add_item('Item1', 50.0, 1)
        with self.assertRaises(ValueError):
            self.calculator.calculate_total(1.5)

    def test_calculate_total_invalid_discount_type_raises_type_error(self):
        self.calculator.add_item('Item1', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calculator.calculate_total('0.1')

    def test_total_items_empty_order(self):
        self.assertEqual(self.calculator.total_items(), 0)

    def test_total_items_multiple_items(self):
        self.calculator.add_item('Item1', 10.0, 2)
        self.calculator.add_item('Item2', 20.0, 3)
        self.assertEqual(self.calculator.total_items(), 5)

    def test_clear_order_clears_all_items(self):
        self.calculator.add_item('Item1', 10.0, 2)
        self.calculator.clear_order()
        self.assertTrue(self.calculator.is_empty())
        self.assertEqual(self.calculator.total_items(), 0)

    def test_clear_order_on_already_empty_order(self):
        self.calculator.clear_order()
        self.assertTrue(self.calculator.is_empty())

    def test_list_items_empty(self):
        self.assertEqual(self.calculator.list_items(), [])

    def test_list_items_unique_names(self):
        self.calculator.add_item('Book', 10.0, 1)
        self.calculator.add_item('Pen', 2.0, 5)
        self.calculator.add_item('Book', 10.0, 2)
        items = self.calculator.list_items()
        self.assertEqual(sorted(items), ['Book', 'Pen'])

    def test_is_empty_returns_true_when_empty(self):
        self.assertTrue(self.calculator.is_empty())

    def test_is_empty_returns_false_when_not_empty(self):
        self.calculator.add_item('Book', 10.0, 1)
        self.assertFalse(self.calculator.is_empty())