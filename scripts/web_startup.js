// cSpell:ignore pyodide pyproject
var pyodide;
var console = document.getElementById("console");
var errors = document.getElementById("errors");
var css_box = document.getElementById("css");
var source = document.getElementById("schemascii");
var download_button = document.getElementById("download");
var ver_switcher = document.getElementById("version");

var schemascii;
var monkeysrc;

var ver_map;

async function main() {
    try {
        info("Loading Python... ");
        pyodide = await loadPyodide({ stdout: info, stderr: error });
        info("done\nInstalling micropip...");
        await pyodide.loadPackage("micropip", { errorCallback: error, messageCallback: () => { } });
        info("done\nFetching versions... ");
        monkeysrc = await fetch("scripts/monkeypatch.py").then(r => r.text());
        var foo = await fetch("https://api.github.com/repos/dragoncoder047/schemascii/contents/dist").then(r => r.json());
        foo = foo.filter(x => x.name.endsWith(".whl")).map(x => x.path);
        ver_map = Object.fromEntries(foo.map(x => [/\/schemascii-([\d.]+)-/.exec(x)[1], x]))
        var all_versions = Object.keys(ver_map);
        //all_versions.push("DEV");
        for (var v of all_versions) {
            var o = document.createElement("option");
            o.textContent = o.value = v;
            ver_switcher.append(o);
        }
        var latest_version = await fetch("pyproject.toml").then(r => r.text()).then(r => /version = "([\d.]+)"/.exec(r)[1]);
        ver_switcher.value = latest_version;
        info(`["${all_versions.join('", "')}"]\nlatest=${latest_version}\n`);
        await switch_version();
        css_box.addEventListener("input", debounce(sync_css));
        source.addEventListener("input", debounce(catched(render)));
        download_button.addEventListener("click", download);
        ver_switcher.addEventListener("change", acatched(switch_version));

        source.removeAttribute("disabled");
        css_box.removeAttribute("disabled");
        console.textContent = "Ready";
    } catch (e) {
        error(`\nFATAL ERROR:\n${e.stack}\n`);
        throw e;
    }
}
function monkeypatch() {
    pyodide.runPython(monkeysrc);
}
function info(line) {
    console.textContent += line;
}
function error(text) {
    errors.textContent += text;
}
function debounce(fun) {
    var timeout;
    return function () {
        if (timeout) clearTimeout(timeout);
        timeout = setTimeout(fun.bind(this, arguments), 100);
    };
}
function catched(fun) {
    return function () {
        try {
            fun.call(this, arguments);
        } catch (e) {
            error(e.stack);
        }
    };
}
async function acatched(fun) {
    return async function() {
        try {
            await fun.call(this, arguments);
        } catch (e) {
            error(e.stack);
        }
    };
}
function sync_css() {
    style_elem.innerHTML = css_box.value;
}
function render() {
    console.textContent = "";
    errors.textContent = "";
    output.textContent = schemascii.patched_render(source.value);
}

async function switch_version() {
    info("Installing Schemascii version " + ver_switcher.value + "... ")
    await pyodide.pyimport("micropip").install(ver_map[ver_switcher.value]);
    monkeypatch();
    schemascii = pyodide.runPython("import schemascii; schemascii");
    info("done\n");
}

function download() {
    var a = document.createElement("a");
    a.setAttribute("href", URL.createObjectURL(new Blob([output.innerHTML], {"type": "application/svg+xml"})));
    a.setAttribute("download", `schemascii_playground_${new Date().toISOString()}_no_css.svg`);
    a.click();
}

main();

// fetch("https://github.com/dragoncoder047/schemascii/zipball/main/").then(r => r.arrayBuffer()).then(b => pyodide.unpackArchive(b, "zip"));
