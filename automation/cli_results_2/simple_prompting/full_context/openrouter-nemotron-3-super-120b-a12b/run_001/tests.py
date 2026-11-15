import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_custom(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_tax_rate_value_error_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_value_error_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_free_shipping_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_free_shipping_threshold_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_shipping_cost_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_new(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'Apple')
        self.assertEqual(calc.items[0]['price'], 1.0)
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_add_item_existing_same_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.items[0]['quantity'], 4)

    def test_add_item_existing_different_price_error(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 2.0)

    def test_add_item_name_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_empty_name_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    def test_add_item_price_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', '1.0')

    def test_add_item_price_non_positive_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', -1.0)

    def test_add_item_quantity_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, 2.5)

    def test_add_item_quantity_less_than_one_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, 0)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0)
        calc.remove_item('Apple')
        self.assertEqual(calc.items, [])

    def test_remove_item_non_existing_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Apple')

    def test_remove_item_name_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_normal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 3.5)

    def test_get_subtotal_empty_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_subtotal_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)

    def test_apply_discount_discount_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100, '0.1')

    def test_apply_discount_discount_out_of_range_low(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100, -0.1)

    def test_apply_discount_discount_out_of_range_high(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100, 1.5)

    def test_apply_discount_negative_subtotal_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10, 0.1)

    def test_calculate_shipping_free(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_charged(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(40.0), 10.0)

    def test_calculate_shipping_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('50')

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_calculate_tax_negative_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-10)

    def test_calculate_total_normal(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Item', 50.0, 2)
        total = calc.calculate_total(discount=0.1)
        self.assertAlmostEqual(total, 90 + 10 + 23)

    def test_calculate_total_free_shipping(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item('Item', 30.0, 2)
        total = calc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 60 + 0 + 6.0)

    def test_calculate_total_empty_order_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_discount_type_error(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0)
        with self.assertRaises(TypeError):
            calc.calculate_total('0.1')

    def test_calculate_total_discount_out_of_range_low(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0)
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)

    def test_calculate_total_discount_out_of_range_high(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.5)

    def test_total_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 2.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0)
        calc.clear_order()
        self.assertEqual(calc.items, [])
        self.assertTrue(calc.is_empty())

    def test_list_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5)
        calc.add_item('Apple', 1.0, 1)
        names = set(calc.list_items())
        self.assertEqual(names, {'Apple', 'Banana'})

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_is_empty_true(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0)
        self.assertFalse(calc.is_empty())