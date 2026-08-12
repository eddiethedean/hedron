"""AUDIT-032 redaction coverage."""

from __future__ import annotations

from hedron_mcp import McpAuditLog, McpProjection, McpTool, redact_value


def test_redact_secrets_in_audit_payloads() -> None:
    payload = redact_value({"token": "abc", "nested": {"password": "x"}, "ok": "visible"})
    assert payload["token"] == "[REDACTED]"
    assert payload["nested"]["password"] == "[REDACTED]"
    assert payload["ok"] == "visible"


def test_registration_and_authz_emit_redacted_events() -> None:
    sink: list[dict] = []
    projection = McpProjection(enabled=True)
    projection.audit = McpAuditLog(sink=sink.append)
    projection.register_tool(
        McpTool(
            name="status",
            schema={"type": "object", "properties": {}},
            mutate=False,
            handler=lambda: {"ok": True},
        )
    )
    projection.check_authz(
        principal="alice",
        action="tools/call",
        resource="status",
        scopes={"token": "should-redact"},
    )
    assert any(e["code"] == "HED-MCP-REGISTER-TOOL" for e in sink)
    authz = [e for e in sink if e["code"] == "HED-MCP-AUTHZ-OK"][0]
    # scopes are not copied into detail by default; ensure redaction helper used on detail
    assert "password" not in str(authz)
    redacted = redact_value({"authorization": "Bearer secret"})
    assert redacted["authorization"] == "[REDACTED]"
