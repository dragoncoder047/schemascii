from __future__ import annotations

import html
import re
from dataclasses import dataclass

import schemascii.data_consumer as _dc
import schemascii.grid as _grid
import schemascii.utils as _utils

ANNOTATION_RE = re.compile(r"\[([^\]]+)\]")


@dataclass
class Annotation(_dc.DataConsumer, namespaces=(":annotation",)):
    """A chunk of text that will be rendered verbatim in the output SVG."""

    options = [
        ("scale",),
        _dc.Option("font", str, "Text font", "sans-serif"),
    ]

    position: complex
    content: str

    css_class = "annotation"

    @classmethod
    def find_all(cls, grid: _grid.Grid) -> list[Annotation]:
        """Return all of the text annotations present in the grid."""
        out: list[Annotation] = []
        for y, line in enumerate(grid.lines):
            for match in ANNOTATION_RE.finditer(line):
                x = match.span()[0]
                text = match.group(1)
                out.append(cls(complex(x, y), text))
        return out

    def render(self, scale, font, **options) -> str:
        return _utils.XML.text(
            html.escape(self.content),
            x=self.position.real * scale,
            y=self.position.imag * scale,
            style=f"font-family:{font}",
            alignment__baseline="middle")
