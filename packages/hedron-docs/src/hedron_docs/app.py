"""Manifest-backed Hedron application factory."""

from __future__ import annotations

import hashlib
from importlib import resources
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urlsplit
from xml.sax.saxutils import escape as xml_escape

from fastapi import Request
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

from hedron import (
    AppShell,
    Brand,
    ColorMode,
    ColorModeToggle,
    Hedron,
    Link,
    Page,
    SkipLink,
    Text,
    apply_color_mode_cookie,
    csrf_token_for_request,
    read_color_mode_preference,
    resolved_theme_from_request,
)
from hedron_core.builtins.landmarks import Nav
from hedron_core.builtins.layout import Container, Stack
from hedron_core.html import html
from hedron_core.security import SafeUrl, UrlPurpose

from .manifest import AssetRecord, PageRecord, SiteManifest, load_manifest
from .render import render_document
from .search import search

_DOCS_CSS = resources.files("hedron_docs").joinpath("static").joinpath("docs.css").read_bytes()
_DOCS_CSS_DIGEST = hashlib.sha256(_DOCS_CSS).hexdigest()[:16]
_DOCS_CSS_PATH = f"/_hedron-docs/docs-{_DOCS_CSS_DIGEST}.css"


def create_docs_app(
    manifest: SiteManifest | str | Path,
    *,
    security: str = "standard",
    session_secret: str | None = None,
) -> Hedron:
    """Create a stateless Hedron app from a validated site manifest."""

    site = load_manifest(manifest)
    app = Hedron(
        title=site.title,
        security=security,
        session_secret=session_secret,
        enable_sessions=session_secret is not None,
        explorer="off",
        default_styles=True,
    )

    @app.get(_DOCS_CSS_PATH, include_in_schema=False)
    def docs_stylesheet() -> Response:  # pyright: ignore[reportUnusedFunction]
        return Response(
            _DOCS_CSS,
            media_type="text/css",
            headers={
                "Cache-Control": "public, max-age=31536000, immutable",
                "ETag": f'"{hashlib.sha256(_DOCS_CSS).hexdigest()}"',
                "X-Content-Type-Options": "nosniff",
            },
        )

    for asset in site.assets:
        _register_asset(app, asset)

    @app.get("/healthz", include_in_schema=False)
    def health() -> JSONResponse:  # pyright: ignore[reportUnusedFunction]
        return JSONResponse({"status": "ok", "build_id": site.build_id})

    @app.get("/readyz", include_in_schema=False)
    def readiness() -> JSONResponse:  # pyright: ignore[reportUnusedFunction]
        ready = bool(site.pages)
        return JSONResponse(
            {"status": "ready" if ready else "degraded", "build_id": site.build_id},
            status_code=200 if ready else 503,
        )

    @app.post("/preferences/theme", include_in_schema=False)
    async def theme_preference(request: Request) -> Response:  # pyright: ignore[reportUnusedFunction]
        """Persist the shell's color-mode choice through an ordinary HTML form."""

        policy = getattr(request.app.state, "hedron_security", None)
        if policy is not None and getattr(policy, "csrf_enabled", False):
            from hedron.security.csrf import prepare_csrf_from_request, validate_csrf

            await prepare_csrf_from_request(request, policy)
            validate_csrf(request, policy)
        form = await request.form()
        raw_mode = form.get("color_mode", ColorMode.SYSTEM.value)
        try:
            mode = ColorMode(str(raw_mode))
        except ValueError:
            mode = ColorMode.SYSTEM
        response = RedirectResponse(_same_origin_return_path(request), status_code=303)
        apply_color_mode_cookie(response, mode, request=request)
        return response

    @app.exception_handler(StarletteHTTPException)
    async def docs_http_error(  # pyright: ignore[reportUnusedFunction]
        request: Request, exc: StarletteHTTPException
    ) -> Response:
        if exc.status_code == 404:
            from hedron.responses import render_component_response

            return render_component_response(
                _shell(
                    site,
                    None,
                    html.h1("Page not found"),
                    html.p("The requested document does not exist."),
                    request=request,
                ),
                request=request,
                status_code=404,
            )
        return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

    @app.page("/search", name="docs_search")
    def search_page(request: Request) -> Page:  # pyright: ignore[reportUnusedFunction]
        query = request.query_params.get("q", "")
        try:
            results = search(site, query, max_length=site.max_query_length)
            result_nodes = [
                html.li(
                    html.a(
                        result.title,
                        href=SafeUrl.parse(_nav_path(result.path), purpose=UrlPurpose.NAVIGATION),
                    ),
                    html.p(result.description),
                )
                for result in results
            ]
            body: list[Any] = [
                html.h1("Search", id="search-title"),
                html.form(
                    html.label("Search", for_="docs-search-query"),
                    html.input(
                        type="search",
                        name="q",
                        id="docs-search-query",
                        value=query,
                        maxlength=site.max_query_length,
                    ),
                    html.button("Search", type="submit"),
                    action=SafeUrl.parse("/search", purpose=UrlPurpose.FORM_ACTION),
                    method="get",
                ),
            ]
            if query:
                body.append(html.p(f"{len(results)} result(s) for {query!r}", role="status"))
                body.append(html.ul(*result_nodes) if result_nodes else html.p("No results found."))
            return _shell(site, None, *body, request=request)
        except ValueError as exc:
            return _shell(site, None, html.p(str(exc), role="alert"), request=request)

    @app.get("/robots.txt", include_in_schema=False)
    def robots(request: Request) -> PlainTextResponse:  # pyright: ignore[reportUnusedFunction]
        base_url = _base_url(site, request)
        return PlainTextResponse(f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n")

    @app.get("/sitemap.xml", include_in_schema=False)
    def sitemap(request: Request) -> Response:  # pyright: ignore[reportUnusedFunction]
        base_url = _base_url(site, request)
        links = "".join(
            f"<url><loc>{xml_escape(base_url + page.path)}</loc></url>" for page in site.pages
        )
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"{links}</urlset>",
            media_type="application/xml",
        )

    page_by_path = {page.path: page for page in site.pages}

    @app.page("/{path:path}", name="docs_manifest_route")
    def manifest_page(request: Request, path: str = "") -> Page | Response:  # pyright: ignore[reportUnusedFunction]
        request_path = _canonical_request_path(request.url.path)
        query = request.url.query
        if request_path != "/" and not request_path.endswith("/"):
            location = request_path + "/"
            if query:
                location += "?" + query
            return RedirectResponse(location, status_code=308)
        page = page_by_path.get(request_path)
        if page is None:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="document not found")
        return _shell(site, page, render_document(page.nodes), request=request)

    return app


def _register_asset(app: Hedron, asset: AssetRecord) -> None:
    content = asset.decoded()
    route_name = f"docs_asset_{hashlib.sha256(asset.path.encode('utf-8')).hexdigest()[:16]}"

    def asset_response() -> Response:
        return Response(
            content,
            media_type=asset.media_type,
            headers={
                "Cache-Control": "public, max-age=31536000, immutable",
                "ETag": f'"{asset.source_hash}"',
                "X-Content-Type-Options": "nosniff",
            },
        )

    asset_response.__name__ = route_name
    asset_response.__qualname__ = route_name
    app.get(asset.path, name=route_name, include_in_schema=False)(asset_response)


def _shell(site: SiteManifest, page: PageRecord | None, *content: Any, request: Request) -> Page:
    nav_pages = sorted(site.pages, key=lambda item: (item.nav_order or (10**9,), item.path))
    visible_pages = [item for item in nav_pages[:80] if item.publication_state == "published"]

    def nav_link(item: PageRecord) -> Any:
        current = bool(page and item.path == page.path)
        attrs: dict[str, Any] = {}
        if current:
            attrs["aria"] = {"current": "page"}
            attrs["data"] = {"hedron-nav-current": "true"}
        return html.li(
            html.a(
                item.nav_title or item.title,
                href=SafeUrl.parse(_nav_path(item.path), purpose=UrlPurpose.NAVIGATION),
                **attrs,
            )
        )

    links = [nav_link(item) for item in visible_pages]
    navigation = Nav(
        html.ul(*links, class_="hedron-docs-primary-nav"),
        html.details(
            html.summary("Menu"),
            html.ul(
                *(nav_link(item) for item in visible_pages),
                class_="hedron-docs-mobile-nav-list",
            ),
            class_="hedron-docs-mobile-nav",
        ),
        aria={"label": "Primary navigation"},
    )
    header_tools = html.div(
        Link("Search", "/search", class_="hedron-docs-search-link"),
        ColorModeToggle(
            preference=read_color_mode_preference(request),
            action="/preferences/theme",
            id="docs-color-mode",
            csrf_token=_csrf_token(request),
        ),
        class_="hedron-docs-header-tools",
    )
    brand = html.div(
        Brand(site.title, href="/", subtitle="Documentation", mark_text="H"),
        header_tools,
        class_="hedron-docs-brand-row",
    )
    extras: list[Any] = []
    if page and page.breadcrumbs:
        breadcrumb_nodes: list[Any] = []
        for label, path in page.breadcrumbs:
            if path:
                breadcrumb_nodes.append(
                    html.li(
                        html.a(
                            label,
                            href=SafeUrl.parse(_nav_path(path), purpose=UrlPurpose.NAVIGATION),
                        )
                    )
                )
            else:
                breadcrumb_nodes.append(html.li(label, aria={"current": "page"}))
        if not breadcrumb_nodes or page.title != page.breadcrumbs[-1][0]:
            breadcrumb_nodes.append(html.li(page.nav_title or page.title, aria={"current": "page"}))
        extras.append(
            html.nav(
                html.ol(*breadcrumb_nodes),
                aria={"label": "Breadcrumb"},
            )
        )
    if page and page.toc:
        extras.append(
            html.aside(
                html.strong("On this page"),
                html.ul(
                    *[
                        html.li(
                            html.a(
                                text,
                                href=SafeUrl.parse(f"#{anchor}", purpose=UrlPurpose.NAVIGATION),
                            )
                        )
                        for anchor, text, _ in page.toc
                    ]
                ),
                aria={"label": "Table of contents"},
            )
        )
    if page and (page.previous_path or page.next_path):
        extras.append(
            html.nav(
                *(
                    [
                        html.a(
                            f"← {page.previous_title}",
                            href=SafeUrl.parse(
                                _nav_path(page.previous_path), purpose=UrlPurpose.NAVIGATION
                            ),
                        )
                    ]
                    if page.previous_path
                    else []
                ),
                *(
                    [
                        html.a(
                            f"{page.next_title} →",
                            href=SafeUrl.parse(
                                _nav_path(page.next_path), purpose=UrlPurpose.NAVIGATION
                            ),
                        )
                    ]
                    if page.next_path
                    else []
                ),
                aria={"label": "Page navigation"},
            )
        )
    if page and (page.edit_url or page.source_url):
        extras.append(
            html.p(
                *(
                    [
                        html.a(
                            "Edit this page",
                            href=SafeUrl.parse(
                                page.edit_url, purpose=UrlPurpose.NAVIGATION, allow_external=True
                            ),
                        )
                    ]
                    if page.edit_url
                    else []
                ),
                *(
                    [
                        html.a(
                            "View source",
                            href=SafeUrl.parse(
                                page.source_url, purpose=UrlPurpose.NAVIGATION, allow_external=True
                            ),
                        )
                    ]
                    if page.source_url
                    else []
                ),
            )
        )
    body = Container(
        Stack(
            *(content or (Text("Page not found"),)),
            *extras,
            gap="lg",
        ),
        max_width="lg",
    )
    footer = Container(Text(f"{site.title} · Built with Hedron"), max_width="xl")
    banner = None
    if site.release_label:
        banner_content: Any = site.release_label
        if site.release_url:
            banner_content = html.a(
                site.release_label,
                href=SafeUrl.parse(
                    site.release_url, purpose=UrlPurpose.NAVIGATION, allow_external=True
                ),
            )
        banner = html.p(
            html.strong("Release: "),
            banner_content,
            role="status",
            class_="hedron-docs-release",
        )
    shell = AppShell(
        nav=navigation,
        body=body,
        brand=brand,
        banner=banner,
        app_footer=footer,
        panel_id="main-panel",
        content_width="wide",
        mobile_collapse=True,
    )
    title = (page.nav_title or page.title) if page else site.title
    description = page.description if page else site.description
    canonical_path = (
        page.canonical_url
        if page and page.canonical_url
        else (page.path if page else request.url.path)
    )
    canonical_target = (
        canonical_path
        if canonical_path.startswith(("http://", "https://"))
        else _base_url(site, request) + canonical_path
    )
    canonical = SafeUrl.parse(
        canonical_target,
        purpose=UrlPurpose.NAVIGATION,
        allow_external=True,
    )
    head = [
        html.link(
            rel="stylesheet",
            href=SafeUrl.parse(_DOCS_CSS_PATH, purpose=UrlPurpose.NAVIGATION),
        ),
        html.meta(name="description", content=description),
        html.link(rel="canonical", href=canonical),
        html.meta(property="og:title", content=title),
        html.meta(property="og:description", content=description),
        html.meta(property="og:url", content=canonical.value),
        html.meta(property="og:type", content="article" if page else "website"),
    ]
    color_mode = read_color_mode_preference(request)
    return Page(
        SkipLink("#main-panel"),
        shell,
        title=title,
        head=head,
        data_theme=None if color_mode is ColorMode.SYSTEM else resolved_theme_from_request(request),
        data_hedron_theme="default",
    )


def _nav_path(path: str) -> str:
    return path.rstrip("/") or "/"


def _base_url(site: SiteManifest, request: Request) -> str:
    return (site.base_url or str(request.base_url)).rstrip("/")


def _same_origin_return_path(request: Request) -> str:
    """Return a safe local redirect target after a preference form submit."""

    referer = request.headers.get("referer", "")
    if referer:
        parsed = urlsplit(referer)
        request_host = request.url.hostname or ""
        if parsed.netloc and parsed.hostname != request_host:
            referer = ""
        elif parsed.path:
            return parsed.path + (("?" + parsed.query) if parsed.query else "")
    return "/"


def _csrf_token(request: Request) -> str | None:
    policy = getattr(request.app.state, "hedron_security", None)
    if policy is None or not getattr(policy, "csrf_enabled", False):
        return None
    return csrf_token_for_request(request, policy)


def _canonical_request_path(path: str) -> str:
    """Encode decoded request segments exactly as compiler routes do."""

    if path == "/":
        return "/"
    try:
        decoded = unquote(path, errors="strict")
    except UnicodeDecodeError:
        return path
    trailing = decoded.endswith("/")
    segments = decoded.strip("/").split("/")
    encoded = "/" + "/".join(quote(segment, safe="-._~") for segment in segments)
    return encoded + ("/" if trailing else "")
