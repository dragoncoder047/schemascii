from .grid import Grid
from .findcomponents import findall
from .findflags import getflags


def render(filename: str, text: str = None, options: dict = None) -> str:
    if text is None:
        with open(filename) as f:
            text = f.read()
    if options is None:
        options = {}
    # get everything
    grid = Grid(filename, text)
    components, bomdata = findall(grid)
    allflags = [f for c in components for f in getflags(grid, c)]
    # TODO: get wires
    print(grid)
    # get some options
    padding = options.get('padding', 1)
    scale = options.get('scale', 1)
    # svg box
    out = ('<svg class="schemascii" ' +
           f'width="{grid.width * scale}" ' +
           f'height="{grid.height * scale}" ' +
           f'viewBox="{-padding} {-padding} {grid.width * scale + padding} {grid.height * scale + padding}" ' +
           'xmlns="http://www.w3.org/2000/svg">')
    # TODO: render wires
    # TODO: render components https://github.com/KenKundert/svg_schematic/blob/master/svg_schematic.py
    out += '</svg>'
    return out
