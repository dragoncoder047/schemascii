# Schemascii Format

## Wires

Wires are simply lines drawn using dashes or pipe symbols.

A corner or wire join (drawn as a dot) is notated by an asterisk (`*`)

Crossed wires (not joined) are notated with a `)` or simply broken to allow the other wire to pass. Examples:

```txt
Crossed:         Joined:       Corner:     Crossed:      Crossed:    Dangling ends:
    |               |            |            |             |              |
 ---)---         ---*---         *---      -------       ---|---           |---
    |               |                         |             |
```

### Wire Tags

Wire tags look like `<name=` or `=name>` and are attached to specific wires. All wires tagged with the same `name` belong to the same net. Currently this only affects rendering.

## Components

Components are notated with their reference designator: one or more uppercase letters followed by an ID (a nonnegative integer) optionally followed by a suffix (which can be composed of uppercase letters and underscores)

* They are always written horizontally even if the terminals are on the top and bottom.
* IDs are allowed to be duplicated and result in the same component values.
* Components can be padded (horizontally and vertically) `#`'s to make them bigger and control the shape (for components that support shapes).

Examples:

* `C33`
* `Q1001`
* `L5`
* `F3#`
* `####D7#####`
* `R333A`
* ```txt
      # ######
       # ########
    ----# #########
        # #U1G1#####----
    ----# #########
       # ########
      # ######
  ```

Components' terminals are annotated with "flags", which are other punctuation characters and lowercase letters touching them.

* Polarized components (caps, diodes, etc.) use a `+` for one terminal to indicate the polarity,
* Transistors use 3 lowercase letters to indicate collector/emitter/base (for bipolar transistors) or source/gate/drain (for field-effect transistors).

## Annotations

### Text Annotations

You can include arbitrary text in the diagram by `[enclosing it in brackets like this]`.

### Line Annotations

To outline certain areas with lines (that are not wires), you can draw lines with colons/tildes (for straight lines), and periods/single quotes (for corners) like so:

```txt
   .~~~~~~~~~~.
   :  .~~~    :
   :  :       :
   :  :       :
   :  :    .~~'~~~~.
   :  '~~~~'       :
   '~~~~~~~~~~~~~~~'
```

Lines are allowed to cross wires. They are crossed the same way that wires cross each other.

## Data

Every drawing is required to have a "data section" appended after it. The data section contains mappings of values to tell Schemascii how to render each component (e.g. how thick to make the lines, what the components' values are, etc.)

The data section is separated from the actual circuit by a line containing `---` and nothing else. This is REQUIRED and Schemascii will complain if it doesn't find any line containing `---` and nothing else, even if there is no data after it.

Here is some example data:

```txt
* {
    %% these are global config options
    color = black
    width = 2; padding = 20;
    format = symbol
    mystring = "hello\nworld"
}

R* %% matches any resistor
{tolerance = .05; wattage = 0.25}

VR1 {
    resistance = 0 - 10k; %% ranges on variable components
    %% trailing comments are allowed
}
```

In each RULE, the SELECTOR defines what components and/or drawing objects match; for the ones that match, the MAPPING (which is stored as a Python `dict`) is or'ed into the computed properties. Rules on the bottom take precedence (there is no such thing as specificity like there is in CSS).

Selectors can match multiple scopes by using glob matching. Schemascii currently uses [`fnmatch`][fnmatch] to determine matching selectors but I'll probably change that.

See [options.md][options] for what options are available in which scopes.

Here is a rough grammar (space ignored):

```ebnf
DATA = RULE (eol+ RULE)* ;
RULE = SELECTOR eol* MAPPING ;
SELECTOR = symbol ;
MAPPING = "{" ((NAME "=" VALUE)? eol)* "}" ;
NAME = string | symbol ;
VALUE = (number | string | symbol)* ;
number = /(?:\d*\.)?\d+(?:[Ee][+-]?\d+)?/ ;
string = /"(?:\\"|[^"])+"|\s+/ ;
symbol = <any sequence of printing characters that isn't another kind of token>
eol = ";" | comment? "\n"+ ;
comment = "%%" <everything until newline> ;
```

### Metric values

For many small components, the value of the component is just a number and some unit -- e.g. for resistors it's ohms (&ohm;). Schemascii includes built-in Metric normalization and units, so if the "value" is a Metric number it will be re-written to be as short as possible while still observing the conventions of typical component values. If the unit symbol is not included, it will be added.

* `value = 0.33m` on an inductor --> "330 &micro;H" (integer values are preferred).
* `value = 0.33` on a resistor --> "0.33 &ohm;" (no Metric multiplier is preferred).
* `value = 1500mA` on a fuse --> "1.5 A" (using decimal point is shorter)
* `value = 2.2 nF` on a capacitor --> "2200 pF" (capacitances aren't typically given in nanofarads)
* `value = 10; power = 5` --> "10 &ohm; 5 W". Many components have "secondary" optional values; the name will be given in the [options][].

Also, if the value is not even a number -- such as `L1 {value = "detector coil"}`, the Metric-normalization code will not activate, and the value written will be used verbatim -- "L1 detector coil".

[fnmatch]: https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch
[options]: options.md