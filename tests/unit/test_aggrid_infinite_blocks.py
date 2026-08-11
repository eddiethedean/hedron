"""AG Grid infinite requests can be fulfilled by asynchronous event listeners."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

_HOST = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "hedron-data"
    / "src"
    / "hedron_data"
    / "assets"
    / "aggrid"
    / "host.js"
)


@pytest.fixture(scope="module")
def node_bin() -> str:
    path = shutil.which("node")
    if path is None:
        pytest.skip("node is required for AG Grid host tests")
    return path


def test_infinite_listener_can_fulfill_an_async_server_block(node_bin: str) -> None:
    script = """
const fs = require("fs");
const vm = require("vm");
const listeners = {};
const host = {
  attrs: {
    "data-hedron-payload": JSON.stringify({
      columns: [{name: "id"}], rows: [{id: "embedded"}], total: 1000,
    }),
    "data-row-model": "infinite",
  },
  getAttribute(name) { return this.attrs[name] || null; },
  setAttribute() {}, removeAttribute() {}, textContent: "",
  dispatchEvent(event) {
    const handler = listeners[event.type];
    if (handler) handler(event);
    return !event.defaultPrevented;
  },
};
global.CustomEvent = class {
  constructor(type, options) {
    this.type = type; Object.assign(this, options); this.defaultPrevented = false;
  }
  preventDefault() { this.defaultPrevented = true; }
};
global.document = {
  addEventListener(name, handler) { listeners[name] = handler; },
  querySelectorAll() { return [host]; },
};
global.window = { agGrid: {
  createGrid(_el, options) {
    global.datasource = options.datasource;
    return { addEventListener() {}, destroy() {} };
  },
} };
vm.runInThisContext(fs.readFileSync("host.js", "utf8"));
listeners.DOMContentLoaded();
host.dispatchEvent = function(event) {
  if (event.type === "hedron-data-pagination") {
    event.preventDefault();
    setTimeout(() => event.detail.success([{id: "server"}], 500), 0);
  }
  return !event.defaultPrevented;
};
let received = null;
global.datasource.getRows({
  startRow: 200, endRow: 300, sortModel: [], filterModel: {},
  successCallback(rows, lastRow) { received = {rows, lastRow}; },
  failCallback() { throw new Error("unexpected failure"); },
});
if (received !== null) throw new Error("embedded fallback was used before async response");
setTimeout(() => process.stdout.write(JSON.stringify(received)), 10);
"""
    result = subprocess.run(
        [node_bin, "-e", script],
        check=True,
        capture_output=True,
        text=True,
        cwd=str(_HOST.parent),
    )
    assert json.loads(result.stdout) == {"rows": [{"id": "server"}], "lastRow": 500}
