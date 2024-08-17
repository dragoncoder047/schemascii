from __future__ import annotations

from dataclasses import dataclass

import schemascii.component as _component
import schemascii.data_parse as _data
import schemascii.errors as _errors
import schemascii.grid as _grid
import schemascii.net as _net
import schemascii.refdes as _rd


@dataclass
class Drawing:
    """A Schemascii drawing document."""

    nets: list  # [Net]
    components: list[_component.Component]
    annotations: list  # [Annotation]
    data: _data.Data

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
            raise _errors.DiagramSyntaxError(
                "data-marker must be present in a drawing! "
                f"(current data-marker is: {marker!r})") from e
        drawing_area = "\n".join(lines[:marker_pos])
        data_area = "\n".join(lines[marker_pos+1:])
        grid = _grid.Grid(filename, drawing_area)
        nets = _net.Net.find_all(grid)
        components = [_component.Component.from_rd(r, grid)
                      for r in _rd.RefDes.find_all(grid)]
        # todo: annotations!
        annotations = []
        data = _data.Data.parse_from_string(
            data_area, marker_pos + 1, filename)
        return cls(nets, components, annotations, data)

    def to_xml_string(self, **options) -> str:
        raise NotImplementedError
