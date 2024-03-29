import argparse
from dataclasses import dataclass
from .errors import ArgumentError


@dataclass
class ConfigConfig:
    name: str
    clazz: type | list
    default: object
    description: str


OPTIONS = [
    ConfigConfig("padding", float, 10, "Amount of padding to add on the edges."),
    ConfigConfig(
        "scale", float, 15, "Scale at which to enlarge the entire diagram by."
    ),
    ConfigConfig("stroke_width", float, 2, "Width of the lines"),
    ConfigConfig("stroke", str, "black", "Color of the lines."),
    ConfigConfig(
        "label",
        ["L", "V", "VL"],
        "VL",
        "Component label style (L=include label, V=include value, VL=both)",
    ),
    ConfigConfig(
        "nolabels",
        bool,
        False,
        "Turns off labels on all components, except for part numbers on ICs.",
    ),
]


def add_config_arguments(a: argparse.ArgumentParser):
    "Register all the config options on the argument parser."
    for opt in OPTIONS:
        if isinstance(opt.clazz, list):
            a.add_argument(
                "--" + opt.name,
                help=opt.description,
                choices=opt.clazz,
                default=opt.default,
            )
        elif opt.clazz is bool:
            a.add_argument(
                "--" + opt.name,
                help=opt.description,
                action="store_false" if opt.default else "store_true",
            )
        else:
            a.add_argument(
                "--" + opt.name,
                help=opt.description,
                type=opt.clazz,
                default=opt.default,
            )


def apply_config_defaults(options: dict) -> dict:
    "Merge the defaults and ensure the options are the right type."
    for opt in OPTIONS:
        if opt.name not in options:
            options[opt.name] = opt.default
            continue
        if isinstance(opt.clazz, list):
            if options[opt.name] not in opt.clazz:
                raise ArgumentError(
                    f"config option {opt.name}: "
                    f"invalid choice: {options[opt.name]} "
                    f"(valid options are {', '.join(map(repr, opt.clazz))})"
                )
            continue
        try:
            options[opt.name] = opt.clazz(options[opt.name])
        except ValueError as err:
            raise ArgumentError(
                f"config option {opt.name}: "
                f"invalid {opt.clazz.__name__} value: "
                f"{options[opt.name]}"
            ) from err
    return options
