"""Scale ingredient quantities in a plain text recipe."""

from .scaler import (
    convert_leading_range,
    convert_leading_unit,
    format_quantity,
    parse_number,
    scale_factor,
    scale_line,
    scale_recipe,
)

__version__ = "0.1.0"

__all__ = [
    "convert_leading_range",
    "convert_leading_unit",
    "format_quantity",
    "parse_number",
    "scale_factor",
    "scale_line",
    "scale_recipe",
]
