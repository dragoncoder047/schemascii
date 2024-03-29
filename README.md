# Schemascii

[![GitHub issues](https://img.shields.io/github/issues/dragoncoder047/schemascii)](https://github.com/dragoncoder047/schemascii/issues)
![GitHub commit activity](https://img.shields.io/github/commit-activity/w/dragoncoder047/schemascii)
![GitHub last commit](https://img.shields.io/github/last-commit/dragoncoder047/schemascii)
![GitHub repo file count](https://img.shields.io/github/directory-file-count/dragoncoder047/schemascii)
![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)

A command-line tool and library for converting ASCII-art diagrams into beautiful SVG circuit schematics.

Turn this:

```none
*--BAT1+--*-------*---*
|         |       |   |
|         R1    .~~~. |
|         |     :   :-*
|         *-----:   :---+C2--*--D2+--*----------J1
|         |     :U1 :        |       |
|        R2     :555:        |       |
|         |   *-:   :-*      |       |
|         C1  | :   : |      +       C3
|         |   *-:   : C4     D1      +
|         *---* .~~~. |      |       |
|         |       |   |      |       |
*---------*-------*---*------*-------*----------J2

BAT1:5
R1:10k
R2:100k
C1:10000p
C2:10u
C3:100u
C4:10p
D1:1N4001
D2:1N4001
U1:NE555,7,6,2,1,5,3,4,8
J1:-5V
J2:GND
```

Into this:

![image](test_data/test_charge_pump.png)

And with a little CSS, this:

![image](test_data/test_charge_pump_css.png)

Works with Python 3.10+. It uses the new `match` feature in a few places. If you need to run Schemascii on an older version of Python, feel free to fork it and send me a pull request.

## Installation

Not published to PyPI yet, so you have two options:

1. Install using pip's VCS support:
  ```bash
  pip install git+https://github.com/dragoncoder047/schemascii
  ```
2. Install from source:
  ```bash
  git clone https://github.com/dragoncoder047/schemascii
  cd schemascii
  pip install .
  ```

You can also add `git+https://github.com/dragoncoder047/schemascii` to your `requirements.txt` if you have one.

## Command line usage

```usage
usage: schemascii [-h] [-V] [-o OUT_FILE] [--padding PADDING] [--scale SCALE] [--stroke_width STROKE_WIDTH] [--stroke STROKE]
                  [--label {L,V,VL}] [--nolabels]
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
  --nolabels            Turns off labels on all components, except for part numbers on ICs.
```

## Python usage

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
    label="LV",
    nolabels=False)
# these are the defaults
```

## Contributing Tips

Make sure you have an *editable* install, so you can edit and still be able to use the `schemascii` command to test it:

```bash
pip uninstall schemascii
cd path/to/your/schemascii/checkout
pip install -e .
```

<!-- https://realpython.com/pypi-publish-python-package/ -->
