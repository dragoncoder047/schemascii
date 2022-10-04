from collections import namedtuple
from enum import IntEnum

Cbox = namedtuple('Cbox', 'x1 y1 x2 y2 type id')
BOMData = namedtuple('BOMData', 'type id data')
Flag = namedtuple('Flag', 'char box side')

class Side(IntEnum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3
