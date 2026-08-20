"""SECURITY-052 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_conformance import (
    SandboxPolicy,
    refuse_secret_env_capture,
    validate_suite_path,
)


def test_security_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["SECURITY-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_refuse_secret_env_capture() -> None:
    secrets = refuse_secret_env_capture(
        {
            "PATH": "/usr/bin",
            "API_KEY": "should-not-capture",
            "HEDRON_TOKEN": "nope",
            "HOME": "/tmp",
        }
    )
    assert "API_KEY" in secrets
    assert "HEDRON_TOKEN" in secrets
    assert "PATH" not in secrets


def test_sandbox_policy_refuses_secret_env() -> None:
    policy = SandboxPolicy()
    try:
        policy.env_for_subprocess({"AWS_SECRET_ACCESS_KEY": "x"})
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_suite_path_rejects_traversal(tmp_path: Path) -> None:
    root = tmp_path / "suites"
    root.mkdir()
    (root / "ok.json").write_text("[]", encoding="utf-8")
    assert validate_suite_path("ok.json", root=root).name == "ok.json"
    try:
        validate_suite_path("../escape.json", root=root)
        ok = False
    except ValueError:
        ok = True
    assert ok
