from itertools import chain
from types import FunctionType
from .utils import Cbox, Flag, Side, Terminal
from .grid import Grid


def over_edges(box: Cbox) -> list:
    "Decorator - Runs around the edges of the box on the grid."
    def inner_over_edges(func: FunctionType):
        out = []
        for p, s in chain(
            # Top side
            ((complex(xx, int(box.p1.imag) - 1), Side.TOP)
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
            result = func(p, s)
            if result is not None:
                out.append(result)
        return out
    return inner_over_edges


def take_flags(grid: Grid, box: Cbox) -> list[Flag]:
    """Runs around the edges of the component box, collects
    the flags, and masks them off to wires."""
    @over_edges(box)
    def flags(p: complex, s: Side) -> Flag | None:
        c = grid.get(p)
        if c in ' -|()*':
            return None
        grid.setmask(p, '*')
        return Flag(p, c, s)
    return flags


def find_edge_marks(grid: Grid, box: Cbox) -> list[Terminal]:
    "Finds all the terminals on the box in the grid."
    flags = take_flags(grid, box)

    @over_edges(box)
    def terminals(p: complex, s: Side) -> Terminal | None:
        c = grid.get(p)
        if ((c in "*|()" and s in (Side.TOP, Side.BOTTOM))
                or (c in "*-" and s in (Side.LEFT, Side.RIGHT))):
            maybe_flag = [f for f in flags if f.pt == p]
            if maybe_flag:
                return Terminal(p, maybe_flag[0].char, s)
            return Terminal(p, None, s)
        return None
    return terminals
