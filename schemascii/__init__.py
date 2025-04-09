import importlib
import os
from typing import Any

import schemascii.components as _c
import schemascii.data as _d
import schemascii.drawing as _drawing

__version__ = "0.3.2"


def import_all_components():
    for root, _, files in os.walk(os.path.dirname(_c.__file__)):
        for f in files:
            if f.endswith(".py"):
                importlib.import_module("." + f.removesuffix(".py"),
                                        _c.__package__)


import_all_components()
del import_all_components


def render(filename: str, text: str | None = None,
           options: dict[str, Any] | _d.Data = {}) -> str:
    """Render the Schemascii diagram to an SVG string."""
    return _drawing.Drawing.from_file(filename, text).to_xml_string(options)


if __name__ == "__main__":
    import schemascii.component as _comp
    print(_comp.Component.all_components)
