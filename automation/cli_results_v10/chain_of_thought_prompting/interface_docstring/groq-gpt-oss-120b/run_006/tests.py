import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        oc = OrderCalculator()
        self.assertEqual(oc.tax_rate, 0.23)
        self.assertEqual(oc.free_shipping_threshold, 100.0)
        self.assertEqual(oc.shipping_cost, 10.0)
        self.assertTrue(oc.is_empty())

    def test_init_custom_valid(self):
        oc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(oc.tax_rate, 0.0)
        self.assertEqual(oc.free_shipping_threshold, 0.0)
        self.assertEqual(oc.shipping_cost, 0.0)

    def test_init_invalid_tax_negative(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.01)

    def test_init_invalid_tax_over_one(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.5)

    def test_init_invalid_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5)

    def test_init_invalid_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_init_invalid_type_tax_rate(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.2')

    def test_init_invalid_type_free_shipping_threshold(self):
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')

    def test_init_invalid_type_shipping_cost(self):
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost=None)

    def test_add_item_single_valid(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        self.assertEqual(oc.total_items(), 2)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_add_item_default_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Banana', 0.8)
        self.assertEqual(oc.total_items(), 1)
        self.assertCountEqual(oc.list_items(), ['Banana'])

    def test_add_item_merge_quantity(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5, 2)
        oc.add_item('Apple', 1.5, 3)
        self.assertEqual(oc.total_items(), 5)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_add_item_conflicting_price(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.5)
        with self.assertRaises(ValueError):
            oc.add_item('Apple', 2.0)

    def test_add_item_empty_name(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('', 1.0, 1)

    def test_add_item_zero_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Orange', 0, 1)

    def test_add_item_negative_price(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Orange', -0.5, 1)

    def test_add_item_quantity_zero(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 1.2, 0)

    def test_add_item_quantity_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.add_item('Pear', 1.2, -3)

    def test_add_item_type_name(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 1.0, 1)

    def test_add_item_type_price(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', '1.0', 1)

    def test_add_item_type_quantity_float(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', 1.0, 2.5)

    def test_add_item_type_quantity_none(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item('Apple', 1.0, None)

    def test_remove_existing_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_remove_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 2)
        oc.add_item('Banana', 0.5, 3)
        oc.remove_item('Apple')
        self.assertFalse(oc.is_empty())
        self.assertCountEqual(oc.list_items(), ['Banana'])
        self.assertEqual(oc.total_items(), 3)

    def test_remove_nonexistent_raises(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        with self.assertRaises(ValueError):
            oc.remove_item('NonExisting')

    def test_remove_from_empty_raises(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.remove_item('Anything')

    def test_remove_item_type_name(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1.0, 1)
        with self.assertRaises(TypeError):
            oc.remove_item(123)

    def test_get_subtotal_multiple_items(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2.0, 3)
        oc.add_item('Banana', 1.5, 2)
        self.assertAlmostEqual(oc.get_subtotal(), 9.0, places=5)

    def test_get_subtotal_single_item(self):
        oc = OrderCalculator()
        oc.add_item('Milk', 1.25, 1)
        self.assertAlmostEqual(oc.get_subtotal(), 1.25, places=5)

    def test_get_subtotal_empty_raises(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.get_subtotal()

    def test_apply_discount_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(100, 0.0), 100.0, places=5)

    def test_apply_discount_full(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(50, 1.0), 0.0, places=5)

    def test_apply_discount_typical(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.apply_discount(200, 0.2), 160.0, places=5)

    def test_apply_discount_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(-10, 0.1)

    def test_apply_discount_discount_negative(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, -0.01)

    def test_apply_discount_discount_over_one(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.apply_discount(100, 1.5)

    def test_apply_discount_type_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('100', 0.1)

    def test_apply_discount_type_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount(100, None)

    def test_calculate_shipping_below_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(99.99), 10.0, places=5)

    def test_calculate_shipping_at_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(100.0), 0.0, places=5)

    def test_calculate_shipping_above_threshold(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(150.0), 0.0, places=5)

    def test_calculate_shipping_zero_subtotal(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_shipping(0.0), 10.0, places=5)

    def test_calculate_shipping_negative_subtotal(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_shipping(-5.0)

    def test_calculate_shipping_type_subtotal_str(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('50')

    def test_calculate_shipping_type_subtotal_none(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping(None)

    def test_calculate_shipping_custom_always_free(self):
        oc = OrderCalculator(free_shipping_threshold=0, shipping_cost=5)
        self.assertAlmostEqual(oc.calculate_shipping(10), 0.0, places=5)

    def test_calculate_shipping_custom_threshold(self):
        oc = OrderCalculator(free_shipping_threshold=30, shipping_cost=7)
        self.assertAlmostEqual(oc.calculate_shipping(25), 7.0, places=5)
        self.assertAlmostEqual(oc.calculate_shipping(35), 0.0, places=5)

    def test_calculate_tax_zero(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(0.0), 0.0, places=5)

    def test_calculate_tax_positive_default(self):
        oc = OrderCalculator()
        self.assertAlmostEqual(oc.calculate_tax(100.0), 23.0, places=5)

    def test_calculate_tax_custom_rate(self):
        oc = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(oc.calculate_tax(50), 5.0, places=5)

    def test_calculate_tax_negative_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_tax(-1.0)

    def test_calculate_tax_type_amount(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax('100')

    def test_calculate_total_no_discount_shipping_applies(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 10.0, 2)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 36.9, places=5)

    def test_calculate_total_free_shipping(self):
        oc = OrderCalculator()
        oc.add_item('Laptop', 120.0, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 147.6, places=5)

    def test_calculate_total_discount_pushes_below_threshold(self):
        oc = OrderCalculator()
        oc.add_item('ItemA', 60.0, 2)
        total = oc.calculate_total(discount=0.25)
        self.assertAlmostEqual(total, 123.0, places=5)

    def test_calculate_total_full_discount(self):
        oc = OrderCalculator()
        oc.add_item('Free', 50, 1)
        total = oc.calculate_total(discount=1.0)
        self.assertAlmostEqual(total, 12.3, places=5)

    def test_calculate_total_custom_config(self):
        oc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50, shipping_cost=7)
        oc.add_item('Item', 45, 1)
        total = oc.calculate_total()
        self.assertAlmostEqual(total, 54.6, places=5)

    def test_calculate_total_empty_order(self):
        oc = OrderCalculator()
        with self.assertRaises(ValueError):
            oc.calculate_total()

    def test_calculate_total_invalid_discount_negative(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=-0.1)

    def test_calculate_total_invalid_discount_over_one(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        with self.assertRaises(ValueError):
            oc.calculate_total(discount=1.2)

    def test_calculate_total_invalid_discount_type(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount='0.1')

    def test_total_items_empty(self):
        oc = OrderCalculator()
        self.assertEqual(oc.total_items(), 0)

    def test_total_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2, 3)
        oc.add_item('Banana', 1, 5)
        self.assertEqual(oc.total_items(), 8)

    def test_total_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 2, 3)
        oc.add_item('Banana', 1, 5)
        oc.remove_item('Apple')
        self.assertEqual(oc.total_items(), 5)

    def test_total_items_after_multiple_adds_same_name(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 1)
        oc.add_item('A', 1, 1)
        oc.add_item('A', 1, 1)
        self.assertEqual(oc.total_items(), 3)

    def test_clear_order_populated(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Banana', 1, 3)
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)
        self.assertCountEqual(oc.list_items(), [])

    def test_clear_order_already_empty(self):
        oc = OrderCalculator()
        oc.clear_order()
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)
        self.assertCountEqual(oc.list_items(), [])

    def test_list_items_empty(self):
        oc = OrderCalculator()
        self.assertCountEqual(oc.list_items(), [])

    def test_list_items_single(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_list_items_multiple(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.add_item('Banana', 1, 1)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana'])

    def test_list_items_no_duplicates(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.add_item('Apple', 1, 2)
        self.assertCountEqual(oc.list_items(), ['Apple'])

    def test_list_items_after_removal(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.add_item('Banana', 1, 1)
        oc.remove_item('Apple')
        self.assertCountEqual(oc.list_items(), ['Banana'])

    def test_is_empty_fresh(self):
        oc = OrderCalculator()
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_adding(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        self.assertFalse(oc.is_empty())

    def test_is_empty_after_removing_last(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.remove_item('Apple')
        self.assertTrue(oc.is_empty())

    def test_is_empty_after_clear(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.clear_order()
        self.assertTrue(oc.is_empty())

    def test_interaction_add_remove_back_to_fresh(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 2)
        oc.add_item('Banana', 1, 3)
        oc.remove_item('Apple')
        oc.remove_item('Banana')
        self.assertTrue(oc.is_empty())
        self.assertEqual(oc.total_items(), 0)
        self.assertCountEqual(oc.list_items(), [])

    def test_interaction_repeated_add_same_name(self):
        oc = OrderCalculator()
        oc.add_item('A', 1, 1)
        oc.add_item('A', 1, 1)
        oc.add_item('A', 1, 1)
        self.assertEqual(len(oc.list_items()), 1)
        self.assertEqual(oc.total_items(), 3)

    def test_interaction_mix_add_remove_add(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        oc.add_item('Banana', 1, 1)
        oc.remove_item('Apple')
        oc.add_item('Apple', 1, 2)
        self.assertCountEqual(oc.list_items(), ['Apple', 'Banana'])
        self.assertEqual(oc.total_items(), 3)

    def test_type_error_add_item(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.add_item(123, 'price', 'qty')

    def test_type_error_remove_item(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        with self.assertRaises(TypeError):
            oc.remove_item(456)

    def test_type_error_apply_discount(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.apply_discount('subtotal', 'discount')

    def test_type_error_calculate_shipping(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_shipping('subtotal')

    def test_type_error_calculate_tax(self):
        oc = OrderCalculator()
        with self.assertRaises(TypeError):
            oc.calculate_tax('amount')

    def test_type_error_calculate_total(self):
        oc = OrderCalculator()
        oc.add_item('Apple', 1, 1)
        with self.assertRaises(TypeError):
            oc.calculate_total(discount='0.1')