import re
from .grid import Grid
from .utils import Cbox, BOMData
from .errors import DiagramSyntaxError, BOMError


SMALL_COMPONENT_OR_BOM = re.compile(r"#*([A-Z]+)(\d*|\.\w+)(:[^\s]+)?#*")


def find_small(grid: Grid) -> tuple[list[Cbox], list[BOMData]]:
    """Searches for small components' RDs and BOM-data sections, and
    blanks them out."""
    components: list[Cbox] = []
    boms: list[BOMData] = []
    for i, line in enumerate(grid.lines):
        for m in SMALL_COMPONENT_OR_BOM.finditer(line):
            ident = m.group(2) or "0"
            if m.group(3):
                boms.append(BOMData(m.group(1), ident, m.group(3)[1:]))
            else:
                components.append(
                    Cbox(
                        complex(m.start(), i),
                        complex(m.end() - 1, i),
                        m.group(1),
                        ident,
                    )
                )
            for z in range(*m.span(0)):
                grid.setmask(complex(z, i))
    return components, boms


TOP_OF_BOX = re.compile(r"\.~+\.")


def find_big(grid: Grid) -> tuple[list[Cbox], list[BOMData]]:
    """Searches for all the large (i.e. box-style components)
    and returns them, and masks them on the grid."""
    boxes: list[Cbox] = []
    boms: list[BOMData] = []
    while True:
        for i, line in enumerate(grid.lines):
            if m1 := TOP_OF_BOX.search(line):
                tb = m1.group()
                x1, x2 = m1.span()
                y1 = i
                y2 = None
                for j, l in enumerate(grid.lines):
                    if j <= y1:
                        continue
                    cs = l[x1:x2]
                    if cs == tb:
                        y2 = j
                        break
                    if not cs[0] == cs[-1] == ":":
                        raise DiagramSyntaxError(
                            f"{grid.filename}: Fragmented box "
                            f"starting at line {y1 + 1}, col {x1 + 1}"
                        )
                else:
                    raise DiagramSyntaxError(
                        f"{grid.filename}: Unfinished box "
                        f"starting at line {y1 + 1}, col {x1 + 1}"
                    )
                inside = grid.clip(complex(x1, y1), complex(x2, y2))
                results, resb = find_small(inside)
                if len(results) == 0 and len(resb) == 0:
                    raise BOMError(
                        f"{grid.filename}: Box starting at "
                        f"line {y1 + 1}, col {x1 + 1} is "
                        f"missing reference designator"
                    )
                if len(results) != 1 and len(resb) != 1:
                    raise BOMError(
                        f"{grid.filename}: Box starting at "
                        f"line {y1 + 1}, col {x1 + 1} has "
                        f"multiple reference designators"
                    )
                if not results:
                    merd = resb[0]
                else:
                    merd = results[0]
                boxes.append(
                    Cbox(complex(x1, y1), complex(x2 - 1, y2), merd.type, merd.id)
                )
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
    """Finds all the marked components and reference designators,
    and masks off all of them, leaving only wires and extraneous text."""
    b1, l1 = find_big(grid)
    b2, l2 = find_small(grid)
    return b1 + b2, l1 + l2


if __name__ == "__main__":
    test_grid = Grid("test_data/test_resistors.txt")
    bbb, _ = find_all(test_grid)
    all_pts = []
    for box in bbb:
        all_pts.extend([box.p1, box.p2])
    test_grid.spark(*all_pts)
