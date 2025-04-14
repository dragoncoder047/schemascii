import typing

import schemascii.component as _c
import schemascii.components as _cs
import schemascii.utils as _utils


@_c.Component.define(("D", "CR"))
class Diode(_cs.PolarizedTwoTerminalComponent, _cs.SiliconComponent):

    always_polarized: typing.Final = True

    def render(self, **options) -> str:
        raise NotImplementedError
        return (_utils.bunch_o_lines(lines, **options)
                + (_utils.make_plus(self.terminals, mid, angle, **options)
                   if self.is_polarized else "")
                + self.format_id_text(
                    _utils.make_text_point(t1, t2, **options), **options))


@_c.Component.define(("LED", "IR"))
class LED(Diode):
    def render(self, **options):
        raise NotImplementedError

# TODO: zener diode, Schottky diode, DIAC, varactor, photodiode
