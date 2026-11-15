import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)

    def test_init_custom(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(oc.tax_rate, 0.1)
        self.assertEqual(oc.free_shipping_threshold, 50.0)
        self.assertEqual(oc.shipping_cost, 5.0)

    def test_init_zero(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0.0)
        self.assertEqual(oc.shipping_cost, 0.0)

    def test_init_negative_tax(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_negative_free_shipping(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='a')

    def test_add_item_single(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.5, 2)
        self.assertEqual(oc.get_subtotal(), 3.0)
        self.assertEqual(oc.total_items(), 2)

    def test_add_item_duplicate(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.5, 2)
        oc.add_item('apple', 1.5, 3)
        self.assertEqual(oc.total_items(), 5)
        self.assertEqual(oc.get_subtotal(), 7.5)

    def test_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('banana', 0.8)
        self.assertEqual(oc.total_items(), 1)
        self.assertEqual(oc.get_subtotal(), 0.8)

    def test_add_item_negative_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('pear', -1.0, 1)

    def test_add_item_negative_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('pear', 1.0, -2)

    def test_add_item_nonint_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('pear', 1.0, 1.5)

    def test_add_item_nonstring_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_remove_item_nonstring(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(None)

    def test_get_subtotal_with_items(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.5, 2)
        oc.add_item('banana', 0.8, 3)
        self.assertEqual(oc.get_subtotal(), 1.5 * 2 + 0.8 * 3)

    def test_get_subtotal_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.5, 2)
        oc.add_item('banana', 0.8, 3)
        oc.remove_item('apple')
        self.assertEqual(oc.get_subtotal(), 0.8 * 3)

    def test_apply_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(20.0, -5.0)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(80.0), 10.0)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_zero_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(oc.calculate_shipping(0.0), 0.0)

    def test_calculate_tax_normal(self):
        oc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(oc.calculate_tax(100.0), 23.0, places=7)

    def test_calculate_tax_zero_amount(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-10.0)

    def test_calculate_total_no_discount_above(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 120)
        self.assertAlmostEqual(oc.calculate_total(), 120.0 + 120.0 * 0.23, places=7)

    def test_calculate_total_negative_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-5.0)

    def test_calculate_total_zero_tax_rate(self):
        oc = OrderCalculator(tax_rate=0.0)
        oc.add_item('apple', 1.0, 80)
        self.assertAlmostEqual(oc.calculate_total(), 80.0 + 10.0, places=7)

    def test_calculate_total_zero_shipping_cost(self):
        oc = OrderCalculator(shipping_cost=0.0)
        oc.add_item('apple', 1.0, 80)
        self.assertAlmostEqual(oc.calculate_total(), 80.0 + 80.0 * 0.23, places=7)

    def test_calculate_total_zero_free_shipping_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=0.0)
        oc.add_item('apple', 1.0, 80)
        self.assertAlmostEqual(oc.calculate_total(), 80.0 + 80.0 * 0.23, places=7)

    def test_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_with_items(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 3)
        oc.add_item('banana', 0.5, 2)
        self.assertEqual(oc.total_items(), 5)

    def test_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 3)
        oc.remove_item('apple')
        self.assertEqual(oc.total_items(), 0)

    def test_clear_order_already_empty(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_list_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_list_items_no_duplicate(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 1)
        oc.add_item('apple', 1.0, 2)
        self.assertEqual(oc.list_items(), ['apple'])

    def test_is_empty_new_order(self):
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

    def test_shipping_exact_threshold(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 100)
        self.assertEqual(oc.calculate_shipping(100.0), 0.0)

    def test_calculate_total_negative_discount_propagation(self):
        oc = OrderCalculator()
        oc.add_item('apple', 1.0, 10)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-5.0)

    def test_calculate_tax_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax('100')

    def test_add_item_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(['apple'], 1.0, 1)

    def test_calculate_total_zero_shipping_and_tax(self):
        oc = OrderCalculator(tax_rate=0.0, shipping_cost=0.0, free_shipping_threshold=100.0)
        oc.add_item('apple', 1.0, 10)
        self.assertAlmostEqual(oc.calculate_total(), 10.0, places=7)

    def test_calculate_total_zero_all(self):
        oc = OrderCalculator(tax_rate=0.0, shipping_cost=0.0, free_shipping_threshold=0.0)
        oc.add_item('apple', 1.0, 10)
        self.assertAlmostEqual(oc.calculate_total(), 10.0, places=7)
if __name__ == '__main__':
    unittest.main()