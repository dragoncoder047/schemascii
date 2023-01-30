class Grid:
    """Helper class for manmaging a 2-D
    grid of ASCII art."""

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
        "Returns true if the point is within the bounds of this grid."
        return 0 <= p.real < self.width and 0 <= p.imag < self.height

    def get(self, p: complex) -> str:
        """Returns the current character at that point --
        space if out of bounds,
        the mask character if it was set,
        otherwise the original character."""
        if not self.validbounds(p):
            return ' '
        return self.getmask(p) or self.data[int(p.imag)][int(p.real)]

    @property
    def lines(self):
        "The current contents, with masks applied."
        return [''.join(self.get(complex(x, y)) for x in range(self.width))
                for y in range(self.height)]

    def getmask(self, p: complex) -> str | bool:
        """Sees the mask applied to the specified point;
        False if it was not set."""
        if not self.validbounds(p):
            return False
        return self.masks[int(p.imag)][int(p.real)]

    def setmask(self, p: complex, mask: str | bool = ' '):
        "Sets or clears the mask at the point."
        if not self.validbounds(p):
            return
        self.masks[int(p.imag)][int(p.real)] = mask

    def clrmask(self, p: complex):
        "Shortcut for `self.setmask(p, False)`"
        self.setmask(p, False)

    def clrall(self):
        "Clears all the masks at once."
        self.masks = [[False for x in range(self.width)]
                      for y in range(self.height)]

    def clip(self, p1: complex, p2: complex):
        """Returns a sub-grid with the contents bounded by the p1 and p2 box.
        Masks are not copied."""
        ls = slice(int(p1.real), int(p2.real))
        cs = slice(int(p1.imag), int(p2.imag) + 1)
        d = '\n'.join(''.join(ln[ls]) for ln in self.data[cs])
        return Grid(self.filename, d)

    def __repr__(self):
        return f"Grid({self.filename!r}, '''\n{chr(10).join(self.lines)}''')"
    __str__ = __repr__

    def spark(self, *points):
        "print the grid highliting the specified points"
        for y in range(self.height):
            for x in range(self.width):
                point = complex(x, y)
                char = self.get(point)
                if point in points:
                    print("\x1B[7m" + char + "\x1B[27m", end="")
                else:
                    print(char, end="")
            print()

if __name__ == '__main__':
    x = Grid('', '   \n   \n   ')
    x.spark(0, 1, 2, 1j, 2j, 1+2j, 2+2j, 2+1j)
