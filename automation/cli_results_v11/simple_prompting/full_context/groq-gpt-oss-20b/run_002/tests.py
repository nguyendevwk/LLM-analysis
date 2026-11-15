import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    # ---------- __init__ ----------
    def test_init_default_parameters(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_init_invalid_tax_rate_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")

    def test_init_invalid_tax_rate_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_free_shipping_threshold_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    def test_init_invalid_free_shipping_threshold_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_invalid_shipping_cost_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    def test_init_invalid_shipping_cost_value(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    # ---------- add_item ----------
    def test_add_item_new(self):
        self.calc.add_item("Apple", 1.5, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]["quantity"], 2)

    def test_add_item_increment_quantity(self):
        self.calc.add_item("Banana", 0.5, 3)
        self.calc.add_item("Banana", 0.5, 2)
        self.assertEqual(self.calc.items[0]["quantity"], 5)

    def test_add_item_same_name_different_price(self):
        self.calc.add_item("Orange", 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item("Orange", 1.2, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 1.0, 1)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Grapes", -1.0, 1)

    def test_add_item_zero_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Grapes", 0, 1)

    def test_add_item_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Peach", 2.0, 0)

    def test_add_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_invalid_price_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("Pear", "1.0", 1)

    def test_add_item_invalid_quantity_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("Pear", 1.0, 1.5)

    # ---------- remove_item ----------
    def test_remove_item_existing(self):
        self.calc.add_item("Mango", 2.0, 1)
        self.calc.remove_item("Mango")
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("Nonexistent")

    def test_remove_item_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    # ---------- get_subtotal ----------
    def test_get_subtotal_normal(self):
        self.calc.add_item("Item1", 10.0, 2)
        self.calc.add_item("Item2", 5.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10.0 * 2 + 5.0 * 3)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    # ---------- apply_discount ----------
    def test_apply_discount_normal(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -0.1)

    def test_apply_discount_discount_over_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, 1.1)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.2)

    def test_apply_discount_invalid_subtotal_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100", 0.2)

    def test_apply_discount_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, "0.2")

    # ---------- calculate_shipping ----------
    def test_calculate_shipping_free(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_paid(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(40.0), 10.0)

    def test_calculate_shipping_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("50")

    # ---------- calculate_tax ----------
    def test_calculate_tax_normal(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero_amount(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_invalid_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("100")

    # ---------- calculate_total ----------
    def test_calculate_total_no_discount(self):
        self.calc.add_item("A", 30.0, 1)
        self.calc.add_item("B", 20.0, 2)
        # subtotal = 70, discount=0 => 70, shipping=10 (threshold 100), tax=70*0.23=16.1
        expected = 70.0 + 10.0 + 16.1
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    def test_calculate_total_with_discount_and_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=80.0, shipping_cost=10.0, tax_rate=0.1)
        calc.add_item("X", 50.0, 1)
        calc.add_item("Y", 30.0, 2)  # subtotal = 110
        # discount 20% => 88, shipping free (threshold 80), tax 88*0.1=8.8
        expected = 88.0 + 0.0 + 8.8
        self.assertAlmostEqual(calc.calculate_total(0.2), expected)

    def test_calculate_total_with_discount_and_paid_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=200.0, shipping_cost=15.0, tax_rate=0.05)
        calc.add_item("X", 50.0, 1)
        calc.add_item("Y", 30.0, 2)  # subtotal = 110
        # discount 20% => 88, shipping 15 (threshold 200), tax (88+15)*0.05=4.65
        expected = 88.0 + 15.0 + 4.65
        self.assertAlmostEqual(calc.calculate_total(0.2), expected)

    def test_calculate_total_full_discount(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0, tax_rate=0.2)
        calc.add_item("Item", 100.0, 1)
        # discount 100% => 0, shipping free (threshold 0), tax 0
        expected = 0.0
        self.assertAlmostEqual(calc.calculate_total(1.0), expected)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_invalid_discount_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_total("0.2")

    def test_calculate_total_invalid_discount_value(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.1)

    # ---------- total_items ----------
    def test_total_items(self):
        self.calc.add_item("A", 10.0, 3)
        self.calc.add_item("B", 5.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    # ---------- clear_order ----------
    def test_clear_order(self):
        self.calc.add_item("A", 10.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.total_items(), 0)

    # ---------- list_items ----------
    def test_list_items_unique(self):
        self.calc.add_item("Apple", 1.0, 1)
        self.calc.add_item("Banana", 0.5, 2)
        self.calc.add_item("Apple", 1.0, 3)
        items = self.calc.list_items()
        self.assertCountEqual(items, ["Apple", "Banana"])

    # ---------- is_empty ----------
    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item("Item", 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item("Item", 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    # ---------- integration: add after clear ----------
    def test_add_after_clear(self):
        self.calc.add_item("Item", 1.0, 1)
        self.calc.clear_order()
        self.calc.add_item("NewItem", 2.0, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]["name"], "NewItem")
        self.assertEqual(self.calc.items[0]["quantity"], 2)


if __name__ == "__main__":
    unittest.main()