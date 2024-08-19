from __future__ import annotations

import itertools
from collections import defaultdict
from dataclasses import dataclass
from typing import ClassVar

import schemascii.grid as _grid
import schemascii.utils as _utils
import schemascii.wire_tag as _wt


@dataclass
class Wire:
    """List of grid points along a wire."""

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
        """tags will be mutated"""
        points = _utils.flood_walk(
            grid, [start], cls.start_dirs, cls.directions, set())
        self_tag = None
        for point, t in itertools.product(points, tags):
            if t.connect_pt == point:
                self_tag = t
                tags.remove(t)
                break
        return cls(points, self_tag)

    def to_xml_string(self, **options) -> str:
        # create lines for all of the neighbor pairs
        links = []
        for p1, p2 in itertools.combinations(self.points, 2):
            if abs(p1 - p2) == 1:
                links.append((p1, p2))
        return _utils.bunch_o_lines(links, **options)

    @classmethod
    def is_wire_character(cls, ch: str) -> bool:
        return ch in cls.start_dirs


if __name__ == '__main__':
    x = _grid.Grid("", """
.

 *    -------------------------*
 |                             |
 *----------||||----*   -------*----=foo>
                    |          |
             -----------       |
                    |          |
             -------*----------*---*
                               |   |
             *-----------------*---*
             |

.
""".strip())
    wire = Wire.get_from_grid(x, 2+4j, _wt.WireTag.find_all(x))
    print(wire)
    x.spark(*wire.points)
    print(wire.to_xml_string(scale=10, stroke_width=2, stroke="black"))
