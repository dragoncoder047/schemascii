class Grid:
    def __init__(self, filename: str, data: str):
        self.filename: str = filename
        self.raw: str = data
        lines: list[str] = data.split('\n')
        maxlen: int = max(len(line) for line in lines)
        self.data: list[list[str]] = [list(line.ljust(maxlen, ' ')) for line in lines]
        self.masks: list[list[bool | str]] = [[False for x in range(maxlen)] for y in range(len(lines))]
        self.width = maxlen
        self.height = len(self.data)

    def get(self, x: int, y: int) -> str:
        if self.getmask(x, y):
            return self.getmask(x, y)
        return self.data[y][x]

    @property
    def lines(self):
        return [''.join(self.get(x, y) for x in range(self.width)) for y in range(self.height)]

    def getmask(self, x: int, y: int) -> str:
        return self.masks[y][x]

    def setmask(self, x: int, y: int, mask: str | bool = ' '):
        self.masks[y][x] = mask

    def clrmask(self, x: int, y: int):
        self.setmask(x, y, False)

    def clrall(self):
        self.masks = [[False for x in range(self.width)] for y in range(self.height)]

    def __repr__(self):
        return "Grid(\n'''\n" + '\n'.join(self.lines) + "'''\n)"
    __str__ = __repr__
