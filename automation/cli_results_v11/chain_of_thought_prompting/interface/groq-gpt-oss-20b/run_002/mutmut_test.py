import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default_parameters(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)

    def test_init_custom_positive_values(self):
        oc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(oc.tax_rate, 0.15)
        self.assertEqual(oc.free_shipping_threshold, 50.0)
        self.assertEqual(oc.shipping_cost, 5.0)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_zero_tax_rate(self):
        oc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(oc.tax_rate, 0.0)

    def test_init_zero_free_shipping_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(oc.free_shipping_threshold, 0.0)

    def test_init_zero_shipping_cost(self):
        oc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(oc.shipping_cost, 0.0)

    def test_init_non_numeric_arguments(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='a')
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='b')
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='c')

    def test_add_item_normal_addition(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.5, 2)
        self.assertEqual(oc.total_items(), 2)
        self.assertListEqual(oc.list_items(), ['apple'])

    def test_add_item_same_name_again(self):
        oc = OrderCalculator()
        oc.add_item('banana', 0.5, 3)
        oc.add_item('banana', 0.5, 2)
        self.assertEqual(oc.total_items(), 5)
        self.assertListEqual(oc.list_items(), ['banana'])

    def test_add_item_zero_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('orange', 1.0, 0)

    def test_add_item_negative_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('orange', 1.0, -1)

    def test_add_item_negative_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('negative', -1.0, 1)

    def test_add_item_empty_string_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_special_character_name(self):
        oc = OrderCalculator()
        oc.add_item('café', 2.0, 1)
        self.assertListEqual(oc.list_items(), ['café'])

    def test_add_item_very_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('bulk', 0.1, 10 ** 6)
        self.assertEqual(oc.total_items(), 10 ** 6)
        self.assertAlmostEqual(oc.get_subtotal(), 0.1 * 10 ** 6)

    def test_add_item_very_large_price(self):
        oc = OrderCalculator()
        oc.add_item('expensive', 10 ** 6, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 10 ** 6)

    def test_add_item_non_int_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('item', 1.0, 1.5)

    def test_add_item_non_float_price(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('item', 'price', 1)

    def test_add_item_non_string_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_remove_item_existing_item(self):
        oc = OrderCalculator()
        oc.add_item('pear', 1.0, 1)
        oc.remove_item('pear')
        self.assertTrue(oc.is_empty())

    def test_remove_item_last_item(self):
        oc = OrderCalculator()
        oc.add_item('melon', 1.0, 1)
        oc.remove_item('melon')
        self.assertTrue(oc.is_empty())

    def test_get_subtotal_one_item(self):
        oc = OrderCalculator()
        oc.add_item('strawberry', 2.0, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 6.0)

    def test_get_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('item1', 1.0, 2)
        oc.add_item('item2', 2.0, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 1.0 * 2 + 2.0 * 3)

    def test_get_subtotal_floating_point_precision(self):
        oc = OrderCalculator()
        oc.add_item('precise', 0.1, 3)
        oc.add_item('precise2', 0.2, 4)
        self.assertAlmostEqual(oc.get_subtotal(), 0.1 * 3 + 0.2 * 4, places=7)

    def test_apply_discount_discount_greater_than_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(30.0, 40.0)

    def test_apply_discount_negative_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(30.0, -5.0)

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 5.0)

    def test_calculate_shipping_subtotal_below_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertAlmostEqual(oc.calculate_shipping(30.0), 10.0)

    def test_calculate_shipping_subtotal_equal_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertAlmostEqual(oc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_subtotal_above_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertAlmostEqual(oc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_negative_discounted_subtotal(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertAlmostEqual(oc.calculate_shipping(-5.0), 10.0)

    def test_calculate_tax_positive_amount(self):
        oc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(oc.calculate_tax(100.0), 20.0)

    def test_calculate_tax_zero_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-10.0)

    def test_calculate_tax_tax_rate_zero(self):
        oc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(oc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_tax_rate_one(self):
        oc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(oc.calculate_tax(100.0), 100.0)

    def test_calculate_total_no_items_discount_positive(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=10.0)

    def test_calculate_total_items_discount_zero_subtotal_below_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0, tax_rate=0.1)
        oc.add_item('item', 20.0, 1)
        subtotal = 20.0
        shipping = 10.0
        tax = (subtotal + shipping) * 0.1
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(oc.calculate_total(), expected)

    def test_calculate_total_items_discount_zero_subtotal_above_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0, tax_rate=0.1)
        oc.add_item('item', 60.0, 1)
        subtotal = 60.0
        tax = subtotal * 0.1
        expected = subtotal + tax
        self.assertAlmostEqual(oc.calculate_total(), expected)

    def test_calculate_total_discount_greater_than_subtotal(self):
        oc = OrderCalculator()
        oc.add_item('item', 20.0, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=25.0)

    def test_calculate_total_negative_discount(self):
        oc = OrderCalculator()
        oc.add_item('item', 20.0, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-5.0)

    def test_calculate_total_custom_tax_rate(self):
        oc = OrderCalculator(tax_rate=0.15)
        oc.add_item('item', 100.0, 1)
        subtotal = 100.0
        tax = subtotal * 0.15
        expected = subtotal + tax
        self.assertAlmostEqual(oc.calculate_total(), expected)

    def test_calculate_total_custom_free_shipping_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=200.0, shipping_cost=10.0, tax_rate=0.1)
        oc.add_item('item', 150.0, 1)
        subtotal = 150.0
        shipping = 10.0
        tax = (subtotal + shipping) * 0.1
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(oc.calculate_total(), expected)

    def test_calculate_total_custom_shipping_cost(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=20.0, tax_rate=0.1)
        oc.add_item('item', 30.0, 1)
        subtotal = 30.0
        shipping = 20.0
        tax = (subtotal + shipping) * 0.1
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(oc.calculate_total(), expected)

    def test_total_items_no_items(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_one_item(self):
        oc = OrderCalculator()
        oc.add_item('item', 1.0, 3)
        self.assertEqual(oc.total_items(), 3)

    def test_total_items_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('a', 1.0, 2)
        oc.add_item('b', 1.0, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('a', 1.0, 2)
        oc.add_item('b', 1.0, 3)
        oc.remove_item('a')
        self.assertEqual(oc.total_items(), 3)

    def test_total_items_after_clearing(self):
        oc = OrderCalculator()
        oc.add_item('a', 1.0, 2)
        oc.clear_order()
        self.assertEqual(oc.total_items(), 0)

    def test_clear_order_order_has_items(self):
        oc = OrderCalculator()
        oc.add_item('a', 1.0, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_clear_order_order_already_empty(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_list_items_no_items(self):
        oc = OrderCalculator()
        self.assertListEqual(oc.list_items(), [])

    def test_list_items_one_item(self):
        oc = OrderCalculator()
        oc.add_item('a', 1.0, 1)
        self.assertListEqual(oc.list_items(), ['a'])

    def test_list_items_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('a', 1.0, 1)
        oc.add_item('b', 1.0, 1)
        self.assertListEqual(oc.list_items(), ['a', 'b'])

    def test_list_items_duplicate_names(self):
        oc = OrderCalculator()
        oc.add_item('dup', 1.0, 1)
        oc.add_item('dup', 1.0, 2)
        self.assertListEqual(oc.list_items(), ['dup'])

    def test_list_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('a', 1.0, 1)
        oc.remove_item('a')
        self.assertListEqual(oc.list_items(), [])

    def test_list_items_after_clearing(self):
        oc = OrderCalculator()
        oc.add_item('a', 1.0, 1)
        oc.clear_order()
        self.assertListEqual(oc.list_items(), [])

    def test_is_empty_no_items(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_adding_items(self):
        oc = OrderCalculator()
        oc.add_item('a', 1.0, 1)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_removing_all_items(self):
        oc = OrderCalculator()
        oc.add_item('a', 1.0, 1)
        oc.remove_item('a')
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_clearing(self):
        oc = OrderCalculator()
        oc.add_item('a', 1.0, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_remove_item_non_string_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_add_item_non_string_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_non_numeric_price(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('item', 'price', 1)

    def test_add_item_non_numeric_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('item', 1.0, 'qty')

    def test_calculate_total_floating_point_precision(self):
        oc = OrderCalculator()
        oc.add_item('item1', 0.1, 3)
        oc.add_item('item2', 0.2, 4)
        subtotal = 0.1 * 3 + 0.2 * 4
        shipping = 10.0 if subtotal < 100.0 else 0.0
        tax = (subtotal + shipping) * 0.23
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(oc.calculate_total(), expected, places=7)

    def test_calculate_total_extreme_values(self):
        oc = OrderCalculator()
        oc.add_item('big', 1000000000000.0, 1)
        subtotal = 1000000000000.0
        shipping = 10.0 if subtotal < 100.0 else 0.0
        tax = (subtotal + shipping) * 0.23
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(oc.calculate_total(), expected)

    def test_calculate_total_zero_tax_rate(self):
        oc = OrderCalculator(tax_rate=0.0)
        oc.add_item('item', 50.0, 1)
        subtotal = 50.0
        shipping = 10.0 if subtotal < 100.0 else 0.0
        expected = subtotal + shipping
        self.assertAlmostEqual(oc.calculate_total(), expected)

    def test_calculate_total_zero_shipping_cost(self):
        oc = OrderCalculator(shipping_cost=0.0, free_shipping_threshold=100.0, tax_rate=0.23)
        oc.add_item('item', 50.0, 1)
        subtotal = 50.0
        shipping = 0.0
        tax = (subtotal + shipping) * 0.23
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(oc.calculate_total(), expected)

    def test_calculate_total_zero_free_shipping_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0, tax_rate=0.23)
        oc.add_item('item', 50.0, 1)
        subtotal = 50.0
        shipping = 0.0
        tax = (subtotal + shipping) * 0.23
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(oc.calculate_total(), expected)

    def test_calculate_total_negative_values_in_all_parameters(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1, free_shipping_threshold=-10.0, shipping_cost=-5.0)

    def test_calculate_total_discount_just_above_subtotal(self):
        oc = OrderCalculator()
        oc.add_item('item', 20.0, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=20.1)

    def test_calculate_total_shipping_cost_positive_threshold_high(self):
        oc = OrderCalculator(free_shipping_threshold=1000000000.0, shipping_cost=10.0, tax_rate=0.23)
        oc.add_item('item', 50.0, 1)
        subtotal = 50.0
        shipping = 10.0
        tax = (subtotal + shipping) * 0.23
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(oc.calculate_total(), expected)

    def test_calculate_total_shipping_cost_zero_and_threshold_low(self):
        oc = OrderCalculator(free_shipping_threshold=1.0, shipping_cost=0.0, tax_rate=0.23)
        oc.add_item('item', 50.0, 1)
        subtotal = 50.0
        shipping = 0.0
        tax = (subtotal + shipping) * 0.23
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(oc.calculate_total(), expected)
if __name__ == '__main__':
    unittest.main()