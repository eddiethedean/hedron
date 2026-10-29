"""Bounded private-storage helpers used by the explicit UI pytest plugin."""

from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import Protocol

import pytest

import hedron.testing.pytest_plugin as ui_plugin
from hedron.testing.pytest_plugin import _make_private_tree, _runtime_provenance


class _RecordProperty(Protocol):
    def __call__(self, name: str, value: object) -> None: ...


@pytest.mark.skipif(os.name != "posix", reason="POSIX directory mode contract")
def test_artifact_tree_is_private_without_changing_selected_root(tmp_path: Path) -> None:
    root = tmp_path / "artifacts"
    root.mkdir(mode=0o750)
    root.chmod(0o750)
    target = root / "run" / "worker" / "test" / "attempt"

    _make_private_tree(root, target)

    assert stat.S_IMODE(root.stat().st_mode) == 0o750
    private_directories = (
        root / "run",
        root / "run" / "worker",
        root / "run" / "worker" / "test",
        target,
    )
    for directory in private_directories:
        assert stat.S_IMODE(directory.stat().st_mode) == 0o700


def test_artifact_tree_rejects_symlinked_run_directory(tmp_path: Path) -> None:
    root = tmp_path / "artifacts"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "run").symlink_to(outside, target_is_directory=True)

    with pytest.raises(OSError, match="symlink"):
        _make_private_tree(root, root / "run" / "worker" / "test")
    assert list(outside.iterdir()) == []


def test_runtime_provenance_contains_versions_without_environment_values() -> None:
    provenance = _runtime_provenance()

    assert provenance["python"]
    assert provenance["platform"]
    assert set(provenance) == {
        "python",
        "platform",
        "hedron",
        "pytest",
        "pytest_playwright",
        "playwright",
        "uvicorn",
    }


def test_artifact_writer_fails_closed_at_per_worker_budget(
    request: pytest.FixtureRequest,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = request.config
    monkeypatch.setattr(
        config.option, "hedron_ui_artifacts", str(tmp_path / "artifacts"), raising=False
    )
    monkeypatch.setattr(ui_plugin._ARTIFACT_BUDGET, "bytes_written", 0)
    monkeypatch.setattr(ui_plugin._ARTIFACT_BUDGET, "artifacts_written", 0)
    monkeypatch.setattr(ui_plugin, "_MAX_ARTIFACT_BYTES_PER_WORKER", 0)

    write = ui_plugin._artifact_writer(request, config)
    with pytest.raises(OSError, match="per-worker budget"):
        write({"error_categories": ["synthetic_probe"]})

    assert not list((tmp_path / "artifacts").rglob("manifest.json"))


def test_artifact_writer_respects_manifest_byte_ceiling(
    request: pytest.FixtureRequest,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    record_property: _RecordProperty,
) -> None:
    config = request.config
    monkeypatch.setattr(
        config.option, "hedron_ui_artifacts", str(tmp_path / "artifacts"), raising=False
    )
    monkeypatch.setattr(ui_plugin._ARTIFACT_BUDGET, "bytes_written", 0)
    monkeypatch.setattr(ui_plugin._ARTIFACT_BUDGET, "artifacts_written", 0)

    ui_plugin._artifact_writer(request, config)({"error_categories": ["synthetic_probe"]})

    manifest = next((tmp_path / "artifacts").rglob("manifest.json"))
    size = manifest.stat().st_size
    record_property("structured_manifest_bytes", str(size))
    assert 0 < size <= ui_plugin._MAX_MANIFEST_BYTES
