from __future__ import annotations
import re
from dataclasses import dataclass

import schemascii.grid as _grid

REFDES_PAT = re.compile(r"([A-Z_]+)(\d*)([A-Z_\d]*)")


@dataclass
class RefDes:
    """Object representing a component reference designator;
    i.e. the letter+number+suffix combination uniquely identifying
    the component on the diagram.
    """

    letter: str
    number: int
    suffix: str
    left: complex
    right: complex

    @classmethod
    def find_all(cls, grid: _grid.Grid) -> list[RefDes]:
        """Finds all of the reference designators present in the
        grid.
        """
        out = []
        for row, line in enumerate(grid.lines):
            for match in REFDES_PAT.finditer(line):
                left_col, right_col = match.span()
                letter, number, suffix = match.groups()
                number = int(number) if number else 0
                out.append(cls(
                    letter,
                    number,
                    suffix,
                    complex(left_col, row),
                    complex(right_col - 1, row)))
        return out

    @property
    def name(self) -> str:
        return f"{self.short_name}{self.suffix}"

    @property
    def short_name(self) -> str:
        return f"{self.letter}{self.number}{self.suffix}"


if __name__ == '__main__':
    import pprint
    gg = _grid.Grid("", """
C1
            BAT3V3
        U3A
                    Q1G1
                    R.Heater
                    ^
                    this one is invalid; only the "R" and "H" are gotten
    GND
""")
    rds = RefDes.find_all(gg)
    pts = [p for r in rds for p in [r.left, r.right]]
    gg.spark(*pts)
    pprint.pprint(rds)
