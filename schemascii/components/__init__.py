import typing
from dataclasses import dataclass

import schemascii.component as _c
import schemascii.errors as _errors

# TODO: import all of the component subclasses to register them


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
    """Shortcut to define a component with two terminals."""
    n_terminals: typing.Final = 2


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
