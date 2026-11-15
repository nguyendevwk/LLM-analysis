import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_parameters(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_invalid_tax_rate_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_invalid_free_shipping_threshold_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_invalid_shipping_cost_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_add_item_new(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 2)

    def test_add_item_increment_quantity_same_price(self):
        self.calc.add_item('Banana', 0.5, 3)
        self.calc.add_item('Banana', 0.5, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 5)

    def test_add_item_same_name_different_price_raises(self):
        self.calc.add_item('Orange', 0.8)
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', 1.0)

    def test_add_item_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0)

    def test_add_item_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Grapes', -2.0)

    def test_add_item_zero_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Grapes', 0.0)

    def test_add_item_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Peach', 1.0, -1)

    def test_add_item_nonint_quantity_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Peach', 1.0, 1.5)

    def test_add_item_nonstring_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_nonnumber_price_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Pear', '1.0')

    def test_remove_item_existing(self):
        self.calc.add_item('Mango', 2.0)
        self.calc.remove_item('Mango')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent_raises(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_nonstring_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_with_items(self):
        self.calc.add_item('Item1', 10.0, 2)
        self.calc.add_item('Item2', 5.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10.0 * 2 + 5.0 * 3)

    def test_get_subtotal_empty_raises(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_normal(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(30.0, 1.0), 0.0)

    def test_apply_discount_invalid_discount_value(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.5)

    def test_apply_discount_negative_discount_value(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)

    def test_apply_discount_negative_subtotal_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.2)

    def test_apply_discount_nonnumber_subtotal_raises(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.2)

    def test_apply_discount_nonnumber_discount_raises(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '0.2')

    def test_calculate_shipping_free(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_nonfree(self):
        self.assertEqual(self.calc.calculate_shipping(50.0), self.calc.shipping_cost)

    def test_calculate_shipping_nonnumber_input_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50')

    def test_calculate_tax_normal(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200.0), 200.0 * self.calc.tax_rate)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_nonnumber_input_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_no_discount(self):
        self.calc.add_item('A', 20.0, 2)
        expected_subtotal = 40.0
        expected_discounted = expected_subtotal
        expected_shipping = self.calc.calculate_shipping(expected_discounted)
        expected_tax = self.calc.calculate_tax(expected_discounted + expected_shipping)
        expected_total = expected_discounted + expected_shipping + expected_tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected_total)

    def test_calculate_total_with_discount(self):
        self.calc.add_item('B', 50.0, 1)
        discount = 0.1
        expected_subtotal = 50.0
        expected_discounted = expected_subtotal * (1 - discount)
        expected_shipping = self.calc.calculate_shipping(expected_discounted)
        expected_tax = self.calc.calculate_tax(expected_discounted + expected_shipping)
        expected_total = expected_discounted + expected_shipping + expected_tax
        self.assertAlmostEqual(self.calc.calculate_total(discount), expected_total)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item('C', 120.0, 1)
        discount = 0.0
        expected_subtotal = 120.0
        expected_discounted = expected_subtotal
        expected_shipping = self.calc.calculate_shipping(expected_discounted)
        expected_tax = self.calc.calculate_tax(expected_discounted + expected_shipping)
        expected_total = expected_discounted + expected_shipping + expected_tax
        self.assertAlmostEqual(self.calc.calculate_total(discount), expected_total)

    def test_calculate_total_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.2')

    def test_calculate_total_invalid_discount_value(self):
        self.calc.add_item('D', 10.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.5)

    def test_total_items(self):
        self.calc.add_item('E', 5.0, 3)
        self.calc.add_item('F', 2.0, 4)
        self.assertEqual(self.calc.total_items(), 7)

    def test_clear_order(self):
        self.calc.add_item('G', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(len(self.calc.items), 0)

    def test_list_items(self):
        self.calc.add_item('H', 1.0, 1)
        self.calc.add_item('H', 1.0, 2)
        self.calc.add_item('I', 2.0, 1)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['H', 'I'])

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('J', 3.0)
        self.assertFalse(self.calc.is_empty())