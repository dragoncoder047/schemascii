import cmath

s = """
#
###
#####
#######
#####
###
#
"""
pts = [complex(c, r)
       for (r, rt) in enumerate(s.splitlines())
       for (c, ch) in enumerate(rt)
       if ch == "#"]


def centroid(pts: list[complex]) -> complex:
    return sum(pts) / len(pts)


def sort_counterclockwise(pts: list[complex],
                          center: complex | None = None) -> list[complex]:
    if center is None:
        center = centroid(pts)
    return sorted(pts, key=lambda p: cmath.phase(p - center))


def perimeter(pts: list[complex]) -> list[complex]:
    out = []
    for pt in pts:
        for d in (-1, 1, -1j, 1j, -1+1j, 1+1j, -1-1j, 1-1j):
            xp = pt + d
            if xp not in pts:
                out.append(pt)
                break
    return sort_counterclockwise(out, centroid(pts))


def example(all_points: list[complex], scale: float = 20) -> str:
    p = perimeter(all_points)
    p.append(p[0])
    vbx = max(map(lambda x: x.real, p)) + 1
    vby = max(map(lambda x: x.imag, p)) + 1
    return f"""<svg
    viewBox="-1 -1 {vbx} {vby}"
    width="{vbx * scale}"
    height="{vbx * scale}">
    <polyline
    fill="none"
    stroke="black"
    stroke-width="0.1"
    points="{" ".join(map(lambda x: f"{x.real},{x.imag}", p))}">
    </polyline></svg>"""


print(example(pts))
