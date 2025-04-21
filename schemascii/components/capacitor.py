from cmath import phase, rect

import schemascii.component as _c
import schemascii.components as _cs
import schemascii.data_consumer as _dc
import schemascii.utils as _utils


@_c.Component.define(":capacitor", ("C"))
class Capacitor(_cs.PolarizedTwoTerminalComponent):
    options = _dc.OptionsSet([
        _dc.Option("value", str, "Capacitance in farads"),
        _dc.Option("voltage", str, "Maximum voltage tolerance in volts", None)
    ])

    @property
    def value_format(self):
        return [("value", "F", True, self.is_variable),
                ("voltage", "V", False)]

    def render(self, **options) -> str:
        t1, t2 = self.terminals[0].pt, self.terminals[1].pt
        mid = (t1 + t2) / 2
        angle = phase(t1 - t2)
        lines = [
            (t1, mid + rect(1/4, angle)),
            (t2, mid + rect(-1/4, angle)),
            *_utils.deep_transform([
                (.4+.25j, -.4+.25j),
                (.4-.25j, -.4-.25j)
            ], mid, angle)
        ]
        return (_utils.bunch_o_lines(lines, **options)
                + (_utils.make_plus(self.terminals, mid, angle, **options)
                   if self.term_option == "polarized" else "")
                + self.format_id_text(
                    _utils.make_text_point(t1, t2, **options), **options))


@_c.Component.define(None, ("VC", "CV"))
class VariableCapacitor(Capacitor, _cs.VariableComponent):
    def render(self, **options):
        t1, t2 = self.terminals[0].pt, self.terminals[1].pt
        return (super().render(**options)
                + _utils.make_variable(
                    (t1 + t2) / 2, phase(t1 - t2), **options))
