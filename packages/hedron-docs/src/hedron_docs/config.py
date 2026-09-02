"""Configuration and bounded MkDocs migration import."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

from hedron_core.compat import tomllib

from .errors import source_error

CONFIG_SCHEMA_VERSION = 2
_MAX_MKDOCS_CONFIG_BYTES = 2_000_000
_MAX_MKDOCS_NODES = 20_000
_MAX_MKDOCS_DEPTH = 64


@dataclass(frozen=True, slots=True)
class NavigationItem:
    title: str
    path: str = ""
    children: tuple[NavigationItem, ...] = ()

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("navigation title must not be empty")
        if bool(self.path) == bool(self.children):
            raise ValueError("navigation item must have exactly one of path or children")
        if self.path:
            _validate_navigation_path(self.path)


@dataclass(frozen=True, slots=True)
class DocsBuildConfig:
    schema_version: int = CONFIG_SCHEMA_VERSION
    docs_dir: Path = Path("docs")
    output: Path = Path("build/hedron-docs/site.json")
    site_title: str = "Documentation"
    site_description: str = ""
    base_url: str = ""
    exclude: tuple[str, ...] = ()
    navigation: tuple[NavigationItem, ...] = ()
    allow_external_links: bool = True
    max_source_bytes: int = 2_000_000
    max_asset_bytes: int = 10_000_000
    max_nodes: int = 10_000
    max_depth: int = 64
    max_table_cells: int = 10_000
    max_code_blocks: int = 200
    max_code_block_bytes: int = 256_000
    max_directives: int = 100
    max_query_length: int = 200
    config_path: Path | None = field(default=None, compare=False)

    def __post_init__(self) -> None:
        if self.schema_version != CONFIG_SCHEMA_VERSION:
            raise ValueError(f"unsupported configuration schema (expected {CONFIG_SCHEMA_VERSION})")
        if not self.site_title.strip():
            raise ValueError("site_title must not be empty")
        limits = (
            self.max_source_bytes,
            self.max_asset_bytes,
            self.max_nodes,
            self.max_depth,
            self.max_table_cells,
            self.max_code_blocks,
            self.max_code_block_bytes,
            self.max_directives,
            self.max_query_length,
        )
        if any(type(value) is not int for value in limits):
            raise ValueError("compiler limits must be integers")
        if any(value < 1 for value in limits):
            raise ValueError("compiler limits must be positive")
        if self.base_url:
            parts = urlsplit(self.base_url)
            if (
                parts.scheme not in {"http", "https"}
                or not parts.netloc
                or parts.query
                or parts.fragment
                or parts.username is not None
                or parts.password is not None
                or "\\" in self.base_url
                or any(ord(char) < 0x20 for char in self.base_url)
            ):
                raise ValueError("base_url must be an absolute http(s) URL without query/fragment")

    def resolved(self, *, root: Path | None = None) -> DocsBuildConfig:
        base = (root or Path.cwd()).resolve()
        docs = self.docs_dir if self.docs_dir.is_absolute() else base / self.docs_dir
        output = self.output if self.output.is_absolute() else base / self.output
        return DocsBuildConfig(
            schema_version=self.schema_version,
            docs_dir=docs,
            output=output,
            site_title=self.site_title,
            site_description=self.site_description,
            base_url=self.base_url,
            exclude=self.exclude,
            navigation=self.navigation,
            allow_external_links=self.allow_external_links,
            max_source_bytes=self.max_source_bytes,
            max_asset_bytes=self.max_asset_bytes,
            max_nodes=self.max_nodes,
            max_depth=self.max_depth,
            max_table_cells=self.max_table_cells,
            max_code_blocks=self.max_code_blocks,
            max_code_block_bytes=self.max_code_block_bytes,
            max_directives=self.max_directives,
            max_query_length=self.max_query_length,
            config_path=self.config_path,
        )


def load_config(path: str | Path = "hedron-docs.toml") -> DocsBuildConfig:
    config_path = Path(path).resolve()
    try:
        raw_value: object = cast(object, tomllib.loads(config_path.read_text(encoding="utf-8")))
    except FileNotFoundError as exc:
        raise source_error("HED-DOCS-0002", f"configuration file not found: {config_path}") from exc
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise source_error("HED-DOCS-0003", f"invalid configuration: {exc}", config_path) from exc
    if not isinstance(raw_value, dict):
        raise source_error("HED-DOCS-0003", "configuration must be a TOML table", config_path)
    raw = cast(dict[str, object], raw_value)
    allowed = {"schema_version", "site", "build"}
    unknown = set(raw) - allowed
    if unknown:
        raise source_error(
            "HED-DOCS-0004", f"unknown configuration sections: {sorted(unknown)}", config_path
        )
    site = _mapping(raw.get("site", {}), config_path)
    build = _mapping(raw.get("build", {}), config_path)
    allowed_site = {
        "title",
        "description",
        "base_url",
        "docs_dir",
        "exclude",
        "allow_external_links",
        "navigation",
    }
    allowed_build = {
        "output",
        "max_source_bytes",
        "max_asset_bytes",
        "max_nodes",
        "max_depth",
        "max_table_cells",
        "max_code_blocks",
        "max_code_block_bytes",
        "max_directives",
        "max_query_length",
    }
    unknown_site = set(site) - allowed_site
    unknown_build = set(build) - allowed_build
    if unknown_site or unknown_build:
        raise source_error(
            "HED-DOCS-0005",
            f"unknown configuration keys: {sorted(unknown_site | unknown_build)}",
            config_path,
        )
    exclude_value = site.get("exclude", [])
    if not isinstance(exclude_value, list):
        raise source_error("HED-DOCS-0006", "site.exclude must be an array of strings", config_path)
    exclude = cast(list[object], exclude_value)
    if not all(isinstance(item, str) for item in exclude):
        raise source_error("HED-DOCS-0006", "site.exclude must be an array of strings", config_path)
    exclude_strings = [item for item in exclude if isinstance(item, str)]
    navigation = _parse_navigation(site.get("navigation", []), config_path)
    try:
        return DocsBuildConfig(
            schema_version=_as_int(raw.get("schema_version")),
            docs_dir=Path(_as_str(site.get("docs_dir", "docs"), "docs_dir")),
            output=Path(_as_str(build.get("output", "build/hedron-docs/site.json"), "output")),
            site_title=_as_str(site.get("title", "Documentation"), "title"),
            site_description=_as_str(site.get("description", ""), "description"),
            base_url=_as_str(site.get("base_url", ""), "base_url"),
            exclude=tuple(exclude_strings),
            navigation=navigation,
            allow_external_links=_as_bool(site.get("allow_external_links", True)),
            max_source_bytes=_as_int(build.get("max_source_bytes", 2_000_000)),
            max_asset_bytes=_as_int(build.get("max_asset_bytes", 10_000_000)),
            max_nodes=_as_int(build.get("max_nodes", 10_000)),
            max_depth=_as_int(build.get("max_depth", 64)),
            max_table_cells=_as_int(build.get("max_table_cells", 10_000)),
            max_code_blocks=_as_int(build.get("max_code_blocks", 200)),
            max_code_block_bytes=_as_int(build.get("max_code_block_bytes", 256_000)),
            max_directives=_as_int(build.get("max_directives", 100)),
            max_query_length=_as_int(build.get("max_query_length", 200)),
            config_path=config_path,
        )
    except ValueError as exc:
        raise source_error(
            "HED-DOCS-0005", f"invalid configuration value: {exc}", config_path
        ) from exc


def import_mkdocs(path: str | Path) -> DocsBuildConfig:
    """Import safe site metadata and exclusion facts from a MkDocs YAML file.

    Plugin objects, hooks, theme configuration, and arbitrary YAML constructors are ignored.
    """

    config_path = Path(path).resolve()
    try:
        import yaml

        if config_path.stat().st_size > _MAX_MKDOCS_CONFIG_BYTES:
            raise ValueError(f"MkDocs configuration exceeds {_MAX_MKDOCS_CONFIG_BYTES} bytes")

        class _SafeMigrationLoader(yaml.SafeLoader):
            pass

        def _ignore_unknown(loader: Any, tag_suffix: str, node: Any) -> Any:
            if isinstance(node, yaml.ScalarNode):
                return loader.construct_scalar(node)
            if isinstance(node, yaml.SequenceNode):
                return loader.construct_sequence(node)
            return loader.construct_mapping(node)

        _SafeMigrationLoader.add_multi_constructor(  # pyright: ignore[reportUnknownMemberType]
            "!", _ignore_unknown
        )
        _SafeMigrationLoader.add_multi_constructor(  # pyright: ignore[reportUnknownMemberType]
            "tag:yaml.org,2002:python/", _ignore_unknown
        )
        source = config_path.read_text(encoding="utf-8")
        composed: object = cast(
            object,
            yaml.compose(  # pyright: ignore[reportUnknownMemberType]
                source, Loader=_SafeMigrationLoader
            ),
        )
        _validate_yaml_tree(composed)
        raw_value: object = cast(object, yaml.load(source, Loader=_SafeMigrationLoader) or {})
    except FileNotFoundError as exc:
        raise source_error(
            "HED-DOCS-0010", f"MkDocs configuration not found: {config_path}"
        ) from exc
    except Exception as exc:
        raise source_error(
            "HED-DOCS-0011", f"invalid MkDocs configuration: {exc}", config_path
        ) from exc
    if not isinstance(raw_value, dict):
        raise source_error("HED-DOCS-0012", "MkDocs configuration must be a mapping", config_path)
    data = cast(dict[str, object], raw_value)
    docs_dir_value = data.get("docs_dir", "docs")
    if not isinstance(docs_dir_value, str):
        raise source_error("HED-DOCS-0012", "MkDocs docs_dir must be a string", config_path)
    docs_dir = Path(docs_dir_value)
    exclude_value = data.get("exclude_docs")
    if exclude_value is None:
        excludes = ()
    elif isinstance(exclude_value, str):
        excludes = tuple(item for item in exclude_value.splitlines() if item.strip())
    elif isinstance(exclude_value, list):
        exclude_items = cast(list[object], exclude_value)
        if not all(isinstance(item, str) for item in exclude_items):
            raise source_error(
                "HED-DOCS-0012",
                "MkDocs exclude_docs must be a string or array of strings",
                config_path,
            )
        string_items = cast(list[str], exclude_items)
        excludes = tuple(item for item in string_items if item.strip())
    else:
        raise source_error(
            "HED-DOCS-0012", "MkDocs exclude_docs must be a string or array of strings", config_path
        )
    try:
        navigation = _parse_mkdocs_navigation(data.get("nav", []), config_path)
        return DocsBuildConfig(
            docs_dir=docs_dir,
            site_title=str(data.get("site_name", "Documentation")),
            site_description=str(data.get("site_description", "")),
            base_url=str(data.get("site_url", "")) if isinstance(data.get("site_url"), str) else "",
            exclude=excludes,
            navigation=navigation,
            config_path=config_path,
        )
    except ValueError as exc:
        raise source_error(
            "HED-DOCS-0012", f"invalid MkDocs site metadata: {exc}", config_path
        ) from exc


def _mapping(value: object, source: Path) -> dict[str, object]:
    if not isinstance(value, dict):
        raise source_error("HED-DOCS-0007", "configuration section must be a table", source)
    return cast(dict[str, object], value)


def _as_int(value: object) -> int:
    if isinstance(value, bool):
        raise ValueError("configuration integer value is invalid")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.fullmatch(r"[+-]?\d+", value.strip()):
        return int(value)
    raise ValueError("configuration integer value is invalid")


def _as_bool(value: object) -> bool:
    if not isinstance(value, bool):
        raise ValueError("configuration boolean value is invalid")
    return value


def _as_str(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"configuration {name} value must be a string")
    return value


def _validate_navigation_path(value: str) -> None:
    if (
        not value
        or value.startswith(("/", "\\"))
        or "\\" in value
        or any(ord(char) < 0x20 for char in value)
    ):
        raise ValueError(f"navigation path must be a safe relative path: {value!r}")
    if any(part in {"", ".", ".."} for part in Path(value).parts):
        raise ValueError(f"navigation path contains a dot segment: {value!r}")


def _parse_navigation(
    value: object, source: Path, *, depth: int = 0, counter: list[int] | None = None
) -> tuple[NavigationItem, ...]:
    if depth > _MAX_MKDOCS_DEPTH:
        raise source_error("HED-DOCS-0006", "navigation nesting exceeds limit", source)
    if not isinstance(value, list):
        raise source_error("HED-DOCS-0006", "site.navigation must be an array of tables", source)
    if counter is None:
        counter = [0]
    result: list[NavigationItem] = []
    for raw_item in cast(list[object], value):
        counter[0] += 1
        if counter[0] > _MAX_MKDOCS_NODES:
            raise source_error("HED-DOCS-0006", "navigation item count exceeds limit", source)
        if not isinstance(raw_item, dict):
            raise source_error("HED-DOCS-0006", "navigation item must be a table", source)
        item = cast(dict[str, object], raw_item)
        unknown = set(item) - {"title", "path", "children"}
        if unknown:
            raise source_error(
                "HED-DOCS-0006", f"unknown navigation keys: {sorted(unknown)}", source
            )
        try:
            title = _as_str(item.get("title", ""), "navigation title")
            path = _as_str(item.get("path", ""), "navigation path")
            children = _parse_navigation(
                item.get("children", []), source, depth=depth + 1, counter=counter
            )
            result.append(NavigationItem(title=title, path=path, children=children))
        except ValueError as exc:
            raise source_error("HED-DOCS-0006", f"invalid navigation: {exc}", source) from exc
    return tuple(result)


def _parse_mkdocs_navigation(
    value: object, source: Path, *, depth: int = 0, counter: list[int] | None = None
) -> tuple[NavigationItem, ...]:
    if value in (None, []):
        return ()
    if depth > _MAX_MKDOCS_DEPTH or not isinstance(value, list):
        raise source_error("HED-DOCS-0012", "MkDocs nav has an invalid or deep shape", source)
    if counter is None:
        counter = [0]
    result: list[NavigationItem] = []
    for raw_item in cast(list[object], value):
        counter[0] += 1
        if counter[0] > _MAX_MKDOCS_NODES:
            raise source_error("HED-DOCS-0012", "MkDocs nav item count exceeds limit", source)
        if isinstance(raw_item, str):
            try:
                result.append(
                    NavigationItem(Path(raw_item).stem.replace("-", " ").title(), raw_item)
                )
            except ValueError as exc:
                raise source_error(
                    "HED-DOCS-0012", f"invalid MkDocs nav path: {exc}", source
                ) from exc
            continue
        raw_mapping = cast(dict[object, object], raw_item) if isinstance(raw_item, dict) else {}
        if not isinstance(raw_item, dict) or len(raw_mapping) != 1:
            raise source_error("HED-DOCS-0012", "MkDocs nav item must have one label", source)
        title, target = next(iter(raw_mapping.items()))
        if not isinstance(title, str):
            raise source_error("HED-DOCS-0012", "MkDocs nav label must be a string", source)
        try:
            if isinstance(target, str):
                result.append(NavigationItem(title, target))
            else:
                result.append(
                    NavigationItem(
                        title,
                        children=_parse_mkdocs_navigation(
                            target, source, depth=depth + 1, counter=counter
                        ),
                    )
                )
        except ValueError as exc:
            raise source_error("HED-DOCS-0012", f"invalid MkDocs nav: {exc}", source) from exc
    return tuple(result)


def _validate_yaml_tree(root: object) -> None:
    if root is None:
        return
    pending: list[tuple[object, int]] = [(root, 1)]
    count = 0
    while pending:
        node, depth = pending.pop()
        count += 1
        if count > _MAX_MKDOCS_NODES or depth > _MAX_MKDOCS_DEPTH:
            raise ValueError("MkDocs YAML exceeds node or nesting limit")
        raw_children = getattr(node, "value", None)
        if not isinstance(raw_children, list):
            continue
        for child in cast(list[object], raw_children):
            tuple_child = cast(tuple[object, ...], child) if isinstance(child, tuple) else ()
            if len(tuple_child) == 2:
                key, item = tuple_child
                pending.append((key, depth + 1))
                pending.append((item, depth + 1))
            else:
                pending.append((child, depth + 1))  # pyright: ignore[reportUnknownArgumentType]
