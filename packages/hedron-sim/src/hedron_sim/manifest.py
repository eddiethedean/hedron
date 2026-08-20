"""Machine-readable declared-subset and divergence manifest for hedron-sim.

The simulator emulates a deliberately small HTMX surface. Every category below
names the features it does emulate *and* the features it refuses, so authors can
diff the manifest instead of discovering an approximation at demo time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hedron_sim.subset import (
    DECLARED_HX_ATTRS,
    DECLARED_HX_METHODS,
    DECLARED_SWAP_STYLES,
    HED_SIM_UNSUPPORTED,
    UnsupportedSimFeatureError,
)

__all__ = [
    "MANIFEST_CATEGORIES",
    "SIM_MANIFEST_SCHEMA",
    "ManifestEntry",
    "divergence_manifest",
    "manifest_entry",
    "manifest_markdown",
    "require_supported_feature",
    "subset_manifest",
]

SIM_MANIFEST_SCHEMA = "hedron-sim-manifest-1"

MANIFEST_CATEGORIES: tuple[str, ...] = (
    "methods",
    "attrs",
    "swaps",
    "triggers",
    "history",
    "forms",
    "extensions",
    "errors",
    "timing",
)


@dataclass(frozen=True, slots=True)
class ManifestEntry:
    """One feature the simulator either emulates or explicitly refuses."""

    category: str
    name: str
    supported: bool
    note: str = ""

    @property
    def failure_code(self) -> str | None:
        return None if self.supported else HED_SIM_UNSUPPORTED

    def as_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "name": self.name,
            "supported": self.supported,
            "note": self.note,
            "failure_code": self.failure_code,
        }


def _supported(
    category: str,
    names: frozenset[str] | tuple[str, ...],
    note: str,
) -> list[ManifestEntry]:
    return [
        ManifestEntry(category=category, name=name, supported=True, note=note)
        for name in sorted(names)
    ]


def _unsupported(category: str, rows: tuple[tuple[str, str], ...]) -> list[ManifestEntry]:
    return [
        ManifestEntry(category=category, name=name, supported=False, note=note)
        for name, note in rows
    ]


def _build_entries() -> dict[str, tuple[ManifestEntry, ...]]:
    entries: dict[str, list[ManifestEntry]] = {}

    entries["methods"] = _supported(
        "methods", DECLARED_HX_METHODS, "dispatched from the pre-rendered route table"
    ) + _unsupported(
        "methods",
        (
            ("HEAD", "no header-only responses in the offline route table"),
            ("OPTIONS", "no preflight or capability negotiation"),
            ("TRACE", "no request echo"),
            ("CONNECT", "no tunneling"),
        ),
    )

    entries["attrs"] = (
        _supported(
            "attrs", DECLARED_HX_ATTRS, "request attribute resolved against a registered route"
        )
        + _supported(
            "attrs",
            ("hx-confirm", "hx-swap", "hx-swap-oob", "hx-target", "hx-trigger"),
            "presentation attribute honored by hedron-sim.js",
        )
        + _unsupported(
            "attrs",
            (
                ("hx-boost", "no document navigation interception"),
                ("hx-headers", "requests never leave the page"),
                ("hx-include", "only the submitting form is serialized"),
                ("hx-indicator", "the simulator draws its own pending state"),
                ("hx-params", "no request parameter filtering"),
                ("hx-push-url", "no history integration"),
                ("hx-select", "responses are used whole"),
                ("hx-sync", "no request queue or abort semantics"),
                ("hx-vals", "no computed request payloads"),
                ("hx-ws", "no socket transport"),
            ),
        )
    )

    entries["swaps"] = _supported(
        "swaps", DECLARED_SWAP_STYLES, "applied to the resolved target region"
    ) + _unsupported(
        "swaps",
        (
            ("morph", "MORPH-048 stays closed; no morphing swap"),
            ("multi:", "no multi-target swap specification"),
            ("settle:", "no settle timing modifier"),
            ("show:", "no scroll or focus modifier"),
            ("swap:", "no swap delay modifier"),
            ("transition:", "no View Transitions integration"),
        ),
    )

    entries["triggers"] = _supported(
        "triggers",
        ("click", "every <n>ms", "load", "submit"),
        "trigger recognized by the offline runtime",
    ) + _unsupported(
        "triggers",
        (
            ("changed", "no value-change gating"),
            ("delay:", "no per-trigger debounce"),
            ("from:", "no external trigger source"),
            ("intersect", "no IntersectionObserver emulation"),
            ("keyup", "no keyboard trigger routing"),
            ("revealed", "no scroll-reveal emulation"),
            ("sse:", "no server-sent events"),
            ("throttle:", "no per-trigger throttle"),
        ),
    )

    entries["history"] = _unsupported(
        "history",
        (
            ("back", "the simulator owns no history stack"),
            ("hx-history-elt", "no history restore target"),
            ("pushState", "the docs URL never changes"),
            ("replaceState", "the docs URL never changes"),
            ("restore", "no snapshot cache"),
        ),
    )

    entries["forms"] = _supported(
        "forms",
        ("application/x-www-form-urlencoded", "submit", "validate"),
        "form submission serialized in-page for validation demos",
    ) + _unsupported(
        "forms",
        (
            ("file upload", "no file transport"),
            ("multipart/form-data", "no multipart encoder"),
            ("native validation", "browser constraint UI is not emulated"),
        ),
    )

    entries["extensions"] = _unsupported(
        "extensions",
        (
            ("client-side-templates", "no template extension"),
            ("head-support", "no document head merging"),
            ("hx-ext", "the extension registry is not emulated"),
            ("idiomorph", "MORPH-048 stays closed"),
            ("response-targets", "no error-status retargeting"),
        ),
    )

    entries["errors"] = _supported(
        "errors",
        ("region-allowlist-denial", "status-from-interaction-result"),
        "deterministic offline failure surfaced in the trace panel",
    ) + _unsupported(
        "errors",
        (
            ("hx-on::error", "no event-handler attributes"),
            ("network failure", "there is no network to fail"),
            ("retry", "no retry or backoff policy"),
            ("timeout", "responses are pre-rendered"),
        ),
    )

    entries["timing"] = _supported(
        "timing",
        ("scenario-clock", "scripted-delay"),
        "virtual time advanced by hedron_sim.recording.SimClock",
    ) + _unsupported(
        "timing",
        (
            ("animation frame", "no frame-accurate scheduling"),
            ("latency profile", "no bandwidth or latency emulation"),
            ("wall-clock parity", "sim placeholders replace real timestamps"),
        ),
    )

    return {category: tuple(entries[category]) for category in MANIFEST_CATEGORIES}


_ENTRIES: dict[str, tuple[ManifestEntry, ...]] = _build_entries()


def subset_manifest() -> dict[str, Any]:
    """Return the machine-readable declared subset (supported features only)."""
    return {
        "schema_version": SIM_MANIFEST_SCHEMA,
        "categories": {
            category: [entry.name for entry in rows if entry.supported]
            for category, rows in _ENTRIES.items()
        },
    }


def divergence_manifest() -> dict[str, Any]:
    """Return the declared subset plus every explicitly refused feature."""
    categories: dict[str, Any] = {}
    for category, rows in _ENTRIES.items():
        categories[category] = {
            "supported": [entry.name for entry in rows if entry.supported],
            "unsupported": [entry.as_dict() for entry in rows if not entry.supported],
        }
    return {
        "schema_version": SIM_MANIFEST_SCHEMA,
        "failure_code": HED_SIM_UNSUPPORTED,
        "categories": categories,
    }


def manifest_entry(category: str, name: str) -> ManifestEntry | None:
    """Return the manifest row for ``name`` in ``category``, or ``None`` if undeclared."""
    for entry in _ENTRIES.get(category, ()):
        if entry.name.lower() == name.strip().lower():
            return entry
    return None


def require_supported_feature(category: str, name: str) -> str:
    """Return ``name`` when the manifest declares it supported, else fail visibly."""
    if category not in _ENTRIES:
        raise UnsupportedSimFeatureError(
            f"hedron-sim has no manifest category {category!r}; "
            f"declared categories={list(MANIFEST_CATEGORIES)}",
            category=category,
            feature=name,
        )
    entry = manifest_entry(category, name)
    if entry is None:
        raise UnsupportedSimFeatureError(
            f"hedron-sim does not declare {category} feature {name!r}; see divergence_manifest()",
            category=category,
            feature=name,
        )
    if not entry.supported:
        raise UnsupportedSimFeatureError(
            f"hedron-sim does not emulate {category} feature {entry.name!r}: {entry.note}",
            category=category,
            feature=entry.name,
        )
    return entry.name


def manifest_markdown() -> str:
    """Render the divergence manifest as documentation-ready Markdown."""
    lines = [
        "# hedron-sim declared subset and divergence",
        "",
        f"Schema: `{SIM_MANIFEST_SCHEMA}`. Refused features raise",
        f"`UnsupportedSimFeatureError` with code `{HED_SIM_UNSUPPORTED}`.",
        "",
    ]
    for category, rows in _ENTRIES.items():
        supported = [entry.name for entry in rows if entry.supported]
        lines.append(f"## {category}")
        lines.append("")
        lines.append(f"- Supported: {', '.join(supported) if supported else 'none'}")
        for entry in rows:
            if not entry.supported:
                lines.append(f"- Unsupported `{entry.name}` — {entry.note}")
        lines.append("")
    return "\n".join(lines)
