from .inline_config import get_inline_configs
from .configs import apply_config_defaults
from .grid import Grid
from .components import find_all
from .edgemarks import find_edge_marks
from .components_render import render_component
from .wires import get_wires
from .utils import XML
from .errors import *

__version__ = "0.2.2"


def render(filename: str, text: str = None, **options) -> str:
    "Render the Schemascii diagram to an SVG string."
    if text is None:
        with open(filename, encoding="ascii") as f:
            text = f.read()
    # get everything
    grid = Grid(filename, text)
    # Passed-in options override diagram inline options
    options = apply_config_defaults(options
                                    | get_inline_configs(grid)
                                    | options.get("override_options", {}))
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
