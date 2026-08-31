"""Framework-neutral command services shared by Workbench CLIs."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, cast

from fastapi_workbench.redact import redact_record


@dataclass(frozen=True, slots=True)
class CheckResolution:
    """Result of the bind/discover/final-resolve command sequence."""

    value: Any
    bound_port: int | None
    discovered_raw: str | None


def deployment_payload(
    resolved: Any, *, status: Mapping[str, object] | None = None
) -> dict[str, object]:
    """Build the shared redacted deployment record used by both CLIs."""
    payload = redact_record(resolved.as_dict())
    if status is not None:
        payload["posit_status"] = redact_record(status)
    return payload


def deployment_text_lines(
    payload: Mapping[str, object], *, status: Mapping[str, object] | None = None
) -> list[str]:
    """Render common text fields while permitting a Posit status extension."""
    lines: list[str] = []
    if status is not None:
        for key in ("product", "evidence", "cookie_strategy", "bridge_enabled"):
            lines.append(f"{key}: {status.get(key)}")
    for key in (
        "mode",
        "bind",
        "external_origin",
        "browser_mount",
        "cookie_mount",
        "source",
        "discovered",
    ):
        lines.append(f"{key}: {payload[key]}")
    warnings = payload.get("warnings")
    if isinstance(warnings, list):
        lines.extend(f"warning: {warning}" for warning in cast(list[object], warnings))
    return lines


def resolve_check(
    *,
    host: str,
    port: int,
    discover: bool,
    discovery_available: bool,
    explicit_mount: Callable[[int | None], bool],
    bind: Callable[[str, int], Any],
    discover_url: Callable[[int], str],
    resolve: Callable[[int | None, str | None], Any],
) -> CheckResolution:
    """Bind before discovery, close reliably, then perform final resolution."""
    sock: Any | None = None
    bound_port: int | None = None
    discovered_raw: str | None = None
    try:
        if discover and discovery_available and not explicit_mount(port):
            bound_socket = bind(host, port)
            sock = bound_socket
            bound_port = int(bound_socket.getsockname()[1])
            discovered_raw = discover_url(bound_port)
        value = resolve(bound_port, discovered_raw)
        return CheckResolution(value, bound_port, discovered_raw)
    finally:
        if sock is not None:
            sock.close()


def normalize_cookie_path(path: str) -> str:
    """Normalize a cookie Path solely for exact mount comparison."""
    if not path or path == "/":
        return "/"
    return path.rstrip("/") or "/"


def parse_set_cookie_path(header: str) -> str | None:
    """Return the RFC 6265 Path attribute, or ``None`` when absent."""
    parts = header.split(";")
    for part in parts[1:]:
        name, sep, value = part.strip().partition("=")
        if not sep or name.lower() != "path":
            continue
        path = value.strip()
        if len(path) >= 2 and path[0] == path[-1] and path[0] in "\"'":
            path = path[1:-1]
        return path
    return None


def cookie_path_matches_mount(header: str, mount: str) -> bool:
    """Fail closed unless a cookie's explicit Path exactly matches the mount."""
    path = parse_set_cookie_path(header)
    return path is not None and normalize_cookie_path(path) == normalize_cookie_path(mount or "/")


_GENERATED_LOCAL_URL = re.compile(
    r'(?:href|src|action|hx-(?:get|post|put|patch|delete))="(/[^"]*)"'
)


def unmounted_generated_urls(html: str, mount: str) -> list[str]:
    """Return generated local URLs that escape the configured mount."""
    if not mount or not html:
        return []
    return sorted(
        {
            match.group(1)
            for match in _GENERATED_LOCAL_URL.finditer(html)
            if match.group(1) != mount and not match.group(1).startswith(mount + "/")
        }
    )


async def probe_asgi_app(
    app: Any,
    mount: str,
    *,
    extra_checks: Callable[[Any, list[str]], Mapping[str, object]] | None = None,
) -> dict[str, object]:
    """Run the common mounted-app probe and return its stable result schema."""
    import httpx

    target = f"{mount}/" if mount else "/"
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="https://doctor.invalid",
        follow_redirects=False,
    ) as client:
        response = await client.get(target)
    html = response.text if "text/html" in response.headers.get("content-type", "") else ""
    unmounted = unmounted_generated_urls(html, mount)
    cookie_headers = response.headers.get_list("set-cookie")
    result: dict[str, object] = {
        "target": target,
        "status": response.status_code,
        "reachable": response.status_code < 500,
        "unmounted_generated_urls": unmounted,
        "generated_urls_mounted": not unmounted,
        "cookie_paths_mounted": all(
            cookie_path_matches_mount(header, mount) for header in cookie_headers
        ),
    }
    if extra_checks is not None:
        result.update(extra_checks(response, cookie_headers))
    return result


def report_checks_ok(report: Mapping[str, object]) -> bool:
    """Evaluate booleans in a doctor report, including nested probe results."""
    if "error" in report:
        return False
    checks = report.get("checks")
    if not isinstance(checks, Mapping):
        return False
    check_values = cast(Mapping[object, object], checks)
    for value in check_values.values():
        if isinstance(value, bool) and not value:
            return False
        if isinstance(value, Mapping):
            nested_checks = cast(Mapping[object, object], value)
            if any(isinstance(nested, bool) and not nested for nested in nested_checks.values()):
                return False
    return True


__all__ = [
    "CheckResolution",
    "cookie_path_matches_mount",
    "deployment_payload",
    "deployment_text_lines",
    "normalize_cookie_path",
    "parse_set_cookie_path",
    "probe_asgi_app",
    "report_checks_ok",
    "resolve_check",
    "unmounted_generated_urls",
]
