"""Build static previews from the actual Edron callback graph."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, cast

from edron import App, Outcome, OutcomeKind
from edron.simulation import SimulationRequest, SimulationResponse, SimulationRoute
from hedron_core import FragmentRegion
from hedron_core.htmx.policy import InteractionResult
from hedron_sim import SimApp, embed_demo, render_handler_html

EDRON_SIM_SCHEMA = "edron-sim/1"
MAX_SIM_ROUTES = 128
MAX_SIM_HTML_BYTES = 4_000_000

__all__ = [
    "EDRON_SIM_SCHEMA",
    "Simulation",
    "SimulationArtifact",
    "SimulationBuildError",
    "SimulationConfig",
]


class SimulationBuildError(RuntimeError):
    """Raised when a real Edron route cannot be rendered deterministically."""


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """Explicit bounds and identity for one static simulation build."""

    entrypoint: str = "/"
    demo_id: str = "edron-sim"
    max_routes: int = MAX_SIM_ROUTES
    max_html_bytes: int = MAX_SIM_HTML_BYTES

    def __post_init__(self) -> None:
        if not self.entrypoint.startswith("/"):
            raise ValueError("simulation entrypoint must begin with '/'")
        if not self.demo_id.strip():
            raise ValueError("simulation demo_id must not be empty")
        if self.max_routes < 1 or self.max_routes > MAX_SIM_ROUTES:
            raise ValueError(f"max_routes must be between 1 and {MAX_SIM_ROUTES}")
        if self.max_html_bytes < 1 or self.max_html_bytes > MAX_SIM_HTML_BYTES:
            raise ValueError(f"max_html_bytes must be between 1 and {MAX_SIM_HTML_BYTES}")


@dataclass(frozen=True, slots=True)
class SimulationArtifact:
    """A self-contained static embed plus the route manifest that produced it."""

    html: str
    manifest: Mapping[str, Any]
    responses: Mapping[str, SimulationResponse] = field(
        default_factory=dict[str, SimulationResponse]
    )

    def embed(self) -> str:
        """Return the generated HTML snippet for a docs page."""
        return self.html

    def manifest_json(self) -> str:
        """Return the bounded manifest as stable JSON."""
        return json.dumps(self.manifest, sort_keys=True, separators=(",", ":"))


class Simulation:
    """Build a docs simulation from an :class:`edron.App`.

    No components are re-authored here. The builder dispatches the actual
    Edron page, fragment, and action callbacks and hands their rendered values
    to the existing static HTMX runtime. Use fixtures for explicit application
    dependencies; arbitrary databases, identity providers, and network calls
    are intentionally outside this package's scope.
    """

    def __init__(
        self,
        app: App,
        *,
        config: SimulationConfig | None = None,
        fixtures: Mapping[str, Any] | None = None,
        route_values: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> None:
        if not isinstance(app, App):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError("Simulation expects an edron.App")
        self.app = app
        self.config = config or SimulationConfig()
        self.fixtures = dict(fixtures or {})
        self.route_values = {str(key): dict(value) for key, value in (route_values or {}).items()}

    @classmethod
    def from_app(cls, app: App, **kwargs: Any) -> Simulation:
        """Construct a simulation using the app's real registration graph."""
        return cls(app, **kwargs)

    def build(self) -> SimulationArtifact:
        """Synchronously build a static simulation.

        Use :meth:`build_async` when called from an already-running event loop.
        """
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.build_async())
        raise RuntimeError("Simulation.build() cannot run inside an event loop; use build_async()")

    async def build_async(self) -> SimulationArtifact:
        """Build a static simulation without starting a server."""
        surface = self.app.simulation(fixtures=self.fixtures)
        routes = surface.routes
        if len(routes) > self.config.max_routes:
            raise SimulationBuildError(
                f"simulation route count {len(routes)} exceeds max_routes={self.config.max_routes}"
            )
        try:
            entrypoint = surface.route("GET", self.config.entrypoint)
        except Exception as exc:
            raise SimulationBuildError(
                f"entrypoint {self.config.entrypoint!r} is not a registered Edron page"
            ) from exc

        responses: dict[str, SimulationResponse] = {}
        for route in routes:
            values = self.route_values.get(route.key, {})
            request = SimulationRequest(
                method=route.method,
                path=route.path,
                values=values,
            )
            try:
                responses[route.key] = await surface.dispatch(route, request)
            except Exception as exc:
                raise SimulationBuildError(f"{route.key} failed during simulation build") from exc

        fragment_html = {
            route.logical_id: self._render_response(responses[route.key])
            for route in routes
            if route.kind == "fragment"
        }
        sim_app = SimApp(
            title=self.app.title,
            demo_id=self.config.demo_id,
        )
        page_response = responses[entrypoint.key]

        def initial_page() -> Any:
            return page_response.value

        sim_app.page(self.config.entrypoint)(initial_page)

        for route in routes:
            response = responses[route.key]
            effects = self._effects(response, routes, fragment_html)
            handler = self._constant_handler(self._renderable(response.value))
            regions = tuple(
                FragmentRegion(region.id, region.selector, region.description)
                for region in route.regions
            )
            if route.kind == "action":
                sim_app.action(
                    route.path,
                    method=route.method,
                    regions=regions,
                    effects=effects,
                )(handler)
            elif route.kind in {"fragment", "page"}:
                sim_app.fragment(
                    route.path,
                    method=route.method,
                    regions=regions,
                    effects=effects,
                )(handler)

        html = embed_demo(sim_app, class_="hedron-sim edron-sim", trace=True)
        if len(html.encode("utf-8")) > self.config.max_html_bytes:
            raise SimulationBuildError(
                f"simulation HTML exceeds max_html_bytes={self.config.max_html_bytes}"
            )
        manifest = {
            "schema": EDRON_SIM_SCHEMA,
            "title": self.app.title,
            "entrypoint": self.config.entrypoint,
            "routes": [self._route_manifest(route) for route in routes],
            "source": self.app.manifest(),
            "callbacks_executed": True,
            "bounds": {
                "max_routes": self.config.max_routes,
                "max_html_bytes": self.config.max_html_bytes,
            },
        }
        return SimulationArtifact(html=html, manifest=manifest, responses=responses)

    @staticmethod
    def _constant_handler(value: Any) -> Any:
        def handler() -> Any:
            return value

        return handler

    @staticmethod
    def _renderable(value: Any) -> Any:
        if isinstance(value, Outcome):
            # Outcome headers are transport mechanics. Keep the static primary
            # response empty; refresh outcomes are represented as explicit
            # effects below rather than inventing UI that the app did not emit.
            return InteractionResult(content=None, status_code=200)
        if value is None:
            return InteractionResult(content=None, status_code=200)
        return value

    @classmethod
    def _render_response(cls, response: SimulationResponse) -> str:
        return render_handler_html(cls._renderable(response.value))

    @staticmethod
    def _effects(
        response: SimulationResponse,
        routes: Sequence[SimulationRoute],
        fragment_html: Mapping[str, str],
    ) -> tuple[Mapping[str, Any], ...]:
        value = response.value
        if not isinstance(value, Outcome):
            return ()
        if value.role is not OutcomeKind.REFRESH:
            return ()
        by_id = {route.logical_id: route for route in routes if route.kind == "fragment"}
        effects: list[Mapping[str, Any]] = []
        raw_handles = value.payload.get("handles", [])
        handles = cast(list[object], raw_handles) if isinstance(raw_handles, list) else []
        for handle in handles:
            route = by_id.get(str(handle))
            if route is None or not route.regions:
                continue
            effects.append(
                {
                    "type": "refresh",
                    "target": route.regions[0].selector,
                    "html": fragment_html.get(route.logical_id, ""),
                }
            )
        return tuple(effects)

    @staticmethod
    def _route_manifest(route: SimulationRoute) -> Mapping[str, Any]:
        return {
            "method": route.method,
            "path": route.path,
            "name": route.name,
            "kind": route.kind,
            "logical_id": route.logical_id,
            "regions": [
                {"id": region.id, "selector": region.selector, "description": region.description}
                for region in route.regions
            ],
        }
