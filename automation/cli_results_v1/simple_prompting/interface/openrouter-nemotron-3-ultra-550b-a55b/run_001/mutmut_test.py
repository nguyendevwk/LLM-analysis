import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = OrderCalculator()

    def test_init_default_parameters(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom_parameters(self):
        calc = OrderCalculator(tax_rate=0.2, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.2)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_add_item_valid(self):
        self.calculator.add_item('Apple', 1.5, 2)
        self.assertEqual(self.calculator.get_subtotal(), 3.0)
        self.assertEqual(self.calculator.total_items(), 2)

    def test_add_item_default_quantity(self):
        self.calculator.add_item('Banana', 2.0)
        self.assertEqual(self.calculator.get_subtotal(), 2.0)
        self.assertEqual(self.calculator.total_items(), 1)

    def test_add_item_invalid_price_negative(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Orange', -1.0, 1)

    def test_add_item_invalid_price_zero(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Orange', 0.0, 1)

    def test_add_item_invalid_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Orange', 1.0, -1)

    def test_add_item_invalid_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Orange', 1.0, 0)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item(123, 1.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('Apple', '1.5', 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item('Apple', 1.5, '2')

    def test_remove_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calculator.remove_item(123)

    def test_get_subtotal_multiple_items(self):
        self.calculator.add_item('Apple', 1.5, 2)
        self.calculator.add_item('Banana', 2.0, 3)
        self.assertEqual(self.calculator.get_subtotal(), 9.0)

    def test_apply_discount_valid(self):
        self.assertEqual(self.calculator.apply_discount(100.0, 0.1), 90.0)
        self.assertEqual(self.calculator.apply_discount(100.0, 0.0), 100.0)
        self.assertEqual(self.calculator.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_invalid_negative(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, -0.1)

    def test_apply_discount_invalid_over_one(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, 1.1)

    def test_apply_discount_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount('100.0', 0.1)
        with self.assertRaises(TypeError):
            self.calculator.apply_discount(100.0, '0.1')

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calculator.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calculator.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertEqual(self.calculator.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_shipping('50.0')

    def test_calculate_tax_valid(self):
        self.assertAlmostEqual(self.calculator.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calculator.calculate_tax(0.0), 0.0)

    def test_calculate_tax_invalid_negative(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_tax(-10.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_tax('100.0')

    def test_calculate_total_no_discount(self):
        self.calculator.add_item('Apple', 10.0, 5)
        total = self.calculator.calculate_total()
        expected_subtotal = 50.0
        expected_shipping = 10.0
        expected_tax = (expected_subtotal + expected_shipping) * 0.23
        expected_total = expected_subtotal + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_with_discount(self):
        self.calculator.add_item('Apple', 10.0, 5)
        total = self.calculator.calculate_total(discount=0.1)
        expected_subtotal = 50.0
        expected_discounted = 45.0
        expected_shipping = 10.0
        expected_tax = (expected_discounted + expected_shipping) * 0.23
        expected_total = expected_discounted + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_free_shipping(self):
        self.calculator.add_item('Apple', 50.0, 3)
        total = self.calculator.calculate_total()
        expected_subtotal = 150.0
        expected_shipping = 0.0
        expected_tax = (expected_subtotal + expected_shipping) * 0.23
        expected_total = expected_subtotal + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_invalid_discount(self):
        self.calculator.add_item('Apple', 10.0, 1)
        with self.assertRaises(ValueError):
            self.calculator.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calculator.calculate_total(discount=1.1)

    def test_total_items_empty(self):
        self.assertEqual(self.calculator.total_items(), 0)

    def test_total_items_multiple(self):
        self.calculator.add_item('Apple', 1.5, 2)
        self.calculator.add_item('Banana', 2.0, 3)
        self.assertEqual(self.calculator.total_items(), 5)

    def test_list_items_empty(self):
        self.assertEqual(self.calculator.list_items(), [])

    def test_list_items_multiple(self):
        self.calculator.add_item('Apple', 1.5, 2)
        self.calculator.add_item('Banana', 2.0, 1)
        items = self.calculator.list_items()
        self.assertIn('Apple', items)
        self.assertIn('Banana', items)
        self.assertEqual(len(items), 2)

    def test_is_empty_true(self):
        self.assertTrue(self.calculator.is_empty())

    def test_is_empty_false(self):
        self.calculator.add_item('Apple', 1.5, 1)
        self.assertFalse(self.calculator.is_empty())