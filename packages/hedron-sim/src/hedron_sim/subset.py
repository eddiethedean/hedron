"""Declared HTMX subset and unsupported-feature failures for hedron-sim."""

from __future__ import annotations

from dataclasses import dataclass

# Mirrors hedron_conformance.authoring_loop.HED_SIM_UNSUPPORTED. hedron-sim does not
# depend on hedron-conformance; tests/unit/test_sim_054.py asserts the two agree.
HED_SIM_UNSUPPORTED = "HED-SIM-UNSUPPORTED"

# Keep synchronized with packages/hedron-sim/src/hedron_sim/static/hedron-sim.js
DECLARED_HX_METHODS: frozenset[str] = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE"})
DECLARED_HX_ATTRS: frozenset[str] = frozenset(
    {"hx-get", "hx-post", "hx-put", "hx-patch", "hx-delete"}
)
DECLARED_SWAP_STYLES: frozenset[str] = frozenset(
    {
        "innerHTML",
        "outerHTML",
        "beforebegin",
        "afterbegin",
        "beforeend",
        "afterend",
        "delete",
        "none",
    }
)


class UnsupportedSimFeatureError(ValueError):
    """Raised when a caller requests behavior outside the declared HTMX subset."""

    code: str = HED_SIM_UNSUPPORTED

    def __init__(self, message: str, *, category: str = "", feature: str = "") -> None:
        super().__init__(message)
        self.category = category
        self.feature = feature


@dataclass(frozen=True, slots=True)
class SimSubset:
    methods: frozenset[str] = DECLARED_HX_METHODS
    attrs: frozenset[str] = DECLARED_HX_ATTRS
    swap_styles: frozenset[str] = DECLARED_SWAP_STYLES

    def as_dict(self) -> dict[str, list[str]]:
        return {
            "methods": sorted(self.methods),
            "attrs": sorted(self.attrs),
            "swap_styles": sorted(self.swap_styles),
        }


DEFAULT_SUBSET = SimSubset()


def require_supported_method(method: str) -> str:
    normalized = method.strip().upper()
    if normalized not in DECLARED_HX_METHODS:
        raise UnsupportedSimFeatureError(
            f"hedron-sim does not emulate HTTP method {method!r}; "
            f"declared subset={sorted(DECLARED_HX_METHODS)}",
            category="methods",
            feature=normalized,
        )
    return normalized


def require_supported_swap(swap: str) -> str:
    # JS treats unknown styles as innerHTML; Python API fails loudly for authors.
    token = swap.strip()
    key = token.split(" ", 1)[0]
    # normalize casing for known tokens
    for style in DECLARED_SWAP_STYLES:
        if key.lower() == style.lower():
            return style if " " not in token else f"{style}{token[len(key) :]}"
    raise UnsupportedSimFeatureError(
        f"hedron-sim does not emulate hx-swap style {swap!r}; "
        f"declared subset={sorted(DECLARED_SWAP_STYLES)}",
        category="swaps",
        feature=key,
    )


def subset_policy_markdown() -> str:
    data = DEFAULT_SUBSET.as_dict()
    lines = [
        "# hedron-sim declared HTMX subset",
        "",
        "Tooling-grade offline simulation covers only:",
        "",
        f"- Methods: {', '.join(data['methods'])}",
        f"- Trigger attrs: {', '.join(data['attrs'])}",
        f"- Swap styles: {', '.join(data['swap_styles'])}",
        "",
        "Region targets must match registered fragment selectors or the runtime",
        "emits a 403 allowlist denial. Unsupported authoring APIs raise",
        "`UnsupportedSimFeatureError`.",
    ]
    return "\n".join(lines) + "\n"
