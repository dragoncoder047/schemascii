from __future__ import annotations

from collections import defaultdict
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

        start_orth = defaultdict(
            lambda: _utils.ORTHAGONAL)
        start_moore = defaultdict(
            lambda: _utils.ORTHAGONAL + _utils.DIAGONAL)
        cont_orth = defaultdict(lambda: None, {"#": _utils.EVERYWHERE})
        cont_moore = defaultdict(lambda: None, {"#": _utils.EVERYWHERE_MOORE})

        # add in the RD's bounds and find the main blob
        blobs.append(_utils.flood_walk(
            grid, list(_utils.iterate_line(rd.left, rd.right)),
            start_orth, cont_orth, seen))
        # now find all of the auxillary blobs
        for perimeter_pt in _utils.perimeter(blobs[0]):
            for d in _utils.DIAGONAL:
                poss_aux_blob_pt = perimeter_pt + d
                if (poss_aux_blob_pt not in seen
                        and grid.get(poss_aux_blob_pt) == "#"):
                    # we found another blob
                    blobs.append(_utils.flood_walk(
                        grid, [poss_aux_blob_pt], start_moore,
                        cont_moore, seen))
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
                    if not any(c == -d for c in _wire.Wire.start_dirs[nch]):
                        # the connecting wire is not really connecting!
                        continue
                    if any(t.pt == poss_term_pt for t in terminals):
                        # already found this one
                        continue
                    if _wire.Wire.is_wire_character(ch):
                        if not any(c == -d for c in _wire.Wire.start_dirs[ch]):
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
    testgrid = _grid.Grid("test_data/stresstest.txt")
    # this will erroneously search the DATA section too but that's OK
    # for this test
    for rd in _rd.RefDes.find_all(testgrid):
        c = Component.from_rd(rd, testgrid)
        print(c)
        for blob in c.blobs:
            testgrid.spark(*blob)
        testgrid.spark(*(t.pt for t in c.terminals))
