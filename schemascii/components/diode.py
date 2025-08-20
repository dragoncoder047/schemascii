from cmath import rect

import schemascii.component as _c
import schemascii.components as _cs
import schemascii.utils as _utils
import schemascii.data_consumer as _dc


@_c.Component.define(":diode", ("D", "CR"))
class Diode(_cs.PolarizedTwoTerminalComponent, _cs.SiliconComponent):
    always_polarized = True

    def get_lines(self, **_options) -> list[complex]:
        t1, t2, mid, angle = self._t4()
        return [
            (t2, mid + rect(0.3, angle)),
            (t1, mid + rect(-0.3, angle)),
            _utils.deep_transform((-0.3 - 0.3j, 0.3 - 0.3j), mid, angle),
        ]

    def get_triangle(self) -> list[complex]:
        _, _, mid, angle = self._t4()
        return _utils.deep_transform(
            (-0.3j, 0.3 + 0.3j, -0.3 + 0.3j), mid, angle)

    def render(self, **options) -> str:
        return (_utils.bunch_o_lines(self.get_lines(**options), **options)
                + _utils.polylinegon(self.get_triangle(), True,
                                     **(options
                                         | {"fill": options.get("color")}))
                + self.format_id_text(None, **options))


@_c.Component.define(None, ("LED", "IR"))
class LED(Diode):
    options = _dc.OptionsSet([
        _dc.Option("color", str, "Color / wavelength of the LED"),
    ])

    def get_lines(self, **options):
        _, _, mid, angle = self._t4()
        return super().get_lines() + _utils.light_arrows(
            mid, angle, True, **options)

# TODO: zener diode, Schottky diode, DIAC, varactor, photodiode
