import argparse
import sys
import warnings

import schemascii
import schemascii.data as _d
import schemascii.errors as _errors


class DataFudgeAction(argparse.Action):
    # from https://stackoverflow.com/a/78890058/23626926
    def __call__(self, parser, namespace, values: str, option_string=None):
        scope, sep, pair = values.partition(".")
        if not sep:
            parser.error("invalid -D format: missing .")
        key, sep, val = pair.partition("=")
        if not sep:
            parser.error("invalid -D format: missing =")
        items = getattr(namespace, self.dest) or _d.Data([])
        items |= _d.Data(
            [_d.Section(scope, {key: _d.parse_simple_value(val)})])
        setattr(namespace, self.dest, items)


def cli_main():
    ap = argparse.ArgumentParser(
        prog="schemascii", description="Render ASCII-art schematics into SVG.")
    ap.add_argument(
        "-V", "--version", action="version",
        version="%(prog)s " + schemascii.__version__)
    ap.add_argument("in_file", help="File to process. (default: stdin)",
                    default="-")
    ap.add_argument(
        "-o",
        "--out",
        default=None,
        dest="out_file",
        help="Output SVG file. (default input file plus .svg, or stdout "
        "if input is stdin)")
    ap.add_argument(
        "-s",
        "--strict",
        action="store_true",
        dest="warnings_are_errors",
        help="Treat warnings as errors. (default: lax mode)")
    ap.add_argument("-D",
                    dest="fudge",
                    metavar="SCOPE.KEY=VALUE",
                    action=DataFudgeAction,
                    help="Add a definition for diagram data. Data passed "
                    "on the command line will override any value specified "
                    "on the drawing itself. For example, -DR.wattage=0.25 to "
                    "make all resistors 1/4 watt. The wildcard in scope is @ "
                    "so as to not conflict with your shell.\n\nThis option "
                    "can be repeated as many times as necessary.")
    args = ap.parse_args()
    if args.out_file is None:
        args.out_file = args.in_file + ".svg"
    text = None
    if args.in_file == "-":
        text = sys.stdin.read()
        args.in_file = "<stdin>"
    try:
        with warnings.catch_warnings(record=True) as captured_warnings:
            result_svg = schemascii.render(args.in_file, text, args.fudge)
    except _errors.Error as err:
        print(type(err).__name__ + ":", err, file=sys.stderr)
        sys.exit(1)
    if captured_warnings:
        for warning in captured_warnings:
            print("Warning:", warning.message, file=sys.stderr)
        if args.warnings_are_errors:
            print("Error: warnings were treated as errors", file=sys.stderr)
            sys.exit(1)
    if args.out_file == "-":
        print(result_svg)
    else:
        with open(args.out_file, "w", encoding="utf-8") as out:
            out.write(result_svg)
        if args.verbose:
            print("Wrote SVG to", args.out_file)


if __name__ == "__main__":
    cli_main()
