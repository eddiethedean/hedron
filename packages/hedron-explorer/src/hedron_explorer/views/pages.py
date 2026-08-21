"""Explorer HTML page builders. Routes stay in router.py."""

from __future__ import annotations

import html as html_lib
import logging
from pathlib import Path
from typing import cast

from fastapi import HTTPException, Request

from hedron_core.component import Component
from hedron_core.plugins import ExplorerProvider
from hedron_core.registry import get_registry
from hedron_core.rendering import NodeLike, RenderMode, render
from hedron_core.typing_aliases import JsonObject
from hedron_explorer.services.catalog import (
    a11y_contracts,
    app_catalog,
    find_component,
    graph_json,
    page_components,
    page_interactions,
    page_routes,
    security_json,
)
from hedron_explorer.services.diff import explorer_diff_report, format_diff_html
from hedron_explorer.services.fs import hdj_text_under_root, project_component_roots
from hedron_explorer.services.health import package_health
from hedron_explorer.services.provider import providers_or_defaults, run_isolated
from hedron_explorer.services.query import (
    CACHE_LIMIT,
    Page,
    paginate,
    parse_cursor,
    parse_limit,
    truncation_banner,
)
from hedron_explorer.views.shell import (
    component_detail_body,
    component_href,
    explorer_href,
    handle_graph_html,
    shell,
)

_logger = logging.getLogger("hedron.explorer")


async def index(request: Request) -> str:
    page = page_components(request)
    rows = "".join(
        f"<tr><td><a href='{component_href(request, c.name)}'>"
        f"{html_lib.escape(c.name)}</a></td>"
        f"<td><code>{html_lib.escape(c.logical_id)}</code></td>"
        f"<td>{html_lib.escape(c.distribution)}</td></tr>"
        for c in page.items
    )
    body = f"""
    <h2>Components</h2>
    {truncation_banner(page, noun="components", request=request)}
    <form method="get" action="">
      <label>Search <input type="search" name="q"
        value="{html_lib.escape(request.query_params.get("q") or "")}"></label>
      <button type="submit">Filter</button>
    </form>
    <table>
      <thead><tr><th>Name</th><th>Logical ID</th><th>Distribution</th></tr></thead>
      <tbody>{rows or "<tr><td colspan='3'>No components</td></tr>"}</tbody>
    </table>
    """
    return shell("Components", body, request=request, active="components")


async def routes_view(request: Request) -> str:
    page = page_routes(request)
    rows = "".join(
        f"<tr><td>{html_lib.escape(r.kind)}</td><td>{html_lib.escape(r.name)}</td>"
        f"<td><code>{html_lib.escape(r.path)}</code></td>"
        f"<td>{html_lib.escape(','.join(r.methods))}</td>"
        f"<td><code>{html_lib.escape(str(dict(r.htmx_inference)))}</code></td></tr>"
        for r in page.items
    )
    body = f"""
    <h2>Routes</h2>
    {truncation_banner(page, noun="routes", request=request)}
    <form method="get" action="">
      <label>Search <input type="search" name="q"
        value="{html_lib.escape(request.query_params.get("q") or "")}"></label>
      <button type="submit">Filter</button>
    </form>
    <table>
      <thead>
        <tr><th>Kind</th><th>Name</th><th>Path</th><th>Methods</th><th>HTMX</th></tr>
      </thead>
      <tbody>{rows or "<tr><td colspan='5'>No routes</td></tr>"}</tbody>
    </table>
    """
    return shell("Routes", body, request=request, active="routes")


async def component_detail(name: str, request: Request) -> str:
    meta = find_component(name)
    if meta is None:
        raise HTTPException(status_code=404, detail=f"Unknown component {name}")
    return shell(
        meta.name, component_detail_body(meta, request), request=request, active="components"
    )


async def graph_view(request: Request) -> str:
    payload = graph_json(request)
    next_cursor = payload.get("next_cursor")
    diagnostic = payload.get("diagnostic")
    graph_page = Page(
        items=list(payload["nodes"]),
        total=int(payload["total"]),
        limit=int(payload["limit"]),
        offset=int(payload["offset"]),
        next_cursor=next_cursor if isinstance(next_cursor, str) else None,
        truncated=bool(payload["truncated"]),
        diagnostic=diagnostic if isinstance(diagnostic, str) else None,
    )
    items = "".join(
        f"<li>{html_lib.escape(str(edge.get('from')))} → "
        f"{html_lib.escape(str(edge.get('kind')))} "
        f"{html_lib.escape(str(edge.get('to')))}</li>"
        for edge in payload.get("edges") or []
        if isinstance(edge, dict)
    )
    return shell(
        "Graph",
        (
            f"<h2>Component graph</h2>"
            f"{truncation_banner(graph_page, noun='graph nodes', request=request)}"
            f"<ul>{items or '<li>No edges</li>'}</ul>"
            f"<h2>View / command graph</h2>{handle_graph_html(request)}"
        ),
        request=request,
        active="graph",
    )


async def security_view(request: Request) -> str:
    payload = security_json(request)
    findings = payload.get("findings") or []
    items = "".join(f"<li>{html_lib.escape(str(f))}</li>" for f in findings)
    audit = payload.get("audit_tail") or []
    audit_items = "".join(f"<li><pre>{html_lib.escape(str(entry))}</pre></li>" for entry in audit)
    return shell(
        "Security",
        (
            f"<h2>Security findings</h2><ul>{items}</ul>"
            f"<h2>Audit tail</h2>"
            f"<ul>{audit_items or '<li>No audit events</li>'}</ul>"
        ),
        request=request,
        active="security",
    )


async def a11y_view(request: Request) -> str:
    from hedron_core import Main, Page, Text, render
    from hedron_core.a11y import (
        ACCESSIBILITY_PROFILE,
        AccessibilityContractCatalog,
        AccessibilityScenario,
        seed_reviewed_contracts,
        validate_page_structure,
    )
    from hedron_core.html import html as h
    from hedron_core.security import SafeUrl, UrlPurpose

    catalog = AccessibilityContractCatalog()
    seed_reviewed_contracts(catalog)
    catalog.ensure_registry()
    all_contracts = list(catalog.contracts.values())
    reviewed_count = sum(1 for c in all_contracts if c.reviewed)
    total = len(all_contracts)
    page = a11y_contracts(request=request)
    shown = page.items
    rows = "".join(
        "<tr>"
        f"<td>{html_lib.escape(c.component)}</td>"
        f"<td>{'yes' if c.reviewed else 'stub'}</td>"
        f"<td>{html_lib.escape(c.native_semantics or '—')}</td>"
        f"<td>{html_lib.escape(c.keyboard or '—')}</td>"
        f"<td>{html_lib.escape(c.notes or '—')}</td>"
        "</tr>"
        for c in shown
    )
    sample = render(
        Page(
            h.a(
                "Skip to content",
                href=SafeUrl.parse("#main", purpose=UrlPurpose.NAVIGATION),
            ),
            Main(h.h1("Explorer sample"), Text("outline"), id="main"),
            title="Explorer a11y sample",
            lang="en",
        )
    ).html
    structure = validate_page_structure(sample)
    landmark_items = (
        "".join(f"<li><code>{html_lib.escape(name)}</code></li>" for name in structure.landmarks)
        or "<li>(none)</li>"
    )
    heading_items = (
        "".join(f"<li><code>{html_lib.escape(name)}</code></li>" for name in structure.headings)
        or "<li>(none)</li>"
    )
    profile = ACCESSIBILITY_PROFILE.as_dict()
    scenario = AccessibilityScenario(
        name="explorer-review",
        covers=("keyboard", "focus", "announcements"),
    )
    summary = scenario.summarize()
    modes = [
        "contrast / non-text contrast",
        "target spacing",
        "focus obstruction",
        "text spacing",
        "zoom / reflow / orientation",
        "reduced motion",
        "forced colors",
        "media alternatives",
        "visualization fallbacks",
    ]
    mode_items = "".join(f"<li>{html_lib.escape(m)}</li>" for m in modes)
    body = f"""
        <h2>Accessibility review workspace</h2>
        {truncation_banner(page, noun="contracts", request=request)}
    <p>Findings distinguish automatic, semi-automatic, and manual status.
    Empty scans never summarize as accessible
    (status: <code>{html_lib.escape(str(summary["status"]))}</code>).</p>
    <section aria-labelledby="a11y-profile">
      <h3 id="a11y-profile">Standards profile</h3>
      <dl>
        <dt>Profile</dt><dd><code>{html_lib.escape(str(profile["profile_id"]))}</code></dd>
        <dt>WCAG</dt><dd>{html_lib.escape(str(profile["wcag_version"]))}
          {"/".join(str(level) for level in cast(list[object], profile["wcag_levels"]))}</dd>
        <dt>WAI-ARIA</dt><dd>{html_lib.escape(str(profile["wai_aria_version"]))}</dd>
      </dl>
    </section>
    <section aria-labelledby="a11y-tree">
      <h3 id="a11y-tree">Structure outline</h3>
      <p>Headings and landmarks from a sample Page render
      (<code>validate_page_structure</code>). Browser accessibility trees and
      live-region logs remain review-mode checklists / Playwright evidence,
      not a live AT tree in Explorer.</p>
      <h4>Landmarks</h4>
      <ul>{landmark_items}</ul>
      <h4>Headings</h4>
      <ul>{heading_items}</ul>
      <h4>Review modes</h4>
      <ul>{mode_items}</ul>
    </section>
    <section aria-labelledby="a11y-contracts">
      <h3 id="a11y-contracts">Component contracts</h3>
      <p>Showing {len(shown)} of {total} contracts
      ({reviewed_count} reviewed; curated REQUIRED set plus registry stubs).</p>
      <table>
        <thead><tr><th>Component</th><th>Reviewed</th><th>Semantics</th>
        <th>Keyboard</th><th>Notes</th></tr></thead>
        <tbody>{rows or "<tr><td colspan='5'>No contracts</td></tr>"}</tbody>
      </table>
    </section>
    <section aria-labelledby="a11y-atag">
      <h3 id="a11y-atag">ATAG authoring assistance</h3>
      <p>Accessibility properties are listed alongside ordinary props on component pages.
      Repair guidance is reversible and author-reviewed; features default on.</p>
    </section>
    """
    return shell("Accessibility", body, request=request, active="a11y")


async def cache_view(request: Request) -> str:
    from hedron_core.cache import get_cache_traces

    events = [
        {
            "kind": event.kind,
            "key_fingerprint": event.key_fingerprint,
            "scope": event.scope,
            "age_ms": event.age_ms,
            "size": event.size,
            "detail": event.detail or "",
        }
        for event in reversed(get_cache_traces())
    ]
    cache_page = paginate(
        events,
        offset=parse_cursor(request),
        limit=parse_limit(request, default=CACHE_LIMIT, cap=CACHE_LIMIT),
    )
    events = cache_page.items
    rows = "".join(
        "<tr>"
        f"<td>{html_lib.escape(str(e['kind']))}</td>"
        f"<td><code>{html_lib.escape(str(e['key_fingerprint']))}</code></td>"
        f"<td>{html_lib.escape(str(e['scope']))}</td>"
        f"<td>{html_lib.escape(str(e.get('age_ms')))}</td>"
        f"<td>{html_lib.escape(str(e.get('size')))}</td>"
        f"<td>{html_lib.escape(str(e.get('detail') or ''))}</td>"
        "</tr>"
        for e in events
    )
    body = f"""
    <h2>Cache traces</h2>
    {truncation_banner(cache_page, noun="cache events", request=request)}
    <p>Key fingerprints only — secret values are never shown.</p>
    <table>
      <thead><tr><th>Kind</th><th>Key</th><th>Scope</th><th>Age ms</th>
      <th>Size</th><th>Detail</th></tr></thead>
      <tbody>{rows or "<tr><td colspan='6'>No cache activity</td></tr>"}</tbody>
    </table>
    """
    return shell("Cache", body, request=request, active="cache")


async def charts_view(request: Request) -> str:
    from hedron_core.registry import get_registry

    registry = get_registry()
    chart_components = [
        c
        for c in registry.components()
        if c.distribution == "hedron-charts"
        or c.name in {"LineChart", "MatplotlibChart", "PlotlyChart", "AltairChart"}
    ]
    rows = "".join(
        "<tr>"
        f"<td><code>{html_lib.escape(c.name)}</code></td>"
        f"<td><code>{html_lib.escape(c.distribution)}</code></td>"
        f"<td>{html_lib.escape(c.accessibility_notes or '')}</td>"
        f"<td>{'yes' if c.browser_modules else 'no'}</td>"
        "</tr>"
        for c in chart_components
    )
    assets = "".join(
        f"<li><code>{html_lib.escape(a.logical_id)}</code> ({html_lib.escape(a.kind)})</li>"
        for a in registry.assets()
        if "chart" in a.logical_id or "plotly" in a.logical_id or "vega" in a.logical_id
    )
    body = f"""
    <h2>Visualization</h2>
    <p>Charts require title and description/alt/waiver. Payload limits and secret
    redaction are enforced by adapters. Browser runtimes are pinned and local.</p>
    <h3>Registered chart components</h3>
    <table>
      <thead><tr><th>Name</th><th>Distribution</th><th>A11y notes</th>
      <th>Browser host</th></tr></thead>
      <tbody>{rows or "<tr><td colspan='4'>No chart components registered</td></tr>"}</tbody>
    </table>
    <h3>Chart assets</h3>
    <ul>{assets or "<li>No chart assets registered yet</li>"}</ul>
    <h3>Security policy</h3>
    <ul>
      <li>Reject raw JavaScript callbacks</li>
      <li>Reject unapproved remote CDN URLs</li>
      <li>Private authenticated caching defaults apply</li>
    </ul>
    """
    return shell("Charts", body, request=request, active="charts")


async def maps_view(request: Request) -> str:
    from hedron_core.registry import get_registry

    registry = get_registry()
    map_components = [
        c
        for c in registry.components()
        if c.distribution == "hedron-maps" or c.name == "Map" and "hedron_maps" in (c.module or "")
    ]
    rows = "".join(
        "<tr>"
        f"<td><code>{html_lib.escape(c.name)}</code></td>"
        f"<td><code>{html_lib.escape(c.distribution)}</code></td>"
        f"<td>{html_lib.escape(c.accessibility_notes or '')}</td>"
        "</tr>"
        for c in map_components
    )
    assets = "".join(
        f"<li><code>{html_lib.escape(a.logical_id)}</code> ({html_lib.escape(a.kind)})</li>"
        for a in registry.assets()
        if "hedron-maps" in a.logical_id or "maplibre" in a.logical_id
    )
    facts_block = _map_plan_facts_html(request)
    body = f"""
    <h2>Maps</h2>
    <p>Explorer inspects compiled MapPlan facts, origins, attribution, CSP, fallback,
    and event schemas without executing untrusted map data.</p>
    {facts_block}
    <h3>Registered map components</h3>
    <table>
      <thead><tr><th>Name</th><th>Distribution</th><th>A11y notes</th></tr></thead>
      <tbody>{rows or "<tr><td colspan='3'>No map components registered</td></tr>"}</tbody>
    </table>
    <h3>Map assets</h3>
    <ul>{assets or "<li>No map assets registered yet</li>"}</ul>
    <h3>Closed events</h3>
    <ul>
      <li>feature-selected / feature-activated</li>
      <li>viewport-changed (map.viewport)</li>
      <li>layer-visibility-changed</li>
      <li>map-loaded / map-failed</li>
    </ul>
    """
    return shell("Maps", body, request=request, active="maps")


async def extensions_view(request: Request) -> str:
    from hedron_core.htmx_extensions import catalog_facts

    facts = catalog_facts()
    rows = "".join(
        "<tr>"
        f"<td><code>{html_lib.escape(str(item.get('public_id', '')))}</code></td>"
        f"<td><code>{html_lib.escape(str(item.get('asset_name', '')))}</code></td>"
        f"<td>{html_lib.escape(str(item.get('version', '')))}</td>"
        f"<td><code>{html_lib.escape(str(item.get('hdj_extension_id', '')))}</code></td>"
        "</tr>"
        for item in facts["extensions"]
    )
    body = f"""
    <h2>HTMX extensions</h2>
    <p>Explorer lists catalog facts without executing untrusted extension code.
    Writing <code>hx-ext</code> never installs an asset. Morph is not admitted
    on this train.</p>
    <p>new_catalog_kind={facts.get("new_catalog_kind")} ·
    feature_bundle_executor={facts.get("feature_bundle_executor")} ·
    morph_admitted={facts.get("morph_admitted")}</p>
    <table>
      <thead>
        <tr><th>Public id</th><th>Asset name</th><th>Version</th><th>HDJ id</th></tr>
      </thead>
      <tbody>{rows or "<tr><td colspan='4'>No catalog facts</td></tr>"}</tbody>
    </table>
    """
    return shell("HTMX extensions", body, request=request, active="extensions")


async def data_view(request: Request) -> str:
    from hedron_core.registry import get_registry

    registry = get_registry()
    data_components = [
        c
        for c in registry.components()
        if c.name in {"DataTable", "DataEditor"} or "hedron_data" in (c.module or "")
    ]
    rows = "".join(
        "<tr>"
        f"<td><code>{html_lib.escape(c.name)}</code></td>"
        f"<td><code>{html_lib.escape(c.distribution)}</code></td>"
        f"<td>{html_lib.escape(c.accessibility_notes or '')}</td>"
        f"<td>{'yes' if c.browser_modules else 'no'}</td>"
        "</tr>"
        for c in data_components
    )
    sample_schema = (
        "<tr><td>id</td><td>read-only key</td><td>no</td></tr>"
        "<tr><td>name</td><td>text</td><td>yes</td></tr>"
        "<tr><td>title</td><td>text</td><td>yes</td></tr>"
        "<tr><td>active</td><td>boolean</td><td>yes</td></tr>"
    )
    body = f"""
    <h2>Data</h2>
    <p>Explorer data previews use isolated sample rows by default.
    Writable-field policy is server-authoritative; forged writes are rejected.</p>
    <h3>Registered data components</h3>
    <table>
      <thead><tr><th>Name</th><th>Distribution</th><th>A11y notes</th>
      <th>Browser host</th></tr></thead>
      <tbody>{rows or "<tr><td colspan='4'>No DataTable/DataEditor registered</td></tr>"}</tbody>
    </table>
    <h3>Sample writable policy</h3>
    <table>
      <thead><tr><th>Field</th><th>Role</th><th>Writable</th></tr></thead>
      <tbody>{sample_schema}</tbody>
    </table>
    <ul>
      <li>Schema and column editors derive from Hedron Field metadata</li>
      <li>Changes, conflicts, timing, and endpoints appear on save diagnostics</li>
      <li>Large sources must use bounded DataEditorSource paging</li>
    </ul>
    """
    return shell("Data", body, request=request, active="data")


async def auto_view(request: Request) -> str:
    from hedron_core.auto import get_last_auto_decision

    decision = get_last_auto_decision()
    if decision is None:
        detail = "<p>No Auto() decision recorded yet in this process.</p>"
    else:
        rejected = "".join(
            f"<li><code>{html_lib.escape(name)}</code>: {html_lib.escape(reason)}</li>"
            for name, reason in decision.rejected
        )
        detail = f"""
        <dl>
          <dt>Selected</dt>
          <dd><code>{html_lib.escape(decision.selected)}</code></dd>
          <dt>Candidates</dt>
          <dd><code>{html_lib.escape(", ".join(decision.candidates))}</code></dd>
          <dt>Inspection</dt>
          <dd><pre>{html_lib.escape(str(dict(decision.inspection)))}</pre></dd>
        </dl>
        <h3>Rejected</h3>
        <ul>{rejected or "<li>None</li>"}</ul>
        """
    body = f"<h2>Auto renderer evidence</h2>{detail}"
    return shell("Auto", body, request=request, active="auto")


def _map_plan_facts_html(request: Request) -> str:
    """Read-only MapPlan facts from app.state or a default OSM compile (no I/O)."""
    try:
        from hedron_maps.compile import compile_map
        from hedron_maps.facts import plan_facts
        from hedron_maps.spec import AccessibilityDef, MapPlan, MapSpec, OpenStreetMap
    except ImportError:
        return "<p>hedron-maps is not installed; MapPlan inspection is unavailable.</p>"

    plans: list[MapPlan] = []
    stored = getattr(getattr(request.app, "state", None), "hedron_map_plans", None)
    if isinstance(stored, (list, tuple)):
        plans.extend(item for item in stored if isinstance(item, MapPlan))
    single = getattr(getattr(request.app, "state", None), "hedron_map_plan", None)
    if isinstance(single, MapPlan):
        plans.append(single)
    if not plans:
        plans.append(
            compile_map(
                MapSpec(
                    basemap=OpenStreetMap.standard(),
                    accessibility=AccessibilityDef(
                        title="Explorer default map",
                        description="Read-only MapPlan inspection sample",
                    ),
                )
            )
        )
    blocks: list[str] = []
    for plan in plans:
        facts = plan_facts(plan)
        rows = "".join(
            "<tr>"
            f"<th>{html_lib.escape(str(key))}</th>"
            f"<td><code>{html_lib.escape(str(value))}</code></td>"
            "</tr>"
            for key, value in facts.items()
        )
        blocks.append(
            "<table>"
            "<thead><tr><th>Fact</th><th>Value</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )
    return "<h3>MapPlan facts</h3>" + "".join(blocks)


def _provider_panel_markup(result: object) -> str:
    if isinstance(result, Component) or hasattr(result, "__hedron_node__"):
        return render(cast(NodeLike, result), mode=RenderMode.FRAGMENT).html
    return html_lib.escape(str(result))


def _provider_panel_body(provider: ExplorerProvider) -> object:
    render_fn = getattr(provider, "render", None)
    if callable(render_fn):
        return render_fn()
    return f"{provider.title} ({provider.plugin}): {provider.description}"


async def packages_view(request: Request) -> str:
    items: list[str] = []
    for provider in providers_or_defaults():
        isolated = run_isolated(provider, lambda current=provider: _provider_panel_body(current))
        if isolated.get("ok"):
            items.append(f"<li>{_provider_panel_markup(isolated.get('result'))}</li>")
            continue
        diagnostic = html_lib.escape(str(isolated.get("diagnostic") or ""))
        error = html_lib.escape(str(isolated.get("error") or "isolated"))
        title = html_lib.escape(provider.title)
        items.append(f"<li role='status'><code>{diagnostic}</code> {title} ({error})</li>")
    health_provider = ExplorerProvider(
        panel_id="package-health",
        title="Package health",
        plugin="hedron-explorer",
    )
    health_isolated = run_isolated(health_provider, package_health)
    if health_isolated.get("ok"):
        health_pre = html_lib.escape(str(health_isolated.get("result")))
    else:
        health_pre = html_lib.escape(str(health_isolated))
    return shell(
        "Packages",
        (
            f"<h2>Packages / plugin panels</h2>"
            f"<ul>{''.join(items) or '<li>No plugin panels</li>'}</ul>"
            f"<h2>Package health (read-only)</h2>"
            "<p>Not <code>hedron package doctor</code> (0.54). Entry points, version skew, "
            "and duplicate registrations only.</p>"
            f"<pre>{health_pre}</pre>"
        ),
        request=request,
        active="packages",
    )


async def elements_view(request: Request) -> str:
    rows = []
    for meta in get_registry().element_definitions():
        href = explorer_href(request, f"/hedron-explorer/elements/{meta.logical_id}")
        events = html_lib.escape(", ".join(meta.events) or "—")
        parts = html_lib.escape(", ".join(meta.parts) or "—")
        origin = "first-party" if meta.first_party else "third-party"
        rows.append(
            "<tr>"
            f'<td><a href="{href}">{html_lib.escape(meta.logical_id)}</a></td>'
            f"<td>{html_lib.escape(meta.tag_name)}</td>"
            f"<td>{meta.abi_version}</td>"
            f"<td>{origin}</td>"
            f"<td>{events}</td>"
            f"<td>{parts}</td>"
            "</tr>"
        )
    empty = '<tr><td colspan="6">No element definitions</td></tr>'
    body = (
        "<h2>Elements</h2>"
        "<table><thead><tr>"
        "<th>Logical id</th><th>Tag</th><th>ABI</th><th>Origin</th>"
        "<th>Events</th><th>Parts</th></tr></thead>"
        f"<tbody>{''.join(rows) or empty}</tbody></table>"
    )
    return shell("Elements", body, request=request, active="elements")


async def element_detail_view(request: Request, logical_id: str) -> str:
    meta = get_registry().get_element_definition(logical_id)
    if meta is None:
        raise HTTPException(status_code=404, detail="Element not found")
    fallback = "".join(
        f"<li><code>{html_lib.escape(key)}</code>: {html_lib.escape(value)}</li>"
        for key, value in meta.fallback.items()
    )
    body = f"""
    <h2>{html_lib.escape(meta.tag_name)}</h2>
    <dl>
      <dt>Logical id</dt><dd>{html_lib.escape(meta.logical_id)}</dd>
      <dt>ABI</dt><dd>{meta.abi_version}</dd>
      <dt>Module</dt><dd>{html_lib.escape(meta.module_asset_id)}</dd>
      <dt>Events</dt><dd>{html_lib.escape(", ".join(meta.events) or "—")}</dd>
      <dt>Parts</dt><dd>{html_lib.escape(", ".join(meta.parts) or "—")}</dd>
      <dt>Slots</dt><dd>{html_lib.escape(", ".join(meta.slots) or "—")}</dd>
      <dt>Tokens</dt><dd>{html_lib.escape(", ".join(meta.tokens) or "—")}</dd>
      <dt>First party</dt><dd>{meta.first_party}</dd>
    </dl>
    <h3>Fallback</h3>
    <ul>{fallback or "<li>None declared</li>"}</ul>
    """
    return shell(meta.tag_name, body, request=request, active="elements")


def _collect_hdj_inventory(
    request: Request,
) -> tuple[list[JsonObject], set[str], list[str]]:
    """Scan project roots for ``*.hdj`` files and build inventory reports (sync I/O)."""
    from hedron_jinja import reconcile_csp
    from hedron_jinja.source import inferred_capabilities, parse_hdj_source

    reports: list[JsonObject] = []
    caps: set[str] = set()
    mismatches: list[str] = []
    project_root = getattr(request.app.state, "hedron_project_root", None)
    roots = project_component_roots(request)
    search_roots = list(roots)
    if project_root:
        search_roots.append(Path(project_root))
    seen: set[Path] = set()
    for root in search_roots:
        root = Path(root).resolve()
        if root in seen or not root.exists():
            continue
        seen.add(root)
        for path in sorted(root.rglob("*.hdj")):
            if any(part.startswith(".") for part in path.parts):
                continue
            source = hdj_text_under_root(path, root)
            if source is None:
                continue
            try:
                rel = str(path.relative_to(root))
                parsed = parse_hdj_source(rel, source)
                required = sorted(
                    set(inferred_capabilities(parsed)) | set(parsed.declaration.requires)
                )
                caps.update(required)
                reports.append(
                    cast(
                        JsonObject,
                        {
                            "name": rel,
                            "kind": str(parsed.declaration.kind),
                            "capabilities": required,
                        },
                    )
                )
                mismatches.extend(
                    reconcile_csp(
                        None,
                        required_capabilities=required,
                        source_name=rel,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                _logger.warning("HDJ inventory parse failed for %s: %s", path, exc)
                reports.append({"name": str(path), "error": str(exc)})
    return reports, caps, mismatches


async def inventory_view(request: Request) -> str:
    """Production / HDJ inventory panel (phase 0.11)."""
    try:
        from hedron_jinja import build_production_inventory

        reports, caps, mismatches = _collect_hdj_inventory(request)
        inv = build_production_inventory(
            template_reports=reports,
            capabilities=sorted(caps) or ("web.html", "jinja.core"),
        )
        payload = html_lib.escape(
            str(
                {
                    **inv.as_dict(),
                    "csp_mismatches": mismatches,
                    "template_count": len(reports),
                }
            )
        )
    except Exception as exc:  # noqa: BLE001
        _logger.warning("Production inventory unavailable: %s", exc)
        payload = html_lib.escape(f"Inventory unavailable: {exc}")
    body = f"<h2>Production inventory</h2><pre>{payload}</pre>"
    return shell("Inventory", body, request=request, active="inventory")


async def settings_view(request: Request) -> str:
    theme = getattr(request.app.state, "hedron_theme", None)
    production = getattr(request.app.state, "hedron_production", None)
    diff_html = format_diff_html(explorer_diff_report(request.app))
    body = f"""
    <h2>Settings</h2>
    <dl>
      <dt>Theme</dt><dd>{html_lib.escape(str(theme))}</dd>
      <dt>Production</dt><dd>{html_lib.escape(str(production))}</dd>
      <dt>Allow mutations</dt><dd>false (default)</dd>
    </dl>
    <h2>Catalog diff</h2>
    {diff_html}
    """
    return shell("Settings", body, request=request, active="settings")


async def interactions_view(request: Request) -> str:
    catalog = app_catalog(request.app)
    page = page_interactions(request, catalog)
    rows = []
    for entry in page.items:
        ident = html_lib.escape(entry.logical_id)
        kind = html_lib.escape(entry.kind)
        effect = html_lib.escape(entry.effect_state)
        desc = html_lib.escape(entry.descriptor_fingerprint)
        schema = html_lib.escape(entry.type_schema_fingerprint or "absent")
        namespaces = html_lib.escape(", ".join(sorted(entry.projections)) or "none")
        rows.append(
            f"<tr><td>{ident}</td><td>{kind}</td><td>{effect}</td>"
            f"<td><code>{desc}</code></td><td><code>{schema}</code></td>"
            f"<td>{namespaces}</td></tr>"
        )
    projections = "".join(
        f"<li><code>{html_lib.escape(name)}</code> provider={html_lib.escape(item.provider)}</li>"
        for name, item in catalog.catalog_projections.items()
    )
    body = f"""
    <h2>Interaction catalog</h2>
    <p>Read-only index of 0.43 descriptors and optional 0.44 TypeSchema.
    Catalog ids and fingerprints are not capabilities.</p>
    <p>Fingerprint <code>{html_lib.escape(catalog.fingerprint)}</code>
    sealed={catalog.sealed}</p>
    <h3>Entries</h3>
    {truncation_banner(page, noun="interactions", request=request)}
    <table>
      <thead><tr><th>Logical id</th><th>Kind</th><th>Effect</th>
      <th>Descriptor</th><th>TypeSchema</th><th>Projections</th></tr></thead>
      <tbody>{"".join(rows) or "<tr><td colspan='6'>No registered handles</td></tr>"}</tbody>
    </table>
    <h3>Package projections</h3>
    <ul>{projections or "<li>No catalog-level projections</li>"}</ul>
    <h3>Provenance</h3>
    <pre>{html_lib.escape(str(dict(catalog.provenance)))}</pre>
    """
    return shell("Interactions", body, request=request, active="interactions")


async def features_view(request: Request) -> str:
    from hedron_core.bundles import included_bundles

    app_id = str(getattr(getattr(request.app, "state", None), "hedron_app_id", "") or "")
    rows = []
    for bundle in included_bundles(app_id=app_id or None):
        ident = html_lib.escape(bundle.logical_id)
        provider = html_lib.escape(f"{bundle.provider} {bundle.provider_version}")
        views = html_lib.escape(
            ", ".join(str(getattr(item, "logical_id", item)) for item in bundle.views) or "—"
        )
        commands = html_lib.escape(
            ", ".join(str(getattr(item, "logical_id", item)) for item in bundle.commands) or "—"
        )
        projections = html_lib.escape(
            ", ".join(item.namespace for item in bundle.projections) or "—"
        )
        limitations = html_lib.escape("; ".join(bundle.limitations) or "—")
        rows.append(
            f"<tr><td>{ident}</td><td>{provider}</td><td>{views}</td>"
            f"<td>{commands}</td><td>{projections}</td><td>{limitations}</td></tr>"
        )
    empty = '<tr><td colspan="6">No FeatureBundles included</td></tr>'
    body = f"""
    <h2>Feature bundles</h2>
    <p>Opt-in package features compiled to ordinary handles. Bundles are not executors
    and catalog/projection presence is not a capability.</p>
    <table>
      <thead><tr><th>Id</th><th>Provider</th><th>Views</th><th>Commands</th>
      <th>Projections</th><th>Limitations</th></tr></thead>
      <tbody>{"".join(rows) or empty}</tbody>
    </table>
    """
    return shell("Features", body, request=request, active="features")
