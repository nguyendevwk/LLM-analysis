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
        self.assertEqual(oc.items[0]['quantity'], 2)

    def test_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8)
        self.assertEqual(oc.items[0]['quantity'], 1)

    def test_add_item_increment_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.items[0]['quantity'], 5)

    def test_add_item_conflicting_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0, 1)

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
            oc.add_item('Apple', '1.0', 1)

    def test_add_item_nonpositive_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 0, 1)

    def test_add_item_invalid_quantity_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', 1.0, 1.5)

    def test_add_item_quantity_less_than_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 1.0, 0)

    def test_remove_item_success(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_remove_item_nonexistent(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Orange')

    def test_remove_item_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_get_subtotal_success(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 3)
        oc.add_item('Banana', 1.0, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 8.0)

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
        result = oc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(result, 50.0)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        result = oc.apply_discount(30.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_invalid_discount_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100.0, '0.1')

    def test_apply_discount_invalid_discount_range(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, 1.5)

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 0.1)

    def test_calculate_shipping_free(self):
        oc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(oc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_cost(self):
        oc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=7.5)
        self.assertAlmostEqual(oc.calculate_shipping(80.0), 7.5)

    def test_calculate_shipping_invalid_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('100')

    def test_calculate_tax_normal(self):
        oc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(oc.calculate_tax(50.0), 10.0)

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
            oc.calculate_tax(None)

    def test_calculate_total_without_discount(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        oc.add_item('ItemA', 30.0, 2)
        total = oc.calculate_total()
        discounted = 60.0
        shipping = 10.0
        tax = (discounted + shipping) * 0.1
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_and_free_shipping(self):
        oc = OrderCalculator(tax_rate=0.2, free_shipping_threshold=50.0, shipping_cost=5.0)
        oc.add_item('ItemA', 40.0, 2)
        total = oc.calculate_total(discount=0.25)
        shipping = 0.0
        tax = (60.0 + shipping) * 0.2
        expected = 60.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount_type(self):
        oc = OrderCalculator()
        oc.add_item('ItemA', 10.0, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount='0.1')

    def test_calculate_total_invalid_discount_range(self):
        oc = OrderCalculator()
        oc.add_item('ItemA', 10.0, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=1.2)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_total_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 3)
        oc.add_item('Banana', 2.0, 2)
        self.assertEqual(oc.total_items(), 5)

    def test_clear_order(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(len(oc.items), 0)

    def test_list_items_unique(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 2.0, 1)
        items = oc.list_items()
        self.assertCountEqual(items, ['Apple', 'Banana'])

    def test_is_empty_initial(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_adding(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        self.assertFalse(oc.is_empty())