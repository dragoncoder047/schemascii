from cmath import phase
from math import pi
from grid import Grid
from utils import iterate_line, extend, merge_colinear, XML

# cSpell:ignore dydx

DIRECTIONS = [1, -1, 1j, -1j]


def is_end(grid: Grid, point: complex) -> bool:
    """Returns true if the point is a loose end."""
    char = grid.get(point)
    if char not in "|()-*":
        return False
    count = 0
    for d in DIRECTIONS:
        c = grid.get(point + d)
        if c in "|()-*":
            count += 1
    return count < 2


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
                print("extending vertically from", point, dydx)
                while grid.get(point) in '-|()':
                    point += dydx
                if grid.get(point) != '*':
                    point -= dydx
            else:
                return None  # The vertical wires do not connect horizontally
        case '-':
            # extend sideways
            if dydx in (1, -1):
                print("extending sideways from", point, dydx)
                while grid.get(point) in '-|()':
                    point += dydx
                if grid.get(point) != '*':
                    point -= dydx
            else:
                return None  # The horizontal wires do not connect vertically
        case '*':
            # extend any direction
            print("asterisk at", point, dydx)
            if grid.get(point + dydx) in '-|()':
                res = next_in_dir(grid, point + dydx, dydx)
                if res is not None:
                    point = res[0]
                else:
                    return None
            if grid.get(point + dydx) == '*':
                point += dydx
            else:
                return None
        case _:
            return None
    print('result', old_point, point)
    if point == old_point:
        return None  # suppress length=0 wires
    return point, old_point


def first_end_or_corner(grid: Grid) -> complex | None:
    """Returns the first "loose end" of a wire in the grid."""
    indexes = [complex(x, y) for y in range(grid.height)
               for x in range(grid.width) if is_end(grid, complex(x, y))]
    if len(indexes) > 0:
        return indexes[0]
    return None


def next_line(grid: Grid) -> tuple[complex, complex] | None:
    """Returns a SVG string of the next line in the grid,
    or None if there are no more. The line is masked off."""

    # Find the first loose end or return None
    start = first_end_or_corner(grid)
    if start is None:
        return None
    for diff in DIRECTIONS:
        line = next_in_dir(grid, start, diff)
        if line is not None and abs(line[0] - line[1]) > 0:
            start, end = line
            break
    else:
        return None
    # Crazy math!!
    way = int(phase(start - end) / pi % 1.0 * 2)
    for px in iterate_line(start, end):
        old = grid.get(px)
        if old == "*":
            continue  # Don't mask out wire crosses just yet
        # way: 0: Horizontal, 1: Vertical
        if old not in ["|()", "-"][way]:
            grid.setmask(px)
    for px in (start, end):
        old = grid.get(px)
        if old == "*" and not is_end(grid, px):
            grid.setmask(px)
    return start, end


def get_wires(grid: Grid, **options) -> str:
    "Finds all the wires and masks them out, returns an SVG string."
    scale = options.get("scale", 1)
    stroke_width = options.get("stroke_width", 1)
    color = options.get("stroke", "black")
    all_lines = []
    w = next_line(grid)
    while w is not None:
        all_lines.append(w)
        print(all_lines, grid)
        w = next_line(grid)
    # return XML.g(
    #     *(
    #         XML.line(
    #             x1=p1.real * scale,
    #             y1=p1.imag * scale,
    #             x2=extend(p1, p2).real * scale,
    #             y2=extend(p1, p2).imag * scale,
    #             stroke__width=stroke_width,
    #             stroke=color,
    #         )
    #         for p1, p2 in line_pieces
    #     ),
    #     class_="wire")


if __name__ == '__main__':
    with open('../test_data/test_resistors.txt') as f:
        x = Grid('test_resistors.txt', f.read())
        print(get_wires(x))
        print(x)
