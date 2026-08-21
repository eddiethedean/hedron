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
    assert store.complete(
        key="k1",
        scope="t1:u1:revoke",
        fingerprint=fp1,
        status=200,
        body=b"ok",
        media_type="text/plain",
    )
    conflict = store.claim(key="k1", fingerprint=fp2, scope="t1:u1:revoke", retention_seconds=60)
    assert conflict.state is ReplayState.CONFLICT
    replay = store.claim(key="k1", fingerprint=fp1, scope="t1:u1:revoke", retention_seconds=60)
    assert replay.state is ReplayState.REPLAYED
    assert replay.cached_body == b"ok"
    assert replay.cached_media_type == "text/plain"


def test_issue_548_in_flight_and_abort_release_key() -> None:
    store = MemoryReplayStore()
    fp = fingerprint_request(
        action_id="x", subject="s", tenant="", inputs={"body_sha256": "abc"}, policy_version="1"
    )
    first = store.claim(key="k", fingerprint=fp, scope=":s:x", retention_seconds=60)
    assert first.state is ReplayState.FIRST
    inflight = store.claim(key="k", fingerprint=fp, scope=":s:x", retention_seconds=60)
    assert inflight.state is ReplayState.IN_FLIGHT
    store.abort(key="k", scope=":s:x", fingerprint=fp)
    again = store.claim(key="k", fingerprint=fp, scope=":s:x", retention_seconds=60)
    assert again.state is ReplayState.FIRST


def test_fingerprint_includes_body_digest() -> None:
    a = fingerprint_request(
        action_id="a",
        subject="s",
        tenant="",
        inputs={"body_sha256": "1"},
        policy_version="1",
    )
    b = fingerprint_request(
        action_id="a",
        subject="s",
        tenant="",
        inputs={"body_sha256": "2"},
        policy_version="1",
    )
    assert a != b
