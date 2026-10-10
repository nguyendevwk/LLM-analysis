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
        self.assertTrue(calc.is_empty())

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_invalid_tax_rate_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_invalid_threshold_or_shipping_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_invalid_types(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_default_quantity(self):
        self.calculator.add_item('Apple', 2.5)
        self.assertEqual(self.calculator.total_items(), 1)
        self.assertFalse(self.calculator.is_empty())
        self.assertEqual(self.calculator.items[0], {'name': 'Apple', 'price': 2.5, 'quantity': 1})

    def test_add_item_custom_quantity(self):
        self.calculator.add_item('Banana', 1.2, 5)
        self.assertEqual(self.calculator.total_items(), 5)

    def test_add_item_merging_existing(self):
        self.calculator.add_item('Milk', 3.0, 2)
        self.calculator.add_item('Milk', 3.0, 3)
        self.assertEqual(self.calculator.total_items(), 5)
        self.assertEqual(len(self.calculator.items), 1)

    def test_add_item_conflicting_price_raises_error(self):
        self.calculator.add_item('Bread', 2.0, 1)
        with self.assertRaises(ValueError):
            self.calculator.add_item('Bread', 2.5, 1)

    def test_add_item_invalid_name(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('', 10.0)

    def test_add_item_invalid_price(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Item', 0.0)
        with self.assertRaises(ValueError):
            self.calculator.add_item('Item', -5.0)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.calculator.add_item('Item', 10.0, 0)
        with self.assertRaises(ValueError):
            self.calculator.add_item('Item', 10.0, -2)

    def test_add_item_invalid_types(self):
        with self.assertRaises(TypeError):
            self.calculator.add_item(123, 10.0)
        with self.assertRaises(TypeError):
            self.calculator.add_item('Item', '10.0')
        with self.assertRaises(TypeError):
            self.calculator.add_item('Item', 10.0, 2.5)

    def test_remove_item_success(self):
        self.calculator.add_item('Apple', 2.0)
        self.calculator.remove_item('Apple')
        self.assertTrue(self.calculator.is_empty())

    def test_remove_item_non_existent_raises_error(self):
        with self.assertRaises(ValueError):
            self.calculator.remove_item('GhostItem')

    def test_remove_item_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calculator.remove_item(123)

    def test_get_subtotal_success(self):
        self.calculator.add_item('Apple', 2.0, 3)
        self.calculator.add_item('Banana', 1.5, 2)
        self.assertEqual(self.calculator.get_subtotal(), 9.0)

    def test_get_subtotal_empty_order_raises_error(self):
        with self.assertRaises(ValueError):
            self.calculator.get_subtotal()

    def test_apply_discount_success(self):
        discounted = self.calculator.apply_discount(100.0, 0.2)
        self.assertEqual(discounted, 80.0)

    def test_apply_discount_invalid_range(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, 1.1)
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(100.0, -0.1)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calculator.apply_discount(-10.0, 0.1)

    def test_apply_discount_invalid_types(self):
        with self.assertRaises(TypeError):
            self.calculator.apply_discount('100', 0.2)
        with self.assertRaises(TypeError):
            self.calculator.apply_discount(100.0, '0.2')

    def test_calculate_shipping_below_threshold(self):
        shipping = self.calculator.calculate_shipping(50.0)
        self.assertEqual(shipping, 10.0)

    def test_calculate_shipping_meets_or_exceeds_threshold(self):
        shipping = self.calculator.calculate_shipping(100.0)
        self.assertEqual(shipping, 0.0)
        shipping_high = self.calculator.calculate_shipping(150.0)
        self.assertEqual(shipping_high, 0.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_shipping('50.0')

    def test_calculate_tax_success(self):
        tax = self.calculator.calculate_tax(100.0)
        self.assertEqual(tax, 23.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_tax(-10.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calculator.calculate_tax('100.0')

    def test_calculate_total_with_shipping(self):
        self.calculator.add_item('Item1', 50.0, 1)
        total = self.calculator.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 73.8)

    def test_calculate_total_free_shipping_and_discount(self):
        self.calculator.add_item('Item1', 150.0, 1)
        total = self.calculator.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 147.6)

    def test_calculate_total_invalid_discount_type(self):
        self.calculator.add_item('Item1', 50.0)
        with self.assertRaises(TypeError):
            self.calculator.calculate_total(discount='0.1')

    def test_total_items(self):
        self.calculator.add_item('A', 10.0, 2)
        self.calculator.add_item('B', 5.0, 3)
        self.assertEqual(self.calculator.total_items(), 5)

    def test_clear_order(self):
        self.calculator.add_item('A', 10.0, 2)
        self.calculator.clear_order()
        self.assertTrue(self.calculator.is_empty())
        self.assertEqual(self.calculator.total_items(), 0)

    def test_list_items(self):
        self.calculator.add_item('Apple', 1.0, 2)
        self.calculator.add_item('Apple', 1.0, 1)
        self.calculator.add_item('Banana', 2.0, 1)
        items_list = self.calculator.list_items()
        self.assertCountEqual(items_list, ['Apple', 'Banana'])
        self.assertEqual(len(items_list), 2)

    def test_is_empty(self):
        self.assertTrue(self.calculator.is_empty())
        self.calculator.add_item('Apple', 1.0)
        self.assertFalse(self.calculator.is_empty())