from __future__ import annotations

import itertools
import typing
from collections import defaultdict
from dataclasses import dataclass

import schemascii.data_consumer as _dc
import schemascii.grid as _grid
import schemascii.utils as _utils


@dataclass
class AnnotationLine(_dc.DataConsumer,
                     namespaces=(":annotation", ":annotation-line")):
    """Class that implements the ability to
    draw annotation lines on the drawing
    without having to use a disconnected wire.
    """

    css_class = "annotation annotation-line"

    directions: typing.ClassVar[
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
    start_dirs: typing.ClassVar[
        defaultdict[str, list[complex]]] = defaultdict(
        lambda: None, {
            "~": _utils.LEFT_RIGHT,
            ":": _utils.UP_DOWN,
            ".": (-1, 1, -1j),
            "'": (-1, 1, 1j),
        })

    # the sole member
    points: list[complex]

    @classmethod
    def get_from_grid(cls, grid: _grid.Grid, start: complex) -> AnnotationLine:
        """Return an AnnotationLine that starts at the specified point."""
        points = _utils.flood_walk(
            grid, [start], cls.start_dirs, cls.directions, set())
        return cls(points)

    @classmethod
    def is_annoline_character(cls, ch: str) -> bool:
        """Return true if ch is a valid character
        to make up an AnnotationLine.
        """
        return ch in cls.start_dirs

    @classmethod
    def find_all(cls, grid: _grid.Grid) -> list[AnnotationLine]:
        """Return all of the annotation lines found in the grid."""
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

    def render(self, **options) -> str:
        # copy-pasted from wire.py except class changed at bottom
        # create lines for all of the neighbor pairs
        links = []
        for p1, p2 in itertools.combinations(self.points, 2):
            if abs(p1 - p2) == 1:
                links.append((p1, p2))
        return _utils.bunch_o_lines(links, **options)


if __name__ == '__main__':
    x = _grid.Grid("", """
                    |          |
             -----------   .~~~|~~~~~~.
                    |      :   |      :
             -------*------:---*---*  :
            ~~~~~~~~~~~~~~~:~~~|~~~~~~~~~~~~~
             *-------------:---*---*  '~~~~.
             |             :               :
                           '~~~~~~~~~~~~~~~'

""")
    line, = AnnotationLine.find_all(x)
    print(line)
    x.spark(*line.points)
