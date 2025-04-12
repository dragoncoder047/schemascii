import typing

import schemascii.components as _c
import schemascii.data_consumer as _dc
import schemascii.utils as _utils


class Diode(_c.PolarizedTwoTerminalComponent, _c.SimpleComponent,
            ids=("D", "CR"), namespaces=(":diode",)):

    always_polarized: typing.Final = True

    options = [
        "inherit",
        _dc.Option("voltage", str, "Maximum reverse voltage rating", None),
        _dc.Option("current", str, "Maximum current rating", None)
    ]

    @property
    def value_format(self):
        return [("voltage", "V", False),
                ("current", "A", False)]

    def render(self, **options) -> str:
        raise NotImplementedError
        return (_utils.bunch_o_lines(lines, **options)
                + (_utils.make_plus(self.terminals, mid, angle, **options)
                   if self.is_polarized else "")
                + self.format_id_text(
                    _utils.make_text_point(t1, t2, **options), **options))


class LED(Diode, ids=("LED", "IR"), namespaces=(":diode", ":led")):
    def render(self, **options):
        raise NotImplementedError
