"""Upgrade fixtures: 0.28.2 non-Workbench parity into 0.29."""

from __future__ import annotations

import json
from pathlib import Path

from hedron_workbench.config import WorkbenchConfig, WorkbenchMode
from hedron_workbench.resolve import resolve_deployment

GOLDENS = Path(__file__).resolve().parent / "goldens_0_28_2"


def test_mode_off_golden() -> None:
    resolved = resolve_deployment(WorkbenchConfig(mode=WorkbenchMode.OFF), environ={})
    payload = {
        "mode": resolved.mode.value,
        "browser_mount": resolved.browser_mount,
        "cookie_mount": resolved.cookie_mount,
        "reload": resolved.reload,
        "workers": resolved.workers,
    }
    path = GOLDENS / "workbench_off.json"
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = json.loads(path.read_text(encoding="utf-8"))
    assert payload == expected


def test_resolve_alias_golden() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(),
        environ={"BASE_PATH": "/s/alias/p/1", "HOST": "127.0.0.1"},
    )
    payload = {
        "browser_mount": resolved.browser_mount,
        "source": resolved.source,
        "alias_warned": any("BASE_PATH" in w for w in resolved.warnings),
    }
    path = GOLDENS / "workbench_resolve.json"
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = json.loads(path.read_text(encoding="utf-8"))
    assert payload == expected


def test_mount_once_golden() -> None:
    resolved = resolve_deployment(WorkbenchConfig(mount="/s/demo/p/9"), environ={})
    payload = {
        "browser_mount": resolved.browser_mount,
        "cookie_mount": resolved.cookie_mount,
        "source": "explicit:mount",
    }
    path = GOLDENS / "workbench_mount.json"
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = json.loads(path.read_text(encoding="utf-8"))
    assert payload == expected
