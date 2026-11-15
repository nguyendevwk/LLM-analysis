import unittest
import math
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_values(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertEqual(self.calc.items, [])

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError) as cm:
            OrderCalculator(tax_rate='0.2')
        self.assertIn("Tax rate must be a float or int.", str(cm.exception))

    def test_init_invalid_tax_rate_value(self):
        with self.assertRaises(ValueError) as cm:
            OrderCalculator(tax_rate=1.5)
        self.assertIn("Tax rate must be between 0.0 and 1.0.", str(cm.exception))

    def test_init_negative_threshold(self):
        with self.assertRaises(ValueError) as cm:
            OrderCalculator(free_shipping_threshold=-10)
        self.assertIn("Free shipping threshold cannot be negative.", str(cm.exception))

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError) as cm:
            OrderCalculator(shipping_cost=-5)
        self.assertIn("Shipping cost cannot be negative.", str(cm.exception))

    def test_init_non_numeric_threshold(self):
        with self.assertRaises(TypeError) as cm:
            OrderCalculator(free_shipping_threshold='50')
        self.assertIn("Free shipping threshold must be a float or int.", str(cm.exception))

    def test_init_non_numeric_shipping_cost(self):
        with self.assertRaises(TypeError) as cm:
            OrderCalculator(shipping_cost='10')
        self.assertIn("Shipping cost must be a float or int.", str(cm.exception))

    def test_init_boundary_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_boundary_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_boundary_free_shipping_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_init_boundary_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_add_item_basic(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 2)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Banana', 0.8)
        self.assertEqual(self.calc.items[0]['quantity'], 1)

    def test_add_item_increment_quantity(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(self.calc.items[0]['quantity'], 4)

    def test_add_item_same_name_diff_price(self):
        self.calc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError) as cm:
            self.calc.add_item('Apple', 1.6, 1)
        self.assertIn("Item with the same name but different price already exists.", str(cm.exception))

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError) as cm:
            self.calc.add_item('', 1.0, 1)
        self.assertIn("Item name cannot be empty.", str(cm.exception))

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError) as cm:
            self.calc.add_item('Apple', 1.0, 0)
        self.assertIn("Quantity must be at least 1.", str(cm.exception))

    def test_add_item_zero_price(self):
        with self.assertRaises(ValueError) as cm:
            self.calc.add_item('Apple', 0, 1)
        self.assertIn("Price must be greater than 0.", str(cm.exception))

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError) as cm:
            self.calc.add_item(123, 1.0, 1)
        self.assertIn("Item name must be a string.", str(cm.exception))

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError) as cm:
            self.calc.add_item('Apple', '1.0', 1)
        self.assertIn("Price must be a number.", str(cm.exception))

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError) as cm:
            self.calc.add_item('Apple', 1.0, '2')
        self.assertIn("Quantity must be an integer.", str(cm.exception))

    def test_add_item_whitespace_name(self):
        self.calc.add_item('   ', 1.0, 1)
        self.assertEqual(self.calc.items[0]['name'], '   ')

    def test_add_item_integer_price(self):
        self.calc.add_item('Item', 2, 1)
        self.assertEqual(self.calc.items[0]['price'], 2)

    def test_add_item_integer_quantity(self):
        self.calc.add_item('Item', 1.0, 3)
        self.assertEqual(self.calc.items[0]['quantity'], 3)

    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 1.5, 1)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.items, [])

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError) as cm:
            self.calc.remove_item('Orange')
        self.assertIn("Item with name 'Orange' does not exist in the order.", str(cm.exception))

    def test_remove_item_invalid_type(self):
        with self.assertRaises(TypeError) as cm:
            self.calc.remove_item(123)
        self.assertIn("Item name must be a string.", str(cm.exception))

    def test_get_subtotal_nonempty(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 0.8, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5.9, places=4)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError) as cm:
            self.calc.get_subtotal()
        self.assertIn("Cannot calculate subtotal on empty order.", str(cm.exception))

    def test_apply_discount_valid(self):
        self.assertAlmostEqual(self.calc.apply_discount(100, 0.2), 80.0, places=4)

    def test_apply_discount_full(self):
        self.assertAlmostEqual(self.calc.apply_discount(50, 1.0), 0.0, places=4)

    def test_apply_discount_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(50, 0.0), 50.0, places=4)

    def test_apply_discount_invalid_discount_type(self):
        with self.assertRaises(TypeError) as cm:
            self.calc.apply_discount(100, '0.2')
        self.assertIn("Discount must be a number.", str(cm.exception))

    def test_apply_discount_invalid_subtotal_type(self):
        with self.assertRaises(TypeError) as cm:
            self.calc.apply_discount('100', 0.2)
        self.assertIn("Subtotal must be a number.", str(cm.exception))

    def test_apply_discount_invalid_discount_value(self):
        with self.assertRaises(ValueError) as cm:
            self.calc.apply_discount(50, 1.5)
        self.assertIn("Discount must be between 0.0 and 1.0.", str(cm.exception))

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError) as cm:
            self.calc.apply_discount(-10, 0.2)
        self.assertIn("Cannot apply discount on negative subtotal.", str(cm.exception))

    def test_apply_discount_negative_discount(self):
        with self.assertRaises(ValueError) as cm:
            self.calc.apply_discount(50, -0.1)
        self.assertIn("Discount must be between 0.0 and 1.0.", str(cm.exception))

    def test_calculate_shipping_free(self):
        self.assertEqual(self.calc.calculate_shipping(120), 0.0)

    def test_calculate_shipping_paid(self):
        self.assertEqual(self.calc.calculate_shipping(80), 10.0)

    def test_calculate_shipping_exact_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100), 0.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError) as cm:
            self.calc.calculate_shipping('80')
        self.assertIn("Discounted subtotal must be a number.", str(cm.exception))

    def test_calculate_shipping_negative_subtotal(self):
        self.assertEqual(self.calc.calculate_shipping(-5), 10.0)

    def test_calculate_tax_valid(self):
        self.assertAlmostEqual(self.calc.calculate_tax(50), 11.5, places=4)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0), 0.0, places=4)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError) as cm:
            self.calc.calculate_tax('50')
        self.assertIn("Amount must be a number.", str(cm.exception))

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError) as cm:
            self.calc.calculate_tax(-5)
        self.assertIn("Cannot calculate tax on negative amount.", str(cm.exception))

    def test_calculate_total_basic(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 0.8, 3)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 19.557, places=3)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 0.8, 3)
        total = self.calc.calculate_total(0.2)
        self.assertAlmostEqual(total, 18.1056, places=4)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item('Item', 30, 4)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 147.6, places=4)

    def test_calculate_total_zero_tax(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Apple', 1.5, 2)
        calc.add_item('Banana', 0.8, 3)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 15.9, places=4)

    def test_calculate_total_full_discount(self):
        self.calc.add_item('Apple', 1.5, 2)
        total = self.calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 10.0, places=4)

    def test_calculate_total_multiple_items(self):
        self.calc.add_item('ItemA', 30, 2)
        total = self.calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 49.2, places=4)

    def test_calculate_total_threshold_boundary(self):
        self.calc.add_item('Item', 20, 5)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 147.6, places=4)

    def test_calculate_total_threshold_just_above(self):
        self.calc.add_item('Item', 20, 5)
        self.calc.free_shipping_threshold = 99.0
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 147.6, places=4)

    def test_calculate_total_threshold_just_below(self):
        self.calc.add_item('Item', 20, 5)
        self.calc.free_shipping_threshold = 101.0
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 157.6, places=4)

    def test_calculate_total_invalid_discount_type(self):
        with self.assertRaises(TypeError) as cm:
            self.calc.calculate_total('0.2')
        self.assertIn("Discount must be a number.", str(cm.exception))

    def test_calculate_total_invalid_discount_value(self):
        with self.assertRaises(ValueError) as cm:
            self.calc.calculate_total(1.5)
        self.assertIn("Discount must be between 0.0 and 1.0.", str(cm.exception))

    def test_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError) as cm:
            self.calc.calculate_total(-0.1)
        self.assertIn("Discount must be between 0.0 and 1.0.", str(cm.exception))

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError) as cm:
            self.calc.calculate_total()
        self.assertIn("Cannot calculate subtotal on empty order.", str(cm.exception))

    def test_calculate_total_discount_none(self):
        with self.assertRaises(TypeError) as cm:
            self.calc.calculate_total(None)
        self.assertIn("Discount must be a number.", str(cm.exception))

    def test_total_items_single(self):
        self.calc.add_item('Apple', 1.5, 3)
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_multiple(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 0.8, 5)
        self.assertEqual(self.calc.total_items(), 7)

    def test_total_items_after_clear(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_list_items_unique(self):
        self.calc.add_item('Apple', 1.5, 1)
        self.calc.add_item('Apple', 1.5, 1)
        self.calc.add_item('Banana', 0.8, 1)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['Apple', 'Banana'])

    def test_list_items_order_not_guaranteed(self):
        self.calc.add_item('Apple', 1.5, 1)
        self.calc.add_item('Banana', 0.8, 1)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['Apple', 'Banana'])

    def test_list_items_after_clear(self):
        self.calc.add_item('Apple', 1.5, 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('Apple', 1.5, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('Apple', 1.5, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_clear_order(self):
        self.calc.add_item('Apple', 1.5, 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.items, [])
        self.assertTrue(self.calc.is_empty())

    def test_add_item_large_quantity(self):
        self.calc.add_item('Apple', 1.5, 10**9)
        self.assertEqual(self.calc.items[0]['quantity'], 10**9)

    def test_add_item_large_price(self):
        self.calc.add_item('Apple', 10**9, 1)
        self.assertEqual(self.calc.items[0]['price'], 10**9)

    def test_apply_discount_edge_high(self):
        result = self.calc.apply_discount(100, 0.999999)
        self.assertAlmostEqual(result, 0.0001, places=4)

    def test_calculate_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.calculate_shipping(10), 0.0)

    def test_calculate_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(10), 0.0)

    def test_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc.calculate_tax(50), 0.0, places=4)

    def test_calculate_tax_full_rate(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc.calculate_tax(50), 50.0, places=4)

    def test_calculate_total_high_threshold_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=1000.0)
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 11.655, places=3)

    def test_calculate_total_discount_full_high_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=1000.0)
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 10.0, places=4)

    def test_calculate_total_discount_full_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 0.0, places=4)

    def test_calculate_total_discount_zero_tax(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 0.0, places=4)

    def test_calculate_total_discount_zero_shipping(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 0.0, places=4)

    def test_calculate_total_discount_zero_shipping_nonzero_tax(self):
        calc = OrderCalculator(shipping_cost=10.0, tax_rate=0.23)
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(1.0)
        self.assertAlmostEqual(total, 10.0, places=4)

    def test_calculate_total_discount_half_zero_shipping(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 0.75, places=4)

    def test_calculate_total_discount_half_shipping(self):
        calc = OrderCalculator(shipping_cost=10.0)
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 10.75, places=4)

    def test_calculate_total_discount_half_zero_tax(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 10.0, places=4)

    def test_calculate_total_discount_half_full_tax(self):
        calc = OrderCalculator(tax_rate=1.0)
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 20.5, places=4)

    def test_calculate_total_discount_half_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=0.75)
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 0.75, places=4)

    def test_calculate_total_discount_half_shipping_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=1.0)
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 10.75, places=4)

    def test_calculate_total_discount_half_shipping_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.5)
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 0.75, places=4)

    def test_calculate_total_discount_half_zero_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 0.75, places=4)

    def test_calculate_total_discount_half_inf_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=float('inf'))
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 10.75, places=4)

    def test_calculate_total_discount_half_inf_shipping(self):
        calc = OrderCalculator(shipping_cost=float('inf'))
        calc.add_item('Apple', 1.5, 1)
        with self.assertRaises(OverflowError):
            calc.calculate_total(0.5)

    def test_calculate_total_discount_half_inf_tax(self):
        calc = OrderCalculator(tax_rate=float('inf'))
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(0.5)
        self.assertTrue(math.isinf(total))

    def test_calculate_total_discount_half_nan_tax(self):
        calc = OrderCalculator(tax_rate=float('nan'))
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(0.5)
        self.assertTrue(math.isnan(total))

    def test_calculate_total_discount_half_nan_shipping(self):
        calc = OrderCalculator(shipping_cost=float('nan'))
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(0.5)
        self.assertTrue(math.isnan(total))

    def test_calculate_total_discount_half_nan_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=float('nan'))
        calc.add_item('Apple', 1.5, 1)
        total = calc.calculate_total(0.5)
        self.assertAlmostEqual(total, 10.75, places=4)

    def test_calculate_total_discount_half_none_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=None)
        calc.add_item('Apple', 1.5, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(0.5)

if __name__ == '__main__':
    unittest.main()