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
    return point, f'<line x1="{old_point.real}" y1="{old_point.imag}" x2="{point.real}" y2="{point.imag}"></line>'


def search_wire(grid: Grid, point: complex) -> tuple[str, list[complex]]:
    seen = []
    out = ''
    frontier = [point]
    # find all the points
    while frontier:
        here = frontier.pop(0)
        seen.append(here)
        for d in DIRECTIONS:
            xx = next_in_dir(grid, here, d)
            if xx is None:
                continue
            p, s = xx
            if all((p not in seen,
                    p not in frontier,
                    p != here)):
                frontier.append(p)
                out += s
    return seen, out


def next_wire(grid: Grid) -> str | None:
    for i, line in enumerate(grid.lines):
        indexes = [line.index(c) for c in '-|()*' if c in line]
        if len(indexes) > 0:
            points, lines = search_wire(grid, complex(i, min(indexes)))
            break
    else:
        return None
    # Turn points into string
    # TODO
    # Mask out used wire
    # TODO
    return f'<g class="wire">{lines}</g>'


def find_wires(grid: Grid) -> list[str]:
    # find all cells that have loose ends
    return next_wire(grid)


if __name__ == '__main__':
    with open('../examples/wires_test.txt') as f:
        x = Grid('wires_test.txt', f.read())
        print(find_wires(x))
