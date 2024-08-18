import re
from dataclasses import dataclass

import schemascii.grid as _grid

ANNOTATION_RE = re.compile(r"\[([^\]]+)\]")


@dataclass
class Annotation:
    position: complex
    content: str

    @classmethod
    def find_all(cls, grid: _grid.Grid):
        out: list[cls] = []
        for y, line in enumerate(grid.lines):
            for match in ANNOTATION_RE.finditer(line):
                x = match.span()[0]
                text = match.group(1)
                out.append(cls(complex(x, y), text))
        return out
