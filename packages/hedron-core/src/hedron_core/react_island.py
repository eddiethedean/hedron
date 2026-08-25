"""An isolated, SSR-safe host contract for optional React islands.

The core package deliberately does not ship React. Applications may attach a
pinned client-side adapter to this host, while the server always renders the
provided fallback and keeps the island isolated behind a CSP-auditable marker.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass

from hedron_core.component import NodeLike
from hedron_core.html import html

__all__ = [
    "REACT_ISLAND_RECIPE",
    "ReactIslandRecipe",
    "react_island_host",
    "react_island_recipe",
]

_SAFE_ID = re.compile(r"^[a-z][a-z0-9-]{0,63}$")


@dataclass(frozen=True, slots=True)
class ReactIslandRecipe:
    """Pinned metadata required before an optional React adapter is attached."""

    logical_id: str = "legacy-chart-island"
    package: str = "react"
    version: str = "18.3.1"
    entrypoint: str = "./island.mjs"
    maturity: str = "Experimental"
    ssr_fallback: bool = True
    csp_safe: bool = True
    cleanup: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "hedron.react-island/1",
            "logical_id": self.logical_id,
            "package": self.package,
            "version": self.version,
            "entrypoint": self.entrypoint,
            "maturity": self.maturity,
            "ssr_fallback": self.ssr_fallback,
            "csp_safe": self.csp_safe,
            "cleanup": self.cleanup,
        }


REACT_ISLAND_RECIPE = ReactIslandRecipe()


def react_island_recipe() -> ReactIslandRecipe:
    """Return the immutable recipe without importing or requiring React."""
    return REACT_ISLAND_RECIPE


def react_island_host(
    island_id: str,
    fallback: NodeLike,
    *,
    props: Mapping[str, object] | None = None,
    recipe: ReactIslandRecipe = REACT_ISLAND_RECIPE,
) -> NodeLike:
    """Render a safe host whose fallback remains valid when enhancement is absent."""
    if not _SAFE_ID.fullmatch(island_id):
        raise ValueError("island_id must contain only lowercase letters, digits, and hyphens")
    if not recipe.ssr_fallback or not recipe.csp_safe or not recipe.cleanup:
        raise ValueError("React island recipe must provide SSR, CSP, and cleanup guarantees")
    try:
        encoded_props = json.dumps(
            dict(props or {}),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("React island props must be finite JSON-serializable values") from exc
    return html.div(
        fallback,
        id=f"hedron-island-{island_id}",
        data={
            "hedron-react-island": recipe.logical_id,
            "hedron-react-version": recipe.version,
            "hedron-react-props": encoded_props,
            "hedron-react-cleanup": "true",
            "hedron-react-ssr-fallback": "true",
        },
    )
