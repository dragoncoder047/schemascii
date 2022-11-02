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
    def render(self) -> str:
        # prev = self.points[0]
        # # copied from https://github.com/KenKundert/svg_schematic/blob/0abb5dc/svg_schematic.py#L284-L302
        # new_points = [prev]
        # for p in  self.points[1:]:
        #     if p != prev: # TODO: remove colinear
        #         candidates = []
        #         candidates.append([complex(prev.real, p.imag)])
        #         candidates.append([complex(p.real, prev.imag)])
        #         ymid = (p.imag + prev.imag)/2
        #         candidates.append([complex(prev.real, ymid), complex(p.real, ymid)])
        #         xmid = (p.real + prev.real)/2
        #         candidates.append([complex(xmid, prev.imag), complex(xmid, p.imag)])
        #         best = None
        #         bestscore = float('inf')
        #         for c in candidates:
        #             if (s := sharpness_score(new_points + c)) < bestscore:
        #                 bestscore = s
        #                 best = c
        #         new_points.extend(c)
        #     new_points.append(p)
        #     prev = p
        return (
            '<polyline class="wire" points="'
            + ' '.join(f'{p.real},{p.imag}' for p in self.points)
            + '"></polyline>'
        )

def colinear(points: list[complex]) -> bool:
    return len(set(phase(p-points[0]) for p in points[1:])) == 1

def sharpness_score(points: list[complex]) -> float:
    score = 0
    prevPoint = points.imag
    prevPhase = phase(points.imag - points[0])
    for p in points[2:]:
        ph = phase(p - prevPoint)
        score += abs(prevPhase - ph)
        prevPoint = p
        prevPhas = ph
    return score
