"""DataEditor in-flight save must not clear newer pending edits (#111)."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

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
        pytest.skip("node is required for DataEditor save-queue tests")
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


def test_reconcile_keeps_edits_queued_during_inflight_save(node_bin: str) -> None:
    script = EDITOR_JS.read_text(encoding="utf-8")
    assert "function snapshotSaveBatch" in script
    assert "function reconcileAfterSuccess" in script
    assert "this._pending = []" not in script.split("if (data.ok)")[1].split("} else if")[0]

    out = _run_node(
        node_bin,
        f"""
const api = require({json.dumps(str(EDITOR_JS))});
let pending = [
  {{row_key: "1", field: "a", value: "A", _opId: 1}},
];
const inserts = [];
const deletes = [];
const snapshot = api.snapshotSaveBatch(pending, inserts, deletes);
const body = api.serializeSaveBody(
  snapshot.updates, snapshot.inserts, snapshot.deletes, "1"
);
// Edit field B while the first save is in flight.
pending = pending.concat([
  {{row_key: "1", field: "b", value: "B", _opId: 2}},
]);
const kept = api.reconcileAfterSuccess(pending, inserts, deletes, snapshot);
process.stdout.write(JSON.stringify({{
  sent: body.updates,
  pendingAfter: kept.pending,
}}));
""",
    )
    payload = json.loads(out)
    assert payload["sent"] == [{"row_key": "1", "field": "a", "value": "A"}]
    assert payload["pendingAfter"] == [{"row_key": "1", "field": "b", "value": "B", "_opId": 2}]


def test_requeued_same_field_survives_inflight_ack(node_bin: str) -> None:
    """Replacing a field while its prior op is in flight keeps the newer op."""
    out = _run_node(
        node_bin,
        f"""
const api = require({json.dumps(str(EDITOR_JS))});
let pending = [
  {{row_key: "1", field: "a", value: "A1", _opId: 1}},
];
const snapshot = api.snapshotSaveBatch(pending, [], []);
// Same field edited again before response: new op id.
pending = [
  {{row_key: "1", field: "a", value: "A2", _opId: 2}},
];
const kept = api.reconcileAfterSuccess(pending, [], [], snapshot);
process.stdout.write(JSON.stringify(kept.pending));
""",
    )
    assert json.loads(out) == [{"row_key": "1", "field": "a", "value": "A2", "_opId": 2}]


def test_reconcile_refreshes_row_version_on_retained_edits(node_bin: str) -> None:
    out = _run_node(
        node_bin,
        f"""
const api = require({json.dumps(str(EDITOR_JS))});
let pending = [
  {{row_key: "1", field: "a", value: "A", row_version: "1", _opId: 1}},
];
const snapshot = api.snapshotSaveBatch(pending, [], []);
pending = pending.concat([
  {{row_key: "1", field: "b", value: "B", row_version: "1", _opId: 2}},
]);
const kept = api.reconcileAfterSuccess(pending, [], [], snapshot, "2");
process.stdout.write(JSON.stringify(kept.pending));
""",
    )
    assert json.loads(out) == [
        {"row_key": "1", "field": "b", "value": "B", "row_version": "2", "_opId": 2}
    ]

    out = _run_node(
        node_bin,
        f"""
const api = require({json.dumps(str(EDITOR_JS))});
const body = api.serializeSaveBody(
  [{{row_key: "1", field: "a", value: "A", row_version: "1", _opId: 9}}],
  [{{id: "new-1", name: "Ada", _opId: 10}}],
  [{{row_key: "2", _opId: 11}}],
  "3"
);
process.stdout.write(JSON.stringify(body));
""",
    )
    body = json.loads(out)
    assert body == {
        "updates": [{"row_key": "1", "field": "a", "value": "A", "row_version": "1"}],
        "inserts": [{"id": "new-1", "name": "Ada"}],
        "deletes": ["2"],
        "dataset_version": "3",
    }
