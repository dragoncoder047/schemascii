from __future__ import annotations

from dataclasses import dataclass

import schemascii.grid as _grid
import schemascii.wire as _wire


@dataclass
class Net:
    """Grouping of wires that are
    electrically connected."""

    wires: list[_wire.Wire]
    # annotation: WireTag | None

    @classmethod
    def find_all(cls, grid: _grid.Grid) -> list[Net]:
        seen_points: set[complex] = set()
        all_nets: list[cls] = []

        for y, line in enumerate(grid.lines):
            for x, ch in enumerate(line):
                if _wire.Wire.is_wire_character(ch):
                    wire = _wire.Wire.get_from_grid(grid, complex(x, y))
                    if all(p in seen_points for p in wire.points):
                        continue
                    all_nets.append(cls([wire]))
                    seen_points.update(wire.points)
        return all_nets
