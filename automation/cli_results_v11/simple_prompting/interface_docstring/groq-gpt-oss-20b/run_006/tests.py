import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    # ---------- __init__ ----------
    def test_init_valid_parameters(self):
        calc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.15)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    def test_init_invalid_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

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
            OrderCalculator(shipping_cost="10")

    # ---------- add_item ----------
    def test_add_item_new(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 2.5, 3)
        self.assertEqual(calc.total_items(), 3)
        self.assertIn("Apple", calc.list_items())

    def test_add_item_merge_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Banana", 1.0, 2)
        calc.add_item("Banana", 1.0, 3)
        self.assertEqual(calc.total_items(), 5)
        self.assertEqual(len(calc.list_items()), 1)

    def test_add_item_same_name_different_price(self):
        calc = OrderCalculator()
        calc.add_item("Orange", 1.5, 1)
        with self.assertRaises(ValueError):
            calc.add_item("Orange", 2.0, 1)

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
            calc.add_item("Pear", "1.0", 1)
        with self.assertRaises(TypeError):
            calc.add_item("Pear", 1.0, "2")

    # ---------- remove_item ----------
    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item("Mango", 3.0, 2)
        calc.remove_item("Mango")
        self.assertTrue(calc.is_empty())

    def test_remove_item_nonexistent(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item("Nonexistent")

    def test_remove_item_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    # ---------- get_subtotal ----------
    def test_get_subtotal_with_items(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 2.0, 3)   # 6.0
        calc.add_item("Banana", 1.5, 2)  # 3.0
        self.assertAlmostEqual(calc.get_subtotal(), 9.0)

    def test_get_subtotal_empty(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    # ---------- apply_discount ----------
    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(75.0, 1.0), 0.0)

    def test_apply_discount_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_invalid_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, -0.1)
        with self.assertRaises(ValueError):
            calc.apply_discount(50.0, 1.1)

    def test_apply_discount_invalid_types(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount("50", 0.1)
        with self.assertRaises(TypeError):
            calc.apply_discount(50.0, "0.1")

    # ---------- calculate_shipping ----------
    def test_calculate_shipping_free(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(120.0), 0.0)

    def test_calculate_shipping_paid(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertAlmostEqual(calc.calculate_shipping(80.0), 10.0)

    def test_calculate_shipping_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping("80")

    # ---------- calculate_tax ----------
    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.2)
        self.assertAlmostEqual(calc.calculate_tax(50.0), 10.0)

    def test_calculate_tax_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertAlmostEqual(calc.calculate_tax(50.0), 0.0)

    def test_calculate_tax_full(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertAlmostEqual(calc.calculate_tax(30.0), 30.0)

    def test_calculate_tax_negative_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax("50")

    # ---------- calculate_total ----------
    def test_calculate_total_normal(self):
        calc = OrderCalculator(tax_rate=0.23, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item("Apple", 2.5, 4)   # 10.0
        calc.add_item("Banana", 1.0, 5)  # 5.0
        # subtotal 15.0, discount 0.2 -> 12.0, shipping 10.0, tax 5.06, total 27.06
        self.assertAlmostEqual(calc.calculate_total(discount=0.2), 27.06, places=2)

    def test_calculate_total_no_discount(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item("Item", 20.0, 2)  # 40.0
        # subtotal 40.0, discount 0 -> 40.0, shipping 5.0, tax 4.5, total 49.5
        self.assertAlmostEqual(calc.calculate_total(), 49.5, places=2)

    def test_calculate_total_full_discount(self):
        calc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=30.0, shipping_cost=5.0)
        calc.add_item("Item", 10.0, 3)  # 30.0
        # subtotal 30.0, discount 1 -> 0.0, shipping 5.0, tax 0.75, total 5.75
        self.assertAlmostEqual(calc.calculate_total(discount=1.0), 5.75, places=2)

    def test_calculate_total_free_shipping(self):
        calc = OrderCalculator(tax_rate=0.2, free_shipping_threshold=50.0, shipping_cost=10.0)
        calc.add_item("Item", 25.0, 3)  # 75.0
        # subtotal 75.0, discount 0 -> 75.0, shipping 0, tax 15.0, total 90.0
        self.assertAlmostEqual(calc.calculate_total(), 90.0, places=2)

    def test_calculate_total_invalid_discount(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.1)

    def test_calculate_total_invalid_type(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount="0.2")

    def test_calculate_total_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_custom_params(self):
        calc = OrderCalculator(tax_rate=0.5, free_shipping_threshold=50.0, shipping_cost=10.0)
        calc.add_item("A", 20.0, 2)  # 40.0
        # subtotal 40.0, discount 0.5 -> 20.0, shipping 10.0, tax 15.0, total 45.0
        self.assertAlmostEqual(calc.calculate_total(discount=0.5), 45.0, places=2)

    # ---------- total_items ----------
    def test_total_items(self):
        calc = OrderCalculator()
        calc.add_item("X", 5.0, 2)
        calc.add_item("Y", 3.0, 4)
        self.assertEqual(calc.total_items(), 6)

    # ---------- clear_order ----------
    def test_clear_order(self):
        calc = OrderCalculator()
        calc.add_item("Z", 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    # ---------- list_items ----------
    def test_list_items(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 1)
        calc.add_item("B", 2.0, 2)
        calc.add_item("A", 1.0, 3)
        self.assertCountEqual(calc.list_items(), ["A", "B"])

    # ---------- is_empty ----------
    def test_is_empty_initial(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_add(self):
        calc = OrderCalculator()
        calc.add_item("Item", 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("Item", 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())


if __name__ == "__main__":
    unittest.main()