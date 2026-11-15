import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def test_constructor_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_constructor_custom(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0)
        self.assertEqual(oc.shipping_cost, 0)

    def test_constructor_tax_rate_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_constructor_tax_rate_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_constructor_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")

    def test_constructor_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_constructor_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_constructor_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_constructor_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost={})

    def test_add_item_normal(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        self.assertEqual(oc.total_items(), 2)
        self.assertIn("Apple", oc.list_items())

    def test_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item("Banana", 0.8)
        self.assertEqual(oc.total_items(), 1)
        self.assertEqual(oc.items[0]["quantity"], 1)

    def test_add_item_duplicate_same_price(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Apple", 1.5, 3)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]["quantity"], 5)

    def test_add_item_duplicate_different_price(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 1)
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 2.0, 1)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("", 1.0)

    def test_add_item_zero_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Item", 0)

    def test_add_item_negative_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Item", -5)

    def test_add_item_quantity_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Item", 1.0, 0)

    def test_add_item_quantity_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Item", 1.0, -2)

    def test_add_item_name_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_price_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("Item", "1.0", 1)

    def test_add_item_quantity_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("Item", 1.0, 1.5)

    def test_remove_item_normal(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.remove_item("Apple")
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)

    def test_remove_item_nonexistent(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item("Pear")

    def test_remove_item_name_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(42)

    def test_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 2)
        oc.add_item("Banana", 1.0, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_total_items_duplicate(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 2)
        oc.add_item("Apple", 1.0, 4)
        self.assertEqual(oc.total_items(), 6)

    def test_list_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    def test_list_items_distinct(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0)
        oc.add_item("Banana", 1.0)
        oc.add_item("Cherry", 1.0)
        self.assertCountEqual(oc.list_items(), ["Apple", "Banana", "Cherry"])

    def test_list_items_duplicate(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 2)
        oc.add_item("Apple", 1.0, 3)
        self.assertEqual(oc.list_items(), ["Apple"])

    def test_clear_order_populated(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0)
        oc.add_item("Banana", 1.0)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)
        self.assertEqual(oc.list_items(), [])

    def test_clear_order_already_empty(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_is_empty_fresh(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_add(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_remove(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0)
        oc.remove_item("Apple")
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_get_subtotal_normal(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Banana", 0.8, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 5.4)

    def test_get_subtotal_single(self):
        oc = OrderCalculator()
        oc.add_item("Gadget", 99.99, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 99.99)

    def test_get_subtotal_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_none(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(200.0, 1.0), 0.0)

    def test_apply_discount_typical(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(150.0, 0.2), 120.0)

    def test_apply_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, -0.1)

    def test_apply_discount_over_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100.0, 1.5)

    def test_apply_discount_subtotal_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount("100", 0.1)

    def test_apply_discount_discount_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100.0, "0.1")

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10.0, 0.1)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_custom_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=0)
        self.assertAlmostEqual(oc.calculate_shipping(5.0), 0.0)

    def test_calculate_shipping_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping("50")

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_positive_default(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_custom_zero(self):
        oc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(oc.calculate_tax(50.0), 0.0)

    def test_calculate_tax_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5.0)

    def test_calculate_tax_type(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax([10])

    def test_calculate_total_free_shipping(self):
        oc = OrderCalculator()
        oc.add_item("ItemA", 60.0, 2)
        total = oc.calculate_total(0.1)
        self.assertAlmostEqual(total, 132.84)

    def test_calculate_total_with_shipping(self):
        oc = OrderCalculator()
        oc.add_item("ItemB", 30.0, 1)
        total = oc.calculate_total(0.0)
        self.assertAlmostEqual(total, 49.2)

    def test_cal