# Schemascii Format

The diagram is made of 3 components: wires, 1-, 2-, and 3-terminal components, and larger components (IC's, etc.) drawn as boxes.

Wires are simply lines drawn using dashes or pipe symbols. A wire join (drawn as a dot) is notated by a lowercase `o`, and crossed wires (not joined) are notated with a `)`. A wire corner is an `*` (asterisk). Examples:

```txt
Valid, crossed:      Valid, joined:     Wire corner:       Loose ends:       Loose ends:      Invalid:
        |                   |                |                  |                 |             |
     ---)---             ---o---             *---            -------           ---|---       ---*---
        |                   |                                   |                 |             |
```

Small components are notated with their reference designator: one or more uppercase letters followed by an ID number. They are always written horizontally even if the terminals are on the top and bottom. IDs are allowed to be duplicated and result in the same component values.

Examples:

* `C33`
* `Q1001`
* `L51`
* `F3`
* `D7`
* `U1`
* `R2`

1-, 2-, and 3-terminal components are able to accept "flags", which are other punctuation characters and lowercase letters touching them.

Polarized components (caps, diodes, etc.) accept a `+` to indicate the polarity, whereas transistors use `^><v` to indicate collector (pointing in) and emitter (pointing out).

Big components are indicated with a box amde of `~` (top and bottom), `:` (sides), and `.` (corners). The inside of the box can be anything you want, but it must include exactly one reference designator as to what component it is.

To include component values, pin numbers, etc, somewhere in the drawing but not touching any wires or other components, you can write component values - these are formatted as the reference designator (same as in circuit) followed by a `:` and the value parameter (which stops at the first whitespace). I usually put these in a "BOM section" below the circuit itself.

For simple components, this is usually just a value rating. For more specific components (mostly silicon devices) this is usually the part number.

Examples:

* `C33:2.2u` -- "2.2&micro;F"
* `Q1001:TIP102` -- just the part number; printed verbatim
* `L51:0.33` -- this is reworked to "330mH" so that it has no decimal point.
* `F3:1500m` -- reworked: "1.5A"
* `D7:1N4001` -- again, part number
* `U1:SN74LS08N,14,1,2,7,3` -- some components let you label pins with whatever you want (in this case just numbers). They start at the top and follow **counterclockwise** to follow with the pin-numbering of most IC's.
* `R2:10,5` -- this is formatted as "10&ohm; 5W". The second value is the rating; for resistors, this is a wattage, for most else, this is a maximum voltage.
