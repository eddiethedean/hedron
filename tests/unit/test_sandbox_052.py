"""SANDBOX-052 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_conformance import (
    NO_NETWORK_MARKER,
    PROCESS_KILL_TIMEOUT_S,
    SandboxPolicy,
    SuitePathError,
    validate_suite_path,
)
from hedron_conformance.sandbox import (
    DEFAULT_MAX_ARCHIVE_BYTES,
    DEFAULT_MAX_ARCHIVE_MEMBERS,
)


def test_sandbox_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["SANDBOX-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_sandbox_policy_defaults() -> None:
    policy = SandboxPolicy()
    assert policy.allow_network is False
    assert policy.no_network_marker == NO_NETWORK_MARKER
    assert policy.process_kill_timeout_s == PROCESS_KILL_TIMEOUT_S
    assert policy.max_archive_bytes == DEFAULT_MAX_ARCHIVE_BYTES
    assert policy.max_archive_members == DEFAULT_MAX_ARCHIVE_MEMBERS
    env = policy.env_for_subprocess({"LANG": "C"})
    assert env[NO_NETWORK_MARKER] == "1"
    assert env["LANG"] == "C"


def test_validate_suite_path_under_root(tmp_path: Path) -> None:
    root = tmp_path / "root"
    nested = root / "a"
    nested.mkdir(parents=True)
    target = nested / "suite.json"
    target.write_text("[]", encoding="utf-8")
    resolved = validate_suite_path("a/suite.json", root=root)
    assert resolved == target.resolve()
    try:
        validate_suite_path(tmp_path / "outside.json", root=root)
        raised = False
    except SuitePathError:
        raised = True
    assert raised
