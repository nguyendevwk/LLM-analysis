import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_zero_boundary(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_one_boundary(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_free_shipping_threshold_zero_boundary(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    def test_init_shipping_cost_zero_boundary(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate=None)

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_init_tax_rate_integer(self):
        calc = OrderCalculator(tax_rate=0)
        self.assertEqual(calc.tax_rate, 0.0)
        calc = OrderCalculator(tax_rate=1)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_free_shipping_threshold_integer(self):
        calc = OrderCalculator(free_shipping_threshold=0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        calc = OrderCalculator(free_shipping_threshold=100)
        self.assertEqual(calc.free_shipping_threshold, 100.0)

    def test_init_shipping_cost_integer(self):
        calc = OrderCalculator(shipping_cost=0)
        self.assertEqual(calc.shipping_cost, 0.0)
        calc = OrderCalculator(shipping_cost=10)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_add_item_new(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertIn('Apple', self.calc.list_items())

    def test_add_item_same_name_price(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Apple', 1.5, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_same_name_diff_price(self):
        self.calc.add_item('Apple', 1.5, 2)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.0, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_price_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 0, 1)

    def test_add_item_price_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', -1.0, 1)

    def test_add_item_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.0, 0)

    def test_add_item_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.0, -2)

    def test_add_item_name_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item(None, 1.0, 1)

    def test_add_item_price_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', '1.0', 1)
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', None, 1)

    def test_add_item_quantity_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.0, 1.5)
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.0, '2')
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.0, None)

    def test_add_item_price_int(self):
        self.calc.add_item('Apple', 2, 1)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_quantity_int(self):
        self.calc.add_item('Apple', 1.0, 5)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_quantity_float_non_integer(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.0, 2.5)

    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Banana')

    def test_remove_item_name_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)
        with self.assertRaises(TypeError):
            self.calc.remove_item(None)

    def test_remove_item_after_cleared(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.remove_item('Apple')

    def test_get_subtotal_with_items(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 2.0, 3)
        expected = 1.5 * 2 + 2.0 * 3
        self.assertAlmostEqual(self.calc.get_subtotal(), expected)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_valid(self):
        result = self.calc.apply_discount(50.0, 0.2)
        self.assertAlmostEqual(result, 40.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(result, 50.0)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(50.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.2)

    def test_apply_discount_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -0.1)

    def test_apply_discount_discount_above_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, 1.1)

    def test_apply_discount_subtotal_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('50', 0.2)

    def test_apply_discount_discount_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(50.0, '0.2')

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(40.0), 10.0)

    def test_calculate_shipping_exact_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50')

    def test_calculate_tax_positive(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_tax_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_typical_flow(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 2.0, 3)
        subtotal = 1.5 * 2 + 2.0 * 3
        discounted = subtotal * 0.8
        shipping = 10.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.2), expected)

    def test_calculate_total_discount_zero_subtotal_below_threshold(self):
        self.calc.add_item('Apple', 1.0, 1)
        subtotal = 1.0
        shipping = 10.0
        tax = (subtotal + shipping) * 0.23
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.0), expected)

    def test_calculate_total_discount_zero_subtotal_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=1.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        subtotal = 2.0
        tax = subtotal * 0.23
        expected = subtotal + tax
        self.assertAlmostEqual(calc.calculate_total(0.0), expected)

    def test_calculate_total_discount_full_subtotal_below_threshold(self):
        self.calc.add_item('Apple', 1.0, 1)
        subtotal = 1.0
        shipping = 10.0
        tax = shipping * 0.23
        expected = shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(1.0), expected)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(0.0)

    def test_calculate_total_discount_invalid_low(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-0.1)

    def test_calculate_total_discount_invalid_high(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.1)

    def test_calculate_total_discount_wrong_type(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.2')

    def test_calculate_total_discount_half_multiple_items(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Banana', 2.0, 3)
        subtotal = 1.5 * 2 + 2.0 * 3
        discounted = subtotal * 0.5
        shipping = 10.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.5), expected)

    def test_calculate_total_discount_half_exact_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=5.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 5)
        subtotal = 5.0
        discounted = subtotal * 0.5
        shipping = 10.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(0.5), expected)

    def test_calculate_total_discount_zero_shipping_zero_tax(self):
        calc = OrderCalculator(tax_rate=0.0, shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 2)
        subtotal = 2.0
        expected = subtotal
        self.assertAlmostEqual(calc.calculate_total(0.0), expected)

    def test_calculate_total_discount_zero_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, tax_rate=0.23, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        subtotal = 2.0
        tax = subtotal * 0.23
        expected = subtotal + tax
        self.assertAlmostEqual(calc.calculate_total(0.0), expected)

    def test_calculate_total_discount_zero_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        subtotal = 2.0
        shipping = 10.0
        expected = subtotal + shipping
        self.assertAlmostEqual(calc.calculate_total(0.0), expected)

    def test_calculate_total_discount_zero_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0, shipping_cost=10.0)
        calc.add_item('Apple', 1.0, 2)
        subtotal = 2.0
        shipping = 10.0
        tax = (subtotal + shipping) * 1.0
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(0.0), expected)

    def test_calculate_total_discount_zero_shipping_zero_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0, shipping_cost=0.0)
        calc.add_item('Apple', 1.0, 2)
        subtotal = 2.0
        expected = subtotal
        self.assertAlmostEqual(calc.calculate_total(0.0), expected)

    def test_total_items_single(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_multiple(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_removal(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_after_clearing(self):
        self.calc.add_item('Apple', 1.0, 3)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_with_items(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_clear_order_already_empty(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items_with_items(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Banana', 2.0, 1)
        self.assertCountEqual(self.calc.list_items(), ['Apple', 'Banana'])

    def test_list_items_duplicates_same_name_price(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Apple', 1.0, 2)
        self.assertCountEqual(self.calc.list_items(), ['Apple'])

    def test_list_items_after_removal(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Banana', 2.0, 1)
        self.calc.remove_item('Apple')
        self.assertCountEqual(self.calc.list_items(), ['Banana'])

    def test_list_items_after_clearing(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_new_instance(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_adding(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_removing_only(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_clearing(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_calculate_total_then_clear_then_total(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.calculate_total(0.0)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.calculate_total(0.0)

    def test_remove_item_updates_total_items(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 2.0, 3)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.total_items(), 3)

    def test_add_same_name_price_increments_total_items(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Apple', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_same_name_diff_price_raises(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.0, 1)

    def test_list_items_after_removal(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Banana', 2.0, 1)
        self.calc.remove_item('Apple')
        self.assertCountEqual(self.calc.list_items(), ['Banana'])

    def test_calculate_total_same_discount_twice(self):
        self.calc.add_item('Apple', 1.0, 1)
        total1 = self.calc.calculate_total(0.0)
        total2 = self.calc.calculate_total(0.0)
        self.assertAlmostEqual(total1, total2)

    def test_clear_order_and_is_empty(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
if __name__ == '__main__':
    unittest.main()