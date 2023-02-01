# Schemascii

[![GitHub issues](https://img.shields.io/github/issues/dragoncoder047/schemascii)](https://github.com/dragoncoder047/schemascii/issues)
![GitHub commit activity](https://img.shields.io/github/commit-activity/w/dragoncoder047/schemascii)
![GitHub last commit](https://img.shields.io/github/last-commit/dragoncoder047/schemascii)
![GitHub repo file count](https://img.shields.io/github/directory-file-count/dragoncoder047/schemascii)
![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)

A command-line tool and library for converting ASCII-art diagrams into beautiful SVG circuit schematics.

Works with Python 3.10+. It uses the new `match` feature in a few places. If you need to run Schemascii on an older version of Python, feel free to fork it and send me a pull request.

Command line usage:

```usage
usage: schemascii [-h] [-V] [-o OUT_FILE] [--padding PADDING] [--scale SCALE] [--stroke_width STROKE_WIDTH] [--stroke STROKE]
                  [--label {L,V,VL}]
                  in_file

Render ASCII-art schematics into SVG.

positional arguments:
  in_file               File to process.

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -o OUT_FILE, --out OUT_FILE
                        Output SVG file. (default input file plus .svg)
  --padding PADDING     Amount of padding to add on the edges.
  --scale SCALE         Scale at which to enlarge the entire diagram by.
  --stroke_width STROKE_WIDTH
                        Width of the lines
  --stroke STROKE       Color of the lines.
  --label {L,V,VL}      Component label style (L=include label, V=include value, VL=both)
```

Python usage example:

```python
import schemascii

# Render a file
svg = schemascii.render("my_circuit.txt")

# Render a string
text = ... # this is the text of your file
svg = schemascii.render("<string>", text)

# Provide options
svg = schemascii.render("my_circuit.txt",
    padding=10,
    scale=15,
    stroke_width=2,
    stroke="black",
    label="LV")
# these are the defaults
```

<!-- https://realpython.com/pypi-publish-python-package/ -->
