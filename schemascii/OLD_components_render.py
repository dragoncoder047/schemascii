from typing import Callable
from cmath import phase, rect
from math import pi
from warnings import warn
from functools import wraps
from .utils import (
    Cbox,
    Terminal,
    BOMData,
    Side,
    arrow_points,
    polylinegon,
    id_text,
    make_text_point,
    bunch_o_lines,
    deep_transform,
    sort_terminals_counterclockwise,
    light_arrows,
    sort_for_flags,
    is_clockwise)
from .errors import TerminalsError, BOMError, UnsupportedComponentError

# pylint: disable=unbalanced-tuple-unpacking

RENDERERS = {}


def component(*rd_s: list[str]) -> Callable:
    "Registers the component under a set of reference designators."

    def rendec(func: Callable[[Cbox, list[Terminal], list[BOMData]], str]):
        for r_d in rd_s:
            rdu = r_d.upper()
            if rdu in RENDERERS:
                raise RuntimeError(f"{rdu} reference designator already taken")
            RENDERERS[rdu] = func
        return func

    return rendec


def n_terminal(n_terminals: int) -> Callable:
    "Ensures the component has N terminals."

    def n_inner(func: Callable) -> Callable:
        @wraps(func)
        def n_check(
                box: Cbox, terminals: list[Terminal],
                bom_data: list[BOMData], **options):
            if len(terminals) != n_terminals:
                raise TerminalsError(
                    f"{box.type}{box.id} component can only "
                    f"have {n_terminals} terminals")
            return func(box, terminals, bom_data, **options)

        return n_check

    return n_inner


def no_ambiguous(func: Callable) -> Callable:
    "Ensures the component has exactly one BOM data marker, and unwraps it."

    @wraps(func)
    def de_ambiguous(
            box: Cbox, terminals: list[Terminal],
            bom_data: list[BOMData], **options):
        if len(bom_data) > 1:
            raise BOMError(
                f"Ambiguous BOM data for {box.type}{box.id}: {bom_data!r}")
        if not bom_data:
            bom_data = [BOMData(box.type, box.id, "")]
        return func(box, terminals, bom_data[0], **options)

    return de_ambiguous


def polarized(func: Callable) -> Callable:
    """Ensures the component has 2 terminals,
    and then sorts them so the + terminal is first."""

    @wraps(func)
    def sort_terminals(
            box: Cbox, terminals: list[Terminal],
            bom_data: list[BOMData], **options):
        if len(terminals) != 2:
            raise TerminalsError(
                f"{box.type}{box.id} component can only have 2 terminals")
        if terminals[1].flag == "+":
            terminals[0], terminals[1] = terminals[1], terminals[0]
        return func(box, terminals, bom_data, **options)

    return sort_terminals


@component("D", "LED", "CR", "IR")
@polarized
@no_ambiguous
def diode(box: Cbox, terminals: list[Terminal], bom_data: BOMData, **options):
    """Draw a diode or LED.
    bom:part-number
    flags:+=positive"""
    t1, t2 = terminals[0].pt, terminals[1].pt
    mid = (t1 + t2) / 2
    angle = phase(t1 - t2)
    lines = [
        (t2, mid + rect(0.3, angle)),
        (t1, mid + rect(-0.3, angle)),
        deep_transform((-0.3 - 0.3j, 0.3 - 0.3j), mid, angle),
    ]
    triangle = deep_transform((-0.3j, 0.3 + 0.3j, -0.3 + 0.3j), mid, angle)
    light_emitting = box.type in ("LED", "IR")
    fill_override = {"stroke": bom_data.data} if box.type == "LED" else {}
    return (
        (light_arrows(mid, angle, True, **options) if light_emitting else "")
        + id_text(
            box,
            bom_data,
            terminals,
            None,
            make_text_point(t1, t2, **options),
            **options,
        )
        + bunch_o_lines(lines, **(options | fill_override))
        + polylinegon(triangle, True, **options)
    )


SIDE_TO_ANGLE_MAP = {
    Side.RIGHT: pi,
    Side.TOP: pi / 2,
    Side.LEFT: 0,
    Side.BOTTOM: 3 * pi / 2,
}


@component("U", "IC")
@no_ambiguous
def integrated_circuit(
    box: Cbox, terminals: list[Terminal], bom_data: BOMData, **options
):
    """Draw an IC.
    bom:part-number[,pin1-label[,pin2-label[,...]]]"""
    label_style = options["label"]
    scale = options["scale"]
    sz = (box.p2 - box.p1) * scale
    mid = (box.p2 + box.p1) * scale / 2
    part_num, *pin_labels = map(str.strip, bom_data.data.split(","))
    out = xmltag("rect", 
        x=box.p1.real * scale,
        y=box.p1.imag * scale,
        width=sz.real,
        height=sz.imag,
        stroke__width=options["stroke_width"],
        stroke=options["stroke"],
        fill="transparent",
    )
    for term in terminals:
        out += bunch_o_lines(
            [(term.pt,
              term.pt + rect(1, SIDE_TO_ANGLE_MAP[term.side]))],
            **options)
    if "V" in label_style and part_num:
        out += xmltag("text", 
            xmltag("tspan", part_num, class_="part-num"),
            x=mid.real,
            y=mid.imag,
            text__anchor="middle",
            font__size=options["scale"],
            fill=options["stroke"],
        )
        mid -= 1j * scale
    if "L" in label_style and not options["nolabels"]:
        out += xmltag("text", 
            xmltag("tspan", f"{box.type}{box.id}", class_="cmp-id"),
            x=mid.real,
            y=mid.imag,
            text__anchor="middle",
            font__size=options["scale"],
            fill=options["stroke"],
        )
    s_terminals = sort_terminals_counterclockwise(terminals)
    for terminal, label in zip(s_terminals, pin_labels):
        sc_text_pt = terminal.pt * scale
        out += xmltag("text", 
            label,
            x=sc_text_pt.real,
            y=sc_text_pt.imag,
            text__anchor=(
                "start" if (terminal.side in (
                    Side.TOP, Side.BOTTOM)) else "middle"
            ),
            font__size=options["scale"],
            fill=options["stroke"],
            class_="pin-label",
        )
    warn(
        "ICs are not fully implemented yet. "
        "Pin labels may have not been rendered correctly."
    )
    return out


@component("J", "P")
@n_terminal(1)
@no_ambiguous
def jack(box: Cbox, terminals: list[Terminal], bom_data: BOMData, **options):
    """Draw a jack connector or plug.
    bom:label[,{circle/input/output}]"""
    scale = options["scale"]
    t1 = terminals[0].pt
    t2 = t1 + rect(1, SIDE_TO_ANGLE_MAP[terminals[0].side])
    sc_t2 = t2 * scale
    sc_text_pt = sc_t2 + rect(scale / 2, SIDE_TO_ANGLE_MAP[terminals[0].side])
    style = "input" if terminals[0].side in (Side.LEFT, Side.TOP) else "output"
    if any(bom_data.data.endswith(x)
           for x in (",circle", ",input", ",output")):
        style = bom_data.data.split(",")[-1]
        bom_data = BOMData(
            bom_data.type,
            bom_data.id,
            bom_data.data.rstrip("cirlenputo").removesuffix(","),
        )
    if style == "circle":
        return (
            bunch_o_lines([(t1, t2)], **options)
            + xmltag("circle", 
                cx=sc_t2.real,
                cy=sc_t2.imag,
                r=scale / 4,
                stroke__width=options["stroke_width"],
                stroke=options["stroke"],
                fill="transparent",
            )
            + id_text(box, bom_data, terminals, None, sc_text_pt, **options)
        )
    if style == "output":
        t1, t2 = t2, t1
    return bunch_o_lines(arrow_points(t1, t2), **options) + id_text(
        box, bom_data, terminals, None, sc_text_pt, **options
    )


@component("Q", "MOSFET", "MOS", "FET")
@n_terminal(3)
@no_ambiguous
def transistor(box: Cbox, terminals: list[Terminal],
               bom_data: BOMData, **options):
    """Draw a bipolar transistor (PNP/NPN) or FET (NFET/PFET).
    bom:{npn/pnp/nfet/pfet}:part-number
    flags:s=source,d=drain,g=gate,e=emitter,c=collector,b=base"""
    if not any(
            bom_data.data.lower().startswith(x)
            for x in ("pnp", "npn", "nfet", "pfet")):
        raise BOMError(f"Need type of transistor for {box.type}{box.id}")
    silicon_type, *part_num = bom_data.data.split(":")
    part_num = ":".join(part_num)
    silicon_type = silicon_type.lower()
    bom_data = BOMData(bom_data.type, bom_data.id, part_num)
    if "fet" in silicon_type:
        ae, se, ctl = sort_for_flags(terminals, box, "s", "d", "g")
    else:
        ae, se, ctl = sort_for_flags(terminals, box, "e", "c", "b")
    ap, sp = ae.pt, se.pt
    diff = sp - ap
    if diff.real == 0:
        mid = complex(ap.real, ctl.pt.imag)
    elif diff.imag == 0:
        mid = complex(ctl.pt.real, ap.imag)
    else:
        # From wolfram alpha "solve m*(x-x1)+y1=(-1/m)*(x-x2)+y2 for x"
        # x = (m^2 x1 - m y1 + m y2 + x2)/(m^2 + 1)
        slope = diff.imag / diff.real
        mid_x = (slope**2 * ap.real
                 - slope * ap.imag
                 + slope * ctl.pt.imag
                 + ctl.pt.real) / (slope**2 + 1)
        mid = complex(mid_x, slope * (mid_x - ap.real) + ap.imag)
    theta = phase(ap - sp)
    backwards = 1 if is_clockwise([ae, se, ctl]) else -1
    thetaquarter = theta + (backwards * pi / 2)
    out_lines = [
        (ap, mid + rect(0.8, theta)),  # Lead in
        (sp, mid - rect(0.8, theta)),  # Lead out
    ]
    if "fet" in silicon_type:
        arr = mid + rect(0.8, theta), mid + \
            rect(0.8, theta) + rect(0.7, thetaquarter)
        if "nfet" == silicon_type:
            arr = arr[1], arr[0]
        out_lines.extend(
            [
                *arrow_points(*arr),
                (
                    mid - rect(0.8, theta),
                    mid - rect(0.8, theta) + rect(0.7, thetaquarter),
                ),
                (
                    mid + rect(1, theta) + rect(0.7, thetaquarter),
                    mid - rect(1, theta) + rect(0.7, thetaquarter),
                ),
                (
                    mid + rect(0.5, theta) + rect(1, thetaquarter),
                    mid - rect(0.5, theta) + rect(1, thetaquarter),
                ),
            ]
        )
    else:
        arr = mid + rect(0.8, theta), mid + \
            rect(0.4, theta) + rect(1, thetaquarter)
        if "npn" == silicon_type:
            arr = arr[1], arr[0]
        out_lines.extend(
            [
                *arrow_points(*arr),
                (
                    mid - rect(0.8, theta),
                    mid - rect(0.4, theta) + rect(1, thetaquarter),
                ),
                (
                    mid + rect(1, theta) + rect(1, thetaquarter),
                    mid - rect(1, theta) + rect(1, thetaquarter),
                ),
            ]
        )
    out_lines.append((mid + rect(1, thetaquarter), ctl.pt))
    return (id_text(box,
                    bom_data,
                    [ae, se],
                    None,
                    make_text_point(ap, sp, **options), **options)
            + bunch_o_lines(out_lines, **options))


@component("G", "GND")
@n_terminal(1)
@no_ambiguous
def ground(box: Cbox, terminals: list[Terminal], bom_data: BOMData, **options):
    """Draw a ground symbol.
    bom:[{earth/chassis/signal/common}]"""
    icon_type = bom_data.data or "earth"
    points = [(0, 1j), (-0.5 + 1j, 0.5 + 1j)]
    match icon_type:
        case "earth":
            points += [(-0.33 + 1.25j, 0.33 + 1.25j),
                       (-0.16 + 1.5j, 0.16 + 1.5j)]
        case "chassis":
            points += [
                (-0.5 + 1j, -0.25 + 1.5j),
                (1j, 0.25 + 1.5j),
                (0.5 + 1j, 0.75 + 1.5j),
            ]
        case "signal":
            points += [(-0.5 + 1j, 1.5j), (0.5 + 1j, 1.5j)]
        case "common":
            pass
        case _:
            raise BOMError(f"Unknown ground symbol type: {icon_type}")
    points = deep_transform(points, terminals[0].pt, pi / 2)
    return bunch_o_lines(points, **options)


@component("S", "SW", "PB")
@n_terminal(2)
@no_ambiguous
def switch(box: Cbox, terminals: list[Terminal], bom_data: BOMData, **options):
    """Draw a mechanical switch symbol.
    bom:{nc/no}[m][:label]"""
    icon_type = bom_data.data or "no"
    if ":" in icon_type:
        icon_type, *b = icon_type.split(":")
        bom_data = BOMData(bom_data.type, bom_data.id, ":".join(b))
    else:
        bom_data = BOMData(bom_data.type, bom_data.id, "")
    t1, t2 = terminals[0].pt, terminals[1].pt
    mid = (t1 + t2) / 2
    angle = phase(t1 - t2)
    scale = options["scale"]
    out = (xmltag("circle", cx=(rect(-scale, angle) + mid * scale).real,
                      cy=(rect(-scale, angle) + mid * scale).imag,
                      r=scale / 4,
                      stroke="transparent",
                      fill=options["stroke"],
                      class_="filled")
           + xmltag("circle", cx=(rect(scale, angle) + mid * scale).real,
                        cy=(rect(scale, angle) + mid * scale).imag,
                        r=scale / 4,
                        stroke="transparent",
                        fill=options["stroke"],
                        class_="filled")
           + bunch_o_lines([
               (t1, mid + rect(1, angle)),
               (t2, mid + rect(-1, angle))], **options))
    sc = 1
    match icon_type:
        case "nc":
            points = [(-1j, -.3+1j)]
        case "no":
            points = [(-1j, -.8+1j)]
            sc = 1.9
        case "ncm":
            points = [(.3-1j, .3+1j)]
            out += polylinegon(
                deep_transform([-.5+.6j, -.5-.6j, .3-.6j, .3+.6j], mid, angle),
                True, **options)
            sc = 1.3
        case "nom":
            points = [(-.5-1j, -.5+1j)]
            out += polylinegon(
                deep_transform([-1+.6j, -1-.6j, -.5-.6j, -.5+.6j], mid, angle),
                True, **options)
            sc = 2.5
        case _:
            raise BOMError(f"Unknown switch symbol type: {icon_type}")
    points = deep_transform(points, mid, angle)
    return bunch_o_lines(points, **options) + out + id_text(
        box, bom_data, terminals, None, make_text_point(
            t1, t2, **(options | {"offset_scaler": sc})), **options)


# code for drawing stuff
# https://github.com/pfalstad/circuitjs1/tree/master/src/com/lushprojects/circuitjs1/client
# https://github.com/KenKundert/svg_schematic/blob/0abb5dc/svg_schematic.py
# https://yqnn.github.io/svg-path-editor/


# These are SVG <path> strings for each component
# + is on the top unless otherwise noted
# terminals will be connected at (0, -1) and (0, 1) relative to the paths here
# if they aren't the path will be transformed
{
    # fuse
    "F": ("M0-.9A.1.1 0 000-1.1.1.1 0 000-.9ZM0-1Q.5-.5 0 0T0 1Q-.5.5 0 "
          "0T0-1ZM0 1.1A.1.1 0 000 .9.1.1 0 000 1.1Z"),
    # jumper pads
    "JP": "M0-1Q-1-1-1-.25H1Q1-1 0-1ZM0 1Q-1 1-1 .25H1Q1 1 0 1",
    # loudspeaker
    "LS": "M0-1V-.5H-.25V.5H.25V-.5H0M0 1V.5ZM1-1 .25-.5V.5L1 1Z",
    # electret mic
    "MIC": "M1 0A1 1 0 00-1 0 1 1 0 001 0V-1 1Z",
}


def render_component(
    box: Cbox, terminals: list[Terminal], bom_data: list[BOMData], **options
):
    "Render the component into an SVG string."
    if box.type not in RENDERERS:
        raise UnsupportedComponentError(box.type)
    return xmltag("g", 
        RENDERERS[box.type](box, terminals, bom_data, **options),
        class_=f"component {box.type}",
    )


__all__ = ["render_component"]
