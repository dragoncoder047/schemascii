import enum

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
#""",
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
  ###########"""]

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


def cir(list: list[complex], is_forward: bool) -> list[complex]:
    if is_forward:
        return list[1:] + [list[0]]
    else:
        return [list[-1]] + list[:-1]


def cull_disallowed_edges(
        all_points: list[complex],
        edges: dict[complex, set[complex]]) -> dict[complex, list[set]]:
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
        tran_5 = list(zip(
            cir(cir(gaps, False), False),
            cir(gaps, False),
            gaps,
            cir(gaps, True),
            cir(cir(gaps, True), True)))
        # im not quite sure what this is doing
        fixed_edges[p1] = set(p1 + d for (d, (q, a, b, c, w))
                              in zip(DIRECTIONS, tran_5)
                              if b and not ((a and c) or (q and w)))
    return fixed_edges


def walk_graph_to_loop(
        start: complex,
        start_dir: complex,
        edges: dict[complex, set[complex]]) -> list[complex]:
    out: list[complex] = []
    current = start
    current_dir = start_dir
    swd_into: dict[complex, set[complex]] = {}
    while not out or current != start:
        out.append(current)
        print(debug_singular_polyline_in_svg(out, current))
        # log the direction we came from
        swd_into.setdefault(current, set()).add(current_dir)
        # prefer counterclockwise (3 directions),
        # then clockwise (3 directions), then forwards, then backwards
        choices_directions = (rot(current_dir, i)
                              for i in (0, 1, -1, 2, -2, 3, -3, 4))
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
                if d not in swd_into.get(nxt, set()) and bt_d is not None:
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


def process_group(g: list[complex], all_pts: list[complex]) -> list[complex]:
    edges = cull_disallowed_edges(all_pts, points_to_edges(g))
    print(dots(g, edges))
    g = walk_graph_to_loop(
        start=max(g, key=lambda x: x.real * 65536 - x.imag),
        start_dir=1j,
        edges=edges)
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


def dots(points: list[complex], edges: dict[complex, list[complex]],
         scale: float = 20) -> str:
    vbx = max(x.real for x in points) + 1
    vby = max(x.imag for x in points) + 1
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


for s in strings:
    print(f"""<pre>{s}</pre>""")
    pts = [complex(c, r)
           for (r, rt) in enumerate(s.splitlines())
           for (c, ch) in enumerate(rt)
           if ch == "#"]
    print(example(pts))
