import argparse
import os
import re
import sys

a = argparse.ArgumentParser("release.py")
a.add_argument("version", help="release tag")
args = a.parse_args()

# Patch new version into files
with open("pyproject.toml") as pyproject:
    pp_text = pyproject.read()
with open("pyproject.toml", "w") as pyproject:
    pyproject.write(
        re.sub(r'version = "[\d.]+"', f'version = "{args.version}"', pp_text))

with open("schemascii/__init__.py") as init:
    init_text = init.read()
with open("schemascii/__init__.py", "w") as init:
    init.write(
        re.sub(r'__version__ = "[\d.]+"', f'__version__ = "{args.version}"', init_text))


def cmd(sh_line):
    print(sh_line)
    if os.system(sh_line):
        sys.exit(1)


cmd("python3 -m build --sdist")
cmd("python3 -m build --wheel")
print("git add -A")
print(f"git commit -m 'blah'")
print(f"git tag {args.version}")
print("git push --tags")
