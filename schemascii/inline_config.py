import re
from .grid import Grid

INLINE_CONFIG_RE = re.compile(r"!([a-z]+)=([^!]*)!", re.I)


def get_inline_configs(grid: Grid) -> dict:
    out = {}
    for y, line in enumerate(grid.lines):
        for m in INLINE_CONFIG_RE.finditer(line):
            interval = m.span()
            key = m.group(1)
            val = m.group(2)
            for x in range(*interval):
                grid.setmask(complex(x, y))
            try:
                val = float(val)
            except ValueError:
                pass
            out[key] = val
    return out


if __name__ == '__main__':
    g = Grid("null",
             """
foobar -------C1-------
!padding=30!!label=!
!foobar=bar!
""")
    print(get_inline_configs(g))
    print(g)
