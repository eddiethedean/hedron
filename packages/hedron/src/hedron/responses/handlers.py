"""Semantic HTMX HTML status responses vs framework-native JSON."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from hedron.htmx import approved_headers, is_htmx_request
from hedron.responses.render import render_component_response
from hedron_core.builtins.content import Text
from hedron_core.builtins.surfaces import Alert
from hedron_core.component import NodeLike
from hedron_core.html import html
from hedron_core.interaction import StatusPolicy, status_policy_for

__all__ = [
    "install_interaction_handlers",
    "semantic_error_fragment",
    "validation_error_fragment",
]


def validation_error_fragment(exc: RequestValidationError) -> NodeLike:
    items: list[NodeLike] = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err.get("loc", ()) if p != "body")
        msg = err.get("msg", "Invalid value")
        items.append(html.li(f"{loc}: {msg}" if loc else str(msg)))
    return html.div(
        Alert("Please correct the highlighted fields.", tone="danger"),
        html.ul(*items) if items else Text("Validation failed"),
        id="hedron-validation-errors",
        role="alert",
        **{"aria-live": "assertive"},
        class_="hedron-validation-errors",
    )


def semantic_error_fragment(status_code: int, detail: object = None) -> NodeLike:
    policy = status_policy_for(status_code)
    message = policy.message
    if detail is not None:
        message = f"{message}: {detail}" if message else str(detail)
    return html.div(
        Alert(message or f"HTTP {status_code}", tone="danger"),
        id="hedron-error-region",
        role="alert",
        **{"aria-live": "assertive"},
        class_="hedron-error-region",
    )


def _policy_headers(policy: StatusPolicy) -> dict[str, str]:
    if policy.no_swap:
        return approved_headers(reswap="none")
    if policy.retarget or policy.reswap or policy.swap:
        return approved_headers(
            retarget=policy.retarget,
            reswap=policy.reswap or policy.swap,
        )
    return {}


def install_interaction_handlers(app: FastAPI) -> None:
    """Register HTMX-aware exception handlers on a FastAPI/Hedron app."""

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(request: Request, exc: RequestValidationError) -> Response:
        if not is_htmx_request(request):
            return JSONResponse(status_code=422, content={"detail": exc.errors()})
        policy = status_policy_for(422)
        return render_component_response(
            validation_error_fragment(exc),
            request=request,
            status_code=422,
            extra_headers=_policy_headers(policy),
            authenticated=bool(getattr(request.state, "hedron_authenticated", False)),
            policy=getattr(request.app.state, "hedron_security", None),
            allow_undeclared_targets=True,
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_handler(request: Request, exc: StarletteHTTPException) -> Response:
        if not is_htmx_request(request):
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        if exc.status_code == 204:
            return Response(status_code=204, headers=_policy_headers(status_policy_for(204)))
        policy = status_policy_for(exc.status_code)
        return render_component_response(
            semantic_error_fragment(exc.status_code, exc.detail),
            request=request,
            status_code=exc.status_code,
            extra_headers=_policy_headers(policy),
            authenticated=bool(getattr(request.state, "hedron_authenticated", False)),
            policy=getattr(request.app.state, "hedron_security", None),
            allow_undeclared_targets=True,
        )
