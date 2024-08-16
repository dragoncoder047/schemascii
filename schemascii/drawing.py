from __future__ import annotations

from dataclasses import dataclass

from .component import Component
from .data_parse import Data
from .errors import DiagramSyntaxError
from .grid import Grid
from .net import Net
from .refdes import RefDes


@dataclass
class Drawing:
    """A Schemascii drawing document."""

    nets: list  # [Net]
    components: list[Component]
    annotations: list  # [Annotation]
    data: Data

    @classmethod
    def parse_from_string(cls,
                          filename: str,
                          data: str | None = None,
                          **options) -> Drawing:
        if data is None:
            with open(filename) as f:
                data = f.read()
        lines = data.splitlines()
        marker = options.get("data-marker", "---")
        try:
            marker_pos = lines.index(marker)
        except ValueError as e:
            raise DiagramSyntaxError(
                "data-marker must be present in a drawing! "
                f"(current data-marker is: {marker!r})") from e
        drawing_area = "\n".join(lines[:marker_pos])
        data_area = "\n".join(lines[marker_pos+1:])
        grid = Grid(filename, drawing_area)
        nets = Net.find_all(grid)
        components = [Component.from_rd(r, grid)
                      for r in RefDes.find_all(grid)]
        # todo: annotations!
        annotations = []
        data = Data.parse_from_string(data_area, marker_pos + 1, filename)
        return cls(nets, components, annotations, data)

    def to_xml_string(self, **options) -> str:
        raise NotImplementedError
