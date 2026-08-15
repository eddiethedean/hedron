from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from pydantic import BaseModel
from starlette.requests import Request

from hedron.connections import ConnectionRegistry
from hedron.state import SessionState, session_state
from hedron_core.builtins.forms import Hx
from hedron_core.builtins.shell import HtmxLink
from hedron_core.interaction import (
    FragmentRegion,
    InteractionPolicy,
    InteractionResult,
    OobUpdate,
    materialize_interaction_nodes,
)
from hedron_elements import (
    BrowserTrace,
    CompositionEdge,
    DraftTransferEnvelope,
    subject_fingerprint,
)


def test_composition_edge_bounds_and_trace_privacy() -> None:
    edge = CompositionEdge(
        id="filter.customers",
        event="hedron-filter",
        action="filter",
        target="results",
        detail_keys=("query",),
    )
    assert edge.as_payload()["fallback"] == "native"
    assert (
        BrowserTrace(correlation_id="c1", element_id="e1", outcome="success").as_payload()[
            "outcome"
        ]
        == "success"
    )
    with pytest.raises(ValueError):
        CompositionEdge(id="bad id", event="x", action="a", target="t")


def test_draft_transfer_is_subject_bound_bounded_and_forbids_capabilities() -> None:
    subject = subject_fingerprint("user-1", "authority-4")
    env = DraftTransferEnvelope.create(
        app="app",
        route_family="edit",
        element_contract="hedron-field-text",
        schema_version="1",
        subject=subject,
        fields={"title": "Draft"},
        operation_id="op-1",
        now=100,
        ttl_seconds=60,
    )
    assert env.storage_key.startswith("hedron:draft:v1:")
    assert json.loads(env.to_json())["fields"] == {"title": "Draft"}
    with pytest.raises(ValueError, match="forbidden draft field"):
        DraftTransferEnvelope.create(
            app="app",
            route_family="edit",
            element_contract="x",
            schema_version="1",
            subject=subject,
            fields={"csrf_token": "x"},
            operation_id="op-2",
            now=100,
        )


def test_select_oob_parity_and_duplicate_oob_rejection() -> None:
    assert Hx(select_oob="#a, #b").as_html_attrs()["hx-select-oob"] == "#a, #b"
    assert HtmxLink("go", "/", select_oob="#a, #b").props.select_oob == "#a, #b"
    result = InteractionResult(
        content="main",
        region_id="main",
        policy=InteractionPolicy(
            declared_regions=(
                FragmentRegion(id="main", selector="#main"),
                FragmentRegion(id="side", selector="#side"),
            )
        ),
        oob=(OobUpdate(content="a", element_id="side"), OobUpdate(content="b", element_id="side")),
    )
    with pytest.raises(ValueError, match="duplicate OobUpdate"):
        materialize_interaction_nodes(result)


class Settings(BaseModel):
    count: int = 0


def test_session_state_refresh_and_dependency_identity() -> None:
    request = Request({"type": "http", "session": {"settings": {"count": 1}}, "headers": []})
    state = SessionState(request, "settings", Settings)
    request.session["settings"] = {"count": 2}
    assert state.value.count == 2
    assert (
        session_state("settings", Settings).dependency
        is session_state("settings", Settings).dependency
    )


def test_connection_registry_single_flight() -> None:
    registry = ConnectionRegistry()
    calls = 0

    def factory() -> object:
        nonlocal calls
        calls += 1
        return object()

    registry.register("db", factory)
    with ThreadPoolExecutor(max_workers=8) as pool:
        values = list(pool.map(lambda _: registry.get("db"), range(32)))
    assert calls == 1
    assert len({id(value) for value in values}) == 1
