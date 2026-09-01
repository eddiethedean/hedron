"""Manifest-backed Hedron application factory."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

from hedron import Hedron, Link, Page, Text
from hedron_core.builtins.document import Head
from hedron_core.builtins.landmarks import Footer, Header, Main, Nav
from hedron_core.builtins.layout import Container, Stack
from hedron_core.html import html
from hedron_core.security import SafeUrl, UrlPurpose

from .manifest import PageRecord, SiteManifest, load_manifest
from .render import render_document
from .search import search


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
    for page in site.pages:
        _register_page(app, site, page)

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
            return _shell(site, None, *body)
        except ValueError as exc:
            return _shell(site, None, html.p(str(exc), role="alert"))

    @app.get("/robots.txt", include_in_schema=False)
    def robots() -> PlainTextResponse:  # pyright: ignore[reportUnusedFunction]
        return PlainTextResponse("User-agent: *\nAllow: /\n")

    @app.get("/sitemap.xml", include_in_schema=False)
    def sitemap() -> Response:  # pyright: ignore[reportUnusedFunction]
        links = "".join(f"<url><loc>{site.base_url}{page.path}</loc></url>" for page in site.pages)
        return Response(
            f'<?xml version="1.0" encoding="UTF-8"?><urlset>{links}</urlset>',
            media_type="application/xml",
        )

    return app


def _register_page(app: Hedron, site: SiteManifest, page: PageRecord) -> None:
    route_name = "docs_" + (
        "home" if page.path == "/" else page.path.strip("/").replace("/", "_").replace("-", "_")
    )

    @app.page(page.path, name=route_name)
    def document_page(page: PageRecord = page) -> Page:  # pyright: ignore[reportUnusedFunction]
        content = render_document(page.nodes)
        return _shell(site, page, content)


def _shell(site: SiteManifest, page: PageRecord | None, *content: Any) -> Page:
    links = [
        html.li(
            Link(
                item.title,
                _nav_path(item.path),
                mark="current" if page and item.path == page.path else None,
            )
        )
        for item in site.pages[:80]
    ]
    header = Header(
        Container(
            Link(site.title, "/", class_="hedron-docs-brand"),
            Nav(html.ul(*links), aria={"label": "Primary navigation"}),
            Link("Search", "/search"),
            max_width="xl",
        )
    )
    main = Main(
        Container(
            Stack(
                *(content or (Text("Page not found"),)),
                gap="lg",
            ),
            max_width="lg",
        ),
        id="main-panel",
    )
    footer = Footer(Container(Text(f"{site.title} · Built with Hedron"), max_width="xl"))
    title = page.title if page else site.title
    description = page.description if page else site.description
    head = Head(
        html.meta(name="description", content=description),
        html.meta(name="og:title", content=title),
        html.meta(name="og:description", content=description),
    )
    return Page(header, main, footer, title=title, head=head)


def _nav_path(path: str) -> str:
    return path.rstrip("/") or "/"
