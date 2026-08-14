"""SimApp: register pages and fragments with ordinary Hedron handlers."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, TypeVar

from hedron_core.interaction import FragmentRegion

__all__ = ["SimApp", "SimRoute"]

F = TypeVar("F", bound=Callable[..., Any])
Handler = Callable[..., Any]


def _as_regions(
    region: FragmentRegion | str | None,
    regions: Sequence[FragmentRegion | str] | None,
    fragment_regions: Sequence[FragmentRegion | str] | None,
) -> tuple[FragmentRegion, ...]:
    merged: list[FragmentRegion] = []
    for item in (
        *(() if region is None else (region,)),
        *(regions or ()),
        *(fragment_regions or ()),
    ):
        if isinstance(item, FragmentRegion):
            merged.append(item)
        else:
            text = str(item)
            selector = text if text.startswith("#") or text.startswith(".") else f"#{text}"
            region_id = text[1:] if text.startswith("#") else text
            merged.append(FragmentRegion(id=region_id, selector=selector))
    return tuple(merged)


@dataclass(frozen=True, slots=True)
class SimRoute:
    """One simulated HTTP fragment/action endpoint."""

    method: str
    path: str
    handler: Handler
    regions: tuple[FragmentRegion, ...] = ()
    explanation: str = ""
    validate: str | None = None
    variants: Mapping[str, Handler] | None = None
    sequence: tuple[Handler, ...] | None = None
    accumulate: str | None = None
    """Form field name — append values into a client-side list for this region."""
    empty: Handler | None = None
    """Handler that renders the empty list container (required with ``accumulate``)."""
    list_remove: bool = False
    """DELETE (or similar): remove one list item by ``data-hedron-sim-list-index``."""

    @property
    def key(self) -> str:
        return f"{self.method.upper()} {self.path}"


@dataclass
class SimApp:
    """Register a page and fragment routes for offline HTMX simulation.

    Handlers use the same return types as a real Hedron app (``Page``, components,
    ``InteractionResult`` / ``swap(...)``). ``embed_demo`` pre-renders them into an
    HTML island plus a JSON route table consumed by ``hedron-sim.js``.

    Optional route extras:

    - ``validate="email"`` + ``variants={"invalid": ..., "valid": ...}`` for form demos
    - ``validate="credentials"`` + ``variants`` (demo user ``ada`` / ``correct-horse``)
    - ``sequence=(handler1, handler2, ...)`` for polling / multi-step GETs
    - ``accumulate="field"`` + ``empty=...`` for append-only list demos (CRUD notes)
    - ``list_remove=True`` on DELETE to drop one accumulated item by index
    """

    title: str = "Hedron sim"
    demo_id: str | None = None
    _page_path: str = field(default="/", init=False, repr=False)
    _page_handler: Handler | None = field(default=None, init=False, repr=False)
    _routes: dict[str, SimRoute] = field(
        default_factory=lambda: {},
        init=False,
        repr=False,
    )

    def region(
        self,
        id: str,
        *,
        selector: str | None = None,
        description: str = "",
    ) -> FragmentRegion:
        """Declare a fragment region (default selector ``#{id}``)."""
        return FragmentRegion(id=id, selector=selector or f"#{id}", description=description)

    def page(self, path: str = "/") -> Callable[[F], F]:
        """Register the initial document body for the demo."""

        def wrap(fn: F) -> F:
            self._page_path = path
            self._page_handler = fn
            return fn

        return wrap

    def fragment(
        self,
        path: str,
        *,
        region: FragmentRegion | str | None = None,
        regions: Sequence[FragmentRegion | str] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        method: str = "GET",
        explanation: str = "",
        validate: str | None = None,
        variants: Mapping[str, Handler] | None = None,
        sequence: Sequence[Handler] | None = None,
        accumulate: str | None = None,
        empty: Handler | None = None,
        list_remove: bool = False,
    ) -> Callable[[F], F]:
        """Register a fragment endpoint with an optional region allowlist."""

        def wrap(fn: F) -> F:
            if accumulate and empty is None:
                raise ValueError("accumulate=... requires empty= handler for the empty list UI")
            route = SimRoute(
                method=method.upper(),
                path=path,
                handler=fn,
                regions=_as_regions(region, regions, fragment_regions),
                explanation=explanation,
                validate=validate,
                variants=dict(variants) if variants else None,
                sequence=tuple(sequence) if sequence else None,
                accumulate=accumulate,
                empty=empty,
                list_remove=list_remove,
            )
            self._register_route(route)
            return fn

        return wrap

    def _register_route(self, route: SimRoute) -> None:
        """Store a route; fail closed on duplicate METHOD/path keys (#209)."""
        if route.key in self._routes:
            raise ValueError(
                f"Duplicate SimApp route registration for {route.key!r}; "
                "each METHOD path may only be registered once."
            )
        self._routes[route.key] = route

    def action(
        self,
        path: str,
        *,
        region: FragmentRegion | str | None = None,
        regions: Sequence[FragmentRegion | str] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        method: str = "POST",
        explanation: str = "",
        validate: str | None = None,
        variants: Mapping[str, Handler] | None = None,
        sequence: Sequence[Handler] | None = None,
        accumulate: str | None = None,
        empty: Handler | None = None,
        list_remove: bool = False,
    ) -> Callable[[F], F]:
        """Register a mutation endpoint (default POST) for form demos."""
        return self.fragment(
            path,
            region=region,
            regions=regions,
            fragment_regions=fragment_regions,
            method=method,
            explanation=explanation,
            validate=validate,
            variants=variants,
            sequence=sequence,
            accumulate=accumulate,
            empty=empty,
            list_remove=list_remove,
        )

    @property
    def page_handler(self) -> Handler | None:
        return self._page_handler

    @property
    def page_path(self) -> str:
        return self._page_path

    @property
    def routes(self) -> dict[str, SimRoute]:
        return dict(self._routes)
