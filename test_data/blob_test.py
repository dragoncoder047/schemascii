import enum
import typing

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
######
###########
################
###########
######
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
#""",
    """
######
 ########
  #########
  ##########
  #########
 ########
######""",
    """
  ###########
 #############
###############
####       ####
####       ####
####       ####
####       ####
###############
 #############
  ###########""",
    """
###############
          ###################""",
    """
###############
          ###################
###############"""]

"""
idea for new algorithm
* find all of the edge points
* sort them by clockwise order around the perimeter
  * this is done not by sorting by angle around the centroid
    (that would only work for convex shapes) but by forming a list
    of edges between adjacent points and then walking the graph
    using a direction vector that is rotated only clockwise
    and starting from the rightmost point and starting down
* handle the shapes that have holes in them by treating
  each edge as a separate shape, then merging the svgs
* find all of the points that are concave
* find all of the straight line points
* assign each straight line point a distance from the nearest
  concave point
* remove the concave points and straight line points that are closer
  than a threshold and are not a local maximum of distance
"""

VN_DIRECTIONS: list[complex] = [1, 1j, -1, -1j]
DIRECTIONS: list[complex] = [1, 1+1j, 1j, -1+1j, -1, -1-1j, -1j, 1-1j]


class VertexType(enum.Enum):
    STRAIGHT = 1
    CONCAVE = 2
    CONVEX = 3


def rot(d: complex, n: int) -> complex:
    # 1 step is 45 degrees
    return DIRECTIONS[(DIRECTIONS.index(d) + n + len(DIRECTIONS))
                      % len(DIRECTIONS)]


def points_to_edges(
        edge_points: list[complex]) -> dict[complex, set[complex]]:
    # find the edge points
    edges: dict[complex, set[complex]] = {}
    for p in edge_points:
        edges[p] = set(p2 for p2 in edge_points
                       if p2 != p and abs(p2 - p) < 1.5)
    return edges


T = typing.TypeVar("T")


def cir(list: list[T], is_forward: bool) -> list[T]:
    if is_forward:
        return list[1:] + [list[0]]
    else:
        return [list[-1]] + list[:-1]


def triples(v: list[T]) -> list[tuple[T, T, T]]:
    return list(zip(cir(v, False), v, cir(v, True)))


def fiveles(v: list[T]) -> list[tuple[T, T, T]]:
    x, y, z = cir(v, False), v, cir(v, True)
    return list(zip(cir(x, False), x, y, z, cir(z, True)))


def cull_disallowed_edges(
        all_points: list[complex],
        edges: dict[complex, set[complex]]) -> dict[complex, set[complex]]:
    # each point can only have 1 to 3 unique directions coming out of it
    # if there are more, find the "outside" direction and remove the inner
    # links
    fixed_edges: dict[complex, set[complex]] = {}
    for p1, conn in edges.items():
        if len(conn) <= 2:
            fixed_edges[p1] = conn.copy()
            continue
        # if there are multiple directions out of here, find the gaps and
        # only keep the ones on the sides of the gaps
        gaps = [p1 + d in all_points for d in DIRECTIONS]
        tran_5 = fiveles(gaps)
        # im not quite sure what this is doing
        fixed_edges[p1] = set(p1 + d for (d, (q, a, b, c, w))
                              in zip(DIRECTIONS, tran_5)
                              if b and not ((a and c) or (q and w)))
    # ensure there are no one way "trap" edges
    # (the above algorithm has some weird edge cases where it may produce
    # one-way edges on accident)
    # XXX This causes issues when it is enabled, why?
    for p1 in all_points:
        for p2 in fixed_edges.setdefault(p1, set()):
            fixed_edges.setdefault(p2, set()).add(p1)
    return fixed_edges


def walk_graph_to_loop(
        start: complex,
        start_dir: complex,
        edges: dict[complex, set[complex]]) -> list[complex]:
    out: list[complex] = []
    current = start
    current_dir = start_dir
    swd_into: dict[complex, set[complex]] = {}
    while not all(e in out for e in edges) or current != start:
        out.append(current)
        print(debug_singular_polyline_in_svg(out, current))
        # log the direction we came from
        swd_into.setdefault(current, set()).add(current_dir)
        choices_directions = (rot(current_dir, i)
                              for i in (-1, -2, -3, 0, 1, 2, 3, 4))
        bt_d = None
        for d in choices_directions:
            # if allowed to walk that direction
            nxt = current + d
            if nxt in edges[current]:
                if nxt not in swd_into.keys():
                    # if we haven't been there before, go there
                    print("go new place")
                    current = nxt
                    current_dir = d
                    break
                # otherwise, if we've been there before, but haven't
                # come from this direction, then save it for later
                if d not in swd_into.get(nxt, set()) and bt_d is None:
                    bt_d = d
                    print("saving", d)
        else:
            if bt_d is not None:
                # if we have a saved direction to go, go that way
                current = current + bt_d
                current_dir = bt_d
            else:
                raise RuntimeError
    print("finished normally")
    return out


def is_mid_maxima(a: int | None, b: int | None, c: int | None) -> bool:
    return all(x is not None for x in (a, b, c)) and a < b and c < b


def remove_unnecessary(pts: list[complex],
                       edges: dict[complex, set[complex]],
                       maxslope=2) -> list[complex]:
    triples_pts = list(triples(pts))
    dirs = [(b-a, c-b) for a, b, c in triples_pts]
    signos = [a.real * b.imag - a.imag * b.real
              + (abs(b - a) if a == b or a == -b else 0) for a, b in dirs]
    # signos: 0 if straightline, negative if concave, positive if convex
    dotnos = [a.real * b.real + a.imag * b.imag for a, b in dirs]
    # dotnos: a measure of pointedness - 0 = right angle, positive = pointy,
    # negative = blunt
    distances = [None if s >= 0 else 0 for s in signos]
    # distances: None if it's a convex or straight un-analyzed,
    # number if it's a concave or counted straight

    # there ought to be a better way to do this
    changing = True
    while changing:
        changing = False
        for j in range(len(distances)):
            i = j - 1
            k = (j + 1) % len(distances)
            iNone = distances[i] is None
            jNone = distances[j] is None
            kNone = distances[k] is None
            if jNone and signos[j] == 0:
                if kNone and iNone:
                    continue
                changing = True
                if kNone:
                    distances[j] = distances[i] + 1
                elif iNone:
                    distances[j] = distances[k] + 1
                else:
                    distances[j] = min(distances[i], distances[k]) + 1
    # at this point, distances should contain:
    # None for the convex points
    # numbers for all others
    maxima = [is_mid_maxima(a, b, c) for (a, b, c) in triples(distances)]
    points_to_maybe_discard = set(
        pt for (pt, dist, maxima) in zip(pts, distances, maxima)
        # keep all the local maxima
        # keep ones that are flat enough
        # --> remove the ones that are not sloped enough
        #     and are not local maxima
        if ((dist is not None and dist < maxslope)
            and not maxima))
    # the ones to definitely keep are the convex ones
    # as well as concave ones that are adjacent to only straight ones that
    # are being deleted
    points_to_def_keep = set(p for p, s in zip(pts, signos)
                             if s > 0
                             or (s < 0 and all(
                                 signos[z := pts.index(q)] == 0
                                 and q in points_to_maybe_discard
                                 for q in edges[p])))
    # special case: keep concave ones that are 2-near at
    # least one convex pointy point (where pointy additionally means that
    # it isn't a 180)
    points_to_def_keep |= set(
        p for (
            p,
            (dot_2l, _, _, _, dot_2r),
            (sig_2l, _, sig_m, _, sig_2r),
            ((dd1_2l, dd2_2l), _, _, _, (dd1_2r, dd2_2r))
        ) in zip(pts, fiveles(dotnos), fiveles(signos), fiveles(dirs))
        if sig_m < 0 and (
            (sig_2l > 0 and dot_2l < 0 and dd1_2l != -dd2_2l)
            or (sig_2r > 0 and dot_2r < 0 and dd1_2r != -dd2_2r)))
    # for debugging
    a = dots([], edges)
    i = a.replace("</svg>", "".join(f"""<circle cx="{
        p.real
    }" cy="{
        p.imag
    }" r="0.5" fill="{
        "red" if r > 0
        else "blue" if r < 0
        else "black"
    }" opacity="50%"></circle>"""
        for p, q, r in zip(pts, distances, dotnos)) + "</svg>")
    z = a.replace("</svg>", "".join(f"""<circle cx="{
        p.real
    }" cy="{
        p.imag
    }" r="0.5" fill="red" opacity="50%"></circle>"""
        for p in (points_to_maybe_discard - points_to_def_keep)) + "</svg>")
    print("begin conc", i, "end conc")
    print("begin discard", z, "end discard")
    # end debugging
    return [p for p in pts
            if p not in points_to_maybe_discard
            or p in points_to_def_keep]


def process_group(g: list[complex], all_pts: list[complex]) -> list[complex]:
    edges = cull_disallowed_edges(all_pts, points_to_edges(g))
    print(dots(g, edges))
    start = min(g, key=lambda x: x.real * 65536 + x.imag)
    next = min(edges[start], key=lambda x: x.real * 65536 - x.imag)
    g = walk_graph_to_loop(
        start=start,
        start_dir=next - start,
        edges=edges)
    g = remove_unnecessary(g, edges)
    return g


def get_outline_points(pts: list[complex]) -> list[list[complex]]:
    # find the edge points
    edge_points: list[complex] = []
    for p in pts:
        if not all(p + d in pts for d in DIRECTIONS) and not all(
                p + d in pts for d in VN_DIRECTIONS):
            edge_points.append(p)
    # find all of the disconnected loop groups
    loop_groups: list[list[complex]] = []
    while edge_points:
        current_group = [edge_points.pop()]
        while True:
            for p in edge_points:
                if any(ep + d == p
                       for ep in current_group
                       for d in DIRECTIONS):
                    current_group.append(p)
                    edge_points.remove(p)
                    break
            else:
                break
        loop_groups.append(current_group)
    # process each group
    return [process_group(g, pts) for g in loop_groups]


def dots(points: list[complex], edges: dict[complex, set[complex]],
         scale: float = 20) -> str:
    vbx = max(x.real for x in (*points, *edges)) + 1
    vby = max(x.imag for x in (*points, *edges)) + 1
    return f"""<svg viewBox="-1 -1 {vbx+2} {vby+2}" width="{
        vbx * scale}" height="{vby * scale}">{"".join(f"""<circle cx="{
            p.real
        }" cy="{p.imag}" r="0.2" fill="red" />""" for p in points)}{
        "".join(f"""<line x1="{p1.real}" y1="{
            p1.imag
        }" x2="{((p1 * 2 + p2) / 3).real}" y2="{
            ((p1 * 2 + p2) / 3).imag
        }" stroke="black" stroke-width="0.1" />"""
            for p1 in edges for p2 in edges[p1])}</svg>"""


def debug_singular_polyline_in_svg(
        points: list[complex], current: complex, scale: float = 20) -> str:
    vbx = max(x.real for x in points) + 1
    vby = max(x.imag for x in points) + 1
    return f"""<svg viewBox="-1 -1 {vbx+2} {vby+2}" width="{
        vbx * scale}" height="{vby * scale}"><polyline
    fill="none"
    stroke="black"
    stroke-width="0.1"
    points="{" ".join(map(lambda x: f"{x.real},{x.imag}", points))}">
    </polyline><circle cx="{current.real}" cy="{
        current.imag
    }" r="0.3" fill="blue" /></svg>"""


def example(all_points: list[complex], scale: float = 20) -> str:
    ps = get_outline_points(all_points)
    vbx = max(x.real for p in ps for x in p) + 1
    vby = max(x.imag for p in ps for x in p) + 1
    polylines = "".join(f"""<polyline
    fill="none"
    stroke="black"
    stroke-width="0.1"
    points="{" ".join(map(lambda x: f"{x.real},{x.imag}", p))}">
    </polyline>""" for p in ps)
    return f"""<svg
    viewBox="-1 -1 {vbx + 2} {vby + 2}"
    width="{vbx * scale}"
    height="{vby * scale}">
    {polylines}</svg>"""


print("<style>svg { border: 1px solid black}body{white-space: pre}</style>")
for s in strings:
    print(f"""<pre>{s}</pre>""")
    pts = [complex(c, r)
           for (r, rt) in enumerate(s.splitlines())
           for (c, ch) in enumerate(rt)
           if ch == "#"]
    print(example(pts))
