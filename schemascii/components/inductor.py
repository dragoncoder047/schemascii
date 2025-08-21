from cmath import phase, rect

import schemascii.components as _cs
import schemascii.component as _c
import schemascii.data_consumer as _dc
import schemascii.utils as _utils
import schemascii.svg as _svg

# TODO: add dot on + end if inductor is polarized


@_c.Component.define(":inductor", ("L",))
class Inductor(_cs.PolarizedTwoTerminalComponent):
    options = _dc.OptionsSet([
        _dc.Option("value", str, "Inductance in henries"),
        _dc.Option("current", str, "Maximum current rating in amps", None)
    ])

    @property
    def value_format(self):
        return [("value", "H", False, self.is_variable),
                ("current", "A", False)]

    def render(self, **options) -> str:
        t1, t2, _, _ = self._t4()
        vec = t1 - t2
        length = abs(vec)
        angle = phase(vec)
        scale = options["scale"]
        data = f"M{t1.real * scale} {t1.imag * scale}"
        d = rect(scale, angle)
        for _ in range(int(length)):
            data += f"a1 1 0 01 {-d.real} {d.imag}"
        return (
            _svg.path(data, "transparent", options["linewidth"],
                      options["color"])
            + self.format_id_text(None, **options))


@_c.Component.define(None, ("VL", "LV"))
class VariableInductor(Inductor, _cs.VariableComponent):
    def render(self, **options):
        _, _, mid, angle = self._t4()
        return (super().render(**options)
                + _utils.make_variable(mid, angle, **options))
