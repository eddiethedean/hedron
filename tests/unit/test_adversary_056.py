"""ADVERSARY-056 evidence."""

from __future__ import annotations

import pytest

from hedron_core.security_plane import (
    EgressError,
    EgressPolicy,
    IntentError,
    MemoryIntentStore,
    SecurityContext,
    SecurityContextError,
    SecurityKeyring,
    TrustCompileError,
    TrustPurpose,
    assert_ssrf_safe,
    compile_trust,
    mint_intent,
    verify_intent,
)


def test_adversary_056_shared_corpus() -> None:
    # Encoding / scheme smuggling
    with pytest.raises(TrustCompileError):
        compile_trust("javascript:alert(1)", TrustPurpose.URL_NAVIGATION)
    with pytest.raises(TrustCompileError):
        compile_trust("<svg><script>x</script></svg>", TrustPurpose.MARKUP_SVG)
    # Cross-purpose reuse
    compiled = compile_trust("/ok", TrustPurpose.URL_NAVIGATION)
    with pytest.raises(TrustCompileError):
        compile_trust(compiled, TrustPurpose.SELECTOR)
    # DNS / private SSRF
    with pytest.raises(EgressError):
        assert_ssrf_safe("http://169.254.169.254/latest/meta-data")
    policy = EgressPolicy(allowed_hosts=frozenset({"api.example"}))
    with pytest.raises(EgressError):
        policy.require("https://api.example@evil.example/")
    # Context confusion
    ctx = SecurityContext(
        application_id="a", subject_id="s", tenant_id="t", scopes=frozenset({"r"})
    )
    payload = ctx.to_serializable()
    with pytest.raises(SecurityContextError):
        SecurityContext.from_serializable({**payload, "fingerprint": "deadbeef" * 4})
    # Stale / substituted intent
    keyring = SecurityKeyring()
    keyring.mint_key(secret=b"c" * 32)
    intent = mint_intent(
        keyring=keyring,
        actor="a",
        tenant="t",
        action="do",
        method="POST",
        resource="r",
        revision="1",
        target="/t",
        payload={"x": 1},
        ttl_seconds=1,
        now=0,
    )
    with pytest.raises(IntentError):
        verify_intent(
            intent,
            keyring=keyring,
            actor="a",
            tenant="t",
            action="do",
            method="POST",
            resource="r",
            revision="1",
            target="/t",
            payload={"x": 1},
            now=10,
        )
    store = MemoryIntentStore()
    store.put_minted(intent.intent_id)
    store.consume(intent.intent_id)
    with pytest.raises(IntentError):
        store.claim(intent.intent_id)
