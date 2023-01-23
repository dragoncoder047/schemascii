from grid import Grid
from utils import Wire, colinear

# cSpell:ignore dydx

DIRECTIONS = [1+0j, -1+0j, 0+1j, 0-1j]


def next_in_dir(grid: Grid, point: complex, dydx: complex) -> complex | None:
    match grid.get(point):
        case '|' | ')':
            # extend up or down
            if dydx in (0+1j, 0-1j):
                while grid.get(point) in '-|)':
                    point += dydx
                return point - (dydx if grid.get(point) not in '-|)*' else 0j)
            return None  # The vertical wires do not connect horizontally
        case '-':
            # extend sideways
            if dydx in (1+0j, -1+0j):
                while grid.get(point) in '-|)':
                    point += dydx
                return point - (dydx if grid.get(point) not in '-|)*' else 0j)
            return None  # The horizontal wires do not connect vertically
        case '*':
            # extend any direction
            if grid.get(point + dydx) in '-|)*':
                return next_in_dir(grid, point + dydx, dydx)
            return None


def search_wire(grid: Grid, point: complex) -> list[list[complex]]:
    seen = []
    frontier = [point]
    # find all the points
    while frontier:
        here = frontier.pop(0)
        seen.append(here)
        for d in DIRECTIONS:
            p = next_in_dir(grid, here, d)
            if all((p is not None,
                    p not in seen,
                    p not in frontier,
                    p != here)):
                frontier.append(p)
    return seen


def next_wire(grid: Grid) -> str | None:
    for i, line in enumerate(grid.lines):
        indexes = [line.index(c) for c in '-|)*' if c in line]
        if len(indexes) > 0:
            points = search_wire(grid, complex(i, min(indexes)))
            break
    else:
        return None
    # Turn points into string
    # TODO


def find_wires(grid: Grid) -> list[str]:
    # find all cells that have loose ends
    return next_wire(grid)


if __name__ == '__main__':
    with open('../examples/wires_test.txt') as f:
        x = Grid('wires_test.txt', f.read())
        print(find_wires(x))
