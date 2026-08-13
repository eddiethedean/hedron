"""DataEditor browser CSV export parity with server-side sanitization (#112)."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from hedron_data import Column, DataTable
from hedron_data.spreadsheet import _reject_or_sanitize

EDITOR_JS = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "hedron-data"
    / "src"
    / "hedron_data"
    / "assets"
    / "tabulator"
    / "editor.js"
)


@pytest.fixture(scope="module")
def node_bin() -> str:
    path = shutil.which("node")
    if path is None:
        pytest.skip("node is required for DataEditor CSV helper tests")
    return path


def _run_node(node_bin: str, script: str) -> str:
    result = subprocess.run(
        [node_bin, "-e", script],
        check=True,
        capture_output=True,
        text=True,
        cwd=str(EDITOR_JS.parent),
    )
    return result.stdout.strip()


def test_editor_js_exports_csv_helpers(node_bin: str) -> None:
    script = EDITOR_JS.read_text(encoding="utf-8")
    assert "function sanitizeFormulaCell" in script
    assert "function csvEscapeField" in script
    assert "function buildCsv" in script
    assert "JSON.stringify(row[c.field]" not in script
    assert "row[field] = value" in script

    out = _run_node(
        node_bin,
        f"""
const api = require({json.dumps(str(EDITOR_JS))});
const vectors = [
  "=2+2", "+1", "-1", "@cmd", "\\t=1", "safe", 'a\\"b', "x,y", "line\\r\\nbreak",
  " =HYPERLINK(\\"http://evil\\",\\"x\\")",
  "\\u0000=cmd",
  "\\ufeff=CMD",
  "\\u00a0=cmd",
  "\\n=cmd",
  "\\uff1dcmd",
  "\\uff0b1",
  "\\uff0d1",
  "\\uff20cmd",
];
for (const v of vectors) {{
  process.stdout.write(JSON.stringify(api.sanitizeFormulaCell(v)) + "\\n");
}}
process.stdout.write(api.buildCsv(
  [{{field: "name", title: "Name", visible: true}}],
  [{{name: "=2+2"}}, {{name: 'a"b'}}, {{name: "edited"}}]
) + "\\n");
""",
    )
    lines = out.splitlines()
    vectors = [
        "=2+2",
        "+1",
        "-1",
        "@cmd",
        "\t=1",
        "safe",
        'a"b',
        "x,y",
        "line\r\nbreak",
        ' =HYPERLINK("http://evil","x")',
        "\x00=cmd",
        "\ufeff=CMD",
        "\xa0=cmd",
        "\n=cmd",
        "\uff1dcmd",
        "\uff0b1",
        "\uff0d1",
        "\uff20cmd",
    ]
    sanitized = lines[: len(vectors)]
    csv_body = "\n".join(lines[len(vectors) :])

    expected = [_reject_or_sanitize(v, formula_policy="sanitize") for v in vectors]
    assert [json.loads(item) for item in sanitized] == expected

    assert csv_body.splitlines()[0] == "Name"
    assert csv_body.splitlines()[1] == "'=2+2"
    assert csv_body.splitlines()[2] == '"a""b"'
    assert csv_body.splitlines()[3] == "edited"
    assert '\\"' not in csv_body

    table = DataTable(
        rows=[{"name": "=2+2"}, {"name": 'a"b'}],
        columns=[Column(name="name", label="Name")],
    )
    # Server CSV ends with a trailing newline from csv.writer; compare data lines.
    server_lines = [line for line in table.to_csv().splitlines() if line]
    client_lines = csv_body.splitlines()[:3]
    assert client_lines[0] == server_lines[0]
    assert client_lines[1] == server_lines[1] or client_lines[1] == f'"{server_lines[1]}"'
    assert 'a""b' in client_lines[2]
    assert 'a""b' in server_lines[2]


def test_editor_js_keeps_pending_edits_in_row_model(node_bin: str) -> None:
    """Simulate _queueUpdate writing through to _rows before export."""
    out = _run_node(
        node_bin,
        f"""
const api = require({json.dumps(str(EDITOR_JS))});
const rows = [{{id: "1", name: "old"}}, {{id: "2", name: "=2+2"}}];
rows[0].name = "edited";
process.stdout.write(api.buildCsv(
  [
    {{field: "id", title: "Id", visible: true}},
    {{field: "name", title: "Name", visible: true}},
  ],
  rows
));
""",
    )
    assert "edited" in out
    assert "old" not in out.splitlines()[1]
    assert "'=2+2" in out
