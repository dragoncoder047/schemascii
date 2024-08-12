from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Generic, TypeVar

from .grid import Grid

T = TypeVar("T")

REFDES_PAT = re.compile(r"([A-Z]+)(\d+)([A-Z\d]*)")


@dataclass
class RefDes(Generic[T]):
    """Object representing a component reference designator;
    i.e. the letter+number+suffix combination uniquely identifying
    the component on the diagram."""

    letter: str
    number: int
    suffix: str
    left: complex
    right: complex

    @classmethod
    def find_all(cls, grid: Grid) -> list[RefDes]:
        out = []
        for row, line in enumerate(grid.lines):
            for match in REFDES_PAT.finditer(line):
                left_col, right_col = match.span()
                letter, number, suffix = match.groups()
                number = int(number)
                out.append(cls(
                    letter,
                    number,
                    suffix,
                    complex(left_col, row),
                    complex(right_col - 1, row)))
        return out


if __name__ == '__main__':
    import pprint
    gg = Grid("test_data/test_charge_pump.txt")
    rds = RefDes.find_all(gg)
    pts = [p for r in rds for p in [r.left, r.right]]
    gg.spark(*pts)
    pprint.pprint(rds)
