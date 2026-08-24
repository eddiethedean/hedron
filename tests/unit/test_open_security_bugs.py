from types import SimpleNamespace

import pytest
from starlette.requests import Request
from starlette.responses import Response

from hedron.builtins.files import validate_upload_filename
from hedron.color_mode import apply_color_mode_cookie
from hedron_core._nodes import ElementNode
from hedron_core._serializer import serialize_node
from hedron_core.color_mode import ColorMode
from hedron_core.diagnostics import HedronError
from hedron_core.security import SafeUrl, Secret, UrlPurpose, redact_value
from hedron_core.uploads import validate_directory_upload
from hedron_mcp.server import AuthorizationError, McpProjection


def test_path_guards_normalize_unicode_and_allow_benign_double_dots() -> None:
    assert (
        SafeUrl.parse("/assets/foo..bar.png", purpose=UrlPurpose.ASSET).value
        == "/assets/foo..bar.png"
    )
    with pytest.raises(ValueError):
        validate_directory_upload([("．．/etc/passwd", 1)], max_files=5, max_total_size=100)
    with pytest.raises(AuthorizationError):
        McpProjection._assert_safe_uri("hedron://pages/．．/secret")


def test_upload_filename_rejects_nul() -> None:
    with pytest.raises(ValueError):
        validate_upload_filename("report.pdf\x00.exe")


def test_redact_value_handles_sets() -> None:
    redacted = redact_value({Secret("leak")})
    frozen = redact_value(frozenset({Secret("leak")}))
    assert redacted == {"***"}
    assert frozen == frozenset({"***"})


def test_serializer_rejects_mixed_case_event_handlers() -> None:
    with pytest.raises(HedronError, match="event handler"):
        serialize_node(
            ElementNode(tag="div", attributes={"oNclick": "alert(1)"}, children=(), void=False)
        )


def test_color_mode_cookie_honors_trusted_forwarded_https() -> None:
    app = SimpleNamespace(
        state=SimpleNamespace(
            hedron_cookie_path="/",
            hedron_security=SimpleNamespace(profile="standard"),
            hedron_trusted_peers={"10.0.0.2"},
        )
    )
    request = Request(
        {
            "type": "http",
            "scheme": "http",
            "path": "/",
            "headers": [(b"x-forwarded-proto", b"https")],
            "client": ("10.0.0.2", 443),
            "app": app,
        }
    )
    response = Response()
    apply_color_mode_cookie(response, ColorMode.DARK, request=request)
    assert "Secure" in response.headers["set-cookie"]
