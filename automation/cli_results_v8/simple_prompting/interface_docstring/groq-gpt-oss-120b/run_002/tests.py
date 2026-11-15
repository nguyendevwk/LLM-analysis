import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)

    def test_init_invalid_tax_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_tax_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_invalid_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_add_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(oc.total_items(), 2)
        self.assertIn('Apple', oc.list_items())

    def test_add_item_increment_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8, 1)
        oc.add_item('Banana', 0.8, 3)
        self.assertEqual(oc.total_items(), 4)

    def test_add_item_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Milk', 1.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Milk', 1.2, 1)

    def test_add_item_invalid_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_invalid_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Bread', 0, 1)

    def test_add_item_invalid_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Egg', 0.2, 0)

    def test_add_item_type_errors(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            oc.add_item('Cheese', '1.0', 1)
        with self.assertRaises(TypeError):
            oc.add_item('Cheese', 1.0, '2')

    def test_remove_existing_item(self):
        oc = OrderCalculator()
        oc.add_item('Juice', 2.0, 1)
        oc.remove_item('Juice')
        self.assertTrue(oc.is_empty())

    def test_remove_nonexistent_item(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Nonexistent')

    def test_remove_item_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_get_subtotal_calculation(self):
        oc = OrderCalculator()
        oc.add_item('A', 10.0, 2)
        oc.add_item('B', 5.5, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 25.5)

    def test_get_subtotal_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_normal(self):
        oc = OrderCalculator()
        result = oc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(30.0, 1.0), 0.0)

    def test_apply_discount_invalid_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 0.1)

    def test_apply_discount_invalid_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(10.0, -0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(10.0, 1.5)

    def test_apply_discount_type_errors(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            oc.apply_discount(100.0, '0.1')

    def test_calculate_shipping_free(self):
        oc = OrderCalculator(free_shipping_threshold=50.0)
        self.assertAlmostEqual(oc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_cost(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=15.0)
        self.assertAlmostEqual(oc.calculate_shipping(80.0), 15.0)

    def test_calculate_shipping_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('30')

    def test_calculate_tax_normal(self):
        oc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(oc.calculate_tax(100.0), 20.0)

    def test_calculate_tax_zero_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax([10])

    def test_calculate_total_no_discount_free_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=20.0)
        oc.add_item('Item1', 10.0, 2)
        total = oc.calculate_total()
        expected = 20.0 + oc.calculate_tax(20.0)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_and_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=5.0, tax_rate=0.1)
        oc.add_item('ItemA', 30.0, 1)
        oc.add_item('ItemB', 20.0, 2)
        total = oc.calculate_total(discount=0.2)
        shipping = oc.calculate_shipping(56.0)
        tax = oc.calculate_tax(56.0 + shipping)
        expected = 56.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount(self):
        oc = OrderCalculator()
        oc.add_item('X', 10.0, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=1.2)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_calculate_total_invalid_discount_type(self):
        oc = OrderCalculator()
        oc.add_item('Y', 5.0, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount='0.1')

    def test_total_items_counts(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0, 3)
        oc.add_item('B', 2.0, 2)
        self.assertEqual(oc.total_items(), 5)

    def test_clear_order_resets(self):
        oc = OrderCalculator()
        oc.add_item('A', 1.0, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.list_items(), [])

    def test_list_items_unique(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 0.5, 1)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana'])

    def test_is_empty_true_false(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())
        oc.add_item('Item', 1.0, 1)
        self.assertFalse(oc.is_empty())