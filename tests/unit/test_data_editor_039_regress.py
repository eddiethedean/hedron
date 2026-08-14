"""REGRESS-039 DataEditor client fixes (#113/#119/#120/#121) via editor.js helpers."""

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
        pytest.skip("node is required for DataEditor REGRESS-039 tests")
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


def test_039_row_versions_bump_once_per_row(node_bin: str) -> None:
    out = _run_node(
        node_bin,
        f"""
const api = require({json.dumps(str(EDITOR_JS))});
const snapshot = api.snapshotSaveBatch(
  [
    {{row_key: "1", field: "first", value: "A", row_version: "1", _opId: 1}},
    {{row_key: "1", field: "last", value: "B", row_version: "1", _opId: 2}},
  ],
  [],
  []
);
process.stdout.write(JSON.stringify(api.rowVersionsAfterBatch(snapshot, "2")));
""",
    )
    assert json.loads(out) == {"1": "2"}


def test_039_delete_unsaved_insert_not_queued(node_bin: str) -> None:
    source = EDITOR_JS.read_text(encoding="utf-8")
    assert "wasInsert" in source
    assert "unsaved local inserts must not become server deletes" in source


def test_039_undo_restores_prior_pending(node_bin: str) -> None:
    source = EDITOR_JS.read_text(encoding="utf-8")
    assert "priorPending" in source
    assert "last.priorPending" in source


def test_039_retain_and_retry_rebases_version(node_bin: str) -> None:
    source = EDITOR_JS.read_text(encoding="utf-8")
    assert "_conflictServerVersion" in source
    assert "Cannot retry without a fresh server revision" in source
    assert "row_version: fresh" in source or "row_version: this._conflictServerVersion" in source
