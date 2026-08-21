"""REPLAY-055 evidence."""

from __future__ import annotations

from hedron.replay import MemoryReplayStore, ReplayState, fingerprint_request


def test_issue_548_same_key_different_fingerprint_is_conflict() -> None:
    store = MemoryReplayStore()
    fp1 = fingerprint_request(
        action_id="revoke", subject="u1", tenant="t1", inputs={"a": 1}, policy_version="1"
    )
    fp2 = fingerprint_request(
        action_id="revoke", subject="u1", tenant="t1", inputs={"a": 2}, policy_version="1"
    )
    first = store.claim(key="k1", fingerprint=fp1, scope="t1:u1:revoke", retention_seconds=60)
    assert first.state is ReplayState.FIRST
    store.complete(key="k1", scope="t1:u1:revoke", fingerprint=fp1, status=200, body=b"ok")
    conflict = store.claim(key="k1", fingerprint=fp2, scope="t1:u1:revoke", retention_seconds=60)
    assert conflict.state is ReplayState.CONFLICT
    replay = store.claim(key="k1", fingerprint=fp1, scope="t1:u1:revoke", retention_seconds=60)
    assert replay.state is ReplayState.REPLAYED
    assert replay.cached_body == b"ok"
