import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    # 1
    def test_init_default_values(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertEqual(oc.items, [])

    # 2
    def test_init_custom_values(self):
        oc = OrderCalculator(tax_rate=0.5, free_shipping_threshold=50, shipping_cost=5)
        self.assertEqual(oc.tax_rate, 0.5)
        self.assertEqual(oc.free_shipping_threshold, 50)
        self.assertEqual(oc.shipping_cost, 5)

    # 3
    def test_init_tax_rate_bounds_0(self):
        oc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(oc.tax_rate, 0.0)

    # 4
    def test_init_tax_rate_bounds_1(self):
        oc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(oc.tax_rate, 1.0)

    # 5
    def test_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    # 6
    def test_init_tax_rate_over(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    # 7
    def test_init_free_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    # 8
    def test_init_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    # 9
    def test_init_type_error_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="high")

    # 10
    def test_init_type_error_free_shipping(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    # 11
    def test_init_type_error_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[])

    # 12
    def test_add_item_basic(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 1)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]["quantity"], 1)

    # 13
    def test_add_item_multiple_distinct(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 1)
        oc.add_item("Banana", 0.5, 2)
        self.assertEqual(len(oc.items), 2)

    # 14
    def test_add_item_increment(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 1)
        oc.add_item("Apple", 1.0, 2)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]["quantity"], 3)

    # 15
    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("", 1.0, 1)

    # 16
    def test_add_item_zero_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 0, 1)

    # 17
    def test_add_item_negative_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Apple", -1, 1)

    # 18
    def test_add_item_zero_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 1.0, 0)

    # 19
    def test_add_item_negative_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 1.0, -1)

    # 20
    def test_add_item_same_name_diff_price(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 1.5, 1)

    # 21
    def test_add_item_type_error_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    # 22
    def test_add_item_type_error_price(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("Apple", "free", 1)

    # 23
    def test_add_item_type_error_quantity(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("Apple", 1.0, 2.5)

    # 24
    def test_remove_item_existing(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 1)
        oc.remove_item("Apple")
        self.assertEqual(len(oc.items), 0)

    # 25
    def test_remove_item_nonexistent(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item("Orange")

    # 26
    def test_remove_item_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    # 27
    def test_get_subtotal_normal(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 2)
        oc.add_item("Banana", 0.5, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 3.5, places=7)

    # 28
    def test_get_subtotal_empty(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    # 29
    def test_apply_discount_normal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0.2), 80.0, places=7)

    # 30
    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0.0), 100.0, places=7)

    # 31
    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 1.0), 0.0, places=7)

    # 32
    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10, 0.2)

    # 33
    def test_apply_discount_discount_out_of_range(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, -0.1)
        with self.assertRaises(ValueError):
            oc.apply_discount(100, 1.1)

    # 34
    def test_apply_discount_type_error_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount("100", 0.2)

    # 35
    def test_apply_discount_type_error_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100, "0.2")

    # 36
    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(50), 10.0)

    # 37
    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(100), 0.0)

    # 38
    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(150), 0.0)

    # 39
    def test_calculate_shipping_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping("50")

    # 40
    def test_calculate_tax_normal(self):
        oc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(oc.calculate_tax(100), 23.0, places=7)

    # 41
    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0), 0.0, places=7)

    # 42
    def test_calculate_tax_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-5)

    # 43
    def test_calculate_tax_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax("100")

    # 44
    def test_calculate_total_no_discount_no_shipping(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 10, 12)  # subtotal 120
        total = oc.calculate_total()
        expected_tax = 120 * 0.23
        self.assertAlmostEqual(total, 120 + 0 + expected_tax, places=7)

    # 45
    def test_calculate_total_with_discount_and_shipping(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 10, 8)  # subtotal 80
        total = oc.calculate_total(discount=0.5)
        discounted = 80 * 0.5
        shipping = 10
        tax = (discounted + shipping) * 0.23
        self.assertAlmostEqual(total, discounted + shipping + tax, places=7)

    # 46
    def test_calculate_total_full_discount(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 10, 8)  # subtotal 80
        total = oc.calculate_total(discount=1.0)
        discounted = 0
        shipping = 10
        tax = shipping * 0.23
        self.assertAlmostEqual(total, discounted + shipping + tax, places=7)

    # 47
    def test_calculate_total_free_shipping(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 10, 12)  # subtotal 120
        total = oc.calculate_total(discount=0.5)
        discounted = 120 * 0.5
        shipping = 0
        tax = discounted * 0.23
        self.assertAlmostEqual(total, discounted + shipping + tax, places=7)

    # 48
    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    # 49
    def test_calculate_total_invalid_discount(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 10, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=1.5)

    # 50
    def test_calculate_total_type_error(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 10, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount="10%")

    # 51
    def test_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1, 3)
        oc.add_item("Banana", 1, 2)
        self.assertEqual(oc.total_items(), 5)

    # 52
    def test_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    # 53
    def test_clear_order_resets(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    # 54
    def test_list_items_unique(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1, 1)
        oc.add_item("Apple", 1, 2)
        self.assertEqual(set(oc.list_items()), {"Apple"})

    # 55
    def test_list_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1, 1)
        oc.add_item("Banana", 1, 1)
        oc.add_item("Apple", 1, 1)
        self.assertEqual(set(oc.list_items()), {"Apple", "Banana"})

    # 56
    def test_list_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.list_items(), [])

    # 57
    def test_is_empty_initial(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    # 58
    def test_is_empty_after_add(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1, 1)
        self.assertFalse(oc.is_empty())

    # 59
    def test_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    # 60
    def test_integration_full_flow(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 10, 2)   # 20
        oc.add_item("Banana", 5, 4)   # 20
        oc.add_item("Cherry", 2, 10)  # 20
        subtotal = oc.get_subtotal()
        self.assertAlmostEqual(subtotal, 60, places=7)
        total = oc.calculate_total(discount=0.1)
        discounted = 60 * 0.9
        shipping = 0 if discounted >= 100 else 10
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected, places=7)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    # 61
    def test_integration_shipping_threshold_boundary(self):
        oc = OrderCalculator(free_shipping_threshold=100, shipping_cost=10)
        oc.add_item("Apple", 50, 1)  # 50
        oc.add_item("Banana", 50, 1)  # 50
        subtotal = oc.get_subtotal()
        self.assertAlmostEqual(subtotal, 100, places=7)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 100 + 0 + 23, places=7)

    # 62
    def test_integration_tax_rate_boundary(self):
        oc = OrderCalculator(tax_rate=0.0)
        oc.add_item("Apple", 10, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 10, places=7)
        oc2 = OrderCalculator(tax_rate=1.0)
        oc2.add_item("Apple", 10, 1)
        total2 = oc2.calculate_total()
        self.assertAlmostEqual(total2, 20, places=7)

    # 63
    def test_add_item_duplicate_name_different_price(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0, 1)
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 1.5, 1)

    # 64
    def test_calculate_shipping_negative_subtotal(self):
        oc = OrderCalculator()
        self.assertEqual(oc.calculate_shipping(-20), 10.0)

    # 65
    def test_apply_discount_negative_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, -0.2)

    # 66
    def test_calculate_total_discount_zero(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 10, 1)
        total = oc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 10 + 10 + 2.3, places=7)

    # 67
    def test_calculate_total_discount_one(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 10, 1)
        total = oc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 10 + 2.3, places=7)

    # 68
    def test_whitespace_name(self):
        oc = OrderCalculator()
        oc.add_item("   ", 1.0, 1)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]["name"], "   ")

    # 69
    def test_zero_quantity_default(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.0)
        self.assertEqual(oc.items[0]["quantity"], 1)

    # 70
    def test_negative_quantity_default(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 1.0, quantity=-1)

    # 71
    def test_zero_price_default(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 0)

    # 72
    def test_remove_all_items_one_by_one(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1, 1)
        oc.add_item("Banana", 1, 1)
        oc.remove_item("Apple")
        oc.remove_item("Banana")
        self.assertTrue(oc.is_empty())

    # 73
    def test_readd_after_removal(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1, 1)
        oc.remove_item("Apple")
        oc.add_item("Apple", 1, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 74
    def test_list_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1, 1)
        oc.add_item("Banana", 1, 1)
        oc.remove_item("Apple")
        self.assertEqual(set(oc.list_items()), {"Banana"})

    # 75
    def test_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1, 3)
        oc.add_item("Banana", 1, 2)
        oc.remove_item("Apple")
        self.assertEqual(oc.total_items(), 2)

    # 76
    def test_clear_order_already_empty(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    # 77
    def test_extremely_small_discount(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 10, 1)
        total = oc.calculate_total(discount=1e-10)
        expected = 10 + 10 + 2.3
        self.assertAlmostEqual(total, expected, places=5)

    # 78
    def test_extremely_large_discount(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 10, 1)
        total = oc.calculate_total(discount=0.999999)
        discounted = 10 * 0.000001
        shipping = 10
        tax = (discounted + shipping) * 0.23
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected, places=5)

    # 79
    def test_tax_rate_zero(self):
        oc = OrderCalculator(tax_rate=0.0)
        oc.add_item("Apple", 10, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 10 + 10, places=7)

    # 80
    def test_tax_rate_one(self):
        oc = OrderCalculator(tax_rate=1.0)
        oc.add_item("Apple", 10, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 10 + 10 + 20, places=7)

    # 81
    def test_free_shipping_threshold_zero(self):
        oc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10)
        oc.add_item("Apple", 10, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 10 + 0 + 2.3, places=7)

    # 82
    def test_shipping_cost_zero(self):
        oc = OrderCalculator(shipping_cost=0.0, free_shipping_threshold=100)
        oc.add_item("Apple", 10, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 10 + 0 + 2.3, places=7)

    # 83
    def test_negative_shipping_cost_after_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5, free_shipping_threshold=0)

    # 84
    def test_mixed_type_inputs_numeric_parameters(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.23")
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold="100")
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost="10")

    # 85
    def test_add_item_price_int_quantity_float(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("Apple", 5, 2.5)

    # 86
    def test_add_item_price_int_quantity_int_dup1(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 87
    def test_add_item_price_float_quantity_int_dup2(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5.0, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 88
    def test_add_item_price_int_quantity_int_dup3(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 89
    def test_add_item_price_float_quantity_int_dup4(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5.0, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 90
    def test_add_item_price_int_quantity_int_dup5(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 91
    def test_add_item_price_float_quantity_int_dup6(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5.0, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 92
    def test_add_item_price_int_quantity_int_dup7(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 93
    def test_add_item_price_float_quantity_int_dup8(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5.0, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 94
    def test_add_item_price_int_quantity_int_dup9(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 95
    def test_add_item_price_float_quantity_int_dup10(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5.0, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 96
    def test_add_item_price_int_quantity_int_dup11(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 97
    def test_add_item_price_float_quantity_int_dup12(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5.0, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 98
    def test_add_item_price_int_quantity_int_dup13(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 99
    def test_add_item_price_float_quantity_int_dup14(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5.0, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

    # 100
    def test_add_item_price_int_quantity_int_dup15(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 5, 2)
        self.assertEqual(oc.items[0]["quantity"], 2)

if __name__ == "__main__":
    unittest.main()