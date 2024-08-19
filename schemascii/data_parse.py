from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass

import schemascii.errors as _errors

TOKEN_PAT = re.compile("|".join([
    r"[\n{};=]",  # special one-character
    "%%",  # comment marker
    r"(?:\d*\.)?\d+(?:[Ee][+-]?\d+)?",  # number
    r"""\"(?:\\"|[^"])+\"|\s+""",  # string
    r"""(?:(?!["\s{};=]).)+""",  # anything else
]))
SPECIAL = {";", "\n", "%%", "{", "}"}


def tokenize(stuff: str) -> list[str]:
    return TOKEN_PAT.findall(stuff)


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
        tokens = tokenize(text)
        lines = (text + "\n").splitlines()
        col = line = index = 0
        lastsig = (0, 0, 0)

        def complain(msg):
            raise _errors.DiagramSyntaxError(
                f"{filename} line {line+startline}: {msg}\n"
                f"  {lines[line]}\n"
                f"  {' ' * col}{'^'*len(look())}".lstrip())

        def complain_eof():
            restore(lastsig)
            skip_space(True)
            if index >= len(tokens):
                complain("unexpected EOF")
            complain("cannot parse after this")

        def look():
            if index >= len(tokens):
                return "\0"
            return tokens[index]

        def eat():
            nonlocal line
            nonlocal col
            nonlocal index
            if index >= len(tokens):
                complain_eof()
            token = tokens[index]
            index += 1
            if token == "\n":
                line += 1
                col = 0
            else:
                col += len(token)
            # import inspect
            # calledfrom = inspect.currentframe().f_back.f_lineno
            # print("** ate token", repr(token),
            #       "called from line", calledfrom)
            return token

        def save():
            return (index, line, col)

        def restore(dat):
            nonlocal index
            nonlocal line
            nonlocal col
            index, line, col = dat

        def mark_used():
            nonlocal lastsig
            lastsig = save()

        def skip_space(newlines: bool = False):
            rv = False
            while look().isspace() and (newlines or look() != "\n"):
                eat()
                rv = True
            return rv

        def skip_comment():
            if look() == "%%":
                while look() != "\n":
                    eat()

        def skip_i(newlines: bool = True):
            while True:
                if newlines and look() == "\n":
                    eat()
                    skip_space()
                elif look() == "%%":
                    skip_comment()
                else:
                    if not skip_space():
                        return

        def expect(expected: set[str]):
            got = look()
            if got in expected:
                eat()
                mark_used()
                return
            complain(f"expected {' or '.join(map(repr, expected))}")

        def expect_not(disallowed: set[str]):
            got = look()
            if got not in disallowed:
                return
            complain(f"unexpected {got!r}")

        def parse_section() -> Section:
            expect_not(SPECIAL)
            name = eat()
            # print("** starting section", repr(name))
            mark_used()
            skip_i()
            expect({"{"})
            data = {}
            while look() != "}":
                data |= parse_kv_pair()
            eat()  # the "}"
            skip_i()
            return Section(name, data)

        def parse_kv_pair() -> dict:
            skip_i()
            if look() == "}":
                # handle case of ";}"
                # print("**** got a ';}'")
                return {}
            expect_not(SPECIAL)
            key = eat()
            mark_used()
            skip_i()
            expect({"="})
            skip_space()
            expect_not(SPECIAL)
            value = ""
            while True:
                value += eat()
                mark_used()
                here = save()
                skip_i(False)
                ahead = look()
                # print("* ahead", repr(ahead), repr(value))
                restore(here)
                if ahead in SPECIAL:
                    break
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
                value = bytes(value, "utf-8").decode("unicode-escape")
            else:
                # try to make a number if possible
                try:
                    temp = value
                    value = float(temp)
                    value = int(temp)
                except ValueError:
                    pass
            # don't eat the ending "}"
            if look() != "}":
                expect({"\n", ";"})
            # print("*** got KV", repr(key), repr(value))
            return {key: value}

        skip_i()
        sections = []
        while index < len(tokens):
            sections.append(parse_section())
        return cls(sections)

    def get_values_for(self, name: str) -> dict:
        out = {}
        for section in self.sections:
            if section.matches(name):
                out |= section.data
        return out

    def global_options(self) -> dict:
        return self.get_values_for("*")


if __name__ == '__main__':
    import pprint
    text = ""
    text = r"""
:all {
    %% these are global config options
    color = black
    width = 2; padding = 20;
    format = symbol
    mystring = "hello\nworld"
}


R* {tolerance = .05; wattage = 0.25}

R1 {
    resistance = 0 - 10k;
    %% trailing comment
}
"""
    my_data = Data.parse_from_string(text)
    pprint.pprint(my_data)
    pprint.pprint(my_data.get_values_for("R1"))
