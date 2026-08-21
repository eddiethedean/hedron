"""CSP-055 evidence."""

from __future__ import annotations

import json

from hedron.csp import CspReporting, compose_csp, ingest_csp_report, new_nonce


def test_issue_545_nonce_and_bounded_redacted_reports() -> None:
    nonce = new_nonce()
    enforcing, report_only = compose_csp(
        "default-src 'self'",
        nonce=nonce.value,
        reporting=CspReporting(mode="enforcing", report_path="/hedron/csp-report"),
    )
    assert enforcing is not None
    assert f"nonce-{nonce.value}" in enforcing
    assert report_only is None

    body = json.dumps(
        {
            "csp-report": {
                "effective-directive": "script-src",
                "document-uri": "https://example/secret",
                "blocked-uri": "https://evil/x",
            }
        }
    ).encode()
    parsed = ingest_csp_report(
        body,
        content_type="application/csp-report",
        reporting=CspReporting(max_body_bytes=4096),
    )
    assert parsed is not None
    assert parsed["redacted"] is True
    assert "document-uri" not in parsed
    assert ingest_csp_report(b"x" * 20_000, content_type="application/json") is None
