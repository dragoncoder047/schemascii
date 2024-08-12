from __future__ import annotations


class Drawing:
    """A Schemascii drawing document."""

    def __init__(
            self,
            wire_nets,  # list of nets of wires
            components,  # list of components found
            annotations,  # boxes, lines, comments, etc
            data):
        self.nets = wire_nets
        self.components = components
        self.annotations = annotations
        self.data = data

    @classmethod
    def parse_from_string(cls, data: str, **options) -> Drawing:
        lines = data.splitlines()
        marker = options.get("data-marker", "---")
        try:
            marker_pos = lines.index(marker)
        except ValueError:
            raise SyntaxError(
                "data-marker must be present in a drawing! "
                f"(current data-marker is: {marker!r})")
        drawing_area = "\n".join(lines[:marker_pos])
        data_area = "\n".join(lines[marker_pos+1:])
        raise NotImplementedError

    def to_xml_string(self, **options) -> str:
        raise NotImplementedError
