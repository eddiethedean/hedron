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

    assert verify_release_artifacts.main() == 0
    # Beta satellites are built in the same train and receive workflow
    # attestations, but are intentionally outside the Stable hash lock.
    (dist / "unapproved-1.0.0.tar.gz").write_bytes(b"extra")
    assert verify_release_artifacts.main() == 0
    (dist / rows[0]["name"]).write_bytes(b"tampered")
    assert verify_release_artifacts.main() == 1
