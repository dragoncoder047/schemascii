from .grid import Grid
import re
from collections import namedtuple

Cbox = namedtuple('Cbox', 'x1 y1 x2 y2 type id')
smallcomp = re.compile(r'([A-Z]+)(\d+)')

def findsmallcomponents(grid: Grid) -> list[Cbox]:
    components = []
    for i, line in enumerate(grid.lines):
        for m in smallcomp.finditer(line):
            components.append(Cbox(m.start(), i, m.end(), i, m.group(1), int(m.group(2))))
    return components
        
