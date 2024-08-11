from collections import defaultdict
from itertools import combinations
from typing import Literal

from .grid import Grid
from .utils import bunch_o_lines

# This is a map of the direction coming into the cell
# to the set of directions coming "out" of the cell.
DirStr = Literal["^", "v", "<", ">"]
NOWHERE = None
EVERYWHERE: defaultdict[DirStr, str] = defaultdict(lambda: "<>^v")
IDENTITY: dict[DirStr, str] = {">": ">", "^": "^", "<": "<", "v": "v"}
WIRE_DIRECTIONS: defaultdict[str, defaultdict[DirStr, str]] = defaultdict(
    lambda: NOWHERE, {
        "-": IDENTITY,
        "|": IDENTITY,
        "(": IDENTITY,
        ")": IDENTITY,
        "*": EVERYWHERE,
    })
WIRE_STARTS: defaultdict[str, str] = defaultdict(lambda: NOWHERE, {
    "-": "<>",
    "|": "^v",
    "(": "^v",
    ")": "^v",
    "*": "<>^v"
})

CHAR2DIR: dict[DirStr, complex] = {">": -1, "<": 1, "^": 1j, "v": -1j}


class Wire(list[complex]):
    """List of grid points along a wire."""

    @classmethod
    def get_from_grid(cls, grid: Grid, start: complex):
        seen: set[complex] = set()
        pts: list[complex] = []
        stack: list[tuple[complex, DirStr]] = [
            (start, WIRE_STARTS[grid.get(start)])]
        while stack:
            point, directions = stack.pop()
            if point in seen:
                continue
            seen.add(point)
            pts.append(point)
            for dir in directions:
                next_pt = point + CHAR2DIR[dir]
                if ((next_dirs := WIRE_DIRECTIONS[grid.get(next_pt)])
                        is not NOWHERE):
                    stack.append((next_pt, next_dirs[dir]))
        return cls(pts)

    def to_xml_string(self, **options) -> str:
        # create lines for all of the neighbor pairs
        links = []
        for p1, p2 in combinations(self, 2):
            if abs(p1 - p2) == 1:
                links.append((p1, p2))
        return bunch_o_lines(links, **options)


if __name__ == '__main__':
    x = Grid("", """
.

 *    -------------------------*
 |                             |
 *----------||||----*   -------*
                    |          |
             -----------       |
                    |          |
             -------*----------*---*
                               |   |
             *-----------------*---*
             |

.
""".strip())
    pts = Wire.get_from_grid(x, 2+4j)
    x.spark(*pts)
    print(pts.to_xml_string(scale=10, stroke_width=2, stroke="black"))
