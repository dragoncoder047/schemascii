import functools
import sys
import re
import js
import json
import warnings
from pyodide.http import open_url as get
import micropip


def sync_css():
    style_elem.innerHTML = css_box.value


def render_catch_warnings(*args, **kwargs):
    import schemascii
    console.textContent = ""
    errors.textContent = ""
    with warnings.catch_warnings(record=True) as captured_warnings:
        out = schemascii.render(*args, **kwargs)
    for warn in captured_warnings:
        print("warning:", warn.message)
    return out


def switch_version():
    if "schemascii" in sys.modules:
        del sys.modules["schemascii"]  # Invalidate cache
    version = ver_switcher.value
    js.eval(
        f'''(async () => await pyodide.globals.get("micropip").install({versions_to_wheel_map[version]!r}))();''')


def download_svg():
    a = js.document.createElement("a")
    a.setAttribute("href", js.URL.createObjectURL(js.Blob.new(
        [output.innerHTML], {"type": "application/svg+xml"})))
    a.setAttribute(
        "download", f"schemascii_playground_{js.Date.new.toISOString()}_no_css.svg")
    a.click()


output = js.document.getElementById("output")
css_box = js.document.getElementById("css")
console = js.document.getElementById("console")
source = js.document.getElementById("schemascii")
style_elem = js.document.getElementById("custom-css")
errors = js.document.getElementById("errors")
ver_switcher = js.document.getElementById("version")
download_button = js.document.getElementById("download")


print("Loading all versions... ", end="")
foo = json.load(
    get("https://api.github.com/repos/dragoncoder047/schemascii/contents/dist"))
foo = filter(lambda x: x["name"].endswith(".whl"), foo)
foo = list(map(lambda x: x["path"], foo))
versions_to_wheel_map = dict(
    zip(map(lambda x: re.search(r"""/schemascii-([\d.]+)-""", x).group(1), foo), foo))
all_versions = list(versions_to_wheel_map.keys())
latest_version = re.search(
    r'''version = "([\d.]+)"''', get("pyproject.toml").read()).group(1)
print(all_versions, "latest =", latest_version)

for ver in all_versions:
    opt = js.document.createElement("option")
    opt.value = opt.textContent = ver
    ver_switcher.append(opt)

ver_switcher.value = latest_version
await micropip.install(versions_to_wheel_map[latest_version])


css_source = get("schemascii_example.css").read()
style_elem.textContent = css_source
css_box.value = css_source
