"""Edron release uploads must match the approved Edron-lane artifacts exactly."""

from __future__ import annotations

import hashlib
import json
import sys

from scripts import verify_edron_release_artifacts


def test_edron_release_artifact_verifier_authenticates_exact_inventory(
    tmp_path, monkeypatch
) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    rows: list[dict[str, str]] = []
    for name in (
        "edron-1.0.0-py3-none-any.whl",
        "edron-1.0.0.tar.gz",
        "edron_sim-0.1.0-py3-none-any.whl",
        "edron_sim-0.1.0.tar.gz",
    ):
        payload = name.encode()
        (dist / name).write_bytes(payload)
        rows.append({"name": name, "sha256": hashlib.sha256(payload).hexdigest()})
    evidence = tmp_path / "evidence.json"
    evidence.write_text(
        json.dumps({"source_commit": "a" * 40, "artifacts": rows}), encoding="utf-8"
    )
    monkeypatch.setattr(verify_edron_release_artifacts, "EVIDENCE", evidence)
    monkeypatch.setattr(
        verify_edron_release_artifacts, "evidence_source_errors", lambda _: []
    )
    monkeypatch.setattr(sys, "argv", ["verify", "--dist-dir", str(dist)])

    assert verify_edron_release_artifacts.main() == 0
    (dist / "unapproved-1.0.0.tar.gz").write_bytes(b"extra")
    assert verify_edron_release_artifacts.main() == 1
    (dist / "unapproved-1.0.0.tar.gz").unlink()
    (dist / rows[0]["name"]).write_bytes(b"tampered")
    assert verify_edron_release_artifacts.main() == 1
