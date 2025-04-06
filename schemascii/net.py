from __future__ import annotations

from dataclasses import dataclass

import schemascii.data_consumer as _dc
import schemascii.grid as _grid
import schemascii.wire as _wire
import schemascii.wire_tag as _wt


@dataclass
class Net(_dc.DataConsumer, namespaces=(":net",)):
    """Grouping of wires that are
    electrically connected.
    """

    wires: list[_wire.Wire]

    @classmethod
    def find_all(cls, grid: _grid.Grid) -> list[Net]:
        """Return a list of all the wire nets found on the grid.
        """
        seen_points: set[complex] = set()
        all_nets: list[Net] = []
        all_tags = _wt.WireTag.find_all(grid)

        for y, line in enumerate(grid.lines):
            for x, ch in enumerate(line):
                if _wire.Wire.is_wire_character(ch):
                    wire = _wire.Wire.get_from_grid(
                        grid, complex(x, y), all_tags)
                    if all(p in seen_points for p in wire.points):
                        continue
                    # find existing net or make a new one
                    for net in all_nets:
                        if any(w.tag is not None
                               and wire.tag is not None
                               and w.tag.name == wire.tag.name
                               for w in net.wires):
                            net.wires.append(wire)
                            break
                    else:
                        all_nets.append(cls([wire]))
                    seen_points.update(wire.points)
        return all_nets

    def render(self, data) -> str:
        return "".join(w.to_xml_string(data) for w in self.wires)


if __name__ == '__main__':
    g = _grid.Grid("", """
=wrap1>------C1------=wrap1>
<wrap2=------C2------<wrap3=
""")
    nets = Net.find_all(g)
    for net in nets:
        print("---NET---")
        for wire in net.wires:
            g.spark(*wire.points)
