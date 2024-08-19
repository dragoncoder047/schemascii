from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from typing import ClassVar
import schemascii.utils as _utils
import schemascii.grid as _grid


@dataclass
class AnnotationLine:
    """Class that implements the ability to
    draw annotation lines on the drawing
    without having to use a disconnected wire."""

    directions: ClassVar[
        defaultdict[str, defaultdict[complex, list[complex]]]] = defaultdict(
        lambda: None, {
            # allow jumps over actual wires
            "-": _utils.IDENTITY,
            "|": _utils.IDENTITY,
            "(": _utils.IDENTITY,
            ")": _utils.IDENTITY,
            ":": _utils.IDENTITY,
            "~": _utils.IDENTITY,
            ".": {
                -1: [1j, 1],
                1j: [],
                -1j: [-1, 1],
                1: [1j, -1]
            },
            "'": {
                -1: [-1j, 1],
                -1j: [],
                1j: [-1, 1],
                1: [-1j, -1]
            }
        })
    start_dirs: ClassVar[
        defaultdict[str, list[complex]]] = defaultdict(
        lambda: None, {
            "~": _utils.LEFT_RIGHT,
            ":": _utils.UP_DOWN,
            ".": (-1, 1, -1j),
            "'": (-1, 1, 1j),
        })

    points: list[complex]

    @classmethod
    def get_from_grid(cls, grid: _grid.Grid, start: complex) -> AnnotationLine:
        points = _utils.flood_walk(
            grid, [start], cls.start_dirs, cls.directions, set())
        return cls(points)

    @classmethod
    def is_annoline_character(cls, ch: str) -> bool:
        return ch in cls.start_dirs

    @classmethod
    def find_all(cls, grid: _grid.Grid) -> list[AnnotationLine]:
        seen_points: set[complex] = set()
        all_lines: list[cls] = []

        for y, line in enumerate(grid.lines):
            for x, ch in enumerate(line):
                if cls.is_annoline_character(ch):
                    line = cls.get_from_grid(grid, complex(x, y))
                    if all(p in seen_points for p in line.points):
                        continue
                    all_lines.append(cls([line]))
                    seen_points.update(line.points)
        return all_lines


if __name__ == '__main__':
    x = _grid.Grid("", """
                    |          |
             -----------   .~~~|~~~~~~.
                    |      :   |      :
             -------*------:---*---*  :
                           :   |   |  :
             *-------------:---*---*  '~~~~.
             |             :               :
                           '~~~~~~~~~~~~~~~'

""")
    line = AnnotationLine.get_from_grid(x, 30+2j)
    print(line)
    x.spark(*line.points)