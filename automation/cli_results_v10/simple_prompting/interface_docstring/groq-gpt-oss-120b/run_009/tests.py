import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_tax_rate_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_invalid_free_shipping_threshold_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_invalid_shipping_cost_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_basic(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertIn('Apple', self.calc.list_items())

    def test_add_item_merge_same_name_price(self):
        self.calc.add_item('Banana', 0.8, 1)
        self.calc.add_item('Banana', 0.8, 3)
        self.assertEqual(self.calc.total_items(), 4)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item('Orange', 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', 1.2, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Grape', -0.5, 1)

    def test_add_item_zero_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Grape', 0.0, 1)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Kiwi', 2.0, 0)

    def test_add_item_invalid_types(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('Mango', '1.0', 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('Mango', 1.0, '1')

    def test_remove_item_existing(self):
        self.calc.add_item('Peach', 2.5, 2)
        self.calc.remove_item('Peach')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_normal(self):
        self.calc.add_item('ItemA', 10.0, 2)
        self.calc.add_item('ItemB', 5.5, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 25.5)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_normal(self):
        result = self.calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(result, 50.0)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(30.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_invalid_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_invalid_discount_range(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, 1.5)

    def test_apply_discount_invalid_types(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '0.1')

    def test_calculate_shipping_free(self):
        self.calc.free_shipping_threshold = 50.0
        cost = self.calc.calculate_shipping(60.0)
        self.assertAlmostEqual(cost, 0.0)

    def test_calculate_shipping_paid(self):
        self.calc.free_shipping_threshold = 100.0
        cost = self.calc.calculate_shipping(80.0)
        self.assertAlmostEqual(cost, self.calc.shipping_cost)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('80')

    def test_calculate_tax_normal(self):
        tax = self.calc.calculate_tax(200.0)
        self.assertAlmostEqual(tax, 200.0 * self.calc.tax_rate)

    def test_calculate_tax_zero(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax([100])

    def test_calculate_total_no_discount_free_shipping(self):
        self.calc.add_item('A', 60.0, 1)
        self.calc.add_item('B', 50.0, 1)
        total = self.calc.calculate_total()
        expected_subtotal = 110.0
        expected_discounted = expected_subtotal
        expected_shipping = 0.0
        expected_tax = (expected_discounted + expected_shipping) * self.calc.tax_rate
        self.assertAlmostEqual(total, expected_discounted + expected_shipping + expected_tax)

    def test_calculate_total_with_discount_and_shipping(self):
        self.calc.add_item('C', 30.0, 2)
        total = self.calc.calculate_total(discount=0.1)
        expected_discounted = 54.0
        expected_shipping = self.calc.shipping_cost
        expected_tax = (expected_discounted + expected_shipping) * self.calc.tax_rate
        self.assertAlmostEqual(total, expected_discounted + expected_shipping + expected_tax)

    def test_calculate_total_invalid_discount(self):
        self.calc.add_item('D', 20.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.2)

    def test_calculate_total_invalid_discount_type(self):
        self.calc.add_item('E', 10.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_total_items_counts_correctly(self):
        self.calc.add_item('X', 5.0, 3)
        self.calc.add_item('Y', 2.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_removal(self):
        self.calc.add_item('Z', 1.0, 4)
        self.calc.remove_item('Z')
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_resets_state(self):
        self.calc.add_item('Item1', 10.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_list_items_unique_names(self):
        self.calc.add_item('Alpha', 1.0, 1)
        self.calc.add_item('Beta', 2.0, 1)
        self.calc.add_item('Alpha', 1.0, 2)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['Alpha', 'Beta'])

    def test_is_empty_initially(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_adding(self):
        self.calc.add_item('Gamma', 3.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clearing(self):
        self.calc.add_item('Delta', 4.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())