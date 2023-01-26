from typing import Callable
from cmath import phase, rect
from math import pi
from utils import (Cbox, Terminal, BOMData, XML, Side,
                   polylinegon, id_text, make_text_point,
                   bunch_o_lines, deep_transform, make_plus)
from metric import format_metric_unit

RENDERERS = {}
# cSpell:ignore rendec Cbox polylinegon


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
                **kwargs):
            if len(terminals) != n_terminals:
                raise TypeError(
                    f"{box.type}{box.id} component can only "
                    f"have {n_terminals} terminals")
            return func(box, terminals, bom_data, **kwargs)
        return n_check
    return n_inner


def no_ambiguous(func: Callable) -> Callable:
    "Ensures the component has exactly one BOM data marker, and unwraps it."
    def de_ambiguous(
            box: Cbox,
            terminals: list[Terminal],
            bom_data: list[BOMData],
            **kwargs):
        if len(bom_data) > 1:
            raise ValueError(
                f"Ambiguous BOM data for {box.type}{box.id}: {bom_data!r}")
        return func(
            box,
            terminals,
            bom_data[0] if bom_data else None,
            **kwargs)
    return de_ambiguous


def polarized(func: Callable) -> Callable:
    """Ensures the component has 2 terminals,
    and then sorts them so the + terminal is first."""
    def sort_terminals(
            box: Cbox,
            terminals: list[Terminal],
            bom_data: list[BOMData],
            **kwargs):
        if len(terminals) != 2:
            raise TypeError(
                f"{box.type}{box.id} component can only "
                f"have 2 terminals")
        if terminals[1].flag == '+':
            terminals[0], terminals[1] = terminals[1], terminals[0]
        return func(
            box,
            terminals,
            bom_data,
            **kwargs)
    return sort_terminals


@component("R")
@n_terminal(2)
@no_ambiguous
def resistor(
        box: Cbox,
        terminals: list[Terminal],
        bom_data: BOMData | None,
        **kwargs):
    "Draw a resistor"
    t1, t2 = terminals[0].pt, terminals[1].pt
    vec = t1 - t2
    length = abs(vec)
    angle = phase(vec)
    quad_angle = angle + pi / 2
    points = [t1]
    for i in range(1, 4 * int(length)):
        points.append(t1 - rect(i / 4, angle) +
                      pow(-1, i) * rect(1, quad_angle) / 4)
    points.append(t2)
    text_pt = make_text_point(t1, t2, **kwargs)
    return (id_text(box, bom_data, terminals, "&ohm;", text_pt, **kwargs)
            + polylinegon(points, **kwargs))


@component("C")
@polarized
@no_ambiguous
def capacitor(
        box: Cbox,
        terminals: list[Terminal],
        bom_data: BOMData | None,
        **kwargs):
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
    text_pt = make_text_point(t1, t2, **kwargs)
    return (id_text(box, bom_data, terminals, "F", text_pt, **kwargs)
            + bunch_o_lines(lines, **kwargs)
            + make_plus(terminals, mid, angle, **kwargs))


@component("D", "LED", "CR")
@polarized
@no_ambiguous
def diode(
        box: Cbox,
        terminals: list[Terminal],
        bom_data: BOMData | None,
        **kwargs):
    "Draw a diode or LED"
    t1, t2 = terminals[0].pt, terminals[1].pt
    mid = (t1 + t2) / 2
    angle = phase(t1 - t2)
    lines = [
        (t2, mid + rect(.3, angle)),
        (t1, mid + rect(-.3, angle)),
        deep_transform((-.3-.3j, .3-.3j), mid, angle)]
    triangle = deep_transform((-.3j, .3+.3j, -.3+.3j), mid, angle)
    text_pt = make_text_point(t1, t2, **kwargs)
    return (id_text(box, bom_data, terminals, None, text_pt, **kwargs)
            + bunch_o_lines(lines, **kwargs)
            + polylinegon(triangle, True, **kwargs))

# code for drawing
# https://github.com/pfalstad/circuitjs1/tree/master/src/com/lushprojects/circuitjs1/client
# https://github.com/KenKundert/svg_schematic/blob/0abb5dc/svg_schematic.py
# https://yqnn.github.io/svg-path-editor/


# These are SVG <path> strings for each component
# + is on the top unless otherwise noted
# terminals will be connected at (0, -1) and (0, 1) relative to the paths here
# if they aren't the path will be transformed
twoterminals = {
    # battery
    'B': 'M.5 1H-.5ZM1 .6H-1ZM.5.2H-.5ZM1-.2H-1ZM.5-.6H-.5ZM1-1H-1Z',
    # diode
    'D': 'M1 1H-1 0L-1-1H1L0 1Z',
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
        **kwargs):
    "Render the component into an SVG string."
    if box.type not in RENDERERS:
        raise NameError(
            f"No renderer defined for {box.type} component")
    return XML.g(
        RENDERERS[box.type](box, terminals, bom_data, **kwargs),
        class_=f"component {box.type}"
    )


__all__ = ['render_component']
