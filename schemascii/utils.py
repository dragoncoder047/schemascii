from __future__ import annotations

import enum
import itertools
import typing
from cmath import phase, pi, rect
from collections import defaultdict

import schemascii.grid as _grid
import schemascii.metric as _metric
import schemascii.svg as _svg

LEFT_RIGHT = {-1+0j, 1+0j}
UP_DOWN = {-1j, 1j}
ORTHAGONAL = LEFT_RIGHT | UP_DOWN
DIAGONAL = {-1+1j, 1+1j, -1-1j, 1-1j}
EVERYWHERE: defaultdict[complex, set[complex]] = defaultdict(
    lambda: ORTHAGONAL)
EVERYWHERE_MOORE: defaultdict[complex, set[complex]] = defaultdict(
    lambda: ORTHAGONAL + DIAGONAL)
IDENTITY: dict[complex, set[complex]] = {x: set((x,)) for x in ORTHAGONAL}


class Flag(typing.NamedTuple):
    """Data indicating the non-wire character next to a component."""
    pt: complex
    char: str
    side: Side


class Terminal(typing.NamedTuple):
    """Data indicating what and where wires connect to the component."""
    pt: complex
    flag: str | None
    side: Side


class Side(enum.Enum):
    """One of the four cardinal directions."""
    RIGHT = 0
    TOP = -pi / 2
    LEFT = pi
    BOTTOM = pi / 2

    @classmethod
    def from_phase(cls, pt: complex) -> Side:
        """Return the side that is closest to pt, if it is interpreted as
        a vector originating from the origin.
        """
        # TODO: fix this so it compares the components,
        # instead of this distance mess
        ops = {
            -pi: Side.LEFT,
            pi: Side.LEFT,
            -pi / 2: Side.TOP,
            pi / 2: Side.BOTTOM,
            0: Side.RIGHT
        }
        pph = phase(pt)
        best_err = float("inf")
        best_side = None
        for ph, s in ops.items():
            err = abs(ph - pph)
            if best_err > err:
                best_err = err
                best_side = s
        return best_side


def flood_walk(
        grid: _grid.Grid,
        seed: set[complex],
        start_dirs: defaultdict[str, set[complex] | None],
        directions: defaultdict[str, defaultdict[
            complex, set[complex] | None]],
        seen: set[complex]) -> list[complex]:
    """Flood-fill the area on the grid starting from seed, only following
    connections in the directions allowed by start_dirs and directions, and
    return the list of reached points.

    seen is the set of points that are already accounted for and should not be
    walked into; the function updates the set seen for points that were
    walked into. Thus, if this function is called twice with the same
    arguments, the second call will always return nothing.
    """
    points: list[complex] = []
    stack: list[tuple[complex, set[complex]]] = [
        (p, start_dirs[grid.get(p)])
        for p in seed]
    while stack:
        point, dirs = stack.pop()
        if point in seen:
            continue
        if not dirs:
            # invalid point
            continue
        seen.add(point)
        points.append(point)
        if dirs:
            for dir in dirs:
                next_pt = point + dir
                next_dirs = directions[grid.get(next_pt)]
                if next_dirs is None:
                    # shortcut
                    next_dirs = defaultdict(lambda: None)
                stack.append((next_pt, next_dirs[dir]))
    return points


def perimeter(pts: set[complex]) -> set[complex]:
    """Return the set of points that are on the boundary of
    the grid-aligned set pts.
    """
    out = set()
    for pt in pts:
        for d in ORTHAGONAL + DIAGONAL:
            xp = pt + d
            if xp not in pts:
                out.add(pt)
                break
    return out  # sort_counterclockwise(out, centroid(pts))


def centroid(pts: set[complex]) -> complex:
    """Return the centroid of the set of points pts."""
    return sum(pts) / len(pts)


def sort_counterclockwise(pts: set[complex],
                          center: complex | None = None) -> list[complex]:
    """Return pts sorted so that the points
    progress clockwise around the center, starting with the
    rightmost point.
    """
    if center is None:
        center = centroid(pts)
    return sorted(pts, key=lambda p: phase(p - center))


def colinear(*points: complex) -> bool:
    """Return true if all the points are in the same line."""
    return len(set(phase(p - points[0]) for p in points[1:])) == 1


def force_int(p: complex) -> complex:
    """Return p with the coordinates rounded to lie on the integer grid."""
    return complex(round(p.real), round(p.imag))


def sharpness_score(points: list[complex]) -> float:
    """Return a number indicating how twisty the line is -- higher means
    the corners are sharper. The result is 0 if the line is degenerate or
    has no corners.
    """
    if len(points) < 3:
        return 0
    score = 0
    prev_pt = points[1]
    prev_ph = phase(points[1] - points[0])
    for p in points[2:]:
        ph = phase(p - prev_pt)
        score += abs(prev_ph - ph)
        prev_pt = p
        prev_ph = ph
    return score


def intersecting(a: complex, b: complex, p: complex, q: complex) -> bool:
    """Return true if colinear line segments AB and PQ intersect.

    If the line segments are not colinear, the result is undefined and
    unpredictable.
    """
    a, b, p, q = a.real, b.real, p.real, q.real
    sort_a, sort_b = min(a, b), max(a, b)
    sort_p, sort_q = min(p, q), max(p, q)
    return sort_a <= sort_p <= sort_b or sort_p <= sort_b <= sort_q


def take_next_group(links: list[tuple[complex, complex]]) -> list[
        tuple[complex, complex]]:
    """Pop the longest possible continuous path off of the `links` list and
    return it, mutating the input list.
    """
    best = [links.pop()]
    while True:
        for pair in links:
            if best[0][0] == pair[1]:
                best.insert(0, pair)
            elif best[0][0] == pair[0]:
                best.insert(0, (pair[1], pair[0]))
            elif best[-1][1] == pair[0]:
                best.append(pair)
            elif best[-1][1] == pair[1]:
                best.append((pair[1], pair[0]))
            else:
                continue
            links.remove(pair)
            break
        else:
            break
    return best


def merge_colinear(links: list[tuple[complex, complex]]):
    """Merge adjacent line segments that are colinear, mutating the input
    list.
    """
    i = 1
    while links:
        if i >= len(links):
            break
        elif links[i][0] == links[i][1]:
            links.remove(links[i])
        elif links[i-1][1] == links[i][0] and colinear(
                links[i-1][0], links[i][0], links[i][1]):
            links[i-1] = (links[i-1][0], links[i][1])
            links.remove(links[i])
        else:
            i += 1


def iterate_line(p1: complex, p2: complex, step: float = 1.0):
    """Yield complex points along a line. Like range() but for complex
    numbers.

    This isn't Bresenham's algorithm but I only use it for perfectly vertical
    or perfectly horizontal lines, so it works well enough. If the line is
    diagonal then weird stuff happens.
    """
    vec = p2 - p1
    point = p1
    while abs(vec) > abs(point - p1):
        yield force_int(point)
        point += rect(step, phase(vec))
    yield point


type DT_Struct = list[DT_Struct] | tuple[DT_Struct] | complex


@typing.overload
def deep_transform(data: list[DT_Struct], origin: complex,
                   theta: float) -> list[DT_Struct]: ...


@typing.overload
def deep_transform(data: tuple[DT_Struct], origin: complex,
                   theta: float) -> tuple[DT_Struct]: ...


@typing.overload
def deep_transform(data: complex, origin: complex,
                   theta: float) -> complex: ...


def deep_transform(data: DT_Struct, origin: complex, theta: float):
    """Transform the point or points first by translating by origin,
    then rotating by theta. Return an identical data structure,
    but with the transformed points substituted.
    """
    if isinstance(data, (list, tuple)):
        return [deep_transform(d, origin, theta) for d in data]
    if isinstance(data, complex):
        return (origin
                + rect(data.real, theta + pi / 2)
                + rect(data.imag, theta))
    try:
        return deep_transform(complex(data), origin, theta)
    except TypeError as err:
        raise TypeError("bad type to deep_transform(): " +
                        type(data).__name__) from err


def _get_slc(options: dict) -> tuple[float, float, str]:
    return options["scale"], options["linewidth"], options["color"]


def points2path(points: list[complex], close: bool = False) -> str:
    """Convert the list of points into SVG <path> commands
    to draw the set of lines.
    """
    def fix(number: float) -> float | int:
        return int(number) if number.is_integer() else number

    def pad(number: float | int) -> str:
        if number < 0:
            return str(number)
        return " " + str(number).removeprefix("0")

    if not points:
        return "z"
    data = f"M{fix(points[0].real)}{pad(fix(points[0].imag))}"
    prev_pt = points[0]
    for pt in points[1:]:
        diff = pt - prev_pt
        if diff.real == 0 and diff.imag == 0:
            continue
        if diff.imag == 0:
            data += f"h{fix(diff.real)}"
        elif diff.real == 0:
            data += f"v{fix(diff.imag)}"
        else:
            data += f"l{fix(diff.real)}{pad(fix(diff.imag))}"
        prev_pt = pt
    if close:
        data += "z"
    return data


def polylinegon(
        points: list[complex], is_polygon: bool = False, **options) -> str:
    """Turn the list of points into a line or filled area.

    If is_polygon is true, stroke color is used as fill color instead
    and stroke width is ignored.
    """
    scale, linewidth, stroke = _get_slc(options)
    scaled_pts = [x * scale for x in points]
    if is_polygon:
        return _svg.path(points2path(scaled_pts, True), stroke,
                         class_="filled")
    return _svg.path(points2path(scaled_pts, False), "transparent",
                     linewidth, stroke)


def find_dots(points: list[tuple[complex, complex]]) -> list[complex]:
    """Find all the points where there are 4 or more connecting wires."""
    seen = {}
    for p1, p2 in points:
        if p1 == p2:
            # Skip zero-length wires
            # XXX: there shouldn't be any of these anymore?
            continue
        seen[p1] = seen.get(p1, 0) + 1
        seen[p2] = seen.get(p2, 0) + 1
    return [pt for pt, count in seen.items() if count > 3]


def bunch_o_lines(pairs: list[tuple[complex, complex]], **options) -> str:
    """Combine the pairs (p1, p2) into a set of SVG <path> commands
    to draw all of the lines.
    """
    scale, linewidth, stroke = _get_slc(options)
    lines = []
    while pairs:
        group = take_next_group(pairs)
        merge_colinear(group)
        # make it a polyline
        pts = [group[0][0]] + [p[1] for p in group]
        lines.append(pts)
    data = ""
    for line in lines:
        data += points2path([x * scale for x in line], False)
    return _svg.path(data, "transparent", linewidth, stroke)


def id_text(
        cname: str,
        terminals: list[Terminal],
        value: str | list[tuple[str, str]
                          | tuple[str, str, bool]
                          | tuple[str, str, bool, bool]],
        point: complex | None = None,
        **options) -> str:
    """Format the component ID and value around the point."""
    nolabels, label = options["nolabels"], options["label"]
    scale, stroke = options["scale"], options["color"]
    font = options["font"]
    if nolabels:
        return ""
    if not point:
        point = centroid(t.pt for t in terminals)
    data = ""
    if isinstance(value, str):
        data = value
        data_css_class = "part-num"
    else:
        for tp in value:
            match tp:
                case (n, unit) if n:
                    data += _metric.format_metric_unit(n, unit)
                case (n, unit, six) if n:
                    data += _metric.format_metric_unit(n, unit, six)
                case (n, unit, six, allow_range) if n:
                    data += _metric.format_metric_unit(
                        n, unit, six, allow_range=allow_range)
                case _:
                    raise ValueError(
                        f"bad values tuple: {tp!r}")
        data_css_class = "cmp-value"
    if len(terminals) > 1:
        textach = (
            "start"
            if (any(Side.BOTTOM == t.side for t in terminals)
                or any(Side.TOP == t.side for t in terminals))
            else "middle")
    else:
        textach = "middle" if terminals[0].side in (
            Side.TOP, Side.BOTTOM) else "start"
    return _svg.xmltag("text",
                       (_svg.xmltag("tspan", cname, class_="cmp-id")
                        if "L" in label else ""),
                       " " if data and "L" in label else "",
                       (_svg.xmltag("tspan", data, class_=data_css_class)
                        if "V" in label else ""),
                       x=point.real,
                       y=point.imag,
                       text__anchor=textach,
                       font__size=scale,
                       fill=stroke,
                       style=f"font-family:{font}")


def make_text_point(t1: complex, t2: complex, **options) -> complex:
    """Compute the scaled coordinates of the text anchor point."""
    scale, offset_scale = options["scale"], options["offset_scale"]
    quad_angle = phase(t1 - t2) + pi / 2
    text_pt = (t1 + t2) * scale / 2
    offset = rect(scale / 2 * offset_scale, quad_angle)
    text_pt += complex(abs(offset.real), -abs(offset.imag))
    return text_pt


def make_plus(center: complex, theta: float, **options) -> str:
    """Make a '+' sign for indicating polarity."""
    return _svg.group(
        bunch_o_lines(
            deep_transform(
                deep_transform([(0.125, -0.125), (0.125j, -0.125j)], 0, theta),
                center + deep_transform(0.33 + 0.75j, 0, theta), 0),
            **options),
        class_="plus")


def arrow_points(p1: complex, p2: complex) -> list[tuple[complex, complex]]:
    """Return points to make an arrow from p1 pointing to p2."""
    angle = phase(p2 - p1)
    tick_len = min(0.5, abs(p2 - p1))
    return [
        (p2, p1),
        (p2, p2 - rect(tick_len, angle + pi / 5)),
        (p2, p2 - rect(tick_len, angle - pi / 5))]


def make_variable(center: complex, theta: float, **options) -> str:
    """Draw a "variable" arrow across the component."""
    return _svg.group(bunch_o_lines(deep_transform(arrow_points(-1, 1),
                                                   center,
                                                   (theta % pi) + pi / 4),
                                    **options),
                      class_="variable")


def light_arrows(center: complex, theta: float, out: bool, **options):
    """Draw arrows towards or away from the component
    (i.e. light-emitting or light-dependent).
    """
    a, b = 1j, 0.3 + 0.3j
    if out:
        a, b = b, a
    return _svg.group(bunch_o_lines(
        deep_transform(arrow_points(a, b),
                       center, theta - pi / 2)
        + deep_transform(arrow_points(a - 0.5, b - 0.5),
                         center, theta - pi / 2),
        **options),
        class_="light-emitting" if out else "light-dependent")


def sort_terminals_counterclockwise(
        terminals: list[Terminal]) -> list[Terminal]:
    """Sort the terminals in counterclockwise order."""
    partitioned = {
        side: list(filtered_terminals)
        for side, filtered_terminals in itertools.groupby(
            terminals, lambda t: t.side)
    }
    return list(
        itertools.chain(
            sorted(partitioned.get(Side.LEFT, []), key=lambda t: t.pt.imag),
            sorted(partitioned.get(Side.BOTTOM, []), key=lambda t: t.pt.real),
            sorted(partitioned.get(Side.RIGHT, []), key=lambda t: -t.pt.imag),
            sorted(partitioned.get(Side.TOP, []), key=lambda t: -t.pt.real),
        )
    )


def is_clockwise(terminals: list[Terminal]) -> bool:
    """Return true if the terminals are clockwise order."""
    sort = sort_terminals_counterclockwise(terminals)
    for _ in range(len(sort)):
        if sort == terminals:
            return True
        sort = sort[1:] + [sort[0]]
    return False


if __name__ == '__main__':
    import pprint
    pts = []
    n = 100
    for x in range(n):
        pts.append(force_int(rect(n, 2 * pi * x / n)))
    pprint.pprint(sort_counterclockwise(pts))
    print(DT_Struct)
