"""Phase 0.15 named connection registry tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from hedron import Hedron
from hedron.connections import (
    ConnectionRegistry,
    ConnectionSpec,
    bind_connection_fixture,
    get_connection,
    install_connections,
)
from hedron_core.testing.fixtures import NamedConnectionFixture


class _Conn:
    def __init__(self, label: str) -> None:
        self.label = label
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_register_get_reuses_same_instance() -> None:
    registry = ConnectionRegistry()
    created: list[_Conn] = []

    def factory() -> _Conn:
        conn = _Conn(f"n{len(created)}")
        created.append(conn)
        return conn

    registry.register("db", factory, kind="custom")
    a = registry.get("db")
    b = registry.get("db")
    assert a is b
    assert len(created) == 1
    assert a.label == "n0"


def test_reset_creates_new_instance() -> None:
    registry = ConnectionRegistry()
    created: list[_Conn] = []

    def factory() -> _Conn:
        conn = _Conn(f"n{len(created)}")
        created.append(conn)
        return conn

    registry.register("db", factory)
    first = registry.get("db")
    registry.reset("db")
    assert first.closed is True
    second = registry.get("db")
    assert second is not first
    assert len(created) == 2


def test_missing_name_raises() -> None:
    registry = ConnectionRegistry()
    with pytest.raises(KeyError, match="unknown connection"):
        registry.get("missing")
    with pytest.raises(KeyError, match="unknown connection"):
        registry.health("missing")
    with pytest.raises(KeyError, match="unknown connection"):
        registry.reset("missing")


def test_health_callable() -> None:
    registry = ConnectionRegistry()
    registry.register(
        "ok",
        lambda: _Conn("ok"),
        healthcheck=lambda conn: conn.label == "ok",
    )
    registry.register(
        "bad",
        lambda: _Conn("bad"),
        healthcheck=lambda conn: False,
    )
    registry.register(
        "boom",
        lambda: _Conn("boom"),
        healthcheck=lambda conn: (_ for _ in ()).throw(RuntimeError("fail")),
    )
    assert registry.health("ok") is True
    assert registry.health("bad") is False
    assert registry.health("boom") is False
    assert registry.spec("ok").healthcheck == "healthcheck"


def test_connection_spec_fields() -> None:
    spec = ConnectionSpec(
        name="warehouse",
        kind="snowflake",
        config={"account": "ref://acct"},
        healthcheck="ping",
    )
    assert spec.name == "warehouse"
    assert spec.kind == "snowflake"
    assert spec.config["account"] == "ref://acct"
    assert spec.healthcheck == "ping"


def test_install_on_hedron_sets_app_state() -> None:
    app = Hedron()
    registry = ConnectionRegistry()
    registry.register("primary", lambda: _Conn("primary"), kind="sqlalchemy")
    install_connections(app, registry)
    assert app.state.hedron_connections is registry

    with TestClient(app) as client:
        assert client.app.state.hedron_connections is registry  # type: ignore[attr-defined]
        conn = registry.get("primary")
        assert conn.label == "primary"
    # Lifespan shutdown disposes cached instances.
    assert conn.closed is True


def test_install_on_fastapi_and_dependency() -> None:
    app = FastAPI()
    registry = ConnectionRegistry()
    counter = {"n": 0}

    def factory() -> dict[str, int]:
        counter["n"] += 1
        return {"n": counter["n"]}

    registry.register("svc", factory)
    install_connections(app, registry)

    @app.get("/conn")
    def read_conn(request: Request) -> dict[str, int]:
        return get_connection(request, "svc")

    @app.get("/dep")
    def read_dep(request: Request) -> dict[str, int]:
        return get_connection(request, "svc")

    with TestClient(app) as client:
        assert client.app.state.hedron_connections is registry
        r1 = client.get("/conn")
        r2 = client.get("/dep")
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json() == r2.json() == {"n": 1}


def test_close_all_disposes_instances() -> None:
    registry = ConnectionRegistry()
    registry.register("a", lambda: _Conn("a"))
    registry.register("b", lambda: _Conn("b"))
    a = registry.get("a")
    b = registry.get("b")
    registry.close_all()
    assert a.closed and b.closed
    assert registry.get("a") is not a


def test_bind_connection_fixture() -> None:
    registry = ConnectionRegistry()
    fixture = NamedConnectionFixture(
        name="analytics",
        provider="snowflake",
        dsn="secret://snowflake/dsn",
        options={"warehouse": "WH"},
    )
    spec = bind_connection_fixture(registry, fixture)
    assert spec.name == "analytics"
    assert spec.kind == "snowflake"
    assert "dsn" in spec.config
    bound = registry.get("analytics")
    assert bound["name"] == "analytics"
    assert bound["provider"] == "snowflake"
    assert bound["options"]["warehouse"] == "WH"
