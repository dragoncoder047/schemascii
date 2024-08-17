from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from typing import ClassVar, Literal

import schemascii.grid as _grid
import schemascii.utils as _utils
import schemascii.wire_tag as _wt

DirStr = Literal["^", "v", "<", ">"] | None
EVERYWHERE: defaultdict[DirStr, str] = defaultdict(lambda: "<>^v")
IDENTITY: dict[DirStr, str] = {">": ">", "^": "^", "<": "<", "v": "v"}

CHAR2DIR: dict[DirStr, complex] = {">": -1, "<": 1, "^": 1j, "v": -1j}


@dataclass
class Wire:
    """List of grid points along a wire."""

    # This is a map of the direction coming into the cell
    # to the set of directions coming "out" of the cell.
    directions: ClassVar[
        defaultdict[str, defaultdict[DirStr, str]]] = defaultdict(
        lambda: None, {
            "-": IDENTITY,
            "|": IDENTITY,
            "(": IDENTITY,
            ")": IDENTITY,
            "*": EVERYWHERE,
        })
    starting_directions: ClassVar[
        defaultdict[str, str]] = defaultdict(
        lambda: None, {
            "-": "<>",
            "|": "^v",
            "(": "^v",
            ")": "^v",
            "*": "<>^v"
        })

    points: list[complex]
    tag: _wt.WireTag | None

    @classmethod
    def get_from_grid(cls, grid: _grid.Grid,
                      start: complex, tags: list[_wt.WireTag]) -> Wire:
        """tags will be mutated"""
        seen: set[complex] = set()
        points: list[complex] = []
        stack: list[tuple[complex, DirStr]] = [
            (start, cls.starting_directions[grid.get(start)])]
        while stack:
            point, directions = stack.pop()
            if point in seen:
                continue
            seen.add(point)
            points.append(point)
            for dir in directions:
                next_pt = point + CHAR2DIR[dir]
                if ((next_dirs := cls.directions[grid.get(next_pt)])
                        is not None):
                    stack.append((next_pt, next_dirs[dir]))
        self_tag = None
        for point in points:
            for t in tags:
                if t.connect_pt == point:
                    self_tag = t
                    tags.remove(t)
                    break
            else:
                continue
            break
        return cls(points, self_tag)

    def to_xml_string(self, **options) -> str:
        # create lines for all of the neighbor pairs
        links = []
        for p1, p2 in combinations(self.points, 2):
            if abs(p1 - p2) == 1:
                links.append((p1, p2))
        return _utils.bunch_o_lines(links, **options)

    @classmethod
    def is_wire_character(cls, ch: str) -> bool:
        return ch in cls.starting_directions


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
