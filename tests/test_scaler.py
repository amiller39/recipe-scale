import unittest
from fractions import Fraction

from recipe_scale.scaler import (
    format_quantity,
    parse_number,
    scale_factor,
    scale_line,
    scale_recipe,
)


class ParseNumberTests(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(parse_number("3"), Fraction(3))

    def test_simple_fraction(self):
        self.assertEqual(parse_number("1/2"), Fraction(1, 2))

    def test_mixed_number(self):
        self.assertEqual(parse_number("1 1/2"), Fraction(3, 2))

    def test_decimal(self):
        self.assertEqual(parse_number("2.5"), Fraction(5, 2))

    def test_invalid_raises(self):
        with self.assertRaises(ValueError):
            parse_number("a lot")


class FormatQuantityTests(unittest.TestCase):
    def test_whole_number(self):
        self.assertEqual(format_quantity(Fraction(4)), "4")

    def test_pure_fraction(self):
        self.assertEqual(format_quantity(Fraction(1, 3)), "1/3")

    def test_mixed_number(self):
        self.assertEqual(format_quantity(Fraction(5, 2)), "2 1/2")

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            format_quantity(Fraction(-1))


class ScaleFactorTests(unittest.TestCase):
    def test_doubling(self):
        self.assertEqual(scale_factor(4, 8), Fraction(2))

    def test_fractional_result(self):
        self.assertEqual(scale_factor(4, 6), Fraction(3, 2))

    def test_zero_current_raises(self):
        with self.assertRaises(ValueError):
            scale_factor(0, 4)

    def test_zero_target_raises(self):
        with self.assertRaises(ValueError):
            scale_factor(4, 0)


class ScaleLineTests(unittest.TestCase):
    def test_scales_leading_quantity(self):
        self.assertEqual(scale_line("2 cups flour", Fraction(3, 2)), "3 cups flour")

    def test_scales_mixed_number(self):
        self.assertEqual(scale_line("1 1/2 tsp salt", Fraction(2)), "3 tsp salt")

    def test_leaves_non_quantity_lines_alone(self):
        self.assertEqual(scale_line("salt to taste", Fraction(2)), "salt to taste")

    def test_preserves_indentation(self):
        self.assertEqual(scale_line("  2 eggs", Fraction(2)), "  4 eggs")

    def test_blank_line_unchanged(self):
        self.assertEqual(scale_line("", Fraction(2)), "")


class ScaleRecipeTests(unittest.TestCase):
    def test_scales_whole_recipe(self):
        text = "Pancakes\n2 cups flour\n1 1/2 tsp salt\nmilk to taste"
        expected = "Pancakes\n4 cups flour\n3 tsp salt\nmilk to taste"
        self.assertEqual(scale_recipe(text, Fraction(2)), expected)


if __name__ == "__main__":
    unittest.main()
