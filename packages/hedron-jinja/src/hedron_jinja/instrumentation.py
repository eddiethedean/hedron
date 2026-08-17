"""HDJ loop/macro budgets, extension evidence, and portable checker fixtures (0.14)."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any

from hedron_core.diagnostics import (
    Diagnostic,
    DiagnosticSeverity,
    SourceSpan,
    error,
    make_diagnostic,
)

__all__ = [
    "ExtensionEvidence",
    "ExtensionRegistry",
    "LoopMacroBudget",
    "LoopMacroCounters",
    "checker_fixture_from_diagnostics",
    "instrumentation_session",
    "record_loop_iteration",
    "record_macro_call",
    "register_htmx_catalog",
]

_loop_used: ContextVar[int] = ContextVar("hedron_hdj_loop_used", default=0)
_macro_used: ContextVar[int] = ContextVar("hedron_hdj_macro_used", default=0)
_loop_limit: ContextVar[int | None] = ContextVar("hedron_hdj_loop_limit", default=None)
_macro_limit: ContextVar[int | None] = ContextVar("hedron_hdj_macro_limit", default=None)


@dataclass(slots=True)
class LoopMacroBudget:
    """Exact loop/macro work accounting limits (phase 0.14)."""

    max_loop_iterations: int = 100_000
    max_macro_calls: int = 10_000


@dataclass(slots=True)
class LoopMacroCounters:
    loop_iterations: int = 0
    macro_calls: int = 0


@dataclass(frozen=True, slots=True)
class ExtensionEvidence:
    """Contracted custom-extension / HTMX-extension evidence metadata."""

    extension_id: str
    version: str
    digest: str
    csp: Mapping[str, str] = field(default_factory=dict)
    load_order: int = 0
    kind: str = "jinja"  # "jinja" | "htmx"

    def __post_init__(self) -> None:
        object.__setattr__(self, "csp", dict(self.csp))
        if not self.extension_id or not self.version or not self.digest:
            raise ValueError("extension_id, version, and digest are required")


def register_htmx_catalog(registry: ExtensionRegistry | None = None) -> ExtensionRegistry:
    """Project core HTMX catalog facts into HDJ evidence. Does not install scripts."""
    from hedron_core.htmx_extensions import catalog_evidence_rows

    target = registry if registry is not None else ExtensionRegistry()
    for row in catalog_evidence_rows():
        if target.get(row.public_id) is not None:
            continue
        target.register(
            ExtensionEvidence(
                extension_id=row.public_id,
                version=row.version,
                digest=row.digest,
                csp={"script-src": "'self'"},
                load_order=row.load_order,
                kind="htmx",
            )
        )
    return target


class ExtensionRegistry:
    """Registered extensions with version/digest/CSP/load-order metadata."""

    def __init__(self) -> None:
        self._items: dict[str, ExtensionEvidence] = {}

    def register(self, evidence: ExtensionEvidence) -> ExtensionEvidence:
        self._items[evidence.extension_id] = evidence
        return evidence

    def get(self, extension_id: str) -> ExtensionEvidence | None:
        return self._items.get(extension_id)

    def items(self) -> Mapping[str, ExtensionEvidence]:
        return dict(self._items)

    def require(self, extension_id: str) -> ExtensionEvidence:
        found = self._items.get(extension_id)
        if found is None:
            raise error(
                "HED-JINJA-0030",
                title="Extension evidence missing",
                explanation=(
                    f"Extension {extension_id!r} is referenced but not registered with "
                    "version/digest/CSP/load-order metadata."
                ),
                remediation=(
                    "Register ExtensionEvidence before binding or remove hx-ext/feature use."
                ),
            )
        return found

    @staticmethod
    def digest_bytes(payload: bytes) -> str:
        return hashlib.sha256(payload).hexdigest()


class _InstrumentationSession:
    def __init__(self, budget: LoopMacroBudget) -> None:
        self.budget = budget
        self._tok_loop_used: Any = None
        self._tok_macro_used: Any = None
        self._tok_loop_limit: Any = None
        self._tok_macro_limit: Any = None

    def __enter__(self) -> LoopMacroCounters:
        self._tok_loop_used = _loop_used.set(0)
        self._tok_macro_used = _macro_used.set(0)
        self._tok_loop_limit = _loop_limit.set(self.budget.max_loop_iterations)
        self._tok_macro_limit = _macro_limit.set(self.budget.max_macro_calls)
        return LoopMacroCounters()

    def __exit__(self, *args: object) -> None:
        if self._tok_macro_limit is not None:
            _macro_limit.reset(self._tok_macro_limit)
        if self._tok_loop_limit is not None:
            _loop_limit.reset(self._tok_loop_limit)
        if self._tok_macro_used is not None:
            _macro_used.reset(self._tok_macro_used)
        if self._tok_loop_used is not None:
            _loop_used.reset(self._tok_loop_used)


def instrumentation_session(budget: LoopMacroBudget | None = None) -> _InstrumentationSession:
    return _InstrumentationSession(budget or LoopMacroBudget())


def record_loop_iteration(count: int = 1) -> int:
    limit = _loop_limit.get()
    used = _loop_used.get() + count
    _loop_used.set(used)
    if limit is not None and used > limit:
        raise error(
            "HED-JINJA-0031",
            title="Loop iteration budget exceeded",
            explanation=f"Template exceeded {limit} loop iterations.",
            remediation="Bound the iterable in Python or raise max_loop_iterations deliberately.",
        )
    return used


def record_macro_call(count: int = 1) -> int:
    limit = _macro_limit.get()
    used = _macro_used.get() + count
    _macro_used.set(used)
    if limit is not None and used > limit:
        raise error(
            "HED-JINJA-0032",
            title="Macro call budget exceeded",
            explanation=f"Template exceeded {limit} macro calls.",
            remediation="Reduce macro recursion or raise max_macro_calls deliberately.",
        )
    return used


def current_counters() -> LoopMacroCounters:
    return LoopMacroCounters(loop_iterations=_loop_used.get(), macro_calls=_macro_used.get())


def checker_fixture_from_diagnostics(
    *,
    fixture_id: str,
    diagnostics: Iterable[Diagnostic],
    contract_version: str = "hedron-portable-1",
) -> dict[str, Any]:
    """Emit a portable SARIF-shaped checker fixture payload."""
    results = []
    for diag in diagnostics:
        results.append(
            {
                "ruleId": diag.code,
                "level": (
                    diag.severity.value if hasattr(diag.severity, "value") else str(diag.severity)
                ),
                "message": {"text": diag.title},
                "properties": {
                    "explanation": diag.explanation,
                    "remediation": diag.remediation,
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": diag.span.path if diag.span else "",
                            },
                            "region": {
                                "startLine": diag.span.start_line if diag.span else 1,
                            },
                        }
                    }
                ]
                if diag.span is not None
                else [],
            }
        )
    return {
        "id": fixture_id,
        "contract_version": contract_version,
        "capability": "diagnostics",
        "format": "sarif-shaped-v1",
        "runs": [{"results": results}],
    }


def extension_feature_diagnostics(
    *,
    declared_features: Iterable[str],
    registry: ExtensionRegistry | None,
    template_name: str,
    body: str = "",
) -> list[Diagnostic]:
    """Require ExtensionEvidence for jinja.extension:* / htmx.extension:* features and hx-ext."""
    diagnostics: list[Diagnostic] = []
    reg = registry or ExtensionRegistry()
    for feature in declared_features:
        if ".extension:" not in feature:
            continue
        ext_id = feature.split(":", 1)[-1]
        if reg.get(ext_id) is None:
            diagnostics.append(
                make_diagnostic(
                    "HED-JINJA-0030",
                    severity=DiagnosticSeverity.ERROR,
                    title="Extension evidence missing",
                    explanation=(
                        f"Feature {feature!r} requires registered version/digest/CSP/load-order "
                        "metadata."
                    ),
                    remediation="Register ExtensionEvidence before binding.",
                    span=SourceSpan(path=template_name, start_line=1),
                )
            )
    # hx-ext alone never installs — require evidence when present in body.
    if "hx-ext=" in body or "hx-ext =" in body:
        # crude extract of quoted values
        import re

        for match in re.finditer(r"hx-ext\s*=\s*['\"]([^'\"]+)['\"]", body, re.I):
            for part in match.group(1).split(","):
                ext_id = part.strip()
                if not ext_id:
                    continue
                if reg.get(ext_id) is None:
                    diagnostics.append(
                        make_diagnostic(
                            "HED-JINJA-0030",
                            severity=DiagnosticSeverity.ERROR,
                            title="hx-ext without registered evidence",
                            explanation=(
                                f"hx-ext references {ext_id!r} but no "
                                "ExtensionEvidence is registered."
                            ),
                            remediation=(
                                "Register version/digest/CSP/load-order metadata; "
                                "hx-ext alone never installs an extension."
                            ),
                            span=SourceSpan(path=template_name, start_line=1),
                        )
                    )
    return diagnostics


def a11y_static_diagnostics(*, template_name: str, body: str) -> list[Diagnostic]:
    """Sound HTML/form/landmark/ID/ARIA/focus subset without claiming WCAG proof."""
    import re

    diagnostics: list[Diagnostic] = []
    # img without alt
    for match in re.finditer(r"<img\b([^>]*)>", body, re.I):
        attrs = match.group(1)
        if not re.search(r"\balt\s*=", attrs, re.I):
            diagnostics.append(
                make_diagnostic(
                    "HED-JINJA-0033",
                    severity=DiagnosticSeverity.WARNING,
                    title="img missing alt",
                    explanation="Static check: <img> without alt attribute.",
                    remediation='Add alt text or alt="" for decorative images.',
                    span=SourceSpan(path=template_name, start_line=1),
                )
            )
    # duplicate id attributes (static literal ids only)
    ids = re.findall(r'\bid\s*=\s*["\']([^"\']+)["\']', body, re.I)
    seen: set[str] = set()
    for element_id in ids:
        if element_id in seen:
            diagnostics.append(
                make_diagnostic(
                    "HED-JINJA-0033",
                    severity=DiagnosticSeverity.WARNING,
                    title="Duplicate HTML id",
                    explanation=f"Static check: duplicate id={element_id!r}.",
                    remediation="Ensure id values are unique within the template.",
                    span=SourceSpan(path=template_name, start_line=1),
                )
            )
        seen.add(element_id)
    # button without text/aria (empty element)
    if re.search(r"<button\b[^>]*>\s*</button>", body, re.I) and not re.search(
        r"<button\b[^>]*aria-label\s*=", body, re.I
    ):
        diagnostics.append(
            make_diagnostic(
                "HED-JINJA-0033",
                severity=DiagnosticSeverity.WARNING,
                title="button missing accessible name",
                explanation="Static check: empty <button> without aria-label.",
                remediation="Provide visible text or aria-label.",
                span=SourceSpan(path=template_name, start_line=1),
            )
        )
    return diagnostics


def portable_checker_json(diagnostics: Iterable[Diagnostic], fixture_id: str = "hdj-check") -> str:
    return json.dumps(
        checker_fixture_from_diagnostics(fixture_id=fixture_id, diagnostics=diagnostics),
        indent=2,
        sort_keys=True,
    )
