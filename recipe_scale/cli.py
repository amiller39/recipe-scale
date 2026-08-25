"""Command line entry point. Reads a file, calls into scaler.py, writes stdout."""

import argparse
import sys
from fractions import Fraction

from .scaler import scale_factor, scale_recipe


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="recipe-scale",
        description="Scale ingredient quantities in a recipe text file.",
    )
    parser.add_argument(
        "recipe",
        type=argparse.FileType("r"),
        help="path to a recipe text file, or - for stdin",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--factor",
        help="multiply every quantity by this number, e.g. 1.5 or 3/2",
    )
    group.add_argument(
        "--servings",
        metavar="FROM:TO",
        help="scale from FROM servings to TO servings, e.g. 4:6",
    )
    args = parser.parse_args(argv)

    if args.factor is not None:
        try:
            factor = Fraction(args.factor)
        except (ValueError, ZeroDivisionError) as exc:
            parser.error(f"invalid --factor: {exc}")
    else:
        if ":" not in args.servings:
            parser.error("--servings must be in the form FROM:TO, e.g. 4:6")
        from_str, to_str = args.servings.split(":", 1)
        try:
            factor = scale_factor(from_str, to_str)
        except (ValueError, ZeroDivisionError) as exc:
            parser.error(str(exc))

    text = args.recipe.read()
    result = scale_recipe(text, factor)
    sys.stdout.write(result)
    if not result.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
