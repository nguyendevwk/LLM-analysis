import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = OrderCalculator()

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.15)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_negative_values_raise_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-50.0)
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_invalid_types_raise_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[])

    def test_add_item_default_quantity(self):
        self.calculator.add_item('Book', 15.0)
        self.assertEqual(self.calculator.total_items(), 1)
        self.assertIn('Book', self.calculator.list_items())

    def test_add_item_explicit_quantity(self):
        self.calculator.add_item('Book', 15.0, quantity=3)
        self.assertEqual(self.calculator.total_items(), 3)

    def test_add_item_increments_existing_quantity(self):
        self.calculator.add_item('Book', 15.0, quantity=2)
        self.calculator.add_item('Book', 15.0, quantity=3)
        self.assertEqual(self.calculator.total_items(), 5)
        self.assertEqual(len(self.calculator.list_items()), 1)

    def test_add_item_zero_price(self):
        self.calculator.add_item('Sample', 0.0, quantity=1)
        self.assertEqual(self.calculator.get_subtotal(), 0.0)
        self.assertEqual(self.calculator.total_items(), 1)

    def test_add_item_negative_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Book', -10.0, quantity=1)

    def test_add_item_zero_or_negative_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Book', 10.0, quantity=0)
        with self.assertRaises(ValueError):
            self.calculator.add_item('Book', 10.0, quantity=-2)

    def test_add_item_empty_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('', 10.0, quantity=1)
        with self.assertRaises(ValueError):
            self.calculator.add_item('   ', 10.0, quantity=1)

    def test_add_item_invalid_types_raise_type_error(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item(123, 10.0, 1)
        with self.assertRaises(TypeError):
            self.calculator.add_item('Book', '10.0', 1)
        with self.assertRaises(TypeError):
            self.calculator.add_item('Book', 10.0, 1.5)

    def test_remove_item_success(self):
        self.calculator.add_item('Book', 15.0, quantity=2)
        self.calculator.remove_item('Book')
        self.assertTrue(self.calculator.is_empty())
        self.assertNotIn('Book', self.calculator.list_items())

    def test_remove_item_non_existent_raises_exception(self):
        self.calculator.add_item('Pen', 1.5)
        with self.assertRaises((KeyError, ValueError)):
            self.calculator.remove_item('Notebook')

    def test_remove_item_from_empty_order_raises_exception(self):
        with self.assertRaises((KeyError, ValueError)):
            self.calculator.remove_item('Book')

    def test_remove_item_case_sensitivity(self):
        self.calculator.add_item('Book', 15.0)
        with self.assertRaises((KeyError, ValueError)):
            self.calculator.remove_item('book')

    def test_get_subtotal_multiple_items(self):
        self.calculator.add_item('Book', 10.0, quantity=2)
        self.calculator.add_item('Pen', 2.5, quantity=4)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 30.0)

    def test_get_subtotal_empty_order(self):
        self.assertEqual(self.calculator.get_subtotal(), 0.0)

    def test_get_subtotal_floating_point_precision(self):
        self.calculator.add_item('Item1', 0.1, quantity=1)
        self.calculator.add_item('Item2', 0.2, quantity=1)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 0.3, places=7)

    def test_apply_discount_zero(self):
        discounted = self.calculator.apply_discount(100.0, 0.0)
        self.assertEqual(discounted, 100.0)

    def test_apply_discount_valid_partial(self):
        discounted = self.calculator.apply_discount(100.0, 20.0)
        self.assertEqual(discounted, 80.0)

    def test_apply_discount_full(self):
        discounted = self.calculator.apply_discount(100.0, 100.0)
        self.assertEqual(discounted, 0.0)

    def test_apply_discount_exceeds_subtotal(self):
        try:
            discounted = self.calculator.apply_discount(100.0, 150.0)
            self.assertEqual(discounted, 0.0)
        except ValueError:
            pass

    def test_apply_discount_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, -10.0)

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calculator.calculate_shipping(99.99)
        self.assertEqual(shipping, 10.0)

    def test_calculate_shipping_at_threshold_boundary(self):
        shipping = self.calculator.calculate_shipping(100.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calculator.calculate_shipping(150.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_zero_subtotal(self):
        shipping = self.calculator.calculate_shipping(0.0)
        self.assertIn(shipping, (0.0, 10.0))

    def test_calculate_shipping_negative_subtotal_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_shipping(-10.0)

    def test_calculate_tax_standard(self):
        tax = self.calculator.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero_amount(self):
        tax = self.calculator.calculate_tax(0.0)
        self.assertEqual(tax, 0.0)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_tax(-100.0)

    def test_calculate_total_without_discount_with_shipping(self):
        self.calculator.add_item('Book', 50.0, quantity=1)
        subtotal = 50.0
        shipping = 10.0
        tax = self.calculator.calculate_tax(subtotal)
        expected_total = subtotal + shipping + tax
        self.assertAlmostEqual(self.calculator.calculate_total(), expected_total)

    def test_calculate_total_without_discount_free_shipping(self):
        self.calculator.add_item('Chair', 100.0, quantity=1)
        subtotal = 100.0
        shipping = 0.0
        tax = self.calculator.calculate_tax(subtotal)
        expected_total = subtotal + shipping + tax
        self.assertAlmostEqual(self.calculator.calculate_total(), expected_total)

    def test_calculate_total_discount_triggers_shipping(self):
        self.calculator.add_item('Chair', 110.0, quantity=1)
        discount = 20.0
        discounted_subtotal = 90.0
        shipping = 10.0
        tax = self.calculator.calculate_tax(discounted_subtotal)
        expected_total = discounted_subtotal + shipping + tax
        self.assertAlmostEqual(self.calculator.calculate_total(discount=discount), expected_total)

    def test_calculate_total_empty_order(self):
        self.assertEqual(self.calculator.calculate_total(), 0.0)

    def test_calculate_total_invalid_discount_raises_value_error(self):
        self.calculator.add_item('Book', 50.0)
        with self.assertRaises(ValueError):
            self.calculator.calculate_total(discount=-5.0)

    def test_total_items_empty_order(self):
        self.assertEqual(self.calculator.total_items(), 0)

    def test_total_items_multiple_items_and_quantities(self):
        self.calculator.add_item('Book', 10.0, quantity=2)
        self.calculator.add_item('Pen', 2.0, quantity=3)
        self.assertEqual(self.calculator.total_items(), 5)

    def test_total_items_after_removal(self):
        self.calculator.add_item('Book', 10.0, quantity=2)
        self.calculator.add_item('Pen', 2.0, quantity=3)
        self.calculator.remove_item('Pen')
        self.assertEqual(self.calculator.total_items(), 2)

    def test_clear_order_resets_state(self):
        self.calculator.add_item('Book', 10.0, quantity=2)
        self.calculator.clear_order()
        self.assertEqual(self.calculator.total_items(), 0)
        self.assertEqual(self.calculator.get_subtotal(), 0.0)
        self.assertTrue(self.calculator.is_empty())

    def test_clear_order_idempotent_on_empty(self):
        self.calculator.clear_order()
        self.assertEqual(self.calculator.total_items(), 0)
        self.assertTrue(self.calculator.is_empty())

    def test_list_items_returns_all_names(self):
        self.calculator.add_item('Book', 10.0)
        self.calculator.add_item('Pen', 2.0)
        items = self.calculator.list_items()
        self.assertCountEqual(items, ['Book', 'Pen'])

    def test_list_items_empty_order(self):
        self.assertEqual(self.calculator.list_items(), [])

    def test_list_items_unique_names(self):
        self.calculator.add_item('Book', 10.0, quantity=1)
        self.calculator.add_item('Book', 10.0, quantity=2)
        items = self.calculator.list_items()
        self.assertEqual(items, ['Book'])

    def test_is_empty_initial_state(self):
        self.assertTrue(self.calculator.is_empty())

    def test_is_empty_false_when_item_added(self):
        self.calculator.add_item('Book', 10.0)
        self.assertFalse(self.calculator.is_empty())

    def test_is_empty_true_after_removing_items(self):
        self.calculator.add_item('Book', 10.0)
        self.calculator.remove_item('Book')
        self.assertTrue(self.calculator.is_empty())