from .grid import Grid
import re
from collections import namedtuple

Cbox = namedtuple('Cbox', 'x1 y1 x2 y2 type id')
BOMData = namedtuple('BOMData', 'type id data')
smallcompbom = re.compile(r'([A-Z]+)(\d+)(?::[^\s]+)?')

def findsmall(grid: Grid) -> tuple[list[Cbox], list[BOMData]]:
    components = []
    boms = []
    for i, line in enumerate(grid.lines):
        for m in smallcompbom.finditer(line):
            if m.group(3):
                boms.append(BOMData(m.group(1), int(m.group(2)), m.group(3)))
            else:
                components.append(Cbox(m.start(), i, m.end(), i, m.group(1), int(m.group(2))))
    return components, boms

def findbig(grid: Grid):
    ...
