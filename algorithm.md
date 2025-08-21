# Schemascii algorithm

(THIS DOCUMENT IS HORRIBLY OUT-OF-DATE, I NEED TO RE-WRITE THE UPDATED ALGORITHM...)

Everything is based on a `Grid` that contains all the data for the document. This `Grid` can be masked to show something else instead of the original, and restored to the original.

The algorithm first starts by finding all the "large component" boxes in the grid. After that, it finds all the "small component" reference designators. Then it picks out the BOM notes so component values, etc. can be included.

Once it has all the components picked out, it runs around the bounding boxes of each component and collects the flags, which are characters adjacent to the component but not the usual `|` and `-` for wires (these are masked out with normal wires.)

Next, wires are mapped out with a tree-walking search algorithm, hopping between corners (which is either breadth-first or depth-first, depending on whether I left the 0 in the `frontier.pop()`) and each group of wires is drawn and placed in a `<g class="wire">`.

Then for each designator, the terminals and bounding boxes are dispatched to a function to generate the SVG path of the component, and it is wrapped in a `<g class="component">` that can be styled.

All of the `<g>`'s are then concatenated together and wrapped in an enclosing `<svg>` element.

That's pretty much it. The CSS does all the rest.
