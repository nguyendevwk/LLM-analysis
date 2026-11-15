import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    def test_init_custom_parameters(self):
        c = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(c.tax_rate, 0.05)
        self.assertEqual(c.free_shipping_threshold, 50.0)
        self.assertEqual(c.shipping_cost, 5.0)

    def test_init_negative_tax_rate_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_negative_free_shipping_threshold_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_negative_shipping_cost_raises(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_default_quantity(self):
        self.calc.add_item("apple", 2.5)
        self.assertIn("apple", self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.5, places=2)

    def test_add_item_explicit_quantity(self):
        self.calc.add_item("banana", 1.2, 3)
        self.assertIn("banana", self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.6, places=2)

    def test_add_item_duplicate_name_increments_quantity(self):
        self.calc.add_item("orange", 1.0, 2)
        self.calc.add_item("orange", 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 5.0, places=2)

    def test_add_item_zero_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("pear", 1.0, 0)

    def test_add_item_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("pear", 1.0, -2)

    def test_add_item_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("pear", -1.0, 1)

    def test_add_item_non_string_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_non_float_price_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("grape", "1.0", 1)

    def test_add_item_non_int_quantity_raises(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("grape", 1.0, 1.5)

    def test_add_item_large_numbers(self):
        self.calc.add_item("gold", 1e9, 1000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1e12, places=2)

    def test_remove_item_existing(self):
        self.calc.add_item("kiwi", 2.0, 2)
        self.calc.remove_item("kiwi")
        self.assertNotIn("kiwi", self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0, places=2)

    def test_remove_item_nonexistent_raises(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item("nonexistent")

    def test_remove_item_after_duplicate_adds(self):
        self.calc.add_item("mango", 3.0, 2)
        self.calc.add_item("mango", 3.0, 3)
        self.calc.remove_item("mango")
        self.assertEqual(self.calc.total_items(), 0)

    def test_remove_item_wrong_type_name_raises(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(456)

    def test_get_subtotal_empty(self):
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0, places=2)

    def test_get_subtotal_single_item(self):
        self.calc.add_item("papaya", 4.5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 9.0, places=2)

    def test_get_subtotal_multiple_items(self):
        self.calc.add_item("a", 1.0, 1)
        self.calc.add_item("b", 2.0, 2)
        self.calc.add_item("c", 3.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1 + 4 + 9, places=2)

    def test_get_subtotal_after_removals(self):
        self.calc.add_item("x", 5.0, 2)
        self.calc.add_item("y", 2.0, 1)
        self.calc.remove_item("x")
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0, places=2)

    def test_get_subtotal_rounding(self):
        self.calc.add_item("z", 0.3333, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.9999, places=4)

    def test_apply_discount_normal(self):
        result = self.calc.apply_discount(100.0, 15.0)
        self.assertAlmostEqual(result, 85.0, places=2)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(result, 50.0, places=2)

    def test_apply_discount_full(self):
        result = self.calc.apply_discount(30.0, 30.0)
        self.assertAlmostEqual(result, 0.0, places=2)

    def test_apply_discount_exceeds_subtotal_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(20.0, 25.0)

    def test_apply_discount_negative_raises(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(20.0, -5.0)

    def test_apply_discount_non_numeric_subtotal_raises(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100", 10.0)

    def test_apply_discount_non_numeric_discount_raises(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, "10")

    def test_calculate_shipping_above_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(150.0), 0.0, places=2)

    def test_calculate_shipping_below_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(80.0), self.calc.shipping_cost, places=2)

    def test_calculate_shipping_exact_threshold(self):
        self.assertAlmostEqual(self.calc.calculate_shipping(self.calc.free_shipping_threshold), 0.0, places=2)

    def test_calculate_shipping_negative_subtotal_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_shipping(-10.0)

    def test_calculate_shipping_non_numeric_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("50")

    def test_calculate_tax_positive_amount(self):
        amount = 100.0
        expected = amount * self.calc.tax_rate
        self.assertAlmostEqual(self.calc.calculate_tax(amount), expected, places=2)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0, places=2)

    def test_calculate_tax_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_non_numeric_raises(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("100")

    def test_calculate_tax_custom_rate(self):
        c = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(c.calculate_tax(200.0), 10.0, places=2)

    def test_calculate_total_empty_no_discount(self):
        self.assertAlmostEqual(self.calc.calculate_total(), 0.0, places=2)

    def test_calculate_total_single_item_below_threshold_no_discount(self):
        self.calc.add_item("item", 40.0, 1)
        subtotal = 40.0
        shipping = self.calc.shipping_cost
        tax = (subtotal + shipping) * self.calc.tax_rate
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected, places=2)

    def test_calculate_total_single_item_above_threshold_no_discount(self):
        self.calc.add_item("item", 120.0, 1)
        subtotal = 120.0
        tax = subtotal * self.calc.tax_rate
        expected = subtotal + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected, places=2)

    def test_calculate_total_discount_keeps_above_threshold(self):
        self.calc.add_item("item", 150.0, 1)
        discount = 20.0
        discounted = 130.0
        tax = discounted * self.calc.tax_rate
        expected = discounted + tax
        self.assertAlmostEqual(self.calc.calculate_total(discount), expected, places=2)

    def test_calculate_total_discount_below_threshold(self):
        self.calc.add_item("item", 80.0, 1)
        discount = 30.0
        discounted = 50.0
        shipping = self.calc.shipping_cost
        tax = (discounted + shipping) * self.calc.tax_rate
        expected = discounted + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(discount), expected, places=2)

    def test_calculate_total_custom_parameters_no_discount(self):
        c = OrderCalculator(tax_rate=0.1, free_shipping_threshold=200.0, shipping_cost=15.0)
        c.add_item("item", 150.0, 1)
        subtotal = 150.0
        shipping = 15.0
        tax = (subtotal + shipping) * 0.1
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(c.calculate_total(), expected, places=