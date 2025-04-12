from __future__ import annotations

import types
import typing
from collections import defaultdict
from dataclasses import dataclass, field

import schemascii.data_consumer as _dc
import schemascii.errors as _errors
import schemascii.grid as _grid
import schemascii.net as _net
import schemascii.refdes as _rd
import schemascii.utils as _utils
import schemascii.wire as _wire


@dataclass
class Component(_dc.DataConsumer, namespaces=(":component",)):
    """An icon representing a single electronic component."""

    all_components: typing.ClassVar[dict[str, type[Component]]] = {}

    options = [
        "inherit",
        _dc.Option("offset_scale", float,
                   "How far to offset the label from the center of the "
                   "component. Relative to the global scale option.", 1),
        _dc.Option("font", str, "Text font for labels", "monospace"),

    ]

    rd: _rd.RefDes
    blobs: list[list[complex]]  # to support multiple parts.
    terminals: list[_utils.Terminal]

    # Ellipsis can only appear at the end. this means like a wildcard meaning
    # that any other flag is suitable
    terminal_flag_opts: typing.ClassVar[
        dict[str, tuple[str | None] | types.EllipsisType]] = (None,)

    term_option: str = field(init=False)

    def __post_init__(self):
        has_any = False
        # optimized check for number of terminals if they're all the same
        available_lengths = sorted(set(map(
            len, self.terminal_flag_opts.values())))
        for optlen in available_lengths:
            if len(self.terminals) == optlen:
                break
        else:
            raise _errors.TerminalsError(
                f"Wrong number of terminals on {self.rd.name}. "
                f"Got {len(self.terminals)} but "
                f"expected {" or ".join(available_lengths)}")
        for fo_name, fo_opt in self.terminal_flag_opts.items():
            if fo_opt is ...:
                has_any = True
                continue
            t_copy = self.terminals.copy()
            t_sorted: list[_utils.Terminal] = []
            match = True
            ellipsis = False
            for opt in fo_opt:
                if opt is ...:
                    ellipsis = True
                    break
                found = [t for t in t_copy if t.flag == opt]
                if not found:
                    match = False
                    break
                t_copy.remove(found[0])
                t_sorted.append(found[0])
            if not ellipsis and t_copy:
                match = False
            if not match:
                continue
            self.terminals = t_sorted + t_copy
            self.term_option = fo_name
            return
        if not has_any:
            raise _errors.TerminalsError(
                f"Illegal terminal flags around {self.rd.name}")

    @property
    def namespaces(self) -> tuple[str, ...]:
        return self.rd.name, self.rd.short_name, self.rd.letter, ":component"

    @classmethod
    def from_rd(cls, rd: _rd.RefDes, grid: _grid.Grid) -> Component:
        """Find the outline of the component and its terminals
        on the grid, starting with the location of the reference designator.

        Will raise an error if the reference designator's letters do not
        have a corresponding renderer implemented.
        """
        # find the right component class
        for cname in cls.all_components:
            if cname == rd.letter:
                cls = cls.all_components[cname]
                break
        else:
            raise _errors.UnsupportedComponentError(rd.letter)

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
            grid, set(_utils.iterate_line(rd.left, rd.right)),
            start_orth, cont_orth, seen))
        # now find all of the auxillary blobs
        for perimeter_pt in _utils.perimeter(blobs[0]):
            for d in _utils.DIAGONAL:
                poss_aux_blob_pt = perimeter_pt + d
                if (poss_aux_blob_pt not in seen
                        and grid.get(poss_aux_blob_pt) == "#"):
                    # we found another blob
                    blobs.append(_utils.flood_walk(
                        grid, {poss_aux_blob_pt}, start_moore,
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
                    terminal_side = _utils.Side.from_phase(d)
                    if _wire.Wire.is_wire_character(ch):
                        if not any(c == -d for c in _wire.Wire.start_dirs[ch]):
                            # the terminal wire is not really connecting!
                            continue
                        # it is just a connected wire, not a flag
                        ch = None
                    else:
                        # mask the special character to be a normal wire so the
                        # wire will reach the terminal
                        if terminal_side in (_utils.Side.LEFT,
                                             _utils.Side.RIGHT):
                            mask_ch = "-"
                        else:
                            mask_ch = "|"
                        grid.setmask(poss_term_pt, mask_ch)
                    terminals.append(
                        _utils.Terminal(poss_term_pt, ch, terminal_side))
        # done
        return cls(rd, blobs, terminals)

    def __init_subclass__(cls, ids: tuple[str, ...] = None,
                          namespaces: tuple[str, ...] = None, **kwargs):
        """Register the component subclass in the component registry."""
        super().__init_subclass__(namespaces=(namespaces or ()), **kwargs)
        if not ids:
            # allow anonymous helper classes
            return
        for id_letters in ids:
            if not (id_letters.isalpha() and id_letters.upper() == id_letters):
                raise ValueError(
                    f"invalid reference designator letters: {id_letters!r}")
            if (id_letters in cls.all_components
                    and cls.all_components[id_letters] is not cls):
                raise ValueError(
                    f"duplicate reference designator letters: {id_letters!r} "
                    f"(trying to register {cls!r}, already "
                    f"occupied by {cls.all_components[id_letters]!r})")
            cls.all_components[id_letters] = cls

    @property
    def css_class(self) -> str:
        return f"component {self.rd.letter}"

    @classmethod
    def process_nets(self, nets: list[_net.Net]) -> None:
        """Hook method called to do stuff with the nets that this
        component type connects to. By default it does nothing.

        If a subclass implements this method to do something, it should
        mutate the list in-place (the return value is ignored).
        """
        pass

    def get_terminals(
            self, *flags_names: str) -> list[_utils.Terminal]:
        """Return the component's terminals sorted so that the terminals with
        the specified flags appear first in the order specified and the
        remaining terminals come after.

        Raises an error if a terminal with the specified flag could not be
        found, or there were multiple terminals with the requested flag
        (ambiguous).
        """
        out: list[_utils.Terminal] = []
        for flag in flags_names:
            matching_terminals = [t for t in self.terminals if t.flag == flag]
            if len(matching_terminals) > 1:
                raise _errors.TerminalsError(
                    f"{self.rd.name}: multiple terminals with the "
                    f"same flag {flag!r}")
            if len(matching_terminals) == 0:
                raise _errors.TerminalsError(
                    f"{self.rd.name}: need a terminal with flag {flag!r}")
            out.append(matching_terminals[0])
        out.extend(t for t in self.terminals if t.flag not in flags_names)
        assert set(self.terminals) == set(out)
        return out
