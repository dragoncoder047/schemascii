from collections import namedtuple
from itertools import groupby, chain
from enum import IntEnum
from math import pi
from cmath import phase, rect
from typing import Callable
import re
from .metric import format_metric_unit
from .errors import TerminalsError

Cbox = namedtuple("Cbox", "p1 p2 type id")
BOMData = namedtuple("BOMData", "type id data")
Flag = namedtuple("Flag", "pt char side")
Terminal = namedtuple("Terminal", "pt flag side")


class Side(IntEnum):
    "Which edge the flag was found on."
    RIGHT = 0
    TOP = 1
    LEFT = 2
    BOTTOM = 3


def colinear(*points: complex) -> bool:
    "Returns true if all the points are in the same line."
    return len(set(phase(p - points[0]) for p in points[1:])) == 1


def force_int(p: complex) -> complex:
    "Force the coordinates of the complex number to lie on the integer grid."
    return complex(round(p.real), round(p.imag))


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


def take_next_group(links: list[tuple[complex, complex]]) -> list[tuple[complex, complex]]:
    """Pops the longes possible link off of the `links` list and returns it,
    mutating the input list."""
    best = [links.pop()]
    while True:
        for pair in links:
            if best[0][0] == pair[1]:
                best.insert(0, pair)
                links.remove(pair)
            elif best[0][0] == pair[0]:
                best.insert(0, (pair[1], pair[0]))
                links.remove(pair)
            elif best[-1][1] == pair[0]:
                best.append(pair)
                links.remove(pair)
            elif best[-1][1] == pair[1]:
                best.append((pair[1], pair[0]))
                links.remove(pair)
            else:
                continue
            break
        else:
            break
    return best


def merge_colinear(links: list[tuple[complex, complex]]):
    "Merges line segments that are colinear. Mutates the input list."
    i = 1
    while True:
        if i == len(links):
            break
        elif links[i][0] == links[i][1]:
            links.remove(links[i])
        elif links[i-1][1] == links[i][0] and colinear(links[i-1][0], links[i][0], links[i][1]):
            links[i-1] = (links[i-1][0], links[i][1])
            links.remove(links[i])
        else:
            i += 1


def iterate_line(p1: complex, p2: complex, step: float = 1.0):
    "Yields complex points along a line."
    vec = p2 - p1
    point = p1
    while abs(vec) > abs(point - p1):
        yield force_int(point)
        point += rect(step, phase(vec))
    yield point


def deep_transform(data, origin: complex, theta: float):
    """Transform the point or points first by translating by origin,
    then rotating by theta. Returns an identical data structure,
    but with the transformed points substituted."""
    if isinstance(data, list | tuple):
        return [deep_transform(d, origin, theta) for d in data]
    if isinstance(data, complex):
        return origin + rect(data.real, theta + pi / 2) + rect(data.imag, theta)
    try:
        return deep_transform(complex(data), origin, theta)
    except TypeError as err:
        raise TypeError("bad type to deep_transform(): " +
                        type(data).__name__) from err


def fix_number(n: float) -> str:
    """If n is an integer, remove the trailing ".0".
    Otherwise round it to 2 digits."""
    if n.is_integer():
        return str(int(n))
    n = round(n, 2)
    if n.is_integer():
        return str(int(n))
    return str(n)


class XMLClass:
    def __getattr__(self, tag) -> Callable:
        def mk_tag(*contents: str, **attrs: str) -> str:
            out = f"<{tag} "
            for k, v in attrs.items():
                if v is False:
                    continue
                if isinstance(v, float):
                    v = fix_number(v)
                elif isinstance(v, str):
                    v = re.sub(r"\b\d+(\.\d+)\b",
                               lambda m: fix_number(float(m.group())), v)
                out += f'{k.removesuffix("_").replace("__", "-")}="{v}" '
            out = out.rstrip() + ">" + "".join(contents)
            return out + f"</{tag}>"

        return mk_tag


XML = XMLClass()
del XMLClass


def polylinegon(points: list[complex], is_polygon: bool = False, **options) -> str:
    "Turn the list of points into a <polyline> or <polygon>."
    scale = options["scale"]
    w = options["stroke_width"]
    c = options["stroke"]
    pts = " ".join(f"{x.real * scale},{x.imag * scale}" for x in points)
    if is_polygon:
        return XML.polygon(points=pts, fill=c, class_="filled")
    return XML.polyline(points=pts, fill="transparent", stroke__width=w, stroke=c)


def find_dots(points: list[tuple[complex, complex]]) -> list[complex]:
    "Finds all the points where there are 4 or more connecting wires."
    seen = {}
    for p1, p2 in points:
        if p1 == p2:
            # Skip zero-length wires
            continue
        if p1 not in seen:
            seen[p1] = 1
        else:
            seen[p1] += 1
        if p2 not in seen:
            seen[p2] = 1
        else:
            seen[p2] += 1
    return [pt for pt, count in seen.items() if count > 3]


def bunch_o_lines(pairs: list[tuple[complex, complex]], **options) -> str:
    "Collapse the pairs of points and return the smallest number of <polyline>s."
    lines = []
    while pairs:
        group = take_next_group(pairs)
        merge_colinear(group)
        # make it a polyline
        pts = [group[0][0]] + [p[1] for p in group]
        lines.append(pts)
    return "".join(polylinegon(line, **options) for line in lines)


def id_text(
    box: Cbox,
    bom_data: BOMData,
    terminals: list[Terminal],
    unit: str | list[str] | None,
    point: complex | None = None,
    **options,
) -> str:
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
            text = " ".join(
                format_metric_unit(x, y, six)
                for x, (y, six) in zip(text.split(","), unit)
            )
            classy = "cmp-value"
        data = XML.tspan(text, class_=classy)
    if len(terminals) > 1:
        textach = (
            "start"
            if (
                any(Side.BOTTOM == t.side for t in terminals)
                or any(Side.TOP == t.side for t in terminals)
            )
            else "middle"
        )
    else:
        textach = "middle" if terminals[0].side in (
            Side.TOP, Side.BOTTOM) else "start"
    return XML.text(
        (XML.tspan(f"{box.type}{box.id}", class_="cmp-id")
         * bool("L" in label_style)),
        " " * (bool(data) and "L" in label_style),
        data * bool("V" in label_style),
        x=point.real,
        y=point.imag,
        text__anchor=textach,
        font__size=options["scale"],
        fill=options["stroke"],
    )


def make_text_point(t1: complex, t2: complex, **options) -> complex:
    "Compute the scaled coordinates of the text anchor point."
    quad_angle = phase(t1 - t2) + pi / 2
    scale = options["scale"]
    text_pt = (t1 + t2) * scale / 2
    offset = rect(scale / 2 * options.get("offset_scaler", 1), quad_angle)
    text_pt += complex(abs(offset.real), -abs(offset.imag))
    return text_pt


def make_plus(terminals: list[Terminal], center: complex, theta: float, **options) -> str:
    "Make a + sign if the terminals indicate the component is polarized."
    if all(t.flag != "+" for t in terminals):
        return ""
    return XML.g(
        bunch_o_lines(
            deep_transform(
                deep_transform([(0.125, -0.125), (0.125j, -0.125j)], 0, theta),
                center + deep_transform(0.33 + 0.75j, 0, theta),
                0,
            ),
            **options,
        ),
        class_="plus",
    )


def arrow_points(p1: complex, p2: complex) -> list[tuple[complex, complex]]:
    "Return points to make an arrow from p1 pointing to p2."
    angle = phase(p2 - p1)
    tick_len = min(0.5, abs(p2 - p1))
    return [
        (p2, p1),
        (p2, p2 - rect(tick_len, angle + pi / 5)),
        (p2, p2 - rect(tick_len, angle - pi / 5)),
    ]


def make_variable(center: complex, theta: float, is_variable: bool = True, **options) -> str:
    "Draw a 'variable' arrow across the component."
    if not is_variable:
        return ""
    return bunch_o_lines(
        deep_transform(arrow_points(-1, 1), center, (theta % pi) + pi / 4), **options
    )


def light_arrows(center: complex, theta: float, out: bool, **options):
    """Draw arrows towards or away from the component
    (i.e. light-emitting or light-dependent)."""
    a, b = 1j, 0.3 + 0.3j
    if out:
        a, b = b, a
    return bunch_o_lines(
        deep_transform(arrow_points(a, b), center, theta - pi / 2), **options
    ) + bunch_o_lines(
        deep_transform(arrow_points(a - 0.5, b - 0.5), center, theta - pi / 2),
        **options,
    )


def sort_counterclockwise(terminals: list[Terminal]) -> list[Terminal]:
    "Sort the terminals in counterclockwise order."
    partitioned = {
        side: list(filtered_terminals)
        for side, filtered_terminals in groupby(terminals, lambda t: t.side)
    }
    return list(
        chain(
            sorted(partitioned.get(Side.LEFT, []), key=lambda t: t.pt.imag),
            sorted(partitioned.get(Side.BOTTOM, []), key=lambda t: t.pt.real),
            sorted(partitioned.get(Side.RIGHT, []), key=lambda t: -t.pt.imag),
            sorted(partitioned.get(Side.TOP, []), key=lambda t: -t.pt.real),
        )
    )


def is_clockwise(terminals: list[Terminal]) -> bool:
    "Return true if the terminals are clockwise order."
    sort = sort_counterclockwise(terminals)
    for _ in range(len(sort)):
        if sort == terminals:
            return True
        sort = sort[1:] + [sort[0]]
    return False


def sort_for_flags(terminals: list[Terminal], box: Cbox, *flags: list[str]) -> list[Terminal]:
    """Sorts out the terminals in the specified order using the flags.
    Raises and error if the flags are absent."""
    out = ()
    for flag in flags:
        matching_terminals = list(filter(lambda t: t.flag == flag, terminals))
        if len(matching_terminals) > 1:
            raise TerminalsError(
                f"Multiple terminals with the same flag {flag} "
                f"on component {box.type}{box.id}"
            )
        if len(matching_terminals) == 0:
            raise TerminalsError(
                f"Need a terminal with the flag {flag} "
                f"on component {box.type}{box.id}"
            )
        (terminal,) = matching_terminals
        out = *out, terminal
        terminals.remove(terminal)
    return out
