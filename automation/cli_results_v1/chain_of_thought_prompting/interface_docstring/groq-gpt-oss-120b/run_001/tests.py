import unittest
from unittest.mock import patch
from temp_upload import OrderCalculator, Item

class TestOrderCalculator(unittest.TestCase):
    def test_init_default(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)

    def test_init_tax_rate_zero(self):
        oc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(oc.tax_rate, 0.0)

    def test_init_tax_rate_one(self):
        oc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(oc.tax_rate, 1.0)

    def test_init_tax_rate_below_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_above_range(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_free_shipping_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    def test_add_item_valid_single(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        self.assertEqual(oc.total_items(), 2)

    def test_add_item_same_name_price_increases_quantity(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Apple", 1.5, 3)
        self.assertEqual(oc.total_items(), 5)

    def test_add_item_different_name(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Banana", 0.8, 1)
        self.assertCountEqual(oc.list_items(), ["Apple", "Banana"])

    def test_add_item_same_name_different_price_error(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 1)
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 2.0, 1)

    def test_add_item_empty_name_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("", 1.0, 1)

    def test_add_item_name_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_zero_price_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 0.0, 1)

    def test_add_item_negative_price_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Apple", -1.0, 1)

    def test_add_item_price_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("Apple", "free", 1)

    def test_add_item_quantity_zero_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 1.0, 0)

    def test_add_item_negative_quantity_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 1.0, -3)

    def test_add_item_quantity_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("Apple", 1.0, 2.5)

    def test_remove_item_existing(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.remove_item("Apple")
        self.assertTrue(oc.is_empty())

    def test_remove_item_not_exists_error(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 1)
        with self.assertRaises(ValueError):
            oc.remove_item("Banana")

    def test_remove_item_name_type_error(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 1)
        with self.assertRaises(TypeError):
            oc.remove_item(None)

    def test_remove_item_last_item_is_empty(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 1)
        oc.remove_item("Apple")
        self.assertTrue(oc.is_empty())

    def test_get_subtotal_non_empty(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Banana", 0.8, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 3.8)

    def test_get_subtotal_empty_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_typical(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0.2), 80.0)

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50, 0.0), 50.0)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(30, 1.0), 0.0)

    def test_apply_discount_negative_discount_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, -0.1)

    def test_apply_discount_over_one_discount_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, 1.5)

    def test_apply_discount_negative_subtotal_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-5, 0.1)

    def test_apply_discount_subtotal_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount("100", 0.1)

    def test_apply_discount_discount_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100, "0.2")

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(150), 0.0)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(100), 0.0)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(99.99), 10.0)

    def test_calculate_shipping_custom_zero_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=0)
        self.assertAlmostEqual(oc.calculate_shipping(5), 0.0)

    def test_calculate_shipping_non_numeric_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping(None)

    def test_calculate_shipping_negative_subtotal_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping(-1)

    def test_calculate_tax_default_positive(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(200), 46.0)

    def test_calculate_tax_zero_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0), 0.0)

    def test_calculate_tax_negative_amount_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-10)

    def test_calculate_tax_non_numeric_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax("200")

    def test_calculate_tax_zero_rate(self):
        oc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(oc.calculate_tax(123.45), 0.0)

    def test_calculate_tax_full_rate(self):
        oc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(oc.calculate_tax(5), 5.0)

    def test_calculate_total_no_discount_above_threshold(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 12.0, 10)
        self.assertAlmostEqual(oc.calculate_total(), 147.6)

    def test_calculate_total_discount_below_threshold(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 12.0, 10)
        self.assertAlmostEqual(oc.calculate_total(0.2), 130.38)

    def test_calculate_total_full_discount(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 12.0, 10)
        self.assertAlmostEqual(oc.calculate_total(1.0), 12.3)

    def test_calculate_total_empty_order_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_calculate_total_invalid_discount_negative_error(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 10, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(-0.1)

    def test_calculate_total_invalid