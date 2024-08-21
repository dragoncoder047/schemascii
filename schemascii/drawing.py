from __future__ import annotations

from dataclasses import dataclass

import schemascii.annoline as _annoline
import schemascii.annotation as _a
import schemascii.component as _component
import schemascii.data as _data
import schemascii.errors as _errors
import schemascii.grid as _grid
import schemascii.net as _net
import schemascii.refdes as _rd
import schemascii.utils as _utils


@dataclass
class Drawing:
    """A Schemascii drawing document."""

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
                "data-marker must be present in a drawing! "
                f"(current data-marker is: {data_marker!r})") from e
        drawing_area = "\n".join(lines[:marker_pos])
        data_area = "\n".join(lines[marker_pos+1:])
        grid = _grid.Grid(filename, drawing_area)
        nets = _net.Net.find_all(grid)
        components = [_component.Component.from_rd(r, grid)
                      for r in _rd.RefDes.find_all(grid)]
        annotations = _a.Annotation.find_all(grid)
        annotation_lines = _annoline.AnnotationLine.find_all(grid)
        data = _data.Data.parse_from_string(
            data_area, marker_pos, filename)
        grid.clrall()
        return cls(nets, components, annotations, annotation_lines, data, grid)

    def to_xml_string(self, fudge: _data.Data | None = None) -> str:
        """Render the entire diagram to a string and return the <svg> element.
        """
        data = self.data
        if fudge:
            data |= fudge
        scale = data.getopt("*", "scale", 10)
        padding = data.getopt("*", "padding", 10)
        content = ""
        raise NotImplementedError
        return _utils.XML.svg(
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
    d = Drawing.from_file("test_data/stresstest.txt")
    pprint.pprint(d)
    print(d.to_xml_string())
