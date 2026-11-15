import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default(self):
        self.assertIsInstance(self.calc, OrderCalculator)

    def test_init_invalid_tax_rate(self):
        for bad in (-0.1, 1.1, '0.2', None):
            with self.assertRaises((ValueError, TypeError)):
                OrderCalculator(tax_rate=bad)

    def test_init_invalid_free_shipping_threshold(self):
        for bad in (-10, '100', None):
            with self.assertRaises((ValueError, TypeError)):
                OrderCalculator(free_shipping_threshold=bad)

    def test_init_invalid_shipping_cost(self):
        for bad in (-5, '10', None):
            with self.assertRaises((ValueError, TypeError)):
                OrderCalculator(shipping_cost=bad)

    def test_init_custom_values(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=5)
        self.assertAlmostEqual(calc.calculate_tax(100), 10.0)
        self.assertAlmostEqual(calc.calculate_shipping(60), 0.0)
        self.assertAlmostEqual(calc.calculate_shipping(40), 5.0)

    def test_add_item_success(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Banana', 0.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.5)

    def test_add_item_duplicate_same_price(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Apple', 1.5, 3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.5)

    def test_add_item_duplicate_different_price(self):
        self.calc.add_item('Apple', 1.5, 2)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.0, 1)

    def test_add_item_invalid_name(self):
        for bad in ('', None, 123):
            with self.assertRaises((ValueError, TypeError)):
                self.calc.add_item(bad, 1.0, 1)

    def test_add_item_invalid_price(self):
        for bad in (0, -1, '1.0'):
            with self.assertRaises((ValueError, TypeError)):
                self.calc.add_item('Apple', bad, 1)

    def test_add_item_invalid_quantity(self):
        for bad in (0, -1, '2'):
            with self.assertRaises((ValueError, TypeError)):
                self.calc.add_item('Apple', 1.0, bad)

    def test_remove_item_success(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_invalid_name(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_get_subtotal_success(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.0)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_success(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_invalid_subtotal(self):
        for bad in (-10, '100'):
            with self.assertRaises((ValueError, TypeError)):
                self.calc.apply_discount(bad, 0.2)

    def test_apply_discount_invalid_discount(self):
        for bad in (-0.1, 1.1, '0.2'):
            with self.assertRaises((ValueError, TypeError)):
                self.calc.apply_discount(100.0, bad)

    def test_calculate_shipping_free(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_paid(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(50.0), self.calc.shipping_cost)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('50')

    def test_calculate_tax_success(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('100')

    def test_calculate_total_no_discount(self):
        self.calc.add_item('Apple', 50.0, 1)
        self.calc.add_item('Banana', 60.0, 1)
        expected_subtotal = 110.0
        expected_tax = expected_subtotal * self.calc.tax_rate
        expected_total = expected_subtotal + expected_tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected_total, places=2)

    def test_calculate_total_half_discount(self):
        self.calc.add_item('Apple', 50.0, 1)
        self.calc.add_item('Banana', 60.0, 1)
        discounted_subtotal = 110.0 * 0.5
        shipping = self.calc.shipping_cost if discounted_subtotal < self.calc.free_shipping_threshold else 0.0
        tax = (discounted_subtotal + shipping) * self.calc.tax_rate
        expected_total = discounted_subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(0.5), expected_total, places=2)

    def test_calculate_total_full_discount(self):
        self.calc.add_item('Apple', 50.0, 1)
        self.calc.add_item('Banana', 60.0, 1)
        discounted_subtotal = 0.0
        shipping = self.calc.shipping_cost
        tax = shipping * self.calc.tax_rate
        expected_total = discounted_subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(1.0), expected_total, places=2)

    def test_calculate_total_invalid_discount(self):
        for bad in (-0.1, 1.1, '0.2'):
            with self.assertRaises((ValueError, TypeError)):
                self.calc.calculate_total(bad)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_total_items(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_clear(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_list_items_unique(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 0.5, 3)
        self.assertEqual(set(self.calc.list_items()), {'Apple', 'Banana'})

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
if __name__ == '__main__':
    unittest.main()