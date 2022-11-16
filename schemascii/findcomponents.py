from .grid import Grid
import re
from .utils import Cbox, BOMData

smallcompbom = re.compile(r'([A-Z]+)(\d+)(:[^\s]+)?')


def findsmall(grid: Grid) -> tuple[list[Cbox], list[BOMData]]:
    components: list[Cbox] = []
    boms: list[BOMData] = []
    for i, line in enumerate(grid.lines):
        for m in smallcompbom.finditer(line):
            if m.group(3):
                boms.append(BOMData(m.group(1),
                    int(m.group(2)), m.group(3)[1:]))
            else:
                components.append(Cbox(complex(m.start(), i), complex(m.end(), i),
                                       m.group(1), int(m.group(2))))
    return components, boms


boxtop = re.compile('\.~+\.')


def findbig(grid: Grid) -> tuple[list[Cbox], list[BOMData]]:
    boxes: list[Cbox] = []
    boms: list[BOMData] = []
    while True:
        for i, line in enumerate(grid.lines):
            if m1 := boxtop.search(line):
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
                    if not cs[0] == cs[-1] == ':':
                        raise SyntaxError(
                            '%s: Fragmented box starting at line %d, col %d' % (grid.filename, y1 + 1, x1 + 1))
                    inners.append(cs[1:-1])
                else:
                    raise SyntaxError(
                        '%s: Unfinished box starting at line %d, col %d' % (grid.filename, y1 + 1, x1 + 1))
                inside = Grid(grid.filename, '\n'.join(inners))
                results, resb = findsmall(inside)
                if len(results) == 0 and len(resb) == 0:
                    raise ValueError(
                        '%s: Box starting at line %d, col %d is missing reference designator' % (grid.filename, y1 + 1, x1 + 1))
                elif len(results) != 1 and len(resb) != 1:
                    raise ValueError(
                        '%s: Box starting at line %d, col %d has multiple reference designators' % (grid.filename, y1 + 1, x1 + 1))
                if not results:
                    merd = resb[0]
                else:
                    merd = results[0]
                boxes.append(Cbox(complex(x1, y1), complex(x2, y2), merd.type, merd.id))
                boms.extend(resb)
                # mark everything
                for i in range(x1, x2):
                    for j in range(y1, y2 + 1):
                        grid.setmask(complex(i, j))
                break
        else:
            break
    return boxes, boms


def findall(grid: Grid) -> tuple[list[Cbox], list[BOMData]]:
    grid.clrall()
    b1, l1 = findbig(grid)
    b2, l2 = findsmall(grid)
    return b1+b2, l1+l2
