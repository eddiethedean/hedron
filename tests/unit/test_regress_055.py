"""REGRESS-055 evidence."""

from __future__ import annotations

from pathlib import Path

from hedron.replay import MemoryReplayStore, ReplayState, fingerprint_request
from hedron.upload import UploadBudget, materialize_upload


def test_regress_055_upgrade_fixtures_present() -> None:
    text = Path("docs/acceptance/upgrade-fixtures-055.md").read_text(encoding="utf-8")
    assert "0.54" in text
    assert "workflow_055" in text


def test_regress_055_cleanup_and_replay_no_orphans() -> None:
    handle = materialize_upload(filename="a.txt", content=b"1", budget=UploadBudget())
    path = handle.path
    handle.cleanup()
    assert not path.exists()

    store = MemoryReplayStore()
    fp = fingerprint_request(action_id="x", subject="s", tenant="", inputs={}, policy_version="1")
    claim = store.claim(key="k", fingerprint=fp, scope=":s:x", retention_seconds=1)
    assert claim.state is ReplayState.FIRST
