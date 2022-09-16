from grid import Grid
import re
from collections import namedtuple

Cbox = namedtuple('Cbox', 'x1 y1 x2 y2 type id')
BOMData = namedtuple('BOMData', 'type id data')
smallcompbom = re.compile(r'([A-Z]+)(\d+)(:[^\s]+)?')


def findsmall(grid: Grid) -> tuple[list[Cbox], list[BOMData]]:
    components: list[Cbox] = []
    boms: list[BOMData] = []
    for i, line in enumerate(grid.lines):
        for m in smallcompbom.finditer(line):
            if m.group(3):
                boms.append(BOMData(m.group(1), int(
                    m.group(2)), m.group(3)[1:]))
            else:
                components.append(Cbox(m.start(), i, m.end(),
                                  i, m.group(1), int(m.group(2))))
    return components, boms


boxtop = re.compile('\.~+\.')


def findbig(grid: Grid) -> tuple[list[Cbox], list[BOMData]]:
    boxes: list[Cbox] = []
    boms: list[BOMData] = []
    while True:
        for i in range(len(grid.lines)):
            line = grid.lines[i]
            if m1 := boxtop.search(line):
                good = True
                tb = m1.group()
                x1 = m1.start()
                x2 = m1.end()
                y1 = i
                y2 = None
                inners = []
                for j, l in enumerate(grid.lines):
                    if j <= y1:
                        continue
                    cs = l[x1:x2]
                    if cs == tb:
                        y2 = j
                        break
                    if not (cs[0] == cs[-1] == ':'):
                        good = False
                        break
                    inners.append(cs[1:-1])
                else:
                    raise SyntaxError(
                        'Unfinished box starting at line %d, col %d' % (y1 + 1, x1 + 1))
                if good:
                    inside = Grid('\n'.join(inners))
                    results, resb = findsmall(inside)
                    if len(results) == 0 and len(resb) == 0:
                        raise ValueError(
                            'Box starting at line %d, col %d is missing reference designator' % (y1 + 1, x1 + 1))
                    elif len(results) != 1 and len(resb) != 1:
                        raise ValueError(
                            'Box starting at line %d, col %d has multiple reference designators' % (y1 + 1, x1 + 1))
                    if not results:
                        merd = resb[0]
                    else:
                        merd = results[0]
                    boxes.append(Cbox(x1, y1, x2, y2, merd.type, merd.id))
                    boms.extend(resb)
                    # mark everything
                    for i in range(x1, x2):
                        for j in range(y1, y2 + 1):
                            grid.setflag(i, j)
                    break
                else:
                    raise SyntaxError(
                        'Fragmented box starting at line %d, col %d' % (y1 + 1, x1 + 1))
        else:
            break
    return boxes, boms

def findall(grid: Grid) -> tuple[list[Cbox], list[BOMData]]:
    grid.clrall()
    b1, l1 = findbig(grid)
    b2, l2 = findsmall(grid)
    return b1+b2, l1+l2


if __name__ == '__main__':
    with open('../examples/test1.txt') as f:
        data = f.read()
    print(findbig(Grid(data)))
