import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_valid_params(self):
        calc = OrderCalculator(0.05, 50.0, 5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(1.1)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator('0.2')
        with self.assertRaises(TypeError):
            OrderCalculator(None)

    def test_init_free_shipping_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1)

    def test_init_free_shipping_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='50')

    def test_init_shipping_cost_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='5')

    def test_add_item_success(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'apple')
        self.assertEqual(calc.items[0]['price'], 1.0)
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_add_item_increments_quantity(self):
        calc = OrderCalculator()
        calc.add_item('book', 10.0)
        calc.add_item('book', 10.0, 3)
        self.assertEqual(calc.items[0]['quantity'], 4)

    def test_add_item_same_name_different_price_raises(self):
        calc = OrderCalculator()
        calc.add_item('pen', 2.0)
        with self.assertRaises(ValueError):
            calc.add_item('pen', 3.0)

    def test_add_item_empty_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 5.0)

    def test_add_item_non_string_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 5.0)

    def test_add_item_price_zero_or_negative_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('item', 0)
        with self.assertRaises(ValueError):
            calc.add_item('item', -1)

    def test_add_item_quantity_less_than_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('item', 5.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item('item', 5.0, -1)

    def test_add_item_non_numeric_price_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('item', '5')
        with self.assertRaises(TypeError):
            calc.add_item('item', None)

    def test_add_item_non_int_quantity_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('item', 5.0, 2.5)
        with self.assertRaises(TypeError):
            calc.add_item('item', 5.0, '2')

    def test_remove_item_success(self):
        calc = OrderCalculator()
        calc.add_item('foo', 1.0)
        calc.remove_item('foo')
        self.assertEqual(calc.items, [])

    def test_remove_item_not_existing_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('bar')

    def test_remove_item_non_string_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_on_items(self):
        calc = OrderCalculator()
        calc.add_item('a', 2.0, 3)
        calc.add_item('b', 5.0, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 11.0)

    def test_get_subtotal_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)
        self.assertAlmostEqual(calc.apply_discount(50.0, 0.0), 50.0)
        self.assertAlmostEqual(calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_out_of_range_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(10.0, -0.1)
        with self.assertRaises(ValueError):
            calc.apply_discount(10.0, 1.1)

    def test_apply_discount_negative_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-5.0, 0.1)

    def test_apply_discount_type_errors(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            calc.apply_discount(100, '0.1')
        with self.assertRaises(TypeError):
            calc.apply_discount(None, 0.1)
        with self.assertRaises(TypeError):
            calc.apply_discount(100, None)

    def test_calculate_shipping_free(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)
        self.assertEqual(calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_charged(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(49.99), 5.0)
        self.assertEqual(calc.calculate_shipping(0.0), 5.0)

    def test_calculate_shipping_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('10')
        with self.assertRaises(TypeError):
            calc.calculate_shipping(None)

    def test_calculate_tax(self):
        calc = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 10.0)
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-1.0)

    def test_calculate_tax_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('5')
        with self.assertRaises(TypeError):
            calc.calculate_tax(None)

    def test_calculate_total_no_discount(self):
        calc = OrderCalculator()
        calc.add_item('book', 20.0, 2)
        self.assertAlmostEqual(calc.calculate_total(), 61.5)

    def test_calculate_total_with_discount(self):
        calc = OrderCalculator()
        calc.add_item('item', 50.0, 2)
        self.assertAlmostEqual(calc.calculate_total(0.1), 123.0)

    def test_calculate_total_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=80.0, shipping_cost=5.0)
        calc.add_item('item', 40.0, 2)
        self.assertAlmostEqual(calc.calculate_total(), 98.4)

    def test_calculate_total_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_invalid_discount_type(self):
        calc = OrderCalculator()
        calc.add_item('a', 10.0)
        with self.assertRaises(TypeError):
            calc.calculate_total('0.1')
        with self.assertRaises(TypeError):
            calc.calculate_total(None)

    def test_calculate_total_discount_out_of_range(self):
        calc = OrderCalculator()
        calc.add_item('a', 10.0)
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.5)

    def test_total_items(self):
        calc = OrderCalculator()
        calc.add_item('a', 1.0, 3)
        calc.add_item('b', 2.0, 4)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order(self):
        calc = OrderCalculator()
        calc.add_item('x', 1.0)
        calc.clear_order()
        self.assertEqual(calc.items, [])
        self.assertTrue(calc.is_empty())

    def test_list_items(self):
        calc = OrderCalculator()
        calc.add_item('apple', 1.0, 2)
        calc.add_item('banana', 2.0, 1)
        calc.add_item('apple', 1.0, 1)
        names = calc.list_items()
        self.assertEqual(set(names), {'apple', 'banana'})
        self.assertEqual(len(names), 2)

    def test_is_empty(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        calc.add_item('a', 1.0)
        self.assertFalse(calc.is_empty())
        calc.remove_item('a')
        self.assertTrue(calc.is_empty())