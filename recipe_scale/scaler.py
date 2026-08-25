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


def scale_line(line, factor):
    """Scale the leading quantity in one line of recipe text, if it has one."""
    stripped = line.strip()
    if not stripped:
        return line
    indent = line[: len(line) - len(line.lstrip())]
    match = QUANTITY_RE.match(stripped)
    if not match:
        return line
    quantity = parse_number(match.group("qty"))
    scaled = quantity * factor
    return f"{indent}{format_quantity(scaled)} {match.group('rest')}"


def scale_recipe(text, factor):
    """Scale every quantity-bearing line in a multi-line recipe."""
    return "\n".join(scale_line(line, factor) for line in text.splitlines())
