import importlib
import os
import re
from typing import Any

import schemascii.components as _cs
import schemascii.data as _d
import schemascii.drawing as _drawing

__version__ = "0.3.2"


def import_all_components():
    for root, _, files in os.walk(os.path.dirname(_cs.__file__)):
        for f in files:
            # ignore dunder __init__ file
            # if we try to import that it gets run twice
            # which tries to double-register stuff and causes problems
            if re.match(r"(?!__)\w+(?<!__)\.py", f):
                importlib.import_module("." + f.removesuffix(".py"),
                                        _cs.__package__)


import_all_components()
del import_all_components


def render(filename: str, text: str | None = None,
           options: dict[str, Any] | _d.Data = {}) -> str:
    """Render the Schemascii diagram to an SVG string."""
    return _drawing.Drawing.from_file(filename, text).to_xml_string(options)


if __name__ == "__main__":
    import schemascii.data as _da
    import schemascii.data_consumer as _d
    import schemascii.refdes as _rd
    import schemascii.utils as _u
    print(_d.DataConsumer.registry["BAT"](
        _rd.RefDes("BAT", 0, "", 0, 0), [], [
            _u.Terminal(0, None, None),
            _u.Terminal(0, None, None)
        ]).to_xml_string(_da.Data([_da.Section(
            "BAT", {"foo": "bar", "value": 10})])))
