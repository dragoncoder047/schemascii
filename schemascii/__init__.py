from .grid import Grid
from .components import find_all
from .edgemarks import find_edge_marks
from .components_render import render_component
from .wires import get_wires
from .utils import XML
from .errors import *

__version__ = "0.1.2"

default_options = {
    'padding': 10,
    'scale': 15,
    'stroke_width': 2,
    'stroke': 'black',
    'label': 'LV',
    'nolabels': False,
}

option_types = {
    'padding': float,
    'scale': float,
    'stroke_width': float,
    'stroke': str,
    'label': str,
    'nolabels': bool,
}


def render(filename: str, text: str = None, **options) -> str:
    "Render the Schemascii diagram to an SVG string."
    if text is None:
        with open(filename, encoding="ascii") as f:
            text = f.read()
    # default options
    options = default_options | options
    for oname, otypefun in option_types.items():
        options[oname] = otypefun(options[oname])
    # get everything
    grid = Grid(filename, text)
    components, bom_data = find_all(grid)
    terminals = {c: find_edge_marks(grid, c) for c in components}
    fixed_bom_data = {c: [b for b in bom_data if
                          b.id == c.id and b.type == c.type]
                      for c in components}
    # get some options
    padding = options['padding']
    scale = options['scale']

    wires = get_wires(grid, **options)
    components_strs = (render_component(
        c, terminals[c], fixed_bom_data[c], **options)
        for c in components)
    return XML.svg(
        wires, *components_strs,
        width=grid.width * scale + padding * 2,
        height=grid.height * scale + padding * 2,
        viewBox=f'{-padding} {-padding} '
        f'{grid.width * scale + padding * 2} '
        f'{grid.height * scale + padding * 2}',
        xmlns="http://www.w3.org/2000/svg",
        class_="schemascii",
    )


if __name__ == '__main__':
    print(render(
        "test_data/test_resistors.txt",
        scale=20, padding=20, stroke_width=2,
        stroke="black"))
