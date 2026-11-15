import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    # __init__ tests
    def test_init_default_parameters(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_invalid_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_invalid_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_invalid_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2)

    def test_init_type_errors(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    # add_item tests
    def test_add_item_success(self):
        self.calc.add_item("Apple", 1.5, 3)
        self.assertEqual(self.calc.total_items(), 3)
        self.assertIn("Apple", self.calc.list_items())

    def test_add_item_merge_quantity_same_name_price(self):
        self.calc.add_item("Banana", 0.5, 2)
        self.calc.add_item("Banana", 0.5, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_different_price_same_name(self):
        self.calc.add_item("Orange", 0.8, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("Orange", 1.0, 1)

    def test_add_item_invalid_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 1.0, 1)

    def test_add_item_invalid_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Grapes", 0.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("Grapes", -1.0, 1)

    def test_add_item_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Peach", 1.0, 0)
        with self.assertRaises(ValueError):
            self.calc.add_item("Peach", 1.0, -2)

    def test_add_item_type_errors(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            self.calc.add_item("Mango", "1.0", 1)
        with self.assertRaises(TypeError):
            self.calc.add_item("Mango", 1.0, "2")

    # remove_item tests
    def test_remove_item_success(self):
        self.calc.add_item("Kiwi", 2.0, 1)
        self.calc.remove_item("Kiwi")
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_not_found(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("Nonexistent")

    def test_remove_item_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    # get_subtotal tests
    def test_get_subtotal_success(self):
        self.calc.add_item("ItemA", 10.0, 2)
        self.calc.add_item("ItemB", 5.0, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 25.0)

    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    # apply_discount tests
    def test_apply_discount_success(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_invalid_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_invalid_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(10.0, 1.1)

    def test_apply_discount_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100", 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, "0.1")

    # calculate_shipping tests
    def test_calculate_shipping_free(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_paid(self):
        self.assertEqual(self.calc.calculate_shipping(50.0), 10.0)

    def test_calculate_shipping_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("50")

    # calculate_tax tests
    def test_calculate_tax_success(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("100")

    # calculate_total tests
    def test_calculate_total_no_discount(self):
        self.calc.add_item("Item1", 50.0, 1)
        self.calc.add_item("Item2", 30.0, 2)
        total = self.calc.calculate_total()
        expected = 110.0 + 10.0 + 0.23 * 120.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_and_free_shipping(self):
        self.calc.add_item("Item1", 50.0, 1)
        self.calc.add_item("Item2", 30.0, 2)
        total = self.calc.calculate_total(discount=0.2)
        expected = 88.0 + 0.0 + 0.23 * 88.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount_and_paid_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=200.0, shipping_cost=15.0)
        calc.add_item("Item1", 50.0, 1)
        calc.add_item("Item2", 30.0, 2)
        total = calc.calculate_total(discount=0.0)
        expected = 110.0 + 15.0 + 0.23 * 125.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_invalid_discount(self):
        self.calc.add_item("Item", 10.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.1)

    def test_calculate_total_type_error(self):
        self.calc.add_item("Item", 10.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount="0.2")

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    # total_items tests
    def test_total_items(self):
        self.calc.add_item("A", 1.0, 2)
        self.calc.add_item("B", 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    # clear_order tests
    def test_clear_order(self):
        self.calc.add_item("C", 5.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    # list_items tests
    def test_list_items(self):
        self.calc.add_item("D", 1.0, 1)
        self.calc.add_item("E", 2.0, 2)
        self.calc.add_item("D", 1.0, 3)
        items = self.calc.list_items()
        self.assertCountEqual(items, ["D", "E"])

    # is_empty tests
    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item("F", 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item("G", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())


if __name__ == "__main__":
    unittest.main()