import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    # Constructor tests
    def test_default_constructor_values(self):
        self.calc.add_item("apple", 10.0, 2)  # subtotal 20
        total = self.calc.calculate_total()
        # 20 + 10 shipping = 30, tax 23% = 6.9, total = 36.9
        self.assertAlmostEqual(total, 36.9, places=2)

    def test_constructor_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.23")

    def test_constructor_invalid_tax_rate_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_constructor_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    def test_constructor_invalid_free_shipping_threshold_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_constructor_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    def test_constructor_invalid_shipping_cost_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    # add_item tests
    def test_add_item_success(self):
        self.calc.add_item("banana", 5.0, 3)
        self.assertEqual(self.calc.list_items(), ["banana"])
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 15.0, places=2)

    def test_add_item_default_quantity(self):
        self.calc.add_item("pear", 2.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.5, places=2)

    def test_add_item_duplicate_same_price(self):
        self.calc.add_item("banana", 5.0, 3)
        self.calc.add_item("banana", 5.0, 2)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 25.0, places=2)

    def test_add_item_duplicate_different_price(self):
        self.calc.add_item("banana", 5.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("banana", 6.0, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 5.0, 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("pear", -1.0, 1)

    def test_add_item_zero_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("pear", 0.0, 1)

    def test_add_item_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("pear", 1.0, 0)

    def test_add_item_wrong_types(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item("pear", "1.0", 1)
        with self.assertRaises(TypeError):
            self.calc.add_item("pear", 1.0, "1")

    # remove_item tests
    def test_remove_item_success(self):
        self.calc.add_item("apple", 2.0, 1)
        self.calc.remove_item("apple")
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("nonexistent")

    def test_remove_item_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    # get_subtotal tests
    def test_get_subtotal_success(self):
        self.calc.add_item("apple", 2.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0, places=2)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    # apply_discount tests
    def test_apply_discount_success(self):
        discounted = self.calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(discounted, 80.0, places=2)

    def test_apply_discount_zero_discount(self):
        discounted = self.calc.apply_discount(100.0, 0.0)
        self.assertAlmostEqual(discounted, 100.0, places=2)

    def test_apply_discount_full_discount(self):
        discounted = self.calc.apply_discount(100.0, 1.0)
        self.assertAlmostEqual(discounted, 0.0, places=2)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.2)

    def test_apply_discount_discount_out_of_range(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.1)

    def test_apply_discount_wrong_types(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100", 0.2)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, "0.2")

    # calculate_shipping tests
    def test_calculate_shipping_free(self):
        shipping = self.calc.calculate_shipping(120.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_paid(self):
        shipping = self.calc.calculate_shipping(80.0)
        self.assertEqual(shipping, self.calc.shipping_cost)

    def test_calculate_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("80")

    # calculate_tax tests
    def test_calculate_tax_success(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0, places=2)

    def test_calculate_tax_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0, places=2)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("100")

    # calculate_total tests
    def test_calculate_total_no_discount(self):
        self.calc.add_item("apple", 10.0, 2)  # subtotal 20
        total = self.calc.calculate_total()
        # 20 + 10 shipping = 30, tax 23% = 6.9, total = 36.9
        self.assertAlmostEqual(total, 36.9, places=2)

    def test_calculate_total_with_discount(self):
        self.calc.add_item("apple", 10.0, 2)  # subtotal 20
        total = self.calc.calculate_total(discount=0.2)
        # discounted 16, shipping 10 = 26, tax 23% = 5.98, total = 31.98
        self.assertAlmostEqual(total, 31.98, places=2)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item("apple", 60.0, 2)  # subtotal 120
        total = self.calc.calculate_total()
        # shipping free, tax 27.6, total 147.6
        self.assertAlmostEqual(total, 147.6, places=2)

    def test_calculate_total_invalid_discount(self):
        self.calc.add_item("apple", 10.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.1)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_wrong_type(self):
        self.calc.add_item("apple", 10.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount="0.2")

    # total_items tests
    def test_total_items(self):
        self.calc.add_item("apple", 1.0, 2)
        self.calc.add_item("banana", 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    # clear_order tests
    def test_clear_order(self):
        self.calc.add_item("apple", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    # list_items tests
    def test_list_items_unique(self):
        self.calc.add_item("apple", 1.0, 1)
        self.calc.add_item("banana", 2.0, 1)
        self.calc.add_item("apple", 1.0, 2)
        items = self.calc.list_items()
        self.assertEqual(set(items), {"apple", "banana"})
        self.assertEqual(len(items), 2)

    def test_list_items_multiple(self):
        self.calc.add_item("apple", 1.0, 1)
        self.calc.add_item("banana", 2.0, 1)
        self.calc.add_item("cherry", 3.0, 1)
        items = self.calc.list_items()
        self.assertEqual(set(items), {"apple", "banana", "cherry"})
        self.assertEqual(len(items), 3)

    # is_empty tests
    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item("apple", 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item("apple", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())


if __name__ == "__main__":
    unittest.main()