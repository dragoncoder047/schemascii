from cmath import phase, rect

import schemascii.components as _cs
import schemascii.component as _c
import schemascii.data_consumer as _dc
import schemascii.utils as _utils
import schemascii.svg as _svg

# TODO: add dot on + end if inductor is polarized


@_c.Component.define(("L",))
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
        t1, t2 = self.terminals[0].pt, self.terminals[1].pt
        vec = t1 - t2
        length = abs(vec)
        angle = phase(vec)
        scale = options["scale"]
        data = f"M{t1.real * scale} {t1.imag * scale}"
        d = rect(scale, angle)
        for _ in range(int(length)):
            data += f"a1 1 0 01 {-d.real} {d.imag}"
        return (
            _svg.path(data, "transparent", options["stroke_width"],
                      options["stroke"])
            + self.format_id_text(
                _utils.make_text_point(t1, t2, **options), **options))


@_c.Component.define(("VL", "LV"))
class VariableInductor(Inductor):
    is_variable = True

    def render(self, **options):
        t1, t2 = self.terminals[0].pt, self.terminals[1].pt
        return (super().render(**options)
                + _utils.make_variable(
                    (t1 + t2) / 2, phase(t1 - t2), **options))
