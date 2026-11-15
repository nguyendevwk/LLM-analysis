import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_init_custom_valid(self):
        c = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(c.tax_rate, 0.0)
        self.assertEqual(c.free_shipping_threshold, 0)
        self.assertEqual(c.shipping_cost, 0)
        self.assertTrue(c.is_empty())

    def test_init_invalid_tax_rate_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_invalid_tax_rate_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_invalid_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_invalid_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_single_valid(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_add_item_merge_same_name_price(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.calc.add_item('Apple', 1.5, 3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.5)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item('Apple', 1.5, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.0, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_name_not_string(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_zero_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 0, 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', -5, 1)

    def test_add_item_price_not_number(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', '5', 1)

    def test_add_item_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.0, 0)

    def test_add_item_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 1.0, -3)

    def test_add_item_quantity_not_int(self):
        with self.assertRaises(TypeError):
            self.calc.add_item('Apple', 1.0, 2.5)

    def test_add_item_large_quantity(self):
        self.calc.add_item('Apple', 2.0, 10000)
        self.assertEqual(self.calc.total_items(), 10000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 20000.0)

    def test_add_item_high_precision_price(self):
        self.calc.add_item('Gum', 0.3333333, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.9999999, places=7)

    def test_remove_item_existing(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 2.0, 1)
        self.calc.remove_item('Apple')
        self.assertNotIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 1)

    def test_remove_item_last_remaining(self):
        self.calc.add_item('Apple', 1.0, 1)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Nonexistent')

    def test_remove_item_name_not_string(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_remove_item_from_empty(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('Anything')

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 2.5, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.5)

    def test_get_subtotal_single_item_quantity_gt_one(self):
        self.calc.add_item('Apple', 2.0, 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 8.0)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_get_subtotal_floating_point(self):
        self.calc.add_item('Item', 0.1, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.3, places=7)

    def test_apply_discount_typical(self):
        result = self.calc.apply_discount(100, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(50, 0.0)
        self.assertAlmostEqual(result, 50.0)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(50, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-5, 0.1)

    def test_apply_discount_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, -0.1)

    def test_apply_discount_discount_over_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100, 1.5)

    def test_apply_discount_subtotal_not_number(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)

    def test_apply_discount_discount_not_number(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, '0.1')

    def test_apply_discount_subtotal_zero(self):
        result = self.calc.apply_discount(0, 0.5)
        self.assertAlmostEqual(result, 0.0)

    def test_calculate_shipping_below_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(50), 10.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_zero_shipping_cost(self):
        c = OrderCalculator(shipping_cost=0)
        self.assertAlmostEqual(c.calculate_shipping(50), 0.0)

    def test_calculate_shipping_not_number(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('10')

    def test_calculate_tax_positive_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200), 46.0)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0), 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10)

    def test_calculate_tax_not_number(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax(None)

    def test_calculate_tax_rate_zero(self):
        c = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(c.calculate_tax(100), 0.0)

    def test_calculate_tax_rate_one(self):
        c = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(c.calculate_tax(100), 100.0)

    def test_calculate_total_typical(self):
        self.calc.add_item('A', 30, 2)
        self.calc.add_item('B', 20, 1)
        total = self.calc.calculate_total(0.1)
        shipping = 10.0
        tax = (72 + shipping) * 0.23
        expected = 72 + shipping + tax
        self.assertAlmostEqual(total, expected, places=7)

    def test_calculate_total_no_discount(self):
        self.calc.add_item('A', 40, 1)
        total = self.calc.calculate_total()
        subtotal = 40
        shipping = 10.0
        tax = (subtotal + shipping) * 0.23
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(total, expected, places=7)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_invalid_discount_negative(self):
        self.calc.add_item('A', 10, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-0.1)

    def test_calculate_total_invalid_discount_over_one(self):
        self.calc.add_item('A', 10, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.5)

    def test_calculate_total_discount_not_number(self):
        self.calc.add_item('A', 10, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.1')

    def test_calculate_total_tax_zero_shipping_zero(self):
        c = OrderCalculator(tax_rate=0.0, shipping_cost=0.0)
        c.add_item('A', 100, 1)
        total = c.calculate_total(0.2)
        self.assertAlmostEqual(total, 80.0)

    def test_calculate_total_floating_point_precision(self):
        self.calc.add_item('A', 0.1, 3)
        total = self.calc.calculate_total(0.1)
        shipping = 10.0
        tax = (0.27 + shipping) * 0.23
        expected = 0.27 + shipping + tax
        self.assertAlmostEqual(total, expected, places=7)

    def test_calculate_total_large_order(self):
        for i in range(100):
            self.calc.add_item(f'Item{i}', i + 1, 2)
        subtotal = sum(((i + 1) * 2 for i in range(100)))
        total = self.calc.calculate_total(0.15)
        discounted = subtotal * 0.85
        shipping = 0.0 if discounted >= 100 else 10.0
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected, places=5)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_single(self):
        self.calc.add_item('A', 1, 1)
        self.assertEqual(self.calc.total_items(), 1)

    def test_total_items_multiple(self):
        self.calc.add_item('A', 1, 2)
        self.calc.add_item('B', 1, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_removal(self):
        self.calc.add_item('A', 1, 2)
        self.calc.add_item('B', 1, 3)
        self.calc.remove_item('A')
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_after_clear(self):
        self.calc.add_item('A', 1, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_non_empty(self):
        self.calc.add_item('A', 1, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_already_empty(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_distinct_names(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.add_item('Banana', 1, 1)
        items = self.calc.list_items()
        self.assertCountEqual(items, ['Apple', 'Banana'])

    def test_list_items_duplicate_names_merged(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.add_item('Apple', 1, 2)
        items = self.calc.list_items()
        self.assertEqual(items, ['Apple'])

    def test_list_items_after_removal(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.remove_item('Apple')
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_after_clear(self):
        self.calc.add_item('Apple', 1, 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty_immediately_after_construction(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_adding_item(self):
        self.calc.add_item('A', 1, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_removing_last_item(self):
        self.calc.add_item('A', 1, 1)
        self.calc.remove_item('A')
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('A', 1, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_integration_full_workflow(self):
        self.calc.add_item('Apple', 30, 2)
        self.calc.add_item('Banana', 20, 1)
        total = self.calc.calculate_total(0.1)
        shipping = 10.0
        tax = (72 + shipping) * 0.23
        expected = 72 + shipping + tax
        self.assertAlmostEqual(total, expected, places=7)

    def test_integration_price_conflict_propagation(self):
        self.calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Apple', 2.0, 1)

    def test_integration_state_reset(self):
        self.calc.add_item('Apple', 10, 1)
        self.calc.clear_order()
        self.calc.add_item('Banana', 5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10.0)

    def test_integration_multiple_discounts_sequence(self):
        self.calc.add_item('Apple', 100, 1)
        total1 = self.calc.calculate_total(0.1)
        total2 = self.calc.calculate_total(0.2)
        discounted1 = 100 * 0.9
        discounted2 = 100 * 0.8
        shipping1 = 0.0 if discounted1 >= 100 else 10.0
        shipping2 = 0.0 if discounted2 >= 100 else 10.0
        expected1 = discounted1 + shipping1 + (discounted1 + shipping1) * 0.23
        expected2 = discounted2 + shipping2 + (discounted2 + shipping2) * 0.23
        self.assertAlmostEqual(total1, expected1, places=7)
        self.assertAlmostEqual(total2, expected2, places=7)

    def test_integration_large_quantity_free_shipping_edge(self):
        self.calc.add_item('Item', 1, 100)
        total = self.calc.calculate_total(0.0)
        tax = 100 * 0.23
        expected = 100 + tax
        self.assertAlmostEqual(total, expected, places=7)

    def test_integration_zero_price_edge(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Free', 0, 1)

    def test_integration_custom_parameters_affect_calculations(self):
        c = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=5)
        c.add_item('A', 30, 2)
        total = c.calculate_total(0.0)
        shipping = 0.0
        tax = 60 * 0.1
        expected = 60 + tax
        self.assertAlmostEqual(total, expected, places=7)

    def test_integration_mixed_type_misuse(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 'price', 'qty')
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.1')