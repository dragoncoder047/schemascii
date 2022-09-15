class Grid:
    def __init__(self, data: str):
        self.raw: str = data
        lines: list[str] = data.split('\n')
        maxlen: int = max(len(line) for line in lines)
        self.lines: list[list[str]] = [list(line.ljust(maxlen, ' ')) for line in lines]
        self.flags: list[list[int]] = [[0 for x in range(maxlen)] for y in range(len(lines))]

    def get(self, x: int, y: int) -> str:
        if self.getflag(x, y) > 0:
            return ' '
        return self.lines[y][x]
    
    def set(self, x: int, y: int, value: str):
        self.lines[y][x] = value

    def getflag(self, x: int, y: int) -> int:
        return self.flags[y][x]
    
    def setflag(self, x: int, y: int, flag: int = 1):
        self.flags[y][x] = flag
    
    def clrflag(self, x: int, y: int):
        self.setflag(x, y, 0)
    
    def __repr__(self):
        return "Grid(\n'''\n" + '\n'.join(''.join(l) for l in self.lines) + "'''\n)"
    __str__ = __repr__
