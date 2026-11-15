import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertEqual(calc.list_items(), [])

    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_tax_rate_zero(self):
        calc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(calc.tax_rate, 0.0)

    def test_init_tax_rate_one(self):
        calc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(calc.tax_rate, 1.0)

    def test_init_tax_rate_negative_valueerror(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)

    def test_init_tax_rate_above_one_valueerror(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_free_shipping_negative_valueerror(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_shipping_cost_negative_valueerror(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_tax_rate_string_typeerror(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.23")

    def test_init_free_shipping_none_typeerror(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_shipping_cost_list_typeerror(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[5])

    def test_add_item_first_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        self.assertEqual(calc.list_items(), ["Apple"])
        self.assertEqual(calc.total_items(), 2)

    def test_add_item_second_distinct(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.add_item("Banana", 0.5)
        self.assertEqual(set(calc.list_items()), {"Apple", "Banana"})
        self.assertEqual(calc.total_items(), 2)

    def test_add_item_same_name_price_increase_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        calc.add_item("Apple", 1.0, 3)
        self.assertEqual(calc.total_items(), 4)

    def test_add_item_default_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        self.assertEqual(calc.total_items(), 1)

    def test_add_item_quantity_one(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1)
        self.assertEqual(calc.total_items(), 1)

    def test_add_item_price_small(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 0.01, 100)
        self.assertAlmostEqual(calc.get_subtotal(), 1.0)

    def test_add_item_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 1000000)
        self.assertEqual(calc.total_items(), 1000000)

    def test_add_item_empty_name_valueerror(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("", 1.0)

    def test_add_item_name_not_string_typeerror(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item(123, 1.0)

    def test_add_item_price_nonpositive_valueerror(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 0.0)
        with self.assertRaises(ValueError):
            calc.add_item("Apple", -5.0)

    def test_add_item_price_string_typeerror(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Apple", "5")

    def test_add_item_quantity_less_than_one_valueerror(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 1.0, 0)
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 1.0, -3)

    def test_add_item_quantity_float_typeerror(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.add_item("Apple", 1.0, 2.5)

    def test_add_item_same_name_diff_price_valueerror(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        with self.assertRaises(ValueError):
            calc.add_item("Apple", 1.5)

    def test_remove_item_existing_single(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.remove_item("Apple")
        self.assertTrue(calc.is_empty())

    def test_remove_item_existing_multiple(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 5)
        calc.remove_item("Apple")
        self.assertTrue(calc.is_empty())

    def test_remove_item_nonexistent_valueerror(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item("Apple")

    def test_remove_item_name_not_string_typeerror(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.remove_item(123)

    def test_remove_item_from_empty_valueerror(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.remove_item("Apple")

    def test_get_subtotal_multiple_items(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 2)
        calc.add_item("Banana", 0.5, 4)
        self.assertAlmostEqual(calc.get_subtotal(), 2.0 + 2.0)

    def test_get_subtotal_single_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.5, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 4.5)

    def test_get_subtotal_fractional_large_qty(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 0.99, 1000)
        self.assertAlmostEqual(calc.get_subtotal(), 990.0)

    def test_get_subtotal_empty_valueerror(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_get_subtotal_after_clear_valueerror(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_apply_discount_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.0), 100.0)

    def test_apply_discount_one(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 1.0), 0.0)

    def test_apply_discount_quarter(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(100.0, 0.25), 75.0)

    def test_apply_discount_subtotal_zero(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(0.0, 0.5), 0.0)

    def test_apply_discount_large_subtotal(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.apply_discount(1e6, 0.000001), 999.999)

    def test_apply_discount_subtotal_negative_valueerror(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_negative_valueerror(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, -0.1)

    def test_apply_discount_above_one_valueerror(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.apply_discount(100.0, 1.2)

    def test_apply_discount_subtotal_string_typeerror(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount("100", 0.1)

    def test_apply_discount_discount_string_typeerror(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.apply_discount(100.0, "0.1")

    def test_calculate_shipping_free(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_charged(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(40.0), 10.0)

    def test_calculate_shipping_at_threshold_free(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_zero_subtotal_charged(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_input_string_typeerror(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_shipping("10")

    def test_calculate_shipping_negative_input(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=10.0)
        # negative treated as below threshold -> shipping cost
        self.assertEqual(calc.calculate_shipping(-10.0), 10.0)

    def test_calculate_shipping_with_custom_params(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=200.0, shipping_cost=25.0)
        self.assertEqual(calc.calculate_shipping(150.0), 25.0)
        self.assertEqual(calc.calculate_shipping(250.0), 0.0)

    def test_calculate_tax_zero(self):
        calc = OrderCalculator()
        self.assertEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_positive(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_fractional(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(33.33), 7.6659, places=4)

    def test_calculate_tax_negative_valueerror(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_tax(-1.0)

    def test_calculate_tax_amount_string_typeerror(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError):
            calc.calculate_tax("100")

    def test_calculate_tax_large_amount(self):
        calc = OrderCalculator()
        self.assertAlmostEqual(calc.calculate_tax(1e12), 2.3e11)

    def test_calculate_total_simple(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 2)
        total = calc.calculate_total()
        # subtotal 20, shipping 10, amount before tax 30, tax 6.9 => total 36.9
        self.assertAlmostEqual(total, 36.9)

    def test_calculate_total_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=20.0)
        calc.add_item("Item", 10.0, 2)  # subtotal 20 >= threshold
        total = calc.calculate_total()
        # subtotal 20, shipping 0, tax 20*0.23=4.6 => total 24.6
        self.assertAlmostEqual(total, 24.6)

    def test_calculate_total_with_discount(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 2)  # subtotal 20
        total = calc.calculate_total(discount=0.1)  # 10% off
        # discounted subtotal 18, shipping 10 (threshold 100), amount before tax 28, tax 6.44 => total 34.44
        self.assertAlmostEqual(total, 34.44)

    def test_calculate_total_default_discount(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0, 2)
        total = calc.calculate_total()
        self.assertAlmostEqual(total, 36.9)

    def test_calculate_total_discount_full(self):
        calc = OrderCalculator(free_shipping_threshold=0.0, shipping_cost=5.0)
        calc.add_item("Item", 10.0, 2)  # subtotal 20
        total = calc.calculate_total(discount=1.0)  # free
        # discounted subtotal 0, shipping threshold 0 => free shipping 0, tax 0 => total 0
        self.assertAlmostEqual(total, 0.0)

    def test_calculate_total_empty_valueerror(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_discount_negative_valueerror(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=-0.1)

    def test_calculate_total_discount_above_one_valueerror(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0)
        with self.assertRaises(ValueError):
            calc.calculate_total(discount=1.2)

    def test_calculate_total_discount_string_typeerror(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0)
        with self.assertRaises(TypeError):
            calc.calculate_total(discount="0.1")

    def test_calculate_total_after_clear_valueerror(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0)
        calc.clear_order()
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_negative_subtotal_valueerror(self):
        calc = OrderCalculator()
        calc.add_item("Item", 10.0)
        # monkey-patch internal items to cause negative subtotal
        calc._items = [{"name": "Item", "price": -10.0, "quantity": 1}]
        with self.assertRaises(ValueError):
            calc.calculate_total()

    def test_calculate_total_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item("Item", 1e6, 2)
        total = calc.calculate_total()
        # subtotal 2e6, shipping 10, tax (2e6+10)*0.23 = 460002.3, total = 2e6+10+460002.3 = 2460012.3
        self.assertAlmostEqual(total, 2460012.3)

    def test_calculate_total_tax_after_shipping(self):
        calc = OrderCalculator()
        calc.add_item("A", 20.0, 1)  # subtotal 20
        # shipping 10 (threshold 100)
        # amount before tax = 30
        # tax = 30*0.23 = 6.9
        # total = 36.9
        total = calc.calculate_total()
        # compute stepwise
        subtotal = calc.get_subtotal()
        discounted = calc.apply_discount(subtotal, 0.0)
        shipping = calc.calculate_shipping(discounted)
        tax = calc.calculate_tax(discounted + shipping)
        expected = discounted + shipping + tax
        self.assertAlmostEqual(total, expected)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_one_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0, 5)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_multiple(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 2)
        calc.add_item("B", 1.0, 3)
        calc.add_item("C", 1.0, 4)
        self.assertEqual(calc.total_items(), 9)

    def test_total_items_after_remove(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 5)
        calc.add_item("B", 1.0, 3)
        calc.remove_item("A")
        self.assertEqual(calc.total_items(), 3)

    def test_total_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 5)
        calc.clear_order()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_large_quantities(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 1000000)
        calc.add_item("B", 1.0, 2000000)
        self.assertEqual(calc.total_items(), 3000000)

    def test_total_items_return_type_int(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0, 1)
        self.assertIsInstance(calc.total_items(), int)

    def test_clear_order_normal(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)

    def test_clear_order_already_empty(self):
        calc = OrderCalculator()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_clear_order_internal_list_empty(self):
        calc = OrderCalculator()
        calc.add_item("A", 1.0)
        calc.clear_order()
        self.assertEqual(len(calc._items), 0)

    def test_clear_order_attributes_unchanged(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=7.0)
        calc.add_item("A", 1.0)
        calc.clear_order()
        self.assertEqual(calc.tax_rate, 0.05)
        self.assertEqual(calc.free_shipping_threshold, 50.0)
        self.assertEqual(calc.shipping_cost, 7.0)

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_one_item(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        self.assertEqual(calc.list_items(), ["Apple"])

    def test_list_items_multiple_distinct(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.add_item("Banana", 2.0)
        calc.add_item("Cherry", 3.0)
        self.assertEqual(set(calc.list_items()), {"Apple", "Banana", "Cherry"})

    def test_list_items_adding_same_item_again(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.add_item("Apple", 1.0)
        self.assertEqual(calc.list_items(), ["Apple"])

    def test_list_items_after_remove(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.add_item("Banana", 2.0)
        calc.remove_item("Apple")
        self.assertEqual(calc.list_items(), ["Banana"])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_return_type_list_of_str(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        result = calc.list_items()
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(x, str) for x in result))

    def test_is_empty_true(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_false_after_add(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        self.assertFalse(calc.is_empty())

    def test_is_empty_true_after_remove_last(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.remove_item("Apple")
        self.assertTrue(calc.is_empty())

    def test_is_empty_true_after_clear(self):
        calc = OrderCalculator()
        calc.add_item("Apple", 1.0)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_return_type_bool(self):
        calc = OrderCalculator()
        self.assertIsInstance(calc.is_empty(), bool)