import unittest
from order_calculator import OrderCalculator

class TestOrderCalculator(unittest.TestCase):

    def test_init_defaults(self):
        calc = OrderCalculator()
        self.assertEqual(calc.tax_rate, 0.23)
        self.assertEqual(calc.free_shipping_threshold, 100.0)
        self.assertEqual(calc.shipping_cost, 10.0)

    def test_init_custom_valid(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=0.0, shipping_cost=0.0)
        self.assertEqual(calc.tax_rate, 0.0)
        self.assertEqual(calc.free_shipping_threshold, 0.0)
        self.assertEqual(calc.shipping_cost, 0.0)

    def test_init_tax_rate_int_float(self):
        calc1 = OrderCalculator(tax_rate=0)
        calc2 = OrderCalculator(tax_rate=0.07)
        self.assertEqual(calc1.tax_rate, 0.0)
        self.assertEqual(calc2.tax_rate, 0.07)

    def test_init_tax_rate_out_of_range_negative(self):
        with self.assertRaises(ValueError) as cm:
            OrderCalculator(tax_rate=-0.1)
        self.assertIn('Tax rate must be between 0.0 and 1.0', str(cm.exception))

    def test_init_tax_rate_out_of_range_over_one(self):
        with self.assertRaises(ValueError) as cm:
            OrderCalculator(tax_rate=1.1)
        self.assertIn('Tax rate must be between 0.0 and 1.0', str(cm.exception))

    def test_init_tax_rate_wrong_type_string(self):
        with self.assertRaises(TypeError) as cm:
            OrderCalculator(tax_rate='0.2')
        self.assertIn('Tax rate must be a float or int', str(cm.exception))

    def test_init_free_shipping_threshold_negative(self):
        with self.assertRaises(ValueError) as cm:
            OrderCalculator(free_shipping_threshold=-5.0)
        self.assertIn('Free shipping threshold cannot be negative', str(cm.exception))

    def test_init_free_shipping_threshold_wrong_type(self):
        with self.assertRaises(TypeError) as cm:
            OrderCalculator(free_shipping_threshold='100')
        self.assertIn('Free shipping threshold must be a float or int', str(cm.exception))

    def test_init_shipping_cost_negative(self):
        with self.assertRaises(ValueError) as cm:
            OrderCalculator(shipping_cost=-2.0)
        self.assertIn('Shipping cost cannot be negative', str(cm.exception))

    def test_init_shipping_cost_wrong_type(self):
        with self.assertRaises(TypeError) as cm:
            OrderCalculator(shipping_cost=[10])
        self.assertIn('Shipping cost must be a float or int', str(cm.exception))

    def test_init_mixed_valid_invalid(self):
        with self.assertRaises(ValueError) as cm:
            OrderCalculator(tax_rate=0.2, free_shipping_threshold=-10)
        self.assertIn('Free shipping threshold cannot be negative', str(cm.exception))

    def test_add_item_new_item(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 3)
        self.assertEqual(len(calc.items), 1)
        item = calc.items[0]
        self.assertEqual(item['name'], 'Apple')
        self.assertEqual(item['price'], 0.5)
        self.assertEqual(item['quantity'], 3)

    def test_add_item_quantity_accumulation(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 2)
        calc.add_item('Apple', 0.5, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 5)

    def test_add_item_same_name_different_price_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 1)
        with self.assertRaises(ValueError) as cm:
            calc.add_item('Apple', 0.6, 1)
        self.assertIn('Item with the same name but different price already exists', str(cm.exception))

    def test_add_item_empty_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError) as cm:
            calc.add_item('', 1.0, 1)
        self.assertIn('Item name cannot be empty', str(cm.exception))

    def test_add_item_non_string_name_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError) as cm:
            calc.add_item(123, 1.0, 1)
        self.assertIn('Item name must be a string', str(cm.exception))

    def test_add_item_price_non_positive_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError) as cm:
            calc.add_item('Apple', 0, 1)
        self.assertIn('Price must be greater than 0', str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            calc.add_item('Apple', -2.5, 1)
        self.assertIn('Price must be greater than 0', str(cm.exception))

    def test_add_item_price_wrong_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError) as cm:
            calc.add_item('Apple', '5', 1)
        self.assertIn('Price must be a number', str(cm.exception))

    def test_add_item_quantity_less_than_one_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError) as cm:
            calc.add_item('Apple', 1.0, 0)
        self.assertIn('Quantity must be at least 1', str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            calc.add_item('Apple', 1.0, -3)
        self.assertIn('Quantity must be at least 1', str(cm.exception))

    def test_add_item_quantity_wrong_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError) as cm:
            calc.add_item('Apple', 1.0, 2.0)
        self.assertIn('Quantity must be an integer', str(cm.exception))
        with self.assertRaises(TypeError) as cm:
            calc.add_item('Apple', 1.0, '2')
        self.assertIn('Quantity must be an integer', str(cm.exception))

    def test_add_item_after_removal_fresh_add(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        calc.add_item('Apple', 1.0, 2)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_add_item_large_quantity(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 10 ** 6)
        self.assertEqual(calc.items[0]['quantity'], 10 ** 6)

    def test_add_item_price_as_int(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 5, 2)
        self.assertEqual(calc.items[0]['price'], 5)
        self.assertEqual(calc.items[0]['quantity'], 2)

    def test_remove_item_existing(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 0)

    def test_remove_item_nonexistent_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError) as cm:
            calc.remove_item('Banana')
        self.assertIn("Item with name 'Banana' does not exist in the order", str(cm.exception))

    def test_remove_item_wrong_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError) as cm:
            calc.remove_item(42)
        self.assertIn('Item name must be a string', str(cm.exception))

    def test_remove_item_double_removal_raises(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        with self.assertRaises(ValueError) as cm:
            calc.remove_item('Apple')
        self.assertIn("Item with name 'Apple' does not exist in the order", str(cm.exception))

    def test_remove_item_state_consistency(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Banana', 0.5, 3)
        calc.remove_item('Apple')
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['name'], 'Banana')
        self.assertEqual(calc.total_items(), 3)

    def test_get_subtotal_normal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.5, 4)
        calc.add_item('Banana', 0.2, 10)
        expected = 0.5 * 4 + 0.2 * 10
        self.assertAlmostEqual(calc.get_subtotal(), expected)

    def test_get_subtotal_empty_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError) as cm:
            calc.get_subtotal()
        self.assertIn('Cannot calculate subtotal on empty order', str(cm.exception))

    def test_get_subtotal_floating_point(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 0.1, 3)
        self.assertAlmostEqual(calc.get_subtotal(), 0.3)

    def test_get_subtotal_large_numbers(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 10 ** 6, 10 ** 6)
        expected = 10 ** 6 * 10 ** 6
        self.assertAlmostEqual(calc.get_subtotal(), expected)

    def test_apply_discount_normal(self):
        calc = OrderCalculator()
        result = calc.apply_discount(100.0, 0.2)
        self.assertAlmostEqual(result, 80.0)

    def test_apply_discount_zero_discount(self):
        calc = OrderCalculator()
        result = calc.apply_discount(50.0, 0.0)
        self.assertAlmostEqual(result, 50.0)

    def test_apply_discount_full_discount(self):
        calc = OrderCalculator()
        result = calc.apply_discount(30.0, 1.0)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_zero_subtotal(self):
        calc = OrderCalculator()
        result = calc.apply_discount(0.0, 0.5)
        self.assertAlmostEqual(result, 0.0)

    def test_apply_discount_negative_subtotal_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError) as cm:
            calc.apply_discount(-5.0, 0.1)
        self.assertIn('Cannot apply discount on negative subtotal', str(cm.exception))

    def test_apply_discount_discount_out_of_range_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError) as cm:
            calc.apply_discount(100.0, -0.1)
        self.assertIn('Discount must be between 0.0 and 1.0', str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            calc.apply_discount(100.0, 1.2)
        self.assertIn('Discount must be between 0.0 and 1.0', str(cm.exception))

    def test_apply_discount_wrong_subtotal_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError) as cm:
            calc.apply_discount('100', 0.1)
        self.assertIn('Subtotal must be a number', str(cm.exception))

    def test_apply_discount_wrong_discount_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError) as cm:
            calc.apply_discount(100.0, '0.1')
        self.assertIn('Discount must be a number', str(cm.exception))

    def test_apply_discount_floating_point(self):
        calc = OrderCalculator()
        result = calc.apply_discount(1.0, 0.333333)
        self.assertAlmostEqual(result, 0.666667, places=6)

    def test_calculate_shipping_free_shipping(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(100.0), 0.0)
        self.assertEqual(calc.calculate_shipping(150.0), 0.0)

    def test_calculate_shipping_shipping_applies(self):
        calc = OrderCalculator(free_shipping_threshold=100.0, shipping_cost=10.0)
        self.assertEqual(calc.calculate_shipping(99.99), 10.0)
        self.assertEqual(calc.calculate_shipping(0.0), 10.0)

    def test_calculate_shipping_exact_threshold(self):
        calc = OrderCalculator(free_shipping_threshold=50.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(50.0), 0.0)

    def test_calculate_shipping_negative_input(self):
        calc = OrderCalculator(free_shipping_threshold=10.0, shipping_cost=5.0)
        self.assertEqual(calc.calculate_shipping(-5.0), 5.0)

    def test_calculate_shipping_wrong_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError) as cm:
            calc.calculate_shipping('100')
        self.assertIn('Discounted subtotal must be a number', str(cm.exception))

    def test_calculate_shipping_instance_specific(self):
        calc = OrderCalculator(tax_rate=0.2, free_shipping_threshold=200.0, shipping_cost=20.0)
        self.assertEqual(calc.calculate_shipping(200.0), 0.0)
        self.assertEqual(calc.calculate_shipping(199.99), 20.0)

    def test_calculate_tax_normal(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(50.0), 11.5)

    def test_calculate_tax_zero_amount(self):
        calc = OrderCalculator(tax_rate=0.23)
        self.assertAlmostEqual(calc.calculate_tax(0.0), 0.0)

    def test_calculate_tax_negative_amount_raises(self):
        calc = OrderCalculator(tax_rate=0.23)
        with self.assertRaises(ValueError) as cm:
            calc.calculate_tax(-10.0)
        self.assertIn('Cannot calculate tax on negative amount', str(cm.exception))

    def test_calculate_tax_wrong_type_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(TypeError) as cm:
            calc.calculate_tax('50')
        self.assertIn('Amount must be a number', str(cm.exception))

    def test_calculate_tax_custom_rate(self):
        calc = OrderCalculator(tax_rate=0.05)
        self.assertAlmostEqual(calc.calculate_tax(100.0), 5.0)

    def test_calculate_tax_floating_point(self):
        calc = OrderCalculator(tax_rate=0.1)
        self.assertAlmostEqual(calc.calculate_tax(33.333), 3.3333, places=4)

    def test_calculate_total_no_discount_shipping_applies(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Book', 20.0, 4)
        total = calc.calculate_total()
        expected = 80.0 + 10.0 + 9.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_free_shipping_after_discount(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Book', 60.0, 2)
        total = calc.calculate_total(discount=0.2)
        total = calc.calculate_total(discount=0.0)
        expected = 120.0 + 0.0 + 120.0 * 0.1
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_nonzero_discount(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=200.0, shipping_cost=10.0)
        calc.add_item('Item', 50.0, 3)
        total = calc.calculate_total(discount=0.1)
        expected = 135.0 + 10.0 + (135.0 + 10.0) * 0.1
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_empty_order_raises(self):
        calc = OrderCalculator()
        with self.assertRaises(ValueError) as cm:
            calc.calculate_total()
        self.assertIn('Cannot calculate subtotal on empty order', str(cm.exception))

    def test_calculate_total_wrong_discount_type_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(TypeError) as cm:
            calc.calculate_total('0.1')
        self.assertIn('Discount must be a number', str(cm.exception))

    def test_calculate_total_discount_out_of_range_raises(self):
        calc = OrderCalculator()
        calc.add_item('Item', 10.0, 1)
        with self.assertRaises(ValueError) as cm:
            calc.calculate_total(-0.05)
        self.assertIn('Discount must be between 0.0 and 1.0', str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            calc.calculate_total(1.5)
        self.assertIn('Discount must be between 0.0 and 1.0', str(cm.exception))

    def test_calculate_total_negative_subtotal_check(self):
        calc = OrderCalculator()
        calc.items = [{'name': 'Test', 'price': -5.0, 'quantity': 1}]
        with self.assertRaises(ValueError) as cm:
            calc.calculate_total()
        self.assertIn('Cannot calculate total on negative subtotal', str(cm.exception))

    def test_calculate_total_tax_after_shipping(self):
        calc = OrderCalculator(tax_rate=0.2, free_shipping_threshold=1000.0, shipping_cost=15.0)
        calc.add_item('Good', 50.0, 1)
        total = calc.calculate_total()
        expected = 50.0 + 15.0 + 13.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_large_numbers(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=1000000000000.0, shipping_cost=100.0)
        calc.add_item('Big', 1000000.0, 1000000.0)
        total = calc.calculate_total()
        expected = 1000000000000.0 + 0.0 + 50000000000.0
        self.assertAlmostEqual(total, expected)

    def test_calculate_total_default_arg(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Item', 20.0, 4)
        total1 = calc.calculate_total()
        total2 = calc.calculate_total(discount=0.0)
        self.assertAlmostEqual(total1, total2)

    def test_total_items_normal(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 2)
        calc.add_item('B', 2.0, 3)
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.total_items(), 0)

    def test_total_items_state_consistency_after_add_remove(self):
        calc = OrderCalculator()
        calc.add_item('X', 1.0, 4)
        calc.add_item('Y', 2.0, 5)
        self.assertEqual(calc.total_items(), 9)
        calc.remove_item('X')
        self.assertEqual(calc.total_items(), 5)

    def test_total_items_large_quantities(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 10 ** 6)
        calc.add_item('Item2', 2.0, 2 * 10 ** 6)
        self.assertEqual(calc.total_items(), 3 * 10 ** 6)

    def test_clear_order_normal(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.add_item('B', 2.0, 1)
        calc.clear_order()
        self.assertEqual(len(calc.items), 0)

    def test_clear_order_state_checks(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())
        self.assertEqual(calc.list_items(), [])
        self.assertEqual(calc.total_items(), 0)
        with self.assertRaises(ValueError):
            calc.get_subtotal()

    def test_clear_order_idempotent(self):
        calc = OrderCalculator()
        calc.clear_order()
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_list_items_distinct_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.add_item('Banana', 2.0, 1)
        calc.add_item('Cherry', 3.0, 1)
        names = set(calc.list_items())
        self.assertEqual(names, {'Apple', 'Banana', 'Cherry'})

    def test_list_items_duplicate_names(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 2)
        calc.add_item('Apple', 1.0, 3)
        calc.add_item('Banana', 2.0, 1)
        names = set(calc.list_items())
        self.assertEqual(names, {'Apple', 'Banana'})

    def test_list_items_empty(self):
        calc = OrderCalculator()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        self.assertEqual(calc.list_items(), [])

    def test_list_items_type_safety(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        result = calc.list_items()
        self.assertTrue(all((isinstance(x, str) for x in result)))
        before_len = len(calc.items)
        _ = calc.list_items()
        after_len = len(calc.items)
        self.assertEqual(before_len, after_len)

    def test_is_empty_empty(self):
        calc = OrderCalculator()
        self.assertTrue(calc.is_empty())

    def test_is_empty_nonempty(self):
        calc = OrderCalculator()
        calc.add_item('Item', 1.0, 1)
        self.assertFalse(calc.is_empty())

    def test_is_empty_state_consistency_after_add_remove(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        self.assertFalse(calc.is_empty())
        calc.remove_item('A')
        self.assertTrue(calc.is_empty())

    def test_is_empty_after_clear(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        calc.clear_order()
        self.assertTrue(calc.is_empty())

    def test_is_empty_no_side_effects(self):
        calc = OrderCalculator()
        calc.add_item('A', 1.0, 1)
        before = list(calc.items)
        calc.is_empty()
        after = list(calc.items)
        self.assertEqual(before, after)

    def test_interaction_basic_workflow(self):
        calc = OrderCalculator(tax_rate=0.1, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Book', 30.0, 2)
        calc.add_item('Pen', 5.0, 4)
        self.assertEqual(calc.total_items(), 6)
        self.assertEqual(set(calc.list_items()), {'Book', 'Pen'})
        self.assertAlmostEqual(calc.get_subtotal(), 80.0)
        total = calc.calculate_total(discount=0.1)
        expected = 72.0 + 10.0 + (72.0 + 10.0) * 0.1
        self.assertAlmostEqual(total, expected)

    def test_interaction_price_change_after_removal(self):
        calc = OrderCalculator()
        calc.add_item('Apple', 1.0, 1)
        calc.remove_item('Apple')
        calc.add_item('Apple', 2.0, 3)
        self.assertEqual(len(calc.items), 1)
        self.assertEqual(calc.items[0]['price'], 2.0)
        self.assertEqual(calc.items[0]['quantity'], 3)

    def test_interaction_exact_free_shipping_threshold(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Item', 50.0, 2)
        self.assertEqual(calc.calculate_shipping(calc.get_subtotal()), 0.0)

    def test_interaction_discount_pushes_below_threshold(self):
        calc = OrderCalculator(tax_rate=0.0, free_shipping_threshold=100.0, shipping_cost=10.0)
        calc.add_item('Item', 120.0, 1)
        self.assertEqual(calc.calculate_total(discount=0.0), 120.0)
        total = calc.calculate_total(discount=0.2)
        expected = 96.0 + 10.0
        self.assertAlmostEqual(total, expected)

    def test_interaction_custom_tax_rate(self):
        calc = OrderCalculator(tax_rate=0.05, free_shipping_threshold=1000.0, shipping_cost=5.0)
        calc.add_item('Goods', 200.0, 3)
        total = calc.calculate_total()
        expected = 600.0 + 5.0 + (600.0 + 5.0) * 0.05
        self.assertAlmostEqual(total, expected)

    def test_interaction_state_consistency_after_mutations(self):
        calc = OrderCalculator()
        seq = [('add', 'A', 1.0, 2), ('add', 'B', 2.0, 3), ('remove', 'A'), ('add', 'C', 3.0, 1), ('clear',), ('add', 'D', 4.0, 5)]
        for step in seq:
            if step[0] == 'add':
                _, name, price, qty = step
                calc.add_item(name, price, qty)
            elif step[0] == 'remove':
                _, name = step
                calc.remove_item(name)
            else:
                calc.clear_order()
            self.assertEqual(calc.total_items(), sum((item['quantity'] for item in calc.items)))
            self.assertEqual(set(calc.list_items()), {item['name'] for item in calc.items})
            self.assertEqual(calc.is_empty(), len(calc.items) == 0)
            if calc.items:
                try:
                    subtotal = calc.get_subtotal()
                    expected = sum((item['price'] * item['quantity'] for item in calc.items))
                    self.assertAlmostEqual(subtotal, expected)
                except ValueError:
                    self.fail('get_subtotal raised ValueError unexpectedly')

    def test_stress_test_many_items(self):
        calc = OrderCalculator()
        for i in range(1000):
            name = f'Item{i}'
            price = float(i % 100 + 1)
            qty = i % 10 + 1
            calc.add_item(name, price, qty)
        total_qty = sum((i % 10 + 1 for i in range(1000)))
        subtotal = sum(((i % 100 + 1.0) * (i % 10 + 1) for i in range(1000)))
        self.assertEqual(calc.total_items(), total_qty)
        self.assertAlmostEqual(calc.get_subtotal(), subtotal)
        total = calc.calculate_total()
        self.assertIsInstance(total, float)