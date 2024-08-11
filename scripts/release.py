#! /usr/bin/env python3
import argparse
import os
import re
import sys

# pylint: disable=unspecified-encoding,missing-function-docstring


def cmd(sh_line):
    print(sh_line)
    if code := os.system(sh_line):
        print("*** Error", code, file=sys.stderr)
        sys.exit(code)


def slurp(file):
    with open(file) as f:
        return f.read()


def spit(file, text):
    with open(file, "w") as f:
        f.write(text)


a = argparse.ArgumentParser()
a.add_argument("version", help="release tag")
args = a.parse_args()

# Patch new version into files
pp_text = slurp("pyproject.toml")
spit("pyproject.toml",
     re.sub(r'version = "[\d.]+"',
            f'version = "{args.version}"', pp_text))

init_text = slurp("schemascii/__init__.py")
spit("schemascii/__init__.py",
     re.sub(r'__version__ = "[\d.]+"',
            f'__version__ = "{args.version}"', init_text))

cmd("scripts/docs.py")
cmd("python3 -m build --sdist")
cmd("python3 -m build --wheel")

cmd("schemascii test_data/test_charge_pump.txt --out test_data/test_charge_pump.txt.svg")

print("for some reason convert isn't working with the css, so aborting the auto-rendering")
sys.exit(0)

cmd("convert test_data/test_charge_pump.txt.svg test_data/test_charge_pump.png")

svg_content = slurp("test_data/test_charge_pump.txt.svg")
css_content = slurp("schemascii_example.css")
spit("test_data/test_charge_pump_css.txt.svg",
     svg_content.replace("</svg>", f'<style>{css_content}</style></svg>'))
cmd("convert test_data/test_charge_pump_css.txt.svg test_data/test_charge_pump_css.png")

# cmd("git add -A")
# cmd("git commit -m 'blah'")
# cmd(f"git tag {args.version}")
# cmd("git push --tags")

# sudo apt update && sudo apt install imagemagick
# for convert command
# doesn't seem to work with the css though :(
