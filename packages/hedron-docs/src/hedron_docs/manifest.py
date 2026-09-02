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
_MAX_MANIFEST_BYTES = 64 * 1024 * 1024
_RESERVED_ROUTES = frozenset({"/search", "/robots.txt", "/sitemap.xml", "/healthz", "/readyz"})


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
        source = data.get("source")
        path = data.get("path")
        media_type = data.get("media_type")
        content_base64 = data.get("content_base64")
        source_hash = data.get("source_hash")
        size_value = data.get("size")
        if (
            not all(
                isinstance(item, str)
                for item in (source, path, media_type, content_base64, source_hash)
            )
            or isinstance(size_value, bool)
            or not isinstance(size_value, int)
        ):
            raise ValueError("manifest asset fields have invalid types")
        asset = cls(
            source=cast(str, source),
            path=cast(str, path),
            media_type=cast(str, media_type),
            content_base64=cast(str, content_base64),
            source_hash=cast(str, source_hash),
            size=size_value,
        )
        if not asset.path.startswith("/_hedron-docs/assets/"):
            raise ValueError(f"invalid asset route: {asset.path}")
        _validate_asset_path(asset.path)
        _validate_relative_source(asset.source)
        if asset.size < 0:
            raise ValueError(f"asset size must not be negative for {asset.path}")
        if not re.fullmatch(r"[0-9a-f]{64}", asset.source_hash):
            raise ValueError(f"invalid asset hash for {asset.path}")
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
            if not isinstance(item_values[0], str) or not isinstance(item_values[1], str):
                raise ValueError("manifest heading id/text must be strings")
            parsed_headings.append((item_values[0], item_values[1], int(str(item_values[2]))))
        if any(level < 1 or level > 6 for _, _, level in parsed_headings):
            raise ValueError("manifest heading level must be between 1 and 6")
        source = data.get("source")
        path = data.get("path")
        title = data.get("title")
        if not all(isinstance(item, str) for item in (source, path, title)):
            raise ValueError("manifest page source/path/title must be strings")
        _validate_relative_source(cast(str, source))
        _validate_page_path(cast(str, path))
        return cls(
            source=cast(str, source),
            path=cast(str, path),
            title=cast(str, title),
            description=_manifest_string(data, "description"),
            headings=tuple(parsed_headings),
            nodes=tuple(DocNode.from_dict(item) for item in nodes),
            search_text=_manifest_string(data, "search_text"),
            source_hash=_manifest_string(data, "source_hash"),
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

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"unsupported or missing manifest schema (expected {SCHEMA_VERSION})")
        if type(self.title) is not str or not self.title.strip():
            raise ValueError("manifest site title must not be empty")
        if type(self.max_query_length) is not int:
            raise ValueError("manifest max_query_length must be an integer")
        if self.max_query_length < 1:
            raise ValueError("manifest max_query_length must be positive")
        _validate_base_url(self.base_url)
        page_keys: set[str] = set()
        for page in self.pages:
            _validate_page_path(page.path)
            _validate_nodes(page.nodes)
            key = page.path.rstrip("/") or "/"
            if key in _RESERVED_ROUTES or key.startswith("/_hedron-docs"):
                raise ValueError(f"manifest page route is reserved: {page.path}")
            folded = key.casefold()
            if folded in page_keys:
                raise ValueError(f"manifest contains duplicate page route: {page.path}")
            page_keys.add(folded)
        asset_paths: set[str] = set()
        for asset in self.assets:
            _validate_asset_path(asset.path)
            _validate_relative_source(asset.source)
            if asset.path in asset_paths:
                raise ValueError(f"manifest contains duplicate asset route: {asset.path}")
            asset_paths.add(asset.path)

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
        max_query_length = site_data.get("max_query_length", 200)
        if isinstance(max_query_length, bool) or not isinstance(max_query_length, int):
            raise ValueError("manifest max_query_length must be an integer")
        return cls(
            title=_manifest_string(site_data, "title", "Documentation"),
            description=_manifest_string(site_data, "description"),
            base_url=_manifest_string(site_data, "base_url"),
            pages=tuple(PageRecord.from_dict(item) for item in page_values),
            assets=tuple(AssetRecord.from_dict(item) for item in asset_values),
            max_query_length=max_query_length,
            compiler_version=_manifest_string(data, "compiler_version", "unknown"),
        )


def _validate_base_url(value: str) -> None:
    if type(value) is not str:
        raise ValueError("manifest base_url must be a string")
    if not value:
        return
    if value != value.strip() or any(ord(char) < 0x20 for char in value):
        raise ValueError("manifest base_url contains disallowed whitespace")
    parts = urlsplit(value)
    try:
        _ = parts.port
    except ValueError as exc:
        raise ValueError("manifest base_url has an invalid port") from exc
    if (
        parts.scheme not in {"http", "https"}
        or not parts.netloc
        or parts.query
        or parts.fragment
        or parts.username is not None
        or parts.password is not None
    ):
        raise ValueError("manifest base_url must be an absolute http(s) URL without query/fragment")
    try:
        SafeUrl.parse(value, purpose=UrlPurpose.NAVIGATION, allow_external=True)
    except HedronError as exc:
        raise ValueError("manifest base_url is unsafe or invalid") from exc


def _manifest_string(data: dict[str, object], key: str, default: str = "") -> str:
    value = data.get(key, default)
    if not isinstance(value, str):
        raise ValueError(f"manifest field {key!r} must be a string")
    return value


def _validate_relative_source(value: str) -> None:
    if type(value) is not str or not value or value.startswith(("/", "\\")):
        raise ValueError("manifest source paths must be relative")
    if any(ord(char) < 0x20 for char in value) or "\\" in value:
        raise ValueError("manifest source paths contain disallowed characters")
    parts = Path(value).parts
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("manifest source paths must not contain dot segments")


def _validate_page_path(value: str, *, require_trailing: bool = True) -> None:
    if type(value) is not str or not value.startswith("/"):
        raise ValueError(f"invalid page route: {value!r}")
    if require_trailing and value != "/" and not value.endswith("/"):
        raise ValueError(f"page routes must end with '/': {value!r}")
    if (
        "//" in value
        or any(char in value for char in "?#\\")
        or any(ord(char) < 0x20 for char in value)
    ):
        raise ValueError(f"invalid page route: {value!r}")
    if value == "/":
        return
    for segment in value.strip("/").split("/"):
        if not segment:
            raise ValueError(f"page routes must not contain empty segments: {value!r}")
        try:
            decoded = unquote(segment, errors="strict")
        except UnicodeDecodeError as exc:
            raise ValueError(f"invalid percent encoding in page route: {value!r}") from exc
        if (
            decoded in {".", ".."}
            or "/" in decoded
            or "\\" in decoded
            or any(ord(char) < 0x20 for char in decoded)
            or quote(decoded, safe="-._~") != segment
        ):
            raise ValueError(f"page route is not normalized: {value!r}")


def _validate_asset_path(value: str) -> None:
    if not value.startswith("/_hedron-docs/assets/"):
        raise ValueError(f"invalid asset route: {value}")
    _validate_page_path(value, require_trailing=False)


def _validate_nodes(nodes: tuple[DocNode, ...]) -> None:
    """Validate URL-bearing AST nodes before an untrusted manifest reaches the renderer."""

    for node in nodes:
        try:
            if node.kind == "link":
                href = node.attr("href")
                if not href:
                    raise ValueError("manifest link is missing href")
                if href.startswith("#"):
                    runtime_href = href
                elif "#" in href:
                    path, fragment = href.split("#", 1)
                    runtime_href = (path.rstrip("/") or "/") + "#" + fragment
                else:
                    runtime_href = href.rstrip("/") or "/"
                SafeUrl.parse(
                    runtime_href,
                    purpose=UrlPurpose.NAVIGATION,
                    allow_external=bool(
                        urlsplit(runtime_href).scheme or urlsplit(runtime_href).netloc
                    ),
                )
            elif node.kind == "image":
                src = node.attr("src")
                if not src:
                    raise ValueError("manifest image is missing src")
                if not (src.startswith("/") or urlsplit(src).scheme or urlsplit(src).netloc):
                    raise ValueError("manifest image src must be root-relative or absolute")
                SafeUrl.parse(
                    src,
                    purpose=UrlPurpose.ASSET,
                    allow_external=bool(urlsplit(src).scheme or urlsplit(src).netloc),
                )
            elif node.kind == "heading":
                heading_id = node.attr("id")
                if not heading_id:
                    raise ValueError("manifest heading is missing id")
                SafeUrl.parse(f"#{heading_id}", purpose=UrlPurpose.NAVIGATION)
            elif node.kind == "alert" and node.attr("tone", "info") not in {
                "info",
                "success",
                "warning",
                "danger",
            }:
                raise ValueError("manifest alert has an invalid tone")
        except HedronError as exc:
            raise ValueError(f"manifest contains an unsafe {node.kind} URL") from exc
        _validate_nodes(node.children)


def load_manifest(value: SiteManifest | str | Path) -> SiteManifest:
    if isinstance(value, SiteManifest):
        return value
    path = Path(value)
    try:
        if path.stat().st_size > _MAX_MANIFEST_BYTES:
            raise ValueError(f"manifest exceeds {_MAX_MANIFEST_BYTES} bytes")
        data = json.loads(path.read_text(encoding="utf-8"))
        return SiteManifest.from_dict(data)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError, RecursionError) as exc:
        raise source_error("HED-DOCS-0200", f"invalid manifest: {exc}", path) from exc


def compile_site(config: DocsBuildConfig) -> SiteManifest:
    cfg = config.resolved(root=config.config_path.parent if config.config_path else None)
    if not cfg.docs_dir.is_dir():
        raise source_error("HED-DOCS-0201", f"documentation directory not found: {cfg.docs_dir}")
    pages: list[PageRecord] = []
    assets: dict[str, AssetRecord] = {}
    seen_paths: dict[str, Path] = {}
    docs_root = cfg.docs_dir.resolve()
    reserved = _RESERVED_ROUTES
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
        try:
            source_size = source_path.stat().st_size
        except OSError as exc:
            raise source_error(
                "HED-DOCS-0202", f"unable to inspect document: {exc}", source_path
            ) from exc
        if source_size > cfg.max_source_bytes:
            raise source_error(
                "HED-DOCS-0202",
                f"document exceeds source limit ({cfg.max_source_bytes} bytes)",
                source_path,
            )
        try:
            source = source_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise source_error(
                "HED-DOCS-0202", f"unable to read document: {exc}", source_path
            ) from exc
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
    encoded = [quote(part, safe="-._~") for part in parts]
    return "/" + "/".join(encoded) + "/"


def _excluded(path: Path, patterns: tuple[str, ...]) -> bool:
    text = path.as_posix()
    return any(
        fnmatch.fnmatch(text, pattern)
        or (pattern.endswith("/**") and (text == pattern[:-3] or text.startswith(pattern[:-2])))
        for pattern in patterns
    )


def _walk(nodes: tuple[DocNode, ...] | list[DocNode]) -> list[DocNode]:
    result: list[DocNode] = []
    pending = list(reversed(nodes))
    while pending:
        node = pending.pop()
        result.append(node)
        pending.extend(reversed(node.children))
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
    if document and value.startswith("#"):
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
        route = "/" + "/".join(quote(part, safe="-._~") for part in relative.parts)
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
    try:
        size = candidate.stat().st_size
    except OSError as exc:
        raise ValueError(f"unable to inspect documentation asset: {relative.as_posix()!r}") from exc
    if size > max_asset_bytes:
        raise ValueError(
            f"documentation asset exceeds limit ({max_asset_bytes} bytes): {relative.as_posix()!r}"
        )
    try:
        content = candidate.read_bytes()
    except OSError as exc:
        raise ValueError(f"unable to read documentation asset: {relative.as_posix()!r}") from exc
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
