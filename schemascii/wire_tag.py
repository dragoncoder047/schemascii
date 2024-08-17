from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

import schemascii.grid as _grid
import schemascii.utils as _utils
import schemascii.wire as _wire

WIRE_TAG_PAT = re.compile(r"<([^\s=]+)=|=([^\s>]+)>")


@dataclass
class WireTag:
    """A wire tag is a named flag on the end of the
    wire, that gives it a name and also indicates what
    direction information flows.

    Wire tags currently only support horizontal connections
    as of right now."""

    name: str
    position: complex
    attach_side: Literal[_utils.Side.LEFT, _utils.Side.RIGHT]
    point_dir: Literal[_utils.Side.LEFT, _utils.Side.RIGHT]
    connect_pt: complex

    @classmethod
    def find_all(cls, grid: _grid.Grid) -> list[WireTag]:
        out: list[cls] = []
        for y, line in enumerate(grid.lines):
            for match in WIRE_TAG_PAT.finditer(line):
                left_grp, right_grp = match.groups()
                x_start, x_end = match.span()
                left_pos = complex(x_start, y)
                right_pos = complex(x_end - 1, y)
                if left_grp is not None:
                    point_dir = _utils.Side.LEFT
                    name = left_grp
                else:
                    point_dir = _utils.Side.RIGHT
                    name = right_grp
                if _wire.Wire.is_wire_character(grid.get(left_pos - 1)):
                    attach_side = _utils.Side.LEFT
                    position = left_pos
                    connect_pt = position - 1
                else:
                    attach_side = _utils.Side.RIGHT
                    position = right_pos
                    connect_pt = position + 1
                out.append(cls(name, position, attach_side,
                               point_dir, connect_pt))
        return out


if __name__ == '__main__':
    import pprint
    g = _grid.Grid("foo.txt", """
-------=foo[0:9]>

    =$rats>--------
""")
    tags = WireTag.find_all(g)
    pprint.pprint(tags)
    g.spark(*(x.connect_pt for x in tags))
