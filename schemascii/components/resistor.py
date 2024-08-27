from cmath import phase, pi, rect

import schemascii.components as _c
import schemascii.data_consumer as _dc
import schemascii.utils as _utils
import schemascii.errors as _errors

# TODO: IEC rectangular symbol
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


class Resistor(_c.TwoTerminalComponent, ids=("R",), namespaces=(":resistor",)):
    options = [
        "inherit",
        _dc.Option("value", str, "Resistance in ohms"),
        _dc.Option("power", str, "Maximum power dissipation in watts "
                   "(i.e. size of the resistor)", None)
    ]

    is_variable = False

    def render(self, value: str, power: str, **options) -> str:
        t1, t2 = self.terminals[0].pt, self.terminals[1].pt
        points = _ansi_resistor_squiggle(t1, t2)
        try:
            id_text = _utils.id_text(self.rd.name, self.terminals,
                                     ((value, "Ω", False, self.is_variable),
                                      (power, "W", False)),
                                     _utils.make_text_point(t1, t2, **options),
                                     **options)
        except ValueError as e:
            raise _errors.BOMError(
                f"{self.rd.name}: Range of values not allowed "
                "on fixed resistor") from e
        return _utils.polylinegon(points, **options) + id_text


class VariableResistor(Resistor, ids=("VR", "RV")):
    is_variable = True

    def render(self, **options):
        t1, t2 = self.terminals[0].pt, self.terminals[1].pt
        return (super().render(**options)
                + _utils.make_variable(
                    (t1 + t2) / 2, phase(t1 - t2), **options))

# TODO: potentiometers


if __name__ == "__main__":
    print(Resistor.all_components)
