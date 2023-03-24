#! /usr/bin/env python3
import re
import os
from itertools import groupby
from schemascii.components_render import RENDERERS

# pylint: disable=unspecified-encoding,missing-function-docstring,invalid-name
# pylint: disable=not-an-iterable
# cSpell:ignore siht etareneg redner iicsa stpircs nettirwrevo ylpmis segnahc
# cSpell:ignore mehcs daetsn detareneg yllacitamotua codc stnenopmoc lliw ruo
# cSpell:ignore sgnirtscod

TOP = ("# Supported Schemascii Components\n\n<!--\n"
       + "".join(reversed("/stpircs nur dna\nyp.redner_stnenopmoc/iicsa"
                          "mehcs ni sgnirtscod eht tide ,daetsnI\n"
                          ".nettirwrevo eb ylpmis "
                          "lliw segnahc ruoY\n!TIDE TON OD\n!ELIF"
                          " DETARENEG YLLACITAMOTUA"))
       + os.path.basename(__file__)
       + "".join(reversed(".elif siht etareneg-er ot "))
       + "\n-->\n\n| Reference Designators | Description | "
       + "BOM Syntax | Supported Flags |"
       + "\n|:--:|:--|:--:|:--|\n")


def group_components_by_func():
    items = groupby(list(RENDERERS.items()), lambda x: x[1])
    out = {}
    for x, g in items:
        out[x] = [p[0] for p in g]
    return out


def parse_docstring(d):
    out = [None, None, None]
    if fs := re.search(r"flags:(.*?)$", d, re.M):
        out[2] = [f.split("=") for f in fs.group(1).split(",")]
        d = d.replace(fs.group(), "")
    if b := re.search(r"bom:(.*?)$", d, re.M):
        out[1] = b.group(1)
        d = d.replace(b.group(), "")
    out[0] = d.strip()
    return out


def main():
    content = TOP
    for func, rds in group_components_by_func().items():
        data = parse_docstring(func.__doc__)
        content += "| " + ", ".join(f"`{x}`" for x in rds) + " | "
        content += data[0].replace("\n", "<br>") + " | "
        content += "`" + data[1] + "` | "
        content += "<br>".join(f"`{x[0]}` = {x[1]}" for x in (data[2] or []))
        content += " |\n"
    with open("supported-components.md", "w") as f:
        f.write(content)


if __name__ == '__main__':
    main()
