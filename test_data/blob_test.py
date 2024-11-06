import collections as _collections

strings = [
    """
#
###
#####
#######
#####
###
#
""",
    """
#
#
#
##
##
##
###
##
##
##
#
#
#
""",
    """
#
#
#
##
##
##
###
######
#########
######
###
##
##
##
#
#
#
""",
    """
#
 #
  #
  #
  #
 #
#"""]


def sinker(pts: list[complex]) -> list[complex]:
    last = None
    out = []
    for p in pts:
        if not last or last.real != p.real:
            out.append(p)
            last = p
    out.append(p)
    return out


def get_outline_points(pts: list[complex]) -> list[complex]:
    by_y = _collections.defaultdict(list)
    for p in pts:
        by_y[p.imag].append(p.real)
    left_side = sinker([complex(min(row), y)
                       for y, row in sorted(by_y.items())])
    right_side = sinker([complex(max(row), y)
                         for y, row in sorted(by_y.items(), reverse=True)])

    return left_side + right_side


def example(all_points: list[complex], scale: float = 20) -> str:
    p = get_outline_points(all_points)
    vbx = max(map(lambda x: x.real, p))
    vby = max(map(lambda x: x.imag, p))
    return f"""<svg
    viewBox="-1 -1 {vbx + 1} {vby + 1}"
    width="{vbx * scale}"
    height="{vby * scale}">
    <polyline
    fill="none"
    stroke="black"
    stroke-width="0.1"
    points="{" ".join(map(lambda x: f"{x.real},{x.imag}", p))}">
    </polyline></svg>"""


for s in strings:
    pts = [complex(c, r)
           for (r, rt) in enumerate(s.splitlines())
           for (c, ch) in enumerate(rt)
           if ch == "#"]
    print(example(pts))
