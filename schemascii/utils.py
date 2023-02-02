from collections import namedtuple
from itertools import groupby, chain
from enum import IntEnum
from math import pi
from cmath import phase, rect
from types import GeneratorType
from typing import Callable
from .metric import format_metric_unit

Cbox = namedtuple('Cbox', 'p1 p2 type id')
BOMData = namedtuple('BOMData', 'type id data')
Flag = namedtuple('Flag', 'pt char side')
Terminal = namedtuple('Terminal', 'pt flag side')


class Side(IntEnum):
    "Which edge the flag was found on."
    RIGHT = 0
    TOP = 1
    LEFT = 2
    BOTTOM = 3


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
    point = p1
    while abs(vec) > abs(point - p1):
        yield point
        point += rect(step, phase(vec))
    yield point


def deep_transform(data, origin: complex, theta: float):
    """Transform the point or points first by translating by origin,
    then rotating by theta. Returns an identical data structure,
    but with the transformed points substituted."""
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
                if v is not False:
                    out += f'{k.removesuffix("_").replace("__", "-")}="{v}" '
            out = out.rstrip() + '>' + ''.join(contents)
            return out + f'</{tag}>'
        return mk_tag


XML = XMLClass()


def polylinegon(points: list[complex], is_polygon: bool = False, **options):
    "Turn the list of points into a <polyline> or <polygon>."
    scale = options["scale"]
    w = options["stroke_width"]
    c = options["stroke"]
    pts = ' '.join(
        f'{x.real * scale},{x.imag * scale}'
        for x in points)
    if is_polygon:
        return XML.polygon(points=pts, fill=c)
    return XML.polyline(
        points=pts, fill="transparent", stroke__width=w, stroke=c)


def find_dots(points: list[tuple[complex, complex]]) -> list[complex]:
    "Finds all the points where there are 3 or more connecting wires."
    seen = {}
    for p1, p2 in points:
        if p1 not in seen:
            seen[p1] = 1
        else:
            seen[p1] += 1
        if p2 not in seen:
            seen[p2] = 1
        else:
            seen[p2] += 1
    return [pt for pt, count in seen.items() if count > 2]


def bunch_o_lines(points: list[tuple[complex, complex]], **options):
    "Return a <line> for each pair of points."
    out = ''
    scale = options['scale']
    w = options["stroke_width"]
    c = options["stroke"]
    for p1, p2 in points:
        out += XML.polyline(
            points=f"{p1.real * scale},"
            f"{p1.imag * scale} "
            f"{p2.real * scale},"
            f"{p2.imag * scale}",
            stroke=c,
            stroke__width=w)
    return out


def id_text(
        box: Cbox,
        bom_data: BOMData,
        terminals: list[Terminal],
        unit: str | list[str] | None,
        point: complex | None = None,
        **options):
    "Format the component ID and value around the point."
    if options["nolabels"]:
        return ""
    label_style = options["label"]
    if point is None:
        point = sum(t.pt for t in terminals) / len(terminals)
    data = ""
    if bom_data is not None:
        text = bom_data.data
        classy = "part-num"
        if unit is None:
            pass
        elif isinstance(unit, str):
            text = format_metric_unit(text, unit)
            classy = "cmp-value"
        else:
            text = " ".join(format_metric_unit(x, y, six)
                            for x, (y, six) in zip(text.split(","), unit))
            classy = "cmp-value"
        data = XML.tspan(text, class_=classy)
    return XML.text(
        (XML.tspan(f"{box.type}{box.id}", class_="cmp-id")
         * bool("L" in label_style)),
        " " * (bool(data) and "L" in label_style),
        data * bool("V" in label_style),
        x=point.real,
        y=point.imag,
        text__anchor="start" if (
            any(Side.BOTTOM == t.side for t in terminals)
            or any(Side.TOP == t.side for t in terminals)
        ) else "middle",
        font__size=options["scale"],
        fill=options["stroke"])


def make_text_point(t1: complex, t2: complex, **options) -> complex:
    "Compute the scaled coordinates of the text anchor point."
    quad_angle = phase(t1 - t2) + pi / 2
    scale = options["scale"]
    text_pt = (t1 + t2) * scale / 2
    offset = rect(scale / 2, quad_angle)
    text_pt += complex(abs(offset.real), -abs(offset.imag))
    return text_pt


def make_plus(
        terminals: list[Terminal],
        center: complex,
        theta: float,
        **options) -> str:
    "Make a + sign if the terminals indicate the component is polarized."
    if all(t.flag != "+" for t in terminals):
        return ""
    return XML.g(
        bunch_o_lines(deep_transform(deep_transform(
            [(.125, -.125), (.125j, -.125j)], 0, theta),
            center + deep_transform(.33+.75j, 0, theta), 0), **options),
        class_="plus")


def make_variable(
        center: complex,
        theta: float,
        is_variable: bool = True,
        **options) -> str:
    "Draw a 'variable' arrow across the component."
    if not is_variable:
        return ""
    theta = theta % pi
    return bunch_o_lines(deep_transform([
        (-.6+.5j, .75-.5j),
        (.75-.5j, .5-.55j),
        (.75-.5j, .7-.25j),
    ], center, theta), **options)


def sort_counterclockwise(terminals: list[Terminal]) -> list[Terminal]:
    "Sort the terminals in counterclockwise order."
    partitioned = {
        side: list(filtered_terminals)
        for side, filtered_terminals in groupby(
            terminals,
            lambda t: t.side)}
    return list(chain(
        sorted(partitioned[Side.LEFT],   key=lambda t:  t.pt.imag),
        sorted(partitioned[Side.BOTTOM], key=lambda t:  t.pt.real),
        sorted(partitioned[Side.RIGHT],  key=lambda t: -t.pt.imag),
        sorted(partitioned[Side.TOP],    key=lambda t: -t.pt.real)))
