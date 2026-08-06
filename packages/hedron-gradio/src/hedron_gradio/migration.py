"""Gradio migration inventory and diagnostics (MIGRATE-018)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

GRADIO_NON_PARITY: tuple[str, ...] = (
    "mutable globals as app state",
    "default-public UI API publication",
    "raw JS injection on server events",
    "raw HTML templates with untrusted interpolation",
    "current-working-directory file exposure",
    "temporary public share links and tunnels",
    "deployed host-code editing (vibe mode)",
    "embedding Gradio UI runtime in hedron-core",
    "treating feedback/flagging as ground truth",
    "browser Python with server process access",
    "community component installation without review",
)

_SHARE_LINK_MARKERS = ("share", "share_link", "public_tunnel", "gradio.live")
_RAW_JS_MARKERS = ("raw_js", "raw_javascript", "js_injection", "custom_js")


def diagnose(app_description: Mapping[str, Any]) -> list[str]:
    """Return reviewable migration findings for a Gradio app description."""
    findings: list[str] = []

    for item in GRADIO_NON_PARITY:
        findings.append(f"non-parity: {item}")

    flags = {str(key).lower() for key in app_description}
    values = " ".join(str(value).lower() for value in app_description.values())

    if flags.intersection(_SHARE_LINK_MARKERS) or "share link" in values:
        findings.append(
            "share links: temporary public tunnels are deliberate non-parity; "
            "use documented development tunnels with exposure warnings"
        )

    if flags.intersection(_RAW_JS_MARKERS) or "raw js" in values or "javascript" in values:
        findings.append(
            "raw js: server-attached JavaScript strings are deliberate non-parity; "
            "use Hedron typed events and scoped assets instead"
        )

    if app_description.get("api_visibility") == "default_public":
        findings.append(
            "api visibility: default-public UI APIs are deliberate non-parity; "
            "register explicit actions per subgraph"
        )

    if app_description.get("file_root") in {".", "cwd", "current_directory"}:
        findings.append(
            "file paths: cwd-as-public-root is deliberate non-parity; "
            "use explicit upload/download roots with authorization"
        )

    return findings
