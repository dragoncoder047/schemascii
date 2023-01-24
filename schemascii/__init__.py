from grid import Grid
from components import find_all
from flags import find_flags


def render(filename: str, text: str = None, options: dict = None) -> str:
    "Render the Schemascii diagram to an SVG string."
    if text is None:
        with open(filename) as f:
            text = f.read()
    if options is None:
        options = {}
    # get everything
    grid = Grid(filename, text)
    components, bomdata = find_all(grid)
    allflags = [f for c in components for f in find_flags(grid, c)]
    # get some options
    padding = options.get('padding', 1)
    scale = options.get('scale', 1)
    # svg box
    out = ('<svg class="schemascii" '
           f'width="{grid.width * scale + padding * 2}" '
           f'height="{grid.height * scale + padding * 2}" '
           f'viewBox="{-padding} {-padding} '
           f'{grid.width * scale + padding * 2} '
           f'{grid.height * scale + padding * 2}" '
           'xmlns="http://www.w3.org/2000/svg">')
    # TODO: render wires
    # TODO: render components
    # https://github.com/KenKundert/svg_schematic/blob/master/svg_schematic.py
    out += '</svg>'
    return out


if __name__ == '__main__':
    print(render("../test_data/test1.txt"))
