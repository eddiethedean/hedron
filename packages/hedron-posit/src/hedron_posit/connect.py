"""Native Connect request helpers (base header / root_path contract)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from starlette.requests import Request

from hedron_core.diagnostics import DiagnosticSeverity, HedronError, make_diagnostic
from hedron_posit.products import PositProduct, connect_product_marker
from hedron_posit.urls import ExternalBase, connect_external_base_from_request

_DEFAULT_CONNECT_PROXY_PEERS: tuple[str, ...] = ()


def _connect_error(code: str, title: str, explanation: str, remediation: str) -> HedronError:
    return HedronError(
        make_diagnostic(
            code,
            severity=DiagnosticSeverity.ERROR,
            title=title,
            explanation=explanation,
            remediation=remediation,
        )
    )


def native_connect_base_from_request(
    request: Request,
    *,
    product: PositProduct,
    trusted_peers: Sequence[str] = _DEFAULT_CONNECT_PROXY_PEERS,
    environ: Mapping[str, str] | None = None,
) -> ExternalBase | None:
    """Validate Connect base header under resolved Connect product mode.

    Request cookies are never modified. Duplicate headers and base/root mismatches
    fail closed. Credential headers are not consumed.
    """
    try:
        base = connect_external_base_from_request(
            request,
            trusted_peers=trusted_peers,
            environ=environ,
        )
    except ValueError as exc:
        message = str(exc)
        code = (
            "HED-POSIT-0302"
            if product is PositProduct.CONNECT or connect_product_marker(environ) is not None
            else "HED-POSIT-0301"
        )
        if "multiple" in message:
            code = "HED-POSIT-0303"
        elif "does not match" in message:
            code = "HED-POSIT-0304"
        raise _connect_error(
            code,
            "Posit Connect base path validation failed",
            message,
            "Ensure exactly one RStudio-Connect-App-Base-URL matches ASGI root_path",
        ) from exc
    return base


__all__ = [
    "native_connect_base_from_request",
]
