import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = OrderCalculator()

    def test_init_default_values(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.tax_rate, 0.23)
        self.assertAlmostEqual(calc.free_shipping_threshold, 100.0)
        self.assertAlmostEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.08, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(calc.tax_rate, 0.08)
        self.assertAlmostEqual(calc.free_shipping_threshold, 50.0)
        self.assertAlmostEqual(calc.shipping_cost, 5.0)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.05)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_invalid_types(self):
        with self.assertRaises((TypeError, ValueError)):
            OrderCalculator(tax_rate='0.23')

    def test_is_empty_initially(self):
        self.assertTrue(self.calculator.is_empty())

    def test_is_empty_after_adding_item(self):
        self.calculator.add_item('Book', 15.0, 1)
        self.assertFalse(self.calculator.is_empty())

    def test_total_items_initially(self):
        self.assertEqual(self.calculator.total_items(), 0)

    def test_total_items_single_item(self):
        self.calculator.add_item('Book', 15.0, 3)
        self.assertEqual(self.calculator.total_items(), 3)

    def test_total_items_multiple_items(self):
        self.calculator.add_item('Book', 15.0, 2)
        self.calculator.add_item('Pen', 2.5, 5)
        self.assertEqual(self.calculator.total_items(), 7)

    def test_add_item_default_quantity(self):
        self.calculator.add_item('Apple', 1.5)
        self.assertEqual(self.calculator.total_items(), 1)
        self.assertIn('Apple', self.calculator.list_items())

    def test_add_item_accumulates_quantity_for_existing_name(self):
        self.calculator.add_item('Apple', 2.0, 2)
        self.calculator.add_item('Apple', 2.0, 3)
        self.assertEqual(self.calculator.total_items(), 5)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 10.0)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('', 10.0, 1)

    def test_add_item_non_string_name(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calculator.add_item(123, 10.0, 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Book', -10.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calculator.add_item('Book', 'invalid_price', 1)

    def test_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Book', 10.0, 0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Book', 10.0, -1)

    def test_add_item_non_integer_quantity(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calculator.add_item('Book', 10.0, 1.5)

    def test_remove_item_success(self):
        self.calculator.add_item('Book', 15.0, 2)
        self.calculator.remove_item('Book')
        self.assertTrue(self.calculator.is_empty())
        self.assertEqual(self.calculator.total_items(), 0)

    def test_remove_item_not_found(self):
        with self.assertRaises((KeyError, ValueError)):
            self.calculator.remove_item('NonExistentItem')

    def test_remove_item_invalid_type(self):
        with self.assertRaises((TypeError, ValueError, KeyError)):
            self.calculator.remove_item(None)

    def test_list_items_empty(self):
        self.assertEqual(self.calculator.list_items(), [])

    def test_list_items_populated(self):
        self.calculator.add_item('Book', 10.0, 1)
        self.calculator.add_item('Pen', 2.0, 1)
        items = self.calculator.list_items()
        self.assertEqual(len(items), 2)
        self.assertIn('Book', items)
        self.assertIn('Pen', items)

    def test_get_subtotal_multiple_items(self):
        self.calculator.add_item('Book', 20.0, 2)
        self.calculator.add_item('Pen', 5.0, 3)
        self.assertAlmostEqual(self.calculator.get_subtotal(), 55.0)

    def test_apply_discount_zero(self):
        result = self.calculator.apply_discount(100.0, 0.0)
        self.assertAlmostEqual(result, 100.0)

    def test_apply_discount_standard(self):
        result = self.calculator.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_full(self):
        result = self.calculator.apply_discount(100.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, -0.1)

    def test_apply_discount_greater_than_one(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, 1.1)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(-50.0, 0.1)

    def test_apply_discount_invalid_type(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calculator.apply_discount(100.0, 'ten_percent')

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calculator.calculate_shipping(99.99)
        self.assertAlmostEqual(shipping, 10.0)

    def test_calculate_shipping_exact_threshold(self):
        shipping = self.calculator.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_above_threshold(self):
        shipping = self.calculator.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calculator.calculate_shipping('one_hundred')

    def test_calculate_tax_standard(self):
        tax = self.calculator.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_zero(self):
        tax = self.calculator.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_tax(-100.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calculator.calculate_tax('invalid')

    def test_calculate_total_without_discount_with_free_shipping(self):
        self.calculator.add_item('Headphones', 100.0, 1)
        subtotal = 100.0
        shipping = 0.0
        tax = 100.0 * 0.23
        expected_total = subtotal + shipping + tax
        self.assertAlmostEqual(self.calculator.calculate_total(), expected_total, delta=0.01)

    def test_calculate_total_invalid_discount_raises(self):
        self.calculator.add_item('Book', 50.0, 1)
        with self.assertRaises(ValueError):
            self.calculator.calculate_total(discount=-0.1)

    def test_calculate_total_discount_exceeding_one_raises(self):
        self.calculator.add_item('Book', 50.0, 1)
        with self.assertRaises(ValueError):
            self.calculator.calculate_total(discount=1.5)