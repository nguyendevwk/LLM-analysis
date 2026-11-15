import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def test_init_valid(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.items, [])

    def test_init_tax_rate_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.23")

    def test_init_tax_rate_value_error_low(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_value_error_high(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_free_shipping_threshold_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    def test_init_free_shipping_threshold_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_shipping_cost_type_error(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    def test_init_shipping_cost_value_error(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_add_item_normal(self):
        calc = OrderCalculator()
        calc.add_item("apple", 1.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]["name"], "apple")
        self.assertEqual(calc.items[0]["price"], 1.0)
        self.assertEqual(calc.items[0]["quantity"], 2)

    def test_add_item_merge_same_name_price(self):
        calc = OrderCalculator()
        calc.add_item("book", 10.0, 1)
        calc.add_item("book", 10.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]["quantity"], 4)

    def test_add_item_empty_name_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("", 5.0)

    def test_add_item_price_zero_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("pen", 0.0)

    def test_add_item_price_negative_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("pen", -1.0)

    def test_add_item_quantity_less_than_one_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("pen", 1.0, 0)

    def test_add_item_quantity_not_int_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("pen", 1.0, 2.5)

    def test_add_item_price_not_number_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("pen", "5.0")

    def test_add_item_name_not_string_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 5.0)

    def test_add_item_same_name_different_price_error(self):
        calc = OrderCalculator()
        calc.add_item("hat", 20.0)
        with self.assertRaises(ValueError):
            calc.add_item("hat", 25.0)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item("shirt", 15.0)
        calc.remove_item("shirt")
        self.assertTrue(calc.is_empty())

    def test_remove_item_not_existing_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item("nonexistent")

    def test_remove_item_name_not_string_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_get_subtotal_normal(self):
        calc = OrderCalculator()
        calc.add_item("a", 2.0, 3)
        calc.add_item("b", 4.0, 1)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0*3 + 4.0*1)

    def test_get_subtotal_empty_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(30.0, 1.0), 0.0)

    def test_apply_discount_invalid_type(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount("100", 0.1)

    def test_apply_discount_discount_out_of_range_low(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)

    def test_apply_discount_discount_out_of_range_high(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.1)

    def test_apply_discount_negative_subtotal_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_calculate_shipping_free(self):
        calc = OrderCalculator(free_shipping_threshold=50.0)
        self.assertEqual(calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_cost(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=7.5)
        self.assertEqual(calc.calculate_shipping(40.0), 7.5)

    def test_calculate_shipping_at_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping("50")

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(calc.calculate_tax(200.0), 20.0)

    def test_calculate_tax_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-5.0)

    def test_calculate_tax_type_error(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax("100")

    def test_calculate_total_basic(self):
        calc = OrderCalculator()
        calc.add_item("item1", 10.0, 2)
        total = calc.calculate_total()
        expected = 20.0 + 10.0 + (20.0+10.0)*0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_with_discount(self):
        calc = OrderCalculator()
        calc.add_item("item1", 50.0, 1)
        total = calc.calculate_total(0.1)
        expected = 50*0.9 + 10.0 + (50*0.9 + 10.0)*0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=30.0)
        calc.add_item("item1", 20.0, 2)
        total = calc.calculate_total()
        expected = 40.0 + 0.0 + 40.0*0.23
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_empty_order_error(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_invalid_discount_type(self):
        calc = OrderCalculator()
        calc.add_item("a", 10.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total("0.1")

    def test_calculate_total_invalid_discount_range_low(self):
        calc = OrderCalculator()
        calc.add_item("a", 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(-0.1)

    def test_calculate_total_invalid_discount_range_high(self):
        calc = OrderCalculator()
        calc.add_item("a", 10.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(1.1)

    def test_total_items(self):
        calc = OrderCalculator()
        calc.add_item("a", 1.0, 2)
        calc.add_item("b", 2.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order(self):
        calc = OrderCalculator()
        calc.add_item("x", 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])

    def test_list_items(self):
        calc = OrderCalculator()
        calc.add_item("apple", 1.0, 1)
        calc.add_item("banana", 2.0, 1)
        calc.add_item("apple", 1.0, 2)
        names = calc.list_items()
        self.assertEqual(set(names), {"apple", "banana"})
        self.assertEqual(len(names), 2)

    def test_is_empty_true(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false(self):
        calc = OrderCalculator()
        calc.add_item("item", 1.0, 1)
        self.assertFalse(calc.is_empty())