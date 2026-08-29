"""HTMX attribute eval policy shared by Python ``html.*`` and HDJ parity."""

from __future__ import annotations

import contextlib
import contextvars
import re
from collections.abc import Generator

from hedron_core.security.urls import nfkc_strip_format

# Matches HDJ ``_HX_JS_VALUE_RE`` in hedron_jinja.source.
_HX_JS_VALUE_RE = re.compile(r"(?:^|[\s,{])js\s*:", re.I)
_HX_EVAL_VALUE_ATTRS = frozenset({"hx-vals", "hx-headers"})
_HX_URL_ATTR_SUFFIXES = frozenset(
    {
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "push-url",
        "replace-url",
    }
)


def canonical_hx_attribute(attribute: str) -> str:
    """Map ``data-hx-*`` aliases to canonical ``hx-*`` names (#230)."""
    lower = attribute.lower()
    if lower.startswith("data-hx-"):
        return "hx-" + lower[8:]
    return lower


_allow_htmx_eval: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "hedron_allow_htmx_eval", default=False
)


def htmx_eval_allowed() -> bool:
    """Return whether ``js:`` values on ``hx-vals`` / ``hx-headers`` are permitted."""
    return _allow_htmx_eval.get()


def set_htmx_eval_allowed(allowed: bool) -> contextvars.Token[bool]:
    """Set the process/context flag; prefer :func:`allow_htmx_eval` in application code."""
    return _allow_htmx_eval.set(allowed)


def reset_htmx_eval_allowed(token: contextvars.Token[bool]) -> None:
    """Reset the flag after :func:`set_htmx_eval_allowed`."""
    _allow_htmx_eval.reset(token)


@contextlib.contextmanager
def allow_htmx_eval(enabled: bool = True) -> Generator[None, None, None]:
    """Temporarily allow (or deny) ``js:`` on ``hx-vals`` / ``hx-headers`` (HDJ ``htmx.eval``)."""
    token = _allow_htmx_eval.set(enabled)
    try:
        yield
    finally:
        _allow_htmx_eval.reset(token)


def hx_value_needs_eval(attribute: str, value: object) -> bool:
    """True when an HTMX attribute value requires the ``htmx.eval`` capability."""
    if not isinstance(value, str):
        return False
    lower = canonical_hx_attribute(attribute)
    if lower.startswith("hx-on"):
        return True
    if lower not in _HX_EVAL_VALUE_ATTRS:
        return False
    return bool(_HX_JS_VALUE_RE.search(value))


def hx_attribute_is_url(attribute: str) -> bool:
    """True when an HTMX attribute carries a URL (#230 data-hx parity)."""
    lower = canonical_hx_attribute(attribute)
    if not lower.startswith("hx-"):
        return False
    suffix = lower[3:]
    return suffix in _HX_URL_ATTR_SUFFIXES


def reject_hx_eval_value(attribute: str, value: object) -> None:
    """Raise ``HED-SEC-0011`` when ``js:`` appears without an explicit opt-in."""
    canonical = canonical_hx_attribute(attribute)
    normalized = value
    if isinstance(value, str):
        normalized = nfkc_strip_format(value)
    if not hx_value_needs_eval(canonical, normalized):
        return
    if htmx_eval_allowed():
        return
    from hedron_core.diagnostics import error

    raise error(
        "HED-SEC-0011",
        title="HTMX js: attribute value rejected",
        explanation=(
            f"Attribute {canonical!r} uses a js: expression, which requires an explicit "
            "htmx.eval opt-in (allow_htmx_eval() or SecurityPolicy.allow_htmx_eval)."
        ),
        remediation=(
            "Pass a JSON object literal without js:, or wrap construction in "
            "hedron_core.htmx_eval.allow_htmx_eval() / set SecurityPolicy.allow_htmx_eval=True."
        ),
    )
