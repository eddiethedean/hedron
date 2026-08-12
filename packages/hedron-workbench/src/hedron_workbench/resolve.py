"""Side-effect-free Workbench configuration resolution."""

from __future__ import annotations

import ipaddress
import os
import re
from collections.abc import Mapping
from urllib.parse import SplitResult, urlsplit

from hedron.mount import cookie_path_for_mount, normalize_mount_path
from hedron_core.codes import HED_WB_0001, HED_WB_0002
from hedron_core.diagnostics import DiagnosticSeverity, HedronError, make_diagnostic
from hedron_workbench.config import (
    DEFAULT_FORWARDED_ALLOW_IPS,
    DEFAULT_HOST,
    DEFAULT_RSERVER_URL,
    ResolvedDeployment,
    WorkbenchConfig,
    WorkbenchMode,
)
from hedron_workbench.detect import is_workbench_forced, rs_server_url, truthy

_PROXY_ROOT = re.compile(r"^/proxy/(?P<port>\d+)(?P<rest>/.*)$")
_MAX_RSERVER_OUTPUT = 4096
_ALIAS_USED = "HED-WB-0008"

_ENV_MODE = "HEDRON_WORKBENCH_MODE"
_ENV_HOST = "HEDRON_WORKBENCH_HOST"
_ENV_PORT = "HEDRON_WORKBENCH_PORT"
_ENV_MOUNT = "HEDRON_WORKBENCH_MOUNT"
_ENV_PUBLIC = "HEDRON_WORKBENCH_PUBLIC_BASE_URL"
_ENV_BIN = "HEDRON_WORKBENCH_RSERVER_URL"
_ENV_DEBUG = "HEDRON_WORKBENCH_DEBUG"
_ENV_RELOAD = "HEDRON_WORKBENCH_RELOAD"
_ENV_WORKERS = "HEDRON_WORKBENCH_WORKERS"
_ENV_OPEN = "HEDRON_WORKBENCH_OPEN_BROWSER"
_ENV_FORWARD = "HEDRON_WORKBENCH_FORWARDED_ALLOW_IPS"
_ENV_ALLOW_EXTERNAL = "HEDRON_WORKBENCH_ALLOW_EXTERNAL_BIND"

# Launcher-only handoff. These are exported after the listener is bound and
# rserver-url has been resolved, then consumed by HedronWorkbench at import.
RESOLVED_MOUNT_ENV = "HEDRON_WORKBENCH_RESOLVED_MOUNT"
RESOLVED_PUBLIC_BASE_ENV = "HEDRON_WORKBENCH_RESOLVED_PUBLIC_BASE"
RESOLVED_MODE_ENV = "HEDRON_WORKBENCH_RESOLVED_MODE"
RESOLVED_SOURCE_ENV = "HEDRON_WORKBENCH_RESOLVED_SOURCE"


def _error(*, title: str, explanation: str, remediation: str) -> HedronError:
    return HedronError(
        make_diagnostic(
            HED_WB_0001,
            severity=DiagnosticSeverity.ERROR,
            title=title,
            explanation=explanation,
            remediation=remediation,
        )
    )


def _warn_alias(name: str) -> str:
    return f"{_ALIAS_USED}: deprecated alias {name} used; prefer HEDRON_WORKBENCH_*"


def _first_str(
    *,
    explicit: str | None,
    namespaced: str | None,
    resolved: str | None = None,
    alias: str | None,
    alias_name: str | None,
    warnings: list[str],
) -> str | None:
    if explicit is not None and str(explicit).strip():
        return str(explicit).strip()
    if namespaced is not None and str(namespaced).strip():
        return str(namespaced).strip()
    if resolved is not None and str(resolved).strip():
        return str(resolved).strip()
    if alias is not None and str(alias).strip():
        if alias_name:
            warnings.append(_warn_alias(alias_name))
        return str(alias).strip()
    return None


def _parse_port(raw: str | int | None, *, name: str = "port") -> int | None:
    if raw is None or not str(raw).strip():
        return None
    try:
        port = int(str(raw).strip())
    except ValueError as exc:
        raise _error(
            title="Invalid Workbench port",
            explanation=f"{name} value {raw!r} is not an integer.",
            remediation="Set the port to 0–65535; 0 requests an ephemeral listener.",
        ) from exc
    if port < 0 or port > 65535:
        raise _error(
            title="Invalid Workbench port",
            explanation=f"{name} {port} is out of range.",
            remediation="Set the port to 0–65535; 0 requests an ephemeral listener.",
        )
    return port


def _parse_workers(raw: str | int | None) -> int:
    if raw is None or not str(raw).strip():
        return 1
    try:
        workers = int(str(raw).strip())
    except ValueError as exc:
        raise _error(
            title="Invalid Workbench worker count",
            explanation=f"workers value {raw!r} is not an integer.",
            remediation="Use one worker; the pre-bound Workbench launcher is single-process.",
        ) from exc
    if workers < 1:
        raise _error(
            title="Invalid Workbench worker count",
            explanation=f"workers must be at least 1, got {workers}.",
            remediation="Use one worker; multi-worker launch is not supported by this runner.",
        )
    return workers


def _validated_mount(raw: str, *, source: str) -> str:
    normalized = normalize_mount_path(raw)
    text = str(raw).strip()
    if normalized or text in {"", "/"}:
        return normalized
    raise _error(
        title="Invalid Workbench mount",
        explanation=f"{source} did not resolve to a safe local mount path.",
        remediation="Use '/' or an absolute path without URLs, traversal, whitespace, or '//'.",
    )


def _validated_public_base(raw: str) -> tuple[str | None, str, SplitResult | None]:
    text = str(raw).strip()
    parsed = urlsplit(text)
    looks_like_url = bool(parsed.scheme or parsed.netloc or text.startswith("//") or "://" in text)
    if not looks_like_url:
        return None, _validated_mount(text, source="public base path"), None
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise _error(
            title="Invalid Workbench public base URL",
            explanation="Public base URLs must use http or https and include a host.",
            remediation="Set a full http(s) URL or a local absolute mount path.",
        )
    if parsed.username or parsed.password or parsed.fragment or parsed.query:
        raise _error(
            title="Unsafe Workbench public base URL",
            explanation="Credentials, query strings, and fragments are not accepted.",
            remediation="Configure credentials separately and provide only origin plus mount path.",
        )
    mount = _validated_mount(parsed.path or "/", source="public base URL path")
    return f"{parsed.scheme}://{parsed.netloc}", mount, parsed


def _validate_host(host: str, *, allow_external: bool) -> str:
    value = str(host).strip()
    if not value:
        return DEFAULT_HOST
    if allow_external or value.lower() == "localhost":
        return value
    try:
        address = ipaddress.ip_address(value)
    except ValueError as exc:
        raise _error(
            title="Workbench listener must be loopback",
            explanation=f"Host {value!r} is not a literal loopback address.",
            remediation=(
                "Use 127.0.0.1/::1, or explicitly enable allow_external_bind after review."
            ),
        ) from exc
    if not address.is_loopback:
        raise _error(
            title="Workbench listener must be loopback",
            explanation=f"Host {value!r} is externally reachable.",
            remediation=(
                "Use a loopback address, or explicitly enable allow_external_bind after review."
            ),
        )
    return value


def _validate_forwarded_allow_ips(raw: str | None) -> str:
    value = str(raw or DEFAULT_FORWARDED_ALLOW_IPS).strip()
    entries = [entry.strip() for entry in value.split(",") if entry.strip()]
    if not entries:
        return DEFAULT_FORWARDED_ALLOW_IPS
    for entry in entries:
        if entry == "*":
            raise _error(
                title="Unsafe forwarded proxy allowlist",
                explanation="Wildcard forwarded proxy trust is not accepted by hedron-workbench.",
                remediation="List the exact proxy IP addresses that connect to Uvicorn.",
            )
        try:
            ipaddress.ip_address(entry)
        except ValueError as exc:
            raise _error(
                title="Invalid forwarded proxy allowlist",
                explanation=f"Proxy entry {entry!r} is not an IP address.",
                remediation="Use a comma-separated list such as '127.0.0.1,::1'.",
            ) from exc
    return ",".join(entries)


def parse_rserver_url_output(raw: str, *, port: int) -> tuple[str, str, str]:
    """Return ``(browser_mount, external_origin, source)`` from rserver-url stdout."""
    text = raw or ""
    if len(text) > _MAX_RSERVER_OUTPUT:
        raise HedronError(
            make_diagnostic(
                HED_WB_0002,
                severity=DiagnosticSeverity.ERROR,
                title="rserver-url output too large",
                explanation="Discovery output exceeded the bounded size.",
                remediation="Inspect the rserver-url binary; do not pipe untrusted data.",
            )
        )
    if any(ord(char) < 32 or ord(char) == 127 for char in text):
        raise HedronError(
            make_diagnostic(
                HED_WB_0002,
                severity=DiagnosticSeverity.ERROR,
                title="Malformed rserver-url output",
                explanation="Discovery output contained control characters or multiple lines.",
                remediation="Use the official rserver-url binary and capture stdout only.",
            )
        )
    text = text.strip()
    if not text:
        raise HedronError(
            make_diagnostic(
                HED_WB_0002,
                severity=DiagnosticSeverity.ERROR,
                title="Empty rserver-url output",
                explanation="Discovery produced no path or URL.",
                remediation="Confirm the session is running and rserver-url -l <port> works.",
            )
        )
    if text.startswith(("http://", "https://")):
        parsed = urlsplit(text)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise HedronError(
                make_diagnostic(
                    HED_WB_0002,
                    severity=DiagnosticSeverity.ERROR,
                    title="Invalid rserver-url URL",
                    explanation="Full-URL discovery must be http(s) with a host.",
                    remediation="Reject the output and fail closed.",
                )
            )
        if parsed.username or parsed.password or parsed.fragment:
            raise HedronError(
                make_diagnostic(
                    HED_WB_0002,
                    severity=DiagnosticSeverity.ERROR,
                    title="Unsafe rserver-url URL",
                    explanation="Credentials and fragments are not accepted.",
                    remediation="Use rserver-url without embedding secrets.",
                )
            )
        mount = _canonicalize_discovered_mount(parsed.path)
        return mount, f"{parsed.scheme}://{parsed.netloc}", "rserver-url:full-url"
    if "://" in text.split("/", 1)[0] or text.startswith("//"):
        raise HedronError(
            make_diagnostic(
                HED_WB_0002,
                severity=DiagnosticSeverity.ERROR,
                title="Rejected rserver-url output",
                explanation="Protocol-relative or unknown-scheme discovery is not accepted.",
                remediation="Expect a path or http(s) URL from rserver-url.",
            )
        )
    mount = _canonicalize_discovered_mount(text)
    return mount, f"http://{DEFAULT_HOST}:{port}", "rserver-url:path"


def _canonicalize_discovered_mount(path: str) -> str:
    mount = normalize_mount_path(path)
    match = _PROXY_ROOT.match(mount)
    if match:
        mount = normalize_mount_path((match.group("rest") or "").rstrip("/"))
    if not mount:
        raise HedronError(
            make_diagnostic(
                HED_WB_0002,
                severity=DiagnosticSeverity.ERROR,
                title="Rejected rserver-url mount",
                explanation="Discovered path failed Hedron mount sanitization.",
                remediation="Do not concatenate untrusted prefixes; fail closed.",
            )
        )
    return mount


def resolve_deployment(
    config: WorkbenchConfig | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    bound_port: int | None = None,
    discovered_raw: str | None = None,
    compatibility_aliases: bool = True,
) -> ResolvedDeployment:
    """Pure resolution. Does not import an app, bind a socket, or exec a binary."""
    cfg = config or WorkbenchConfig()
    env = os.environ if environ is None else environ
    warnings: list[str] = []

    mode_raw = _first_str(
        explicit=cfg.mode.value if cfg.mode is not WorkbenchMode.AUTO else None,
        namespaced=env.get(_ENV_MODE),
        resolved=env.get(RESOLVED_MODE_ENV),
        alias=None,
        alias_name=None,
        warnings=warnings,
    )
    try:
        mode = WorkbenchMode.parse(mode_raw)
    except ValueError as exc:
        raise _error(
            title="Invalid Workbench mode",
            explanation=str(exc),
            remediation="Use auto, on, or off.",
        ) from exc

    allow_external = cfg.allow_external_bind or truthy(env.get(_ENV_ALLOW_EXTERNAL))
    host_raw = _first_str(
        explicit=cfg.host,
        namespaced=env.get(_ENV_HOST),
        alias=env.get("HOST") if compatibility_aliases else None,
        alias_name="HOST",
        warnings=warnings,
    )
    host = _validate_host(host_raw or DEFAULT_HOST, allow_external=allow_external)

    if cfg.port is not None:
        port = _parse_port(cfg.port, name="config port")
    elif env.get(_ENV_PORT) is not None:
        port = _parse_port(env.get(_ENV_PORT), name=_ENV_PORT)
    elif compatibility_aliases and env.get("PORT") is not None:
        warnings.append(_warn_alias("PORT"))
        port = _parse_port(env.get("PORT"), name="PORT")
    else:
        port = _parse_port(bound_port, name="bound port") or 0

    mount_explicit = _first_str(
        explicit=cfg.mount,
        namespaced=env.get(_ENV_MOUNT),
        resolved=env.get(RESOLVED_MOUNT_ENV),
        alias=env.get("BASE_PATH") if compatibility_aliases else None,
        alias_name="BASE_PATH",
        warnings=warnings,
    )
    public_explicit = _first_str(
        explicit=cfg.public_base_url,
        namespaced=env.get(_ENV_PUBLIC),
        resolved=env.get(RESOLVED_PUBLIC_BASE_ENV),
        alias=env.get("PUBLIC_BASE_URL") if compatibility_aliases else None,
        alias_name="PUBLIC_BASE_URL",
        warnings=warnings,
    )

    legacy_debug = truthy(env.get("WORKBENCH_DEBUG")) if compatibility_aliases else False
    debug = cfg.debug or truthy(env.get(_ENV_DEBUG)) or legacy_debug
    if legacy_debug and not truthy(env.get(_ENV_DEBUG)) and not cfg.debug:
        warnings.append(_warn_alias("WORKBENCH_DEBUG"))
    reload = (
        cfg.reload
        or truthy(env.get(_ENV_RELOAD))
        or (truthy(env.get("RELOAD")) if compatibility_aliases else False)
    )
    workers = (
        _parse_workers(cfg.workers) if cfg.workers != 1 else _parse_workers(env.get(_ENV_WORKERS))
    )
    open_browser = cfg.open_browser or truthy(env.get(_ENV_OPEN))

    proxy_alias = env.get("HEDRON_TRUSTED_PROXIES")
    proxy_alias_name: str | None = None
    if proxy_alias is None and compatibility_aliases:
        proxy_alias = env.get("FORWARDED_ALLOW_IPS")
        proxy_alias_name = "FORWARDED_ALLOW_IPS" if proxy_alias is not None else None
    forwarded_raw = _first_str(
        explicit=cfg.forwarded_allow_ips,
        namespaced=env.get(_ENV_FORWARD),
        alias=proxy_alias,
        alias_name=proxy_alias_name,
        warnings=warnings,
    )
    forwarded = _validate_forwarded_allow_ips(forwarded_raw)

    configured_bin = cfg.rserver_url_bin if cfg.rserver_url_bin != DEFAULT_RSERVER_URL else None
    bin_path = str(env.get(_ENV_BIN) or configured_bin or DEFAULT_RSERVER_URL).strip()

    discovered = False
    source = "default"
    forced = (
        is_workbench_forced(env)
        if compatibility_aliases
        else truthy(env.get("HEDRON_WORKBENCH_FORCE"))
    )
    active = mode is WorkbenchMode.ON or forced
    browser_mount = ""
    external_origin = f"http://{host}:{port}" if port else f"http://{host}"

    public_origin: str | None = None
    public_mount = ""
    public_parsed: SplitResult | None = None
    if public_explicit is not None:
        public_origin, public_mount, public_parsed = _validated_public_base(public_explicit)

    if mount_explicit is not None:
        browser_mount = _validated_mount(mount_explicit, source="explicit Workbench mount")
        source = (
            str(env.get(RESOLVED_SOURCE_ENV) or "launcher:resolved")
            if env.get(RESOLVED_MOUNT_ENV) and cfg.mount is None and not env.get(_ENV_MOUNT)
            else "explicit:mount"
        )
        active = True
        if public_explicit is not None:
            if (
                public_mount
                and browser_mount != public_mount
                and not public_mount.endswith(browser_mount)
            ):
                raise _error(
                    title="Conflicting Workbench mount and origin",
                    explanation="Explicit mount and public base path disagree.",
                    remediation="Set one source; do not concatenate conflicting prefixes.",
                )
            if public_origin:
                external_origin = public_origin
    elif discovered_raw is not None:
        browser_mount, origin, source = parse_rserver_url_output(discovered_raw, port=port or 1)
        discovered = True
        active = True
        if public_origin:
            discovered_netloc = urlsplit(origin).netloc.lower()
            assert public_parsed is not None
            if public_parsed.netloc.lower() != discovered_netloc:
                raise _error(
                    title="Conflicting Workbench origin",
                    explanation="Explicit public base disagrees with rserver-url.",
                    remediation="Unset PUBLIC_BASE_URL or HEDRON_WORKBENCH_PUBLIC_BASE_URL.",
                )
            external_origin = public_origin
        else:
            external_origin = origin
    elif public_explicit is not None:
        external_origin = public_origin or external_origin
        browser_mount = public_mount
        source = (
            str(env.get(RESOLVED_SOURCE_ENV) or "launcher:resolved")
            if env.get(RESOLVED_PUBLIC_BASE_ENV) and cfg.public_base_url is None
            else "explicit:public_base"
        )
        active = True

    if forced and mode is WorkbenchMode.AUTO:
        warnings.append(
            "WORKBENCH_FORCE requests local reproduction; RS_SERVER_URL still does not grant trust"
        )

    if mode is WorkbenchMode.OFF:
        browser_mount = ""
        source = "mode:off"
        discovered = False
        active = False

    if rs_server_url(env) and not discovered and discovered_raw is None and mount_explicit is None:
        source = "rs_server_url:pending" if source == "default" else source

    return ResolvedDeployment(
        mode=mode,
        host=host,
        port=port or 0,
        bind=f"{host}:{port or 0}",
        external_origin=external_origin,
        browser_mount=browser_mount,
        cookie_mount=cookie_path_for_mount(browser_mount),
        source=source,
        active=active,
        warnings=tuple(warnings),
        discovered=discovered,
        rserver_url_bin=bin_path,
        forwarded_allow_ips=forwarded,
        reload=reload,
        workers=workers,
        open_browser=open_browser,
        debug=debug,
        factory=cfg.factory,
        app_target=cfg.app_target,
    )
