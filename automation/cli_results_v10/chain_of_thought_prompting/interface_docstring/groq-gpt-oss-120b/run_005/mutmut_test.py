import unittest
import math
from decimal import Decimal
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_constructor_default(self):
        oc = self._calc()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_constructor_custom_valid(self):
        oc = self._calc(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0.0)
        self.assertEqual(oc.shipping_cost, 0.0)

    def test_constructor_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            self._calc(tax_rate=-0.01)

    def test_constructor_tax_rate_over_one(self):
        with self.assertRaises(ValueError):
            self._calc(tax_rate=1.5)

    def test_constructor_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            self._calc(free_shipping_threshold=-5)

    def test_constructor_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            self._calc(shipping_cost=-1)

    def test_constructor_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            self._calc(tax_rate='0.2')

    def test_constructor_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            self._calc(free_shipping_threshold='100')

    def test_constructor_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            self._calc(shipping_cost=None)

    def test_add_item_same_name_different_price(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 3.0, 1)

    def test_add_item_empty_name(self):
        oc = self._calc()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_price_zero(self):
        oc = self._calc()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 0.0, 1)

    def test_add_item_price_negative(self):
        oc = self._calc()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', -1.0, 1)

    def test_add_item_quantity_zero(self):
        oc = self._calc()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 1.0, 0)

    def test_add_item_quantity_negative(self):
        oc = self._calc()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 1.0, -2)

    def test_add_item_name_wrong_type(self):
        oc = self._calc()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_price_wrong_type(self):
        oc = self._calc()
        with self.assertRaises(TypeError):
            oc.add_item('Kiwi', '1.5', 1)

    def test_add_item_quantity_wrong_type(self):
        oc = self._calc()
        with self.assertRaises(TypeError):
            oc.add_item('Kiwi', 1.5, 1.5)

    def test_add_item_very_large_quantity(self):
        oc = self._calc()
        oc.add_item('Grapes', 0.01, 10000)
        self.assertEqual(oc.total_items(), 10000)
        self.assertAlmostEqual(oc.get_subtotal(), 100.0, places=5)

    def test_add_item_high_precision_price(self):
        oc = self._calc()
        oc.add_item('Mango', 0.3333333, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 0.9999999, places=5)

    def test_add_item_name_with_whitespace(self):
        oc = self._calc()
        oc.add_item('  Fancy  Apple  ', 2.0, 1)
        self.assertIn('  Fancy  Apple  ', oc.list_items())

    def test_remove_item_only(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_remove_item_one_of_many(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        oc.add_item('Banana', 1.0, 1)
        oc.remove_item('Banana')
        self.assertFalse(oc.is_empty())
        self.assertEqual(oc.list_items(), ['Apple'])

    def test_remove_item_nonexistent(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        with self.assertRaises(ValueError):
            oc.remove_item('Orange')

    def test_remove_item_wrong_type(self):
        oc = self._calc()
        with self.assertRaises(TypeError):
            oc.remove_item(None)

    def test_remove_item_after_merge(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 2)
        oc.add_item('Apple', 2.5, 3)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_remove_item_from_empty(self):
        oc = self._calc()
        with self.assertRaises(ValueError):
            oc.remove_item('Anything')

    def test_is_empty_fresh(self):
        oc = self._calc()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_add(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_remove_last(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_clear(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_clear_on_empty(self):
        oc = self._calc()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_list_items_empty(self):
        oc = self._calc()
        self.assertEqual(oc.list_items(), [])

    def test_list_items_one(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        self.assertEqual(oc.list_items(), ['Apple'])

    def test_list_items_multiple(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        oc.add_item('Banana', 1.0, 1)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana'])

    def test_list_items_duplicate_merged(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        oc.add_item('Apple', 2.5, 2)
        self.assertEqual(oc.list_items(), ['Apple'])

    def test_list_items_case_sensitivity(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        oc.add_item('apple', 2.5, 1)
        self.assertCountEqual(oc.list_items(), ['Apple', 'apple'])

    def test_list_items_whitespace_names(self):
        oc = self._calc()
        oc.add_item('  Foo  ', 1.0, 1)
        self.assertEqual(oc.list_items(), ['  Foo  '])

    def test_total_items_empty(self):
        oc = self._calc()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_single(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 3)
        self.assertEqual(oc.total_items(), 3)

    def test_total_items_multiple(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 3)
        oc.add_item('Banana', 1.0, 1)
        oc.add_item('Apple', 2.5, 2)
        self.assertEqual(oc.total_items(), 6)

    def test_total_items_after_removal(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 3)
        oc.add_item('Banana', 1.0, 2)
        oc.remove_item('Banana')
        self.assertEqual(oc.total_items(), 3)

    def test_total_items_large_quantity(self):
        oc = self._calc()
        oc.add_item('Grapes', 0.01, 10000)
        self.assertEqual(oc.total_items(), 10000)

    def test_total_items_after_clear(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        oc.clear_order()
        self.assertEqual(oc.total_items(), 0)

    def test_get_subtotal_empty_raises(self):
        oc = self._calc()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_get_subtotal_one_item(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 7.5, places=5)

    def test_get_subtotal_multiple_items(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 3)
        oc.add_item('Banana', 1.0, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 8.5, places=5)

    def test_get_subtotal_after_merge(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 3)
        oc.add_item('Apple', 2.5, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 12.5, places=5)

    def test_get_subtotal_after_removal(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 3)
        oc.add_item('Banana', 1.0, 1)
        oc.remove_item('Banana')
        self.assertAlmostEqual(oc.get_subtotal(), 7.5, places=5)

    def test_get_subtotal_high_precision(self):
        oc = self._calc()
        oc.add_item('Mango', 0.3333333, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 0.9999999, places=5)

    def test_get_subtotal_very_large(self):
        oc = self._calc()
        oc.add_item('Gold', 1e+150, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 2e+150, places=5)

    def test_apply_discount_zero(self):
        oc = self._calc()
        self.assertAlmostEqual(oc.apply_discount(100.0, 0.0), 100.0, places=5)

    def test_apply_discount_twenty_percent(self):
        oc = self._calc()
        self.assertAlmostEqual(oc.apply_discount(200.0, 0.2), 160.0, places=5)

    def test_apply_discount_full(self):
        oc = self._calc()
        self.assertAlmostEqual(oc.apply_discount(50.0, 1.0), 0.0, places=5)

    def test_apply_discount_negative(self):
        oc = self._calc()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -0.1)

    def test_apply_discount_over_one(self):
        oc = self._calc()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, 1.5)

    def test_apply_discount_negative_subtotal(self):
        oc = self._calc()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 0.1)

    def test_apply_discount_subtotal_wrong_type(self):
        oc = self._calc()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)

    def test_apply_discount_discount_wrong_type(self):
        oc = self._calc()
        with self.assertRaises(TypeError):
            oc.apply_discount(100.0, '0.1')

    def test_apply_discount_subtotal_zero(self):
        oc = self._calc()
        self.assertAlmostEqual(oc.apply_discount(0.0, 0.5), 0.0, places=5)

    def test_apply_discount_boundary_one(self):
        oc = self._calc()
        self.assertAlmostEqual(oc.apply_discount(80.0, 1.0), 0.0, places=5)

    def test_apply_discount_boundary_zero(self):
        oc = self._calc()
        self.assertAlmostEqual(oc.apply_discount(80.0, 0.0), 80.0, places=5)

    def test_calculate_shipping_below_threshold(self):
        oc = self._calc()
        self.assertAlmostEqual(oc.calculate_shipping(99.99), 10.0, places=5)

    def test_calculate_shipping_at_threshold(self):
        oc = self._calc()
        self.assertAlmostEqual(oc.calculate_shipping(100.0), 0.0, places=5)

    def test_calculate_shipping_above_threshold(self):
        oc = self._calc()
        self.assertAlmostEqual(oc.calculate_shipping(150.0), 0.0, places=5)

    def test_calculate_shipping_zero_subtotal(self):
        oc = self._calc()
        self.assertAlmostEqual(oc.calculate_shipping(0.0), 10.0, places=5)

    def test_calculate_shipping_wrong_type(self):
        oc = self._calc()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('50')

    def test_calculate_shipping_custom_zero_threshold(self):
        oc = self._calc(free_shipping_threshold=0.0)
        self.assertAlmostEqual(oc.calculate_shipping(5.0), 0.0, places=5)

    def test_calculate_shipping_custom_zero_cost(self):
        oc = self._calc(shipping_cost=0.0)
        self.assertAlmostEqual(oc.calculate_shipping(50.0), 0.0, places=5)

    def test_calculate_tax_zero(self):
        oc = self._calc()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0, places=5)

    def test_calculate_tax_positive(self):
        oc = self._calc()
        self.assertAlmostEqual(oc.calculate_tax(100.0), 23.0, places=5)

    def test_calculate_tax_large(self):
        oc = self._calc()
        self.assertAlmostEqual(oc.calculate_tax(1234.56), 1234.56 * 0.23, places=5)

    def test_calculate_tax_negative(self):
        oc = self._calc()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-10.0)

    def test_calculate_tax_wrong_type(self):
        oc = self._calc()
        with self.assertRaises(TypeError):
            oc.calculate_tax([100])

    def test_calculate_tax_custom_zero(self):
        oc = self._calc(tax_rate=0.0)
        self.assertAlmostEqual(oc.calculate_tax(100.0), 0.0, places=5)

    def test_calculate_tax_custom_full(self):
        oc = self._calc(tax_rate=1.0)
        self.assertAlmostEqual(oc.calculate_tax(100.0), 100.0, places=5)

    def test_calculate_total_empty_order(self):
        oc = self._calc()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_calculate_total_single_item_free_shipping(self):
        oc = self._calc(free_shipping_threshold=0.0)
        oc.add_item('Banana', 1.0, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 1.23, places=5)

    def test_calculate_total_multiple_items_discount_shipping(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 3)
        oc.add_item('Banana', 1.0, 1)
        total = oc.calculate_total(0.1)
        self.assertAlmostEqual(total, 21.7095, places=4)

    def test_calculate_total_full_discount_shipping_charged(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 3)
        oc.add_item('Banana', 1.0, 1)
        total = oc.calculate_total(1.0)
        self.assertAlmostEqual(total, 12.3, places=5)

    def test_calculate_total_discount_exact_threshold(self):
        oc = self._calc(free_shipping_threshold=50.0)
        oc.add_item('Apple', 2.5, 25)
        total = oc.calculate_total(0.2)
        self.assertAlmostEqual(total, 61.5, places=5)

    def test_calculate_total_discount_over_one(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(1.5)

    def test_calculate_total_discount_wrong_type(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total('0.1')

    def test_calculate_total_no_discount(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        total = oc.calculate_total(0.0)
        expected = 2.5 + 10.0 + (2.5 + 10.0) * 0.23
        self.assertAlmostEqual(total, expected, places=5)

    def test_calculate_total_full_discount_free_shipping(self):
        oc = self._calc(free_shipping_threshold=0.0)
        oc.add_item('Apple', 2.5, 1)
        total = oc.calculate_total(1.0)
        self.assertAlmostEqual(total, 0.0, places=5)

    def test_calculate_total_custom_zero_shipping(self):
        oc = self._calc(free_shipping_threshold=0.0, shipping_cost=0.0)
        oc.add_item('Apple', 2.5, 2)
        total = oc.calculate_total(0.1)
        discounted = 5.0 * 0.9
        tax = discounted * 0.23
        self.assertAlmostEqual(total, discounted + tax, places=5)

    def test_calculate_total_idempotent(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 2)
        first = oc.calculate_total(0.1)
        second = oc.calculate_total(0.1)
        self.assertAlmostEqual(first, second, places=5)
        self.assertEqual(oc.total_items(), 2)

    def test_calculate_total_after_clear(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        oc.clear_order()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_clear_order_non_empty(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.list_items(), [])
        self.assertEqual(oc.total_items(), 0)

    def test_clear_order_already_empty(self):
        oc = self._calc()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_clear_order_after_failed_add(self):
        oc = self._calc()
        try:
            oc.add_item('', 1.0, 1)
        except ValueError:
            pass
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_interaction_list_before_and_after_clear(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 1)
        oc.add_item('Banana', 1.0, 1)
        before = oc.list_items()
        oc.clear_order()
        after = oc.list_items()
        self.assertCountEqual(before, ['Apple', 'Banana'])
        self.assertEqual(after, [])

    def test_interaction_calculate_total_no_mutation(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 2)
        total1 = oc.calculate_total(0.1)
        total2 = oc.calculate_total(0.1)
        self.assertAlmostEqual(total1, total2, places=5)
        self.assertEqual(oc.total_items(), 2)

    def test_interaction_mixed_operations(self):
        oc = self._calc()
        oc.add_item('Apple', 2.5, 2)
        oc.add_item('Banana', 1.0, 3)
        oc.remove_item('Apple')
        discounted = oc.apply_discount(oc.get_subtotal(), 0.2)
        shipping = oc.calculate_shipping(discounted)
        tax = oc.calculate_tax(discounted + shipping)
        total = discounted + shipping + tax
        self.assertAlmostEqual(oc.calculate_total(0.2), total, places=5)

    def test_interaction_repeated_add_remove(self):
        oc = self._calc()
        for _ in range(5):
            oc.add_item('Apple', 2.5, 1)
            oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_interaction_custom_params_total_equals_discounted(self):
        oc = self._calc(tax_rate=0.0, shipping_cost=0.0, free_shipping_threshold=0.0)
        oc.add_item('Apple', 2.5, 2)
        total = oc.calculate_total(0.15)
        discounted = oc.apply_discount(5.0, 0.15)
        self.assertAlmostEqual(total, discounted, places=5)

    def test_interaction_extreme_floats(self):
        oc = self._calc()
        oc.add_item('Gold', 1e+308, 2)
        total = oc.calculate_total()
        self.assertTrue(math.isinf(total))

    def test_interaction_decimal_type_error(self):
        oc = self._calc()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', Decimal('1.5'), 1)