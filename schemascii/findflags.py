from utils import Cbox, Flag, Side
from grid import Grid
from itertools import chain

def getflags(grid: Grid, box: Cbox) -> list[Flag]:
    out = []
    for x, y, s in chain(
        # Top side
        ((xx, box.y1 - 1, Side.TOP) for xx in range(box.x1, box.x2 + 1)),
        # Right side
        ((box.x2 + 1, yy, Side.RIGHT) for yy in range(box.y1, box.y2 + 1)),
        # Bottom side
        ((xx, box.y2 + 1, Side.BOTTOM) for xx in range(box.x1, box.x2 + 1)),
        # Left side
        ((box.x1 - 1, yy, Side.LEFT) for yy in range(box.y1, box.y2 + 1)),
    ):
        try:
            c = grid.get(x, y)
        except IndexError:
            continue
        if c in '*o':
            raise ValueError(
                "%s not allowed here (at line %d, col %d)" % (c, y + 1, x + 1))
        if c == ' ':
            continue
        if s in (Side.TOP, Side.BOTTOM):
            grid.setmask(x, y, '|')
        if s in (Side.LEFT, Side.RIGHT):
            grid.setmask(x, y, '-')
        out.append(Flag(c, box, s))
    return out
