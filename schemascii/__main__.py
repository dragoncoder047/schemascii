import argparse
import sys
import warnings
from . import render, __version__
from .errors import Error
from .configs import add_config_arguments


def cli_main():
    ap = argparse.ArgumentParser(
        prog="schemascii", description="Render ASCII-art schematics into SVG."
    )
    ap.add_argument(
        "-V", "--version", action="version", version="%(prog)s " + __version__
    )
    ap.add_argument("in_file", help="File to process.")
    ap.add_argument(
        "-o",
        "--out",
        default=None,
        dest="out_file",
        help="Output SVG file. (default input file plus .svg)",
    )
    add_config_arguments(ap)
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


if __name__ == "__main__":
    cli_main()
