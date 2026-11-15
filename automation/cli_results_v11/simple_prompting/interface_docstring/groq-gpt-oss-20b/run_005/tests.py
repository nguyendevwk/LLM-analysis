import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def test_init_valid_default(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_init_valid_custom(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertTrue(calc.is_empty())

    def test_init_invalid_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    def test_init_invalid_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    def test_init_invalid_types(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    def test_add_item_valid(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.5, 2)
        self.assertEqual(calc.total_items(), 2)
        self.assertIn("Apple", calc.list_items())

    def test_add_item_merge_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Banana", 0.5, 3)
        calc.add_item("Banana", 0.5, 2)
        self.assertEqual(calc.total_items(), 5)

    def test_add_item_duplicate_name_different_price(self):
        calc = OrderCalculator()
        calc.add_item("Orange", 0.8, 1)
        with self.assertRaises(ValueError):
            calc.add_item("Orange", 1.0, 1)

    def test_add_item_invalid_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("", 1.0, 1)

    def test_add_item_invalid_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Grapes", 0.0, 1)
        with self.assertRaises(ValueError):
            calc.add_item("Grapes", -1.0, 1)

    def test_add_item_invalid_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Peach", 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item("Peach", 1.0, -2)

    def test_add_item_invalid_types(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)
        with self.assertRaises(TypeError):
            calc.add_item("Mango", "1.0", 1)
        with self.assertRaises(TypeError):
            calc.add_item("Mango", 1.0, "2")

    def test_remove_item_valid(self):
        calc = OrderCalculator()
        calc.add_item("Kiwi", 2.0, 1)
        calc.remove_item("Kiwi")
        self.assertTrue(calc.is_empty())

    def test_remove_item_nonexistent(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item("Nonexistent")

    def test_remove_item_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_valid(self):
        calc = OrderCalculator()
        calc.add_item("Item1", 10.0, 2)
        calc.add_item("Item2", 5.0, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 35.0, places=5)

    def test_get_subtotal_empty(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_valid(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0, places=5)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        result = calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(result, 50.0, places=5)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        result = calc.apply_discount(75.0, 1.0)
        self.assertAlmostEqual(result, 0.0, places=5)

    def test_apply_discount_invalid_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, -0.1)
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, 1.5)

    def test_apply_discount_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.2)

    def test_apply_discount_invalid_types(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount("100", 0.2)
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, "0.2")

    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(99.99), 10.0, places=5)

    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(100.0), 0.0, places=5)

    def test_calculate_shipping_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping("100")

    def test_calculate_tax_valid(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0, places=5)

    def test_calculate_tax_negative_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax("100")

    def test_calculate_total_no_discount(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item("A", 10.0, 2)
        calc.add_item("B", 5.0, 3)
        subtotal = 35.0
        shipping = 10.0
        tax = (subtotal + shipping) * 0.23
        expected_total = subtotal + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(), expected_total, places=5)

    def test_calculate_total_with_discount(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item("A", 10.0, 2)
        calc.add_item("B", 5.0, 3)
        discounted = 35.0 * 0.8
        shipping = 10.0
        tax = (discounted + shipping) * 0.23
        expected_total = discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(0.2), expected_total, places=5)

    def test_calculate_total_full_discount(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item("A", 10.0, 2)
        calc.add_item("B", 5.0, 3)
        discounted = 0.0
        shipping = 10.0
        tax = shipping * 0.23
        expected_total = discounted + shipping + tax
        self.assertAlmostEqual(calc.calculate_total(1.0), expected_total, places=5)

    def test_calculate_total_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_invalid_discount(self):
        calc = OrderCalculator()
        calc.add_item("A", 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.5)

    def test_calculate_total_invalid_type(self):
        calc = OrderCalculator()
        calc.add_item("A", 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total("0.2")

    def test_total_items(self):
        calc = OrderCalculator()
        calc.add_item("X", 1.0, 3)
        calc.add_item("Y", 2.0, 4)
        self.assertEqual(calc.total_items(), 7)

    def test_clear_order(self):
        calc = OrderCalculator()
        calc.add_item("Z", 5.0, 2)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.total_items(), 0)

    def test_list_items(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 1)
        calc.add_item("B", 2.0, 1)
        calc.add_item("A", 1.0, 2)
        items = calc.list_items()
        self.assertEqual(set(items), {"A", "B"})
        self.assertEqual(len(items), 2)

    def test_is_empty(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())
        calc.add_item("C", 3.0, 1)
        self.assertFalse(calc.is_empty())
        calc.clear_order()
        self.assertTrue(calc.is_empty())


if __name__ == "__main__":
    unittest.main()