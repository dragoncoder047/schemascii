import re
from grid import Grid
from utils import Cbox, BOMData

SMALL_COMPONENT_OR_BOM = re.compile(r'([A-Z]+)(\d+)(:[^\s]+)?')


def find_small(grid: Grid) -> tuple[list[Cbox], list[BOMData]]:
    components: list[Cbox] = []
    boms: list[BOMData] = []
    for i, line in enumerate(grid.lines):
        for m in SMALL_COMPONENT_OR_BOM.finditer(line):
            if m.group(3):
                boms.append(BOMData(m.group(1),
                                    int(m.group(2)), m.group(3)[1:]))
            else:
                components.append(Cbox(complex(m.start(), i), complex(m.end(),
                                                                      i),
                                       m.group(1), int(m.group(2))))
    return components, boms


TOP_OF_BOX = re.compile(r'\.~+\.')


def find_big(grid: Grid) -> tuple[list[Cbox], list[BOMData]]:
    boxes: list[Cbox] = []
    boms: list[BOMData] = []
    while True:
        for i, line in enumerate(grid.lines):
            if m1 := TOP_OF_BOX.search(line):
                tb = m1.group()
                x1 = m1.start()
                x2 = m1.end()
                y1 = i
                y2 = None
                for j, l in enumerate(grid.lines):
                    if j <= y1:
                        continue
                    cs = l[x1:x2]
                    if cs == tb:
                        y2 = j
                        break
                    if not cs[0] == cs[-1] == ':':
                        raise SyntaxError(
                            f'{grid.filename}: Fragmented box '
                            f'starting at line {y1 + 1}, col {x1 + 1}')
                else:
                    raise SyntaxError(
                        f'{grid.filename}: Unfinished box '
                        f'starting at line {y1 + 1}, col {x1 + 1}')
                inside = grid.clip(complex(x1, y1), complex(x2, y2))
                print("inside is", inside)
                results, resb = find_small(inside)
                if len(results) == 0 and len(resb) == 0:
                    raise ValueError(
                        f'{grid.filename}: Box starting at '
                        f'line {y1 + 1}, col {x1 + 1} is '
                        f'missing reference designator')
                if len(results) != 1 and len(resb) != 1:
                    raise ValueError(
                        f'{grid.filename}: Box starting at '
                        f'line {y1 + 1}, col {x1 + 1} has '
                        f'multiple reference designators')
                if not results:
                    merd = resb[0]
                else:
                    merd = results[0]
                boxes.append(
                    Cbox(complex(x1, y1),
                         complex(x2, y2),
                         merd.type,
                         merd.id))
                boms.extend(resb)
                # mark everything
                for i in range(x1, x2):
                    for j in range(y1, y2 + 1):
                        grid.setmask(complex(i, j))
                break
        else:
            break
    return boxes, boms


def find_all(grid: Grid) -> tuple[list[Cbox], list[BOMData]]:
    b1, l1 = find_big(grid)
    b2, l2 = find_small(grid)
    return b1+b2, l1+l2
