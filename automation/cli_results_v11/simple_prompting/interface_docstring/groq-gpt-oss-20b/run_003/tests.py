import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    # __init__ tests
    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    def test_init_custom(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_invalid_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_invalid_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_wrong_types(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    # add_item tests
    def test_add_item_success(self):
        self.calc.add_item("Apple", 1.5, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertIn("Apple", self.calc.list_items())

    def test_add_item_increment(self):
        self.calc.add_item("Banana", 0.5, 3)
        self.calc.add_item("Banana", 0.5, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_conflict_price(self):
        self.calc.add_item("Orange", 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("Orange", 1.5, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 1.0, 1)

    def test_add_item_invalid_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Grapes", 0.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("Grapes", -1.0, 1)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Peach", 2.0, 0)
        with self.assertRaises(ValueError):
            self.calc.add_item("Peach", 2.0, -3)

    def test_add_item_wrong_types(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item("Mango", "1.0", 1)
        with self.assertRaises(TypeError):
            self.calc.add_item("Mango", 1.0, "2")

    # remove_item tests
    def test_remove_item_success(self):
        self.calc.add_item("Kiwi", 1.2, 1)
        self.calc.remove_item("Kiwi")
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("Nonexistent")

    def test_remove_item_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    # get_subtotal tests
    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_get_subtotal_value(self):
        self.calc.add_item("Item1", 2.0, 3)
        self.calc.add_item("Item2", 1.5, 2)
        subtotal = self.calc.get_subtotal()
        self.assertAlmostEqual(subtotal, 2.0 * 3 + 1.5 * 2)

    # apply_discount tests
    def test_apply_discount_value(self):
        discounted = self.calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(discounted, 80.0)

    def test_apply_discount_invalid_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_invalid_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, 1.5)

    def test_apply_discount_wrong_types(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100", 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, "0.1")

    # calculate_shipping tests
    def test_calculate_shipping_free(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertEqual(shipping, 0.0)

    def test_calculate_shipping_paid(self):
        shipping = self.calc.calculate_shipping(50.0)
        self.assertEqual(shipping, self.calc.shipping_cost)

    def test_calculate_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("50")

    # calculate_tax tests
    def test_calculate_tax_value(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("100")

    # calculate_total tests
    def test_calculate_total_no_discount(self):
        self.calc.add_item("A", 20.0, 3)  # subtotal 60
        total = self.calc.calculate_total()
        expected = 60.0 + self.calc.shipping_cost + 0.23 * (60.0 + self.calc.shipping_cost)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount(self):
        self.calc.add_item("B", 50.0, 2)  # subtotal 100
        total = self.calc.calculate_total(discount=0.5)
        discounted = 50.0
        shipping = 0.0 if discounted >= self.calc.free_shipping_threshold else self.calc.shipping_cost
        expected = discounted + shipping + 0.23 * (discounted + shipping)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_full_discount(self):
        self.calc.add_item("C", 30.0, 1)  # subtotal 30
        total = self.calc.calculate_total(discount=1.0)
        shipping = self.calc.shipping_cost
        expected = shipping + 0.23 * shipping
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping(self):
        self.calc.add_item("D", 200.0, 1)  # subtotal 200
        total = self.calc.calculate_total(discount=0.5)
        discounted = 100.0
        shipping = 0.0
        expected = discounted + shipping + 0.23 * (discounted + shipping)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_paid_shipping(self):
        self.calc.add_item("E", 150.0, 1)  # subtotal 150
        total = self.calc.calculate_total(discount=0.5)
        discounted = 75.0
        shipping = self.calc.shipping_cost
        expected = discounted + shipping + 0.23 * (discounted + shipping)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount(self):
        self.calc.add_item("F", 10.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.5)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount="0.2")

    # total_items test
    def test_total_items(self):
        self.calc.add_item("G", 5.0, 2)
        self.calc.add_item("H", 3.0, 4)
        self.assertEqual(self.calc.total_items(), 6)

    # clear_order test
    def test_clear_order(self):
        self.calc.add_item("I", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    # list_items test
    def test_list_items(self):
        self.calc.add_item("J", 2.0, 1)
        self.calc.add_item("K", 3.0, 1)
        self.calc.add_item("J", 2.0, 2)
        items = self.calc.list_items()
        self.assertCountEqual(items, ["J", "K"])

    # is_empty tests
    def test_is_empty_true(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_false(self):
        self.calc.add_item("L", 4.0, 1)
        self.assertFalse(self.calc.is_empty())


if __name__ == "__main__":
    unittest.main()