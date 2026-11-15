import unittest
from temp_upload import OrderCalculator, Item

class TestOrderCalculator(unittest.TestCase):
    def test_01_constructor_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertEqual(oc.items, [])

    def test_02_constructor_custom(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0, shipping_cost=0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0)
        self.assertEqual(oc.shipping_cost, 0)

    def test_03_constructor_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")

    def test_04_constructor_tax_rate_value_error_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_05_constructor_tax_rate_value_error_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_06_constructor_free_shipping_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=[])

    def test_07_constructor_free_shipping_threshold_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_08_constructor_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost={})

    def test_09_constructor_shipping_cost_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_10_add_item_normal_first_insertion(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]["name"], "Apple")
        self.assertEqual(oc.items[0]["price"], 1.5)
        self.assertEqual(oc.items[0]["quantity"], 2)
        self.assertEqual(oc.total_items(), 2)

    def test_11_add_item_same_name_price_increase(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Apple", 1.5, 3)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]["quantity"], 5)

    def test_12_add_item_same_name_different_price_error(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 1)
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 2.0, 1)

    def test_13_add_item_name_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_14_add_item_empty_name_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("", 1.0, 1)

    def test_15_add_item_price_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("Apple", [], 1)

    def test_16_add_item_price_non_positive_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 0, 1)
        with self.assertRaises(ValueError):
            oc.add_item("Apple", -1, 1)

    def test_17_add_item_quantity_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("Apple", 1.0, 2.5)

    def test_18_add_item_quantity_less_than_one_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 1.0, 0)

    def test_19_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0)
        self.assertEqual(oc.items[0]["quantity"], 1)

    def test_20_remove_item_normal_removal(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 1)
        oc.remove_item("Apple")
        self.assertTrue(oc.is_empty())

    def test_21_remove_item_nonexistent_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item("Banana")

    def test_22_remove_item_name_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(None)

    def test_23_remove_item_multiple_items_target_removed(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 1)
        oc.add_item("Banana", 2.0, 1)
        oc.remove_item("Apple")
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]["name"], "Banana")

    def test_24_get_subtotal_normal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Banana", 2.0, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 5.0)

    def test_25_get_subtotal_empty_order_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_26_apply_discount_typical(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0.2), 80.0)

    def test_27_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0.0), 100.0)

    def test_28_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 1.0), 0.0)

    def test_29_apply_discount_above_one_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, 1.1)

    def test_30_apply_discount_negative_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, -0.1)

    def test_31_apply_discount_negative_subtotal_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-5, 0.1)

    def test_32_apply_discount_subtotal_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount("100", 0.1)

    def test_33_apply_discount_discount_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100, {})

    def test_34_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(150), 0.0)

    def test_35_calculate_shipping_exact_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(100), 0.0)

    def test_36_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(50), 10.0)

    def test_37_calculate_shipping_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping([])

    def test_38_calculate_shipping_negative_subtotal(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(-10), 10.0)

    def test_39_calculate_tax_positive_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(200), 46.0)

    def test_40_calculate_tax_zero_amount(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0), 0.0)

    def test_41_calculate_tax_negative_amount_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5)

    def test_42_calculate_tax_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax((1, 2))

    def test_43_calculate_total_normal_case(self):
        oc = OrderCalculator()
        oc.add_item("Product", 100.0, 1)
        total = oc.calculate_total(0.1)
        self.assertAlmostEqual(total, 123.0)

    def test_44_calculate_total_free_shipping(self):
        oc = OrderCalculator()
        oc.add_item("Product", 150.0, 1)
        total = oc.calculate_total(0.2)
        self.assertAlmostEqual(total, 147.6)

    def test_45_calculate_total_full_discount(self):
        oc = OrderCalculator()
        oc.add_item("Product", 100.0, 1)
        total = oc.calculate_total(1.0)
        self.assertAlmostEqual(total, 12.3)

    def test_46_calculate_total_empty_order_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_47_calculate_total_discount_type_error(self):
        oc = OrderCalculator()
        oc.add_item("Product", 100.0, 1)
        with self.assertRaises(TypeError):