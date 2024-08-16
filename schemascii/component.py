from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .grid import Grid
from .refdes import RefDes
from .utils import (DIAGONAL, ORTHAGONAL, Side, Terminal, iterate_line,
                    perimeter)
from .wire import Wire


@dataclass
class Component:
    all_components: ClassVar[dict[str, type[Component]]] = {}

    rd: RefDes
    blobs: list[list[complex]]  # to support multiple parts.
    terminals: list[Terminal]

    @classmethod
    def from_rd(cls, rd: RefDes, grid: Grid) -> Component:
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
            directions = ORTHAGONAL
            if moore:
                directions += DIAGONAL
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
        blobs.append(flood(iterate_line(rd.left, rd.right), False))
        # now find all of the auxillary blobs
        for perimeter_pt in perimeter(blobs[0]):
            for d in DIAGONAL:
                poss_aux_blob_pt = perimeter_pt + d
                if (poss_aux_blob_pt not in seen
                        and grid.get(poss_aux_blob_pt) == "#"):
                    # we found another blob
                    blobs.append(flood([poss_aux_blob_pt], True))
        # find all of the terminals
        terminals: list[Terminal] = []
        for perimeter_pt in perimeter(seen):
            # these get masked with wires because they are like wires
            for d in ORTHAGONAL:
                poss_term_pt = perimeter_pt + d
                ch = grid.get(poss_term_pt)
                if ch != "#" and not ch.isspace():
                    # candidate for terminal
                    # search around again to see if a wire connects
                    # to it
                    for d in ORTHAGONAL:
                        if (grid.get(d + poss_term_pt)
                                in Wire.starting_directions.keys()):
                            # there is a neighbor with a wire, so it must
                            # be a terminal
                            break
                            # now d holds the direction of the terminal
                    else:
                        # no nearby wires - must just be something
                        # like the reference designator or other junk
                        continue
                    if any(t.pt == poss_term_pt for t in terminals):
                        # already found this one
                        continue
                    if ch in Wire.starting_directions.keys():
                        # it is just a connected wire, not a flag
                        ch = None
                    else:
                        # mask the wire
                        grid.setmask(poss_term_pt, "*")
                    terminals.append(
                        Terminal(poss_term_pt, ch, Side.from_phase(d)))
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

    testgrid = Grid("", """

  [xor gate]     [op amp]

    # ######                   #
     # ########                ###
  ----# #########         ----+#####
      # #U1G1#####----         #U2A###-----
  ----# #########         -----#####
     # ########                ###
    # ######                   #
""")
    for rd in RefDes.find_all(testgrid):
        c = Component.from_rd(rd, testgrid)
        print(c)
        for blob in c.blobs:
            testgrid.spark(*blob)
        testgrid.spark(*(t.pt for t in c.terminals))
