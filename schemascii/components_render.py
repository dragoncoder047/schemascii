from typing import Callable
from cmath import phase, rect
from math import pi
from warnings import warn
from .utils import (Cbox, Terminal, BOMData, XML, Side, arrow_points,
                    polylinegon, id_text, make_text_point,
                    bunch_o_lines, deep_transform, make_plus, make_variable,
                    sort_counterclockwise, light_arrows, sort_for_flags, is_clockwise)
from .errors import TerminalsError, BOMError, UnsupportedComponentError

RENDERERS = {}


def component(*rd_s: list[str]) -> Callable:
    "Registers the component under a set of reference designators."
    def rendec(func: Callable[[Cbox, list[Terminal], list[BOMData]], str]):
        for r_d in rd_s:
            rdu = r_d.upper()
            if rdu in RENDERERS:
                raise RuntimeError(
                    f"{rdu} reference designator already taken")
            RENDERERS[rdu] = func
        return func
    return rendec


def n_terminal(n_terminals: int) -> Callable:
    "Ensures the component has N terminals."
    def n_inner(func: Callable) -> Callable:
        def n_check(
                box: Cbox,
                terminals: list[Terminal],
                bom_data: list[BOMData],
                **options):
            if len(terminals) != n_terminals:
                raise TerminalsError(
                    f"{box.type}{box.id} component can only "
                    f"have {n_terminals} terminals")
            return func(box, terminals, bom_data, **options)
        return n_check
    return n_inner


def no_ambiguous(func: Callable) -> Callable:
    "Ensures the component has exactly one BOM data marker, and unwraps it."
    def de_ambiguous(
            box: Cbox,
            terminals: list[Terminal],
            bom_data: list[BOMData],
            **options):
        if len(bom_data) > 1:
            raise BOMError(
                f"Ambiguous BOM data for {box.type}{box.id}: {bom_data!r}")
        if not bom_data:
            bom_data = [BOMData(box.type, box.id, "")]
        return func(
            box,
            terminals,
            bom_data[0],
            **options)
    return de_ambiguous


def polarized(func: Callable) -> Callable:
    """Ensures the component has 2 terminals,
    and then sorts them so the + terminal is first."""
    def sort_terminals(
            box: Cbox,
            terminals: list[Terminal],
            bom_data: list[BOMData],
            **options):
        if len(terminals) != 2:
            raise TerminalsError(
                f"{box.type}{box.id} component can only "
                f"have 2 terminals")
        if terminals[1].flag == '+':
            terminals[0], terminals[1] = terminals[1], terminals[0]
        return func(
            box,
            terminals,
            bom_data,
            **options)
    return sort_terminals


def resistor(
        box: Cbox,
        terminals: list[Terminal],
        bom_data: BOMData,
        **options):
    "Draw a resistor"
    t1, t2 = terminals[0].pt, terminals[1].pt
    vec = t1 - t2
    mid = (t1 + t2) / 2
    length = abs(vec)
    angle = phase(vec)
    quad_angle = angle + pi / 2
    points = [t1]
    for i in range(1, 4 * int(length)):
        points.append(t1 - rect(i / 4, angle) +
                      pow(-1, i) * rect(1, quad_angle) / 4)
    points.append(t2)
    text_pt = make_text_point(t1, t2, **options)
    return (polylinegon(points, **options)
            + make_variable(mid, angle, "V" in box.type, **options)
            + id_text(
        box, bom_data, terminals, (("Ω", False), ("W", False)),
        text_pt, **options))


# Register it
component("R", "RV", "VR")(n_terminal(2)(no_ambiguous(resistor)))


@component("C", "CV", "VC")
@n_terminal(2)
@no_ambiguous
def capacitor(
        box: Cbox,
        terminals: list[Terminal],
        bom_data: BOMData,
        **options):
    "Draw a capacitor"
    t1, t2 = terminals[0].pt, terminals[1].pt
    mid = (t1 + t2) / 2
    angle = phase(t1 - t2)
    lines = [
        (t1, mid + rect(.25, angle)),
        (t2, mid + rect(-.25, angle))] + deep_transform([
            (complex(.4,  .25), complex(-.4,  .25)),
            (complex(.4, -.25), complex(-.4, -.25)),
        ], mid, angle)
    text_pt = make_text_point(t1, t2, **options)
    return (bunch_o_lines(lines, **options)
            + make_plus(terminals, mid, angle, **options)
            + make_variable(mid, angle, "V" in box.type, **options)
            + id_text(
        box, bom_data, terminals, (("F", True), ("V", False)),
        text_pt, **options))


@component("B", "BT", "BAT")
@polarized
@no_ambiguous
def battery(
        box: Cbox,
        terminals: list[Terminal],
        bom_data: BOMData,
        **options):
    "Draw a battery cell"
    t1, t2 = terminals[0].pt, terminals[1].pt
    mid = (t1 + t2) / 2
    angle = phase(t1 - t2)
    lines = [
        (t1, mid + rect(.5, angle)),
        (t2, mid + rect(-.5, angle))] + deep_transform([
            (complex(.5,  .5), complex(-.5,  .5)),
            (complex(.25, .16), complex(-.25, .16)),
            (complex(.5, -.16), complex(-.5,  -.16)),
            (complex(.25, -.5), complex(-.25, -.5)),
        ], mid, angle)
    text_pt = make_text_point(t1, t2, **options)
    return (id_text(
        box, bom_data, terminals, (("V", False), ("Ah", False)),
        text_pt, **options)
        + bunch_o_lines(lines, **options))


@component("D", "LED", "CR", "IR")
@polarized
@no_ambiguous
def diode(
        box: Cbox,
        terminals: list[Terminal],
        bom_data: BOMData,
        **options):
    "Draw a diode or LED"
    t1, t2 = terminals[0].pt, terminals[1].pt
    mid = (t1 + t2) / 2
    angle = phase(t1 - t2)
    lines = [
        (t2, mid + rect(.3, angle)),
        (t1, mid + rect(-.3, angle)),
        deep_transform((-.3-.3j, .3-.3j), mid, angle)]
    triangle = deep_transform((-.3j, .3+.3j, -.3+.3j), mid, angle)
    text_pt = make_text_point(t1, t2, **options)
    light_emitting = "LED", "IR"
    return ((light_arrows(mid, angle, True, **options)
             if box.type in light_emitting else "")
            + id_text(box, bom_data, terminals, None, text_pt, **options)
            + bunch_o_lines(lines, **options)
            + polylinegon(triangle, True, **options))


SIDE_TO_ANGLE_MAP = {
    Side.RIGHT: pi,
    Side.TOP:  pi / 2,
    Side.LEFT: 0,
    Side.BOTTOM: 3 * pi / 2,
}


@component("U", "IC")
@no_ambiguous
def integrated_circuit(
        box: Cbox,
        terminals: list[Terminal],
        bom_data: BOMData,
        **options):
    "Draw an IC"
    label_style = options["label"]
    scale = options["scale"]
    sz = (box.p2 - box.p1) * scale
    mid = (box.p2 + box.p1) * scale / 2
    part_num, *pin_labels = map(str.strip, bom_data.data.split(","))
    out = XML.rect(
        x=box.p1.real * scale,
        y=box.p1.imag * scale,
        width=sz.real,
        height=sz.imag,
        stroke__width=options["stroke_width"],
        stroke=options["stroke"],
        fill="transparent")
    for term in terminals:
        out += bunch_o_lines([(
            term.pt,
            term.pt + rect(1, SIDE_TO_ANGLE_MAP[term.side])
        )], **options)
    if "V" in label_style and part_num:
        out += XML.text(
            XML.tspan(part_num, class_="part-num"),
            x=mid.real,
            y=mid.imag,
            text__anchor="middle",
            font__size=options["scale"],
            fill=options["stroke"])
        mid -= 1j * scale
    if "L" in label_style and not options["nolabels"]:
        out += XML.text(
            XML.tspan(f"{box.type}{box.id}", class_="cmp-id"),
            x=mid.real,
            y=mid.imag,
            text__anchor="middle",
            font__size=options["scale"],
            fill=options["stroke"])
    s_terminals = sort_counterclockwise(terminals)
    for terminal, label in zip(s_terminals, pin_labels):
        sc_text_pt = terminal.pt * scale
        out += XML.text(
            label,
            x=sc_text_pt.real,
            y=sc_text_pt.imag,
            text__anchor=("start" if (terminal.side in (Side.TOP, Side.BOTTOM))
                          else "middle"),
            font__size=options["scale"],
            fill=options["stroke"],
            class_="pin-label")
    warn("ICs are not fully implemented yet. "
         "Pin labels may have not been rendered correctly.")
    return out


@component("J", "P")
@n_terminal(1)
@no_ambiguous
def jack(
        box: Cbox,
        terminals: list[Terminal],
        bom_data: BOMData,
        **options):
    "Draw a jack connector or plug"
    scale = options["scale"]
    sc_t1 = terminals[0].pt * scale
    sc_t2 = sc_t1 + rect(scale, SIDE_TO_ANGLE_MAP[terminals[0].side])
    sc_text_pt = sc_t2 + rect(scale * 2, SIDE_TO_ANGLE_MAP[terminals[0].side])
    return (
        XML.line(
            x1=sc_t1.real,
            x2=sc_t2.real,
            y1=sc_t1.imag,
            y2=sc_t2.imag,
            stroke__width=options["stroke_width"],
            stroke=options["stroke"])
        + XML.circle(
            cx=sc_t2.real,
            cy=sc_t2.imag,
            r=scale / 4,
            stroke__width=options["stroke_width"],
            stroke=options["stroke"],
            fill="transparent")
        + id_text(box, bom_data, terminals, None, sc_text_pt, **options))


@component("Q", "MOSFET", "MOS", "FET")
@n_terminal(3)
@no_ambiguous
def transistor(
        box: Cbox,
        terminals: list[Terminal],
        bom_data: BOMData,
        **options):
    "Draw a bipolar transistor (PNP/NPN) or FET (NFET/PFET)"
    if all(x not in bom_data.data.lower() for x in ("pnp:", "npn:", "nfet:", "pfet:")):
        raise BOMError(
            f"Need type of transistor for {box.type}{box.id}")
    silicon_type, part_num = bom_data.data.split(":")
    silicon_type = silicon_type.lower()
    bom_data = BOMData(bom_data.type, bom_data.id, part_num)
    if 'fet' in silicon_type:
        ae, se, ctl = sort_for_flags(terminals, box, "s", "d", "g")
    else:
        ae, se, ctl = sort_for_flags(terminals, box, "e", "c", "b")
    ap, sp = ae.pt, se.pt
    mid = (ap + sp) / 2 # TODO: slide this to line up with middle
    theta = phase(ap - sp)
    backwards = 1 if is_clockwise([ae, se, ctl]) else -1
    thetaquarter = theta + (backwards * pi / 2)
    out_lines = [
        (ap, mid + rect(.8, theta)),  # Lead in
        (sp, mid - rect(.8, theta)),  # Lead out
    ]
    if 'fet' in silicon_type:
        arr = mid + rect(.8, theta), mid + rect(.8, theta) + rect(.7, thetaquarter)
        if 'nfet' == silicon_type:
            arr = arr[1], arr[0]
        out_lines.extend([
            *arrow_points(*arr),
            (mid - rect(.8, theta), mid - rect(.8, theta) + rect(.7, thetaquarter)),
            (mid + rect(1, theta) + rect(.7, thetaquarter),
             mid - rect(1, theta) + rect(.7, thetaquarter)),
            (mid + rect(.5, theta) + rect(1, thetaquarter),
             mid - rect(.5, theta) + rect(1, thetaquarter)),
        ])
    else:
        arr = mid + rect(.8, theta), mid + rect(.4, theta) + rect(1, thetaquarter)
        if 'npn' == silicon_type:
            arr = arr[1], arr[0]
        out_lines.extend([
            *arrow_points(*arr),
            (mid - rect(.8, theta), mid - rect(.4, theta) + rect(1, thetaquarter)),
            (mid + rect(1, theta) + rect(1, thetaquarter),
             mid - rect(1, theta) + rect(1, thetaquarter)),
        ])
    text_pt = make_text_point(ap, sp, **options)
    return (id_text(box, bom_data, [ae, se], None, text_pt, **options)
            + bunch_o_lines(out_lines, **options))

# code for drawing stuff
# https://github.com/pfalstad/circuitjs1/tree/master/src/com/lushprojects/circuitjs1/client
# https://github.com/KenKundert/svg_schematic/blob/0abb5dc/svg_schematic.py
# https://yqnn.github.io/svg-path-editor/


# These are SVG <path> strings for each component
# + is on the top unless otherwise noted
# terminals will be connected at (0, -1) and (0, 1) relative to the paths here
# if they aren't the path will be transformed
twoterminals = {
    # fuse
    'F': 'M0-.9A.1.1 0 000-1.1.1.1 0 000-.9ZM0-1Q.5-.5 0 0T0 1Q-.5.5 0 0T0-1ZM0 1.1A.1.1 0 000 .9.1.1 0 000 1.1Z',
    # jumper pads
    'JP': 'M0-1Q-1-1-1-.25H1Q1-1 0-1ZM0 1Q-1 1-1 .25H1Q1 1 0 1',
    # inductor style 1 (humps)
    'L': 'M0-1A.1.1 0 010-.6.1.1 0 010-.2.1.1 0 010 .2.1.1 0 010 .6.1.1 0 010 1 .1.1 0 000 .6.1.1 0 000 .2.1.1 0 000-.2.1.1 0 000-.6.1.1 0 000-1Z',
    # inductor style 2 (coil)
    # 'L': 'M0-1C1-1 1-.2 0-.2S-1-.8 0-.8 1 0 0 0-1-.6 0-.6 1 .2 0 .2-1-.4 0-.4 1 .4 0 .4-1-.2 0-.2 1 .6 0 .6-1 0 0 0 1 .8 0 .8-1 .2 0 .2 1 1 0 1C1 1 1 .2 0 .2S-1 .8 0 .8 1 0 0 0-1 .6 0 .6 1-.2 0-.2-1 .4 0 .4 1-.4 0-.4-1 .2 0 .2 1-.6 0-.6-1 0 0 0 1-.8 0-.8-1-.2 0-.2 1-1 0-1Z',
    # loudspeaker
    'LS': 'M0-1V-.5H-.25V.5H.25V-.5H0M0 1V.5ZM1-1 .25-.5V.5L1 1Z',
    # electret mic
    'MIC': 'M1 0A1 1 0 00-1 0 1 1 0 001 0V-1 1Z',
}


def render_component(
        box: Cbox,
        terminals: list[Terminal],
        bom_data: list[BOMData],
        **options):
    "Render the component into an SVG string."
    if box.type not in RENDERERS:
        raise UnsupportedComponentError(box.type)
    return XML.g(
        RENDERERS[box.type](box, terminals, bom_data, **options),
        class_=f"component {box.type}"
    )


__all__ = ['render_component']
