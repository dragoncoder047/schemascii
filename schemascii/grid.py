class Grid:
    def __init__(self, filename: str, data: str):
        self.filename: str = filename
        self.raw: str = data
        lines: list[str] = data.split('\n')
        maxlen: int = max(len(line) for line in lines)
        self.data: list[list[str]] = [
            list(line.ljust(maxlen, ' ')) for line in lines]
        self.masks: list[list[bool | str]] = [
            [False for x in range(maxlen)] for y in range(len(lines))]
        self.width = maxlen
        self.height = len(self.data)

    def validbounds(self, p: complex) -> bool:
        return 0 <= p.real < self.width and 0 <= p.imag < self.height

    def get(self, p: complex) -> str:
        if not self.validbounds(p):
            return ' '
        return self.getmask(p) or self.data[int(p.imag)][int(p.real)]

    @property
    def lines(self):
        return [''.join(self.get(complex(x, y)) for x in range(self.width))
                for y in range(self.height)]

    def getmask(self, p: complex) -> str:
        if not self.validbounds(p):
            return False
        return self.masks[int(p.imag)][int(p.real)]

    def setmask(self, p: complex, mask: str | bool = ' '):
        if not self.validbounds(p):
            return
        self.masks[int(p.imag)][int(p.real)] = mask

    def clrmask(self, p: complex):
        self.setmask(p, False)

    def clrall(self):
        self.masks = [[False for x in range(self.width)]
                      for y in range(self.height)]

    def __repr__(self):
        return f"Grid({self.filename!r}, '''\n{chr(10).join(self.lines)}''')"
    __str__ = __repr__
