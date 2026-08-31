"""First-party hedron-map component (RENDER-047)."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from hedron_core.builtins.map_geo import DEFAULT_MAX_FEATURES, MarkerSpec, sanitize_geojson
from hedron_core.component import Component, NodeLike
from hedron_core.csrf_strategy import DEFAULT_CSRF_COOKIE_NAME, DEFAULT_CSRF_HEADER_NAME
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.rendering import active_render_context
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_maps.compile import compile_map
from hedron_maps.spec import (
    AccessibilityDef,
    GeoJSONLayer,
    MapPlan,
    MapPolicy,
    MapSpec,
    MarkerLayer,
    OpenStreetMap,
    RasterTiles,
    ViewState,
)

ABI_VERSION = 1
TAG_NAME = "hedron-map"
ELEMENT_ID = "hedron-map"
_UNSET = object()


def _ensure_tile_allowed(tiles: str | None, allowlist: Sequence[str]) -> str | None:
    """Validate a construction-time tile template against explicit prefixes."""
    if tiles is None:
        return None
    prefixes = [str(raw).strip() for raw in allowlist]
    if any(not prefix for prefix in prefixes) or not prefixes:
        raise error(
            "HED-MAP-0002",
            title="Disallowed map tile source",
            explanation="tile_allowlist entries must be non-empty URL prefixes.",
            remediation="Pass concrete allowlisted origins or path prefixes.",
        )
    if not any(
        tiles.startswith(prefix)
        and (
            prefix.endswith(("/", "?", "#"))
            or tiles[len(prefix) :] == ""
            or tiles[len(prefix)] in "/?#"
        )
        for prefix in prefixes
    ):
        raise error(
            "HED-MAP-0002",
            title="Disallowed map tile source",
            explanation=f"Tile template {tiles!r} is not covered by {prefixes!r}.",
            remediation="Pass an allowlisted tile URL prefix or omit tiles.",
        )
    return tiles


__all__ = [
    "ABI_VERSION",
    "ELEMENT_ID",
    "Map",
    "TAG_NAME",
    "fallback_nodes",
    "plan_payload_json",
]


def plan_payload_json(plan: MapPlan) -> str:
    payload = plan.to_json_dict()
    if not plan.accessibility.include_table:
        payload = dict(payload)
        acc_raw = payload.get("accessibility")
        acc = dict(acc_raw) if isinstance(acc_raw, dict) else {}
        acc["table_rows"] = []
        payload["accessibility"] = acc
    return json.dumps(payload, separators=(",", ":"), allow_nan=False, default=str)


def fallback_nodes(plan: MapPlan) -> list[NodeLike]:
    nodes: list[NodeLike] = [
        html.figcaption(
            html.strong(plan.accessibility.title),
            html.span(f" — {plan.accessibility.description}"),
        )
    ]
    rows = list(plan.accessibility.table_rows) if plan.accessibility.include_table else []
    header = html.tr(html.th("Label"), html.th("Latitude"), html.th("Longitude"), html.th("Link"))
    body: list[NodeLike] = []
    for row in rows:
        href = row.get("href")
        action = row.get("action")
        label = str(row.get("label") or row.get("id") or "")
        if href:
            parsed = (
                href
                if isinstance(href, SafeUrl)
                else SafeUrl.parse(str(href), purpose=UrlPurpose.NAVIGATION)
            )
            link: NodeLike = html.a(label or "Open", href=parsed)
        elif action:
            link = html.span(str(action))
        else:
            link = html.span("")
        body.append(
            html.tr(
                html.td(label),
                html.td("" if row.get("lat") is None else str(row.get("lat"))),
                html.td("" if row.get("lon") is None else str(row.get("lon"))),
                html.td(link),
            )
        )
    nodes.append(
        html.table(
            html.caption("Map features and markers"),
            html.thead(header),
            html.tbody(*body) if body else html.tbody(),
            class_="hedron-map-alternative",
        )
    )
    if plan.attribution:
        nodes.append(html.p(" · ".join(plan.attribution), class_="hedron-map-attribution"))
    return nodes


class MapProps(Props):
    title: str = "Map"
    class_: str | None = None


class Map(Component[MapProps]):
    """Additive maps Map. OSM default is here only; core hedron.Map is unchanged."""

    props_type = MapProps
    logical_name = "Map"
    distribution = "hedron-maps"

    def __init__(
        self,
        spec: MapSpec | Mapping[str, Any] | None = None,
        *,
        center: tuple[float, float] = (0.0, 0.0),
        zoom: float = 2.0,
        title: str = "Map",
        description: str = "Geographic map",
        basemap: object = _UNSET,
        policy: MapPolicy | None = None,
        layers: Sequence[object] = (),
        tiles: str | None = None,
        tile_allowlist: Sequence[str] = (),
        attribution: str = "",
        markers: Sequence[MarkerSpec | Mapping[str, Any]] = (),
        geojson: Mapping[str, Any] | None = None,
        max_features: int = DEFAULT_MAX_FEATURES,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(MapProps(title=title, class_=class_, **kwargs))
        self._max_features = max_features
        self._interaction_commands: dict[str, str] = {}
        if spec is not None:
            self._spec = spec if isinstance(spec, MapSpec) else MapSpec.model_validate(dict(spec))
            return

        overlay: list[object] = list(layers)
        if markers:
            dumped: list[dict[str, Any]] = []
            for item in markers:
                if isinstance(item, MarkerSpec):
                    dumped.append(item.model_dump(mode="json"))
                else:
                    dumped.append(dict(item))
            overlay.append(MarkerLayer(markers=tuple(dumped)))
        if geojson is not None:
            cleaned, _features = sanitize_geojson(geojson, max_features=max_features)
            overlay.append(
                GeoJSONLayer(data=dict(cleaned or {"type": "FeatureCollection", "features": []}))
            )

        resolved_basemap: object
        resolved_policy = policy
        if tiles is not None:
            _ensure_tile_allowed(tiles, tile_allowlist)
            resolved_basemap = RasterTiles(url=tiles, attribution=attribution or "Tiles")
            origin = None
            if tiles.startswith("https://"):
                from urllib.parse import urlparse

                parsed = urlparse(tiles)
                origin = f"{parsed.scheme}://{parsed.netloc}"
            if origin:
                base = resolved_policy if resolved_policy is not None else MapPolicy()
                existing = tuple(base.allowed_origins)
                resolved_policy = base.model_copy(
                    update={"allowed_origins": tuple(dict.fromkeys((*existing, origin)))}
                )
        elif basemap is _UNSET:
            resolved_basemap = OpenStreetMap.standard()
        else:
            resolved_basemap = basemap

        acc = AccessibilityDef(title=title, description=description)
        self._spec = MapSpec(
            basemap=resolved_basemap,  # type: ignore[arg-type]
            layers=tuple(overlay),  # type: ignore[arg-type]
            view=ViewState(center=center, zoom=zoom),
            accessibility=acc,
            policy=resolved_policy,
        )

    def compile_plan(self) -> MapPlan:
        return compile_map(self._spec, policy=self._spec.policy, max_features=self._max_features)

    def register_interaction(self, event: str, path: str) -> None:
        """Register a generated event endpoint for the map host."""
        self._interaction_commands[event] = path

    def render(self) -> NodeLike:
        plan = self.compile_plan()
        payload = plan_payload_json(plan)
        children = fallback_nodes(plan)
        context = active_render_context()
        csrf_cookie_name = getattr(context, "csrf_cookie_name", DEFAULT_CSRF_COOKIE_NAME)
        csrf_header_name = getattr(context, "csrf_header_name", DEFAULT_CSRF_HEADER_NAME)
        attrs = {
            "data-hedron-abi": str(ABI_VERSION),
            "data-hedron-element": ELEMENT_ID,
            "data-hedron-map": "first-party",
            "data-hedron-payload": payload,
            "role": "region",
            "aria-label": plan.accessibility.title,
            "class_": self.props.class_,
            "data-hedron-csrf-cookie": csrf_cookie_name,
            "data-hedron-csrf-header": csrf_header_name,
        }
        if self._interaction_commands:
            attrs["data-hedron-map-commands"] = json.dumps(
                self._interaction_commands, separators=(",", ":")
            )
        return html.tag(TAG_NAME)(
            html.figure(*children, class_="hedron-map-fallback-figure"),
            **attrs,
        )
