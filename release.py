import argparse
import os

a = argparse.ArgumentParser("release.py")
a.add_argument("version", help="release tag")
a.add_argument("-m", "--message", default=None, help="release commit message")
args = a.parse_args()
if args.message is None:
    args.message = f"Release {args.version}"


def cmd(sh_line):
    print(sh_line)
    os.system(sh_line)


cmd("git add -A")
cmd(f"git commit -m {args.message!r}")
cmd(f"git tag {args.version}")
cmd("git push --tags")
