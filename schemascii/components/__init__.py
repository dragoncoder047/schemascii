from __future__ import annotations
import typing
from dataclasses import dataclass

import schemascii.component as _c
import schemascii.errors as _errors
import schemascii.utils as _utils


class SimpleComponent:
    """Component mixin class that simplifies the formatting
    of the various values and their units into the id_text.
    """

    value_format: typing.ClassVar[list[tuple[str, str]
                                       | tuple[str, str, bool]
                                       | tuple[str, str, bool, bool]]]

    def format_id_text(self: _c.Component | SimpleComponent,
                       textpoint: complex, **options):
        val_fmt = []
        for valsch in self.value_format:
            val_fmt.append((options[valsch[0]], *valsch[1:]))
        try:
            id_text = _utils.id_text(self.rd.name, self.terminals,
                                     val_fmt, textpoint, **options)
        except ValueError as e:
            raise _errors.BOMError(
                f"{self.rd.name}: Range of values not allowed "
                "on fixed-value component") from e
        return id_text


@dataclass
class NTerminalComponent(_c.Component):
    """Represents a component that only ever has N terminals.

    The class must have an attribute n_terminals with the number
    of terminals."""
    n_terminals: typing.ClassVar[int]

    def __post_init__(self):
        if self.n_terminals != len(self.terminals):
            raise _errors.TerminalsError(
                f"{self.rd.name}: can only have {self.n_terminals} terminals "
                f"(found {len(self.terminals)})")


class TwoTerminalComponent(NTerminalComponent):
    """Shortcut to define a component with two terminals, and one primary
    value, that may or may not be variable."""
    n_terminals: typing.Final[int] = 2
    is_variable: typing.ClassVar[bool] = False


@dataclass
class PolarizedTwoTerminalComponent(TwoTerminalComponent):
    """Helper class that ensures that a component has only two terminals,
    and if provided, sorts the terminals so that the "+" terminal comes
    first in the list.
    """

    always_polarized: typing.ClassVar[bool] = False

    def __post_init__(self):
        super().__post_init__()  # check count of terminals
        num_plus = sum(t.flag == "+" for t in self.terminals)
        if (self.always_polarized and num_plus != 1) or num_plus > 1:
            raise _errors.TerminalsError(
                f"{self.rd.name}: need '+' on only one terminal to indicate "
                "polarization")
        if self.terminals[1].flag == "+":
            # swap first and last
            self.terminals.insert(0, self.terminals.pop(-1))

    @property
    def is_polarized(self) -> bool:
        return any(t.flag == "+" for t in self.terminals)
