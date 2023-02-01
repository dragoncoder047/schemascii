from cmath import phase, rect
from math import pi
from .grid import Grid
from .utils import iterate_line, merge_colinear, XML

# cSpell:ignore dydx

DIRECTIONS = [1, -1, 1j, -1j]


def next_in_dir(
        grid: Grid,
        point: complex,
        dydx: complex) -> tuple[complex, complex] | None:
    """Follows the wire starting at the point in the specified direction,
    until some interesting change (a corner, junction, or end). Returns the
    tuple (new, old)."""
    old_point = point
    match grid.get(point):
        case '|' | '(' | ')':
            # extend up or down
            if dydx in (1j, -1j):
                while grid.get(point) in '-|()':
                    point += dydx
                if grid.get(point) != '*':
                    point -= dydx
            else:
                return None  # The vertical wires do not connect horizontally
        case '-':
            # extend sideways
            if dydx in (1, -1):
                while grid.get(point) in '-|()':
                    point += dydx
                if grid.get(point) != '*':
                    point -= dydx
            else:
                return None  # The horizontal wires do not connect vertically
        case '*':
            # can extend any direction
            if grid.get(point + dydx) in "|()-*":
                point += dydx
                res = next_in_dir(grid, point, dydx)
                if res is not None:
                    point = res[0]
                elif dydx in (1j, -1j) and grid.get(point) == "-":
                    return None
                elif dydx in (1, -1) and grid.get(point) in "|()":
                    return None
            else:
                return None
        case _:
            return None
    if point == old_point:
        return None
    return point, old_point


def search_wire(grid: Grid, point: complex) -> list[tuple[complex, complex]]:
    """Flood-fills the grid starting at the point, and returns
    the list of all the straight pieces of wire encountered."""
    seen = [point]
    out = []
    frontier = [point]
    # find all the points
    while frontier:
        here = frontier.pop()
        for d in DIRECTIONS:
            line = next_in_dir(grid, here, d)
            if line is None or abs(line[1] - line[0]) == 0:
                continue
            p = line[0]
            if p not in seen and p != here:
                frontier.append(p)
                seen.append(p)
                out.append(line)
    return out


def blank_wire(grid: Grid, p1: complex, p2: complex):
    "Blank out the wire from p1 to p2."
    # Crazy math!!
    way = int(phase(p1 - p2) / pi % 1.0 * 2)
    side = rect(1, phase(p1 - p2) + pi / 2)
    for px in iterate_line(p1, p2):
        old = grid.get(px)
        # way: 0: Horizontal, 1: Vertical
        # Don't mask out wire crosses
        keep = ["|()", "-"][way]
        swap = "|-"[way]
        if old not in keep:
            if (grid.get(px + side) in keep and
                    grid.get(px - side) in keep):
                grid.setmask(px, swap)
            else:
                grid.setmask(px)


def next_wire(grid: Grid, **options) -> str | None:
    """Returns a SVG string of the next line in the grid,
    or None if there are no more. The line is masked off."""
    scale = options["scale"]
    stroke_width = options["stroke_width"]
    color = options["stroke"]
    # Find the first wire or return None
    for i, line in enumerate(grid.lines):
        indexes = [line.index(c) for c in '-|()*' if c in line]
        if len(indexes) > 0:
            line_pieces = search_wire(grid, complex(min(indexes), i))
            if line_pieces:
                break
    else:
        return None
    # Blank out the used wire
    for p1, p2 in line_pieces:
        blank_wire(grid, p1, p2)
        if p1 == p2:
            raise RuntimeError("0-length wire")
    return XML.g(
        *(
            XML.line(
                x1=p1.real * scale,
                y1=p1.imag * scale,
                x2=p2.real * scale,
                y2=p2.imag * scale,
                stroke__width=stroke_width,
                stroke=color,
            )
            for p1, p2 in line_pieces
        ),
        class_="wire")


def get_wires(grid: Grid, **options) -> str:
    "Finds all the wires and masks them out, returns an SVG string."
    out = ""
    w = next_wire(grid, **options)
    while w is not None:
        out += w
        w = next_wire(grid, **options)
    return out


if __name__ == '__main__':
    xg = Grid('test_data/test_resistors.txt')
    print(get_wires(xg, scale=20))
    print(xg)
