"""Deterministic site manifest and compiler."""

from __future__ import annotations

import base64
import fnmatch
import hashlib
import json
import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from hedron_core.diagnostics import HedronError
from hedron_core.security import SafeUrl, UrlPurpose

from .ast import DocNode
from .config import DocsBuildConfig
from .errors import source_error
from .markdown import parse_markdown

SCHEMA_VERSION = "hedron-docs-manifest-1"


@dataclass(frozen=True, slots=True)
class AssetRecord:
    source: str
    path: str
    media_type: str
    content_base64: str
    source_hash: str
    size: int

    def decoded(self) -> bytes:
        try:
            content = base64.b64decode(self.content_base64, validate=True)
        except ValueError as exc:
            raise ValueError(f"invalid base64 content for asset {self.path}") from exc
        if len(content) != self.size:
            raise ValueError(f"asset size does not match manifest for {self.path}")
        if hashlib.sha256(content).hexdigest() != self.source_hash:
            raise ValueError(f"asset hash does not match manifest for {self.path}")
        return content

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "path": self.path,
            "media_type": self.media_type,
            "content_base64": self.content_base64,
            "source_hash": self.source_hash,
            "size": self.size,
        }

    @classmethod
    def from_dict(cls, value: object) -> AssetRecord:
        if not isinstance(value, dict):
            raise ValueError("manifest asset must be an object")
        data = cast(dict[str, object], value)
        asset = cls(
            source=str(data["source"]),
            path=str(data["path"]),
            media_type=str(data["media_type"]),
            content_base64=str(data["content_base64"]),
            source_hash=str(data["source_hash"]),
            size=int(str(data["size"])),
        )
        if not asset.path.startswith("/_hedron-docs/assets/"):
            raise ValueError(f"invalid asset route: {asset.path}")
        asset.decoded()
        return asset


@dataclass(frozen=True, slots=True)
class PageRecord:
    source: str
    path: str
    title: str
    description: str
    headings: tuple[tuple[str, str, int], ...]
    nodes: tuple[DocNode, ...]
    search_text: str
    source_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "path": self.path,
            "title": self.title,
            "description": self.description,
            "headings": [list(item) for item in self.headings],
            "nodes": [node.to_dict() for node in self.nodes],
            "search_text": self.search_text,
            "source_hash": self.source_hash,
        }

    @classmethod
    def from_dict(cls, value: object) -> PageRecord:
        if not isinstance(value, dict):
            raise ValueError("manifest page must be an object")
        data = cast(dict[str, object], value)
        nodes_value = data.get("nodes", [])
        headings_value = data.get("headings", [])
        if not isinstance(nodes_value, list) or not isinstance(headings_value, list):
            raise ValueError("manifest page nodes/headings must be arrays")
        nodes = cast(list[object], nodes_value)
        headings = cast(list[object], headings_value)
        parsed_headings: list[tuple[str, str, int]] = []
        for item in headings:
            if not isinstance(item, list):
                raise ValueError("manifest heading must be a three-item array")
            item_values = cast(list[object], item)
            if len(item_values) != 3:
                raise ValueError("manifest heading must be a three-item array")
            parsed_headings.append(
                (str(item_values[0]), str(item_values[1]), int(str(item_values[2])))
            )
        return cls(
            source=str(data["source"]),
            path=str(data["path"]),
            title=str(data["title"]),
            description=str(data.get("description", "")),
            headings=tuple(parsed_headings),
            nodes=tuple(DocNode.from_dict(item) for item in nodes),
            search_text=str(data.get("search_text", "")),
            source_hash=str(data.get("source_hash", "")),
        )


@dataclass(frozen=True, slots=True)
class SiteManifest:
    title: str
    description: str
    base_url: str
    pages: tuple[PageRecord, ...]
    assets: tuple[AssetRecord, ...] = ()
    max_query_length: int = 200
    compiler_version: str = "0.1.0"
    schema_version: str = SCHEMA_VERSION

    @property
    def build_id(self) -> str:
        """Stable identifier for this exact compiled manifest."""

        return hashlib.sha256(self.dumps().encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "compiler_version": self.compiler_version,
            "site": {
                "title": self.title,
                "description": self.description,
                "base_url": self.base_url,
                "max_query_length": self.max_query_length,
            },
            "pages": [page.to_dict() for page in self.pages],
            "assets": [asset.to_dict() for asset in self.assets],
        }

    def dumps(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, indent=2) + "\n"

    def write(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.dumps(), encoding="utf-8")
        return target

    @classmethod
    def from_dict(cls, value: object) -> SiteManifest:
        if not isinstance(value, dict):
            raise ValueError(f"unsupported or missing manifest schema (expected {SCHEMA_VERSION})")
        data = cast(dict[str, object], value)
        if data.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"unsupported or missing manifest schema (expected {SCHEMA_VERSION})")
        site = data.get("site", {})
        pages = data.get("pages", [])
        assets = data.get("assets", [])
        if (
            not isinstance(site, dict)
            or not isinstance(pages, list)
            or not isinstance(assets, list)
        ):
            raise ValueError("manifest site/pages/assets have invalid shape")
        site_data = cast(dict[str, object], site)
        page_values = cast(list[object], pages)
        asset_values = cast(list[object], assets)
        return cls(
            title=str(site_data.get("title", "Documentation")),
            description=str(site_data.get("description", "")),
            base_url=str(site_data.get("base_url", "")),
            pages=tuple(PageRecord.from_dict(item) for item in page_values),
            assets=tuple(AssetRecord.from_dict(item) for item in asset_values),
            max_query_length=int(str(site_data.get("max_query_length", 200))),
            compiler_version=str(data.get("compiler_version", "unknown")),
        )


def load_manifest(value: SiteManifest | str | Path) -> SiteManifest:
    if isinstance(value, SiteManifest):
        return value
    path = Path(value)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return SiteManifest.from_dict(data)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise source_error("HED-DOCS-0200", f"invalid manifest: {exc}", path) from exc


def compile_site(config: DocsBuildConfig) -> SiteManifest:
    cfg = config.resolved(root=config.config_path.parent if config.config_path else None)
    if not cfg.docs_dir.is_dir():
        raise source_error("HED-DOCS-0201", f"documentation directory not found: {cfg.docs_dir}")
    pages: list[PageRecord] = []
    assets: dict[str, AssetRecord] = {}
    seen_paths: dict[str, Path] = {}
    docs_root = cfg.docs_dir.resolve()
    reserved = {"/search", "/robots.txt", "/sitemap.xml", "/healthz", "/readyz"}
    for source_path in sorted(cfg.docs_dir.rglob("*.md")):
        if not source_path.is_file() or _excluded(
            source_path.relative_to(cfg.docs_dir), cfg.exclude
        ):
            continue
        try:
            source_path.resolve(strict=True).relative_to(docs_root)
        except (OSError, ValueError) as exc:
            raise source_error(
                "HED-DOCS-0206", "document source escapes the documentation root", source_path
            ) from exc
        source = source_path.read_text(encoding="utf-8")
        if len(source.encode("utf-8")) > cfg.max_source_bytes:
            raise source_error(
                "HED-DOCS-0202",
                f"document exceeds source limit ({cfg.max_source_bytes} bytes)",
                source_path,
            )
        nodes = parse_markdown(source, source_path=source_path, max_nodes=cfg.max_nodes)
        rel = source_path.relative_to(cfg.docs_dir).with_suffix("")
        nodes = _normalize_nodes(
            nodes,
            cfg.docs_dir / rel.parent,
            cfg.docs_dir,
            allow_external_links=cfg.allow_external_links,
            assets=assets,
            max_asset_bytes=cfg.max_asset_bytes,
        )
        path = _public_path(rel)
        route_key = path.rstrip("/") or "/"
        if route_key in reserved or route_key.startswith("/_hedron-docs"):
            raise source_error(
                "HED-DOCS-0205", f"route is reserved by the docs application: {path}", source_path
            )
        collision_key = route_key.casefold()
        if collision_key in seen_paths:
            raise source_error(
                "HED-DOCS-0203", f"route collision with {seen_paths[collision_key]}", source_path
            )
        seen_paths[collision_key] = source_path
        headings = tuple(
            (node.attr("id"), node.text, int(node.attr("level", "2")))
            for node in _walk(nodes)
            if node.kind == "heading"
        )
        title = headings[0][1] if headings else rel.name.replace("-", " ").replace("_", " ").title()
        description = _first_text(nodes)
        pages.append(
            PageRecord(
                source=str(source_path.relative_to(cfg.docs_dir)),
                path=path,
                title=title,
                description=description,
                headings=headings,
                nodes=nodes,
                search_text=" ".join(_node_text(node) for node in _walk(nodes)),
                source_hash=hashlib.sha256(source.encode("utf-8")).hexdigest(),
            )
        )
    pages.sort(key=lambda page: page.path)
    if not pages:
        raise source_error("HED-DOCS-0204", f"no Markdown documents found under {cfg.docs_dir}")
    return SiteManifest(
        title=cfg.site_title,
        description=cfg.site_description,
        base_url=cfg.base_url,
        pages=tuple(pages),
        assets=tuple(sorted(assets.values(), key=lambda asset: asset.path)),
        max_query_length=cfg.max_query_length,
    )


def _public_path(relative: Path) -> str:
    parts = list(relative.parts)
    if parts == ["index"]:
        return "/"
    if parts and parts[-1] == "index":
        parts.pop()
    value = "/" + "/".join(parts) + "/"
    return re.sub(r"/{2,}", "/", value)


def _excluded(path: Path, patterns: tuple[str, ...]) -> bool:
    text = path.as_posix()
    return any(
        fnmatch.fnmatch(text, pattern)
        or (pattern.endswith("/**") and (text == pattern[:-3] or text.startswith(pattern[:-2])))
        for pattern in patterns
    )


def _walk(nodes: tuple[DocNode, ...] | list[DocNode]) -> list[DocNode]:
    result: list[DocNode] = []
    for node in nodes:
        result.append(node)
        result.extend(_walk(node.children))
    return result


def _node_text(node: DocNode) -> str:
    return node.text or " ".join(_node_text(child) for child in node.children)


def _first_text(nodes: tuple[DocNode, ...]) -> str:
    for node in _walk(nodes):
        if node.kind == "paragraph" and _node_text(node).strip():
            return _node_text(node).strip()[:240]
    return ""


def _normalize_nodes(
    nodes: tuple[DocNode, ...],
    source_parent: Path,
    docs_dir: Path,
    *,
    allow_external_links: bool,
    assets: dict[str, AssetRecord],
    max_asset_bytes: int,
) -> tuple[DocNode, ...]:
    normalized: list[DocNode] = []
    for node in nodes:
        attrs = dict(node.attrs)
        if node.kind == "link" and attrs.get("href"):
            attrs["href"] = _normalize_url(
                attrs["href"],
                source_parent,
                docs_dir,
                document=True,
                allow_external_links=allow_external_links,
                assets=assets,
                max_asset_bytes=max_asset_bytes,
            )
        elif node.kind == "image" and attrs.get("src"):
            attrs["src"] = _normalize_url(
                attrs["src"],
                source_parent,
                docs_dir,
                document=False,
                allow_external_links=allow_external_links,
                assets=assets,
                max_asset_bytes=max_asset_bytes,
            )
        normalized.append(
            DocNode(
                kind=node.kind,
                text=node.text,
                attrs=tuple(sorted(attrs.items())),
                children=_normalize_nodes(
                    node.children,
                    source_parent,
                    docs_dir,
                    allow_external_links=allow_external_links,
                    assets=assets,
                    max_asset_bytes=max_asset_bytes,
                ),
                line=node.line,
            )
        )
    return tuple(normalized)


def _normalize_url(
    value: str,
    source_parent: Path,
    docs_dir: Path,
    *,
    document: bool,
    allow_external_links: bool,
    assets: dict[str, AssetRecord],
    max_asset_bytes: int,
) -> str:
    parts = urlsplit(value)
    if parts.scheme or parts.netloc:
        if not allow_external_links:
            raise ValueError(f"external documentation URL is disabled: {value!r}")
        purpose = UrlPurpose.NAVIGATION if document else UrlPurpose.ASSET
        try:
            SafeUrl.parse(value, purpose=purpose, allow_external=True)
        except HedronError as exc:
            raise ValueError(f"unsafe or invalid documentation URL: {value!r}") from exc
        return value
    if value.startswith("#"):
        try:
            SafeUrl.parse(value, purpose=UrlPurpose.NAVIGATION)
        except HedronError as exc:
            raise ValueError(f"unsafe or invalid documentation URL: {value!r}") from exc
        return value
    if document and parts.path == "/":
        return urlunsplit(("", "", "/", parts.query, parts.fragment))
    raw_path = Path(unquote(parts.path))
    if raw_path.is_absolute():
        candidate = (docs_dir / raw_path.relative_to(raw_path.anchor)).resolve()
    else:
        candidate = (source_parent / raw_path).resolve()
    try:
        relative = candidate.relative_to(docs_dir.resolve())
    except ValueError as exc:
        raise ValueError(f"documentation URL escapes docs root: {value!r}") from exc
    if not document:
        route = _compile_asset(candidate, relative, assets, max_asset_bytes=max_asset_bytes).path
    elif relative.suffix.lower() == ".md":
        if not candidate.is_file():
            raise ValueError(f"linked documentation page does not exist: {value!r}")
        route = _public_path(relative.with_suffix(""))
    elif candidate.is_file():
        route = _compile_asset(candidate, relative, assets, max_asset_bytes=max_asset_bytes).path
    else:
        route = "/" + relative.as_posix()
    normalized = urlunsplit(("", "", route, parts.query, parts.fragment))
    if document:
        runtime_url = normalized
        if "#" in runtime_url:
            path, fragment = runtime_url.split("#", 1)
            runtime_url = (path.rstrip("/") or "/") + "#" + fragment
        else:
            runtime_url = runtime_url.rstrip("/") or "/"
        try:
            SafeUrl.parse(runtime_url, purpose=UrlPurpose.NAVIGATION)
        except HedronError as exc:
            raise ValueError(f"unsafe or invalid documentation URL: {value!r}") from exc
    return normalized


def _compile_asset(
    candidate: Path,
    relative: Path,
    assets: dict[str, AssetRecord],
    *,
    max_asset_bytes: int,
) -> AssetRecord:
    if not candidate.is_file():
        raise ValueError(f"documentation asset does not exist: {relative.as_posix()!r}")
    content = candidate.read_bytes()
    if len(content) > max_asset_bytes:
        raise ValueError(
            f"documentation asset exceeds limit ({max_asset_bytes} bytes): {relative.as_posix()!r}"
        )
    source_hash = hashlib.sha256(content).hexdigest()
    encoded_source = quote(relative.as_posix(), safe="/-._~")
    path = f"/_hedron-docs/assets/{source_hash[:16]}/{encoded_source}"
    media_type = mimetypes.guess_type(relative.name)[0] or "application/octet-stream"
    asset = AssetRecord(
        source=relative.as_posix(),
        path=path,
        media_type=media_type,
        content_base64=base64.b64encode(content).decode("ascii"),
        source_hash=source_hash,
        size=len(content),
    )
    assets[path] = asset
    return asset
