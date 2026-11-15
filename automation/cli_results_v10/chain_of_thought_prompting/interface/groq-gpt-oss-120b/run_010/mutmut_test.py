import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_constructor_default(self):
        self.assertAlmostEqual(self.calc.calculate_tax(1), 0.23)

    def test_constructor_custom(self):
        c = OrderCalculator(tax_rate=0.1, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(c.calculate_tax(100), 10.0)
        self.assertEqual(c.calculate_shipping(40), 5.0)

    def test_constructor_negative_tax(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.05)

    def test_constructor_negative_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-10)

    def test_constructor_negative_shipping(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-1)

    def test_constructor_non_numeric(self):
        with self.assertRaises((TypeError, ValueError)):
            OrderCalculator(tax_rate='high')

    def test_add_item_normal(self):
        self.calc.add_item('Apple', 1.5, 3)
        self.assertIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.5)

    def test_add_item_default_quantity(self):
        self.calc.add_item('Banana', 2.0)
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0)

    def test_add_item_aggregate_quantity(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Apple', 1.0, 5)
        self.assertEqual(self.calc.total_items(), 7)
        self.assertAlmostEqual(self.calc.get_subtotal(), 7.0)

    def test_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Bad', -0.99, 1)

    def test_add_item_non_numeric_price(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calc.add_item('Bad', 'free', 1)

    def test_add_item_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Zero', 1.0, 0)

    def test_add_item_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Neg', 1.0, -3)

    def test_add_item_quantity_non_integer(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calc.add_item('FloatQty', 1.0, 2.5)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_non_string_name(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 1.0, 1)

    def test_add_item_large_numbers(self):
        self.calc.add_item('Big', 1000000.0, 10000)
        self.assertEqual(self.calc.total_items(), 10000)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10000000000.0)

    def test_remove_item_normal(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Banana', 2.0, 1)
        self.calc.remove_item('Apple')
        self.assertNotIn('Apple', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0)

    def test_remove_item_empty_name(self):
        with self.assertRaises((ValueError, KeyError)):
            self.calc.remove_item('')

    def test_remove_item_non_string(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(42)

    def test_remove_item_after_aggregation(self):
        self.calc.add_item('Apple', 1.0, 2)
        self.calc.add_item('Apple', 1.0, 3)
        self.calc.remove_item('Apple')
        self.assertTrue(self.calc.is_empty())

    def test_get_subtotal_multiple(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.5, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.5)

    def test_get_subtotal_after_removal(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.0, 1)
        self.calc.remove_item('A')
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0)

    def test_get_subtotal_precision(self):
        self.calc.add_item('X', 0.1, 1)
        self.calc.add_item('Y', 0.2, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.3, places=7)

    def test_apply_discount_zero(self):
        result = self.calc.apply_discount(150.0, 0.0)
        self.assertAlmostEqual(result, 150.0)

    def test_apply_discount_excessive(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, 60.0)

    def test_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -5.0)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 5.0)

    def test_apply_discount_non_numeric(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calc.apply_discount('ten', 5)

    def test_calculate_shipping_above_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_at_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_below_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(80.0), 10.0)

    def test_calculate_shipping_custom(self):
        c = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(c.calculate_shipping(30.0), 5.0)
        self.assertEqual(c.calculate_shipping(60.0), 0.0)

    def test_calculate_shipping_near_threshold(self):
        self.assertEqual(self.calc.calculate_shipping(99.999999), 10.0)

    def test_calculate_tax_standard(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_custom_rate(self):
        c = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(c.calculate_tax(200.0), 20.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-10.0)

    def test_calculate_tax_non_numeric(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calc.calculate_tax('ten')

    def test_calculate_tax_precision(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.1), 0.023, places=7)

    def test_calculate_total_no_discount_free_shipping(self):
        self.calc.add_item('A', 60.0, 2)
        total = self.calc.calculate_total()
        expected = 120.0 + self.calc.calculate_tax(120.0)
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_excessive_discount(self):
        self.calc.add_item('A', 30.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=40.0)

    def test_total_items_after_adds(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_after_removal(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.0, 3)
        self.calc.remove_item('A')
        self.assertEqual(self.calc.total_items(), 3)

    def test_total_items_after_clear(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.clear_order()
        self.assertEqual(self.calc.total_items(), 0)

    def test_total_items_aggregation(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('A', 1.0, 3)
        self.assertEqual(self.calc.total_items(), 5)

    def test_total_items_empty(self):
        self.assertEqual(self.calc.total_items(), 0)

    def test_clear_order_already_empty(self):
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_clear_order_then_reuse(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.clear_order()
        self.calc.add_item('B', 2.0, 1)
        self.assertIn('B', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 1)

    def test_list_items_after_adds(self):
        self.calc.add_item('A', 1.0, 1)
        self.calc.add_item('B', 2.0, 1)
        self.assertCountEqual(self.calc.list_items(), ['A', 'B'])

    def test_list_items_after_duplicate_add(self):
        self.calc.add_item('A', 1.0, 1)
        self.calc.add_item('A', 1.0, 2)
        self.assertEqual(self.calc.list_items(), ['A'])

    def test_list_items_after_removal(self):
        self.calc.add_item('A', 1.0, 1)
        self.calc.add_item('B', 2.0, 1)
        self.calc.remove_item('A')
        self.assertEqual(self.calc.list_items(), ['B'])

    def test_list_items_after_clear(self):
        self.calc.add_item('A', 1.0, 1)
        self.calc.clear_order()
        self.assertEqual(self.calc.list_items(), [])

    def test_list_items_type(self):
        self.calc.add_item('A', 1.0, 1)
        lst = self.calc.list_items()
        self.assertIsInstance(lst, list)
        self.assertTrue(all((isinstance(i, str) for i in lst)))

    def test_is_empty_initial(self):
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_add(self):
        self.calc.add_item('A', 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_is_empty_after_last_removal(self):
        self.calc.add_item('A', 1.0, 1)
        self.calc.remove_item('A')
        self.assertTrue(self.calc.is_empty())

    def test_is_empty_after_clear(self):
        self.calc.add_item('A', 1.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_large_order_scalability(self):
        for i in range(100):
            self.calc.add_item(f'Item{i}', 1.0, 1)
        self.assertEqual(self.calc.total_items(), 100)
        self.assertAlmostEqual(self.calc.get_subtotal(), 100.0)

    def test_floating_point_rounding_consistency(self):
        self.calc.add_item('A', 0.1, 1)
        self.calc.add_item('B', 0.2, 1)
        manual = round(0.1 + 0.2, 7)
        self.assertAlmostEqual(self.calc.get_subtotal(), manual, places=7)

    def test_custom_config_negative_discount(self):
        c = OrderCalculator(tax_rate=0.05, free_shipping_threshold=30.0, shipping_cost=7.0)
        c.add_item('A', 20.0, 1)
        with self.assertRaises(ValueError):
            c.calculate_total(discount=-5.0)

    def test_repeated_clears(self):
        self.calc.clear_order()
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())

    def test_add_after_clear(self):
        self.calc.add_item('A', 1.0, 1)
        self.calc.clear_order()
        self.calc.add_item('B', 2.0, 2)
        self.assertIn('B', self.calc.list_items())
        self.assertEqual(self.calc.total_items(), 2)

    def test_invalid_discount_type_propagation(self):
        self.calc.add_item('A', 10.0, 1)
        with self.assertRaises((TypeError, ValueError)):
            self.calc.calculate_total(discount='five')