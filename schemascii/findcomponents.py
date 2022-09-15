from .grid import Grid
import re
from collections import namedtuple

Cbox = namedtuple('Cbox', 'x1 y1 x2 y2 type id')
BOMData = namedtuple('BOMData', 'type id data')
smallcompbom = re.compile(r'([A-Z]+)(\d+)(:[^\s]+)?')

def findsmall(grid: Grid) -> tuple[list[Cbox], list[BOMData]]:
    components = []
    boms = []
    for i, line in enumerate(grid.lines):
        for m in smallcompbom.finditer(line):
            if m.group(3):
                boms.append(BOMData(m.group(1), int(m.group(2)), m.group(3)[1:]))
            else:
                components.append(Cbox(m.start(), i, m.end(), i, m.group(1), int(m.group(2))))
    return components, boms

boxtop = re.compile('\.~+\.')

def findbig(grid: Grid):
    boxes = []
    while True:
        for i, line in enumerate(grid.lines):
            if m1 := boxtop.search(line):
                good = True
                tb = m.group()
                x1 = m.start()
                x2 = m.end()
                y1 = i
                inners = []
                for j, l in enumerate(grid.lines):
                    if j <= y1: continue
                    cs = l[x1:x2]
                    if cs == tb:
                        break
                    if not (cs[0] == cs[-1] == ':'):
                        good = False
                        break
                    inners.append(cs[1:-1])
                else:
                    raise SyntaxError(
                        'Incomplete box starting at line %d, col %d' % (x1 + 1, y1 + 1))
                if good:
                    inside = Grid(inners.join('\n'))
                    results, _ = findsmall(inside)
                    raise Exception('Todo: finish')
        else:
            break
    return boxes

