import unittest
from order_calculator import OrderCalculator
from unittest.mock import patch

class TestOrderCalculator(unittest.TestCase):
    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_valid_custom(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")

    def test_init_tax_rate_out_of_range_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_out_of_range_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_free_shipping_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="50")

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_int_parameters(self):
        calc = OrderCalculator(tax_rate=0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(calc.tax_rate, 0)
        self.assertEqual(calc.free_shipping_threshold, 0)
        self.assertEqual(calc.shipping_cost, 0)

    def test_add_item_new_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]["name"], "Apple")
        self.assertEqual(calc.items[0]["price"], 1.0)
        self.assertEqual(calc.items[0]["quantity"], 3)
        self.assertEqual(calc.total_items(), 3)

    def test_add_item_increase_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Book", 10.0, 2)
        calc.add_item("Book", 10.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]["quantity"], 5)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Pen", 2.0)
        self.assertEqual(calc.items[0]["quantity"], 1)

    def test_add_item_price_as_int(self):
        calc = OrderCalculator()
        calc.add_item("Bag", 20, 1)
        self.assertEqual(calc.items[0]["price"], 20)

    def test_add_item_name_empty_string_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("", 5.0, 1)

    def test_add_item_name_not_string_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 5.0, 1)

    def test_add_item_price_not_numeric_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Item", "5", 1)

    def test_add_item_price_zero_or_negative_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Item", 0, 1)
        with self.assertRaises(ValueError):
            calc.add_item("Item", -2.0, 1)

    def test_add_item_quantity_not_int_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Item", 5.0, 2.5)

    def test_add_item_quantity_less_than_one_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Item", 5.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item("Item", 5.0, -1)

    def test_add_item_same_name_different_price_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item("Book", 10.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item("Book", 12.0, 1)

    def test_add_item_after_removal_same_name_different_price_succeeds(self):
        calc = OrderCalculator()
        calc.add_item("Book", 10.0, 1)
        calc.remove_item("Book")
        calc.add_item("Book", 12.0, 1)
        self.assertEqual(calc.items[0]["price"], 12.0)

    def test_remove_item_existing_item(self):
        calc = OrderCalculator()
        calc.add_item("Toy", 5.0, 2)
        calc.remove_item("Toy")
        self.assertEqual(calc.items, [])
        self.assertTrue(calc.is_empty())

    def test_remove_item_nonexistent_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError) as cm:
            calc.remove_item("Nonexistent")
        self.assertIn("Nonexistent", str(cm.exception))

    def test_remove_item_name_not_string_raises_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_multiple_adds_then_remove(self):
        calc = OrderCalculator()
        calc.add_item("Snack", 2.0, 3)
        calc.add_item("Snack", 2.0, 4)
        self.assertEqual(calc.items[0]["quantity"], 7)
        calc.remove_item("Snack")
        self.assertEqual(calc.items, [])

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item("Book", 10.0, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 20.0)

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item("A", 5.0, 3)
        calc.add_item("B", 2.0, 4)
        self.assertAlmostEqual(calc.get_subtotal(), 5.0*3 + 2.0*4)

    def test_get_subtotal_float_price(self):
        calc = OrderCalculator()
        calc.add_item("Candy", 4.99, 2)
        self.assertAlmostEqual(calc.get_subtotal(), 4.99*2)

    def test_get_subtotal_empty_order_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_after_clear_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item("Item", 5.0, 1)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(30.0, 1.0), 0.0)

    def test_apply_discount_float_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(99.99, 0.1), 99.99*0.9)

    def test_apply_discount_subtotal_as_int(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50, 0.1), 45.0)

    def test_apply_discount_negative_subtotal_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_discount_out_of_range_low_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_out_of_range_high_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.2)

    def test_apply_discount_subtotal_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount("100", 0.1)

    def test_apply_discount_discount_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, "0.1")

    def test_calculate_shipping_free_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(120.0), 0.0)

    def test_calculate_shipping_exact_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_charged_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(80.0), 10.0)

    def test_calculate_shipping_zero_shipping_cost(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_subtotal_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping("50")

    def test_calculate_shipping_negative_subtotal_no_validation(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(-30.0), 10.0)  # still below threshold

    def test_calculate_shipping_uses_updated_instance_values(self):
        calc = OrderCalculator()
        calc.free_shipping_threshold = 50.0
        calc.shipping_cost = 7.0
        self.assertEqual(calc.calculate_shipping(60.0), 0.0)
        self.assertEqual(calc.calculate_shipping(40.0), 7.0)

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(200.0), 46.0)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_float_amount(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(calc.calculate_tax(99.99), 99.99*0.05)

    def test_calculate_tax_amount_as_int(self):
        calc = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(calc.calculate_tax(200), 20.0)

    def test_calculate_tax_negative_amount_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_amount_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax("100")

    def test_calculate_tax_uses_updated_tax_rate(self):
        calc = OrderCalculator()
        calc.tax_rate = 0.1
        self.assertAlmostEqual(calc.calculate_tax(200.0), 20.0)

    def test_calculate_total_no_discount_free_shipping(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item("Item", 50.0, 2)  # subtotal 100
        total = calc.calculate_total()
        expected = 100.0 + 0.0 + (100.0 * 0.23)  # subtotal + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_shipping_charged(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item("Item", 50.0, 2)  # subtotal 100
        total = calc.calculate_total(discount=0.1)  # discounted 90, shipping 10, tax on 100
        expected = 90.0 + 10.0 + ((90.0 + 10.0) * 0.23)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping_after_discount(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item("Item", 75.0, 2)  # subtotal 150
        total = calc.calculate_total(discount=0.2)  # discounted 120 >= threshold -> free shipping
        expected = 120.0 + 0.0 + (120.0 * 0.23)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_empty_order_raises_value_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_negative_subtotal_raises_value_error(self):
        calc = OrderCalculator()
        with patch.object(calc, 'get_subtotal', return_value=-5.0):
            with self.assertRaises(ValueError):
                calc.calculate_total()

    def test_calculate_total_discount_type_error(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount="0.1")

    def test_calculate_total_discount_out_of_range_raises_value_error(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.05)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.5)

    def test_calculate_total_uses_updated_shipping_and_tax(self):
        calc = OrderCalculator()
        calc.add_item("Item", 50.0, 2)  # subtotal 100
        calc.shipping_cost = 5.0
        calc.tax_rate = 0.1
        total = calc.calculate_total()  # no discount, shipping charged because threshold default 100? subtotal=100 >=100 -> free shipping actually.
        # adjust threshold to ensure shipping charged
        calc.free_shipping_threshold = 150.0
        total = calc.calculate_total()
        expected = 100.0 + 5.0 + ((100.0 + 5.0) * 0.1)
        self.assertAlmostEqual(total, expected)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_single_item(self):
        calc = OrderCalculator()
        calc.add_item("Item", 5.0, 7)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 3)
        calc.add_item("B", 2.0, 4)
        self.assertEqual(calc.total_items(), 7)

    def test_total_items_after_add_remove_add(self):
        calc = OrderCalculator()
        calc.add_item("Item", 1.0, 2)
        calc.remove_item("Item")
        calc.add_item("Item", 1.0, 3)
        self.assertEqual(calc.total_items(), 3)

    def test_clear_order_non_empty(self):
        calc = OrderCalculator()
        calc.add_item("Item", 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.items, [])
        self.assertTrue(calc.is_empty())

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()  # should not raise
        self.assertEqual(calc.items, [])

    def test_clear_order_does_not_affect_config(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=30.0, shipping_cost=7.0)
        tax = calc.tax_rate
        thr = calc.free_shipping_threshold
        ship = calc.shipping_cost
        calc.add_item("Item", 10.0, 1)
        calc.clear_order()
        self.assertEqual(calc.tax_rate, tax)
        self.assertEqual(calc.free_shipping_threshold, thr)
        self.assertEqual(calc.shipping_cost, ship)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_single_unique_name(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        self.assertEqual(set(calc.list_items()), {"Apple"})

    def test_list_items_multiple_unique_names(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.add_item("Banana", 2.0, 1)
        self.assertEqual(set(calc.list_items()), {"Apple", "Banana"})

    def test_list_items_duplicate_names(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Apple", 1.0, 3)
        self.assertEqual(set(calc.list_items()), {"Apple"})

    def test_list_items_after_removal(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.add_item("Banana", 2.0, 1)
        calc.remove_item("Apple")
        self.assertEqual(set(calc.list_items()), {"Banana"})

    def test_list_items_returned_list_isolation(self):
        calc = OrderCalculator()
        calc.add_item("Item", 1.0, 1)
        lst = calc.list_items()
        lst.append("Extra")
        self.assertNotIn("Extra", calc.list_items())

    def test_is_empty_true(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false(self):
        calc = OrderCalculator()
        calc.add_item("Item", 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_state_transitions(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        calc.add_item("A", 1.0, 1)
        self.assertFalse(calc.is_empty())
        calc.remove_item("A")
        self.assertTrue(calc.is_empty())
        calc.clear_order()
        self.assertTrue(calc.is_empty())