# recipe-scale

Recipes are written for one yield, and doubling or halving one by hand
means retyping every line and getting the fractions wrong ("1 1/2 tsp"
doubled is not "2 tsp"). recipe-scale reads a plain text recipe and
rewrites every ingredient quantity by an exact factor, using Python's
`fractions.Fraction` so "1/3 cup" tripled comes out as "1 cup" instead of
a rounded decimal.

Only the standard library is used. No dependencies to install.

## Usage

Given `pancakes.txt`:

```
Pancakes (serves 4)
2 cups flour
1 1/2 tsp salt
1/4 cup sugar
2 eggs
1 1/4 cups milk
salt to taste
```

Scale by a plain multiplier:

```
$ python -m recipe_scale.cli pancakes.txt --factor 1.5
Pancakes (serves 4)
3 cups flour
2 1/4 tsp salt
3/8 cup sugar
3 eggs
1 7/8 cups milk
salt to taste
```

Or scale from one serving count to another:

```
$ python -m recipe_scale.cli pancakes.txt --servings 4:6
Pancakes (serves 4)
3 cups flour
2 1/4 tsp salt
3/8 cup sugar
3 eggs
1 7/8 cups milk
salt to taste
```

Read from stdin with `-` as the filename.

Lines with no leading number (titles, "salt to taste") are left alone.

## Install

```
pip install -e .
```

This installs a `recipe-scale` console script; until then, run it as a
module with `python -m recipe_scale.cli`.

## How it works

`recipe_scale/scaler.py` holds the parsing and scaling logic as pure
functions: strings and Fractions in, strings and Fractions out, no file
or console access. `recipe_scale/cli.py` is the thin layer that reads
the file, calls into scaler.py, and writes the result. Tests live in
`tests/test_scaler.py`.

## License

MIT, see LICENSE.
