from cmath import phase
from math import pi as PI
from grid import Grid
from utils import Wire, iterate_line

# cSpell:ignore dydx

DIRECTIONS = [1+0j, -1+0j, 0+1j, 0-1j]


def next_in_dir(grid: Grid, point: complex, dydx: complex) -> tuple[complex, str] | None:
    old_point = point
    match grid.get(point):
        case '|' | ')' | '(':
            # extend up or down
            if dydx in (0+1j, 0-1j):
                while grid.get(point) in '-|()':
                    point += dydx
                if grid.get(point) not in '-|()*':
                    point -= dydx
            else:
                return None  # The vertical wires do not connect horizontally
        case '-':
            # extend sideways
            if dydx in (1+0j, -1+0j):
                while grid.get(point) in '-|()':
                    point += dydx
                if grid.get(point) not in '-|()*':
                    point -= dydx
            else:
                return None  # The horizontal wires do not connect vertically
        case '*':
            # extend any direction
            if grid.get(point + dydx) in '-|()*':
                point, s = next_in_dir(grid, point + dydx, dydx)
                if point is None:
                    return None
                return point, s
            return None
        case _:
            return None
    return point, old_point


def search_wire(grid: Grid, point: complex) -> list[tuple[complex, complex]]:
    seen = [point]
    out = []
    frontier = [point]
    # find all the points
    while frontier:
        here = frontier.pop(0)
        for d in DIRECTIONS:
            line = next_in_dir(grid, here, d)
            if line is None:
                continue
            p = line[0]
            if p not in seen and p != here:
                frontier.append(p)
                seen.append(p)
                out.append(line)
    return out


BLANKOUT = [
    "|()",  # 0: Horizontal
    "-",  # 1: Vertical
]


def next_wire(grid: Grid) -> str | None:
    # Find the first wire or return None
    for i, line in enumerate(grid.lines):
        indexes = [line.index(c) for c in '-|()*' if c in line]
        if len(indexes) > 0:
            line_pairs = search_wire(grid, complex(i, min(indexes)))
            if line_pairs:
                break
    else:
        return None
    # Blank out the used wire
    for p1, p2 in line_pairs:
        way = int(phase(p1 - p2) / PI % 1.0 * 2)
        for px in iterate_line(p1, p2):
            old = grid.get(px)
            if old not in BLANKOUT[way]:
                grid.setmask(px)
    # Return a <g>
    lines_str = ''.join(
        f'<line x1="{p1.real}" y1="{p1.imag}" x2="{p2.real}" y2="{p2.imag}"></line>' for p1, p2 in line_pairs)
    return f'<g class="wire">{lines_str}</g>'


def find_wires(grid: Grid) -> list[str]:
    out = ""
    w = next_wire(grid)
    while w is not None:
        out += w
        w = next_wire(grid)
    return out


if __name__ == '__main__':
    with open('../examples/wires_test.txt') as f:
        x = Grid('wires_test.txt', f.read())
        print(find_wires(x))
        print(x)
