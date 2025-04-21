import argparse
import os
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
            parser.error("invalid -D argument: missing .")
        key, sep, val = pair.partition("=")
        if not sep:
            parser.error("invalid -D argument: missing =")
        items = getattr(namespace, self.dest) or _d.Data([])
        items |= _d.Data(
            [_d.Section(scope, {key: _d.parse_simple_value(val)})])
        setattr(namespace, self.dest, items)


def cli_main():
    ap = argparse.ArgumentParser(
        prog="schemascii",
        description="Render ASCII-art schematics into SVG.")
    ap.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s " + schemascii.__version__)
    ap.add_argument(
        "-i",
        "--in",
        type=argparse.FileType("r"),
        default=None,
        dest="in_file",
        help="File to process. (default: stdin)")
    ap.add_argument(
        "-o",
        "--out",
        type=argparse.FileType("w"),
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
    try:
        if args.in_file is None:
            args.in_file = sys.stdin
            if args.out_file is None:
                args.out_file = sys.stdout
        elif args.out_file is None:
            args.out_file = open(args.in_file.name + ".svg", "w")
        try:
            with warnings.catch_warnings(record=True) as captured_warnings:
                result_svg = schemascii.render(args.in_file.name,
                                               args.in_file.read(), args.fudge)
        except _errors.Error as err:
            if args.out_file is not sys.stdout:
                os.unlink(args.out_file.name)
            ap.error(err.nice_message())

        if captured_warnings:
            for warning in captured_warnings:
                print("Warning:", warning.message, file=sys.stderr)
            if args.warnings_are_errors:
                print("Error: warnings were treated as errors",
                      file=sys.stderr)
                sys.exit(1)

        args.out_file.write(result_svg)
    finally:
        args.in_file.close()
        args.out_file.close()


if __name__ == "__main__":
    cli_main()
