from collections import namedtuple
from enum import IntEnum
from cmath import phase

Cbox = namedtuple('Cbox', 'p1 p2 type id')
BOMData = namedtuple('BOMData', 'type id data')
Flag = namedtuple('Flag', 'char box side')

class Side(IntEnum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3

class Wire:
    def __init__(self, points: list[complex]):
        self.points = points
    def topath(self) -> str:
        out = ''

def colinear(points: list[complex]) -> bool:
    return len(set(phase(p-points[0]) for p in points[1:])) == 1

def sharpness_score(points: list[complex]) -> float:
    score = 0
    prevPoint = points[1]
    prevPhase = phase(points[1] - points[0])
    for p in points[2:]:
        ph = phase(p - prevPoint)
        score += abs(prevPhase - ph)
        prevPoint = p
        prevPhas = ph
    return score
