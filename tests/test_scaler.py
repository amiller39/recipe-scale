import unittest
from fractions import Fraction

from recipe_scale.scaler import (
    convert_leading_range,
    convert_leading_unit,
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


class ConvertLeadingUnitTests(unittest.TestCase):
    def test_tsp_rolls_up_to_tbsp(self):
        quantity, rest = convert_leading_unit(Fraction(3), "tsp salt")
        self.assertEqual(quantity, Fraction(1))
        self.assertEqual(rest, "tbsp salt")

    def test_tbsp_rolls_up_to_cup(self):
        quantity, rest = convert_leading_unit(Fraction(16), "tbsp butter")
        self.assertEqual(quantity, Fraction(1))
        self.assertEqual(rest, "cup butter")

    def test_stays_in_tsp_when_small(self):
        quantity, rest = convert_leading_unit(Fraction(2), "tsp vanilla")
        self.assertEqual(quantity, Fraction(2))
        self.assertEqual(rest, "tsp vanilla")

    def test_cup_stays_cup_when_already_largest(self):
        quantity, rest = convert_leading_unit(Fraction(2), "cups flour")
        self.assertEqual(quantity, Fraction(2))
        self.assertEqual(rest, "cups flour")

    def test_unrecognized_unit_passes_through(self):
        quantity, rest = convert_leading_unit(Fraction(3), "cloves garlic")
        self.assertEqual(quantity, Fraction(3))
        self.assertEqual(rest, "cloves garlic")

    def test_singular_at_exactly_one(self):
        quantity, rest = convert_leading_unit(Fraction(48), "tsp flour")
        self.assertEqual(quantity, Fraction(1))
        self.assertEqual(rest, "cup flour")


class ScaleLineRangeTests(unittest.TestCase):
    def test_scales_integer_range(self):
        self.assertEqual(
            scale_line("2-3 cloves garlic", Fraction(2)), "4-6 cloves garlic"
        )

    def test_scales_fraction_range(self):
        self.assertEqual(
            scale_line("1/2-3/4 cup broth", Fraction(2)), "1-1 1/2 cup broth"
        )

    def test_scales_decimal_range(self):
        self.assertEqual(
            scale_line("1.5-2 cups stock", Fraction(2)), "3-4 cups stock"
        )

    def test_preserves_indentation(self):
        self.assertEqual(scale_line("  2-3 eggs", Fraction(2)), "  4-6 eggs")

    def test_non_range_hyphen_not_mistaken_for_range(self):
        # "to-taste" isn't a quantity range; the line has no leading number.
        self.assertEqual(
            scale_line("salt to-taste", Fraction(2)), "salt to-taste"
        )


class ConvertLeadingRangeTests(unittest.TestCase):
    def test_range_rolls_up_to_tbsp(self):
        lo, hi, rest = convert_leading_range(Fraction(3), Fraction(6), "tsp salt")
        self.assertEqual(lo, Fraction(1))
        self.assertEqual(hi, Fraction(2))
        self.assertEqual(rest, "tbsp salt")

    def test_range_stays_small_unit_when_low_end_is_small(self):
        lo, hi, rest = convert_leading_range(Fraction(2), Fraction(3), "tsp vanilla")
        self.assertEqual(lo, Fraction(2))
        self.assertEqual(hi, Fraction(3))
        self.assertEqual(rest, "tsp vanilla")

    def test_range_unrecognized_unit_passes_through(self):
        lo, hi, rest = convert_leading_range(Fraction(2), Fraction(3), "cloves garlic")
        self.assertEqual(lo, Fraction(2))
        self.assertEqual(hi, Fraction(3))
        self.assertEqual(rest, "cloves garlic")


class ScaleLineRangeConvertUnitsTests(unittest.TestCase):
    def test_convert_units_on_for_range(self):
        self.assertEqual(
            scale_line("1-2 tsp vanilla", Fraction(3), convert_units=True),
            "1-2 tbsp vanilla",
        )

    def test_convert_units_off_leaves_range_in_original_unit(self):
        self.assertEqual(
            scale_line("1-2 tsp vanilla", Fraction(3)), "3-6 tsp vanilla"
        )


class ScaleLineConvertUnitsTests(unittest.TestCase):
    def test_convert_units_off_by_default(self):
        self.assertEqual(
            scale_line("1 1/2 tsp salt", Fraction(2)), "3 tsp salt"
        )

    def test_convert_units_on(self):
        self.assertEqual(
            scale_line("1 1/2 tsp salt", Fraction(2), convert_units=True),
            "1 tbsp salt",
        )

    def test_convert_units_leaves_non_units_alone(self):
        self.assertEqual(
            scale_line("2 cloves garlic", Fraction(3), convert_units=True),
            "6 cloves garlic",
        )


if __name__ == "__main__":
    unittest.main()
