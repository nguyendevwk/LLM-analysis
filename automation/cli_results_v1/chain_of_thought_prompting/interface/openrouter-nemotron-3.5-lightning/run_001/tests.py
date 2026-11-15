import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default_parameters(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_init_custom_configuration(self):
        c = OrderCalculator(tax_rate=0.15, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(c.tax_rate, 0.15)
        self.assertEqual(c.free_shipping_threshold, 50.0)
        self.assertEqual(c.shipping_cost, 5.0)

    def test_init_negative_tax_rate_raises_valueerror(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_negative_shipping_cost_raises_valueerror(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1.0)

    def test_init_free_shipping_threshold_zero(self):
        c = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(c.free_shipping_threshold, 0.0)

    def test_add_item_normal(self):
        self.calc.add_item("Widget", 10.0)
        self.assertIn("Widget", self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_with_quantity(self):
        self.calc.add_item("Gadget", 20.0, quantity=3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertEqual(self.calc.get_subtotal(), 60.0)

    def test_add_item_empty_name_raises_valueerror(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 10.0)

    def test_add_item_negative_price_raises_valueerror(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Item", -5.0)

    def test_add_item_negative_quantity_raises_valueerror(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Item", 10.0, quantity=-1)

    def test_add_item_zero_quantity_no_items_added(self):
        self.calc.add_item("Item", 10.0, quantity=0)
        self.assertEqual(self.calc.total_items(), 0)

    def test_add_item_duplicate_name(self):
        self.calc.add_item("Item", 10.0)
        self.calc.add_item("Item", 5.0)
        self.assertIn("Item", self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 2)

    def test_add_item_large_quantity(self):
        self.calc.add_item("Item", 1.0, quantity=1000)
        self.assertEqual(self.calc.total_items(), 1000)
        self.assertEqual(self.calc.get_subtotal(), 1000.0)

    def test_remove_item_existing(self):
        self.calc.add_item("Item", 10.0)
        self.calc.remove_item("Item")
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    def test_remove_item_non_existent_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item("NonExistent")

    def test_remove_item_from_empty_cart_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item("Anything")

    def test_remove_item_case_sensitivity(self):
        self.calc.add_item("Apple", 10.0)
        with self.assertRaises(KeyError):
            self.calc.remove_item("apple")

    def test_remove_item_last_item(self):
        self.calc.add_item("Only", 10.0)
        self.calc.remove_item("Only")
        self.assertTrue(self.calc.is_empty())

    def test_get_subtotal_empty_cart(self):
        self.assertEqual(self.calc.get_subtotal(), 0.0)

    def test_get_subtotal_single_item(self):
        self.calc.add_item("Item", 15.0)
        self.assertEqual(self.calc.get_subtotal(), 15.0)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.assertEqual(self.calc.get_subtotal(), 30.0)

    def test_get_subtotal_quantity_gt1(self):
        self.calc.add_item("Item", 12.0, quantity=4)
        self.assertEqual(self.calc.get_subtotal(), 48.0)

    def test_get_subtotal_floating_point_precision(self):
        self.calc.add_item("A", 0.1, quantity=3)
        self.calc.add_item("B", 0.2, quantity=1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.5)

    def test_apply_discount_no_discount(self):
        subtotal = self.calc.get_subtotal()
        result = self.calc.apply_discount(subtotal, 0.0)
        self.assertEqual(result, 0.0)

    def test_apply_discount_absolute(self):
        result = self.calc.apply_discount(100.0, 20.0)
        self.assertEqual(result, 80.0)

    def test_apply_discount_exceeds_subtotal(self):
        result = self.calc.apply_discount(10.0, 20.0)
        self.assertEqual(result, 0.0)

    def test_apply_discount_negative_raises_valueerror(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -10.0)

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_exactly_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_negative_discounted_subtotal_raises_valueerror(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_shipping(-1.0)

    def test_calculate_shipping_threshold_zero(self):
        c = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(c.calculate_shipping(0.0), 0.0)

    def test_calculate_tax_normal(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount_raises_valueerror(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-1.0)

    def test_calculate_total_full_flow_no_discount(self):
        self.calc.add_item("Item", 80.0)
        total = self.calc.calculate_total()
        self.assertIsInstance(total, float)

    def test_calculate_total_with_discount(self):
        self.calc.add_item("Item", 100.0)
        total = self.calc.calculate_total(discount=20.0)
        self.assertIsInstance(total, float)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item("Item", 150.0)
        total = self.calc.calculate_total()
        self.assertIsInstance(total, float)

    def test_calculate_total_without_free_shipping(self):
        self.calc.add_item("Item", 50.0)
        total = self.calc.calculate_total()
        self.assertIsInstance(total, float)

    def test_calculate_total_default_discount(self):
        self.calc.add_item("Item", 50.0)
        total = self.calc.calculate_total()
        self.assertIsInstance(total, float)

    def test_total_items_empty_cart(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_single_quantity_one(self):
        self.calc.add_item("Item", 10.0)
        self.assertEqual(self.calc.total_items(), 1)

    def test_total_items_multiple_quantities(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0, quantity=3)
        self.assertEqual(self.calc.total_items(), 4)

    def test_total_items_item_quantity_five(self):
        self.calc.add_item("Item", 1.0, quantity=5)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order_resets_cart(self):
        self.calc.add_item("Item", 10.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_already_empty(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_clear_order_post_state(self):
        self.calc.add_item("Item", 10.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])
        self.assertEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.total_items(), 0)

    def test_list_items_empty_cart(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_with_items(self):
        self.calc.add_item("A", 10.0)
        self.calc.add_item("B", 20.0)
        self.assertEqual(self.calc.list_items(), ["A", "B"])

    def test_list_items_duplicate_names(self):
        self.calc.add_item("Item", 10.0)
        self.calc.add_item("Item", 5.0)
        self.assertEqual(self.calc.list_items(), ["Item", "Item"])

    def test_is_empty_initially(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false_after_adding(self):
        self.calc.add_item("Item", 10.0)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_true_after_clear(self):
        self.calc.add_item("Item", 10.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_true_after_removing_all(self):
        self.calc.add_item("Item", 10.0)
        self.calc.remove_item("Item")
        self.assertTrue(self.calc.is_empty())