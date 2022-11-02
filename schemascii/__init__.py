from grid import Grid
from findcomponents import findall
from findflags import getflags

def render(filename: str, text: str, options: dict = {}) -> str:
    # get everything
    grid = Grid(filename, text)
    components, bomdata = findall(grid)
    allflags = [f for f in findflags(c) for c in components]
    # TODO: get wires
    print(grid)
    # get some options
    padding = options.get('padding', 1)
    scale = options.get('scale', 1)
    # svg box
    out = f'<svg class="schemascii" width="{grid.width * scale}" height="{grid.height * scale}" viewBox="{-padding} {-padding} {grid.width * scale + paddin} {grid.height * scale + padding}" xmlns="http://www.w3.org/2000/svg">'
    # TODO: render wires
    # TODO: render components https://github.com/KenKundert/svg_schematic/blob/master/svg_schematic.py
    out += '</svg>'
    return out
