"""INTENT-056 evidence."""

from __future__ import annotations

import pytest

from hedron_core.security_plane import (
    IntentError,
    IntentState,
    MemoryIntentStore,
    SecurityKeyring,
    mint_intent,
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
