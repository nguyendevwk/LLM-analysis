import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_defaults(self):
        self.assertEqual(self.calc.tax_rate, 0.23)
        self.assertEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertEqual(self.calc.shipping_cost, 10.0)
        self.assertTrue(self.calc.is_empty())

    def test_init_invalid_tax_rate(self):
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=-0.1)
        with self.assertRaises(ValueError):
            OrderCalculator(tax_rate=1.1)

    def test_init_invalid_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-5.0)

    def test_init_invalid_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-2.0)

    def test_init_type_errors(self):
        with self.assertRaises(TypeError):
            OrderCalculator(tax_rate='0.23')
        with self.assertRaises(TypeError):
            OrderCalculator(free_shipping_threshold='100')
        with self.assertRaises(TypeError):
            OrderCalculator(shipping_cost='10')

    def test_add_item_typical(self):
        self.calc.add_item('apple', 1.0, 2)
        self.assertEqual(self.calc.total_items(), 2)
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0)

    def test_add_item_duplicate_same_price(self):
        self.calc.add_item('book', 10.0)
        self.calc.add_item('book', 10.0, 3)
        self.assertEqual(self.calc.total_items(), 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 40.0)

    def test_add_item_duplicate_different_price_raises(self):
        self.calc.add_item('pen', 5.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('pen', 6.0)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 5.0)

    def test_add_item_nonpositive_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('item', 0.0)
        with self.assertRaises(ValueError):
            self.calc.add_item('item', -1.0)

    def test_add_item_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('item', 5.0, 0)
        with self.assertRaises(ValueError):
            self.calc.add_item('item', 5.0, -1)

    def test_add_item_type_errors(self):
        with self.assertRaises(TypeError):
            self.calc.add_item(123, 5.0)
        with self.assertRaises(TypeError):
            self.calc.add_item('item', '5.0')
        with self.assertRaises(TypeError):
            self.calc.add_item('item', 5.0, '2')

    def test_remove_item_existing(self):
        self.calc.add_item('tool', 7.5, 2)
        self.calc.remove_item('tool')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_nonexistent(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('ghost')

    def test_remove_item_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.remove_item(42)

    def test_get_subtotal_typical(self):
        self.calc.add_item('a', 2.0, 3)
        self.calc.add_item('b', 5.0, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 11.0)

    def test_get_subtotal_empty_raises(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount_typical(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.2), 80.0)
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 0.0), 50.0)
        self.assertAlmostEqual(self.calc.apply_discount(30.0, 1.0), 0.0)

    def test_apply_discount_invalid_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-1.0, 0.1)

    def test_apply_discount_invalid_discount(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, -0.1)
        with self.assertRaises(ValueError):
            self.calc.apply_discount(100.0, 1.1)

    def test_apply_discount_type_errors(self):
        with self.assertRaises(TypeError):
            self.calc.apply_discount('100', 0.1)
        with self.assertRaises(TypeError):
            self.calc.apply_discount(100, '0.1')

    def test_calculate_shipping_free(self):
        self.calc.free_shipping_threshold = 50.0
        self.assertEqual(self.calc.calculate_shipping(50.0), 0.0)
        self.assertEqual(self.calc.calculate_shipping(100.0), 0.0)

    def test_calculate_shipping_charged(self):
        self.calc.shipping_cost = 7.5
        self.assertEqual(self.calc.calculate_shipping(49.99), 7.5)
        self.assertEqual(self.calc.calculate_shipping(0.0), 7.5)

    def test_calculate_shipping_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_shipping('10')

    def test_calculate_tax_typical(self):
        self.calc.tax_rate = 0.1
        self.assertAlmostEqual(self.calc.calculate_tax(200.0), 20.0)
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_tax_type_error(self):
        with self.assertRaises(TypeError):
            self.calc.calculate_tax('10')

    def test_calculate_total_typical(self):
        self.calc.add_item('item1', 20.0, 2)
        self.calc.add_item('item2', 30.0, 1)
        total = self.calc.calculate_total(0.1)
        self.assertAlmostEqual(total, 89.79, places=2)

    def test_calculate_total_free_shipping(self):
        self.calc.free_shipping_threshold = 50.0
        self.calc.add_item('cheap', 30.0, 2)
        total = self.calc.calculate_total(0.0)
        self.assertAlmostEqual(total, 73.8, places=2)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_calculate_total_invalid_discount(self):
        self.calc.add_item('item', 10.0)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(-0.1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(1.5)

    def test_calculate_total_type_error(self):
        self.calc.add_item('item', 5.0)
        with self.assertRaises(TypeError):
            self.calc.calculate_total('0.1')

    def test_total_items(self):
        self.assertEqual(self.calc.total_items(), 0)
        self.calc.add_item('a', 1.0, 3)
        self.calc.add_item('b', 2.0, 4)
        self.assertEqual(self.calc.total_items(), 7)

    def test_clear_order(self):
        self.calc.add_item('x', 5.0)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.list_items(), [])
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_list_items(self):
        self.calc.add_item('apple', 1.0)
        self.calc.add_item('banana', 2.0)
        self.calc.add_item('apple', 1.0, 2)
        items = set(self.calc.list_items())
        self.assertEqual(items, {'apple', 'banana'})

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('something', 1.0)
        self.assertFalse(self.calc.is_empty())
        self.calc.remove_item('something')
        self.assertTrue(self.calc.is_empty())