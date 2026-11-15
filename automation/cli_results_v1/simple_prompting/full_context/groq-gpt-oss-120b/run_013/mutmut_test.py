import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_init_invalid_tax_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_tax_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 3)
        self.assertEqual(oc.total_items(), 3)
        self.assertIn('Apple', oc.list_items())

    def test_add_item_merge_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.5, 2)
        oc.add_item('Banana', 0.5, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_add_item_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Milk', 1.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Milk', 1.2, 1)

    def test_add_item_invalid_name_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0)

    def test_add_item_invalid_price_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Bread', '1.0')

    def test_add_item_nonpositive_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Bread', 0)

    def test_add_item_invalid_quantity_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Egg', 0.2, 1.5)

    def test_add_item_quantity_less_than_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Egg', 0.2, 0)

    def test_remove_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Cheese', 2.0, 1)
        oc.remove_item('Cheese')
        self.assertTrue(oc.is_empty())

    def test_remove_item_not_exists(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Nonexistent')

    def test_remove_item_invalid_name_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_get_subtotal_success(self):
        oc = OrderCalculator()
        oc.add_item('A', 10, 2)
        oc.add_item('B', 5, 1)
        self.assertEqual(oc.get_subtotal(), 25)

    def test_get_subtotal_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_normal(self):
        oc = OrderCalculator()
        result = oc.apply_discount(100, 0.2)
        self.assertEqual(result, 80)

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(50, 0.0), 50)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(30, 1.0), 0)

    def test_apply_discount_invalid_discount_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100, '0.1')

    def test_apply_discount_invalid_discount_range(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, 1.5)

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10, 0.1)

    def test_calculate_shipping_free(self):
        oc = OrderCalculator(free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(oc.calculate_shipping(60), 0.0)

    def test_calculate_shipping_cost(self):
        oc = OrderCalculator(free_shipping_threshold=100, shipping_cost=7)
        self.assertEqual(oc.calculate_shipping(80), 7)

    def test_calculate_shipping_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('100')

    def test_calculate_tax_normal(self):
        oc = OrderCalculator(tax_rate=0.2)
        self.assertEqual(oc.calculate_tax(50), 10)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_tax(0), 0)

    def test_calculate_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5)

    def test_calculate_tax_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax(None)

    def test_calculate_total_no_discount_free_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=20, shipping_cost=5, tax_rate=0.1)
        oc.add_item('X', 10, 2)
        total = oc.calculate_total()
        subtotal = 20
        discounted = 20
        shipping = 0
        tax = (discounted + shipping) * 0.1
        self.assertAlmostEqual(total, discounted + shipping + tax)

    def test_calculate_total_with_discount_and_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=100, shipping_cost=10, tax_rate=0.2)
        oc.add_item('Y', 30, 1)
        total = oc.calculate_total(discount=0.1)
        subtotal = 30
        discounted = 27
        shipping = 10
        tax = (discounted + shipping) * 0.2
        self.assertAlmostEqual(total, discounted + shipping + tax)

    def test_calculate_total_invalid_discount_type(self):
        oc = OrderCalculator()
        oc.add_item('Z', 5, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount='0.1')

    def test_calculate_total_invalid_discount_range(self):
        oc = OrderCalculator()
        oc.add_item('Z', 5, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=1.2)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 2)
        oc.add_item('B', 2, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_clear_order(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.items, [])

    def test_list_items_unique(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 1)
        oc.add_item('A', 1, 2)
        oc.add_item('B', 2, 1)
        items = oc.list_items()
        self.assertCountEqual(items, ['A', 'B'])

    def test_is_empty_true(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_false(self):
        oc = OrderCalculator()
        oc.add_item('Item', 1, 1)
        self.assertFalse(oc.is_empty())