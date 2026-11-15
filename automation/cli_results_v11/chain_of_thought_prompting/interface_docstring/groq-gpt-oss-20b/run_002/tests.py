import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    # 1
    def test_init_default(self):
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)

    # 2
    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.1)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 5.0)

    # 3
    def test_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    # 4
    def test_init_tax_rate_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    # 5
    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")

    # 6
    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    # 7
    def test_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")

    # 8
    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    # 9
    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    # 10
    def test_add_item_single(self):
        self.calc.add_item("Apple", 1.5)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]["quantity"], 1)

    # 11
    def test_add_item_same_name_same_price(self):
        self.calc.add_item("Apple", 1.5)
        self.calc.add_item("Apple", 1.5, quantity=2)
        self.assertEqual(self.calc.items[0]["quantity"], 3)

    # 12
    def test_add_item_same_name_different_price(self):
        self.calc.add_item("Apple", 1.5)
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 2.0)

    # 13
    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("", 1.0)

    # 14
    def test_add_item_name_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0)

    # 15
    def test_add_item_price_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 0.0)

    # 16
    def test_add_item_price_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", -1.0)

    # 17
    def test_add_item_price_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("Apple", "1.5")

    # 18
    def test_add_item_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.add_item("Apple", 1.0, quantity=0)

    # 19
    def test_add_item_quantity_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.add_item("Apple", 1.0, quantity=1.5)

    # 20
    def test_add_item_quantity_default(self):
        self.calc.add_item("Apple", 1.5)
        self.assertEqual(self.calc.items[0]["quantity"], 1)

    # 21
    def test_remove_item_existing(self):
        self.calc.add_item("Apple", 1.5)
        self.calc.remove_item("Apple")
        self.assertTrue(self.calc.is_empty())

    # 22
    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item("Banana")

    # 23
    def test_remove_item_name_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(123)

    # 24
    def test_get_subtotal_multiple_items(self):
        self.calc.add_item("Apple", 1.5, quantity=2)
        self.calc.add_item("Banana", 0.5, quantity=3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.5, places=5)

    # 25
    def test_get_subtotal_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    # 26
    def test_apply_discount_valid(self):
        result = self.calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0, places=5)

    # 27
    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.2)

    # 28
    def test_apply_discount_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)

    # 29
    def test_apply_discount_discount_over_one(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.1)

    # 30
    def test_apply_discount_subtotal_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount("100", 0.2)

    # 31
    def test_apply_discount_discount_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100.0, "0.2")

    # 32
    def test_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(90.0)
        self.assertAlmostEqual(shipping, 10.0, places=5)

    # 33
    def test_calculate_shipping_equal_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0, places=5)

    # 34
    def test_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0, places=5)

    # 35
    def test_calculate_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping("90")

    # 36
    def test_calculate_tax_valid(self):
        tax = self.calc.calculate_tax(100.0)
        self.assertAlmostEqual(tax, 23.0, places=5)

    # 37
    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    # 38
    def test_calculate_tax_wrong_type(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax("100")

    # 39
    def test_calculate_total_no_discount_subtotal_below_threshold(self):
        self.calc.add_item("Apple", 1.5, quantity=2)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 15.3, places=5)

    # 40
    def test_calculate_total_no_discount_subtotal_above_threshold(self):
        self.calc.add_item("Apple", 50.0, quantity=2)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 123.0, places=5)

    # 41
    def test_calculate_total_discount_half(self):
        self.calc.add_item("Apple", 50.0, quantity=2)
        total = self.calc.calculate_total(discount=0.5)
        self.assertAlmostEqual(total, 61.5, places=5)

    # 42
    def test_calculate_total_discount_full(self):
        self.calc.add_item("Apple", 50.0, quantity=2)
        total = self.calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 0.0, places=5)

    # 43
    def test_calculate_total_discount_full_with_high_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=200.0)
        calc.add_item("Apple", 50.0, quantity=2)
        total = calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 12.3, places=5)

    # 44
    def test_calculate_total_discount_negative(self):
        self.calc.add_item("Apple", 50.0, quantity=2)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.1)

    # 45
    def test_calculate_total_discount_over_one(self):
        self.calc.add_item("Apple", 50.0, quantity=2)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.1)

    # 46
    def test_calculate_total_discount_wrong_type(self):
        self.calc.add_item("Apple", 50.0, quantity=2)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount="0.2")

    # 47
    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    # 48
    def test_total_items_after_adding(self):
        self.calc.add_item("Apple", 1.0, quantity=2)
        self.calc.add_item("Banana", 1.0, quantity=3)
        self.assertEqual(self.calc.total_items(), 5)

    # 49
    def test_total_items_after_clearing(self):
        self.calc.add_item("Apple", 1.0, quantity=2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    # 50
    def test_clear_order_after_adding(self):
        self.calc.add_item("Apple", 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    # 51
    def test_clear_order_get_subtotal_after_clearing(self):
        self.calc.add_item("Apple", 1.0)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    # 52
    def test_clear_order_calculate_total_after_clearing(self):
        self.calc.add_item("Apple", 1.0)
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    # 53
    def test_list_items_multiple_distinct(self):
        self.calc.add_item("Apple", 1.0)
        self.calc.add_item("Banana", 1.0)
        items = sorted(self.calc.list_items())
        self.assertEqual(items, ["Apple", "Banana"])

    # 54
    def test_list_items_duplicate_item(self):
        self.calc.add_item("Apple", 1.0)
        self.calc.add_item("Apple", 1.0)
        items = self.calc.list_items()
        self.assertEqual(items, ["Apple"])

    # 55
    def test_list_items_after_clearing(self):
        self.calc.add_item("Apple", 1.0)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    # 56
    def test_is_empty_new_instance(self):
        self.assertTrue(self.calc.is_empty())

    # 57
    def test_is_empty_after_adding(self):
        self.calc.add_item("Apple", 1.0)
        self.assertFalse(self.calc.is_empty())

    # 58
    def test_is_empty_after_clearing(self):
        self.calc.add_item("Apple", 1.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    # 59
    def test_calculate_total_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item("Apple", 50.0, quantity=2)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 100.0, places=5)

    # 60
    def test_calculate_total_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item("Apple", 50.0, quantity=2)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 123.0, places=5)

    # 61
    def test_calculate_total_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item("Apple", 50.0, quantity=2)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 123.0, places=5)

    # 62
    def test_add_item_quantity_exactly_one(self):
        self.calc.add_item("Apple", 1.0)
        self.assertEqual(self.calc.items[0]["quantity"], 1)

    # 63
    def test_add_item_price_integer(self):
        self.calc.add_item("Apple", 5)
        self.assertEqual(self.calc.items[0]["price"], 5)

    # 64
    def test_add_item_large_quantity(self):
        self.calc.add_item("Apple", 1.0, quantity=1000000)
        self.assertEqual(self.calc.items[0]["quantity"], 1000000)

    # 65
    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(100.0, 0.0)
        self.assertAlmostEqual(result, 100.0, places=5)

    # 66
    def test_apply_discount_full(self):
        result = self.calc.apply_discount(100.0, 1.0)
        self.assertAlmostEqual(result, 0.0, places=5)

    # 67
    def test_calculate_shipping_exact_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0, places=5)

    # 68
    def test_calculate_shipping_just_below_threshold(self):
        shipping = self.calc.calculate_shipping(99.999)
        self.assertAlmostEqual(shipping, 10.0, places=5)

    # 69
    def test_calculate_shipping_just_above_threshold(self):
        shipping = self.calc.calculate_shipping(100.001)
        self.assertAlmostEqual(shipping, 0.0, places=5)

    # 70
    def test_calculate_tax_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0, places=5)

    # 71
    def test_calculate_tax_large_amount(self):
        tax = self.calc.calculate_tax(1e12)
        self.assertAlmostEqual(tax, 2.3e11, places=5)

    # 72
    def test_calculate_total_discount_zero_subtotal_exact_threshold(self):
        self.calc.add_item("Apple", 50.0, quantity=2)
        total = self.calc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 123.0, places=5)

    # 73
    def test_calculate_total_discount_zero_subtotal_just_below_threshold(self):
        self.calc.add_item("Apple", 33.33, quantity=3)
        total = self.calc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 135.3877, places=5)

    # 74
    def test_calculate_total_discount_zero_subtotal_just_above_threshold(self):
        self.calc.add_item("Apple", 33.34, quantity=3)
        total = self.calc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 123.0123, places=5)

    # 75
    def test_remove_item_last_item(self):
        self.calc.add_item("Apple", 1.0)
        self.calc.remove_item("Apple")
        self.assertTrue(self.calc.is_empty())

    # 76
    def test_remove_item_multiple_quantity(self):
        self.calc.add_item("Apple", 1.0, quantity=5)
        self.calc.remove_item("Apple")
        self.assertTrue(self.calc.is_empty())

    # 77
    def test_list_items_many_items(self):
        for i in range(10):
            self.calc.add_item(f"Item{i}", 1.0)
        items = sorted(self.calc.list_items())
        expected = [f"Item{i}" for i in range(10)]
        self.assertEqual(items, expected)

    # 78
    def test_total_items_many_items(self):
        self.calc.add_item("Apple", 1.0, quantity=2)
        self.calc.add_item("Banana", 1.0, quantity=3)
        self.calc.add_item("Cherry", 1.0, quantity=5)
        self.assertEqual(self.calc.total_items(), 10)

    # 79
    def test_clear_order_already_empty(self):
        try:
            self.calc.clear_order()
        except Exception as e:
            self.fail(f"clear_order raised an exception on empty order: {e}")

    # 80
    def test_add_item_name_whitespace(self):
        self.calc.add_item("  Apple  ", 1.0)
        self.assertIn("  Apple  ", self.calc.list_items())

    # 81
    def test_add_item_name_unicode(self):
        self.calc.add_item("Café", 1.0)
        self.assertIn("Café", self.calc.list_items())

    # 82
    def test_calculate_total_small_amounts(self):
        self.calc.add_item("Apple", 0.0001)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 12.300123, places=5)

    # 83
    def test_calculate_total_large_amounts(self):
        self.calc.add_item("Apple", 1e12)
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 1.23e12, places=5)

    # 84
    def test_apply_discount_small_subtotal(self):
        result = self.calc.apply_discount(0.0001, 0.2)
        self.assertAlmostEqual(result, 0.00008, places=5)

    # 85
    def test_calculate_shipping_small_subtotal(self):
        shipping = self.calc.calculate_shipping(0.0001)
        self.assertAlmostEqual(shipping, 10.0, places=5)

    # 86
    def test_calculate_tax_small_amount(self):
        tax = self.calc.calculate_tax(0.0001)
        self.assertAlmostEqual(tax, 0.000023, places=5)

    # 87
    def test_calculate_total_edge_combination_no_tax_no_shipping(self):
        calc = OrderCalculator(tax_rate=0.0, shipping_cost=0.0, free_shipping_threshold=0.0)
        calc.add_item("Apple", 10.0)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 10.0, places=5)

    # 88
    def test_calculate_total_edge_combination_full_discount(self):
        calc = OrderCalculator(tax_rate=0.0, shipping_cost=0.0, free_shipping_threshold=0.0)
        calc.add_item("Apple", 10.0)
        total = calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 0.0, places=5)

    # 89
    def test_add_item_after_clearing(self):
        self.calc.add_item("Apple", 1.0)
        self.calc.clear_order()
        self.calc.add_item("Banana", 2.0)
        self.assertIn("Banana", self.calc.list_items())
        self.assertNotIn("Apple", self.calc.list_items())

    # 90
    def test_remove_item_after_clearing(self):
        self.calc.clear_order()
        with self.assertRaises(ValueError):
            self.calc.remove_item("Apple")

    # 91
    def test_list_items_after_clearing_and_readding(self):
        self.calc.clear_order()
        self.calc.add_item("Apple", 1.0)
        self.calc.add_item("Banana", 2.0)
        items = sorted(self.calc.list_items())
        self.assertEqual(items, ["Apple", "Banana"])

    # 92
    def test_is_empty_after_clearing_and_readding(self):
        self.calc.clear_order()
        self.calc.add_item("Apple", 1.0)
        self.assertFalse(self.calc.is_empty())

    # 93
    def test_calculate_total_discount_exact_threshold(self):
        self.calc.add_item("Apple", 50.0, quantity=2)
        total = self.calc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 98.4, places=5)

    # 94
    def test_calculate_total_discount_just_below_threshold(self):
        self.calc.add_item("Apple", 33.33, quantity=3)
        total = self.calc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 110.69056, places=5)

    # 95
    def test_calculate_total_discount_just_above_threshold(self):
        self.calc.add_item("Apple", 33.34, quantity=3)
        total = self.calc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 98.40984, places=5)

    # 96
    def test_calculate_total_discount_zero_subtotal(self):
        self.calc.add_item("Apple", 0.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.0)

    # 97
    def test_calculate_total_discount_large_subtotal(self):
        self.calc.add_item("Apple", 1e12, quantity=1)
        total = self.calc.calculate_total(discount=0.5)
        self.assertAlmostEqual(total, 6.15e11, places=5)

    # 98
    def test_calculate_total_discount_small_subtotal_exact_threshold_tax_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item("Apple", 50.0, quantity=2)
        total = calc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 80.0, places=5)

    # 99
    def test_calculate_total_discount_small_subtotal_exact_threshold_shipping_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item("Apple", 50.0, quantity=2)
        total = calc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 98.4, places=5)

    # 100
    def test_calculate_total_discount_small_subtotal_exact_threshold_shipping_zero_and_tax_zero(self):
        calc = OrderCalculator(tax_rate=0.0, shipping_cost=0.0, free_shipping_threshold=0.0)
        calc.add_item("Apple", 50.0, quantity=2)
        total = calc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 80.0, places=5)

if __name__ == "__main__":
    unittest.main()