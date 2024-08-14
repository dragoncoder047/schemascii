from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .grid import Grid
from .refdes import RefDes
from .utils import iterate_line, perimeter


@dataclass
class Component:
    all_components: ClassVar[dict[str, type[Component]]] = {}

    rd: RefDes
    blobs: list[list[complex]]  # to support multiple parts.
    # flags: list[Flag]
    # terminals: list[Terminal]

    @classmethod
    def from_rd(cls, rd: RefDes, grid: Grid) -> Component:
        # find the right component class
        for cname in cls.all_components:
            if cname == rd.letter:
                cls = cls.all_components[cname]
                break

        # now flood-fill to find the blobs
        blobs = []
        seen = set()

        def flood(starting: list[complex], moore: bool) -> list[complex]:
            frontier = list(starting)
            out = []
            directions = [1, -1, 1j, -1j]
            if moore:
                directions.extend([-1+1j, 1+1j, -1-1j, 1-1j])
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
        for pt in perimeter(blobs[0]):
            for d in [-1+1j, 1+1j, -1-1j, 1-1j]:
                cx = pt + d
                if cx not in seen and grid.get(cx) == "#":
                    # we found another blob
                    blobs.append(flood([cx], True))
        # find all of the flags
        pass
        # done
        return cls(rd, blobs)

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

# ######         #
 # ########      ###
  # #########    #####
  # #U1G1#####   #U2A###
  # #########    #####
 # ########      ###
# ######         #
""")
    for rd in RefDes.find_all(testgrid):
        c = Component.from_rd(rd, testgrid)
        print(c)
        for blob in c.blobs:
            testgrid.spark(*blob)

    class BarComponent(Component, names=["FOO"]):
        pass