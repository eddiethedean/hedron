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
    rows: list[dict[str, str | int]] = []
    for index in range(26):
        name = f"package_{index:02d}-1.0.0-py3-none-any.whl"
        payload = f"artifact-{index}".encode()
        (dist / name).write_bytes(payload)
        rows.append(
            {"name": name, "sha256": hashlib.sha256(payload).hexdigest(), "size": len(payload)}
        )
    evidence = tmp_path / "evidence.json"
    evidence.write_text(json.dumps({"artifacts": rows}), encoding="utf-8")
    monkeypatch.setattr(verify_release_artifacts, "DIST", dist)
    monkeypatch.setattr(verify_release_artifacts, "EVIDENCE", evidence)
    monkeypatch.setattr(verify_release_artifacts, "evidence_source_errors", lambda _, **__: [])

    assert verify_release_artifacts.main() == 0
    # Beta satellites are built in the same train and receive workflow
    # attestations, but are intentionally outside the Stable hash lock.
    (dist / "unapproved-1.0.0.tar.gz").write_bytes(b"extra")
    assert verify_release_artifacts.main() == 0
    (dist / rows[0]["name"]).write_bytes(b"tampered")
    assert verify_release_artifacts.main() == 1


def test_release_artifact_verifier_enforces_candidate_exact_set(tmp_path, monkeypatch) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    rows: list[dict[str, str | int]] = []
    for distribution in ("hedron_core", "hedron"):
        for suffix, ending in (("whl", "py3-none-any.whl"), ("tar.gz", "tar.gz")):
            name = (
                f"{distribution}-1.2.0-{ending}"
                if suffix == "whl"
                else f"{distribution}-1.2.0.{ending}"
            )
            payload = f"candidate-{distribution}-{suffix}".encode()
            (dist / name).write_bytes(payload)
            rows.append(
                {
                    "name": name,
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "size": len(payload),
                }
            )
    wheels = [row for row in rows if str(row["name"]).endswith(".whl")]
    evidence = tmp_path / "evidence" / "python-artifacts.json"
    evidence.parent.mkdir()
    evidence.write_text(
        json.dumps(
            {
                "schema": "hedron.phase-120-python-artifact-evidence/1",
                "phase": "1.2",
                "target": "v1.2.0",
                "source_commit": "a" * 40,
                "environment": {
                    "python": "3.12.0",
                    "uv": "0.12.1",
                    "os": "Linux",
                    "architecture": "x86_64",
                    "source_date_epoch": 315619200,
                },
                "reproducibility": {"repeat_builds": 2, "verified": True},
                "retention_reference": "https://github.com/example/actions/runs/1",
                "packages": ["hedron-core", "hedron"],
                "python310_compatibility": {
                    "schema": "hedron.phase-120-python310-compatibility/1",
                    "source_commit": "a" * 40,
                    "python": "3.10.20",
                    "candidate_install": "rejected by Requires-Python",
                    "candidate_artifact": next(
                        row["name"] for row in rows if str(row["name"]).startswith("hedron-1.2.0-")
                    ),
                    "candidate_sha256": next(
                        row["sha256"]
                        for row in rows
                        if str(row["name"]).startswith("hedron-1.2.0-")
                    ),
                    "candidate_rejection_mentions_python_310_and_311": True,
                    "unpinned_requirement": "hedron",
                    "resolved_version": "1.1.3",
                    "predecessor_version": "1.1.3",
                    "platform": "Linux",
                    "architecture": "x86_64",
                },
                "installed_application_upgrade_rollback": {
                    "schema": "hedron.phase-120-python311-upgrade-rollback/1",
                    "source_commit": "a" * 40,
                    "predecessor_version": "1.1.3",
                    "candidate_version": "1.2.0",
                    "python": "3.11.14",
                    "platform": "Linux",
                    "architecture": "x86_64",
                    "application": "generated fixture",
                    "baseline": {
                        "result": "pass",
                        "hedron": "1.1.3",
                        "uv_lock_sha256": "c" * 64,
                    },
                    "upgrade": {
                        "result": "pass",
                        "hedron": "1.2.0",
                        "uv_lock_sha256": "d" * 64,
                    },
                    "rollback": {
                        "result": "pass",
                        "hedron": "1.1.3",
                        "uv_lock_sha256": "c" * 64,
                        "restored_original_lock": True,
                    },
                    "candidate_artifacts": [
                        {"name": row["name"], "sha256": row["sha256"]} for row in wheels
                    ],
                },
                "artifacts": rows,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(verify_release_artifacts, "evidence_source_errors", lambda _, **__: [])
    monkeypatch.setattr(
        verify_release_artifacts,
        "expected_packages",
        lambda: {"hedron-core": "1.2.0", "hedron": "1.2.0"},
    )

    args = [
        "--evidence-manifest",
        str(evidence),
        "--dist-dir",
        str(dist),
        "--expected-artifact-count",
        "4",
        "--exact-set",
    ]
    assert verify_release_artifacts.main(args) == 0

    (dist / "unapproved-1.2.0.tar.gz").write_bytes(b"extra")
    assert verify_release_artifacts.main(args) == 1


def test_candidate_artifact_verifier_rejects_malformed_ledger(tmp_path, monkeypatch) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    evidence = tmp_path / "python-artifacts.json"
    evidence.write_text(
        json.dumps({"artifacts": [{"name": "hedron-1.2.0.whl", "sha256": "abc"}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(verify_release_artifacts, "evidence_source_errors", lambda _, **__: [])

    assert (
        verify_release_artifacts.main(
            [
                "--evidence-manifest",
                str(evidence),
                "--dist-dir",
                str(dist),
                "--expected-artifact-count",
                "1",
                "--exact-set",
            ]
        )
        == 1
    )


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


def test_candidate_ledger_allows_only_the_ledger_after_source_freeze(monkeypatch) -> None:
    source = "b" * 40
    evidence_root = verify_release_artifacts.ROOT / "docs/acceptance/evidence-120"
    evidence_prefix = f"{evidence_root.relative_to(verify_release_artifacts.ROOT)}/"
    changed = f"{evidence_prefix}python-artifacts.json\n{evidence_prefix}native-artifacts.json\n"

    def fake_check_output(command, **_kwargs):
        if command[:3] == ["git", "diff", "--name-only"]:
            if command[3] == f"{source}..HEAD":
                return changed
            return ""
        if command[:3] == ["git", "ls-files", "--others"]:
            return ""
        raise AssertionError(command)

    monkeypatch.setattr(verify_release_artifacts.subprocess, "check_output", fake_check_output)
    assert not verify_release_artifacts.evidence_source_errors(source, evidence_root=evidence_root)

    changed = f"{evidence_root.relative_to(verify_release_artifacts.ROOT)}/SCOPE.md\n"
    assert verify_release_artifacts.evidence_source_errors(source, evidence_root=evidence_root) == [
        "approved release evidence is stale; source_commit predates non-evidence changes: "
        "docs/acceptance/evidence-120/SCOPE.md"
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
