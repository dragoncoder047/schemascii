import os
import sys

# pylint: disable=missing-function-docstring


def cmd(sh_line: str, say: bool = True):
    if say:
        print(sh_line)
    if code := os.system(sh_line):  # nosec start_process_with_a_shell
        print("*** Error", code, file=sys.stderr)
        sys.exit(code)


def slurp(file: os.PathLike) -> str:
    with open(file) as f:
        return f.read()


def spit(file: os.PathLike, text: str):
    with open(file, "w") as f:
        f.write(text)


def spy[T](value: T) -> T:
    print(value)
    return value
