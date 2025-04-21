from cmath import phase, pi, rect

import schemascii.components as _cs
import schemascii.component as _c
import schemascii.data_consumer as _dc
import schemascii.utils as _utils

# TODO: IEC rectangular symbol, other variable markings?
# see here: https://eepower.com/resistor-guide/resistor-standards-and-codes/resistor-symbols/  # noqa: E501


def _ansi_resistor_squiggle(t1: complex, t2: complex) -> list[complex]:
    vec = t1 - t2
    length = abs(vec)
    angle = phase(vec)
    quad_angle = angle + pi / 2
    points = [t1]
    for i in range(1, 4 * int(length)):
        points.append(t1 - rect(i / 4, angle)
                      + (rect(1/4, quad_angle) * pow(-1, i)))
    points.append(t2)
    return points


@_c.Component.define(":resistor", ("R",))
class Resistor(_cs.TwoTerminalComponent):
    options = _dc.OptionsSet([
        _dc.Option("value", str, "Resistance in ohms"),
        _dc.Option("wattage", str, "Maximum power dissipation in watts "
                   "(i.e. size of the resistor)", None)
    ])

    @property
    def value_format(self):
        return [("value", "Ω", False, self.is_variable),
                ("wattage", "W", False)]

    def render(self, **options) -> str:
        t1, t2 = self.terminals[0].pt, self.terminals[1].pt
        points = _ansi_resistor_squiggle(t1, t2)
        return (_utils.polylinegon(points, **options)
                + self.format_id_text(
                    _utils.make_text_point(t1, t2, **options), **options))


@_c.Component.define(None, ("VR", "RV"))
class VariableResistor(Resistor, _cs.VariableComponent):
    def render(self, **options):
        t1, t2 = self.terminals[0].pt, self.terminals[1].pt
        return (super().render(**options)
                + _utils.make_variable(
                    (t1 + t2) / 2, phase(t1 - t2), **options))

# TODO: potentiometers
