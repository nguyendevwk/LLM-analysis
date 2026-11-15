import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(1), 0.23)
        self.assertEqual(oc.calculate_shipping(100), 0.0)
        self.assertEqual(oc.calculate_shipping(99), 10.0)

    def test_init_custom(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(oc.calculate_tax(1), 0.1)
        self.assertEqual(oc.calculate_shipping(50), 0.0)
        self.assertEqual(oc.calculate_shipping(49), 5.0)

    def test_init_negative_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-100.0)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-10.0)

    def test_init_non_numeric_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.1')

    def test_init_non_numeric_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_non_numeric_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_single_item(self):
        oc = OrderCalculator()
        oc.add_item('apple', 2.5, 3)
        self.assertEqual(oc.get_subtotal(), 7.5)
        self.assertEqual(oc.total_items(), 3)

    def test_add_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('apple', 2.0, 1)
        oc.add_item('banana', 1.5, 2)
        self.assertEqual(oc.get_subtotal(), 5.0)

    def test_add_same_item_increments_quantity(self):
        oc = OrderCalculator()
        oc.add_item('apple', 2.0, 1)
        oc.add_item('apple', 2.0, 2)
        self.assertEqual(oc.get_subtotal(), 6.0)
        self.assertEqual(oc.total_items(), 3)

    def test_add_item_zero_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('apple', 2.0, 0)

    def test_add_item_negative_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('apple', 2.0, -1)

    def test_add_item_negative_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('apple', -2.0, 1)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 2.0, 1)

    def test_add_item_none_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(None, 2.0, 1)

    def test_add_item_non_string_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 2.0, 1)

    def test_add_item_none_price(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('apple', None, 1)

    def test_add_item_non_numeric_price(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('apple', '2.0', 1)

    def test_add_item_none_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('apple', 2.0, None)

    def test_add_item_non_numeric_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('apple', 2.0, 1.5)

    def test_remove_last_item_makes_order_empty(self):
        oc = OrderCalculator()
        oc.add_item('apple', 2.0, 1)
        oc.remove_item('apple')
        self.assertTrue(oc.is_empty())

    def test_remove_item_none_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(None)

    def test_remove_item_non_string_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item('apple', 2.0, 1)
        self.assertEqual(oc.get_subtotal(), 2.0)

    def test_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('apple', 2.0, 1)
        oc.add_item('banana', 3.0, 2)
        self.assertEqual(oc.get_subtotal(), 8.0)

    def test_subtotal_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('apple', 2.0, 1)
        oc.add_item('banana', 3.0, 2)
        oc.remove_item('apple')
        self.assertEqual(oc.get_subtotal(), 6.0)

    def test_apply_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(5.0, -1.0)

    def test_shipping_above_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        result = oc.calculate_shipping(150.0)
        self.assertEqual(result, 0.0)

    def test_shipping_below_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        result = oc.calculate_shipping(50.0)
        self.assertEqual(result, 10.0)

    def test_shipping_exact_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        result = oc.calculate_shipping(100.0)
        self.assertEqual(result, 0.0)

    def test_shipping_negative_subtotal(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        result = oc.calculate_shipping(-10.0)
        self.assertEqual(result, 10.0)

    def test_tax_normal(self):
        oc = OrderCalculator(tax_rate=0.2)
        self.assertEqual(oc.calculate_tax(100.0), 20.0)

    def test_tax_zero_amount(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_tax(0.0), 0.0)

    def test_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5.0)

    def test_total_no_discount(self):
        oc = OrderCalculator()
        oc.add_item('apple', 10.0, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 24.6)

    def test_total_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total(-5.0)

    def test_total_with_free_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        oc.add_item('apple', 30.0, 2)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 73.8)

    def test_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 2)
        oc.add_item('banana', 1.0, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_total_items_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 1)
        oc.clear_order()
        self.assertEqual(oc.total_items(), 0)

    def test_list_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_list_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 1)
        oc.add_item('banana', 1.0, 1)
        self.assertEqual(oc.list_items(), ['apple', 'banana'])

    def test_list_items_unique_names(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 1)
        oc.add_item('apple', 1.0, 2)
        self.assertEqual(oc.list_items(), ['apple'])

    def test_list_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 1)
        oc.add_item('banana', 1.0, 1)
        oc.remove_item('apple')
        self.assertEqual(oc.list_items(), ['banana'])

    def test_list_items_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 1)
        oc.clear_order()
        self.assertEqual(oc.list_items(), [])

    def test_is_empty_initial(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_add(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 1)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_removal_of_last_item(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 1)
        oc.remove_item('apple')
        self.assertTrue(oc.is_empty())
if __name__ == '__main__':
    unittest.main()