import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.tax_rate, 0.23, places=6)
        self.assertAlmostEqual(calc.free_shipping_threshold, 100.0, places=6)
        self.assertAlmostEqual(calc.shipping_cost, 10.0, places=6)

    def test_init_custom_numeric(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.tax_rate, 0.1, places=6)
        self.assertAlmostEqual(calc.free_shipping_threshold, 50.0, places=6)
        self.assertAlmostEqual(calc.shipping_cost, 5.0, places=6)

    def test_init_non_numeric_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='high')

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_non_numeric_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='cheap')

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_non_numeric_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='free')

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_add_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5, 2)
        self.assertIn('Apple', calc.list_items())
        self.assertEqual(calc.total_items(), 2)
        self.assertAlmostEqual(calc.get_subtotal(), 3.0, places=6)

    def test_add_duplicate_item(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.5, 3)
        calc.add_item('Banana', 0.5, 2)
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 2.5, places=6)

    def test_add_item_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Grape', 0.3, -2)

    def test_add_item_non_int_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Peach', 1.2, 2.5)

    def test_add_item_negative_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Mango', -1.0, 1)

    def test_add_item_non_numeric_price(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Kiwi', 'free', 1)

    def test_add_item_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0, 1)

    def test_add_item_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_remove_item_multiple_quantities(self):
        calc = OrderCalculator()
        calc.add_item('Banana', 0.5, 3)
        calc.add_item('Banana', 0.5, 2)
        calc.remove_item('Banana')
        self.assertNotIn('Banana', calc.list_items())
        self.assertEqual(calc.total_items(), 0)

    def test_remove_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises((ValueError, TypeError)):
            calc.remove_item('')

    def test_remove_non_string_name(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(456)

    def test_get_subtotal_after_adds(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 4)
        expected = 1.0 * 2 + 0.5 * 4
        self.assertAlmostEqual(calc.get_subtotal(), expected, places=6)

    def test_get_subtotal_after_removes(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 4)
        calc.remove_item('Apple')
        expected = 0.5 * 4
        self.assertAlmostEqual(calc.get_subtotal(), expected, places=6)

    def test_apply_discount_negative_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -5.0)

    def test_apply_discount_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 5.0)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(90.0)
        self.assertAlmostEqual(shipping, 10.0, places=6)

    def test_calculate_shipping_at_threshold(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0, places=6)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(110.0)
        self.assertAlmostEqual(shipping, 0.0, places=6)

    def test_calculate_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        shipping = calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, 0.0, places=6)

    def test_calculate_tax_positive_amount(self):
        calc = OrderCalculator()
        tax = calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0, places=6)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        tax = calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0, places=6)

    def test_calculate_tax_negative_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-10.0)

    def test_calculate_total_no_discount_above_threshold(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 110)
        total = calc.calculate_total()
        expected = 110.0 + 110.0 * 0.23
        self.assertAlmostEqual(total, expected, places=6)

    def test_calculate_total_negative_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-5.0)

    def test_total_items_after_adding(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        calc.add_item('Banana', 0.5, 2)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_removing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 3)
        calc.add_item('Banana', 0.5, 2)
        calc.remove_item('Apple')
        self.assertEqual(calc.total_items(), 2)

    def test_total_items_empty_order(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_then_add_new_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.clear_order()
        calc.add_item('Banana', 0.5, 3)
        self.assertIn('Banana', calc.list_items())
        self.assertNotIn('Apple', calc.list_items())

    def test_list_items_after_adding(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 0.5, 2)
        items = calc.list_items()
        self.assertIn('Apple', items)
        self.assertIn('Banana', items)

    def test_list_items_duplicate_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Apple', 1.0, 2)
        items = calc.list_items()
        self.assertEqual(len(items), 1)
        self.assertIn('Apple', items)

    def test_list_items_empty_order(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_is_empty_after_construction(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_adding_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_removing_last_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_clearing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_non_numeric_numeric_parameters(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='high')
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='cheap')
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='free')
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 'price', 1)
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, 1.5)
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, 'discount')
        with self.assertRaises(TypeError):
            calc.calculate_tax('amount')

    def test_negative_values_disallowed(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', -1.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, -2)
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -5.0)
        with self.assertRaises(ValueError):
            calc.calculate_tax(-10.0)

    def test_add_item_empty_name_exception(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0, 1)

    def test_add_item_non_string_name_exception(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    def test_threshold_exactly_at_subtotal(self):
        calc = OrderCalculator()
        shipping = calc.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0, places=6)

    def test_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        shipping = calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, 0.0, places=6)

    def test_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        tax = calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 0.0, places=6)

    def test_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        shipping = calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, 0.0, places=6)

    def test_isolation_of_tests(self):
        calc1 = OrderCalculator()
        calc1.add_item('Apple', 1.0, 1)
        calc2 = OrderCalculator()
        self.assertTrue(calc2.is_empty())
        self.assertNotIn('Apple', calc2.list_items())
if __name__ == '__main__':
    unittest.main()