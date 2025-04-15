from __future__ import annotations

import typing

type OrFalse[T] = T | typing.Literal[False]


def fix_number(n: float) -> str:
    """If n is an integer, remove the trailing ".0".
    Otherwise round it to 2 digits, and return the stringified
    number.
    """
    if n.is_integer():
        return str(int(n))
    n = round(n, 2)
    if n.is_integer():
        return str(int(n))
    return str(n)


def xmltag(tag: str, *contents: str, **attrs: str | bool | float | int) -> str:
    out = f"<{tag}"
    for k, v in attrs.items():
        if v is False:
            continue
        if isinstance(v, float):
            v = fix_number(v)
        # XXX: this gets called on every XML level
        # XXX: which means that it will be called multiple times
        # XXX: unnecessarily
        # elif isinstance(v, str):
        #     v = re.sub(r"\b\d+(\.\d+)\b",
        #                lambda m: fix_number(float(m.group())), v)
        out += f' {k.removesuffix("_").replace("__", "-")}="{v}"'
    out = out + ">" + "".join(contents)
    return out + f"</{tag}>"


def group(*items: str, class_: OrFalse[str] = False) -> str:
    return xmltag("g", *items, class_=class_)


def path(data: str, fill: OrFalse[str] = False,
         linewidth: OrFalse[float] = False, stroke: OrFalse[str] = False,
         class_: OrFalse[str] = False) -> str:
    return xmltag("path", d=data, fill=fill, stroke__width=linewidth,
                  stroke=stroke, class_=class_)


def circle(center: complex, radius: float, stroke: OrFalse[str] = False,
           fill: OrFalse[str] = False, class_: OrFalse[str] = False) -> str:
    return xmltag("circle", cx=center.real, cy=center.imag, r=radius,
                  stroke=stroke, fill=fill, class_=class_)


def whole_thing(contents: str, width: float, height: float, viewBox: str,
                xmlns="http://www.w3.org/2000/svg",
                class_="schemascii") -> str:
    return xmltag("svg", contents, width=width, height=height,
                  viewBox=viewBox, xmlns=xmlns, class_=class_)
