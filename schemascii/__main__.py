import argparse
import sys
from . import render, __version__


def cli_main():
    ap = argparse.ArgumentParser(
        prog="schemascii",
        description="Render ASCII-art schematics into SVG.")
    ap.add_argument("in_file",
                    help="File to process.")
    ap.add_argument("-o", "--out",
                    default=None,
                    dest="out_file",
                    help="Output SVG file. (default input file plus .svg)")
    args = ap.parse_args()
    if args.out_file is None:
        args.out_file = args.in_file + ".svg"
    try:
        result_svg = render(args.in_file)
    except Exception as e:
        print("error:", e, file=sys.stderr)
        sys.exit(1)
    with open(args.out_file, "w", encoding="utf-8") as out:
        out.write(result_svg)


if __name__ == '__main__':
    cli_main()
