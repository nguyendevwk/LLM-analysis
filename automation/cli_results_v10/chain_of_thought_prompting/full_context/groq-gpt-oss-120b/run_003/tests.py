import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_init_custom_valid(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0)
        self.assertEqual(oc.shipping_cost, 0)

    def test_init_tax_rate_out_of_range_low(self):
        with self.assertRaisesRegex(ValueError, 'Tax rate must be between 0.0 and 1.0.'):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_out_of_range_high(self):
        with self.assertRaisesRegex(ValueError, 'Tax rate must be between 0.0 and 1.0.'):
            OrderCalculator(tax_rate=1.5)

    def test_init_tax_rate_wrong_type(self):
        with self.assertRaisesRegex(TypeError, 'Tax rate must be a float or int.'):
            OrderCalculator(tax_rate='0.2')

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaisesRegex(ValueError, 'Free shipping threshold cannot be negative.'):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaisesRegex(TypeError, 'Free shipping threshold must be a float or int.'):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_negative_shipping_cost(self):
        with self.assertRaisesRegex(ValueError, 'Shipping cost cannot be negative.'):
            OrderCalculator(shipping_cost=-1)

    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaisesRegex(TypeError, 'Shipping cost must be a float or int.'):
            OrderCalculator(shipping_cost=[])

    def test_add_item_first_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['quantity'], 1)
        self.assertEqual(oc.total_items(), 1)

    def test_add_item_explicit_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, quantity=3)
        self.assertEqual(oc.items[0]['quantity'], 3)
        self.assertEqual(oc.total_items(), 3)

    def test_add_item_second_distinct(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5)
        oc.add_item('Banana', 0.8)
        self.assertEqual(len(oc.items), 2)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana'])

    def test_add_item_merge_same_name_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, quantity=2)
        oc.add_item('Apple', 1.5, quantity=4)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]['quantity'], 6)

    def test_add_item_same_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5)
        with self.assertRaisesRegex(ValueError, 'Item with the same name but different price already exists.'):
            oc.add_item('Apple', 2.0)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Item name cannot be empty.'):
            oc.add_item('', 1.0)

    def test_add_item_name_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Item name must be a string.'):
            oc.add_item(123, 1.0)

    def test_add_item_price_non_positive(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Price must be greater than 0.'):
            oc.add_item('Apple', 0)
        with self.assertRaisesRegex(ValueError, 'Price must be greater than 0.'):
            oc.add_item('Apple', -5)

    def test_add_item_price_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Price must be a number.'):
            oc.add_item('Apple', 'free')

    def test_add_item_quantity_less_than_one(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Quantity must be at least 1.'):
            oc.add_item('Apple', 1.0, quantity=0)
        with self.assertRaisesRegex(ValueError, 'Quantity must be at least 1.'):
            oc.add_item('Apple', 1.0, quantity=-2)

    def test_add_item_quantity_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Quantity must be an integer.'):
            oc.add_item('Apple', 1.0, quantity=2.5)

    def test_add_item_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Widget', 0.01, quantity=10000)
        self.assertEqual(oc.total_items(), 10000)

    def test_add_item_price_as_int(self):
        oc = OrderCalculator()
        oc.add_item('Gadget', 5)
        self.assertEqual(oc.items[0]['price'], 5)

    def test_remove_item_existing(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_remove_item_nonexistent(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, "Item with name 'Nonexistent' does not exist in the order."):
            oc.remove_item('Nonexistent')

    def test_remove_item_name_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Item name must be a string.'):
            oc.remove_item(None)

    def test_remove_item_from_empty(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, "Item with name 'Anything' does not exist in the order."):
            oc.remove_item('Anything')

    def test_get_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, quantity=3)
        oc.add_item('Banana', 1.0, quantity=2)
        self.assertEqual(oc.get_subtotal(), 8.0)

    def test_get_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 5.0)
        self.assertEqual(oc.get_subtotal(), 5.0)

    def test_get_subtotal_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Cannot calculate subtotal on empty order.'):
            oc.get_subtotal()

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(100, 0.0), 100)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(50, 1.0), 0.0)

    def test_apply_discount_typical(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(200, 0.2), 160.0)

    def test_apply_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Discount must be between 0.0 and 1.0.'):
            oc.apply_discount(100, -0.1)

    def test_apply_discount_over_one(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Discount must be between 0.0 and 1.0.'):
            oc.apply_discount(100, 1.5)

    def test_apply_discount_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Discount must be a number.'):
            oc.apply_discount(100, '0.2')

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Cannot apply discount on negative subtotal.'):
            oc.apply_discount(-10, 0.1)

    def test_apply_discount_subtotal_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Subtotal must be a number.'):
            oc.apply_discount([], 0.1)

    def test_apply_discount_subtotal_zero(self):
        oc = OrderCalculator()
        self.assertEqual(oc.apply_discount(0, 0.5), 0.0)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(150), 0.0)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_negative_subtotal(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(-5), 10.0)

    def test_calculate_shipping_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Discounted subtotal must be a number.'):
            oc.calculate_shipping('free')

    def test_calculate_shipping_custom_free_always(self):
        oc = OrderCalculator(free_shipping_threshold=0)
        self.assertEqual(oc.calculate_shipping(5), 0.0)

    def test_calculate_shipping_custom_cost(self):
        oc = OrderCalculator(shipping_cost=5.5)
        self.assertEqual(oc.calculate_shipping(50), 5.5)

    def test_calculate_tax_default(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(50), 11.5)

    def test_calculate_tax_zero_amount(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_tax(0), 0.0)

    def test_calculate_tax_negative(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Cannot calculate tax on negative amount.'):
            oc.calculate_tax(-5)

    def test_calculate_tax_wrong_type(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(TypeError, 'Amount must be a number.'):
            oc.calculate_tax({})

    def test_calculate_tax_custom_full(self):
        oc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(oc.calculate_tax(30), 30.0)

    def test_calculate_tax_custom_zero(self):
        oc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(oc.calculate_tax(123), 0.0)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaisesRegex(ValueError, 'Cannot calculate subtotal on empty order.'):
            oc.calculate_total()

    def test_calculate_total_discount_wrong_type(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 10)
        with self.assertRaisesRegex(TypeError, 'Discount must be a number.'):
            oc.calculate_total(discount='0.1')

    def test_calculate_total_discount_out_of_range(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 10)
        with self.assertRaisesRegex(ValueError, 'Discount must be between 0.0 and 1.0.'):
            oc.calculate_total(discount=1.2)

    def test_calculate_total_no_discount_below_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 40, quantity=2)
        total = oc.calculate_total()
        expected = 80 + 10.0 + (80 + 10.0) * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_no_discount_above_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 75, quantity=2)
        total = oc.calculate_total()
        expected = 150 + 150 * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_discount_below_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 60, quantity=2)
        total = oc.calculate_total(discount=0.2)
        expected = 96 + 10.0 + (96 + 10.0) * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_discount_above_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 65, quantity=2)
        total = oc.calculate_total(discount=0.2)
        expected = 104 + 104 * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_full_discount(self):
        oc = OrderCalculator()
        oc.add_item('Item', 50)
        total = oc.calculate_total(discount=1.0)
        expected = 10.0 + 10.0 * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_custom_configuration(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=7)
        oc.add_item('Item', 40)
        total = oc.calculate_total(discount=0.25)
        expected = 30 + 7 + (30 + 7) * 0.1
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_large_numbers(self):
        oc = OrderCalculator()
        for i in range(100):
            oc.add_item(f'Item{i}', 100, quantity=10)
        subtotal = oc.get_subtotal()
        total = oc.calculate_total()
        expected = subtotal + subtotal * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_calculate_total_floating_point_rounding(self):
        oc = OrderCalculator()
        oc.add_item('Item', 33.33, quantity=1)
        total = oc.calculate_total(discount=0.15)
        discounted = 33.33 * 0.85
        expected = discounted + 10.0 + (discounted + 10.0) * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, quantity=2)
        oc.add_item('B', 1, quantity=3)
        oc.add_item('C', 1, quantity=1)
        self.assertEqual(oc.total_items(), 6)

    def test_total_items_merge(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, quantity=2)
        oc.add_item('A', 1, quantity=5)
        self.assertEqual(oc.total_items(), 7)

    def test_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, quantity=4)
        oc.remove_item('A')
        self.assertEqual(oc.total_items(), 0)

    def test_clear_order_non_empty(self):
        oc = OrderCalculator()
        oc.add_item('A', 1)
        oc.add_item('B', 2)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(len(oc.items), 0)
        self.assertEqual(oc.total_items(), 0)

    def test_clear_order_already_empty(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_list_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_list_items_distinct(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1)
        oc.add_item('Banana', 1)
        oc.add_item('Cherry', 1)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana', 'Cherry'])

    def test_list_items_duplicate_name(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1)
        oc.add_item('Apple', 1, quantity=2)
        self.assertEqual(oc.list_items(), ['Apple'])

    def test_list_items_type(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1)
        for name in oc.list_items():
            self.assertIsInstance(name, str)

    def test_is_empty_fresh(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_add(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_remove(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_integration_add_clear_total(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 10)
        oc.clear_order()
        with self.assertRaisesRegex(ValueError, 'Cannot calculate subtotal on empty order.'):
            oc.calculate_total()

    def test_integration_discount_to_threshold(self):
        oc = OrderCalculator()
        oc.add_item('Item', 125)
        total = oc.calculate_total(discount=0.2)
        expected = 100 + 100 * 0.23
        self.assertAlmostEqual(total, expected, places=2)

    def test_integration_add_remove_queries(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, quantity=3)
        oc.add_item('Banana', 2, quantity=2)
        oc.remove_item('Apple')
        self.assertCountEqual(oc.list_items(), ['Banana'])
        self.assertEqual(oc.total_items(), 2)

    def test_integration_custom_values_used(self):
        oc = OrderCalculator(tax_rate=0.5, free_shipping_threshold=200, shipping_cost=0)
        oc.add_item('Item', 150)
        total = oc.calculate_total()
        expected = 150 + 150 * 0.5
        self.assertAlmostEqual(total, expected, places=2)