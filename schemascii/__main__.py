import argparse
import sys
import warnings
from . import render, __version__
from .errors import Error


def cli_main():
    ap = argparse.ArgumentParser(
        prog="schemascii",
        description="Render ASCII-art schematics into SVG.")
    ap.add_argument("-V", "--version",
                    action="version",
                    version="%(prog)s " + __version__)
    ap.add_argument("in_file",
                    help="File to process.")
    ap.add_argument("-o", "--out",
                    default=None,
                    dest="out_file",
                    help="Output SVG file. (default input file plus .svg)")
    ap.add_argument("--padding",
                    help="Amount of padding to add on the edges.",
                    type=int,
                    default=10)
    ap.add_argument("--scale",
                    help="Scale at which to enlarge the entire diagram by.",
                    type=int,
                    default=15)
    ap.add_argument("--stroke_width",
                    help="Width of the lines",
                    type=int,
                    default=2)
    ap.add_argument("--stroke",
                    help="Color of the lines.",
                    default="black")
    ap.add_argument("--label",
                    help="Component label style "
                    "(L=include label, V=include value, VL=both)",
                    choices=["L", "V", "VL"],
                    default="VL")
    ap.add_argument("--nolabels",
                    help="Turns off labels on all components, "
                    "except for part numbers on ICs.",
                    action="store_true")
    args = ap.parse_args()
    if args.out_file is None:
        args.out_file = args.in_file + ".svg"
    text = None
    if args.in_file == "-":
        text = sys.stdin.read()
        args.in_file = "<stdin>"
    try:
        with warnings.catch_warnings(record=True) as captured_warnings:
            result_svg = render(args.in_file, text, **vars(args))
    except Error as err:
        print(type(err).__name__ + ":", err, file=sys.stderr)
        sys.exit(1)
    if captured_warnings:
        for warn in captured_warnings:
            print("warning:", warn.message, file=sys.stderr)
    if args.out_file == "-":
        print(result_svg)
    else:
        with open(args.out_file, "w", encoding="utf-8") as out:
            out.write(result_svg)


if __name__ == '__main__':
    cli_main()