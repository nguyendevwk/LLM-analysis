import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_values(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(100.0), 23.0)
        self.assertEqual(calc.calculate_shipping(99.0), 10.0)

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_tax(100.0), 10.0)
        self.assertEqual(calc.calculate_shipping(49.0), 5.0)

    def test_init_invalid_tax_rate(self):
        with self.assertRaises((ValueError, TypeError)):
            OrderCalculator(tax_rate=-0.1)

    def test_init_invalid_shipping_cost(self):
        with self.assertRaises((ValueError, TypeError)):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_invalid_free_shipping_threshold(self):
        with self.assertRaises((ValueError, TypeError)):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_add_item_success(self):
        self.calc.add_item('Book', 15.0, 2)
        self.assertFalse(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 2)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Pen', 2.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.5)

    def test_add_item_invalid_price_zero_or_negative(self):
        with self.assertRaises((ValueError, TypeError)):
            self.calc.add_item('Item', 0.0, 1)
        with self.assertRaises((ValueError, TypeError)):
            self.calc.add_item('Item', -10.0, 1)

    def test_add_item_invalid_quantity_zero_or_negative(self):
        with self.assertRaises((ValueError, TypeError)):
            self.calc.add_item('Item', 10.0, 0)
        with self.assertRaises((ValueError, TypeError)):
            self.calc.add_item('Item', 10.0, -1)

    def test_add_item_empty_name(self):
        with self.assertRaises((ValueError, TypeError)):
            self.calc.add_item('', 10.0, 1)

    def test_add_item_invalid_types(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 10.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('Item', '10.0', 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('Item', 10.0, 1.5)

    def test_remove_item_success(self):
        self.calc.add_item('Book', 15.0, 2)
        self.calc.remove_item('Book')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_not_found(self):
        with self.assertRaises((KeyError, ValueError)):
            self.calc.remove_item('NonExistent')

    def test_remove_item_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_empty(self):
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('Item A', 10.0, 2)
        self.calc.add_item('Item B', 15.5, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 35.5)

    def test_apply_discount_valid(self):
        discounted = self.calc.apply_discount(100.0, 15.0)
        self.assertAlmostEqual(discounted, 85.0)

    def test_apply_discount_zero(self):
        discounted = self.calc.apply_discount(100.0, 0.0)
        self.assertAlmostEqual(discounted, 100.0)

    def test_apply_discount_negative(self):
        with self.assertRaises((ValueError, TypeError)):
            self.calc.apply_discount(100.0, -10.0)

    def test_apply_discount_exceeding_subtotal(self):
        with self.assertRaises((ValueError, TypeError)):
            self.calc.apply_discount(50.0, 60.0)

    def test_apply_discount_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 10.0)

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        with self.assertRaises((ValueError, TypeError)):
            self.calc.calculate_shipping(-10.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50.0')

    def test_calculate_tax_standard(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises((ValueError, TypeError)):
            self.calc.calculate_tax(-50.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100.0')

    def test_calculate_total_empty_order(self):
        self.assertEqual(self.calc.calculate_total(), 0.0)

    def test_calculate_total_with_shipping(self):
        self.calc.add_item('Item', 50.0, 1)
        subtotal = 50.0
        shipping = 10.0
        tax = 50.0 * 0.23
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.0), expected)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item('Item', 120.0, 1)
        subtotal = 120.0
        shipping = 0.0
        tax = 120.0 * 0.23
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.0), expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('Item', 100.0, 1)
        discounted = 80.0
        shipping = 10.0
        tax = 80.0 * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(20.0), expected)

    def test_calculate_total_invalid_discount(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises((ValueError, TypeError)):
            self.calc.calculate_total(-10.0)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_multiple(self):
        self.calc.add_item('A', 10.0, 2)
        self.calc.add_item('B', 20.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order(self):
        self.calc.add_item('A', 10.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_non_empty(self):
        self.calc.add_item('Apple', 1.0, 5)
        self.calc.add_item('Banana', 2.0, 2)
        items = self.calc.list_items()
        self.assertIn('Apple', items)
        self.assertIn('Banana', items)
        self.assertEqual(len(items), 2)

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('Pen', 1.5, 1)
        self.assertFalse(self.calc.is_empty())