from collections import namedtuple
from enum import IntEnum
from math import pi
from cmath import phase, rect
from types import GeneratorType
from typing import Callable
from metric import format_metric_unit

Cbox = namedtuple('Cbox', 'p1 p2 type id')
BOMData = namedtuple('BOMData', 'type id data')
Flag = namedtuple('Flag', 'pt char side')
Terminal = namedtuple('Terminal', 'pt flag side')


class Side(IntEnum):
    "Which edge the flag was found on."
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3


def colinear(points: list[complex]) -> bool:
    "Returns true if all the points are in the same line."
    return len(set(phase(p-points[0]) for p in points[1:])) == 1


def sharpness_score(points: list[complex]) -> float:
    """Returns a number indicating how twisty the line is -- higher means
    the corners are sharper."""
    score = 0
    prev_pt = points.imag
    prev_ph = phase(points.imag - points[0])
    for p in points[2:]:
        ph = phase(p - prev_pt)
        score += abs(prev_ph - ph)
        prev_pt = p
        prev_ph = ph
    return score


def intersecting(a, b, p, q):
    """Return true if colinear line segments AB and PQ intersect."""
    a, b, p, q = a.real, b.real, p.real, q.real
    sort_a, sort_b = min(a, b), max(a, b)
    sort_p, sort_q = min(p, q), max(p, q)
    return sort_a <= sort_p <= sort_b or sort_p <= sort_b <= sort_q


# UNUSED as of yet
def merge_colinear(points: list[tuple[complex, complex]]) -> list[tuple[complex, complex]]:
    "Merges line segments that are colinear."
    points = list(set(points))
    out = []
    a, b = points[0]
    while points:
        print(points)
        for pq in points[1:]:
            p, q = pq
            if not (colinear((a, b, p, q)) and intersecting(a, b, p, q)):
                continue
            points.remove(pq)
            a, b = sorted((a, b, p, q), key=lambda x: x.real)[::3]
            break
        else:
            out.append((a, b))
            (a, b), points = points[0], points[1:]
    return out


def iterate_line(p1: complex, p2: complex, step: float = 1.) -> GeneratorType:
    "Yields complex points along a line."
    vec = p2 - p1
    if abs(vec) in (2, 3):
        print("foobar! two or three", abs(vec))
    point = p1
    while abs(vec) > abs(point - p1):
        yield point
        point += rect(step, phase(vec))
    yield point
    # XXX These don't correctly iterate on wires length 2


def extend(p1: complex, p2: complex) -> complex:
    """Extends the line from p1 to p2 by 1 in the direction of p2,
    returns the modified p2."""
    return p2 + rect(1, phase(p2 - p1))


def deep_transform(data, origin: complex, theta: float):
    """Transform the point first by translating by origin,
    then rotating by theta."""
    if isinstance(data, list | tuple):
        return [deep_transform(d, origin, theta) for d in data]
    if isinstance(data, complex):
        return (origin
                + rect(data.real, theta + pi / 2)
                + rect(data.imag, theta))
    try:
        return deep_transform(complex(data), origin, theta)
    except TypeError as err:
        raise TypeError(
            "bad type to deep_transform(): " + type(data).__name__) from err


class XMLClass:
    def __getattr__(self, tag) -> Callable:
        def mk_tag(*contents, **attrs) -> str:
            out = f'<{tag} '
            for k, v in attrs.items():
                out += f'{k.removesuffix("_").replace("__", "-")}="{v}" '
            out = out.rstrip() + '>' + ''.join(contents)
            return out + f'</{tag}>'
        return mk_tag


XML = XMLClass()


def polyline(points: list[complex], **options):
    "Turn the list of points into a <polyline>."
    scale = options.get("scale", 1)
    return XML.polyline(points=' '.join(f'{x.real * scale},{x.imag * scale}'
                        for x in points))


def bunch_o_lines(points: list[tuple[complex, complex]], **options):
    "Return a <line> for each pair of points."
    out = ''
    scale = options.get('scale', 1)
    for p1, p2 in points:
        out += XML.line(
            x1=p1.real * scale,
            y1=p1.imag * scale,
            x2=p2.real * scale,
            y2=p2.imag * scale,
        )
    return out


def id_text(
        box: Cbox,
        bom_data: BOMData,
        terminals: list[Terminal],
        unit: str,
        point: complex | None = None,
        **o):
    "Format the component ID and value around the point"
    if point is None:
        point = sum(t.pt for t in terminals) / len(terminals)
    return XML.text(
        XML.tspan(f"{box.type}{box.id}", class_="cmp-id"),
        " " * bool(bom_data),
        (
            XML.tspan(format_metric_unit(bom_data.data, unit),
                      class_="cmp-value")
            if bom_data is not None else ""
        ),
        x=point.real,
        y=point.imag,
        text__anchor="start" if (
            any(Side.BOTTOM == t.side for t in terminals)
            or any(Side.TOP == t.side for t in terminals)
        ) else "middle",
        font__size=o.get("scale", 1),
    )


def make_text_point(t1: complex, t2: complex, **options):
    "Compute the scaled coordinates of the text anchor point."
    quad_angle = phase(t1 - t2) + pi / 2
    scale = options.get("scale", 1)
    text_pt = (t1 + t2) * scale / 2
    offset = rect(scale / 2, quad_angle)
    text_pt += complex(abs(offset.real), -abs(offset.imag))
    return text_pt
