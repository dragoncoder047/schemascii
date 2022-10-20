# Schemascii algorithm

Everything is based on a `Grid` that contains all the data for the document. This `Grid` can be masked to show something else instead of the original, and restored to the original.

The algorithm first starts by finding all the "large component" boxes in the grid. After that, it finds all the "small component" reference designators. Then it picks out the BOM notes so component values, etc. can be drawn.

Once it has all the components picked out, it runs around the bounding boxes of each component and collects the flags, which are characters adjacent to the component but not the usual `|` and `-` for wires (these are masked out with normal wires.)

***--- IMPLEMENTATION LIMIT OF CURRENT CODE... more coming soon ---***

Next, wires are mapped out with a flood fill algorithm. The straight lines coming out of each component is followed until it comes to a join or corner, and those "end" terminals are saved. The rest of the wires are drawn, one `<g>` per wire.

Then for each designator, the "end" terminals are dispatched to the function to generate the SVG path of the component, returning its own `<g>` that can be styled.

That's pretty much it.
