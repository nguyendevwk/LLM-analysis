import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    # __init__ tests
    def test_init_default_parameters(self):
        calc = OrderCalculator()
        self.assertIsInstance(calc, OrderCalculator)

    def test_init_invalid_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_invalid_tax_rate_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.23")

    def test_init_invalid_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    def test_init_invalid_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    # add_item tests
    def test_add_item_success(self):
        self.calc.add_item("Apple", 1.5, 2)
        self.assertEqual(self.calc.list_items(), ["Apple"])
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 3.0)

    def test_add_item_default_quantity(self):
        self.calc.add_item("Banana", 0.5)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.5)

    def test_add_item_duplicate_same_price(self):
        self.calc.add_item("Orange", 0.8, 3)
        self.calc.add_item("Orange", 0.8, 2)
        self.assertEqual(self.calc.total_items(), 5)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.0)

    def test_add_item_duplicate_different_price(self):
        self.calc.add_item("Grapes", 2.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("Grapes", 2.5, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 1.0, 1)

    def test_add_item_price_zero_or_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Pear", 0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("Pear", -1, 1)

    def test_add_item_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Peach", 1.0, 0)

    def test_add_item_wrong_types(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item("Mango", "1.0", 1)
        with self.assertRaises(TypeError):
            self.calc.add_item("Mango", 1.0, "2")

    # remove_item tests
    def test_remove_item_success(self):
        self.calc.add_item("Kiwi", 1.2, 2)
        self.calc.remove_item("Kiwi")
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("Nonexistent")

    def test_remove_item_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    # get_subtotal tests
    def test_get_subtotal_success(self):
        self.calc.add_item("Item1", 2.0, 3)
        self.calc.add_item("Item2", 1.5, 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0 * 3 + 1.5 * 2)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    # apply_discount tests
    def test_apply_discount_success(self):
        discounted = self.calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(discounted, 80.0)

    def test_apply_discount_zero(self):
        discounted = self.calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(discounted, 50.0)

    def test_apply_discount_full(self):
        discounted = self.calc.apply_discount(75.0, 1.0)
        self.assertAlmostEqual(discounted, 0.0)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_discount_out_of_range(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, 1.1)

    def test_apply_discount_wrong_types(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100", 0.2)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, "0.2")

    # calculate_shipping tests
    def test_calculate_shipping_free(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    def test_calculate_shipping_non_free(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertAlmostEqual(shipping, self.calc.shipping_cost)

    def test_calculate_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("50")

    # calculate_tax tests
    def test_calculate_tax_success(self):
        tax = self.calc.calculate_tax(200.0)
        self.assertAlmostEqual(tax, 200.0 * self.calc.tax_rate)

    def test_calculate_tax_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("100")

    # calculate_total tests
    def test_calculate_total_no_discount(self):
        self.calc.add_item("A", 20.0, 2)  # subtotal 40
        total = self.calc.calculate_total()
        expected_subtotal = 40.0
        expected_shipping = 0.0 if expected_subtotal >= self.calc.free_shipping_threshold else self.calc.shipping_cost
        expected_tax = (expected_subtotal + expected_shipping) * self.calc.tax_rate
        expected_total = expected_subtotal + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_with_discount(self):
        self.calc.add_item("B", 30.0, 1)  # subtotal 30
        total = self.calc.calculate_total(discount=0.5)  # discounted 15
        expected_subtotal = 30.0
        discounted = expected_subtotal * 0.5
        expected_shipping = 0.0 if discounted >= self.calc.free_shipping_threshold else self.calc.shipping_cost
        expected_tax = (discounted + expected_shipping) * self.calc.tax_rate
        expected_total = discounted + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item("C", 200.0, 1)  # subtotal 200
        total = self.calc.calculate_total(discount=0.5)  # discounted 100
        expected_subtotal = 200.0
        discounted = expected_subtotal * 0.5
        expected_shipping = 0.0 if discounted >= self.calc.free_shipping_threshold else self.calc.shipping_cost
        expected_tax = (discounted + expected_shipping) * self.calc.tax_rate
        expected_total = discounted + expected_shipping + expected_tax
        self.assertAlmostEqual(total, expected_total)

    def test_calculate_total_invalid_discount(self):
        self.calc.add_item("D", 10.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.1)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_wrong_type(self):
        self.calc.add_item("E", 5.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount="0.2")

    # total_items tests
    def test_total_items(self):
        self.calc.add_item("X", 1.0, 3)
        self.calc.add_item("Y", 2.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    # clear_order tests
    def test_clear_order(self):
        self.calc.add_item("Z", 5.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()
        with self.assertRaises(ValueError):
            self.calc.calculate_total()
        with self.assertRaises(ValueError):
            self.calc.remove_item("Z")

    # list_items tests
    def test_list_items(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.add_item("Banana", 0.5, 2)
        self.calc.add_item("Apple", 1.0, 3)
        items = self.calc.list_items()
        self.assertCountEqual(items, ["Apple", "Banana"])

    # is_empty tests
    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item("Item", 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item("Item", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())


if __name__ == "__main__":
    unittest.main()