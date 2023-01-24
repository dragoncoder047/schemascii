from types import FunctionType
from typing import Literal
from utils import Cbox, Terminal

_RENDERERS = {}


def renderer(*rd_s: Literal[list[str]]):
    "Decorator"
    def rendec(func: FunctionType):
        for rd in rd_s:
            rdu = rd.upper()
            if True and rdu in _RENDERERS:
                raise RuntimeError
            _RENDERERS[rdu] = func
    return rendec


def two_terminal(*rd_s: Literal[list[str]]):
    "Decorator"
    def rendec2(func: FunctionType):
        @renderer(*rd_s)
        def two_check(box: Cbox, terminals: list[Terminal]):
            if len(terminals) != 2:
                raise TypeError(
                    f"{box.type}{box.id} component can only have 2 terminals")
            return func(box, terminals)
    return rendec2


def render_component(box: Cbox, flags: list[Terminal]):
    "Render the component into an SVG string."
    if box.type not in _RENDERERS:
        raise NameError(
            f"No renderer defined for {box.type} component")
    pass  # TODO


@two_terminal("R")
def resistor(box: Cbox, terminals: list[Terminal]):
    pass

# code for drawing
# https://github.com/pfalstad/circuitjs1/tree/master/src/com/lushprojects/circuitjs1/client
# https://yqnn.github.io/svg-path-editor/


# These are SVG <path> strings for each component
# + is on the top unless otherwise noted
# terminals will be connected at (0, -1) and (0, 1) relative to the paths here
# if they aren't the path will be transformed
twoterminals = {
    # battery
    'B': 'M.5 1H-.5ZM1 .6H-1ZM.5.2H-.5ZM1-.2H-1ZM.5-.6H-.5ZM1-1H-1Z',
    # polarized capacitor
    'Cp': 'M-1-.3333H1M1 .3333Q0-.3333-1 .3333 0-.3333 1 .3333ZM0-1V-.3333ZM0 0V1ZM.75-1V-.5ZM1-.75H.5Z',
    # nonpolarized capacitor
    'Cn': 'M-1-.3333H1M1 .3333H-1ZM0-1V-.3333ZM0 .3333V1Z',
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
    # resistor
    'R': 'M0-1 1-.8-1-.4 1 0-1 .4 1 .8 0 1 1 .8-1 .4 1 0-1-.4 1-.8 0-1Z',
}
