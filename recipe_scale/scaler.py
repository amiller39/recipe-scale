"""Pure functions for parsing and scaling recipe quantities.

Nothing here touches a file or the console. All input/output happens in
cli.py so these functions stay trivial to unit test: string or Fraction
in, string or Fraction out.
"""

import re
from fractions import Fraction

# Matches a leading quantity at the start of a (stripped) line, followed by
# whatever the ingredient text is. Recognizes plain integers, decimals,
# simple fractions ("1/2"), and mixed numbers ("1 1/2"). Lines with no
# leading number ("salt to taste", section headers, blank lines) don't
# match and are passed through untouched.
QUANTITY_RE = re.compile(
    r"^(?P<qty>\d+\s+\d+/\d+|\d+/\d+|\d*\.\d+|\d+)\s+(?P<rest>\S.*)$"
)

# Matches a leading range like "2-3 cloves garlic" or "1/2-3/4 cup broth".
# Range ends are limited to integers, decimals, and simple fractions --
# mixed numbers are left out because "1 1/2-2" would collide with the
# space that separates the quantity from the ingredient text.
RANGE_RE = re.compile(
    r"^(?P<lo>\d*\.\d+|\d+/\d+|\d+)-(?P<hi>\d*\.\d+|\d+/\d+|\d+)\s+(?P<rest>\S.*)$"
)


def parse_number(text):
    """Parse a quantity token ("2", "1/2", "1 1/2", "2.5") into a Fraction.

    Raises ValueError for anything that isn't one of those forms.
    """
    text = text.strip()
    parts = text.split()
    if len(parts) == 2:
        whole, frac = parts
        return Fraction(int(whole)) + Fraction(frac)
    return Fraction(text)


def format_quantity(value):
    """Render a Fraction as a mixed number string, e.g. Fraction(5, 2) -> "2 1/2"."""
    if value < 0:
        raise ValueError("quantity cannot be negative")
    whole, remainder = divmod(value.numerator, value.denominator)
    if remainder == 0:
        return str(whole)
    if whole == 0:
        return f"{remainder}/{value.denominator}"
    return f"{whole} {remainder}/{value.denominator}"


def scale_factor(current_servings, target_servings):
    """Return the Fraction to multiply quantities by to go from current to target servings."""
    current = Fraction(current_servings)
    target = Fraction(target_servings)
    if current <= 0:
        raise ValueError("current servings must be positive")
    if target <= 0:
        raise ValueError("target servings must be positive")
    return target / current


def scale_line(line, factor, convert_units=False):
    """Scale the leading quantity in one line of recipe text, if it has one."""
    stripped = line.strip()
    if not stripped:
        return line
    indent = line[: len(line) - len(line.lstrip())]

    range_match = RANGE_RE.match(stripped)
    if range_match:
        lo = parse_number(range_match.group("lo")) * factor
        hi = parse_number(range_match.group("hi")) * factor
        rest = range_match.group("rest")
        if convert_units:
            lo, hi, rest = convert_leading_range(lo, hi, rest)
        return f"{indent}{format_quantity(lo)}-{format_quantity(hi)} {rest}"

    match = QUANTITY_RE.match(stripped)
    if not match:
        return line
    quantity = parse_number(match.group("qty"))
    scaled = quantity * factor
    rest = match.group("rest")
    if convert_units:
        scaled, rest = convert_leading_unit(scaled, rest)
    return f"{indent}{format_quantity(scaled)} {rest}"


def scale_recipe(text, factor, convert_units=False):
    """Scale every quantity-bearing line in a multi-line recipe."""
    return "\n".join(
        scale_line(line, factor, convert_units=convert_units)
        for line in text.splitlines()
    )


# Volume units expressed in teaspoons, the common base for conversion.
# Spoon and cup measures only -- liquid/dry weight units (oz, g) aren't
# interchangeable without ingredient density, so they're left alone.
_UNIT_TO_TSP = {
    "tsp": Fraction(1),
    "teaspoon": Fraction(1),
    "teaspoons": Fraction(1),
    "tbsp": Fraction(3),
    "tablespoon": Fraction(3),
    "tablespoons": Fraction(3),
    "cup": Fraction(48),
    "cups": Fraction(48),
}

# Ordered largest to smallest so conversion picks the biggest unit that
# still gives a quantity of at least 1, e.g. 4 tbsp becomes 1/4 cup only
# once it reaches a full cup; otherwise it stays in tablespoons.
_UNIT_STEPS = (
    ("cup", "cups", Fraction(48)),
    ("tbsp", "tbsp", Fraction(3)),
    ("tsp", "tsp", Fraction(1)),
)


def _unit_and_tail(rest):
    """Split rest into (tsp_per_unit, tail).

    tsp_per_unit is None if the leading word of rest isn't a recognized
    volume unit, in which case tail is meaningless and should be ignored.
    """
    parts = rest.split(maxsplit=1)
    if not parts:
        return None, rest
    word = parts[0]
    tail = parts[1] if len(parts) > 1 else ""
    return _UNIT_TO_TSP.get(word.lower()), tail


def convert_leading_unit(quantity, rest):
    """Re-express quantity/rest in the most natural spoon-or-cup unit.

    rest is the ingredient text following the quantity, e.g. "tbsp butter".
    If its first word is a recognized volume unit, returns a new
    (quantity, rest) pair scaled into whichever of tsp/tbsp/cup keeps the
    number at least 1. Anything else (weights, "cloves garlic", "eggs")
    is returned unchanged.
    """
    tsp_per_unit, tail = _unit_and_tail(rest)
    if tsp_per_unit is None:
        return quantity, rest
    tsp_total = quantity * tsp_per_unit
    for singular, plural, factor in _UNIT_STEPS:
        converted = tsp_total / factor
        # tsp is the last, smallest step, so it always matches if nothing
        # bigger did -- guaranteeing the loop returns.
        if converted >= 1 or factor == 1:
            name = singular if converted == 1 else plural
            new_rest = f"{name} {tail}" if tail else name
            return converted, new_rest


def convert_leading_range(lo, hi, rest):
    """Range-aware counterpart to convert_leading_unit.

    Converts both ends of a lo-hi range into the same spoon-or-cup unit,
    picked so the smaller end reads at least 1 in that unit -- otherwise a
    range like "4-6 tsp" could come out as "1 1/3-2 tbsp", mixing a clean
    number with an awkward one.
    """
    tsp_per_unit, tail = _unit_and_tail(rest)
    if tsp_per_unit is None:
        return lo, hi, rest
    tsp_lo = lo * tsp_per_unit
    tsp_hi = hi * tsp_per_unit
    for singular, plural, factor in _UNIT_STEPS:
        converted_lo = tsp_lo / factor
        if converted_lo >= 1 or factor == 1:
            converted_hi = tsp_hi / factor
            name = singular if converted_lo == 1 and converted_hi == 1 else plural
            new_rest = f"{name} {tail}" if tail else name
            return converted_lo, converted_hi, new_rest
