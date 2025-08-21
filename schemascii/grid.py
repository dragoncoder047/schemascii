class Grid:
    """Helper class for managing a 2-D
    grid of ASCII art.
    """

    def __init__(self, filename: str, data: str | None = None):
        if data is None:
            with open(filename, encoding="ascii") as f:
                data = f.read()
        self.filename: str = filename
        self.raw: str = data
        lines: list[str] = data.split("\n")
        maxlen: int = max(len(line) for line in lines)
        self.data: list[list[str]] = [list(line.ljust(maxlen, " "))
                                      for line in lines]
        self.masks: list[list[bool | str]] = [
            [False for _ in range(maxlen)] for _ in range(len(lines))
        ]
        self.width = maxlen
        self.height = len(self.data)

    def validbounds(self, p: complex) -> bool:
        """Returns true if the point is within the bounds of this grid."""
        return 0 <= p.real < self.width and 0 <= p.imag < self.height

    def get(self, p: complex) -> str:
        """Returns the current character at that point --
        space if out of bounds,
        the mask character if it was set,
        otherwise the original character.
        """
        if not self.validbounds(p):
            return " "
        return self.getmask(p) or self.data[int(p.imag)][int(p.real)]

    @property
    def lines(self) -> tuple[str]:
        """The current contents, with masks applied."""
        return tuple([
            "".join(self.get(complex(x, y)) for x in range(self.width))
            for y in range(self.height)
        ])

    def getmask(self, p: complex) -> str | bool:
        """Return the mask applied to the specified point
        (False if it was not set).
        """
        if not self.validbounds(p):
            return False
        return self.masks[int(p.imag)][int(p.real)]

    def setmask(self, p: complex, mask: str | bool = " "):
        "Sets or clears the mask at the point."
        if not self.validbounds(p):
            return
        self.masks[int(p.imag)][int(p.real)] = mask

    def clrmask(self, p: complex):
        """Shortcut for `self.setmask(p, False)`"""
        self.setmask(p, False)

    def clrall(self):
        """Clears all the masks at once."""
        self.masks = [[False for _ in range(self.width)]
                      for _ in range(self.height)]

    def clip(self, p1: complex, p2: complex):
        """Returns a sub-grid with the contents bounded by the p1 and p2 box.
        Masks are not copied.
        """
        ls = slice(int(p1.real), int(p2.real))
        cs = slice(int(p1.imag), int(p2.imag) + 1)
        d = "\n".join("".join(ln[ls]) for ln in self.data[cs])
        return Grid(self.filename, d)

    def shrink(self):
        """Shrinks self so that there is not any space between the edges and
        the next non-whitespace character. Takes masks into account.
        """
        # clip the top lines
        while all(self.get(complex(x, 0)).isspace()
                  for x in range(self.width)):
            self.height -= 1
            self.data.pop(0)
            self.masks.pop(0)
        # clip the bottom lines
        while all(self.get(complex(x, self.height - 1)).isspace()
                  for x in range(self.width)):
            self.height -= 1
            self.data.pop()
            self.masks.pop()
        # find the max indent space on left
        min_indent = self.width
        for line in self.lines:
            this_indent = len(line) - len(line.lstrip())
            min_indent = min(min_indent, this_indent)
        # chop the space
        # TODO: for left and right, need to take into account the mask array
        if min_indent > 0:
            self.width -= min_indent
            for line in self.data:
                del line[0:min_indent]
            for line in self.masks:
                del line[0:min_indent]
        # find the max indent space on right
        min_indent = self.width
        for line in self.lines:
            this_indent = len(line) - len(line.rstrip())
            min_indent = min(min_indent, this_indent)
        # chop the space
        if min_indent > 0:
            self.width -= min_indent
            for line in self.data:
                del line[len(line)-min_indent:]
            for line in self.masks:
                del line[len(line)-min_indent:]

    def __repr__(self):
        return (f"Grid({self.filename!r}, \"\"\""
                f"\n{chr(10).join(self.lines)}\"\"\")")

    __str__ = __repr__

    def spark(self, *points):
        """Print the grid highliting the specified points.
        (Used for debugging.)

        This won't work in IDLE since it relies on
        ANSI terminal escape sequences.
        """
        for y in range(self.height):
            for x in range(self.width):
                point = complex(x, y)
                char = self.get(point)
                if point in points:
                    print("\x1B[7m" + char + "\x1B[27m", end="")
                else:
                    print(char, end="")
            print()


if __name__ == "__main__":
    x = Grid("", """

     xx---
       hha--
    a     awq

""")
    x.spark(0, complex(x.width - 1, 0), complex(0, x.height - 1),
            complex(x.width - 1, x.height - 1))
    x.shrink()
    print()
    x.spark(0, complex(x.width - 1, 0), complex(0, x.height - 1),
            complex(x.width - 1, x.height - 1))
