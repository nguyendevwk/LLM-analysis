import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_free_shipping_threshold_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_shipping_cost_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_new(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0)

    def test_add_item_existing_same_price_increments_quantity(self):
        self.calc.add_item('Book', 10.0)
        self.calc.add_item('Book', 10.0, 3)
        self.assertEqual(self.calc.total_items(), 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 40.0)

    def test_add_item_existing_different_price_raises(self):
        self.calc.add_item('Pen', 2.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Pen', 2.5)

    def test_add_item_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 5.0)

    def test_add_item_price_non_positive_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', 0.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', -1.0)

    def test_add_item_quantity_less_than_one_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', 5.0, 0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Item', 5.0, -1)

    def test_add_item_wrong_types_raise(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 5.0)
        with self.assertRaises(TypeError):
            self.calc.add_item('Item', '5.0')
        with self.assertRaises(TypeError):
            self.calc.add_item('Item', 5.0, '2')

    def test_remove_item_existing(self):
        self.calc.add_item('Toy', 7.0, 2)
        self.calc.remove_item('Toy')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_non_existing_raises(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Ghost')

    def test_remove_item_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('A', 2.0, 3)
        self.calc.add_item('B', 5.0, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 11.0)

    def test_get_subtotal_empty_order_raises(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_normal(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.2), 80.0)
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 0.0), 50.0)
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_edge_values(self):
        self.assertAlmostEqual(self.calc.apply_discount(0.0, 0.5), 0.0)
        self.assertAlmostEqual(self.calc.apply_discount(10.0, 0.0), 10.0)
        self.assertAlmostEqual(self.calc.apply_discount(10.0, 1.0), 0.0)

    def test_apply_discount_negative_subtotal_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-1.0, 0.1)

    def test_apply_discount_invalid_discount_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, 1.5)

    def test_apply_discount_wrong_types_raise(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, '0.1')

    def test_calculate_shipping_free_when_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_free_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_charged_when_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_zero_subtotal(self):
        self.assertEqual(self.calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('100')
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping(None)

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(calc.calculate_tax(200.0), 20.0)

    def test_calculate_tax_zero_rate(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_zero_amount(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')
        with self.assertRaises(TypeError):
            self.calc.calculate_tax(None)

    def test_calculate_total_normal(self):
        self.calc.add_item('Item1', 20.0, 2)
        self.calc.add_item('Item2', 30.0, 1)
        total = self.calc.calculate_total(discount=0.1)
        self.assertAlmostEqual(total, 89.79)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item('Expensive', 120.0, 1)
        total = self.calc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 147.6)

    def test_calculate_total_zero_discount(self):
        self.calc.add_item('Cheap', 10.0, 5)
        total = self.calc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 73.8)

    def test_calculate_total_full_discount(self):
        self.calc.add_item('Free', 5.0, 10)
        total = self.calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 12.3)

    def test_calculate_total_empty_order_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_invalid_discount_raises(self):
        self.calc.add_item('Item', 10.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.5)

    def test_calculate_total_wrong_type_raises(self):
        self.calc.add_item('Item', 5.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_total_items(self):
        self.calc.add_item('A', 1.0, 3)
        self.calc.add_item('B', 2.0, 4)
        self.assertEqual(self.calc.total_items(), 7)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order(self):
        self.calc.add_item('X', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Banana', 2.0)
        self.calc.add_item('Apple', 1.0, 2)
        items = self.calc.list_items()
        self.assertEqual(sorted(items), ['Apple', 'Banana'])

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('Any', 1.0)
        self.assertFalse(self.calc.is_empty())
        self.calc.remove_item('Any')
        self.assertTrue(self.calc.is_empty())