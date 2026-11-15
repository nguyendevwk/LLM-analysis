import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_default_params(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom_valid_params(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)
        self.assertTrue(calc.is_empty())

    def test_init_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_tax_rate_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_free_shipping_threshold_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_shipping_cost_negative_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_tax_rate_string_raises_TypeError(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')

    def test_init_free_shipping_threshold_string_raises_TypeError(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_shipping_cost_string_raises_TypeError(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_init_tax_rate_None_raises_TypeError(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate=None)

    def test_init_free_shipping_threshold_None_raises_TypeError(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_shipping_cost_None_raises_TypeError(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_add_item_first_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(calc.total_items(), 2)
        self.assertEqual(calc.list_items(), ['Apple'])
        self.assertAlmostEqual(calc.get_subtotal(), 2.0)

    def test_add_item_same_name_price_increases_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)
        self.assertAlmostEqual(calc.get_subtotal(), 5.0)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.5)
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 1.5)

    def test_add_item_price_with_many_decimals(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.3333333333, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 0.9999999999)

    def test_add_item_empty_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('', 1.0)

    def test_add_item_price_non_positive_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 0.0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', -1.0)

    def test_add_item_quantity_less_than_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 1.0, -5)

    def test_add_item_same_name_different_price_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item('Apple', 2.0, 1)
        self.assertEqual(calc.total_items(), 1)
        self.assertAlmostEqual(calc.get_subtotal(), 1.0)

    def test_add_item_non_string_name_raises_TypeError(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_non_numeric_price_raises_TypeError(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', '1.0')

    def test_add_item_non_int_quantity_raises_TypeError(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, 1.5)
        with self.assertRaises(TypeError):
            calc.add_item('Apple', 1.0, '2')

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)

    def test_remove_item_quantity_greater_than_one(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 5)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_remove_item_from_single_item_order(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_remove_item_non_existent_name_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            calc.remove_item('Banana')
        self.assertFalse(calc.is_empty())

    def test_remove_item_non_string_name_raises_TypeError(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_from_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item('Apple')

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.5, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 7.5)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 2)
        calc.add_item('Banana', 3.0, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 7.0)

    def test_get_subtotal_fractional_price(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.1, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3)

    def test_get_subtotal_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_state_consistency(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 2.0, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 4.0)
        calc.add_item('Banana', 3.0, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 7.0)
        calc.remove_item('Apple')
        self.assertAlmostEqual(calc.get_subtotal(), 3.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_twenty_percent(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_subtotal_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_one_hundred_percent(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_negative_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-1.0, 0.1)

    def test_apply_discount_negative_discount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_above_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.1)

    def test_apply_discount_non_numeric_inputs_raises_TypeError(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, '0.1')

    def test_apply_discount_precision(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(1.0, 0.333333), 0.666667, places=6)

    def test_calculate_shipping_free_when_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_cost_when_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_free_at_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(-50.0), 10.0)

    def test_calculate_shipping_non_numeric_input_raises_TypeError(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping('100')

    def test_calculate_shipping_respects_constructor_values(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(30.0), 5.0)
        self.assertEqual(calc.calculate_shipping(60.0), 0.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_fractional_amount(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(0.1), 0.023)

    def test_calculate_tax_negative_amount_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-1.0)

    def test_calculate_tax_non_numeric_input_raises_TypeError(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax('100')

    def test_calculate_tax_respects_constructor_rate(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(calc.calculate_tax(200.0), 10.0)

    def test_calculate_total_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_one_item_no_discount_above_threshold(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Apple', 50.0, 2)
        expected = 100.0 + calc.calculate_tax(100.0)
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_one_item_discount_below_threshold(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Apple', 50.0, 2)
        total = calc.calculate_total(0.1)
        discounted = 100.0 * 0.9
        shipping = 10.0
        taxable = discounted + shipping
        expected = taxable + calc.calculate_tax(taxable)
        self.assertAlmostEqual(calc.calculate_total(0.1), expected)

    def test_calculate_total_discount_zero(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Apple', 50.0, 2)
        total_no_discount = calc.calculate_total()
        total_zero_discount = calc.calculate_total(0.0)
        self.assertAlmostEqual(total_no_discount, total_zero_discount)

    def test_calculate_total_discount_one(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Apple', 50.0, 2)
        total = calc.calculate_total(1.0)
        shipping = 10.0
        taxable = shipping
        expected = taxable + calc.calculate_tax(taxable)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount_negative_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)

    def test_calculate_total_invalid_discount_above_one_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.1)

    def test_calculate_total_non_numeric_discount_raises_TypeError(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total('0.1')

    def test_calculate_total_state_consistency(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item('A', 20.0, 2)
        calc.add_item('B', 30.0, 1)
        subtotal = 70.0
        discounted = calc.apply_discount(subtotal, 0.0)
        shipping = calc.calculate_shipping(discounted)
        taxable = discounted + shipping
        expected = taxable + calc.calculate_tax(taxable)
        self.assertAlmostEqual(calc.calculate_total(), expected)
        discounted = calc.apply_discount(subtotal, 0.1)
        shipping = calc.calculate_shipping(discounted)
        taxable = discounted + shipping
        expected = taxable + calc.calculate_tax(taxable)
        self.assertAlmostEqual(calc.calculate_total(0.1), expected)
        calc.remove_item('A')
        subtotal = 30.0
        discounted = calc.apply_discount(subtotal, 0.0)
        shipping = calc.calculate_shipping(discounted)
        taxable = discounted + shipping
        expected = taxable + calc.calculate_tax(taxable)
        self.assertAlmostEqual(calc.calculate_total(), expected)

    def test_calculate_total_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('Big', 10 ** 6, 10 ** 6)
        subtotal = 10 ** 12
        total = calc.calculate_total()
        expected = subtotal + calc.calculate_tax(subtotal)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_deterministic(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10.0, 2)
        r1 = calc.calculate_total(0.05)
        r2 = calc.calculate_total(0.05)
        self.assertEqual(r1, r2)

    def test_calculate_total_after_clear_order_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10.0, 1)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 5)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 1.0, 3)
        calc.add_item('C', 1.0, 1)
        self.assertEqual(calc.total_items(), 6)

    def test_total_items_increase_existing_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(calc.total_items(), 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_decrease_on_remove(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 4)
        calc.add_item('Banana', 1.0, 2)
        self.assertEqual(calc.total_items(), 6)
        calc.remove_item('Apple')
        self.assertEqual(calc.total_items(), 2)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_non_empty(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 2)
        self.assertFalse(calc.is_empty())
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_internal_list_length(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 1.0, 1)
        self.assertEqual(len(calc.items), 2)
        calc.clear_order()
        self.assertEqual(len(calc.items), 0)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_duplicate_name_single_entry(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        self.assertEqual(calc.list_items(), ['Apple'])

    def test_list_items_after_remove(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 1.0, 1)
        calc.remove_item('Apple')
        self.assertEqual(calc.list_items(), ['Banana'])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_is_empty_initial(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_add(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_remove_last(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_consistency_with_total_items(self):
        calc = OrderCalculator()
        self.assertEqual(calc.is_empty(), calc.total_items() == 0)
        calc.add_item('A', 1.0, 1)
        self.assertEqual(calc.is_empty(), calc.total_items() == 0)
        calc.remove_item('A')
        self.assertEqual(calc.is_empty(), calc.total_items() == 0)
        calc.add_item('B', 2.0, 3)
        calc.add_item('C', 3.0, 1)
        self.assertEqual(calc.is_empty(), calc.total_items() == 0)
        calc.clear_order()
        self.assertEqual(calc.is_empty(), calc.total_items() == 0)