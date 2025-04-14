from __future__ import annotations
import typing
from dataclasses import dataclass

import schemascii.component as _c
import schemascii.errors as _errors
import schemascii.utils as _utils
import schemascii.data_consumer as _dc


class SimpleComponent(_c.Component):
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
class TwoTerminalComponent(SimpleComponent):
    """Shortcut to define a component with two terminals."""
    terminal_flag_opts: typing.ClassVar = {"ok": (None, None)}
    is_variable: typing.ClassVar = False


@dataclass
class PolarizedTwoTerminalComponent(TwoTerminalComponent):
    """Helper class that ensures that a component has only two terminals,
    and if provided, sorts the terminals so that the "+" terminal comes
    first in the list.
    """

    always_polarized: typing.ClassVar[bool] = False

    @property
    def terminal_flags_opts(self):
        if self.always_polarized:
            return {"polarized": ("+", None)}
        return {"polarized": ("+", None), "unpolarized": (None, None)}


@dataclass
class SiliconComponent(_c.Component):
    """Class for a part that doesn't have a traditional Metric value that
    defines its behavior, but only a specific part number.
    """

    options = _dc.OptionsSet([
        _dc.Option("part-number", str, "The manufacturer-specified part "
                   "number (e.g. NE555P, 2N7000, L293D, ATtiny85, etc.)")
    ])
