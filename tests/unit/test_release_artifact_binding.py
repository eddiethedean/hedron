"""Release uploads must be exactly the approved reproducible artifact set."""

from __future__ import annotations

import hashlib
import json

from scripts import verify_release_artifacts


def test_release_artifact_verifier_authenticates_every_stable_artifact(
    tmp_path, monkeypatch
) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    rows: list[dict[str, str]] = []
    for index in range(26):
        name = f"package_{index:02d}-1.0.0-py3-none-any.whl"
        payload = f"artifact-{index}".encode()
        (dist / name).write_bytes(payload)
        rows.append({"name": name, "sha256": hashlib.sha256(payload).hexdigest()})
    evidence = tmp_path / "evidence.json"
    evidence.write_text(json.dumps({"artifacts": rows}), encoding="utf-8")
    monkeypatch.setattr(verify_release_artifacts, "DIST", dist)
    monkeypatch.setattr(verify_release_artifacts, "EVIDENCE", evidence)
    monkeypatch.setattr(verify_release_artifacts, "evidence_source_errors", lambda _: [])

    assert verify_release_artifacts.main() == 0
    # Beta satellites are built in the same train and receive workflow
    # attestations, but are intentionally outside the Stable hash lock.
    (dist / "unapproved-1.0.0.tar.gz").write_bytes(b"extra")
    assert verify_release_artifacts.main() == 0
    (dist / rows[0]["name"]).write_bytes(b"tampered")
    assert verify_release_artifacts.main() == 1


def test_release_artifact_verifier_rejects_stale_source_commit(monkeypatch) -> None:
    source = "a" * 40

    def fake_check_output(command, **_kwargs):
        if command[:3] == ["git", "diff", "--name-only"]:
            if command[3] == f"{source}..HEAD":
                return "packages/hedron/src/hedron/app.py\n"
            return ""
        if command[:3] == ["git", "ls-files", "--others"]:
            return ""
        raise AssertionError(command)

    monkeypatch.setattr(verify_release_artifacts.subprocess, "check_output", fake_check_output)

    assert verify_release_artifacts.evidence_source_errors(source) == [
        "approved release evidence is stale; source_commit predates non-evidence changes: "
        "packages/hedron/src/hedron/app.py"
    ]


def test_release_artifact_verifier_allows_evidence_only_commit(monkeypatch) -> None:
    source = "b" * 40

    def fake_check_output(command, **_kwargs):
        if command[:3] == ["git", "diff", "--name-only"]:
            if command[3] == f"{source}..HEAD":
                return (
                    "docs/acceptance/compatibility-report-100/local-build-evidence.json\n"
                    "docs/acceptance/compatibility-report-100/edron-build-evidence.json\n"
                )
            return ""
        if command[:3] == ["git", "ls-files", "--others"]:
            return ""
        raise AssertionError(command)

    monkeypatch.setattr(verify_release_artifacts.subprocess, "check_output", fake_check_output)

    assert verify_release_artifacts.evidence_source_errors(source) == []
