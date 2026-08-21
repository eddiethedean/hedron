"""REGRESS-056 evidence."""

from __future__ import annotations

from hedron.workflow import WorkflowBudget, WorkflowManifest
from hedron_core.security import SafeUrl, Secret, TrustedHtml, UrlPurpose
from hedron_core.security_plane import EgressError, SecurityPolicy, assert_ssrf_safe


def test_regress_056_055_compatibility() -> None:
    # 0.55 workflow inspection still works.
    manifest = WorkflowManifest(
        layout_regions=("master", "detail"),
        capabilities=("items.edit",),
        budgets=WorkflowBudget(body_bytes=1024),
    )
    assert "reason_codes" in manifest.redacted_dict()
    # Prior trust types still usable and compatible with control plane presets.
    policy = SecurityPolicy.from_name("standard")
    assert policy.csrf_enabled is True
    assert str(SafeUrl.parse("/ok", purpose=UrlPurpose.NAVIGATION))
    assert str(TrustedHtml.reviewed("<i>x</i>", source="test"))
    assert "secret" not in repr(Secret("secret-value")).lower() or "***" in repr(Secret("x"))
    # Compatibility egress helper remains fail-closed on loopback.
    try:
        assert_ssrf_safe("http://localhost/x")
        raised = False
    except EgressError:
        raised = True
    assert raised
