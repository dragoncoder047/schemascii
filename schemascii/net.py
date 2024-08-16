from __future__ import annotations

from dataclasses import dataclass

from .grid import Grid
from .wire import Wire


@dataclass
class Net:
    """Grouping of wires that are
    electrically connected."""

    wires: list[Wire]
    # annotation: WireTag | None

    @classmethod
    def find_all(cls, grid: Grid) -> list[Net]:
        seen_points: set[complex] = set()
        all_nets: list[cls] = []

        for y, line in enumerate(grid.lines):
            for x, ch in enumerate(line):
                if Wire.is_wire_character(ch):
                    wire = Wire.get_from_grid(grid, complex(x, y))
                    if all(p in seen_points for p in wire.points):
                        continue
                    all_nets.append(cls([wire]))
                    seen_points.update(wire.points)
        return all_nets
