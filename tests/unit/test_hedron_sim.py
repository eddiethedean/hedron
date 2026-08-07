"""Unit tests for hedron-sim offline HTMX embeds."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

from hedron import (
    InteractionResult,
    OobHost,
    OobUpdate,
    Page,
    RefreshButton,
    Text,
    html,
    swap,
)
from hedron_core.interaction import InteractionPolicy
from hedron_core.rendering import RenderMode
from hedron_sim import (
    SIM_LOCAL_TIME,
    SIM_UTC,
    SimApp,
    embed_demo,
    render_handler_html,
    sim_form,
    sim_local_time,
    sim_utc,
    wrap_browser_chrome,
)
from hedron_sim.assets import copy_assets, css_text, javascript_text
from hedron_sim.embed import route_table

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"


def _hello_app() -> SimApp:
    app = SimApp(title="Sim test", demo_id="unit-hello")
    status = app.region("service-status")

    def panel():
        return html.div(
            Text(f"up {sim_utc()}"),
            id=status.id,
            role="status",
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Text("Hello"),
            panel(),
            RefreshButton.for_region(status, href="/status", label="Refresh"),
            title="Home",
        )

    @app.fragment("/status", region=status)
    def refresh():
        return swap(panel())

    return app


def test_embed_demo_includes_real_hx_attrs_and_route_table() -> None:
    html_out = embed_demo(_hello_app())
    assert 'data-hedron-sim="unit-hello"' in html_out
    assert 'hx-get="/status"' in html_out or "hx-get='/status'" in html_out
    assert 'hx-target="#service-status"' in html_out
    assert "hx-swap" in html_out
    assert "data-hedron-sim-routes" in html_out
    assert "<template data-hedron-sim-routes>" in html_out
    assert '<script type="application/json" data-hedron-sim-routes>' not in html_out
    assert SIM_UTC in html_out
    assert "data-hedron-sim-trace" in html_out
    assert "data-hedron-sim-stage" in html_out

    match = re.search(
        r"<(?:template|script)[^>]*data-hedron-sim-routes[^>]*>(.*?)</(?:template|script)>",
        html_out,
        flags=re.DOTALL,
    )
    assert match is not None
    raw = (
        match.group(1)
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
        .replace("\\u003c", "<")
    )
    payload = json.loads(raw)
    assert "GET /status" in payload["routes"]
    route = payload["routes"]["GET /status"]
    assert route["status"] == 200
    assert route["regions"][0]["selector"] == "#service-status"
    assert SIM_UTC in route["html"]
    assert 'id="service-status"' in route["html"]


def test_route_table_allowlist_payload() -> None:
    table = route_table(_hello_app())
    assert table["demoId"] == "unit-hello"
    assert table["routes"]["GET /status"]["regions"][0]["id"] == "service-status"


def test_route_table_sequence_and_variants() -> None:
    app = SimApp(demo_id="seq")
    region = app.region("panel")

    @app.page("/")
    def home() -> Page:
        return Page(html.div(id=region.id), title="x")

    @app.fragment(
        "/tick",
        region=region,
        sequence=(
            lambda: swap(html.div("one", id=region.id)),
            lambda: swap(html.div("two", id=region.id)),
        ),
    )
    def tick():
        return swap(html.div("one", id=region.id))

    @app.action(
        "/invite",
        region=region,
        validate="email",
        variants={
            "invalid": lambda: swap(html.div("bad", id=region.id)),
            "valid": lambda: swap(html.div("ok", id=region.id)),
        },
    )
    def invite():
        return swap(html.div("bad", id=region.id))

    table = route_table(app)
    assert len(table["routes"]["GET /tick"]["sequence"]) == 2
    assert table["routes"]["POST /invite"]["validate"] == "email"
    assert "valid" in table["routes"]["POST /invite"]["variants"]
    assert "ok" in table["routes"]["POST /invite"]["variants"]["valid"]["html"]


def test_route_table_credentials_validate() -> None:
    app = SimApp(demo_id="auth")
    region = app.region("panel")

    @app.page("/")
    def home() -> Page:
        return Page(html.div(id=region.id), title="x")

    @app.action(
        "/login",
        region=region,
        validate="credentials",
        variants={
            "invalid": lambda: InteractionResult(
                content=html.div("bad", id=region.id),
                status_code=401,
                region_id=region.id,
            ),
            "valid": lambda: swap(html.div("ok", id=region.id)),
        },
    )
    def login():
        return swap(html.div("bad", id=region.id))

    table = route_table(app)
    assert table["routes"]["POST /login"]["validate"] == "credentials"
    assert table["routes"]["POST /login"]["variants"]["invalid"]["status"] == 401
    assert "ok" in table["routes"]["POST /login"]["variants"]["valid"]["html"]


def test_route_table_accumulate_and_list_remove() -> None:
    app = SimApp(demo_id="list")
    listing = app.region("notes")

    @app.page("/")
    def home() -> Page:
        return Page(html.div(id=listing.id), title="x")

    @app.action(
        "/notes",
        region=listing,
        accumulate="note",
        empty=lambda: swap(html.div(html.p("empty"), id=listing.id)),
    )
    def add():
        return swap(html.li(sim_form("note")))

    @app.fragment("/notes/item", region=listing, method="DELETE", list_remove=True)
    def remove():
        return swap(html.div(html.p("empty"), id=listing.id))

    table = route_table(app)
    acc = table["routes"]["POST /notes"]["accumulate"]
    assert acc["field"] == "note"
    assert "__HEDRON_SIM_FORM:note__" in acc["itemHtml"]
    assert "empty" in acc["emptyHtml"]
    assert table["routes"]["DELETE /notes/item"]["listRemove"] is True


def test_accumulate_requires_empty_handler() -> None:
    app = SimApp(demo_id="bad")
    listing = app.region("notes")

    @app.page("/")
    def home() -> Page:
        return Page(html.div(id=listing.id), title="x")

    with pytest.raises(ValueError, match="empty"):

        @app.action("/notes", region=listing, accumulate="note")
        def add():
            return swap(html.li(sim_form("note")))


def test_embed_requires_page() -> None:
    app = SimApp(demo_id="empty")
    with pytest.raises(ValueError, match="page"):
        embed_demo(app)


def test_embed_escapes_script_breakouts_in_route_json() -> None:
    app = SimApp(demo_id="xss")
    region = app.region("panel")

    @app.page("/")
    def home() -> Page:
        return Page(html.div(id=region.id), title="x")

    @app.fragment("/evil", region=region)
    def evil():
        return swap(html.div("</script><img src=x onerror=alert(1)>", id=region.id))

    out = embed_demo(app)
    # Raw breakout must not appear as a live HTML end-tag inside the JSON script.
    assert "</script><img" not in out
    assert "&lt;" in out and "</script><img" not in out
    match = re.search(
        r"<(?:template|script)[^>]*data-hedron-sim-routes[^>]*>(.*?)</(?:template|script)>",
        out,
        flags=re.DOTALL,
    )
    assert match is not None
    payload = json.loads(
        match.group(1)
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
        .replace("\\u003c", "<")
    )
    body = payload["routes"]["GET /evil"]["html"]
    assert "panel" in body
    assert "script" in body.lower()
    assert "onerror" in body.lower() or "alert" in body.lower() or "&lt;" in body


def test_embed_demo_extra_attrs_and_trace_off() -> None:
    out = embed_demo(_hello_app(), trace=False, attrs={"data-demo": 'a"b'})
    assert "data-hedron-sim-trace" not in out
    assert 'data-demo="a&quot;b"' in out


def test_wrap_browser_chrome_escapes_url_and_wraps_island() -> None:
    island = embed_demo(_hello_app(), class_="hedron-sim hedron-sim--browser")
    wrapped = wrap_browser_chrome(
        island,
        url="127.0.0.1:8000/<script>",
        logo_src='assets/"mark".svg',
        caption="Click <strong>Refresh</strong>",
    )
    assert "hedron-browser-sim" in wrapped
    assert "&lt;script&gt;" in wrapped
    assert 'src="assets/&quot;mark&quot;.svg"' in wrapped
    assert "Click <strong>Refresh</strong>" in wrapped
    assert 'data-hedron-sim="unit-hello"' in wrapped


def test_render_handler_html_page_vs_fragment() -> None:
    page = Page(html.div("body-only", id="service-status"), title="Status")
    page_html = render_handler_html(page, mode=RenderMode.PAGE)
    frag_html = render_handler_html(page, mode=RenderMode.FRAGMENT)
    assert "<!DOCTYPE html>" in page_html or "<!doctype html>" in page_html.lower()
    assert "<html" in page_html.lower()
    assert "body-only" in frag_html
    assert "<html" not in frag_html.lower()


def test_render_handler_html_interaction_result_and_none() -> None:
    assert render_handler_html(None) == ""
    result = InteractionResult(content=html.div("ok", id="panel"), status_code=201)
    assert 'id="panel"' in render_handler_html(result)
    assert "ok" in render_handler_html(result)


def test_route_table_includes_oob_markup() -> None:
    app = SimApp(demo_id="oob")
    main = app.region("primary")
    host = app.region("toast-host")

    @app.page("/")
    def home() -> Page:
        return Page(
            html.div(id=main.id),
            OobHost(id=host.id),
            title="oob",
        )

    @app.action("/save", regions=(main, host))
    def save():
        return InteractionResult(
            content=html.div("saved", id=main.id),
            oob=(
                OobUpdate(
                    content=OobHost(html.span("toast"), id=host.id),
                    element_id=host.id,
                ),
            ),
            policy=InteractionPolicy(declared_regions=(main, host)),
        )

    table = route_table(app)
    html_out = table["routes"]["POST /save"]["html"]
    assert "hx-swap-oob" in html_out
    assert 'id="toast-host"' in html_out
    assert "saved" in html_out


def test_delete_and_query_path_routes() -> None:
    app = SimApp(demo_id="methods")
    region = app.region("row")

    @app.page("/")
    def home() -> Page:
        return Page(html.div(id=region.id), title="x")

    @app.fragment("/items/1", region=region, method="DELETE")
    def delete():
        return swap(html.div("gone", id=region.id))

    @app.fragment("/results?page=2", region=region)
    def page_two():
        return swap(html.div("page-2", id=region.id))

    table = route_table(app)
    assert "DELETE /items/1" in table["routes"]
    assert "GET /results?page=2" in table["routes"]
    assert "page-2" in table["routes"]["GET /results?page=2"]["html"]


def test_sim_tokens() -> None:
    assert sim_utc() == SIM_UTC
    assert sim_local_time() == SIM_LOCAL_TIME
    assert sim_form("email") == "__HEDRON_SIM_FORM:email__"
    assert sim_form("user-name_1") == "__HEDRON_SIM_FORM:user-name_1__"
    with pytest.raises(ValueError):
        sim_form("!!!")


def test_packaged_assets_include_theme_and_runtime_hooks() -> None:
    css = css_text()
    js = javascript_text()
    assert '[data-md-color-scheme="slate"] .hedron-sim' in css
    assert "--hs-bg" in css
    assert "--hs-accent" in css
    assert "hx-confirm" in js
    assert "data-hedron-sim-modes" in js
    assert 'hx-trigger="load"' in js or "hx-trigger" in js
    assert "regionAllows" in js
    assert "applyTokens" in js
    assert "SIM_UTC" in js or "__HEDRON_SIM_UTC__" in js
    assert "stopImmediatePropagation" in js
    assert "data-hedron-sim-href" in js
    assert "data-hedron-sim-action" in js
    assert "neutralizeProgressiveAnchors" in js or "data-hedron-sim-href" in js
    assert "enforceBootInvariants" in js
    assert "hedronSimBlocked" in js or "hedron-sim-blocked" in js
    assert "beginSimGuard" in js
    assert "accumulate" in js or "renderAccumulatedList" in js
    assert "listRemove" in js or "list_remove" in js or "listRemove" in js
    assert ", true" in js  # capture-phase listeners
    assert "<strong>HEDRON_SIM_UTC</strong>" in js  # legacy markdown-mangled token
    assert "escapeHtml(String(value))" in js  # form-token XSS guard


def test_docs_sim_js_escapes_form_tokens() -> None:
    docs_js = (DOCS / "javascript" / "hedron-sim.js").read_text(encoding="utf-8")
    assert "escapeHtml(String(value))" in docs_js
    assert docs_js == javascript_text()


def test_copy_assets_writes_js_and_css(tmp_path: Path) -> None:
    js_dir = tmp_path / "javascript"
    css_dir = tmp_path / "stylesheets"
    js_path, css_path = copy_assets(js_dir, css_dir)
    assert js_path.is_file()
    assert css_path is not None and css_path.is_file()
    assert "HedronSim" in js_path.read_text(encoding="utf-8")
    assert "--hs-bg" in css_path.read_text(encoding="utf-8")
    js_only, css_none = copy_assets(js_dir, None)
    assert js_only.is_file()
    assert css_none is None


def test_docs_theme_sync_hooks_present() -> None:
    demos_js = (DOCS / "javascript" / "component-demos.js").read_text(encoding="utf-8")
    assert "docsColorPreference" in demos_js
    assert "hdcThemeLocal" in demos_js
    assert "data-md-color-scheme" in demos_js
    assert "MutationObserver" in demos_js
    demos_css = (DOCS / "stylesheets" / "component-demos.css").read_text(encoding="utf-8")
    assert '[data-md-color-scheme="slate"] .hedron-component-demo' in demos_css


def test_docs_sim_css_mirrors_package_theme_tokens() -> None:
    docs_css = (DOCS / "stylesheets" / "hedron-sim.css").read_text(encoding="utf-8")
    assert '[data-md-color-scheme="slate"] .hedron-sim' in docs_css
    assert "--hs-bg" in docs_css


@pytest.fixture(scope="module")
def _docs_on_path() -> None:
    path = str(DOCS)
    if path not in sys.path:
        sys.path.insert(0, path)


@pytest.mark.usefixtures("_docs_on_path")
def test_all_component_demo_builders_embed() -> None:
    from demos.components import COMPONENT_DEMO_BUILDERS, build_component_demo

    assert COMPONENT_DEMO_BUILDERS
    for name in sorted(COMPONENT_DEMO_BUILDERS):
        html_out = build_component_demo(name)
        assert "data-hedron-sim" in html_out, name
        assert "data-hedron-sim-routes" in html_out, name
        match = re.search(
            r"<(?:template|script)[^>]*data-hedron-sim-routes[^>]*>(.*?)</(?:template|script)>",
            html_out,
            flags=re.DOTALL,
        )
        assert match is not None, name
        payload = json.loads(
            match.group(1)
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&amp;", "&")
            .replace("\\u003c", "<")
        )
        assert payload["routes"], name


@pytest.mark.usefixtures("_docs_on_path")
def test_core_concepts_modes_demo_renders_both_modes() -> None:
    from demos.core_concepts import build_core_concepts_modes_demo

    html_out = build_core_concepts_modes_demo()
    assert 'data-hedron-sim-modes="core-concepts"' in html_out
    assert 'data-sim-mode="page"' in html_out
    assert 'data-sim-mode="fragment"' in html_out
    assert "service-status" in html_out
    assert "&lt;" in html_out  # escaped PAGE/FRAGMENT source


@pytest.mark.usefixtures("_docs_on_path")
def test_guide_and_hello_demo_builders_embed() -> None:
    from demos.contracts import CONTRACTS

    for contract in CONTRACTS:
        if contract.mode_demo or contract.id.startswith("component-"):
            continue
        html_out = contract.builder()
        assert "data-hedron-sim" in html_out, contract.id
        if not contract.mode_demo:
            assert "data-hedron-sim-routes" in html_out, contract.id


@pytest.mark.usefixtures("_docs_on_path")
def test_allowlist_demo_registers_correct_and_wrong_targets() -> None:
    from demos.guides import build_allowlist_403_demo

    html_out = build_allowlist_403_demo()
    assert 'hx-target="#panel"' in html_out or "hx-target='#panel'" in html_out
    match = re.search(
        r"<(?:template|script)[^>]*data-hedron-sim-routes[^>]*>(.*?)</(?:template|script)>",
        html_out,
        flags=re.DOTALL,
    )
    assert match is not None
    payload = json.loads(
        match.group(1)
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
        .replace("\\u003c", "<")
    )
    # At least one route declares regions so the JS can enforce allowlists.
    assert any(route.get("regions") for route in payload["routes"].values())


@pytest.mark.usefixtures("_docs_on_path")
def test_every_sim_demo_has_runnable_app_source() -> None:
    """Delegates to the catalog suite — keep a thin alias for discoverability."""
    from demos.contracts import contract_ids
    from demos.runnable_code import runnable_path

    for sim_id in sorted(contract_ids()):
        assert runnable_path(sim_id).is_file(), sim_id


@pytest.mark.usefixtures("_docs_on_path")
def test_every_sim_include_has_demo_contract() -> None:
    from demos.contracts import CONTRACTS, contract_ids

    includes = {path.stem for path in (DOCS / "includes" / "sim").glob("*.html")}
    ids = contract_ids()
    assert includes == ids, f"missing={sorted(includes - ids)} extra={sorted(ids - includes)}"
    for contract in CONTRACTS:
        assert contract.steps, contract.id
        assert len(contract.steps) >= contract.min_steps, contract.id
