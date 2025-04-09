from __future__ import annotations

import typing
from dataclasses import dataclass

import schemascii.annoline as _annoline
import schemascii.annotation as _a
import schemascii.component as _component
import schemascii.data as _data
import schemascii.data_consumer as _dc
import schemascii.errors as _errors
import schemascii.grid as _grid
import schemascii.net as _net
import schemascii.refdes as _rd
import schemascii.svg_utils as _svg


@dataclass
class Drawing(_dc.DataConsumer, namespaces=(":root",)):
    """A Schemascii drawing document."""

    options = [
        ("scale",),
        _dc.Option("padding", float,
                   "Margin around the border of the drawing", 10),
    ]

    nets: list[_net.Net]
    components: list[_component.Component]
    annotations: list[_a.Annotation]
    annotation_lines: list[_annoline.AnnotationLine]
    data: _data.Data
    grid: _grid.Grid

    @classmethod
    def from_file(cls,
                  filename: str,
                  data: str | None = None,
                  *,
                  data_marker: str = "---") -> Drawing:
        """Loads the Schemascii diagram from a file.

        If data is not provided, the file at filename is read in
        text mode.

        The data_marker argument is the sigil line that separates the
        graphics section from the data section.
        """
        if data is None:
            with open(filename) as f:
                data = f.read()
        lines = data.splitlines()
        try:
            marker_pos = lines.index(data_marker)
        except ValueError as e:
            raise _errors.DiagramSyntaxError(
                "data_marker must be present in a drawing! "
                f"(current data_marker is: {data_marker!r})") from e
        drawing_area = "\n".join(lines[:marker_pos])
        data_area = "\n".join(lines[marker_pos+1:])
        # find everything
        grid = _grid.Grid(filename, drawing_area)
        nets = _net.Net.find_all(grid)
        components = [_component.Component.from_rd(r, grid)
                      for r in _rd.RefDes.find_all(grid)]
        annotations = _a.Annotation.find_all(grid)
        annotation_lines = _annoline.AnnotationLine.find_all(grid)
        data = _data.Data.parse_from_string(
            data_area, marker_pos, filename)
        # process nets
        for comp in components:
            comp.process_nets(nets)
        grid.clrall()
        return cls(nets, components, annotations, annotation_lines, data, grid)

    def to_xml_string(
            self,
            fudge: _data.Data | dict[str, typing.Any] | None = None) -> str:
        """Render the entire diagram to a string and return the <svg> element.
        """
        data = self.data
        if fudge:
            data |= fudge
        return super().to_xml_string(data)

    def render(self, data, scale: float, padding: float, **options) -> str:
        # render everything
        content = _svg.group(
            _svg.group(
                *(net.to_xml_string(data) for net in self.nets),
                class_="wires"),
            _svg.group(
                *(comp.to_xml_string(data) for comp in self.components),
                class_="components"),
            class_="electrical")
        content += _svg.group(
            *(line.to_xml_string(data) for line in self.annotation_lines),
            *(anno.to_xml_string(data) for anno in self.annotations),
            class_="annotations")
        return _svg.group(
            content,
            width=self.grid.width * scale + padding * 2,
            height=self.grid.height * scale + padding * 2,
            viewBox=f"{-padding} {-padding} "
            f"{self.grid.width * scale + padding * 2} "
            f"{self.grid.height * scale + padding * 2}",
            xmlns="http://www.w3.org/2000/svg",
            class_="schemascii")


if __name__ == '__main__':
    import pprint
    print("All components: ", end="")
    pprint.pprint(_component.Component.all_components)
    print("All namespaces: ", end="")
    pprint.pprint(_data.Data.available_options)
    d = Drawing.from_file("test_data/stresstest.txt")
    pprint.pprint(d)
    print(d.to_xml_string())
