"""Bounded Explorer laboratory: simulate, click-preview, element-simulate."""

from __future__ import annotations

import logging
from typing import Any, cast

from fastapi import Request
from fastapi.responses import JSONResponse

from hedron_core.registry import RouteMeta, get_registry
from hedron_core.typing_aliases import JsonObject
from hedron_explorer.services.runtime import TRACE

_logger = logging.getLogger("hedron.explorer")

SIMULATE_KEYS = frozenset(
    {
        "route",
        "allow_mutations",
        "mode",
        "target",
        "boosted",
        "history_restore",
        "status",
    }
)
_SIMULATE_KEYS = SIMULATE_KEYS
ELEMENT_FAILURES = frozenset({"none", "module", "upgrade"})


def parse_regions(inference: dict[str, Any]) -> dict[str, str]:
    regions_raw = inference.get("fragment_regions") or ""
    regions: dict[str, str] = {}
    if isinstance(regions_raw, dict):
        return {str(k): str(v) for k, v in regions_raw.items()}
    if isinstance(regions_raw, str) and regions_raw.startswith("{"):
        import ast

        try:
            parsed = ast.literal_eval(regions_raw)
        except (SyntaxError, ValueError):
            parsed = {}
        if isinstance(parsed, dict):
            regions = {str(k): str(v) for k, v in parsed.items()}
    return regions


async def require_csrf(request: Request) -> JSONResponse | None:
    policy = getattr(request.app.state, "hedron_security", None)
    if policy is None:
        return JSONResponse(
            {"detail": "CSRF policy required for simulate"},
            status_code=403,
        )
    from hedron_core.csrf import validate_double_submit

    strategy = None
    resolve = getattr(policy, "resolve_csrf_strategy", None)
    if callable(resolve):
        try:
            strategy = resolve()
        except Exception as exc:  # noqa: BLE001
            _logger.warning("CSRF strategy resolve failed: %s", exc)
            return JSONResponse(
                {"detail": f"CSRF strategy resolve failed: {exc}"},
                status_code=403,
            )
    csrf_name = (
        getattr(strategy, "cookie_name", None)
        or getattr(policy, "csrf_cookie_name", None)
        or "hedron_csrf"
    )
    cookie = request.cookies.get(csrf_name)
    header_name = (
        getattr(strategy, "header_name", None)
        or getattr(policy, "csrf_header_name", None)
        or "X-CSRF-Token"
    )
    header = (
        request.headers.get(header_name)
        or request.headers.get("X-CSRF-Token")
        or request.headers.get("X-Hedron-CSRF")
    )
    form_token = None
    if strategy is None:
        if not validate_double_submit(
            cookie_token=cookie, header_token=header, form_token=form_token
        ):
            return JSONResponse({"detail": "CSRF validation failed"}, status_code=403)
        return None
    validator = getattr(request.app.state, "hedron_csrf_validate", None)
    if callable(validator):
        try:
            result = validator(request, policy)
            if hasattr(result, "__await__"):
                result = await result  # type: ignore[misc]
        except Exception as exc:  # noqa: BLE001
            _logger.warning("CSRF validation raised: %s", exc)
            return JSONResponse({"detail": "CSRF validation failed"}, status_code=403)
        if result is not None and not result:
            return JSONResponse({"detail": "CSRF validation failed"}, status_code=403)
        return None
    if not validate_double_submit(cookie_token=cookie, header_token=header, form_token=form_token):
        return JSONResponse({"detail": "CSRF validation failed"}, status_code=403)
    return None


def click_preview_payload(route: RouteMeta, *, target: str | None) -> dict[str, Any]:
    inference = dict(getattr(route, "htmx_inference", {}) or {})
    regions = parse_regions(inference)
    methods = tuple(route.methods or ("GET",))
    csrf_required = inference.get("csrf_required")
    if csrf_required is None:
        csrf_required = any(m.upper() not in {"GET", "HEAD", "OPTIONS"} for m in methods)
    else:
        csrf_required = str(csrf_required).lower() in {"1", "true", "yes"}
    return {
        "method": methods[0],
        "path": route.path,
        "target": target,
        "swap": str(inference.get("swap") or "outerHTML"),
        "csrf_required": bool(csrf_required),
        "declared_regions": [
            {"id": rid, "selector": value.split("|", 1)[0]} for rid, value in regions.items()
        ],
    }


async def simulate(request: Request) -> Any:
    try:
        payload = await request.json()
    except Exception as exc:  # noqa: BLE001
        _logger.debug("simulate: invalid JSON body: %s", exc)
        return JSONResponse({"detail": "Invalid JSON body"}, status_code=400)
    if not isinstance(payload, dict):
        return JSONResponse({"detail": "JSON object required"}, status_code=400)
    unknown = set(payload) - SIMULATE_KEYS
    if unknown:
        return JSONResponse(
            {"detail": f"Unknown keys: {', '.join(sorted(unknown))}"},
            status_code=400,
        )
    if payload.get("allow_mutations"):
        return JSONResponse(
            {"detail": "Mutation simulation is disabled by default"},
            status_code=403,
        )
    csrf_error = await require_csrf(request)
    if csrf_error is not None:
        return csrf_error
    name = payload.get("route")
    if not isinstance(name, str) or not name:
        return JSONResponse({"detail": "route is required"}, status_code=400)
    routes = {r.name: r for r in get_registry().routes()}
    if name not in routes:
        return JSONResponse(
            {"detail": "Unregistered route identifier"},
            status_code=400,
        )
    TRACE.appendleft({"kind": "simulate", "route": name, "mutations": False})
    mode = str(payload.get("mode") or "fragment")
    route = routes[name]
    inference = dict(getattr(route, "htmx_inference", {}) or {})
    status_raw = payload.get("status")
    if status_raw is None or status_raw == "":
        status_code = 200
    else:
        try:
            status_code = int(status_raw)
        except (TypeError, ValueError):
            return JSONResponse({"detail": "status must be an integer"}, status_code=400)
    target = payload.get("target")
    regions = parse_regions(inference)
    region_ok = True
    region_error = None
    if target:
        if not regions:
            region_ok = False
            region_error = f"HX-Target {target!r} is not an authorized fragment region"
        else:
            region_ok = any(target == value.split("|", 1)[0] for _rid, value in regions.items())
            if not region_ok:
                region_error = f"HX-Target {target!r} is not an authorized fragment region"
    swap = str(inference.get("swap") or "outerHTML")
    click_preview = click_preview_payload(route, target=target if isinstance(target, str) else None)
    return cast(
        JsonObject,
        {
            "ok": region_ok,
            "route": name,
            "mutations": False,
            "mode": mode,
            "boosted": bool(payload.get("boosted")),
            "history_restore": bool(payload.get("history_restore")),
            "status": status_code,
            "target": target,
            "primary": {
                "kind": route.kind,
                "path": route.path,
                "swap": swap,
            },
            "oob": [],
            "event_timing": {"trigger": None, "after_swap": None, "after_settle": None},
            "history": "push" if mode in {"boosted", "page"} else "none",
            "assets": "predeclared-shell",
            "cache_variation": ["HX-Request", "HX-History-Restore-Request"]
            + (["HX-Target"] if inference.get("fragment_regions") else []),
            "inference": inference,
            "override_source": "route.htmx_inference",
            "error": region_error,
            "click_preview": click_preview,
        },
    )


async def click_preview(request: Request) -> Any:
    name = request.query_params.get("route")
    target = request.query_params.get("target")
    if not name:
        return JSONResponse({"detail": "route query parameter is required"}, status_code=400)
    routes = {r.name: r for r in get_registry().routes()}
    if name not in routes:
        return JSONResponse({"detail": "Unregistered route identifier"}, status_code=400)
    return cast(JsonObject, {"click_preview": click_preview_payload(routes[name], target=target)})


async def element_simulate(request: Request) -> Any:
    csrf_error = await require_csrf(request)
    if csrf_error is not None:
        return csrf_error
    try:
        payload = await request.json()
    except Exception as exc:  # noqa: BLE001
        _logger.debug("element_simulate: invalid JSON body: %s", exc)
        return JSONResponse({"detail": "Invalid JSON body"}, status_code=400)
    if not isinstance(payload, dict):
        return JSONResponse({"detail": "JSON object required"}, status_code=400)
    logical_id = payload.get("logical_id")
    failure = payload.get("failure", "none")
    if not isinstance(logical_id, str) or not logical_id:
        return JSONResponse({"detail": "logical_id required"}, status_code=400)
    if failure not in ELEMENT_FAILURES:
        return JSONResponse({"detail": "failure must be none|module|upgrade"}, status_code=400)
    meta = get_registry().get_element_definition(logical_id)
    if meta is None:
        return JSONResponse({"detail": "Element not found"}, status_code=404)
    behavior = {
        "none": meta.fallback.get("pre_upgrade", "server content visible"),
        "module": meta.fallback.get("module_failure", "retain server content"),
        "upgrade": meta.fallback.get("js_off", "server content visible"),
    }[failure]
    return {
        "logical_id": meta.logical_id,
        "tag_name": meta.tag_name,
        "failure": failure,
        "fallback": behavior,
        "declared_fallback": dict(meta.fallback),
    }


def redacted_app_scenario(*, route: str, ok: bool) -> dict[str, Any]:
    """Redacted AppScenario snippet for laboratory export. No invented auth."""
    return {
        "kind": "AppScenario",
        "route": route,
        "ok": ok,
        "auth": None,
        "redacted": True,
        "allow_mutations": False,
    }
