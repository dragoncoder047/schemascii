from cmath import phase, rect

import schemascii.components as _c
import schemascii.data_consumer as _dc
import schemascii.utils as _utils


class Battery(_c.PolarizedTwoTerminalComponent, _c.SimpleComponent,
              ids=("B", "BT", "BAT"), namespaces=(":battery",)):
    options = [
        "inherit",
        _dc.Option("value", str, "Battery voltage"),
        _dc.Option("capacity", str, "Battery capacity in amp-hours", None)
    ]

    @property
    def value_format(self):
        return [("value", "V", True, self.is_variable),
                ("capacity", "Ah", False)]

    def render(self, **options) -> str:
        t1, t2 = self.terminals[0].pt, self.terminals[1].pt
        mid = (t1 + t2) / 2
        angle = phase(t1 - t2)
        lines = [
            (t1, mid + rect(0.5, angle)),
            (t2, mid + rect(-0.5, angle)),
            *_utils.deep_transform(
                [
                    (complex(0.5, 0.5), complex(-0.5, 0.5)),
                    (complex(0.25, 0.16), complex(-0.25, 0.16)),
                    (complex(0.5, -0.16), complex(-0.5, -0.16)),
                    (complex(0.25, -0.5), complex(-0.25, -0.5)),
                ],
                mid,
                angle)
        ]
        return (_utils.bunch_o_lines(lines, **options)
                + self.format_id_text(
                    _utils.make_text_point(t1, t2, **options), **options))
