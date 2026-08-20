"""ROUTEURL-052 evidence."""

from __future__ import annotations

import pytest
from starlette.responses import RedirectResponse

from hedron_posit import HedronPosit, PositConfig, compose_local_url
from hedron_posit.config import WorkbenchConfig, WorkbenchMode


def test_compose_local_url_query_fragment() -> None:
    assert (
        compose_local_url("/profile", mount="/apps/demo", query={"tab": "1"}, fragment="main")
        == "/apps/demo/profile?tab=1#main"
    )


def test_href_redirect_query_fragment_parity() -> None:
    app = HedronPosit(
        title="routeurl-052",
        posit=PositConfig(
            workbench=WorkbenchConfig(mode=WorkbenchMode.ON, mount="/s/abc/p/xyz/"),
        ),
        session_secret="test-secret-routeurl",
        external_base_url="https://example.invalid/apps/demo/",
    )

    @app.get("/profile")
    async def profile() -> dict[str, str]:
        return {"ok": "1"}

    href = app.href("/profile", query={"tab": "x"}, fragment="sec")
    assert href.endswith("/profile?tab=x#sec")
    assert href.startswith("/s/abc/p/xyz")
    named = app.href_for("profile", query={"tab": "y"}, fragment="top")
    assert "tab=y" in named and named.endswith("#top")
    response = app.redirect("/profile", query={"next": "/home"}, fragment="box")
    assert isinstance(response, RedirectResponse)
    assert "next=" in response.headers["location"]
    named_redirect = app.redirect_for("profile", query={"q": "1"})
    assert "q=1" in named_redirect.headers["location"]


def test_browser_and_durable_url_query_fragment_parity() -> None:
    app = HedronPosit(
        title="routeurl-durable",
        posit=PositConfig(
            workbench=WorkbenchConfig(mode=WorkbenchMode.ON, mount="/s/abc/p/xyz/"),
        ),
        session_secret="test-secret-routeurl-durable",
        external_base_url="https://example.invalid/apps/demo/",
    )

    @app.get("/callback")
    async def callback() -> dict[str, str]:
        return {"ok": "1"}

    browser = app.browser_url("/callback", query={"state": "1"}, fragment="done")
    assert browser.startswith("https://example.invalid/apps/demo/callback")
    assert "state=1" in browser and browser.endswith("#done")
    durable = app.durable_url("/callback", query={"code": "x"}, fragment="top")
    assert durable.startswith("https://example.invalid/apps/demo/callback")
    assert "code=x" in durable and durable.endswith("#top")
    named = app.browser_url_for("callback", query={"n": "2"})
    assert "n=2" in named
    durable_named = app.durable_url_for("callback", query={"n": "3"})
    assert "n=3" in durable_named


def test_ephemeral_workbench_mount_rejects_durable_url() -> None:
    app = HedronPosit(
        title="routeurl-ephemeral",
        posit=PositConfig(
            workbench=WorkbenchConfig(
                mode=WorkbenchMode.ON,
                mount="/s/abc/p/xyz/",
                public_base_url="https://workbench.invalid/s/abc/p/xyz/",
            ),
        ),
        session_secret="test-secret-routeurl-eph",
    )
    with pytest.raises(ValueError, match="ephemeral"):
        app.durable_url("/callback")


def test_compose_local_url_rejects_none_query_value() -> None:
    with pytest.raises(ValueError, match="must not be None"):
        compose_local_url("/p", mount="/m", query={"a": None})
