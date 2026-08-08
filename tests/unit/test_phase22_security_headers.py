"""Phase 0.22 SecurityPolicy header composition (HEADERS-022)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from hedron import Hedron, Page, Text
from hedron.security.policy import SecurityHeadersPolicy, SecurityPolicy


def test_headers_policy_overrides_csp_only() -> None:
    base = SecurityPolicy.from_name("standard")
    policy = SecurityPolicy(
        profile=base.profile,
        csrf_enabled=base.csrf_enabled,
        security_headers=SecurityHeadersPolicy(
            content_security_policy="default-src 'none'",
        ),
        content_security_policy=base.content_security_policy,
        frame_options=base.frame_options,
        content_type_options=base.content_type_options,
        referrer_policy=base.referrer_policy,
    )
    headers = policy.response_headers()
    assert headers["Content-Security-Policy"] == "default-src 'none'"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["Referrer-Policy"] == "no-referrer"


def test_security_headers_false_and_app_emit_no_security_headers() -> None:
    base = SecurityPolicy.from_name("standard")
    for mode in (False, "app"):
        policy = SecurityPolicy(
            profile=base.profile,
            security_headers=mode,  # type: ignore[arg-type]
            content_security_policy=base.content_security_policy,
        )
        headers = policy.response_headers()
        assert "Content-Security-Policy" not in headers
        assert "X-Frame-Options" not in headers
        assert "X-Content-Type-Options" not in headers
        assert "Referrer-Policy" not in headers


def test_hsts_override_emitted() -> None:
    policy = SecurityPolicy(
        security_headers=SecurityHeadersPolicy(hsts_max_age=31536000),
    )
    headers = policy.response_headers()
    assert headers["Strict-Transport-Security"] == "max-age=31536000"
    assert headers["X-Frame-Options"] == "DENY"


def test_fastapi_response_uses_merged_csp() -> None:
    base = SecurityPolicy.from_name("standard")
    policy = SecurityPolicy(
        profile=base.profile,
        csrf_enabled=True,
        security_headers=SecurityHeadersPolicy(
            content_security_policy="default-src 'self'; frame-src 'none'",
        ),
        content_security_policy=base.content_security_policy,
    )
    app = Hedron(title="headers-022", security=policy, explorer="off", session_secret="test")

    @app.page("/")
    def home() -> Page:
        return Page(Text("hi"), title="home")

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers.get("content-security-policy") == (
        "default-src 'self'; frame-src 'none'"
    )
    assert response.headers.get("x-frame-options") == "DENY"
