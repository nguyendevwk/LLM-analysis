import unittest
from order_calculator import OrderCalculator


class TestOrderCalculator(unittest.TestCase):
    # __init__ tests
    def test_init_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertEqual(oc.items, [])

    def test_init_custom_valid(self):
        oc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50, shipping_cost=5.5)
        self.assertEqual(oc.tax_rate, 0.1)
        self.assertEqual(oc.free_shipping_threshold, 50)
        self.assertEqual(oc.shipping_cost, 5.5)

    def test_init_tax_rate_zero_boundary(self):
        oc = OrderCalculator(tax_rate=0.0)
        self.assertEqual(oc.tax_rate, 0.0)

    def test_init_tax_rate_one_boundary(self):
        oc = OrderCalculator(tax_rate=1.0)
        self.assertEqual(oc.tax_rate, 1.0)

    def test_init_tax_rate_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_tax_rate_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_tax_rate_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate="0.2")

    def test_init_free_shipping_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_init_free_shipping_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold=None)

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=[10])

    # add_item tests
    def test_add_item_first(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]["name"], "Apple")
        self.assertEqual(oc.items[0]["price"], 1.5)
        self.assertEqual(oc.items[0]["quantity"], 2)
        self.assertEqual(oc.total_items(), 2)

    def test_add_item_second_distinct(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Banana", 0.8, 3)
        self.assertEqual(len(oc.items), 2)
        names = {i["name"] for i in oc.items}
        self.assertSetEqual(names, {"Apple", "Banana"})
        self.assertEqual(oc.total_items(), 5)

    def test_add_item_merge_same_name_price(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Apple", 1.5, 4)
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]["quantity"], 6)

    def test_add_item_same_name_different_price_error(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        with self.assertRaises(ValueError):
            oc.add_item("Apple", 2.0, 1)

    def test_add_item_empty_name_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("", 1.0, 1)

    def test_add_item_price_zero_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Orange", 0, 1)

    def test_add_item_price_negative_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Orange", -1.2, 1)

    def test_add_item_quantity_zero_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Orange", 1.0, 0)

    def test_add_item_quantity_negative_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item("Orange", 1.0, -3)

    def test_add_item_name_wrong_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_price_wrong_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("Pear", "1.0", 1)

    def test_add_item_quantity_wrong_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item("Pear", 1.0, 1.5)

    def test_add_item_price_int_valid(self):
        oc = OrderCalculator()
        oc.add_item("Kiwi", 2, 1)
        self.assertEqual(oc.items[0]["price"], 2)

    def test_add_item_large_quantity(self):
        oc = OrderCalculator()
        oc.add_item("Gadget", 0.01, 1_000_000)
        self.assertEqual(oc.items[0]["quantity"], 1_000_000)

    def test_add_item_high_precision_price(self):
        oc = OrderCalculator()
        oc.add_item("Precise", 0.123456789, 2)
        self.assertAlmostEqual(oc.items[0]["price"], 0.123456789, places=9)

    # remove_item tests
    def test_remove_item_existing_single(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.remove_item("Apple")
        self.assertTrue(oc.is_empty())

    def test_remove_item_existing_multiple(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Banana", 0.8, 3)
        oc.remove_item("Banana")
        self.assertEqual(len(oc.items), 1)
        self.assertEqual(oc.items[0]["name"], "Apple")

    def test_remove_item_nonexistent_error(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        with self.assertRaises(ValueError):
            oc.remove_item("Cherry")

    def test_remove_item_wrong_type_error(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.remove_item(None)

    def test_remove_item_after_merge(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Apple", 1.5, 4)
        oc.remove_item("Apple")
        self.assertTrue(oc.is_empty())

    def test_remove_item_manual_malformed(self):
        oc = OrderCalculator()
        oc.items = [
            {"name": "Apple", "price": 1.0, "quantity": 1},
            {"name": "Apple", "price": 2.0, "quantity": 1},
        ]
        oc.remove_item("Apple")
        self.assertTrue(oc.is_empty())

    # get_subtotal tests
    def test_get_subtotal_single(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 3.0)

    def test_get_subtotal_multiple(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Banana", 0.8, 3)
        self.assertAlmostEqual(oc.get_subtotal(), 5.4)

    def test_get_subtotal_after_merge(self):
        oc = OrderCalculator()
        oc.add_item("Apple", 1.5, 2)
        oc.add_item("Apple", 1.5, 4)
        self.assertAlmostEqual(oc.get_subtotal(), 9.0)

    def test_get_subtotal_empty_error(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_get_subtotal_large_numbers(self):
        oc = OrderCalculator()
        oc.add_item("Expensive", 1_000_000, 1_000)
        self.assertAlmostEqual(oc.get_subtotal(), 1_000_000_000_000)

    def test