import typing

import schemascii.components as _c
import schemascii.utils as _utils


class Diode(_c.PolarizedTwoTerminalComponent, _c.SiliconComponent,
            ids=("D", "CR")):

    always_polarized: typing.Final = True

    def render(self, **options) -> str:
        raise NotImplementedError
        return (_utils.bunch_o_lines(lines, **options)
                + (_utils.make_plus(self.terminals, mid, angle, **options)
                   if self.is_polarized else "")
                + self.format_id_text(
                    _utils.make_text_point(t1, t2, **options), **options))


class LED(Diode, ids=("LED", "IR")):
    def render(self, **options):
        raise NotImplementedError

# TODO: zener diode, Schottky diode, DIAC, varactor, photodiode
