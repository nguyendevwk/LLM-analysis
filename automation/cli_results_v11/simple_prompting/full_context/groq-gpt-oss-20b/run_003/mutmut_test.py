import unittest
from order_calculator import OrderCalculator
from decimal import Decimal
from fractions import Fraction

class TestOrderCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = OrderCalculator()

    def test_init_default(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)
        self.assertTrue(calc.is_empty())

    def test_init_invalid_tax_rate_value(self):
        for bad in [-0.1, 1.1]:
            with self.assertRaises(ValueError):
                OrderCalculator(tax_rate=bad)

    def test_init_negative_free_shipping_threshold(self):
        with self.assertRaises(ValueError):
            OrderCalculator(free_shipping_threshold=-1)

    def test_init_negative_shipping_cost(self):
        with self.assertRaises(ValueError):
            OrderCalculator(shipping_cost=-5)

    def test_add_item_new(self):
        self.calc.add_item('Apple', 1.5, 2)
        self.assertEqual(len(self.calc.items), 1)
        self.assertEqual(self.calc.items[0]['name'], 'Apple')
        self.assertEqual(self.calc.items[0]['price'], 1.5)
        self.assertEqual(self.calc.items[0]['quantity'], 2)

    def test_add_item_increment(self):
        self.calc.add_item('Banana', 0.5, 3)
        self.calc.add_item('Banana', 0.5, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_same_name_diff_price(self):
        self.calc.add_item('Orange', 1.0, 1)
        with self.assertRaises(ValueError):
            self.calc.add_item('Orange', 1.2, 1)

    def test_add_item_invalid_name_type(self):
        for bad in [123, [1], {'name': 'x'}, None, True, complex(1, 1)]:
            with self.assertRaises(TypeError):
                self.calc.add_item(bad, 1.0, 1)

    def test_add_item_empty_name(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('', 1.0, 1)

    def test_add_item_invalid_price_value(self):
        for bad in [0, -1, -0.5]:
            with self.assertRaises(ValueError):
                self.calc.add_item('Item', bad, 1)

    def test_add_item_invalid_quantity_value(self):
        for bad in [0, -1]:
            with self.assertRaises(ValueError):
                self.calc.add_item('Item', 1.0, bad)

    def test_remove_item_existing(self):
        self.calc.add_item('Grapes', 2.0, 1)
        self.calc.remove_item('Grapes')
        self.assertTrue(self.calc.is_empty())

    def test_remove_item_non_existing(self):
        with self.assertRaises(ValueError):
            self.calc.remove_item('NonExistent')

    def test_remove_item_invalid_name_type(self):
        for bad in [123, [1], {'name': 'x'}, None, True, complex(1, 1)]:
            with self.assertRaises(TypeError):
                self.calc.remove_item(bad)

    def test_get_subtotal(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.5, 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.5)

    def test_get_subtotal_empty(self):
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_apply_discount(self):
        self.assertAlmostEqual(self.calc.apply_discount(100.0, 0.2), 80.0)

    def test_apply_discount_zero(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 0.0), 50.0)

    def test_apply_discount_full(self):
        self.assertAlmostEqual(self.calc.apply_discount(50.0, 1.0), 0.0)

    def test_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 0.1)

    def test_apply_discount_invalid_discount(self):
        for bad in [-0.1, 1.1]:
            with self.assertRaises(ValueError):
                self.calc.apply_discount(100.0, bad)

    def test_calculate_shipping_free(self):
        self.assertEqual(self.calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_not_free(self):
        self.assertEqual(self.calc.calculate_shipping(50.0), 10.0)

    def test_calculate_tax(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0), 23.0)

    def test_calculate_tax_zero(self):
        self.assertAlmostEqual(self.calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    def test_calculate_total_full_discount(self):
        self.calc.add_item('Item', 40.0, 1)
        total = self.calc.calculate_total(discount=1.0)
        shipping = 10.0
        tax = shipping * 0.23
        self.assertAlmostEqual(total, shipping + tax)

    def test_calculate_total_shipping_not_free(self):
        self.calc.add_item('Item', 80.0, 1)
        total = self.calc.calculate_total(discount=0.5)
        discounted = 40.0
        shipping = 10.0
        tax = (discounted + shipping) * 0.23
        self.assertAlmostEqual(total, discounted + shipping + tax)

    def test_calculate_total_empty_order(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total()

    def test_total_items(self):
        self.calc.add_item('X', 1.0, 3)
        self.calc.add_item('Y', 2.0, 2)
        self.assertEqual(self.calc.total_items(), 5)

    def test_clear_order(self):
        self.calc.add_item('Z', 5.0, 1)
        self.calc.clear_order()
        self.assertTrue(self.calc.is_empty())
        self.assertEqual(self.calc.items, [])
        with self.assertRaises(ValueError):
            self.calc.get_subtotal()

    def test_list_items(self):
        self.calc.add_item('A', 1.0, 1)
        self.calc.add_item('B', 2.0, 1)
        self.calc.add_item('A', 1.0, 2)
        items = self.calc.list_items()
        self.assertEqual(set(items), {'A', 'B'})

    def test_list_items_empty(self):
        self.assertEqual(self.calc.list_items(), [])

    def test_is_empty(self):
        self.assertTrue(self.calc.is_empty())
        self.calc.add_item('Item', 1.0, 1)
        self.assertFalse(self.calc.is_empty())

    def test_add_item_default_quantity(self):
        self.calc.add_item('DefaultQty', 1.0)
        self.assertEqual(self.calc.total_items(), 1)

    def test_add_item_quantity_multiple(self):
        self.calc.add_item('MultiQty', 1.0, 5)
        self.assertEqual(self.calc.total_items(), 5)

    def test_add_item_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('ZeroQty', 1.0, 0)

    def test_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('NegQty', 1.0, -3)

    def test_add_item_price_zero(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('ZeroPrice', 0.0, 1)

    def test_add_item_price_negative(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('NegPrice', -1.0, 1)

    def test_remove_item_removes_all(self):
        self.calc.add_item('Dup', 1.0, 2)
        self.calc.add_item('Dup', 1.0, 3)
        self.calc.remove_item('Dup')
        self.assertTrue(self.calc.is_empty())

    def test_total_items_multiple(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.0, 3)
        self.calc.add_item('A', 1.0, 1)
        self.assertEqual(self.calc.total_items(), 6)

    def test_calculate_total_discount_out_of_range(self):
        self.calc.add_item('Item', 50.0, 1)
        for bad in [-0.1, 1.1]:
            with self.assertRaises(ValueError):
                self.calc.calculate_total(discount=bad)

    def test_calculate_total_discount_negative(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-0.5)

    def test_calculate_total_discount_over_one(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=1.5)

    def test_calculate_total_discount_type_string(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount='0.5')

    def test_calculate_total_discount_type_list(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=[0.5])

    def test_calculate_total_discount_type_dict(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount={'disc': 0.5})

    def test_calculate_total_discount_type_none(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=None)

    def test_calculate_total_discount_type_complex(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=complex(1, 1))

    def test_calculate_total_discount_type_tuple(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=(0.5,))

    def test_calculate_total_discount_type_set(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount={0.5})

    def test_calculate_total_discount_type_frozenset(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=frozenset([0.5]))

    def test_calculate_total_discount_type_bytes(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=b'0.5')

    def test_calculate_total_discount_type_bytearray(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=bytearray(b'0.5'))

    def test_calculate_total_discount_type_memoryview(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=memoryview(b'0.5'))

    def test_calculate_total_discount_type_decimal(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=Decimal('0.5'))

    def test_calculate_total_discount_type_fraction(self):
        self.calc.add_item('Item', 50.0, 1)
        with self.assertRaises(TypeError):
            self.calc.calculate_total(discount=Fraction(1, 2))
if __name__ == '__main__':
    unittest.main()