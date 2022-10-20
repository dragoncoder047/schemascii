# Schemascii algorithm

Everything is based on a `Grid` that contains all the data for the document. This `Grid` can be masked to show something else instead of the original, and restored to the original.

The algorithm first starts by finding all the "large component" boxes in the grid. After that, it finds all the "small component" reference designators.

Once it has all the components picked out, it runs around the bounding boxes of each component and collects the flags, which are characters adjacent to the component but not the usual `|` and `-` for wires (these are masked out with normal wires.)

***--- IMPLEMENTATION LIMIT OF CURRENT CODE... more coming soon ---***

Next, wires are mapped out with a flood fill algorithm. The ends of the wires adjacent to the components are saved. The wires are drawn first, one `<g>` per wire.

Then for each designator, it is dispatched to the function to generate the SVG path, returning its own `<g>` that can be styled.

That's pretty much it.
