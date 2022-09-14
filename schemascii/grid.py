class Grid:
    def __init__(self, data: str):
        self.raw = data
        lines = data.split('\n')
        maxlen = max(len(line) for line in lines)
        self.lines = [list(line.ljust(maxlen, ' ')) for line in lines]
        self.marked = [[False for x in range(maxlen)] for y in range(len(lines))]

    def get(self, x: int, y: int) -> str:
        if self.ismarked(x, y):
            return ' '
        return self.lines[y][x]
    
    def set(self, x: int, y: int, value: str):
        self.lines[y][x] = value

    def ismarked(self, x: int, y: int) -> bool:
        return self.marked[y][x]
    
    def mark(self, x: int, y: int):
        self.marked[y][x] = True
    
    def unmark(self, x: int, y: int):
        self.marked[y][x] = False
    
    def __getitem__(self, coords: tuple[int]) -> str:
        if isinstance(coords, tuple) and len(coords) == 2:
            return self.get(coords[0], coords[1])
        else:
            raise ValueError('Bad coordinates value: %s' % coords)
    
    def __setitem__(self, coords: tuple[int], value: bool | str):
        if isinstance(coords, tuple) and len(coords) == 2:
            if isinstance(value, bool):
                if value:
                    self.mark(coords[0], coords[1])
                else:
                    self.unmark(coords[0], coords[1])
            elif isinstance(value, str) and len(value) == 1:
                self.set(coords[0], coords[1], value)
            else:
                raise ValueError('Bad item value: %s' % value)
        else:
            raise ValueError('Bad coordinates value: %s' % coords)
        return self
    
    def __repr__(self):
        return '\n'.join(''.join(l) for l in self.lines)
    __str__ = __repr__
