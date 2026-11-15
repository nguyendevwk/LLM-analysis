import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = OrderCalculator()

    # 1
    def test_01_init_defaults(self):
        self.assertAlmostEqual(self.calc.tax_rate, 0.23)
        self.assertAlmostEqual(self.calc.free_shipping_threshold, 100.0)
        self.assertAlmostEqual(self.calc.shipping_cost, 10.0)

    # 2
    def test_02_init_custom_parameters(self):
        c = OrderCalculator(tax_rate=0.05, free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertAlmostEqual(c.tax_rate, 0.05)
        self.assertAlmostEqual(c.free_shipping_threshold, 50.0)
        self.assertAlmostEqual(c.shipping_cost, 5.0)

    # 3
    def test_03_init_non_numeric_tax_rate(self):
        with self.assertRaises((TypeError, ValueError)):
            OrderCalculator(tax_rate='high')

    # 4
    def test_04_init_negative_tax_rate(self):
        with self.assertRaises((TypeError, ValueError)):
            OrderCalculator(tax_rate=-0.1)

    # 5
    def test_05_init_non_numeric_free_shipping_threshold(self):
        with self.assertRaises((TypeError, ValueError)):
            OrderCalculator(free_shipping_threshold='lots')

    # 6
    def test_06_init_negative_shipping_cost(self):
        with self.assertRaises((TypeError, ValueError)):
            OrderCalculator(shipping_cost=-5.0)

    # 7
    def test_07_add_item_basic(self):
        self.calc.add_item('Apple', 1.5, 3)
        self.assertListEqual(self.calc.list_items(), ['Apple'])
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 4.5)

    # 8
    def test_08_add_item_default_quantity(self):
        self.calc.add_item('Banana', 0.8)
        self.assertListEqual(self.calc.list_items(), ['Banana'])
        self.assertEqual(self.calc.total_items(), 1)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.8)

    # 9
    def test_09_add_item_multiple_distinct(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.5, 1)
        self.calc.add_item('C', 0.5, 4)
        self.assertListEqual(self.calc.list_items(), ['A', 'B', 'C'])
        self.assertEqual(self.calc.total_items(), 7)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0*2 + 2.5*1 + 0.5*4)

    # 10
    def test_10_add_item_duplicate_name_aggregates(self):
        self.calc.add_item('Milk', 2.0, 1)
        self.calc.add_item('Milk', 2.0, 2)
        self.assertListEqual(self.calc.list_items(), ['Milk'])
        self.assertEqual(self.calc.total_items(), 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 6.0)

    # 11
    def test_11_add_item_negative_price(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Eggs', -0.5, 2)

    # 12
    def test_12_add_item_price_not_number(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calc.add_item('Eggs', 'free', 2)

    # 13
    def test_13_add_item_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Bread', 1.2, 0)

    # 14
    def test_14_add_item_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.calc.add_item('Bread', 1.2, -3)

    # 15
    def test_15_add_item_quantity_not_int(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calc.add_item('Bread', 1.2, 2.5)

    # 16
    def test_16_add_item_name_not_string(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calc.add_item(None, 1.0, 1)

    # 17
    def test_17_remove_item_existing(self):
        self.calc.add_item('Orange', 1.0, 2)
        self.calc.remove_item('Orange')
        self.assertListEqual(self.calc.list_items(), [])
        self.assertEqual(self.calc.total_items(), 0)
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    # 18
    def test_18_remove_item_one_of_several(self):
        self.calc.add_item('A', 1.0, 1)
        self.calc.add_item('B', 2.0, 2)
        self.calc.add_item('C', 3.0, 3)
        self.calc.remove_item('B')
        self.assertListEqual(self.calc.list_items(), ['A', 'C'])
        self.assertEqual(self.calc.total_items(), 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0*1 + 3.0*3)

    # 19
    def test_19_remove_item_nonexistent(self):
        with self.assertRaises(KeyError):
            self.calc.remove_item('Nonexistent')

    # 20
    def test_20_remove_item_name_not_string(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calc.remove_item(123)

    # 21
    def test_21_get_subtotal_empty(self):
        self.assertAlmostEqual(self.calc.get_subtotal(), 0.0)

    # 22
    def test_22_get_subtotal_single_item(self):
        self.calc.add_item('Item', 2.5, 4)
        self.assertAlmostEqual(self.calc.get_subtotal(), 10.0)

    # 23
    def test_23_get_subtotal_multiple_items(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.0, 3)
        self.assertAlmostEqual(self.calc.get_subtotal(), 1.0*2 + 2.0*3)

    # 24
    def test_24_get_subtotal_after_removal(self):
        self.calc.add_item('A', 1.0, 2)
        self.calc.add_item('B', 2.0, 3)
        self.calc.remove_item('A')
        self.assertAlmostEqual(self.calc.get_subtotal(), 2.0*3)

    # 25
    def test_25_apply_discount_normal(self):
        result = self.calc.apply_discount(100.0, 15.0)
        self.assertAlmostEqual(result, 85.0)

    # 26
    def test_26_apply_discount_equal(self):
        result = self.calc.apply_discount(30.0, 30.0)
        self.assertAlmostEqual(result, 0.0)

    # 27
    def test_27_apply_discount_exceeds(self):
        result = self.calc.apply_discount(20.0, 50.0)
        self.assertAlmostEqual(result, 0.0)

    # 28
    def test_28_apply_discount_negative(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(50.0, -5.0)

    # 29
    def test_29_apply_discount_non_numeric(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calc.apply_discount(50.0, 'ten')

    # 30
    def test_30_apply_discount_negative_subtotal(self):
        with self.assertRaises(ValueError):
            self.calc.apply_discount(-10.0, 5.0)

    # 31
    def test_31_calculate_shipping_below_threshold(self):
        shipping = self.calc.calculate_shipping(80.0)
        self.assertAlmostEqual(shipping, 10.0)

    # 32
    def test_32_calculate_shipping_at_threshold(self):
        shipping = self.calc.calculate_shipping(100.0)
        self.assertAlmostEqual(shipping, 0.0)

    # 33
    def test_33_calculate_shipping_above_threshold(self):
        shipping = self.calc.calculate_shipping(150.0)
        self.assertAlmostEqual(shipping, 0.0)

    # 34
    def test_34_calculate_shipping_custom_threshold_and_cost(self):
        c = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=7.5)
        self.assertAlmostEqual(c.calculate_shipping(30.0), 7.5)
        self.assertAlmostEqual(c.calculate_shipping(50.0), 0.0)
        self.assertAlmostEqual(c.calculate_shipping(70.0), 0.0)

    # 35
    def test_35_calculate_shipping_negative_subtotal(self):
        shipping = self.calc.calculate_shipping(-10.0)
        self.assertAlmostEqual(shipping, 10.0)

    # 36
    def test_36_calculate_tax_positive_amount(self):
        tax = self.calc.calculate_tax(200.0)
        self.assertAlmostEqual(tax, 46.0)

    # 37
    def test_37_calculate_tax_zero_amount(self):
        tax = self.calc.calculate_tax(0.0)
        self.assertAlmostEqual(tax, 0.0)

    # 38
    def test_38_calculate_tax_custom_rate(self):
        c = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(c.calculate_tax(100.0), 5.0)

    # 39
    def test_39_calculate_tax_negative_amount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-5.0)

    # 40
    def test_40_calculate_tax_non_numeric(self):
        with self.assertRaises((TypeError, ValueError)):
            self.calc.calculate_tax('ten')

    # 41
    def test_41_calculate_total_empty_no_discount(self):
        total = self.calc.calculate_total()
        self.assertAlmostEqual(total, 0.0)

    # 42
    def test_42_calculate_total_below_threshold_no_discount(self):
        self.calc.add_item('Item', 40.0, 2)  # subtotal 80
        subtotal = self.calc.get_subtotal()
        shipping = self.calc.calculate_shipping(subtotal)
        tax = self.calc.calculate_tax(subtotal + shipping)
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    # 43
    def test_43_calculate_total_above_threshold_no_discount(self):
        self.calc.add_item('Item', 60.0, 2)  # subtotal 120
        subtotal = self.calc.get_subtotal()
        shipping = self.calc.calculate_shipping(subtotal)
        tax = self.calc.calculate_tax(subtotal + shipping)
        expected = subtotal + shipping + tax
        self.assertAlmostEqual(self.calc.calculate_total(), expected)

    # 44
    def test_44_calculate_total_discount_keeps_free_shipping(self):
        self.calc.add_item('Item', 60.0, 2)  # 120
        total = self.calc.calculate_total(discount=10.0)  # discounted 110 >= 100
        shipping = self.calc.calculate_shipping(110.0)
        tax = self.calc.calculate_tax(110.0 + shipping)
        expected = 110.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    # 45
    def test_45_calculate_total_discount_triggers_shipping(self):
        self.calc.add_item('Item', 60.0, 2)  # 120
        total = self.calc.calculate_total(discount=30.0)  # discounted 90 < 100
        shipping = self.calc.calculate_shipping(90.0)
        tax = self.calc.calculate_tax(90.0 + shipping)
        expected = 90.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    # 46
    def test_46_calculate_total_discount_exceeds_subtotal(self):
        self.calc.add_item('Item', 20.0, 1)  # 20
        total = self.calc.calculate_total(discount=50.0)  # discounted 0
        shipping = self.calc.calculate_shipping(0.0)
        tax = self.calc.calculate_tax(0.0 + shipping)
        expected = 0.0 + shipping + tax
        self.assertAlmostEqual(total, expected)

    # 47
    def test_47_calculate_total_negative_discount(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_total(discount=-5.0)

    # 48
    def test_48_calculate_total_discount_non_numeric(self):
        with self.assertRaises((TypeError