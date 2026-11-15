import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    def test_01_default_init(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_02_custom_init(self):
        c = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(c.tax_rate, 0.0)
        self.assertEqual(c.free_shipping_threshold, 0.0)
        self.assertEqual(c.shipping_cost, 0.0)

    def test_03_invalid_init_negative_tax(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_04_add_item_single(self):
        self.calc.add_item("Apple", 1.5, 2)
        self.assertIn("Apple", self.calc.list_items())
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)
        self.assertEqual(self.calc.total_items(), 2)

    def test_05_add_item_multiple_distinct(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.add_item("Banana", 2.0, 3)
        self.assertCountEqual(self.calc.list_items(), ["Apple", "Banana"])
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0 + 2.0 * 3)
        self.assertEqual(self.calc.total_items(), 4)

    def test_06_add_item_duplicate_name(self):
        self.calc.add_item("Widget", 5.0, 1)
        self.calc.add_item("Widget", 5.0, 2)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5.0 * 3)

    def test_07_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 1.0, 1)

    def test_08_add_item_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_09_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Bad", -1.0, 1)

    def test_10_add_item_zero_price(self):
        self.calc.add_item("Free", 0.0, 2)
        self.assertIn("Free", self.calc.list_items())
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.total_items(), 2)

    def test_11_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("BadQty", 1.0, -2)

    def test_12_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("ZeroQty", 1.0, 0)

    def test_13_remove_item_normal(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.remove_item("Apple")
        self.assertFalse(self.calc.list_items())
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertTrue(self.calc.is_empty())

    def test_14_remove_item_among_many(self):
        self.calc.add_item("A", 1.0, 1)
        self.calc.add_item("B", 2.0, 2)
        self.calc.add_item("C", 3.0, 3)
        self.calc.remove_item("B")
        self.assertCountEqual(self.calc.list_items(), ["A", "C"])
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0 * 1 + 3.0 * 3)

    def test_15_remove_nonexistent_raises(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item("Missing")

    def test_16_get_subtotal_multiple_items(self):
        self.calc.add_item("A", 1.0, 2)
        self.calc.add_item("B", 2.5, 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0 * 2 + 2.5 * 4)

    def test_17_get_subtotal_empty(self):
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    def test_18_apply_discount_normal(self):
        result = self.calc.apply_discount(150.0, 20.0)
        self.assertAlmostEqual(result, 130.0)

    def test_19_apply_discount_equal(self):
        result = self.calc.apply_discount(80.0, 80.0)
        self.assertAlmostEqual(result, 0.0)

    def test_20_apply_discount_exceeds(self):
        result = self.calc.apply_discount(50.0, 60.0)
        self.assertAlmostEqual(result, 0.0)

    def test_21_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -5.0)

    def test_22_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, 10.0)

    def test_23_calculate_shipping_at_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_24_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_25_calculate_shipping_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_shipping(-10.0)

    def test_26_calculate_tax_positive(self):
        tax = self.calc.calculate_tax(80.0)
        self.assertAlmostEqual(tax, 80.0 * 0.23)

    def test_27_calculate_tax_zero(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_28_calculate_tax_negative(self):
        tax = self.calc.calculate_tax(-20.0)
        self.assertAlmostEqual(tax, -20.0 * 0.23)

    def test_29_calculate_total_no_discount_below_threshold(self):
        self.calc.add_item("A", 30.0, 2)  # subtotal 60
        total = self.calc.calculate_total()
        shipping = 10.0
        tax = (60.0 + shipping) * 0.23
        expected = 60.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_30_calculate_total_no_discount_above_threshold(self):
        self.calc.add_item("A", 60.0, 2)  # subtotal 120
        total = self.calc.calculate_total()
        shipping = 0.0
        tax = 120.0 * 0.23
        expected = 120.0 + tax
        self.assertAlmostEqual(total, expected)

    def test_31_calculate_total_discount_pushes_below_threshold(self):
        self.calc.add_item("A", 60.0, 2)  # subtotal 120
        total = self.calc.calculate_total(discount=30.0)  # discounted 90
        shipping = 10.0
        tax = (90.0 + shipping) * 0.23
        expected = 90.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_32_calculate_total_discount_equals_subtotal(self):
        self.calc.add_item("A", 40.0, 2)  # subtotal 80
        total = self.calc.calculate_total(discount=80.0)
        shipping = 10.0
        tax = shipping * 0.23
        expected = shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_33_calculate_total_discount_exceeds_subtotal(self):
        self.calc.add_item("A", 30.0, 2)  # subtotal 60
        total = self.calc.calculate_total(discount=100.0)
        shipping = 10.0
        tax = shipping * 0.23
        expected = shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_34_calculate_total_empty_order(self):
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 0.0)

    def test_35_total_items_multiple_adds(self):
        self.calc.add_item("A", 1.0, 3)
        self.calc.add_item("B", 2.0, 4)
        self.assertEqual(self.calc.total_items(), 7)

    def test_36_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_37_total_items_after_removal(self):
        self.calc.add_item("A", 1.0, 3)
        self.calc.add_item("B", 2.0, 2)
        self.calc.remove_item("A")
        self.assertEqual(self.calc.total_items(), 2)

    def test_38_clear_order_resets_state(self):
        self.calc.add_item("A", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)
        self.assertEqual(self.calc.list_items(), [])
        self.assertEqual(self.calc.total_items(), 0)

    def test_39_list_items_multiple(self):
        self.calc.add_item("A", 1.0, 1)
        self.calc.add_item("B", 2.0, 1)
        self.calc.add_item("C", 3.0, 1)
        self.assertEqual(self.calc.list_items(), ["A", "B", "C"])

    def test_40_list_items_after_removal(self):
        self.calc.add_item("A", 1.0, 1)
        self.calc.add_item("B", 2.0, 1)
        self.calc.add_item("C", 3.0, 1)
        self.calc.remove_item("B")
        self.assertEqual(self.calc.list_items(), ["A", "C"])

    def test_41_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_42_is_empty_fresh(self):
        self.assertTrue(self.calc.is_empty())

    def test_43_is_empty_after_add(self):
        self.calc.add_item("A", 1