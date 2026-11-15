import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_out_of_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_type_errors(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_typical(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0)

    def test_add_item_increments_quantity(self):
        self.calc.add_item('Book', 10.0)
        self.calc.add_item('Book', 10.0, 3)
        self.assertEqual(self.calc.total_items(), 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 40.0)

    def test_add_item_same_name_different_price_raises(self):
        self.calc.add_item('Pen', 2.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Pen', 2.5)

    def test_add_item_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 5.0)

    def test_add_item_non_string_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 5.0)

    def test_add_item_price_non_positive_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', 0.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', -1.0)

    def test_add_item_price_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Item', '5.0')

    def test_add_item_quantity_less_than_one_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', 5.0, 0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', 5.0, -1)

    def test_add_item_quantity_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Item', 5.0, '2')

    def test_remove_item_existing(self):
        self.calc.add_item('Tool', 7.5, 2)
        self.calc.remove_item('Tool')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_not_existing_raises(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_non_string_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(42)

    def test_get_subtotal_typical(self):
        self.calc.add_item('A', 2.0, 3)
        self.calc.add_item('B', 5.0, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 11.0)

    def test_get_subtotal_empty_order_raises(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_typical(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.2), 80.0)
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 0.0), 50.0)
        self.assertAlmostEqual(self.calc.apply_discount(30.0, 1.0), 0.0)

    def test_apply_discount_invalid_range(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, 1.1)

    def test_apply_discount_negative_subtotal_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-5.0, 0.1)

    def test_apply_discount_type_errors(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, '0.1')

    def test_calculate_shipping_free_when_above_threshold(self):
        self.calc.free_shipping_threshold = 50.0
        self.calc.shipping_cost = 5.0
        self.assertEqual(self.calc.calculate_shipping(50.0), 0.0)
        self.assertEqual(self.calc.calculate_shipping(75.0), 0.0)

    def test_calculate_shipping_charged_when_below_threshold(self):
        self.calc.free_shipping_threshold = 50.0
        self.calc.shipping_cost = 5.0
        self.assertEqual(self.calc.calculate_shipping(30.0), 5.0)
        self.assertEqual(self.calc.calculate_shipping(0.0), 5.0)

    def test_calculate_shipping_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('10')

    def test_calculate_tax_typical(self):
        self.calc.tax_rate = 0.1
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 10.0)
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('10')

    def test_calculate_total_typical(self):
        self.calc.add_item('Item1', 20.0, 2)
        self.calc.add_item('Item2', 30.0, 1)
        total = self.calc.calculate_total(discount=0.1)
        self.assertAlmostEqual(total, 89.79)

    def test_calculate_total_no_discount_free_shipping(self):
        self.calc.free_shipping_threshold = 50.0
        self.calc.shipping_cost = 5.0
        self.calc.add_item('Cheap', 30.0, 1)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 43.05)

    def test_calculate_total_free_shipping(self):
        self.calc.free_shipping_threshold = 50.0
        self.calc.shipping_cost = 5.0
        self.calc.add_item('Expensive', 60.0, 1)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 73.8)

    def test_calculate_total_empty_order_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_invalid_discount_raises(self):
        self.calc.add_item('Item', 10.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.1)

    def test_calculate_total_type_error_discount(self):
        self.calc.add_item('Item', 10.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_total_items_typical(self):
        self.calc.add_item('A', 1.0, 3)
        self.calc.add_item('B', 2.0, 4)
        self.assertEqual(self.calc.total_items(), 7)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order(self):
        self.calc.add_item('X', 5.0, 2)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_list_items(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Banana', 2.0)
        self.calc.add_item('Apple', 1.0, 2)
        items = self.calc.list_items()
        self.assertEqual(sorted(items), ['Apple', 'Banana'])

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('Item', 1.0)
        self.assertFalse(self.calc.is_empty())
        self.calc.remove_item('Item')
        self.assertTrue(self.calc.is_empty())