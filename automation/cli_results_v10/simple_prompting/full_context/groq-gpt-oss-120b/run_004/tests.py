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

    def test_init_negative_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['name'], 'Apple')
        self.assertEqual(oc.items[0]['price'], 1.5)
        self.assertEqual(oc.items[0]['quantity'], 2)

    def test_add_item_increment_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8, 1)
        oc.add_item('Banana', 0.8, 3)
        self.assertEqual(oc.items[0]['quantity'], 4)

    def test_add_item_different_price_same_name(self):
        oc = OrderCalculator()
        oc.add_item('Milk', 2.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Milk', 2.5, 1)

    def test_add_item_invalid_name_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_invalid_price_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Bread', '1.0', 1)

    def test_add_item_negative_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Bread', -1.0, 1)

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
        oc.add_item('Cheese', 3.0, 1)
        oc.remove_item('Cheese')
        self.assertTrue(oc.is_empty())

    def test_remove_item_not_exists(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Nonexistent')

    def test_remove_item_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_get_subtotal_success(self):
        oc = OrderCalculator()
        oc.add_item('Item1', 10.0, 2)
        oc.add_item('Item2', 5.0, 3)
        self.assertEqual(oc.get_subtotal(), 10.0 * 2 + 5.0 * 3)

    def test_get_subtotal_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_success(self):
        oc = OrderCalculator()
        result = oc.apply_discount(200.0, 0.1)
        self.assertAlmostEqual(result, 180.0)

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(80.0, 1.0), 0.0)

    def test_apply_discount_invalid_discount_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100.0, '0.2')

    def test_apply_discount_invalid_discount_range(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, 1.5)

    def test_apply_discount_invalid_subtotal_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 0.1)

    def test_calculate_shipping_free(self):
        oc = OrderCalculator(free_shipping_threshold=50.0)
        self.assertEqual(oc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_cost(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=12.5)
        self.assertEqual(oc.calculate_shipping(80.0), 12.5)

    def test_calculate_shipping_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('30')

    def test_calculate_tax_success(self):
        oc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(oc.calculate_tax(150.0), 30.0)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax([100])

    def test_calculate_tax_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5.0)

    def test_calculate_total_no_discount_free_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=20.0)
        oc.add_item('A', 10.0, 2)
        total = oc.calculate_total()
        subtotal = 20.0
        tax = subtotal * oc.tax_rate
        self.assertAlmostEqual(total, subtotal + tax)

    def test_calculate_total_with_discount_and_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=15.0, tax_rate=0.1)
        oc.add_item('B', 30.0, 2)
        total = oc.calculate_total(discount=0.2)
        subtotal = 60.0
        discounted = subtotal * 0.8
        shipping = 15.0
        tax = (discounted + shipping) * 0.1
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount_type(self):
        oc = OrderCalculator()
        oc.add_item('C', 5.0, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount='0.1')

    def test_total_items(self):
        oc = OrderCalculator()
        oc.add_item('X', 1.0, 3)
        oc.add_item('Y', 2.0, 2)
        self.assertEqual(oc.total_items(), 5)

    def test_clear_order(self):
        oc = OrderCalculator()
        oc.add_item('Z', 4.0, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(len(oc.items), 0)

    def test_list_items(self):
        oc = OrderCalculator()
        oc.add_item('Alpha', 1.0, 1)
        oc.add_item('Beta', 2.0, 1)
        oc.add_item('Alpha', 1.0, 2)
        items = oc.list_items()
        self.assertCountEqual(items, ['Alpha', 'Beta'])

    def test_is_empty_true_false(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())
        oc.add_item('Item', 1.0, 1)
        self.assertFalse(oc.is_empty())

    def test_calculate_total_full_discount_shipping_applied(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=8.0, tax_rate=0.15)
        oc.add_item('D', 20.0, 2)
        total = oc.calculate_total(discount=1.0)
        discounted = 0.0
        shipping = 8.0
        tax = shipping * 0.15
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)