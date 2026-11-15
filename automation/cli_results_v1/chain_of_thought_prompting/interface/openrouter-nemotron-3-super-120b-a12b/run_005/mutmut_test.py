import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_init_custom(self):
        calc = OrderCalculator(tax_rate=0.08, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.08)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_negative(self):
        calc = OrderCalculator(tax_rate=-0.05)
        self.assertEqual(calc.tax_rate, -0.05)

    def test_init_free_shipping_threshold_zero_or_negative(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        calc2 = OrderCalculator(free_shipping_threshold=-10.0)
        self.assertEqual(calc2.free_shipping_threshold, -10.0)

    def test_init_shipping_cost_zero_or_negative(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)
        calc2 = OrderCalculator(shipping_cost=-5.0)
        self.assertEqual(calc2.shipping_cost, -5.0)

    def test_add_item_new_item(self):
        self.calc.add_item("Apple", 0.5, 3)
        self.assertIn("Apple", self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 3)

    def test_add_item_existing_item_increases_quantity(self):
        self.calc.add_item("Apple", 0.5, 2)
        self.calc.add_item("Apple", 0.5, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_quantity_default(self):
        self.calc.add_item("Banana", 0.3)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_quantity_zero(self):
        self.calc.add_item("Orange", 0.8, 0)
        self.assertIn("Orange", self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 0)

    def test_add_item_price_zero(self):
        self.calc.add_item("Freebie", 0.0, 5)
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_add_item_large_numbers(self):
        self.calc.add_item("Big", 1e6, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2e6)

    def test_add_item_non_string_name_raises_typeerror(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_non_numeric_price_raises_typeerror(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("Item", "price", 1)

    def test_add_item_non_integer_quantity_raises_typeerror(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("Item", 1.0, 1.5)

    def test_add_item_negative_quantity_raises_valueerror(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Item", 1.0, -1)

    def test_add_item_negative_price_accepted(self):
        self.calc.add_item("Refund", -10.0, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), -10.0)

    def test_remove_item_existing_item(self):
        self.calc.add_item("Apple", 0.5, 2)
        self.calc.remove_item("Apple")
        self.assertNotIn("Apple", self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 0)

    def test_remove_item_existing_item_multiple_quantity(self):
        self.calc.add_item("Apple", 0.5, 3)
        self.calc.remove_item("Apple")
        self.assertNotIn("Apple", self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 0)

    def test_remove_item_missing_item_noop(self):
        self.calc.add_item("Apple", 0.5, 1)
        initial_subtotal = self.calc.get_subtotal()
        self.calc.remove_item("Banana")
        self.assertEqual(self.calc.get_subtotal(), initial_subtotal)

    def test_remove_item_non_string_name_raises_typeerror(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    def test_remove_item_empty_string_name(self):
        self.calc.add_item("", 1.0, 2)
        self.calc.remove_item("")
        self.assertNotIn("", self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 0)

    def test_get_subtotal_normal(self):
        self.calc.add_item("A", 2.0, 3)
        self.calc.add_item("B", 1.5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0*3 + 1.5*2)

    def test_get_subtotal_empty_order(self):
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_get_subtotal_zero_price_items(self):
        self.calc.add_item("Free", 0.0, 5)
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_get_subtotal_zero_quantity_items(self):
        self.calc.add_item("ZeroQty", 5.0, 0)
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_get_subtotal_floating_point_precision(self):
        self.calc.add_item("A", 0.1, 1)
        self.calc.add_item("B", 0.2, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.3)

    def test_apply_discount_normal(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.10), 90.0)

    def test_apply_discount_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_one_hundred_percent(self):
        self.assertAlmostEqual(self.calc.apply_discount(80.0, 1.0), 0.0)

    def test_apply_discount_above_one(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 1.2), -10.0)

    def test_apply_discount_negative(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, -0.05), 52.5)

    def test_apply_discount_non_numeric_raises_typeerror(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100", 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, "0.1")

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(80.0), 10.0)

    def test_calculate_shipping_at_threshold_free(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_just_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(99.999), 10.0)

    def test_calculate_shipping_negative_subtotal(self):
        self.assertEqual(self.calc.calculate_shipping(-10.0), 10.0)

    def test_calculate_shipping_zero_or_negative_shipping_cost(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)
        calc2 = OrderCalculator(shipping_cost=-5.0)
        self.assertEqual(calc2.calculate_shipping(50.0), -5.0)

    def test_calculate_shipping_zero_or_negative_free_shipping_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.calculate_shipping(-1.0), 10.0)  # -1 < 0 => shipping cost
        self.assertEqual(calc.calculate_shipping(0.0), 0.0)    # 0 >= 0 => free
        calc2 = OrderCalculator(free_shipping_threshold=-10.0)
        self.assertEqual(calc2.calculate_shipping(-5.0), 0.0)  # -5 >= -10 => free
        self.assertEqual(calc2.calculate_shipping(-20.0), 10.0) # -20 < -10 => cost

    def test_calculate_shipping_non_numeric_raises_typeerror(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("100")

    def test_calculate_tax_normal(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_custom_rate(self):
        calc = OrderCalculator(tax_rate=0.08)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 8.0)

    def test_calculate_tax_zero_amount(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(-50.0), -11.5)

    def test_calculate_tax_large_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(1e12), 2.3e11)

    def test_calculate_tax_non_numeric_raises_typeerror(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("100")

    def test_calculate_total_empty_order_no_discount:
        # subtotal 0, discount 0 => discounted_subtotal 0, shipping cost (threshold 100) => 10, tax on (0+10) = 2.3
        self.assertAlmostEqual(self.calc.calculate_total(0.0), 12.3)

    def test_calculate_total_with_discount_below_threshold:
        self.calc.add_item("Book", 50.0, 1)  # subtotal 50
        # discount 0.2 => discounted_subtotal 40, shipping 10, amount after shipping 50, tax 0.23*50=11.5 => total 61.5
        self.assertAlmostEqual(self.calc.calculate_total(0.2), 61.5)

    def test_calculate_total_above_threshold_free_shipping:
        self.calc.add_item("Item", 120.0, 1)  # subtotal 120 >= threshold => free shipping
        # discount 0.1 => discounted_subtotal 108, shipping 0, tax on 108 = 24.84 => total 132.84
        self.assertAlmostEqual(self.calc.calculate_total(0.1), 132.84)

    def test_calculate_total_empty_order_zero_discount:
        self.assertAlmostEqual(self.calc.calculate_total(0.0), 12.3)

    def test_calculate_total_discount_one_hundred_percent:
        self.calc.add_item("Item", 100.0, 1)
        # discount 1.0 => discounted_subtotal 0, shipping 10, tax on 10 = 2.3 => total 12.3
        self.assertAlmostEqual(self.calc.calculate_total(1.0), 12.3)

    def test_calculate_total_discount_outside_bounds:
        self.calc.add_item("Item", 50.0, 1)
        # discount -0.1 => increase subtotal by 10% => 55, shipping 10, amount 65, tax 14.95 => total 79.95
        self.assertAlmostEqual(self.calc.calculate_total(-0.1), 79.95)
        # discount 1.5 => discounted_subtotal -25, shipping 10 (since -25 < 100), amount -15, tax -3.45 => total -18.45
        self.assertAlmostEqual(self.calc.calculate_total(1.5), -18.45)

    def test_calculate_total_non_numeric_discount_raises_typeerror(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total("0.1")

    def test_total_items_normal(self):
        self.calc.add_item("A", 1.0, 2)
        self.calc.add_item("B", 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_empty_order(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_zero_quantity_items(self):
        self.calc.add_item("Zero", 5.0, 0)
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order(self):
        self.calc.add_item("Item", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.total_items(), 0)
        self.assertEqual(self.calc.list_items(), [])

    def test_clear_order_multiple_times(self):
        self.calc.add_item("Item", 1.0, 1)
        self.calc.clear_order()
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_list_items_normal(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.add_item("Banana", 2.0, 1)
        items = self.calc.list_items()
        self.assertEqual(set(items), {"Apple", "Banana"})
        self.assertEqual(len(items), 2)

    def test_list_items_empty_order(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_duplicate_item_name_once(self):
        self.calc.add_item("Apple", 1.0, 2)
        self.calc.add_item("Apple", 1.0, 3)
        self.assertEqual(self.calc.list_items(), ["Apple"])

    def test_list_items_after_removal(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.add_item("Banana", 1.0, 1)
        self.calc.remove_item("Apple")
        self.assertEqual(self.calc.list_items(), ["Banana"])

    def test_is_empty_normal(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item("Item", 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_zero_quantity_item_considered_not_empty(self):
        self.calc.add_item("Zero", 1.0, 0)
        self.assertFalse(self.calc.is_empty())  # zero quantity still present in list_items

    def test_is_empty_after_clear_or_remove_last(self):
        self.calc.add_item("Item", 1.0, 1)
        self.calc.remove_item("Item")
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item("Item", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_interaction_add_two_items_apply_discount_calculate_total_remove_one_recalculate(self):
        self.calc.add_item("A", 10.0, 2)  # 20
        self.calc.add_item("B", 5.0, 3)    # 15 => subtotal 35
        # discount 0.1 => discounted_subtotal 31.5, shipping 10 (since <100), amount 41.5, tax 9.545 => total 51.045
        self.assertAlmostEqual(self.calc.calculate_total(0.1), 51.045)
        self.calc.remove_item("A")  # remove 20 => subtotal 15
        # discount 0.1 => discounted_subtotal 13.5, shipping 10, amount 23.5, tax 5.405 => total 28.905
        self.assertAlmostEqual(self.calc.calculate_total(0.1), 28.905)

    def test_interaction_free_shipping_threshold_crossed_by_discount(self):
        self.calc.add_item("Item", 120.0, 1)  # subtotal 120 >= threshold => free shipping
        # no discount => total = subtotal + tax on subtotal = 120 + 27.6 = 147.6
        self.assertAlmostEqual(self.calc.calculate_total(0.0), 147.6)
        # apply discount 0.2 => discounted_subtotal 96 (<100) => shipping 10, amount after shipping 106, tax 24.38 => total 130.38
        self.assertAlmostEqual(self.calc.calculate_total(0.2), 130.38)

    def test_interaction_clear_then_add_new_items(self):
        self.calc.add_item("Old", 1.0, 1)
        self.calc.clear_order()
        self.calc.add_item("New", 2.0, 3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0)

    def test_interaction_alternate_add_remove_same_name(self):
        for i in range(5):
            self.calc.add_item("X", 1.0, 1)
            self.assertEqual(self.calc.total_items(), i+1)
            self.calc.remove_item("X")
            self.assertEqual(self.calc.total_items(), 0)