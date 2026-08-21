"""CONFORM-056 evidence."""

from __future__ import annotations

from hedron_conformance.security import (
    HOST_DISPOSITIONS,
    SECURITY_PROFILE_VERSION,
    differential_summary,
    run_security_profile,
    security_profile_manifest,
)


def test_conform_056_profile_differential() -> None:
    manifest = security_profile_manifest()
    assert manifest["version"] == SECURITY_PROFILE_VERSION
    assert manifest["composition"] == "SecurityPolicy"
    results = run_security_profile(adapters=("fastapi", "flask", "django"))
    summary = differential_summary(results)
    assert summary["all_passed"]
    assert set(summary["by_invariant"]) >= {
        "csrf_before_handler",
        "context_isolation",
        "budget_before_body",
    }
    for adapter in ("fastapi", "flask", "django"):
        assert summary["by_invariant"]["csrf_before_handler"][adapter] is True
    assert "posit" in HOST_DISPOSITIONS
    assert HOST_DISPOSITIONS["notebook"]["streaming_body"] == "unsupported"
