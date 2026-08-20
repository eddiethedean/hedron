"""ROUTEURL-052 evidence."""

from __future__ import annotations

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
    assert (
        "next=%2Fhome" in response.headers["location"]
        or "next=/home" in response.headers["location"]
    )
    named_redirect = app.redirect_for("profile", query={"q": "1"})
    assert "q=1" in named_redirect.headers["location"]
