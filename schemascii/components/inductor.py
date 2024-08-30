from cmath import phase, rect

import schemascii.components as _c
import schemascii.data_consumer as _dc
import schemascii.utils as _utils


class Inductor(_c.PolarizedTwoTerminalComponent, _c.SimpleComponent,
               ids=("L",), namespaces=(":inductor",)):
    options = [
        "inherit",
        _dc.Option("value", str, "Inductance in henries"),
        _dc.Option("current", str, "Maximum current rating in amps", None)
    ]

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
            _utils.XML.path(d=data, stroke=options["stroke"],
                            fill="transparent",
                            stroke__width=options["stroke_width"])
            + self.format_id_text(
                _utils.make_text_point(t1, t2, **options), **options))


class VariableInductor(Inductor, ids=("VL", "LV")):
    is_variable = True

    def render(self, **options):
        t1, t2 = self.terminals[0].pt, self.terminals[1].pt
        return (super().render(**options)
                + _utils.make_variable(
                    (t1 + t2) / 2, phase(t1 - t2), **options))
