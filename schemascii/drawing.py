from __future__ import annotations

from dataclasses import dataclass

import schemascii.annotation as _a
import schemascii.component as _component
import schemascii.data_parse as _data
import schemascii.errors as _errors
import schemascii.grid as _grid
import schemascii.net as _net
import schemascii.refdes as _rd


@dataclass
class Drawing:
    """A Schemascii drawing document."""

    nets: list[_net.Net]
    components: list[_component.Component]
    annotations: list[_a.Annotation]
    data: _data.Data
    grid: _grid.Grid

    @classmethod
    def load(cls,
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
        annotations = _a.Annotation.find_all(grid)
        data = _data.Data.parse_from_string(
            data_area, marker_pos, filename)
        grid.clrall()
        return cls(nets, components, annotations, data, grid)

    def to_xml_string(self, **options) -> str:
        raise NotImplementedError


if __name__ == '__main__':
    import pprint
    import itertools
    d = Drawing.load("test_data/stresstest.txt")
    pprint.pprint(d)
    for net in d.nets:
        print("\n---net---")
        for wire in net.wires:
            d.grid.spark(*wire.points)
    for comp in d.components:
        print("\n---component---")
        pprint.pprint(comp)
        d.grid.spark(*itertools.chain.from_iterable(comp.blobs))
        for t in comp.terminals:
            d.grid.spark(t.pt)
            print()
