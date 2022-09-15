class Grid:
    def __init__(self, data: str):
        self.raw: str = data
        lines: list[str] = data.split('\n')
        maxlen: int = max(len(line) for line in lines)
        self.data: list[list[str]] = [list(line.ljust(maxlen, ' ')) for line in lines]
        self.flags: list[list[int]] = [[0 for x in range(maxlen)] for y in range(len(lines))]
        self.width = maxlen
        self.height = len(self.data)

    def get(self, x: int, y: int) -> str:
        if self.getflag(x, y) > 0:
            return ' '
        return self.data[y][x]

    @property
    def lines(self):
        return [''.join(self.get(x, y) for x in range(self.width)) for y in range(self.height)]

    def set(self, x: int, y: int, value: str):
        self.data[y][x] = value

    def getflag(self, x: int, y: int) -> int:
        return self.flags[y][x]

    def setflag(self, x: int, y: int, flag: int = 1):
        self.flags[y][x] = flag

    def clrflag(self, x: int, y: int):
        self.setflag(x, y, 0)

    def clrall(self):
        self.flags = [[0 for x in range(self.width)] for y in range(self.height)]

    def __repr__(self):
        return "Grid(\n'''\n" + '\n'.join(self.lines) + "'''\n)"
    __str__ = __repr__
