from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import schemascii.grid as _grid
import schemascii.refdes as _rd
import schemascii.utils as _utils
import schemascii.wire as _wire


@dataclass
class Component:
    all_components: ClassVar[dict[str, type[Component]]] = {}

    rd: _rd.RefDes
    blobs: list[list[complex]]  # to support multiple parts.
    terminals: list[_utils.Terminal]

    @classmethod
    def from_rd(cls, rd: _rd.RefDes, grid: _grid.Grid) -> Component:
        # find the right component class
        for cname in cls.all_components:
            if cname == rd.letter:
                cls = cls.all_components[cname]
                break

        # now flood-fill to find the blobs
        blobs: list[list[complex]] = []
        seen: set[complex] = set()

        def flood(starting: list[complex], moore: bool) -> list[complex]:
            frontier = list(starting)
            out: list[complex] = []
            directions = _utils.ORTHAGONAL
            if moore:
                directions += _utils.DIAGONAL
            while frontier:
                point = frontier.pop(0)
                out.append(point)
                seen.add(point)
                for d in directions:
                    newpoint = point + d
                    if grid.get(newpoint) != "#":
                        continue
                    if newpoint not in seen:
                        frontier.append(newpoint)
            return out

        # add in the RD's bounds and find the main blob
        blobs.append(flood(_utils.iterate_line(rd.left, rd.right), False))
        # now find all of the auxillary blobs
        for perimeter_pt in _utils.perimeter(blobs[0]):
            for d in _utils.DIAGONAL:
                poss_aux_blob_pt = perimeter_pt + d
                if (poss_aux_blob_pt not in seen
                        and grid.get(poss_aux_blob_pt) == "#"):
                    # we found another blob
                    blobs.append(flood([poss_aux_blob_pt], True))
        # find all of the terminals
        terminals: list[_utils.Terminal] = []
        for perimeter_pt in _utils.perimeter(seen):
            # these get masked with wires because they are like wires
            for d in _utils.ORTHAGONAL:
                poss_term_pt = perimeter_pt + d
                if poss_term_pt in seen:
                    continue
                ch = grid.get(poss_term_pt)
                if ch != "#" and not ch.isspace():
                    # candidate for terminal
                    # look to see if a wire connects
                    # to it in the expected direction
                    nch = grid.get(d + poss_term_pt)
                    if not _wire.Wire.is_wire_character(nch):
                        # no connecting wire - must just be something
                        # like a close packed neighbor component or other junk
                        continue
                    if not any(_wire.CHAR2DIR[c] == -d
                               for c in _wire.Wire.start_dirs[nch]):
                        # the connecting wire is not really connecting!
                        continue
                    if any(t.pt == poss_term_pt for t in terminals):
                        # already found this one
                        continue
                    if _wire.Wire.is_wire_character(ch):
                        if not any(_wire.CHAR2DIR[c] == -d
                                   for c in _wire.Wire.start_dirs[ch]):
                            # the terminal wire is not really connecting!
                            continue
                        # it is just a connected wire, not a flag
                        ch = None
                    terminals.append(_utils.Terminal(
                        poss_term_pt, ch, _utils.Side.from_phase(d)))
        # done
        return cls(rd, blobs, terminals)

    def __init_subclass__(cls, names: list[str]):
        """Register the component subclass in the component registry."""
        for name in names:
            if not (name.isalpha() and name.upper() == name):
                raise ValueError(
                    f"invalid reference designator letters: {name!r}")
            if name in cls.all_components:
                raise ValueError(
                    f"duplicate reference designator letters: {name!r}")
            cls.all_components[name] = cls


if __name__ == '__main__':
    class FooComponent(Component, names=["U", "FOO"]):
        pass

    print(Component.all_components)

    testgrid = _grid.Grid("", """

  [xor gate]     [op amp]

    # ######                   #
     # ########                ###
  ----# #########         ----+#####
      # #U1G1#####----         #U2A###-----
  ----# #########         -----#####
     # ########                ###
    # ######                   #
""")
    for rd in _rd.RefDes.find_all(testgrid):
        c = Component.from_rd(rd, testgrid)
        print(c)
        for blob in c.blobs:
            testgrid.spark(*blob)
        testgrid.spark(*(t.pt for t in c.terminals))
