from cmath import phase
from math import pi
from grid import Grid
from utils import iterate_line, extend, merge_colinear, XML

# cSpell:ignore dydx

DIRECTIONS = [1, -1, 1j, -1j]


def is_end(grid: Grid, point: complex) -> bool:
    """Returns if the point contains a "loose end" wire."""
    char = grid.get(point)
    if char not in "|()-*":
        return False
    if char in "|()":
        diffs = [1j, -1j]
        conn = "|()*"
        cross = "-"
    elif char == "-":
        diffs = [1, -1]
        conn = "-*"
        cross = "|()"
    elif char == '*':
        diffs = [1, -1, 1j, -1j]
        conn = "|()-*"
        cross = ""
    count_conn = 0
    for d in diffs:
        c = grid.get(point + d)
        while (c := grid.get(point + d)) in cross:
            point += d
        if c in conn:
            count_conn += 1
    return count_conn < 2


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
            # extend any direction
            if grid.get(point + dydx) in '-|()':
                return next_in_dir(grid, point + dydx, dydx)
            if grid.get(point + dydx) == '*':
                point += dydx
            else:
                return None
        case _:
            return None
    if point == old_point:
        return None  # suppress length=0 wires
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
            print(here, line)
            if line is None:
                continue
            p = line[0]
            if p not in seen and p != here:
                frontier.append(p)
                seen.append(p)
                out.append(line)
    return out


def first_end(grid: Grid) -> complex | None:
    """Returns the first "loose end" of a wire in the grid."""
    indexes = [complex(x, y) for y in range(grid.height)
               for x in range(grid.width) if is_end(grid, complex(x, y))]
    if len(indexes) > 0:
        return indexes[0]
    return None


def next_wire(grid: Grid, **options) -> str | None:
    """Returns a SVG string of the next line in the grid,
    or None if there are no more. The line is masked off."""
    scale = options.get("scale", 1)
    stroke_width = options.get("stroke_width", 1)
    color = options.get("stroke", "black")
    # Find the first loose end or return None
    end = first_end(grid)
    if end is None:
        return None
    line_pieces = search_wire(grid, end)
    if not line_pieces:
        # got a length 0 wire
        grid.setmask(end)
        return ""
    # Blank out the used wire
    for p1, p2 in line_pieces:
        # Crazy math!!
        way = int(phase(p1 - p2) / pi % 1.0 * 2)
        for px in iterate_line(p1, p2):
            old = grid.get(px)
            # way: 0: Horizontal, 1: Vertical
            if old not in ["|()", "-"][way]:
                grid.setmask(px)  # Don't mask out wire crosses
    return XML.g(
        *(
            XML.line(
                x1=p1.real * scale,
                y1=p1.imag * scale,
                x2=extend(p1, p2).real * scale,
                y2=extend(p1, p2).imag * scale,
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
    with open('../test_data/test_resistors.txt') as f:
        x = Grid('test_resistors.txt', f.read())
        print(get_wires(x, 1))
        print(x)
