import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_parameters(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_init_custom_parameters(self):
        oc = OrderCalculator(tax_rate=0.08, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(oc.tax_rate, 0.08)
        self.assertEqual(oc.free_shipping_threshold, 50.0)
        self.assertEqual(oc.shipping_cost, 5.0)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_single_default_quantity(self):
        self.calc.add_item('Apple', 1.2)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.2, places=2)

    def test_add_item_single_explicit_quantity(self):
        self.calc.add_item('Banana', 0.5, 4)
        self.assertIn('Banana', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0, places=2)

    def test_add_item_increment_quantity(self):
        self.calc.add_item('Milk', 2.0, 1)
        self.calc.add_item('Milk', 2.0, 2)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0, places=2)

    def test_add_item_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_empty_string_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0)

    def test_add_item_price_zero_or_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Pen', 0.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Pen', -1.5)

    def test_add_item_price_not_number(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Pen', 'free')

    def test_add_item_quantity_zero_or_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Notebook', 2.5, 0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Notebook', 2.5, -3)

    def test_add_item_quantity_not_int(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Notebook', 2.5, 2.5)

    def test_remove_item_one_of_multiple(self):
        self.calc.add_item('A', 1.0)
        self.calc.add_item('B', 2.0)
        self.calc.remove_item('A')
        self.assertIn('B', self.calc.list_items())
        self.assertNotIn('A', self.calc.list_items())
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0, places=2)

    def test_remove_item_name_not_string(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(42)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('X', 3.33, 3)
        self.calc.add_item('Y', 4.44, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 18.87, places=2)

    def test_get_subtotal_floating_precision(self):
        self.calc.add_item('Z', 0.1, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.3, places=2)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(result, 50.0, places=2)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -5.0)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 5.0)

    def test_calculate_shipping_below_threshold(self):
        cost = self.calc.calculate_shipping(45.0)
        self.assertAlmostEqual(cost, 10.0, places=2)

    def test_calculate_shipping_at_threshold(self):
        cost = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(cost, 0.0, places=2)

    def test_calculate_shipping_above_threshold(self):
        cost = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(cost, 0.0, places=2)

    def test_calculate_tax_positive_amount(self):
        tax = self.calc.calculate_tax(200.0)
        self.assertAlmostEqual(tax, 46.0, places=2)

    def test_calculate_tax_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0, places=2)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_total_no_discount_above_threshold(self):
        self.calc.add_item('Item1', 60.0)
        self.calc.add_item('Item2', 60.0)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 147.6, places=2)

    def test_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-5.0)

    def test_total_items_empty_order(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_multiple_quantities(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 1.0, 5)
        self.calc.add_item('C', 1.0, 1)
        self.assertEqual(self.calc.total_items(), 8)

    def test_clear_order_on_empty_order(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items_empty_order(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_after_adding(self):
        self.calc.add_item('Pen', 1.0)
        self.calc.add_item('Pencil', 0.5)
        self.calc.add_item('Eraser', 0.2)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['Pen', 'Pencil', 'Eraser'])

    def test_list_items_after_removing_one(self):
        self.calc.add_item('Pen', 1.0)
        self.calc.add_item('Pencil', 0.5)
        self.calc.remove_item('Pen')
        self.assertCountEqual(self.calc.list_items(), ['Pencil'])

    def test_is_empty_fresh_instance(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_adding(self):
        self.calc.add_item('Item', 1.0)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_removing_only_item(self):
        self.calc.add_item('Item', 1.0)
        self.calc.remove_item('Item')
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('Item', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_boundary_price_exactly_at_threshold(self):
        self.calc.add_item('Item', 100.0)
        total = self.calc.calculate_total()
        expected_tax = 100.0 * 0.23
        self.assertAlmostEqual(total, 100.0 + expected_tax, places=2)

    def test_boundary_price_just_above_threshold(self):
        self.calc.add_item('Item', 100.01)
        total = self.calc.calculate_total()
        expected_tax = 100.01 * 0.23
        self.assertAlmostEqual(total, 100.01 + expected_tax, places=2)

    def test_error_propagation_non_numeric_inputs(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 10)
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50')
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('20')

    def test_add_item_after_clear_order(self):
        self.calc.add_item('Item', 1.0)
        self.calc.clear_order()
        self.calc.add_item('New', 2.0)
        self.assertIn('New', self.calc.list_items())
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0, places=2)

    def test_custom_configuration_affects_calculations(self):
        oc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=200.0, shipping_cost=15.0)
        oc.add_item('Item', 180.0)
        shipping = oc.calculate_shipping(180.0)
        tax = oc.calculate_tax(180.0)
        self.assertAlmostEqual(shipping, 15.0, places=2)
        self.assertAlmostEqual(tax, 9.0, places=2)
        oc.add_item('Extra', 30.0)
        shipping2 = oc.calculate_shipping(210.0)
        self.assertAlmostEqual(shipping2, 0.0, places=2)

    def test_custom_configuration_invalid_values(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='high')
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)