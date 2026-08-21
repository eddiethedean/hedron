"""INTENT-056 evidence."""

from __future__ import annotations

import pytest

from hedron_core.security_plane import (
    IntentError,
    IntentState,
    KeyRecord,
    MemoryIntentStore,
    SecurityKeyring,
    mint_intent,
    verify_and_consume,
    verify_intent,
)


def test_intent_056_bind_consume_and_key_rotation() -> None:
    keyring = SecurityKeyring()
    key = keyring.mint_key(key_id="k1", purpose="intent", secret=b"a" * 32)
    store = MemoryIntentStore()
    intent = mint_intent(
        keyring=keyring,
        actor="user-1",
        tenant="t1",
        action="items.update",
        method="POST",
        resource="item:9",
        revision="r3",
        target="/items/9",
        payload={"name": "x"},
    )
    store.put_minted(intent.intent_id)
    verify_intent(
        intent,
        keyring=keyring,
        actor="user-1",
        tenant="t1",
        action="items.update",
        method="POST",
        resource="item:9",
        revision="r3",
        target="/items/9",
        payload={"name": "x"},
    )
    with pytest.raises(IntentError):
        verify_intent(
            intent,
            keyring=keyring,
            actor="user-2",
            tenant="t1",
            action="items.update",
            method="POST",
            resource="item:9",
            revision="r3",
            target="/items/9",
            payload={"name": "x"},
        )
    assert store.claim(intent.intent_id) is IntentState.CLAIMED
    assert store.consume(intent.intent_id) is IntentState.CONSUMED
    with pytest.raises(IntentError):
        store.consume(intent.intent_id)
    successor = keyring.mint_key(key_id="k2", purpose="intent", secret=b"b" * 32)
    keyring.rotate(key.key_id, successor=successor)
    # Old key still verifies.
    verify_intent(
        intent,
        keyring=keyring,
        actor="user-1",
        tenant="t1",
        action="items.update",
        method="POST",
        resource="item:9",
        revision="r3",
        target="/items/9",
        payload={"name": "x"},
    )
    windowed = SecurityKeyring()
    windowed.add(
        KeyRecord(
            key_id="k-exp",
            purpose="intent",
            secret=b"c" * 32,
            status="active",
            not_before=1.0,
            not_after=2.0,
        )
    )
    with pytest.raises(IntentError):
        windowed.get_for_mint("intent", now=1000.0)
    fresh = mint_intent(
        keyring=keyring,
        actor="user-1",
        tenant="t1",
        action="items.update",
        method="POST",
        resource="item:9",
        revision="r4",
        target="/items/9",
        payload={"name": "y"},
        store=store,
        now=1000.0,
    )
    verify_and_consume(
        fresh,
        keyring=keyring,
        store=store,
        actor="user-1",
        tenant="t1",
        action="items.update",
        method="POST",
        resource="item:9",
        revision="r4",
        target="/items/9",
        payload={"name": "y"},
        now=1000.0,
    )
    with pytest.raises(IntentError):
        store.consume(fresh.intent_id)
