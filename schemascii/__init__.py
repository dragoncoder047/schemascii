import importlib
import os

import schemascii.components as _comp
import schemascii.drawing as _drawing

__version__ = "0.3.2"


def import_all_components():
    for f in os.scandir(os.path.dirname(_comp.__file__)):
        if f.is_file():
            importlib.import_module(
                f"{_comp.__package__}.{f.name.removesuffix('.py')}")


import_all_components()
del import_all_components


def render(filename: str, text: str | None = None, **options) -> str:
    """Render the Schemascii diagram to an SVG string."""
    return _drawing.Drawing.from_file(filename, text).to_xml_string(options)


if __name__ == "__main__":
    print(render(
        "test_data/test_resistors.txt",
        scale=20,
        padding=20,
        stroke_width=2,
        stroke="black"))
