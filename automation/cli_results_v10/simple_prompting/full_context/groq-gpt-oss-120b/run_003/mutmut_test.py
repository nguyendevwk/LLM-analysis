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
            OrderCalculator(tax_rate=-0.1)
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
        self.assertEqual(oc.total_items(), 4)
        self.assertEqual(oc.items[0]['quantity'], 4)

    def test_add_item_conflicting_price(self):
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

    def test_add_item_nonpositive_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Bread', 0, 1)

    def test_add_item_invalid_quantity_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Eggs', 0.2, 1.5)

    def test_add_item_quantity_less_than_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Eggs', 0.2, 0)

    def test_remove_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Cheese', 3.0, 1)
        oc.remove_item('Cheese')
        self.assertTrue(oc.is_empty())

    def test_remove_item_nonexistent(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Nonexistent')

    def test_remove_item_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_get_subtotal_success(self):
        oc = OrderCalculator()
        oc.add_item('ItemA', 10.0, 2)
        oc.add_item('ItemB', 5.5, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 25.5)

    def test_get_subtotal_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_typical(self):
        oc = OrderCalculator()
        result = oc.apply_discount(200.0, 0.1)
        self.assertAlmostEqual(result, 180.0)

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(80.0, 1.0), 0.0)

    def test_apply_discount_invalid_discount_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100.0, '0.2')

    def test_apply_discount_out_of_range(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, 1.5)

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 0.2)

    def test_calculate_shipping_free(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=7.0)
        self.assertEqual(oc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_cost(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=12.5)
        self.assertEqual(oc.calculate_shipping(80.0), 12.5)

    def test_calculate_shipping_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('100')

    def test_calculate_tax_typical(self):
        oc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(oc.calculate_tax(150.0), 30.0)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax([100])

    def test_calculate_total_typical(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=5.0)
        oc.add_item('Prod1', 30.0, 2)
        oc.add_item('Prod2', 20.0, 1)
        total = oc.calculate_total(discount=0.25)
        shipping = 5.0
        tax = (60 + shipping) * 0.1
        expected = 60 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=8.0)
        oc.add_item('Item', 25.0, 2)
        total = oc.calculate_total(discount=0.0)
        tax = 50 * oc.tax_rate
        expected = 50 + 0.0 + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_calculate_total_invalid_discount_type(self):
        oc = OrderCalculator()
        oc.add_item('A', 10.0, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount='0.1')

    def test_calculate_total_discount_out_of_range(self):
        oc = OrderCalculator()
        oc.add_item('A', 10.0, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=1.2)

    def test_total_items(self):
        oc = OrderCalculator()
        oc.add_item('X', 1.0, 3)
        oc.add_item('Y', 2.0, 2)
        self.assertEqual(oc.total_items(), 5)

    def test_clear_order(self):
        oc = OrderCalculator()
        oc.add_item('Z', 5.0, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.items, [])

    def test_list_items_unique(self):
        oc = OrderCalculator()
        oc.add_item('Alpha', 1.0, 1)
        oc.add_item('Beta', 2.0, 1)
        oc.add_item('Alpha', 1.0, 2)
        names = oc.list_items()
        self.assertCountEqual(names, ['Alpha', 'Beta'])

    def test_is_empty_initial(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_add(self):
        oc = OrderCalculator()
        oc.add_item('Item', 1.0, 1)
        self.assertFalse(oc.is_empty())