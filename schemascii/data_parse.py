from __future__ import annotations

import fnmatch
import re
import tomllib
from dataclasses import dataclass

from .errors import DiagramSyntaxError


@dataclass
class Section(dict):
    """Section of data relevant to one portion of the drawing."""

    header: str
    data: dict

    def __getitem__(self, key):
        return self.data[key]

    def matches(self, name) -> bool:
        """True if self.header matches the name."""
        return fnmatch.fnmatch(name, self.header)


@dataclass
class Data:
    """Class that holds the data of a drawing."""

    sections: list[Section]

    @classmethod
    def parse_from_string(cls, text: str, startline=1, filename="") -> Data:
        # add newlines so that the line number is
        # correct in TOML parse error messages
        corrected_text = ("\n" * (startline - 1)) + text
        try:
            data = tomllib.loads(corrected_text)
        except tomllib.TOMLDecodeError as e:
            if filename:
                e.add_note(
                    f"note: while parsing data section in file: {filename}")
            raise
        sections = []
        for key in data:
            sections.append(Section(key, data[key]))
        return cls(sections)


if __name__ == '__main__':
    text = r"""

[drawing]
color = "black"
width = 2
padding = 20
format = "symbol"

[R1]
value = 10
tolerance = 0.05
wattage = 0.25

[R2]
"""
    print(Data.parse_from_string(text))
