from grid import Grid
from utils import Wire


DIRECTIONS = [1+0j, -1+0j, 0+1j, 0-1j]


def get_dir(grid: Grid, point: complex, dir: complex) -> complex | None:
    pass


def flood_fill(grid: Grid, point: complex, dydx: complex = 1+0j) -> list[complex]:
    stack = [point]
    pass # TODO


def next_wire(grid: Grid) -> list[list[complex]]:
    for i, line in enumerate(grid.lines):
        pass # TODO


def find_wires(grid: Grid) -> list[str]:
    # find all cells that have loose ends
    pass


if __name__ == '__main__':
    with open('../examples/wires_test.txt') as f:
        x = Grid('test1.txt', f.read())
        print(find_wires(x))
