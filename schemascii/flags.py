from itertools import chain
from utils import Cbox, Flag, Side
from grid import Grid


def find_flags(grid: Grid, box: Cbox) -> list[Flag]:
    out = []
    for p, s in chain(
        # Top side
        ((complex(xx, int(box.p2.imag) - 1), Side.TOP)
         for xx in range(int(box.p1.real), int(box.p2.real) + 1)),
        # Right side
        ((complex(int(box.p2.real) + 1, yy), Side.RIGHT)
         for yy in range(int(box.p1.imag), int(box.p2.imag) + 1)),
        # Bottom side
        ((complex(xx, int(box.p2.imag) + 1), Side.BOTTOM)
         for xx in range(int(box.p1.real), int(box.p2.real) + 1)),
        # Left side
        ((complex(int(box.p1.real) - 1, yy), Side.LEFT)
         for yy in range(int(box.p1.imag), int(box.p2.imag) + 1)),
    ):
        try:
            c = grid.get(p)
        except IndexError:
            continue
        # if c in '*o':
        #     raise ValueError(
        #         "%s not allowed here (at line %d, col %d)" % (c, p.imag + 1, p.real + 1))
        if c == ' ':
            continue
        if s in (Side.TOP, Side.BOTTOM):
            grid.setmask(p, '|')
        if s in (Side.LEFT, Side.RIGHT):
            grid.setmask(p, '-')
        out.append(Flag(c, box, s))
    return out
