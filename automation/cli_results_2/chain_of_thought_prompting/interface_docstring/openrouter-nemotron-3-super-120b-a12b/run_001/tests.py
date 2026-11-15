import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.list_items(), [])

    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_tax_rate_lower_bound(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_upper_bound(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_tax_rate_out_of_range_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_out_of_range_above_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.01)

    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.23")

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1.0)

    def test_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    def test_init_mixed_invalid_args(self):
        with self.assertRaises((ValueError, TypeError)):
            OrderCalculator(tax_rate=-0.1, shipping_cost=-5.0)

    def test_add_item_first_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        self.assertEqual(calc.list_items(), ["Apple"])
        self.assertEqual(calc.total_items(), 2)

    def test_add_item_second_distinct_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.add_item("Banana", 0.5)
        self.assertEqual(set(calc.list_items()), {"Apple", "Banana"})
        self.assertEqual(calc.total_items(), 2)

    def test_add_item_same_name_price_increases_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Apple", 1.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_add_item_same_name_different_price_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 2.0)

    def test_add_item_empty_name_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("", 1.0)

    def test_add_item_name_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_price_non_positive_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 0.0)
        with self.assertRaises(ValueError):
            calc.add_item("Apple", -1.0)

    def test_add_item_price_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Apple", "1.0")
        with self.assertRaises(TypeError):
            calc.add_item("Apple", None)

    def test_add_item_quantity_less_than_one_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 1.0, -3)

    def test_add_item_quantity_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Apple", 1.0, 1.5)
        with self.assertRaises(TypeError):
            calc.add_item("Apple", 1.0, "2")

    def test_add_item_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 10**6)
        self.assertEqual(calc.total_items(), 10**6)

    def test_add_item_after_clear_order(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        calc.add_item("Apple", 1.0, 2)
        self.assertEqual(calc.total_items(), 2)

    def test_remove_item_existing_single_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.remove_item("Apple")
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)

    def test_remove_item_existing_multi_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 3)
        calc.remove_item("Apple")
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)

    def test_remove_item_nonexistent_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item("Apple")

    def test_remove_item_name_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_from_empty_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item("Apple")

    def test_remove_item_updates_total_items(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Banana", 2.0, 1)
        calc.remove_item("Apple")
        self.assertEqual(calc.total_items(), 1)

    def test_remove_then_add_same_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.remove_item("Apple")
        calc.add_item("Apple", 1.0, 3)
        self.assertEqual(calc.total_items(), 3)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 2.5, 4)
        self.assertEqual(calc.get_subtotal(), 10.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 2.0, 3)
        calc.add_item("Banana", 1.5, 2)
        self.assertEqual(calc.get_subtotal(), 2.0*3 + 1.5*2)

    def test_get_subtotal_fractional(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 0.1, 3)
        calc.add_item("Banana", 0.2, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 0.1*3 + 0.2*2)

    def test_get_subtotal_empty_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_after_clear_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_after_remove_all_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.remove_item("Apple")
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero_discount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full_discount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_zero_subtotal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_negative_subtotal_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_discount_out_of_range_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, -0.1)
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, 1.1)

    def test_apply_discount_subtotal_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount("100", 0.1)
        with self.assertRaises(TypeError):
            calc.apply_discount(None, 0.1)

    def test_apply_discount_discount_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, "0.1")
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, None)

    def test_apply_discount_floating_point_edge(self):
        calc = OrderCalculator()
        result = calc.apply_discount(0.1, 0.3333333)
        expected = 0.1 * (1 - 0.3333333)
        self.assertAlmostEqual(result, expected)

    def test_apply_discount_large_numbers(self):
        calc = OrderCalculator()
        self.assertEqual(calc.apply_discount(1e12, 0.1), 9e11)

    def test_calculate_shipping_free_shipping(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_paid_shipping(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(99.999), 10.0)

    def test_calculate_shipping_exact_threshold_free(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_negative_input(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(-5.0), 10.0)

    def test_calculate_shipping_non_numeric_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping("100")
        with self.assertRaises(TypeError):
            calc.calculate_shipping(None)

    def test_calculate_shipping_zero_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_large_numbers(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_shipping(1e12), 0.0)

    def test_calculate_tax_normal(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(50.0), 11.5)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-1.0)

    def test_calculate_tax_non_numeric_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax("50")
        with self.assertRaises(TypeError):
            calc.calculate_tax(None)

    def test_calculate_tax_custom_rate(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertEqual(calc.calculate_tax(100.0), 5.0)

    def test_calculate_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.calculate_tax(100.0), 0.0)

    def test_calculate_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.calculate_tax(100.0), 100.0)

    def test_calculate_tax_floating_point(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.1), 0.023)

    def test_calculate_total_simple_order(self):
        calc = OrderCalculator()
        calc.add_item("Item", 20.0, 2)
        self.assertAlmostEqual(calc.calculate_total(), 61.5)

    def test_calculate_total_free_shipping(self):
        calc = OrderCalculator()
        calc.add_item("Item", 60.0, 2)  # subtotal 120 >= 100
        self.assertAlmostEqual(calc.calculate_total(), 120.0 * 1.23)  # no shipping, tax on 120

    def test_calculate_total_with_discount(self):
        calc = OrderCalculator()
        calc.add_item("Item", 50.0, 2)  # subtotal 100
        # discount 0.1 => discounted subtotal 90 (<100) => shipping 10
        # tax on (90+10)=100 *0.23 =23
        # total = 90+10+23 =123
        self.assertAlmostEqual(calc.calculate_total(0.1), 123.0)

    def test_calculate_total_empty_order_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_negative_subtotal_raises_value_error(self):
        class Subcalc(OrderCalculator):
            def get_subtotal(self):
                return -1.0
        calc = Subcalc()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_invalid_discount_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0)
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.1)

    def test_calculate_total_discount_wrong_type_raises_type_error(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0)
        with self.assertRaises(TypeError):
            calc.calculate_total("0.1")
        with self.assertRaises(TypeError):
            calc.calculate_total(None)

    def test_calculate_total_after_clear_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item("Item", 1e6, 2)
        self.assertAlmostEqual(calc.calculate_total(), (2e6 + 10) * 1.23)  # shipping applies

    def test_calculate_total_does_not_mutate_state(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 2)
        before_items = list(calc.list_items())
        before_total = calc.total_items()
        calc.calculate_total()
        after_items = list(calc.list_items())
        after_total = calc.total_items()
        self.assertEqual(before_items, after_items)
        self.assertEqual(before_total, after_total)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 3)
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Banana", 2.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 4)
        calc.add_item("Banana", 2.0, 1)
        calc.remove_item("Apple")
        self.assertEqual(calc.total_items(), 1)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 5)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_accumulation(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Apple", 1.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Item", 1.0, 10**9)
        self.assertEqual(calc.total_items(), 10**9)

    def test_clear_order_with_items(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_idempotent(self):
        calc = OrderCalculator()
        calc.clear_order()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_fresh_start(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        calc.add_item("Banana", 2.0)
        self.assertEqual(calc.list_items(), ["Banana"])
        self.assertEqual(calc.total_items(), 1)

    def test_clear_order_reference_reset(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        id_before = id(calc.list_items())
        calc.clear_order()
        id_after = id(calc.list_items())
        self.assertNotEqual(id_before, id_after)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        self.assertEqual(calc.list_items(), ["Apple"])

    def test_list_items_multiple_distinct(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.add_item("Banana", 2.0)
        self.assertEqual(set(calc.list_items()), {"Apple", "Banana"})

    def test_list_items_duplicates_single_entry(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Apple", 1.0, 3)
        self.assertEqual(calc.list_items(), ["Apple"])

    def test_list_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.add_item("Banana", 2.0)
        calc.remove_item("Apple")
        self.assertEqual(calc.list_items(), ["Banana"])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_returns_copy(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        lst = calc.list_items()
        lst.append("Banana")
        self.assertNotIn("Banana", calc.list_items())

    def test_is_empty_true_when_empty(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_after_add(self):
        calc = OrderCalculator()
        calc.add_item("Item", 1.0)
        self.assertFalse(calc.is_empty())

    def test_is_empty_true_after_removal_all(self):
        calc = OrderCalculator()
        calc.add_item("Item", 1.0)
        calc.remove_item("Item")
        self.assertTrue(calc.is_empty())

    def test_is_empty_true_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("Item", 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_consistent_with_list_items_and_total_items(self):
        calc = OrderCalculator()
        self.assertEqual(calc.is_empty(), len(calc.list_items()) == 0)
        self.assertEqual(calc.is_empty(), calc.total_items() == 0)
        calc.add_item("A", 1.0, 2)
        self.assertEqual(calc.is_empty(), len(calc.list_items()) == 0)
        self.assertEqual(calc.is_empty(), calc.total_items() == 0)
        calc.remove_item("A")
        self.assertEqual(calc.is_empty(), len(calc.list_items()) == 0)
        self.assertEqual(calc.is_empty(), calc.total_items() == 0)