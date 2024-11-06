from __future__ import annotations

import itertools
from collections import defaultdict
from dataclasses import dataclass
from typing import ClassVar

import schemascii.data_consumer as _dc
import schemascii.grid as _grid
import schemascii.utils as _utils
import schemascii.wire_tag as _wt


@dataclass
class Wire(_dc.DataConsumer, namespaces=(":wire",)):
    """List of grid points along a wire that are
    electrically connected.
    """

    css_class = "wire"

    # This is a map of the direction coming into the cell
    # to the set of directions coming "out" of the cell.
    directions: ClassVar[
        defaultdict[str, defaultdict[complex, list[complex]]]] = defaultdict(
        lambda: None, {
            "-": _utils.IDENTITY,
            "|": _utils.IDENTITY,
            "(": _utils.IDENTITY,
            ")": _utils.IDENTITY,
            "*": _utils.EVERYWHERE,
            # allow jumps through annotation lines
            ":": _utils.IDENTITY,
            "~": _utils.IDENTITY,
        })
    start_dirs: ClassVar[
        defaultdict[str, list[complex]]] = defaultdict(
        lambda: None, {
            "-": _utils.LEFT_RIGHT,
            "|": _utils.UP_DOWN,
            "(": _utils.UP_DOWN,
            ")": _utils.UP_DOWN,
            "*": _utils.ORTHAGONAL,
        })

    points: list[complex]
    tag: _wt.WireTag | None

    @classmethod
    def get_from_grid(cls, grid: _grid.Grid,
                      start: complex, tags: list[_wt.WireTag]) -> Wire:
        """Return the wire starting at the grid point specified.

        tags will be mutated if any of the tags connects to this wire.
        """
        points = _utils.flood_walk(
            grid, [start], cls.start_dirs, cls.directions, set())
        self_tag = None
        for point, t in itertools.product(points, tags):
            if t.connect_pt == point:
                self_tag = t
                tags.remove(t)
                break
        return cls(points, self_tag)

    def render(self, data, **options) -> str:
        scale = options["scale"]
        linewidth = options["linewidth"]
        # create lines for all of the neighbor pairs
        links = []
        for p1, p2 in itertools.combinations(self.points, 2):
            if abs(p1 - p2) == 1:
                links.append((p1, p2))
        # find dots
        dots = ""
        for dot_pt in _utils.find_dots(links):
            dots += _utils.XML.circle(
                cx=scale * dot_pt.real,
                cy=scale * dot_pt.real,
                r=linewidth,
                class_="dot")
        return (_utils.bunch_o_lines(links, **options)
                + (self.tag.to_xml_string(data) if self.tag else "")
                + dots)

    @classmethod
    def is_wire_character(cls, ch: str) -> bool:
        return ch in cls.start_dirs


if __name__ == '__main__':
    x = _grid.Grid("", """
.

                   |   [TODO: this loop-de-loop causes problems]
                   |   [is it worth fixing?]
---------------------------------*
                   |             |
                   |             |
                   *-------------*

.
""".strip())
    wire = Wire.get_from_grid(x, 2+4j, _wt.WireTag.find_all(x))
    print(wire)
    x.spark(*wire.points)
