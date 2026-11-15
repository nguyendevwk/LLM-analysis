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
        self.assertTrue(calc.is_empty())

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.15)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_boundary_values(self):
        calc1 = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc1.tax_rate, 0.0)
        self.assertEqual(calc1.free_shipping_threshold, 0.0)
        self.assertEqual(calc1.shipping_cost, 0.0)
        calc2 = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc2.tax_rate, 1.0)

    def test_init_tax_rate_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_negative_free_shipping_threshold_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_negative_shipping_cost_raises_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_invalid_types_raise_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10.0])

    def test_add_item_single_default_quantity(self):
        self.calc.add_item('Book', 15.0)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertIn('Book', self.calc.list_items())

    def test_add_item_single_explicit_quantity(self):
        self.calc.add_item('Pen', 2.0, quantity=5)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_existing_increases_quantity(self):
        self.calc.add_item('Book', 15.0, quantity=2)
        self.calc.add_item('Book', 15.0, quantity=3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_existing_different_price_raises_value_error(self):
        self.calc.add_item('Book', 15.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Book', 20.0)

    def test_add_item_empty_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 10.0)

    def test_add_item_zero_or_negative_price_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Freebie', 0.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Loss', -5.0)

    def test_add_item_invalid_quantity_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Book', 15.0, quantity=0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Book', 15.0, quantity=-2)

    def test_add_item_invalid_name_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 15.0)

    def test_add_item_invalid_price_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Book', '15.0')

    def test_add_item_invalid_quantity_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Book', 15.0, quantity=1.5)

    def test_remove_item_success(self):
        self.calc.add_item('Book', 15.0)
        self.calc.remove_item('Book')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_non_existent_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('NonExistent')

    def test_remove_item_invalid_name_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(None)

    def test_get_subtotal_single_item(self):
        self.calc.add_item('Book', 15.0, quantity=2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 30.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('Book', 15.0, quantity=2)
        self.calc.add_item('Pen', 2.0, quantity=5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 40.0)

    def test_get_subtotal_empty_order_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_standard(self):
        result = self.calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(100.0, 0.0)
        self.assertAlmostEqual(result, 100.0)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(100.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative_subtotal_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-50.0, 0.1)

    def test_apply_discount_negative_rate_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)

    def test_apply_discount_rate_above_one_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.1)

    def test_apply_discount_invalid_types_raise_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100.0', 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '0.1')

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_at_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_zero_subtotal(self):
        shipping = self.calc.calculate_shipping(0.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50.0')

    def test_calculate_tax_standard(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_tax_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax(None)

    def test_calculate_total_without_free_shipping(self):
        self.calc.add_item('Book', 50.0, quantity=1)
        total = self.calc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 61.5)

    def test_calculate_total_with_free_shipping(self):
        self.calc.add_item('Laptop', 1000.0, quantity=1)
        total = self.calc.calculate_total(discount=0.1)
        self.assertAlmostEqual(total, 1107.0)

    def test_calculate_total_default_discount(self):
        self.calc.add_item('Book', 50.0, quantity=1)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 73.8)

    def test_calculate_total_full_discount(self):
        self.calc.add_item('Book', 50.0, quantity=1)
        total = self.calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 12.3)

    def test_calculate_total_empty_order_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_invalid_discount_raises_value_error(self):
        self.calc.add_item('Book', 50.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.5)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.5)

    def test_calculate_total_invalid_discount_type_raises_type_error(self):
        self.calc.add_item('Book', 50.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_total_items_empty_order(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_populated_order(self):
        self.calc.add_item('Book', 15.0, quantity=2)
        self.calc.add_item('Pen', 2.0, quantity=3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order_populated(self):
        self.calc.add_item('Book', 15.0, quantity=2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_already_empty(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items_empty_order(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_populated_order(self):
        self.calc.add_item('Book', 15.0, quantity=2)
        self.calc.add_item('Pen', 2.0, quantity=1)
        items = self.calc.list_items()
        self.assertEqual(len(items), 2)
        self.assertIn('Book', items)
        self.assertIn('Pen', items)

    def test_is_empty_new_order(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_populated_order(self):
        self.calc.add_item('Book', 15.0)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_cleared_order(self):
        self.calc.add_item('Book', 15.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())