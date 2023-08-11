import sys
if "schemascii" in sys.modules:
    del sys.modules["schemascii"]

import warnings
import schemascii

print("monkeypatching... ", end="")

def patched(src):
    with warnings.catch_warnings(record=True) as captured_warnings:
        out = schemascii.render("<playground>", src)
    for warn in captured_warnings:
        print("warning:", warn.message)
    return out

schemascii.patched_render = patched
