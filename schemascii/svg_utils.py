import typing


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


class XMLClass:
    def __getattr__(self, tag: str) -> typing.Callable[..., str]:
        def mk_tag(*contents: str, **attrs: str | bool | float | int) -> str:
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

        return mk_tag


XML = XMLClass()
del XMLClass


def group(*items: str, class_: str | False = False) -> str:
    return XML.g(*items, class_=class_)


def path(data: str,
         fill: str | False = False,
         stroke_width: float | False = False,
         stroke: str | False = False,
         class_: str | False = False) -> str:
    return XML.path(d=data, fill=fill, stroke__width=stroke_width,
                    stroke=stroke, class_=class_)


def circle(center: complex, radius: float, stroke: str | False = False,
           fill: str | False = False, class_: str | False = False) -> str:
    return XML.circle(cx=center.real, cy=center.imag, r=radius,
                      stroke=stroke, fill=fill, class_=class_)
