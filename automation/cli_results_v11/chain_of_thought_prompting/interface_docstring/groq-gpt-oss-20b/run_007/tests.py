import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    # 1
    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    # 2
    def test_init_custom(self):
        calc = OrderCalculator(tax_rate=0.15, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.tax_rate, 0.15)
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
    def test_init_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    # 6
    def test_init_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    # 7
    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10.0)

    # 8
    def test_init_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)

    # 9
    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5.0)

    # 10
    def test_init_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    # 11
    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")

    # 12
    def test_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=[100.0])

    # 13
    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost={"cost": 10})

    # 14
    def test_add_item_normal(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.5, 2)
        self.assertEqual(calc.total_items(), 2)

    # 15
    def test_add_item_duplicate_same_name_price(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.5, 2)
        calc.add_item("Apple", 1.5, 3)
        self.assertEqual(calc.total_items(), 5)

    # 16
    def test_add_item_same_name_different_price(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.5, 2)
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 2.0, 1)

    # 17
    def test_add_item_empty_name(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("", 1.0, 1)

    # 18
    def test_add_item_non_positive_price(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 0.0, 1)

    # 19
    def test_add_item_quantity_less_than_one(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 1.0, 0)

    # 20
    def test_add_item_negative_quantity(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 1.0, -3)

    # 21
    def test_add_item_name_not_string(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0, 1)

    # 22
    def test_add_item_price_not_float(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Apple", "1.0", 1)

    # 23
    def test_add_item_quantity_not_int(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Apple", 1.0, 1.5)

    # 24
    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        self.assertEqual(calc.total_items(), 1)

    # 25
    def test_add_item_price_as_int(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Apple", 2, 1)

    # 26
    def test_remove_item_normal(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.remove_item("Apple")
        self.assertTrue(calc.is_empty())

    # 27
    def test_remove_item_nonexistent(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item("Banana")

    # 28
    def test_remove_item_name_not_string(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    # 29
    def test_remove_item_post_removal_state(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.remove_item("Apple")
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.total_items(), 0)
        self.assertEqual(calc.list_items(), [])

    # 30
    def test_get_subtotal_normal(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.5, 2)
        calc.add_item("Banana", 0.5, 4)
        self.assertAlmostEqual(calc.get_subtotal(), 4.0)

    # 31
    def test_get_subtotal_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    # 32
    def test_get_subtotal_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    # 33
    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.2), 80.0)

    # 34
    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    # 35
    def test_apply_discount_full(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 1.0), 0.0)

    # 36
    def test_apply_discount_zero_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(0.0, 0.5), 0.0)

    # 37
    def test_apply_discount_negative_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.2)

    # 38
    def test_apply_discount_discount_negative(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(10.0, -0.1)

    # 39
    def test_apply_discount_discount_over_one(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(10.0, 1.1)

    # 40
    def test_apply_discount_non_numeric_subtotal(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount("100", 0.2)

    # 41
    def test_apply_discount_non_numeric_discount(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, "0.2")

    # 42
    def test_calculate_shipping_above_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(120.0), 0.0)

    # 43
    def test_calculate_shipping_below_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(99.99), 10.0)

    # 44
    def test_calculate_shipping_exact_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    # 45
    def test_calculate_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    # 46
    def test_calculate_shipping_shipping_cost_zero(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=0.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    # 47
    def test_calculate_shipping_negative_subtotal(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(-5.0), 10.0)

    # 48
    def test_calculate_shipping_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping("100")

    # 49
    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    # 50
    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    # 51
    def test_calculate_tax_negative_amount(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-10.0)

    # 52
    def test_calculate_tax_non_numeric(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax("100")

    # 53
    def test_calculate_total_typical(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.5, 2)
        calc.add_item("Banana", 0.5, 4)
        total = calc.calculate_total(discount=0.1)
        self.assertAlmostEqual(total, 16.728, places=3)

    # 54
    def test_calculate_total_no_discount_free_shipping_threshold_met(self):
        calc = OrderCalculator(free_shipping_threshold=30.0, shipping_cost=5.0)
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Banana", 0.5, 4)
        total = calc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total, 11.07, places=2)

    # 55
    def test_calculate_total_full_discount(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Banana", 0.5, 4)
        total = calc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 12.3, places=2)

    # 56
    def test_calculate_total_invalid_discount(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.1)

    # 57
    def test_calculate_total_non_numeric_discount(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount="0.1")

    # 58
    def test_calculate_total_empty_order(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    # 59
    def test_calculate_total_custom_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        calc.add_item("Apple", 1.0, 1)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 11.0, places=2)

    # 60
    def test_calculate_total_custom_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        calc.add_item("Apple", 1.0, 1)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 22.0, places=2)

    # 61
    def test_calculate_total_custom_free_shipping_threshold_zero(self):
        calc = OrderCalculator(free_shipping_threshold=0.0)
        calc.add_item("Apple", 1.0, 1)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 1.23, places=2)

    # 62
    def test_calculate_total_custom_shipping_cost_zero(self):
        calc = OrderCalculator(shipping_cost=0.0)
        calc.add_item("Apple", 1.0, 1)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 1.23, places=2)

    # 63
    def test_calculate_total_all_custom_parameters(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        calc.add_item("Apple", 1.5, 2)
        calc.add_item("Banana", 0.5, 4)
        total = calc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total, 9.9, places=2)

    # 64
    def test_total_items_normal(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Banana", 0.5, 4)
        self.assertEqual(calc.total_items(), 6)

    # 65
    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    # 66
    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    # 67
    def test_clear_order_after_adding(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    # 68
    def test_clear_order_total_items(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    # 69
    def test_clear_order_list_items(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    # 70
    def test_clear_order_get_subtotal(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    # 71
    def test_list_items_normal(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.add_item("Banana", 0.5, 2)
        self.assertCountEqual(calc.list_items(), ["Apple", "Banana"])

    # 72
    def test_list_items_duplicate_names(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.add_item("Apple", 1.0, 2)
        self.assertCountEqual(calc.list_items(), ["Apple"])

    # 73
    def test_list_items_after_clearing(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    # 74
    def test_is_empty_new_instance(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    # 75
    def test_is_empty_after_adding(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        self.assertFalse(calc.is_empty())

    # 76
    def test_is_empty_after_removing_only_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.remove_item("Apple")
        self.assertTrue(calc.is_empty())

    # 77
    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    # 78
    def test_integration_calculate_total_after_add_remove(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.add_item("Banana", 0.5, 4)
        calc.remove_item("Apple")
        total = calc.calculate_total(discount=0.1)
        self.assertAlmostEqual(total, 14.254, places=3)

    # 79
    def test_integration_calculate_total_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    # 80
    def test_integration_calculate_total_manual_vs_helper(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.add_item("Banana", 0.5, 4)
        subtotal = calc.get_subtotal()
        discounted = calc.apply_discount(subtotal, 0.2)
        shipping = calc.calculate_shipping(discounted)
        tax = calc.calculate_tax(discounted + shipping)
        total_manual = discounted + shipping + tax
        total_calc = calc.calculate_total(discount=0.2)
        self.assertAlmostEqual(total_manual, total_calc, places=3)

    # 81
    def test_edge_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        self.assertEqual(calc.total_items(), 1)

    # 82
    def test_edge_add_item_price_zero(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 0.0, 1)

    # 83
    def test_edge_add_item_small_price(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1e-12, 1)
        self.assertEqual(calc.total_items(), 1)

    # 84
    def test_edge_apply_discount_boundary_values(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)
        self.assertAlmostEqual(calc.apply_discount(100.0, 1.0), 0.0)

    # 85
    def test_edge_calculate_shipping_exact_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)

    # 86
    def test_edge_calculate_tax_zero_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    # 87
    def test_edge_calculate_total_boundary_discounts(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        self.assertAlmostEqual(calc.calculate_total(discount=0.0), 1.23, places=2)
        self.assertAlmostEqual(calc.calculate_total(discount=1.0), 12.3, places=2)

    # 88
    def test_type_check_add_item_price_string(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Apple", "1.0", 1)

    # 89
    def test_type_check_add_item_quantity_float(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Apple", 1.0, 1.5)

    # 90
    def test_type_check_calculate_tax_amount_list(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax([100])

    # 91
    def test_type_check_calculate_shipping_discounted_subtotal_dict(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping({"subtotal": 100})

    # 92
    def test_type_check_calculate_total_discount_string(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount="0.1")

if __name__ == "__main__":
    unittest.main()