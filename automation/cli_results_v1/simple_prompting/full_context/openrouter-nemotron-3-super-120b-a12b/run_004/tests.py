import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_valid(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_tax_rate_value_error_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_value_error_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_free_shipping_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='50')

    def test_init_free_shipping_threshold_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='5')

    def test_init_shipping_cost_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_typical(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['quantity'], 2)

    def test_add_item_merge_same_name_price(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Apple', 1.0, 3)
        self.assertEqual(self.calc.items[0]['quantity'], 4)

    def test_add_item_empty_name_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0)

    def test_add_item_price_zero_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 0.0)

    def test_add_item_price_negative_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', -1.0)

    def test_add_item_quantity_less_than_one_error(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.0, 0)

    def test_add_item_name_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    def test_add_item_price_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', '1.0')

    def test_add_item_quantity_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.0, 2.5)

    def test_add_item_same_name_different_price_error(self):
        self.calc.add_item('Apple', 1.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.0)

    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_non_existing_error(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Apple')

    def test_remove_item_name_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_typical(self):
        self.calc.add_item('Apple', 2.0, 3)
        self.calc.add_item('Banana', 1.0, 2)
        self.assertEqual(self.calc.get_subtotal(), 8.0)

    def test_get_subtotal_single_item(self):
        self.calc.add_item('Apple', 5.0)
        self.assertEqual(self.calc.get_subtotal(), 5.0)

    def test_get_subtotal_empty_order_error(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_typical(self):
        result = self.calc.apply_discount(100.0, 0.2)
        self.assertEqual(result, 80.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(50.0, 0.0)
        self.assertEqual(result, 50.0)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(30.0, 1.0)
        self.assertEqual(result, 0.0)

    def test_apply_discount_discount_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, '0.2')

    def test_apply_discount_subtotal_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100.0', 0.1)

    def test_apply_discount_discount_out_of_range_low(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_out_of_range_high(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.1)

    def test_apply_discount_negative_subtotal_error(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.1)

    def test_calculate_shipping_free(self):
        self.calc.free_shipping_threshold = 50.0
        self.calc.shipping_cost = 10.0
        self.assertEqual(self.calc.calculate_shipping(50.0), 0.0)
        self.assertEqual(self.calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_charged(self):
        self.calc.free_shipping_threshold = 50.0
        self.calc.shipping_cost = 10.0
        self.assertEqual(self.calc.calculate_shipping(40.0), 10.0)
        self.assertEqual(self.calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50')

    def test_calculate_tax_typical(self):
        self.calc.tax_rate = 0.23
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_error(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_typical(self):
        self.calc.add_item('Item', 20.0, 2)
        self.calc.tax_rate = 0.1
        self.calc.free_shipping_threshold = 50.0
        self.calc.shipping_cost = 5.0
        total = self.calc.calculate_total(discount=0.1)
        self.assertAlmostEqual(total, 45.1)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item('Item', 60.0, 1)
        self.calc.tax_rate = 0.0
        self.calc.free_shipping_threshold = 50.0
        self.calc.shipping_cost = 10.0
        total = self.calc.calculate_total(discount=0.0)
        self.assertEqual(total, 60.0)

    def test_calculate_total_empty_order_error(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_discount_type_error(self):
        self.calc.add_item('Item', 10.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.1')

    def test_calculate_total_discount_out_of_range_low(self):
        self.calc.add_item('Item', 10.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)

    def test_calculate_total_discount_out_of_range_high(self):
        self.calc.add_item('Item', 10.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.1)

    def test_total_items_typical(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order(self):
        self.calc.add_item('Item', 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items(self):
        self.calc.add_item('Apple', 1.0)
        self.calc.add_item('Banana', 2.0)
        self.calc.add_item('Apple', 1.0, 2)
        names = self.calc.list_items()
        self.assertEqual(set(names), {'Apple', 'Banana'})
        self.assertEqual(len(names), 2)

    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item('Item', 1.0)
        self.assertFalse(self.calc.is_empty())